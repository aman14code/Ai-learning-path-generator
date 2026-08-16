import pandas as pd
import numpy as np
import re
import warnings
import os
warnings.filterwarnings("ignore")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
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

print("[3] Training LinearSVC classifier...")
clf = Pipeline([
    ("tfidf", TfidfVectorizer(
        max_features=60000,
        ngram_range=(1, 3),
        min_df=1,
        max_df=0.95,
        stop_words="english",
        sublinear_tf=True,
        strip_accents="unicode"
    )),
    ("svc", LinearSVC(C=1.0, max_iter=2000, random_state=42))
])

clf.fit(train["clean"], train["Course"])

print("[4] Predicting course for each test review...")
predicted_courses = clf.predict(test["clean"])
print(f"    Predicted {len(predicted_courses)} courses")
print(f"    Unique courses predicted: {len(set(predicted_courses))}")

print("[5] Checking train-set accuracy (sanity check)...")
train_preds = clf.predict(train["clean"])
train_acc   = (train_preds == train["Course"].values).mean()
print(f"    Train accuracy: {train_acc*100:.2f}%")

print("[6] Picking top-10 most similar reviews from predicted course...")
from sklearn.feature_extraction.text import TfidfVectorizer as TV
from sklearn.preprocessing import normalize as nrm

vec = TV(max_features=40000, ngram_range=(1,2), min_df=1, max_df=0.95,
         stop_words="english", sublinear_tf=True, strip_accents="unicode")
vec.fit(all_texts)
train_mat = nrm(vec.transform(train["clean"].tolist()))
test_mat  = nrm(vec.transform(test["clean"].tolist()))

train_idx   = train["Index"].values
train_course= train["Course"].values
test_idx    = test["Index"].values

course_to_rows = {}
for c in train["Course"].unique():
    course_to_rows[c] = np.where(train_course == c)[0]

try:
    from tqdm import tqdm
    itr = tqdm(range(len(test)), desc="Generating recs", ncols=70)
except ImportError:
    itr = range(len(test))

recommendations = []
for i in itr:
    pred_course = predicted_courses[i]
    row_positions = course_to_rows.get(pred_course, np.array([]))
    if len(row_positions) == 0:
        row_positions = np.arange(len(train))
    course_mat = train_mat[row_positions]
    sims = (test_mat[i] @ course_mat.T).toarray().flatten()
    top10_local = np.argsort(-sims)[:10]
    top10_global = row_positions[top10_local]
    recs = train_idx[top10_global].tolist()
    while len(recs) < 10:
        recs.append(int(train_idx[row_positions[0]]))
    recommendations.append(recs[:10])

print(f"    Generated {len(recommendations)} recommendations")

print("[7] Saving submission...")
out_path = os.path.join(_here, "submission_FINAL_v4.csv")
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
    recs = recommendations[i]
    courses = [train[train["Index"] == r]["Course"].values[0] for r in recs]
    print(f"Test {test_idx[i]}: predicted={predicted_courses[i]}")
    print(f"  -> Majority course: {Counter(courses).most_common(1)[0][0]}")
    print()

print("DONE! Submit: submission_FINAL_v4.csv")
