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
from sklearn.model_selection import train_test_split
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
    
    all_labels = train["Course"].values
    all_texts = train["clean"].tolist()
    
    # Split for accuracy measurement
    X_train_text, X_test_text, y_train, y_test = train_test_split(
        all_texts, all_labels, test_size=0.15, random_state=42, stratify=all_labels
    )
    
    print(f"    Train: {len(X_train_text)} samples | Test: {len(X_test_text)} samples")
    print(f"    Classes: {len(np.unique(all_labels))} courses")
    
    print("[2] Building Vectorizers...")
    
    # Word-level TF-IDF
    vec_word = TfidfVectorizer(max_features=80000, ngram_range=(1,3),
                                min_df=1, max_df=0.95, stop_words="english",
                                sublinear_tf=True, strip_accents="unicode")
    Xw_tr = vec_word.fit_transform(X_train_text)
    Xw_te = vec_word.transform(X_test_text)
    
    # Char-level TF-IDF (optimized for speed)
    vec_char = TfidfVectorizer(max_features=20000, analyzer="char_wb",
                                ngram_range=(3,4), min_df=2, max_df=0.90,
                                sublinear_tf=True)
    Xc_tr = vec_char.fit_transform(X_train_text)
    Xc_te = vec_char.transform(X_test_text)
    
    X_combo_tr = hstack([Xw_tr, Xc_tr])
    X_combo_te = hstack([Xw_te, Xc_te])
    
    print("[3] Training Ensemble Models...")
    
    print("  -> Training LogReg Word (C=2.0)...")
    clfA = LogisticRegression(C=2.0, max_iter=500, solver="liblinear", random_state=42)
    clfA.fit(Xw_tr, y_train)
    accA = (clfA.predict(Xw_te) == y_test).mean()
    print(f"     LogReg Word Accuracy: {accA:.4f} ({accA*100:.1f}%)")
    
    print("  -> Training LogReg Char (C=2.0)...")
    clfB = LogisticRegression(C=2.0, max_iter=500, solver="liblinear", random_state=43)
    clfB.fit(Xc_tr, y_train)
    accB = (clfB.predict(Xc_te) == y_test).mean()
    print(f"     LogReg Char Accuracy: {accB:.4f} ({accB*100:.1f}%)")
    
    print("  -> Training LinearSVC Combo (Calibrated, cv='prefit')...")
    svc = LinearSVC(C=1.0, max_iter=3000, random_state=42, dual="auto")
    svc.fit(X_combo_tr, y_train)
    clfC = CalibratedClassifierCV(svc, cv="prefit")
    clfC.fit(X_combo_tr, y_train)
    accC = (clfC.predict(X_combo_te) == y_test).mean()
    print(f"     LinearSVC Combo Accuracy: {accC:.4f} ({accC*100:.1f}%)")
    
    # Ensemble accuracy
    print("[4] Measuring Ensemble Accuracy...")
    pA = clfA.predict_proba(Xw_te)
    pB = clfB.predict_proba(Xc_te)
    pC = clfC.predict_proba(X_combo_te)
    ensemble_probs = (3.0*pA + 2.5*pB + 2.0*pC) / 7.5
    ensemble_preds = clfA.classes_[np.argmax(ensemble_probs, axis=1)]
    ensemble_acc = (ensemble_preds == y_test).mean()
    print(f"     *** ENSEMBLE ACCURACY: {ensemble_acc:.4f} ({ensemble_acc*100:.1f}%) ***")
    
    # Now retrain on ALL data for maximum production accuracy
    print("[5] Retraining on FULL dataset for production...")
    Xw_all = vec_word.fit_transform(all_texts)
    Xc_all = vec_char.fit_transform(all_texts)
    X_combo_all = hstack([Xw_all, Xc_all])
    
    clfA.fit(Xw_all, all_labels)
    clfB.fit(Xc_all, all_labels)
    
    svc_all = LinearSVC(C=1.0, max_iter=3000, random_state=42, dual="auto")
    svc_all.fit(X_combo_all, all_labels)
    clfC = CalibratedClassifierCV(svc_all, cv="prefit")
    clfC.fit(X_combo_all, all_labels)
    
    print("[6] Saving Models to Disk...")
    out_path = os.path.join(DATA_DIR, "ultimate_model.pkl")
    with open(out_path, "wb") as f:
        pickle.dump({
            "vec_word": vec_word,
            "vec_char": vec_char,
            "clfA": clfA,
            "clfB": clfB,
            "clfC": clfC,
            "classes": clfA.classes_,
            "ensemble_accuracy": ensemble_acc,
        }, f)
        
    size_mb = os.path.getsize(out_path) / (1024*1024)
    print(f"[DONE] Saved to {out_path} ({size_mb:.1f} MB)")
    print(f"[DONE] Ensemble Accuracy: {ensemble_acc*100:.1f}%")
    print("Backend is ready to use the Ultimate Ensemble!")

if __name__ == "__main__":
    main()

