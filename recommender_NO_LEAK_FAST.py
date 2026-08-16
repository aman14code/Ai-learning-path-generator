import pandas as pd
import numpy as np
import re
import os
import warnings
warnings.filterwarnings("ignore")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import normalize

_here = os.path.dirname(os.path.abspath(__file__))
_desktop = r"c:\Users\amans\OneDrive\Desktop"

def find_file(name):
    for folder in [_here, _desktop, os.getcwd()]:
        p = os.path.join(folder, name)
        if os.path.exists(p) and os.path.getsize(p) > 1000:
            return p
    raise FileNotFoundError(f"Cannot find {name}")

print("="*80)
print("FAST DATA-LEAK FIX - (1 MINUTE RUNTIME)")
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

print("\n[2] Fixing the Data Leak...")

cleaned_train_texts = []
for i, row in train.iterrows():
    review = clean(row['Reviews'])
    course = clean(row['Course'])
    review = review.replace(course, " ")
    for word in course.split():
        if len(word) > 3:
            review = review.replace(word, " ")
    review = re.sub(r"\s+", " ", review).strip()
    cleaned_train_texts.append(review)

train["clean"] = cleaned_train_texts
test["clean"] = test["Reviews"].apply(clean)

train_labels = train["Course"].values
train_idx = train["Index"].values
test_idx = test["Index"].values
all_texts = train["clean"].tolist() + test["clean"].tolist()

print("\n[3] Extracting features (Word N-Grams Only for Speed)...")
vec = TfidfVectorizer(max_features=80000, ngram_range=(1,2), min_df=1, max_df=0.95, sublinear_tf=True)
vec.fit(all_texts)
X_tr = vec.transform(train["clean"])
X_te = vec.transform(test["clean"])

print("\n[4] Training single ultra-fast Logistic Regression...")
clf = LogisticRegression(C=2.0, max_iter=200, random_state=42, n_jobs=-1)
clf.fit(X_tr, train_labels)
predicted_courses = clf.predict(X_te)

print("\n[5] Generating Top-10 recommendations...")
train_mat = normalize(X_tr)
test_mat = normalize(X_te)
course_to_rows = {c: np.where(train_labels == c)[0] for c in train["Course"].unique()}

recommendations = []
for i in range(len(test)):
    pred_course = predicted_courses[i]
    row_positions = course_to_rows.get(pred_course, np.arange(len(train)))
    
    sims = (test_mat[i] @ train_mat[row_positions].T).toarray().flatten()
    top10_global = row_positions[np.argsort(-sims)[:10]]
    
    recs = train_idx[top10_global].tolist()
    while len(recs) < 10:
        recs.append(int(train_idx[row_positions[0]]))
    recommendations.append(recs[:10])

print("\n[6] Saving submission...")
out_path = os.path.join(_here, "submission_NO_LEAK_FAST.csv")
sub = pd.DataFrame({
    "Index": test_idx,
    "Index_list": [str(r) for r in recommendations],
})
sub.to_csv(out_path, index=False)

print("\n="*80)
print("DONE! Submit submission_NO_LEAK_FAST.csv")
print("="*80)
