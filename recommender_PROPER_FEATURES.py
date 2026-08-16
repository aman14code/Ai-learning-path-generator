import pandas as pd
import numpy as np
import re
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import VotingClassifier
from scipy.sparse import hstack
from scipy.sparse import csr_matrix
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
print("PROPER FEATURE ENGINEERING - TARGET 80-85/100")
print("="*80)

# Load original data (don't remove course names!)
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

# ADVANCED FEATURE ENGINEERING
def extract_advanced_features(df):
    df = df.copy()
    
    # Length features  
    df['review_length'] = df['clean'].str.len()
    df['word_count'] = df['clean'].str.split().str.len()
    
    # Programming keywords
    programming_words = ['python', 'javascript', 'java', 'react', 'node', 'html', 'css']
    df['programming_score'] = df['clean'].apply(
        lambda x: sum(1 for word in programming_words if word in x)
    )
    
    # Learning keywords
    learning_words = ['learn', 'understand', 'tutorial', 'beginner', 'advanced', 'project']
    df['learning_score'] = df['clean'].apply(
        lambda x: sum(1 for word in learning_words if word in x)
    )
    
    # Sentiment indicators
    positive_words = ['great', 'excellent', 'amazing', 'perfect', 'love', 'recommend']
    negative_words = ['bad', 'terrible', 'boring', 'difficult', 'confusing']
    
    df['positive_score'] = df['clean'].apply(
        lambda x: sum(1 for word in positive_words if word in x)
    )
    df['negative_score'] = df['clean'].apply(
        lambda x: sum(1 for word in negative_words if word in x)
    )
    
    return df

print("\n[2] Extracting advanced features...")
train = extract_advanced_features(train)
test = extract_advanced_features(test)

# MULTIPLE TF-IDF CONFIGURATIONS
print("\n[3] Extracting TF-IDF features...")

# Config 1: Word 1-3 grams
vec1 = TfidfVectorizer(max_features=80000, ngram_range=(1,3), min_df=1, max_df=0.95, 
                       stop_words='english', sublinear_tf=True)
X1_train = vec1.fit_transform(train["clean"])
X1_test = vec1.transform(test["clean"])

# Config 2: Char 3-6 grams  
vec2 = TfidfVectorizer(max_features=60000, analyzer='char_wb', ngram_range=(3,6), 
                       min_df=1, max_df=0.95, sublinear_tf=True)
X2_train = vec2.fit_transform(train["clean"])
X2_test = vec2.transform(test["clean"])

# Config 3: Word 1-2 grams (different params)
vec3 = TfidfVectorizer(max_features=50000, ngram_range=(1,2), min_df=2, max_df=0.9, 
                       stop_words='english', sublinear_tf=True)  
X3_train = vec3.fit_transform(train["clean"])
X3_test = vec3.transform(test["clean"])

# Combine text features
X_text_train = hstack([X1_train, X2_train, X3_train])
X_text_test = hstack([X1_test, X2_test, X3_test])

# Add manual features
manual_features = ['review_length', 'word_count', 'programming_score', 
                   'learning_score', 'positive_score', 'negative_score']

manual_train = csr_matrix(train[manual_features].values)
manual_test = csr_matrix(test[manual_features].values)

# Final combined features
X_train_final = hstack([X_text_train, manual_train])
X_test_final = hstack([X_text_test, manual_test])

print(f"    Total features: {X_train_final.shape[1]}")

# ADVANCED ENSEMBLE
print("\n[4] Training advanced ensemble...")

# Multiple classifiers with different parameters
classifiers = [
    ('lr1', LogisticRegression(C=1.0, max_iter=1000, random_state=42)),
    ('lr2', LogisticRegression(C=2.0, max_iter=1000, random_state=43)), 
    ('lr3', LogisticRegression(C=0.5, max_iter=1000, random_state=44)),
]

# Voting ensemble
ensemble = VotingClassifier(estimators=classifiers, voting='soft', n_jobs=1)
ensemble.fit(X_train_final, train["Course"])

predictions = ensemble.predict(X_test_final)

print("\n[5] Generating top-10 recommendations...")

# Same top-10 selection logic as before
course_to_indices = {course: np.where(train["Course"] == course)[0] 
                    for course in train["Course"].unique()}

vec_sim = TfidfVectorizer(max_features=50000, ngram_range=(1,2), min_df=1, max_df=0.95, 
                         stop_words='english', sublinear_tf=True)
vec_sim.fit(train["clean"].tolist() + test["clean"].tolist())

train_mat = normalize(vec_sim.transform(train["clean"]))
test_mat = normalize(vec_sim.transform(test["clean"]))

recommendations = []

for i in range(len(test)):
    pred_course = predictions[i]
    course_indices = course_to_indices.get(pred_course, np.array([]))
    
    if len(course_indices) == 0:
        course_indices = np.arange(len(train))
    
    course_mat = train_mat[course_indices]
    sims = (test_mat[i] @ course_mat.T).toarray().flatten()
    
    top10_local = np.argsort(-sims)[:10]
    top10_global = course_indices[top10_local]
    recs = train["Index"].values[top10_global].tolist()
    
    while len(recs) < 10:
        recs.append(train["Index"].values[course_indices[0]])
    
    recommendations.append(recs[:10])

# Save submission
print("\n[6] Saving submission...")
out_path = os.path.join(_here, "submission_PROPER_FEATURES.csv")
submission = pd.DataFrame({
    "Index": test["Index"].values,
    "Index_list": [str(r) for r in recommendations],
})
submission.to_csv(out_path, index=False)

print("\n="*80)
print(f"DONE! Saved to {out_path}")
print("="*80)
