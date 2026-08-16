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

print("[1] Loading data...")
train = pd.read_csv(find_file("train.csv"))
test  = pd.read_csv(find_file("test.csv"))
print(f"    Train: {train.shape} | Test: {test.shape}")

train_idx  = train["Index"].values
test_idx   = test["Index"].values
courses    = train["Course"].values

def clean(text):
    if pd.isna(text): return ""
    text = str(text).lower()
    text = re.sub(r"http\S+|www\S+|\S+@\S+", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return re.sub(r"\s+", " ", text).strip()

print("[2] Cleaning text...")
train_texts = train["Reviews"].apply(clean).tolist()
test_texts  = test["Reviews"].apply(clean).tolist()
all_texts   = train_texts + test_texts

# Build course profile: aggregate all reviews per course into one document
print("[3] Building course profiles...")
course_profiles = train.groupby("Course")["Reviews"].apply(lambda x: " ".join(x.apply(clean))).reset_index()
course_names    = course_profiles["Course"].values
profile_texts   = course_profiles["Reviews"].tolist()
n_courses       = len(course_names)

# Map course name -> list of train indices (for picking best representative)
course_to_train_rows = {}
for c, grp in train.groupby("Course"):
    course_to_train_rows[c] = grp.index.values  # dataframe positions

print(f"    Courses: {n_courses}")

print("[4] Extracting features...")

fit_texts = all_texts + profile_texts

vec_w12 = TfidfVectorizer(max_features=40000, ngram_range=(1,2), min_df=1, max_df=0.95,
                           stop_words="english", sublinear_tf=True, strip_accents="unicode")
vec_w12.fit(fit_texts)
train_w12   = normalize(vec_w12.transform(train_texts))
test_w12    = normalize(vec_w12.transform(test_texts))
profile_w12 = normalize(vec_w12.transform(profile_texts))
print(f"    TF-IDF (1,2): train={train_w12.shape}, profiles={profile_w12.shape}")

vec_w13 = TfidfVectorizer(max_features=50000, ngram_range=(1,3), min_df=1, max_df=0.95,
                           stop_words="english", sublinear_tf=True, strip_accents="unicode")
vec_w13.fit(fit_texts)
train_w13   = normalize(vec_w13.transform(train_texts))
test_w13    = normalize(vec_w13.transform(test_texts))
profile_w13 = normalize(vec_w13.transform(profile_texts))
print(f"    TF-IDF (1,3): done")

vec_ch = TfidfVectorizer(max_features=30000, analyzer="char_wb", ngram_range=(3,5),
                          min_df=1, max_df=0.95, sublinear_tf=True)
vec_ch.fit(fit_texts)
train_ch   = normalize(vec_ch.transform(train_texts))
test_ch    = normalize(vec_ch.transform(test_texts))
profile_ch = normalize(vec_ch.transform(profile_texts))
print(f"    Char ngrams: done")

svd = TruncatedSVD(n_components=200, random_state=42)
svd.fit(normalize(vec_w12.transform(fit_texts)))
train_svd   = normalize(svd.transform(train_w12))
test_svd    = normalize(svd.transform(test_w12))
profile_svd = normalize(svd.transform(profile_w12))
print(f"    SVD-200: done")

print("[5] Computing test-to-course similarity (for course ranking)...")

WEIGHTS = {"w12": 2.5, "w13": 2.0, "ch": 1.5, "svd": 2.0}
W_TOTAL = sum(WEIGHTS.values())

def norm01(m):
    mn = m.min(axis=1, keepdims=True)
    mx = m.max(axis=1, keepdims=True)
    return (m - mn) / np.clip(mx - mn, 1e-9, None)

# Course-level similarity: test vs course profiles
sim_c_w12 = (test_w12  @ profile_w12.T).toarray()
sim_c_w13 = (test_w13  @ profile_w13.T).toarray()
sim_c_ch  = (test_ch   @ profile_ch.T).toarray()
sim_c_svd =  test_svd  @ profile_svd.T
if hasattr(sim_c_svd, "toarray"):
    sim_c_svd = sim_c_svd.toarray()

course_sim = (
    WEIGHTS["w12"] * norm01(sim_c_w12) +
    WEIGHTS["w13"] * norm01(sim_c_w13) +
    WEIGHTS["ch"]  * norm01(sim_c_ch)  +
    WEIGHTS["svd"] * norm01(sim_c_svd)
) / W_TOTAL

print(f"    Course similarity matrix: {course_sim.shape}")

print("[6] Computing test-to-review similarity (for best rep per course)...")

CHUNK = 500
N_TEST = len(test_texts)
TOP_K  = 10

# Also compute individual review similarity to pick the BEST review per course
# This is done in chunks to save memory
all_row_sims = np.zeros((N_TEST, len(train_texts)), dtype=np.float32)

chunk_starts = list(range(0, N_TEST, CHUNK))
if HAS_TQDM:
    chunk_starts = tqdm(chunk_starts, desc="  Row sims", ncols=70)

for start in chunk_starts:
    end   = min(start + CHUNK, N_TEST)
    batch = slice(start, end)

    s_w12 = (test_w12[batch] @ train_w12.T).toarray()
    s_w13 = (test_w13[batch] @ train_w13.T).toarray()
    s_ch  = (test_ch[batch]  @ train_ch.T).toarray()
    s_svd =  test_svd[batch] @ train_svd.T
    if hasattr(s_svd, "toarray"):
        s_svd = s_svd.toarray()

    row_sim = (
        WEIGHTS["w12"] * norm01(s_w12) +
        WEIGHTS["w13"] * norm01(s_w13) +
        WEIGHTS["ch"]  * norm01(s_ch)  +
        WEIGHTS["svd"] * norm01(s_svd)
    ) / W_TOTAL

    all_row_sims[start:end] = row_sim.astype(np.float32)

print(f"    Row similarity matrix: {all_row_sims.shape}")

print("[7] Generating recommendations (top-10 diverse courses)...")

recommendations = []

for i in range(N_TEST):
    top10_course_pos = np.argsort(-course_sim[i])[:TOP_K]
    recs = []
    for cpos in top10_course_pos:
        cname     = course_names[cpos]
        row_pos   = course_to_train_rows[cname]          # dataframe positions in train
        best_pos  = row_pos[np.argmax(all_row_sims[i][row_pos])]
        recs.append(int(train_idx[best_pos]))
    recommendations.append(recs)

print(f"    Generated {len(recommendations)} recommendations")

print("[8] Saving submission...")
out_path = os.path.join(_here, "submission_FINAL_v3.csv")
sub = pd.DataFrame({
    "Index":      test_idx,
    "Index_list": [str(r) for r in recommendations],
})
sub.to_csv(out_path, index=False)
print(f"    Saved -> {out_path}  ({sub.shape[0]} rows)")
print(sub.head(3).to_string())

print()
import ast
idx_to_course = dict(zip(train["Index"].values, train["Course"].values))
for i in range(3):
    recs    = recommendations[i]
    courses_rec = [idx_to_course[r] for r in recs]
    print(f"Test {test_idx[i]}: \"{test['Reviews'].iloc[i][:80]}...\"")
    print(f"  -> Courses: {courses_rec}")
    print()

print("DONE! Submit: submission_FINAL_v3.csv")
