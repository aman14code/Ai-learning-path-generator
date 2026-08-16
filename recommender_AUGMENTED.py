import pandas as pd
import numpy as np
import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import normalize
from scipy.sparse import hstack
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
print("DATA AUGMENTATION SOLVER - TARGET 95-100/100")
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

print("\n[2] Performing 50/50 Data Augmentation...")
# Create a scrubbed version of the training data
train_scrubbed = train.copy()

def scrub_course_name(row):
    text = row["clean"]
    course = str(row["Course"]).lower()
    # Remove all non-alphanumeric from course just like we did to text
    course = re.sub(r"[^a-z0-9\s]", " ", course)
    course = re.sub(r"\s+", " ", course).strip()
    return text.replace(course, "this course")

train_scrubbed["clean"] = train_scrubbed.apply(scrub_course_name, axis=1)

# Double the dataset! 110k -> 220k
train_augmented = pd.concat([train, train_scrubbed], ignore_index=True)
print(f"    Original training rows: {len(train)}")
print(f"    Augmented training rows: {len(train_augmented)}")

print("\n[3] Extracting TF-IDF Features...")
vec1 = TfidfVectorizer(max_features=80000, ngram_range=(1,2), min_df=2, max_df=0.95, stop_words='english', sublinear_tf=True)
vec2 = TfidfVectorizer(max_features=60000, analyzer='char_wb', ngram_range=(3,5), min_df=2, max_df=0.95, sublinear_tf=True)

print("    -> Fitting words...")
X1_train = vec1.fit_transform(train_augmented["clean"])
X1_test = vec1.transform(test["clean"])

print("    -> Fitting chars...")
X2_train = vec2.fit_transform(train_augmented["clean"])
X2_test = vec2.transform(test["clean"])

X_train_final = hstack([X1_train, X2_train])
X_test_final = hstack([X1_test, X2_test])

print(f"    Total features: {X_train_final.shape[1]}")

print("\n[4] Training Logistic Regression on Augmented Data...")
# We use max_iter=200, which is plenty for TF-IDF, C=1.0
clf = LogisticRegression(C=1.0, max_iter=200, random_state=42, n_jobs=1)
clf.fit(X_train_final, train_augmented["Course"])

print("\n[5] Predicting Test Courses...")
predictions = clf.predict(X_test_final)

print("\n[6] Generating Top-10 Recommendations via Cosine Similarity...")
# Build similarity matrix using ONLY the original training data (so we don't recommend duplicated indices)
course_to_indices = {course: np.where(train["Course"] == course)[0] for course in train["Course"].unique()}

vec_sim = TfidfVectorizer(max_features=50000, ngram_range=(1,2), min_df=1, max_df=0.95, stop_words='english', sublinear_tf=True)
vec_sim.fit(train["clean"].tolist() + test["clean"].tolist())

train_mat = normalize(vec_sim.transform(train["clean"]))
test_mat = normalize(vec_sim.transform(test["clean"]))

recommendations = []
for i in range(len(test)):
    pred_course = predictions[i]
    course_indices = course_to_indices.get(pred_course, np.array([]))
    if len(course_indices) == 0: course_indices = np.arange(len(train))
    
    course_mat = train_mat[course_indices]
    sims = (test_mat[i] @ course_mat.T).toarray().flatten()
    
    top10_local = np.argsort(-sims)[:10]
    top10_global = course_indices[top10_local]
    
    recs = train["Index"].values[top10_global].tolist()
    while len(recs) < 10: recs.append(train["Index"].values[course_indices[0]])
    recommendations.append(recs[:10])

print("\n[7] Saving submission...")
out_path = os.path.join(_here, "submission_AUGMENTED_95.csv")
submission = pd.DataFrame({
    "Index": test["Index"].values,
    "Index_list": [str(r) for r in recommendations],
})
submission.to_csv(out_path, index=False)
print("\n="*80)
print(f"🚀 DONE! Saved to {out_path}")
print("="*80)
