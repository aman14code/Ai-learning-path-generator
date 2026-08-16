import pandas as pd
import numpy as np
import re
import os
from collections import Counter
import warnings
warnings.filterwarnings("ignore")

_here = os.path.dirname(os.path.abspath(__file__))
_desktop = r"c:\Users\amans\OneDrive\Desktop"

def find_file(name):
    for folder in [_here, _desktop, os.getcwd()]:
        p = os.path.join(folder, name)
        if os.path.exists(p) and os.path.getsize(p) > 1000:
            return p
    raise FileNotFoundError(f"Cannot find {name}")

print("="*80)
print("SBERT + LOGISTIC REGRESSION - TARGET 95+/100")
print("="*80)

try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("\n ERROR: sentence-transformers not installed!")
    print("Run: pip install sentence-transformers")
    exit(1)

from sklearn.linear_model import LogisticRegression
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import normalize

# ============================================================================
# 1. LOAD & CLEAN DATA
# ============================================================================
print("\n[1] Loading data...")
train = pd.read_csv(find_file("train.csv"))
test = pd.read_csv(find_file("test.csv"))

def clean(text):
    if pd.isna(text): return ""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+|\S+@\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

train["clean"] = train["Reviews"].apply(clean)
test["clean"] = test["Reviews"].apply(clean)
print(f"    Train: {train.shape}, Test: {test.shape}")

# ============================================================================
# 2. SENTENCE-BERT EMBEDDINGS
# ============================================================================
print("\n[2] Encoding with Sentence-BERT (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')

train_embeddings = model.encode(
    train["clean"].tolist(),
    batch_size=64,
    show_progress_bar=True,
    convert_to_numpy=True
)

test_embeddings = model.encode(
    test["clean"].tolist(),
    batch_size=64,
    show_progress_bar=True,
    convert_to_numpy=True
)

train_embeddings = normalize(train_embeddings)
test_embeddings = normalize(test_embeddings)
print("    Embeddings generated and normalized")

# ============================================================================
# 3. LOGISTIC REGRESSION CLASSIFICATION (MUCH BETTER THAN PROTOTYPES)
# ============================================================================
print("\n[3] Training Classifier on SBERT embeddings...")

clf = LogisticRegression(C=2.0, max_iter=1000, n_jobs=-1, random_state=42)
clf.fit(train_embeddings, train["Course"])

predicted_courses = clf.predict(test_embeddings)
train_acc = (clf.predict(train_embeddings) == train["Course"]).mean()

print(f"    Train accuracy: {train_acc*100:.2f}%")
print(f"    Predicted {len(set(predicted_courses))} unique courses")

# ============================================================================
# 4. SELECT TOP-10 FROM PREDICTED COURSE
# ============================================================================
print("\n[4] Selecting best 10 examples from each predicted course...")

course_to_indices = {course: np.where(train["Course"] == course)[0] for course in train["Course"].unique()}
train_idx = train["Index"].values
test_idx = test["Index"].values

recommendations = []

try:
    from tqdm import tqdm
    iterator = tqdm(range(len(test)), desc="Top-10 selection", ncols=80)
except:
    iterator = range(len(test))

for i in iterator:
    pred_course = predicted_courses[i]
    test_emb = test_embeddings[i].reshape(1, -1)
    
    # Get all training examples from this course
    course_indices = course_to_indices[pred_course]
    course_embs = train_embeddings[course_indices]
    
    # Find most similar 10
    sims = cosine_similarity(test_emb, course_embs)[0]
    top10_local = np.argsort(-sims)[:10]
    top10_global = course_indices[top10_local]
    
    # Convert to Index values
    recs = train_idx[top10_global].tolist()
    
    while len(recs) < 10:
        recs.append(train_idx[course_indices[0]])
    
    recommendations.append(recs[:10])

# ============================================================================
# 5. VALIDATION & SAVE
# ============================================================================
print("\n[5] Saving submission...")

out_path = os.path.join(_here, "submission_BERT_MAX.csv")
sub = pd.DataFrame({
    "Index": test_idx,
    "Index_list": [str(r) for r in recommendations],
})
sub.to_csv(out_path, index=False)

print(f"\n SBERT SUBMISSION COMPLETE!")
print(f" File: {out_path}")

for i in range(min(3, len(test))):
    recs = recommendations[i]
    rec_courses = [train[train["Index"] == r]["Course"].values[0] for r in recs]
    majority = Counter(rec_courses).most_common(1)[0]
    print(f"\n    Test {test_idx[i]}:")
    print(f"      Predicted: {predicted_courses[i]}")
    print(f"      Majority: {majority[0]} ({majority[1]}/10)")

print("\n DONE! Submit submission_BERT_MAX.csv")
