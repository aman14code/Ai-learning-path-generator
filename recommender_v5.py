import pandas as pd
import numpy as np
import re
import warnings
import os
from scipy.sparse import hstack
warnings.filterwarnings("ignore")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import normalize, LabelEncoder
from sklearn.pipeline import Pipeline

_here    = os.path.dirname(os.path.abspath(__file__))
_desktop = r"c:\Users\amans\OneDrive\Desktop"

def find_file(name):
    for folder in [_here, _desktop, os.getcwd()]:
        p = os.path.join(folder, name)
        if os.path.exists(p) and os.path.getsize(p) > 1000:
            return p
    raise FileNotFoundError(f"Cannot find {name}")

print("[1] Loading data...")
train = pd.read_csv(find_file("train.csv"))
test  = pd.read_csv(find_file("test.csv"))
print(f"    Train: {train.shape} | Test: {test.shape} | Courses: {train['Course'].nunique()}")

def clean(text):
    if pd.isna(text): return ""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+|\S+@\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

print("[2] Cleaning text...")
train["clean"] = train["Reviews"].apply(clean)
test["clean"]  = test["Reviews"].apply(clean)
all_texts = train["clean"].tolist() + test["clean"].tolist()

train_labels = train["Course"].values
train_idx    = train["Index"].values
test_idx     = test["Index"].values

print("[3] Building combined feature matrix (word + char ngrams)...")

# Word TF-IDF
vec_word = TfidfVectorizer(
    max_features=80000, ngram_range=(1, 3),
    min_df=1, max_df=0.95, stop_words="english",
    sublinear_tf=True, strip_accents="unicode"
)
vec_word.fit(all_texts)
X_train_word = vec_word.transform(train["clean"].tolist())
X_test_word  = vec_word.transform(test["clean"].tolist())
print(f"    Word features: {X_train_word.shape[1]}")

# Char TF-IDF (important for catching course-specific technical terms)
vec_char = TfidfVectorizer(
    max_features=50000, analyzer="char_wb",
    ngram_range=(3, 6), min_df=1, max_df=0.95,
    sublinear_tf=True
)
vec_char.fit(all_texts)
X_train_char = vec_char.transform(train["clean"].tolist())
X_test_char  = vec_char.transform(test["clean"].tolist())
print(f"    Char features: {X_train_char.shape[1]}")

# Concatenate both feature sets
X_train = hstack([X_train_word, X_train_char])
X_test  = hstack([X_test_word,  X_test_char])
print(f"    Combined features: {X_train.shape[1]}")

print("[4] Training ensemble classifiers...")

# Classifier 1: LinearSVC (fast, strong)
svc = LinearSVC(C=0.8, max_iter=3000, random_state=42, dual=True)
svc.fit(X_train, train_labels)
pred_svc = svc.predict(X_test)
train_acc_svc = (svc.predict(X_train) == train_labels).mean()
print(f"    LinearSVC train acc: {train_acc_svc*100:.2f}%")

# Classifier 2: Logistic Regression (better probability estimates)
lr = LogisticRegression(C=5.0, max_iter=1000, solver="saga",
                         multi_class="multinomial", random_state=42, n_jobs=-1)
lr.fit(X_train, train_labels)
pred_lr = lr.predict(X_test)
train_acc_lr = (lr.predict(X_train) == train_labels).mean()
print(f"    LogReg train acc: {train_acc_lr*100:.2f}%")

# Classifier 3: LinearSVC with different C
svc2 = LinearSVC(C=2.0, max_iter=3000, random_state=99, dual=True)
svc2.fit(X_train, train_labels)
pred_svc2 = svc2.predict(X_test)
train_acc_svc2 = (svc2.predict(X_train) == train_labels).mean()
print(f"    LinearSVC-C2 train acc: {train_acc_svc2*100:.2f}%")

print("[5] Ensemble vote (majority of 3 classifiers)...")
all_preds = np.array([pred_svc, pred_lr, pred_svc2])  # shape (3, N_TEST)

from scipy.stats import mode
ensemble_preds, _ = mode(all_preds, axis=0)
ensemble_preds = ensemble_preds.flatten()
print(f"    Unique courses predicted: {len(set(ensemble_preds))}")

print("[6] Picking top-10 most similar reviews from predicted course...")
from sklearn.preprocessing import normalize as nrm

# Use word TF-IDF for similarity within predicted course
train_mat_n = nrm(X_train_word)
test_mat_n  = nrm(X_test_word)

course_to_rows = {}
for c in train["Course"].unique():
    course_to_rows[c] = np.where(train_labels == c)[0]

try:
    from tqdm import tqdm
    itr = tqdm(range(len(test)), desc="Generating recs", ncols=70)
except ImportError:
    itr = range(len(test))

recommendations = []
for i in itr:
    pred_course   = ensemble_preds[i]
    row_positions = course_to_rows.get(pred_course, np.array([]))
    if len(row_positions) == 0:
        row_positions = np.arange(len(train))
    course_mat = train_mat_n[row_positions]
    sims = (test_mat_n[i] @ course_mat.T).toarray().flatten()
    top10_local  = np.argsort(-sims)[:10]
    top10_global = row_positions[top10_local]
    recs = train_idx[top10_global].tolist()
    while len(recs) < 10:
        recs.append(int(train_idx[row_positions[0]]))
    recommendations.append(recs[:10])

print(f"    Generated {len(recommendations)} recommendations")

print("[7] Saving submission...")
out_path = os.path.join(_here, "submission_FINAL_v5.csv")
sub = pd.DataFrame({
    "Index":      test_idx,
    "Index_list": [str(r) for r in recommendations],
})
sub.to_csv(out_path, index=False)
print(f"    Saved -> {out_path}  ({sub.shape[0]} rows)")
print(sub.head(3).to_string())

print()
from collections import Counter
for i in range(5):
    recs    = recommendations[i]
    courses = [train[train["Index"] == r]["Course"].values[0] for r in recs]
    print(f"Test {test_idx[i]}: predicted={ensemble_preds[i]}")
    print(f"  -> Majority: {Counter(courses).most_common(1)[0][0]}")
print()
print("DONE! Submit: submission_FINAL_v5.csv")
