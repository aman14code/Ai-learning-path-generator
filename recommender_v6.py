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
from sklearn.naive_bayes import MultinomialNB
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import normalize

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

train_labels = train["Course"].values
train_idx    = train["Index"].values
test_idx     = test["Index"].values
all_texts    = train["clean"].tolist() + test["clean"].tolist()

print("[3] Vectorizing (word + char ngrams)...")

vec_word = TfidfVectorizer(max_features=80000, ngram_range=(1,3),
                            min_df=1, max_df=0.95, stop_words="english",
                            sublinear_tf=True, strip_accents="unicode")
vec_word.fit(all_texts)
Xw_train = vec_word.transform(train["clean"].tolist())
Xw_test  = vec_word.transform(test["clean"].tolist())
print(f"    Word features: {Xw_train.shape[1]}")

vec_char = TfidfVectorizer(max_features=60000, analyzer="char_wb",
                            ngram_range=(3,6), min_df=1, max_df=0.95,
                            sublinear_tf=True)
vec_char.fit(all_texts)
Xc_train = vec_char.transform(train["clean"].tolist())
Xc_test  = vec_char.transform(test["clean"].tolist())
print(f"    Char features: {Xc_train.shape[1]}")

# Combined matrix for classifiers that can handle it
X_combo_train = hstack([Xw_train, Xc_train])
X_combo_test  = hstack([Xw_test,  Xc_test])
print(f"    Combined: {X_combo_train.shape[1]}")

print("[4] Training 4 classifiers...")

# C1: LogisticRegression on word features
clf1 = LogisticRegression(C=1.5, max_iter=2000, solver="saga",
                           multi_class="multinomial", random_state=42, n_jobs=-1)
clf1.fit(Xw_train, train_labels)
acc1 = (clf1.predict(Xw_train) == train_labels).mean()
print(f"    C1 LogReg-word   train acc: {acc1*100:.2f}%")

# C2: LogisticRegression on char features
clf2 = LogisticRegression(C=1.5, max_iter=2000, solver="saga",
                           multi_class="multinomial", random_state=43, n_jobs=-1)
clf2.fit(Xc_train, train_labels)
acc2 = (clf2.predict(Xc_train) == train_labels).mean()
print(f"    C2 LogReg-char   train acc: {acc2*100:.2f}%")

# C3: LinearSVC on combined (calibrated for probabilities)
svc = LinearSVC(C=1.0, max_iter=3000, random_state=42, dual=True)
clf3 = CalibratedClassifierCV(svc, cv=3)
clf3.fit(X_combo_train, train_labels)
acc3 = (clf3.predict(X_combo_train) == train_labels).mean()
print(f"    C3 SVC-combo     train acc: {acc3*100:.2f}%")

# C4: Naive Bayes on word features (fast, different inductive bias)
clf4 = MultinomialNB(alpha=0.05)
clf4.fit(Xw_train, train_labels)
acc4 = (clf4.predict(Xw_train) == train_labels).mean()
print(f"    C4 NaiveBayes    train acc: {acc4*100:.2f}%")

print("[5] Weighted probability ensemble...")
p1 = clf1.predict_proba(Xw_test)
p2 = clf2.predict_proba(Xc_test)
p3 = clf3.predict_proba(X_combo_test)
p4 = clf4.predict_proba(Xw_test)

# Weights proportional to train accuracy
W = [3.0, 2.5, 2.0, 1.0]
ensemble_probs = (W[0]*p1 + W[1]*p2 + W[2]*p3 + W[3]*p4) / sum(W)

classes         = clf1.classes_
predicted_courses = classes[np.argmax(ensemble_probs, axis=1)]
print(f"    Unique courses predicted: {len(set(predicted_courses))}")

print("[6] Picking top-10 similar reviews from predicted course...")

course_to_rows = {c: np.where(train_labels == c)[0] for c in train["Course"].unique()}

train_mat = normalize(vec_word.transform(train["clean"].tolist()))
test_mat  = normalize(vec_word.transform(test["clean"].tolist()))

try:
    from tqdm import tqdm
    itr = tqdm(range(len(test)), desc="Recs", ncols=70)
except ImportError:
    itr = range(len(test))

recommendations = []
for i in itr:
    pred_course   = predicted_courses[i]
    row_positions = course_to_rows.get(pred_course, np.arange(len(train)))
    sims = (test_mat[i] @ train_mat[row_positions].T).toarray().flatten()
    top10_global  = row_positions[np.argsort(-sims)[:10]]
    recs = train_idx[top10_global].tolist()
    while len(recs) < 10:
        recs.append(int(train_idx[row_positions[0]]))
    recommendations.append(recs[:10])

print(f"    Generated {len(recommendations)} recommendations")

print("[7] Saving submission...")
out_path = os.path.join(_here, "submission_FINAL_v6.csv")
sub = pd.DataFrame({
    "Index":      test_idx,
    "Index_list": [str(r) for r in recommendations],
})
sub.to_csv(out_path, index=False)
print(f"    Saved -> {out_path}  ({sub.shape[0]} rows)")
print(sub.head(3).to_string())

print()
from collections import Counter
for i in range(3):
    recs    = recommendations[i]
    courses = [train[train["Index"] == r]["Course"].values[0] for r in recs]
    mv      = Counter(courses).most_common(1)[0]
    print(f"Test {test_idx[i]}: predicted={predicted_courses[i]}")
    print(f"  -> Majority: {mv[0]} ({mv[1]}/10)")
print()
print("DONE! Submit: submission_FINAL_v6.csv")
