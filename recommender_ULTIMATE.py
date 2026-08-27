"""
ULTIMATE MAX ACCURACY - ONE RUN, ONE SUBMISSION
Strategy:
  1. Direct course-name regex match (near 100% for reviews that mention the course name)
  2. 3-classifier ensemble fallback (LogReg word + LogReg char + LinearSVC combo)
  3. Pick top-10 most similar reviews from the predicted course
"""
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
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import normalize

try:
    from tqdm import tqdm
    TQDM = True
except ImportError:
    TQDM = False
    def tqdm(x, **kw): return x

_here    = os.path.dirname(os.path.abspath(__file__))
_desktop = r"c:\Users\amans\OneDrive\Desktop"

def find_file(name):
    for folder in [_here, _desktop, os.getcwd(), r"c:\Users\amans\OneDrive\Desktop\HCL Simplified Hackathon\pathfinder\backend\data"]:
        p = os.path.join(folder, name)
        if os.path.exists(p) and os.path.getsize(p) > 1000:
            return p
    raise FileNotFoundError(f"Cannot find {name}")

print("=" * 70)
print("  ULTIMATE MAX ACCURACY RECOMMENDER")
print("=" * 70)

# ------------------------------------------------------------------
# 1. Load
# ------------------------------------------------------------------
print("\n[1] Loading data...")
train = pd.read_csv(find_file("train.csv"))
test  = pd.read_csv(find_file("test.csv"))
print(f"    Train: {train.shape} | Test: {test.shape}")

def clean(text):
    if pd.isna(text): return ""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+|\S+@\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

train["clean"] = train["Reviews"].apply(clean)
test["clean"]  = test["Reviews"].apply(clean)

train_labels  = train["Course"].values
train_idx_col = train["Index"].values
test_idx_col  = test["Index"].values
all_texts     = train["clean"].tolist() + test["clean"].tolist()

course_list   = train["Course"].unique().tolist()
course_to_rows = {c: np.where(train_labels == c)[0] for c in course_list}

# ------------------------------------------------------------------
# 2. STEP 1: Direct course-name matching in review text
#    (Many reviews explicitly say "I completed <CourseName>...")
# ------------------------------------------------------------------
print("\n[2] Direct course-name matching...")

# Build regex pattern for each course (longest match first)
sorted_courses = sorted(course_list, key=len, reverse=True)

def find_course_in_text(text):
    """Return the course name if found directly in the review, else None."""
    for course in sorted_courses:
        # match course name as substring (cleaned)
        pattern = re.escape(clean(course))
        if re.search(pattern, text):
            return course
    return None

test["direct_match"] = test["clean"].apply(find_course_in_text)
n_direct = test["direct_match"].notna().sum()
n_needs_clf = test["direct_match"].isna().sum()
print(f"    Direct match found  : {n_direct} / {len(test)} ({100*n_direct/len(test):.1f}%)")
print(f"    Needs classifier    : {n_needs_clf} / {len(test)}")

# ------------------------------------------------------------------
# 3. STEP 2: Ensemble classifier for remaining reviews
# ------------------------------------------------------------------
print("\n[3] Training ensemble classifier for the remaining...")

vec_word = TfidfVectorizer(max_features=80000, ngram_range=(1,3),
                            min_df=1, max_df=0.95, stop_words="english",
                            sublinear_tf=True, strip_accents="unicode")
vec_word.fit(all_texts)
Xw_tr = vec_word.transform(train["clean"].tolist())
Xw_te = vec_word.transform(test["clean"].tolist())
print(f"    Word features: {Xw_tr.shape[1]}")

vec_char = TfidfVectorizer(max_features=60000, analyzer="char_wb",
                            ngram_range=(3,6), min_df=1, max_df=0.95,
                            sublinear_tf=True)
vec_char.fit(all_texts)
Xc_tr = vec_char.transform(train["clean"].tolist())
Xc_te = vec_char.transform(test["clean"].tolist())
print(f"    Char features: {Xc_tr.shape[1]}")

X_combo_tr = hstack([Xw_tr, Xc_tr])
X_combo_te = hstack([Xw_te, Xc_te])
print(f"    Combined: {X_combo_tr.shape[1]}")

# Classifier A: LogReg on word
print("    Training LogReg-word (C=2.0)...")
clfA = LogisticRegression(C=2.0, max_iter=1000, solver="saga",
                           random_state=42, n_jobs=-1)
clfA.fit(Xw_tr, train_labels)
accA = (clfA.predict(Xw_tr) == train_labels).mean()
print(f"    LogReg-word  train acc: {accA*100:.2f}%")

# Classifier B: LogReg on char
print("    Training LogReg-char (C=2.0)...")
clfB = LogisticRegression(C=2.0, max_iter=1000, solver="saga",
                           random_state=43, n_jobs=-1)
clfB.fit(Xc_tr, train_labels)
accB = (clfB.predict(Xc_tr) == train_labels).mean()
print(f"    LogReg-char  train acc: {accB*100:.2f}%")

# Classifier C: Calibrated LinearSVC on combined
print("    Training LinearSVC-combo (calibrated)...")
svc = LinearSVC(C=1.0, max_iter=3000, random_state=42, dual=True)
clfC = CalibratedClassifierCV(svc, cv=3)
clfC.fit(X_combo_tr, train_labels)
accC = (clfC.predict(X_combo_tr) == train_labels).mean()
print(f"    SVC-combo    train acc: {accC*100:.2f}%")

# Weighted probability ensemble
print("    Ensembling probabilities...")
pA = clfA.predict_proba(Xw_te)
pB = clfB.predict_proba(Xc_te)
pC = clfC.predict_proba(X_combo_te)

# 3-Model Ensemble
ensemble_probs   = (3.0*pA + 2.5*pB + 2.0*pC) / 7.5
classes          = clfA.classes_
clf_predictions  = classes[np.argmax(ensemble_probs, axis=1)]
print(f"    Unique clf predictions: {len(set(clf_predictions))}")

# ------------------------------------------------------------------
# 4. Merge: direct match takes priority, classifier fills the rest
# ------------------------------------------------------------------
print("\n[4] Merging predictions...")
final_predicted = []
for i in range(len(test)):
    dm = test["direct_match"].iloc[i]
    final_predicted.append(dm if dm is not None else clf_predictions[i])

final_predicted = np.array(final_predicted)

n_from_direct = sum(1 for i,dm in enumerate(test["direct_match"]) if dm is not None)
n_from_clf    = len(test) - n_from_direct
print(f"    From direct match : {n_from_direct}")
print(f"    From classifier   : {n_from_clf}")
print(f"    Unique final      : {len(set(final_predicted))}")

# ------------------------------------------------------------------
# 5. Pick top-10 most similar reviews from predicted course
# ------------------------------------------------------------------
print("\n[5] Generating recommendations using COMBINED features for maximum accuracy...")

# CRITICAL FIX: Use the combined Word+Char matrix for similarity instead of just Word matrix!
# This drastically improves the quality of the top 10 recommended reviews.
train_mat = normalize(X_combo_tr)
test_mat  = normalize(X_combo_te)

itr = range(len(test))
if TQDM:
    itr = tqdm(list(itr), desc="Recs", ncols=70)

recommendations = []
for i in itr:
    pred_course   = final_predicted[i]
    row_positions = course_to_rows.get(pred_course, np.arange(len(train)))
    sims = (test_mat[i] @ train_mat[row_positions].T).toarray().flatten()
    top10_global  = row_positions[np.argsort(-sims)[:10]]
    recs = train_idx_col[top10_global].tolist()
    while len(recs) < 10:
        recs.append(int(train_idx_col[row_positions[0]]))
    recommendations.append(recs[:10])

print(f"    Generated {len(recommendations)} recommendations")

# ------------------------------------------------------------------
# 6. Save
# ------------------------------------------------------------------
print("\n[6] Saving submission...")
out_path = os.path.join(_here, "submission_ULTIMATE.csv")
sub = pd.DataFrame({
    "Index":      test_idx_col,
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
    mv      = Counter(courses).most_common(1)[0]
    src     = "DIRECT" if test["direct_match"].iloc[i] is not None else "CLASSIFIER"
    print(f"Test {test_idx_col[i]} [{src}]: predicted={final_predicted[i]}")
    print(f"  -> Majority: {mv[0]} ({mv[1]}/10)")

print()
print("=" * 70)
print("  DONE! Submit: submission_ULTIMATE.csv")
print("=" * 70)
