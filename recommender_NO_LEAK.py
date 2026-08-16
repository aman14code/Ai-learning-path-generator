import pandas as pd
import numpy as np
import re
import os
import warnings
warnings.filterwarnings("ignore")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.calibration import CalibratedClassifierCV
from scipy.sparse import hstack
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
print("ULTIMATE DATA-LEAK FIX - TARGET 95-100/100 (NO GPU NEEDED)")
print("="*80)

print("\n[1] Loading data...")
train = pd.read_csv(find_file("train.csv"))
test = pd.read_csv(find_file("test.csv"))
print(f"    Train: {train.shape} | Test: {test.shape}")

def clean(text):
    if pd.isna(text): return ""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+|\S+@\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

print("\n[2] Fixing the Data Leak (Removing Course Names from Train Data)...")
# We discovered EVERY training review contains the exact course name.
# Test reviews DO NOT. This confused the previous models.
# By removing the course name, the model is forced to learn the actual syllabus keywords!

cleaned_train_texts = []
for i, row in train.iterrows():
    review = clean(row['Reviews'])
    course = clean(row['Course'])
    
    # Remove the exact course string from the review
    review = review.replace(course, " ")
    
    # Also remove individual words of the course name if they are distinct
    for word in course.split():
        if len(word) > 3:
            review = review.replace(word, " ")
            
    # Clean up multiple spaces
    review = re.sub(r"\s+", " ", review).strip()
    cleaned_train_texts.append(review)

train["clean"] = cleaned_train_texts
test["clean"] = test["Reviews"].apply(clean)

train_labels = train["Course"].values
train_idx = train["Index"].values
test_idx = test["Index"].values
all_texts = train["clean"].tolist() + test["clean"].tolist()

print("\n[3] Extracting features (Word + Char N-Grams)...")
vec_word = TfidfVectorizer(max_features=80000, ngram_range=(1,3), min_df=1, max_df=0.95, sublinear_tf=True)
vec_word.fit(all_texts)
Xw_tr = vec_word.transform(train["clean"])
Xw_te = vec_word.transform(test["clean"])

vec_char = TfidfVectorizer(max_features=60000, analyzer="char_wb", ngram_range=(3,6), min_df=1, max_df=0.95, sublinear_tf=True)
vec_char.fit(all_texts)
Xc_tr = vec_char.transform(train["clean"])
Xc_te = vec_char.transform(test["clean"])

X_combo_tr = hstack([Xw_tr, Xc_tr])
X_combo_te = hstack([Xw_te, Xc_te])

print("\n[4] Training unbiased models...")
# Model 1
clf1 = LogisticRegression(C=2.0, max_iter=1000, random_state=42, n_jobs=-1)
clf1.fit(Xw_tr, train_labels)

# Model 2
clf2 = LogisticRegression(C=2.0, max_iter=1000, random_state=43, n_jobs=-1)
clf2.fit(Xc_tr, train_labels)

# Model 3
svc = LinearSVC(C=1.0, max_iter=2000, random_state=42)
clf3 = CalibratedClassifierCV(svc, cv=3)
clf3.fit(X_combo_tr, train_labels)

print("\n[5] Ensembling probabilities...")
p1 = clf1.predict_proba(Xw_te)
p2 = clf2.predict_proba(Xc_te)
p3 = clf3.predict_proba(X_combo_te)

ensemble_probs = (p1 + p2 + p3) / 3.0
classes = clf1.classes_
predicted_courses = classes[np.argmax(ensemble_probs, axis=1)]

print(f"    Predicted {len(set(predicted_courses))} unique courses")

print("\n[6] Generating Top-10 recommendations for each test review...")
# Use TF-IDF within the predicted course to find the best 10 matches
train_mat = normalize(Xw_tr)
test_mat = normalize(Xw_te)
course_to_rows = {c: np.where(train_labels == c)[0] for c in train["Course"].unique()}

recommendations = []
try:
    from tqdm import tqdm
    itr = tqdm(range(len(test)), ncols=80)
except:
    itr = range(len(test))

for i in itr:
    pred_course = predicted_courses[i]
    row_positions = course_to_rows.get(pred_course, np.arange(len(train)))
    
    sims = (test_mat[i] @ train_mat[row_positions].T).toarray().flatten()
    top10_global = row_positions[np.argsort(-sims)[:10]]
    
    recs = train_idx[top10_global].tolist()
    while len(recs) < 10:
        recs.append(int(train_idx[row_positions[0]]))
    recommendations.append(recs[:10])

print("\n[7] Saving submission...")
out_path = os.path.join(_here, "submission_NO_LEAK_95plus.csv")
sub = pd.DataFrame({
    "Index": test_idx,
    "Index_list": [str(r) for r in recommendations],
})
sub.to_csv(out_path, index=False)
print(f"    Saved -> {out_path} ({sub.shape[0]} rows)")

from collections import Counter
for i in range(3):
    recs = recommendations[i]
    courses = [train[train["Index"] == r]["Course"].values[0] for r in recs]
    mv = Counter(courses).most_common(1)[0]
    print(f"\nTest {test_idx[i]}:")
    print(f"  Predicted: {predicted_courses[i]}")
    print(f"  Majority: {mv[0]} ({mv[1]}/10)")

print("\n="*80)
print("DONE! Submit submission_NO_LEAK_95plus.csv")
print("="*80)
