import pandas as pd
import numpy as np
import re
import warnings
import os
warnings.filterwarnings("ignore")

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import normalize

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False
    def tqdm(x, **kw): return x

_here    = os.path.dirname(os.path.abspath(__file__))
_desktop = r"c:\Users\amans\OneDrive\Desktop"

def find_file(name):
    for folder in [_here, _desktop, os.getcwd()]:
        p = os.path.join(folder, name)
        if os.path.exists(p) and os.path.getsize(p) > 1000:
            return p
    raise FileNotFoundError(f"Cannot find {name}")

train = pd.read_csv(find_file("train.csv"))
test  = pd.read_csv(find_file("test.csv"))

def clean(text):
    if pd.isna(text):
        return ""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+|\S+@\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

train_texts = train["Reviews"].apply(clean).tolist()
test_texts  = test["Reviews"].apply(clean).tolist()
train_idx   = train["Index"].values
test_idx    = test["Index"].values

all_texts = train_texts + test_texts

vec_w12 = TfidfVectorizer(max_features=40000, ngram_range=(1, 2), min_df=1, max_df=0.95, stop_words="english", sublinear_tf=True, strip_accents="unicode")
vec_w12.fit(all_texts)
train_w12 = normalize(vec_w12.transform(train_texts))
test_w12  = normalize(vec_w12.transform(test_texts))

vec_w13 = TfidfVectorizer(max_features=50000, ngram_range=(1, 3), min_df=1, max_df=0.95, stop_words="english", sublinear_tf=True, strip_accents="unicode")
vec_w13.fit(all_texts)
train_w13 = normalize(vec_w13.transform(train_texts))
test_w13  = normalize(vec_w13.transform(test_texts))

vec_ch = TfidfVectorizer(max_features=30000, analyzer="char_wb", ngram_range=(3, 5), min_df=1, max_df=0.95, sublinear_tf=True)
vec_ch.fit(all_texts)
train_ch = normalize(vec_ch.transform(train_texts))
test_ch  = normalize(vec_ch.transform(test_texts))

svd = TruncatedSVD(n_components=200, random_state=42)
svd.fit(normalize(vec_w12.transform(all_texts)))
train_svd = normalize(svd.transform(train_w12))
test_svd  = normalize(svd.transform(test_w12))

WEIGHTS = {"w12": 2.5, "w13": 2.0, "ch": 1.5, "svd": 2.0}
W_TOTAL = sum(WEIGHTS.values())
N_TEST  = len(test_texts)
TOP_K   = 10
CHUNK   = 500

recommendations = []

def norm01(m):
    mn = m.min(axis=1, keepdims=True)
    mx = m.max(axis=1, keepdims=True)
    return (m - mn) / np.clip(mx - mn, 1e-9, None)

chunk_starts = list(range(0, N_TEST, CHUNK))
if HAS_TQDM:
    chunk_starts = tqdm(chunk_starts, desc="Progress", ncols=70)

for start in chunk_starts:
    end   = min(start + CHUNK, N_TEST)
    batch = slice(start, end)

    s_w12 = (test_w12[batch] @ train_w12.T).toarray()
    s_w13 = (test_w13[batch] @ train_w13.T).toarray()
    s_ch  = (test_ch[batch]  @ train_ch.T).toarray()
    s_svd =  test_svd[batch] @ train_svd.T
    if hasattr(s_svd, "toarray"):
        s_svd = s_svd.toarray()

    ensemble = (
        WEIGHTS["w12"] * norm01(s_w12) +
        WEIGHTS["w13"] * norm01(s_w13) +
        WEIGHTS["ch"]  * norm01(s_ch)  +
        WEIGHTS["svd"] * norm01(s_svd)
    ) / W_TOTAL

    for row_pos in np.argsort(-ensemble, axis=1)[:, :TOP_K]:
        recommendations.append(train_idx[row_pos].tolist())

out_path = os.path.join(_here, "submission_FINAL_v2.csv")
sub = pd.DataFrame({
    "Index":      test_idx,
    "Index_list": [str(r) for r in recommendations],
})
sub.to_csv(out_path, index=False)
print(f"Done! Saved -> {out_path}  ({sub.shape[0]} rows)")
print(sub.head(3).to_string())
