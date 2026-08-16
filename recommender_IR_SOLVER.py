import pandas as pd
import numpy as np
import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize
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
print("INFORMATION RETRIEVAL SOLVER - TARGET 95-100/100")
print("="*80)

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

# Optional: Remove exact course names from train data to prevent noise
# But because the syllabus sentences are so distinct, pure TF-IDF will naturally match them perfectly anyway.
# We will use Word (1-3) and Char (3-6) n-grams to capture maximum template overlap.

print("\n[2] Extracting massive TF-IDF Vocabulary...")
# Combine texts to build vocabulary
all_texts = train["clean"].tolist() + test["clean"].tolist()

vec_word = TfidfVectorizer(max_features=100000, ngram_range=(1,3), min_df=1, max_df=0.95, stop_words='english', sublinear_tf=True)
vec_char = TfidfVectorizer(max_features=80000, analyzer='char_wb', ngram_range=(3,6), min_df=1, max_df=0.95, sublinear_tf=True)

print("    -> Fitting Word n-grams...")
vec_word.fit(all_texts)
print("    -> Fitting Char n-grams...")
vec_char.fit(all_texts)

print("\n[3] Transforming Matrices...")
from scipy.sparse import hstack

train_word = vec_word.transform(train["clean"])
test_word = vec_word.transform(test["clean"])

train_char = vec_char.transform(train["clean"])
test_char = vec_char.transform(test["clean"])

train_mat = hstack([train_word, train_char])
test_mat = hstack([test_word, test_char])

print(f"    Total feature dimension: {train_mat.shape[1]}")

# Normalize to ensure dot product equals cosine similarity
train_mat = normalize(train_mat)
test_mat = normalize(test_mat)

print("\n[4] Computing Cosine Similarity & Extracting Top 10...")
# Matrix multiplication: test (10977 x Features) dot train.T (Features x 110000)
# Doing this in chunks to avoid memory spikes
chunk_size = 1000
recommendations = []

train_idx = train["Index"].values

for i in range(0, len(test), chunk_size):
    end = min(i + chunk_size, len(test))
    test_chunk = test_mat[i:end]
    
    # Dense similarity matrix for chunk: (chunk_size, 110000)
    sim_chunk = (test_chunk @ train_mat.T).toarray()
    
    # Get top 10 indices for each row in chunk
    # argpartition is much faster than argsort for finding top K
    # We negate sim_chunk to sort descending
    top10_local_idx = np.argpartition(-sim_chunk, 10, axis=1)[:, :10]
    
    # argpartition doesn't guarantee order within the top K, so we sort the top K
    for row_idx in range(sim_chunk.shape[0]):
        row_top10 = top10_local_idx[row_idx]
        # Sort these 10 based on actual similarity scores
        sorted_top10 = row_top10[np.argsort(-sim_chunk[row_idx, row_top10])]
        
        # Map back to training Index
        recs = train_idx[sorted_top10].tolist()
        recommendations.append(recs)
        
    print(f"    Processed {end} / {len(test)} reviews...")

print("\n[5] Saving submission...")
out_path = os.path.join(_here, "submission_IR_SOLVER.csv")
submission = pd.DataFrame({
    "Index": test["Index"].values,
    "Index_list": [str(r) for r in recommendations],
})
submission.to_csv(out_path, index=False)
print("\n="*80)
print(f"🚀 DONE! Saved to {out_path}")
print("="*80)
