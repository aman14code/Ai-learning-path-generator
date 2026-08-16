import pandas as pd, ast, numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

train = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\train.csv')
test  = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\test.csv')
final = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\HCL Simplified Hackathon\submission_MEGA_FINAL.csv')

print('=== FORMAT CHECK ===')
print(f'Train Index range  : {train["Index"].min()} - {train["Index"].max()}')
print(f'Test  Index range  : {test["Index"].min()} - {test["Index"].max()}')
print()

# Check what the current submission contains
all_rec = []
for r in final['Index_list']:
    all_rec.extend(ast.literal_eval(r))
print(f'Current submission rec index range: {min(all_rec)} - {max(all_rec)}')
print(f'Current submission unique rec indices: {len(set(all_rec))} (should be up to 109776)')
print()
print('Train Index column first 5 values:', train["Index"].head(5).tolist())
print()

# Verify: are those 0-279 values actual train Index values?
low_indices = [i for i in set(all_rec) if i < 280]
print(f'All rec values < 280: {sorted(low_indices)[:20]}')
print()
# What is train row at index 0, 1, 2... vs train "Index" column
print('Are values 0-279 valid train "Index" column values?')
print(f'Train Index 0 exists: {0 in train["Index"].values}')
print(f'Train Index 279 exists: {279 in train["Index"].values}')
print(f'Train Index 1400 exists: {1400 in train["Index"].values}')
print()

# Quick test: TF-IDF on 1000 train reviews to see quality
print('=== QUICK ACCURACY ESTIMATE ===')
sample_test = test.head(3)
vec = TfidfVectorizer(ngram_range=(1,2), max_features=15000, stop_words='english', sublinear_tf=True)
vec.fit(train['Reviews'].tolist() + test['Reviews'].tolist())
train_mat = vec.transform(train['Reviews'].tolist())
test_mat  = vec.transform(sample_test['Reviews'].tolist())
sims = (test_mat @ train_mat.T).toarray()
for i in range(3):
    top10 = np.argsort(-sims[i])[:10]
    top10_train_idx = train['Index'].iloc[top10].tolist()
    top10_courses   = train['Course'].iloc[top10].tolist()
    current_recs = ast.literal_eval(final['Index_list'].iloc[i])
    print(f'Test {test["Index"].iloc[i]}:')
    print(f'  Test Review: {test["Reviews"].iloc[i][:120]}...')
    print(f'  NEW top-10 train indices: {top10_train_idx}')
    print(f'  NEW courses found: {list(set(top10_courses))}')
    print(f'  OLD submission:    {current_recs}')
    print(f'  OLD rec range: {min(current_recs)}-{max(current_recs)} (WRONG - should be in 0-109775)')
    print()
