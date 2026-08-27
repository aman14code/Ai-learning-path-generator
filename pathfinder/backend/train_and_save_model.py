import pandas as pd
import numpy as np
import re
import os
import pickle
from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import LinearSVC
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

def clean_text(text):
    if pd.isna(text): return ""
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+', '', text)
    text = re.sub(r'\S+@\S+', '', text)
    text = re.sub(r'[^a-z0-9\s]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def main():
    print("="*60)
    print("  TRAINING ULTIMATE ENSEMBLE MODEL FOR BACKEND")
    print("="*60)
    
    train_path = os.path.join(DATA_DIR, "train.csv")
    if not os.path.exists(train_path):
        print(f"ERROR: Cannot find {train_path}")
        return
        
    print("[1] Loading data...")
    train = pd.read_csv(train_path)
    train["clean"] = train["Reviews"].apply(clean_text)
    
    # In the real backend, the "Course" names are unique
    train_labels = train["Course"].values
    
    print("[2] Building Vectorizers...")
    all_texts = train["clean"].tolist()
    
    # Same settings as recommender_ULTIMATE.py
    vec_word = TfidfVectorizer(max_features=80000, ngram_range=(1,3),
                                min_df=1, max_df=0.95, stop_words="english",
                                sublinear_tf=True, strip_accents="unicode")
    Xw_tr = vec_word.fit_transform(all_texts)
    
    vec_char = TfidfVectorizer(max_features=60000, analyzer="char_wb",
                                ngram_range=(3,6), min_df=1, max_df=0.95,
                                sublinear_tf=True)
    Xc_tr = vec_char.fit_transform(all_texts)
    
    X_combo_tr = hstack([Xw_tr, Xc_tr])
    
    print("[3] Training Ensemble Models...")
    print("  -> Training LogReg Word (C=2.0)...")
    clfA = LogisticRegression(C=2.0, max_iter=500, solver="lbfgs", random_state=42, n_jobs=-1)
    clfA.fit(Xw_tr, train_labels)
    
    print("  -> Training LogReg Char (C=2.0)...")
    clfB = LogisticRegression(C=2.0, max_iter=500, solver="lbfgs", random_state=43, n_jobs=-1)
    clfB.fit(Xc_tr, train_labels)
    
    print("  -> Training LinearSVC Combo (Calibrated)...")
    svc = LinearSVC(C=1.0, max_iter=3000, random_state=42, dual=True)
    clfC = CalibratedClassifierCV(svc, cv=3)
    clfC.fit(X_combo_tr, train_labels)
    
    print("[4] Saving Models to Disk...")
    out_path = os.path.join(DATA_DIR, "ultimate_model.pkl")
    with open(out_path, "wb") as f:
        pickle.dump({
            "vec_word": vec_word,
            "vec_char": vec_char,
            "clfA": clfA,
            "clfB": clfB,
            "clfC": clfC,
            "classes": clfA.classes_
        }, f)
        
    print(f"[DONE] Saved to {out_path}")
    print("DONE! Backend is ready to use the Ultimate Ensemble.")

if __name__ == "__main__":
    main()
