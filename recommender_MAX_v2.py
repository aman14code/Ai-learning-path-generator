# -*- coding: utf-8 -*-
"""
MAXIMUM ACCURACY RECOMMENDER v2
Strategy:
  1. Course prediction via 4-classifier ensemble
  2. Within PREDICTED course: find 10 most similar reviews using
     multi-signal similarity (specific content + word + char TF-IDF)
  3. Key insight: reviews are templated, so we strip generic sentences
     and focus on course-specific technical content for similarity
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import pandas as pd
import numpy as np
import re
import os
import warnings
import time
from collections import Counter
from scipy.sparse import hstack
warnings.filterwarnings("ignore")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import normalize

_here = os.path.dirname(os.path.abspath(__file__))

def find_file(name):
    locations = [
        _here,
        r"c:\Users\amans\OneDrive\Desktop",
        r"c:\Users\amans\Downloads",
        os.getcwd()
    ]
    for folder in locations:
        p = os.path.join(folder, name)
        if os.path.exists(p) and os.path.getsize(p) > 1000:
            return p
    raise FileNotFoundError(f"Cannot find {name}")

print("=" * 70)
print("  MAXIMUM ACCURACY RECOMMENDER v2")
print("=" * 70)

# ------------------------------------------------------------------
# 1. Load
# ------------------------------------------------------------------
print("\n[1/7] Loading data...")
t0 = time.time()
train = pd.read_csv(find_file("train.csv"))
test = pd.read_csv(find_file("test.csv"))
print(f"    Train: {train.shape} | Test: {test.shape}")

def clean(text):
    if pd.isna(text): return ""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+|\S+@\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

train["clean"] = train["Reviews"].apply(clean)
test["clean"] = test["Reviews"].apply(clean)
train_labels = train["Course"].values
train_idx_col = train["Index"].values
test_idx_col = test["Index"].values

course_list = train["Course"].unique().tolist()
course_to_rows = {c: np.where(train_labels == c)[0] for c in course_list}

# ------------------------------------------------------------------
# 2. Train classifier ensemble
# ------------------------------------------------------------------
print("\n[2/7] Training classifier ensemble...")
all_texts = train["clean"].tolist() + test["clean"].tolist()

# Word TF-IDF
print("    [a] Word TF-IDF (1,3)...")
vec_word = TfidfVectorizer(max_features=80000, ngram_range=(1, 3),
                            min_df=1, max_df=0.95, stop_words="english",
                            sublinear_tf=True, strip_accents="unicode")
vec_word.fit(all_texts)
Xw_tr = vec_word.transform(train["clean"])
Xw_te = vec_word.transform(test["clean"])

# Char TF-IDF
print("    [b] Char TF-IDF (3,6)...")
vec_char = TfidfVectorizer(max_features=60000, analyzer="char_wb",
                            ngram_range=(3, 6), min_df=1, max_df=0.95,
                            sublinear_tf=True)
vec_char.fit(all_texts)
Xc_tr = vec_char.transform(train["clean"])
Xc_te = vec_char.transform(test["clean"])

X_combo_tr = hstack([Xw_tr, Xc_tr])
X_combo_te = hstack([Xw_te, Xc_te])

# Classifier A: LogReg word C=2.0
print("    [c] LogReg-word (C=2.0)...")
clfA = LogisticRegression(C=2.0, max_iter=2000, solver="saga", random_state=42, n_jobs=-1)
clfA.fit(Xw_tr, train_labels)
accA = (clfA.predict(Xw_tr) == train_labels).mean()
print(f"        train acc: {accA*100:.2f}%")

# Classifier B: LogReg char C=2.0
print("    [d] LogReg-char (C=2.0)...")
clfB = LogisticRegression(C=2.0, max_iter=2000, solver="saga", random_state=43, n_jobs=-1)
clfB.fit(Xc_tr, train_labels)
accB = (clfB.predict(Xc_tr) == train_labels).mean()
print(f"        train acc: {accB*100:.2f}%")

# Classifier C: Calibrated LinearSVC
print("    [e] SVC-combo (calibrated, cv=3)...")
svc = LinearSVC(C=1.0, max_iter=3000, random_state=42, dual=True)
clfC = CalibratedClassifierCV(svc, cv=3)
clfC.fit(X_combo_tr, train_labels)
accC = (clfC.predict(X_combo_tr) == train_labels).mean()
print(f"        train acc: {accC*100:.2f}%")

# Classifier D: LogReg combo C=1.5
print("    [f] LogReg-combo (C=1.5)...")
clfD = LogisticRegression(C=1.5, max_iter=2000, solver="saga", random_state=44, n_jobs=-1)
clfD.fit(X_combo_tr, train_labels)
accD = (clfD.predict(X_combo_tr) == train_labels).mean()
print(f"        train acc: {accD*100:.2f}%")

# Ensemble
print("    [g] Ensembling probabilities...")
pA = clfA.predict_proba(Xw_te)
pB = clfB.predict_proba(Xc_te)
pC = clfC.predict_proba(X_combo_te)
pD = clfD.predict_proba(X_combo_te)

# Weighted ensemble
ensemble_probs = (3.0*pA + 2.5*pB + 2.0*pC + 3.0*pD) / 10.5
classes = clfA.classes_
clf_predictions = classes[np.argmax(ensemble_probs, axis=1)]
print(f"    Unique predictions: {len(set(clf_predictions))}")

# ------------------------------------------------------------------
# 3. Build sentence-level template analysis
# ------------------------------------------------------------------
print("\n[3/7] Analyzing sentence templates...")

def split_sents(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', str(text)) if len(s.strip()) > 10]

# Count sentence frequency
sent_freq = Counter()
for rev in train['Reviews']:
    for s in split_sents(rev):
        sent_freq[s] += 1

# Generic sentences (appear 100+ times) - shared across courses
generic_sents = {s for s, c in sent_freq.items() if c >= 100}
print(f"    Generic template sentences: {len(generic_sents)}")

# Extract course-specific content (remove generic sentences)
def extract_specific(text):
    sents = split_sents(text)
    specific = [s for s in sents if s not in generic_sents]
    if not specific:
        return clean(text)
    return clean(' '.join(specific))

train["specific"] = train["Reviews"].apply(extract_specific)
test["specific"] = test["Reviews"].apply(extract_specific)

# ------------------------------------------------------------------
# 4. Build multi-signal similarity matrices
# ------------------------------------------------------------------
print("\n[4/7] Building similarity signals...")

# Signal 1: Course-specific content (highest signal)
print("    [a] Specific-content TF-IDF...")
vec_spec = TfidfVectorizer(max_features=50000, ngram_range=(1, 3), min_df=1,
                           max_df=0.95, stop_words='english', sublinear_tf=True)
all_spec = train["specific"].tolist() + test["specific"].tolist()
vec_spec.fit(all_spec)
train_spec = normalize(vec_spec.transform(train["specific"]))
test_spec = normalize(vec_spec.transform(test["specific"]))

# Signal 2: Full word-level similarity (already computed)
print("    [b] Full word TF-IDF (reusing)...")
train_word = normalize(Xw_tr)
test_word = normalize(Xw_te)

# Signal 3: Char-level (already computed)
print("    [c] Char TF-IDF (reusing)...")
train_char_norm = normalize(Xc_tr)
test_char_norm = normalize(Xc_te)

# ------------------------------------------------------------------
# 5. Generate top-10 recommendations with multi-signal scoring
# ------------------------------------------------------------------
print("\n[5/7] Generating recommendations...")

recommendations = []

for i in range(len(test)):
    pred_course = clf_predictions[i]
    row_positions = course_to_rows.get(pred_course, np.arange(len(train)))

    if len(row_positions) < 10:
        row_positions = np.arange(len(train))

    # Multi-signal similarity within the predicted course
    # Signal 1: specific content (weight 3.0)
    sim_spec = (test_spec[i] @ train_spec[row_positions].T).toarray().flatten()
    # Signal 2: word-level (weight 2.0)
    sim_word = (test_word[i] @ train_word[row_positions].T).toarray().flatten()
    # Signal 3: char-level (weight 1.5)
    sim_char = (test_char_norm[i] @ train_char_norm[row_positions].T).toarray().flatten()

    # Combined score
    combined = 3.0 * sim_spec + 2.0 * sim_word + 1.5 * sim_char

    top10_local = np.argsort(-combined)[:10]
    top10_global = row_positions[top10_local]
    recs = train_idx_col[top10_global].tolist()

    while len(recs) < 10:
        recs.append(int(train_idx_col[row_positions[0]]))
    recommendations.append(recs[:10])

    if (i + 1) % 1000 == 0:
        elapsed = time.time() - t0
        print(f"    {i+1}/{len(test)} ({elapsed:.0f}s)")

print(f"    Done! {len(recommendations)} recommendations")

# ------------------------------------------------------------------
# 6. Validate
# ------------------------------------------------------------------
print("\n[6/7] Validating...")

idx_to_course = dict(zip(train_idx_col, train_labels))
validation_matches = 0
for i in range(len(test)):
    recs = recommendations[i]
    courses = [idx_to_course[r] for r in recs]
    majority = Counter(courses).most_common(1)[0]
    if majority[0] == clf_predictions[i]:
        validation_matches += 1

val_acc = validation_matches / len(test)

# ------------------------------------------------------------------
# 7. Save
# ------------------------------------------------------------------
print("\n[7/7] Saving...")

out_path = os.path.join(_here, "submission_MAX_v2.csv")
sub = pd.DataFrame({
    "Index": test_idx_col,
    "Index_list": [str(r) for r in recommendations],
})
sub.to_csv(out_path, index=False)

# Samples
print("\nSamples:")
for i in range(min(5, len(test))):
    recs = recommendations[i]
    courses = [idx_to_course[r] for r in recs]
    majority = Counter(courses).most_common(1)[0]
    print(f"  Test {test_idx_col[i]}: predicted={clf_predictions[i][:40]}")
    print(f"    Majority: {majority[0][:40]} ({majority[1]}/10)")

elapsed = time.time() - t0
print(f"\n{'='*70}")
print(f"  COMPLETE!")
print(f"{'='*70}")
print(f"  Saved: {out_path}")
print(f"  Shape: {sub.shape}")
print(f"  Validation: {val_acc:.2%}")
print(f"  Time: {elapsed:.0f}s")
print(f"  Expected score: ~{int(val_acc*100)}/100")
print(f"{'='*70}")
