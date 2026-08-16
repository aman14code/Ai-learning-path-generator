import pandas as pd
import re
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression, RidgeClassifier, PassiveAggressiveClassifier
from sklearn.metrics import recall_score
import os

desk = r'c:\Users\amans\OneDrive\Desktop'
train = pd.read_csv(os.path.join(desk, 'train.csv'))

def clean(t):
    if pd.isna(t): return ""
    return re.sub(r'[^a-z0-9\s]', ' ', str(t).lower())

train['c'] = train['Reviews'].apply(clean)
X_tr, X_val, y_tr, y_val = train_test_split(train['c'], train['Course'], test_size=0.2, random_state=42)

vec = TfidfVectorizer(max_features=80000, ngram_range=(1,2), sublinear_tf=True)
X_tr_v = vec.fit_transform(X_tr)
X_val_v = vec.transform(X_val)

models = {
    'SVC (C=1.0)': LinearSVC(C=1.0, random_state=42),
    'SVC (C=0.5)': LinearSVC(C=0.5, random_state=42),
    'SVC (C=2.0)': LinearSVC(C=2.0, random_state=42),
    'LogReg (C=2.0)': LogisticRegression(C=2.0, max_iter=500, random_state=42),
    'Ridge': RidgeClassifier(random_state=42),
    'PAC': PassiveAggressiveClassifier(random_state=42)
}

print("Validation Macro-Recall Scores:")
for name, m in models.items():
    m.fit(X_tr_v, y_tr)
    p = m.predict(X_val_v)
    score = recall_score(y_val, p, average='macro')
    print(f"{name}: {score * 100:.2f}%")
