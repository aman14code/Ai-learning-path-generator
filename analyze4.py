import pandas as pd
import ast, numpy as np

train = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\train.csv')
test = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\test.csv')
sample = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\sample_submission.csv')

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ---------------------------------------------------------------
# Step 1: Check what structure the train reviews have
# Are reviews templated? Do they share many common sentences?
# ---------------------------------------------------------------
print('=== REVIEW STRUCTURE ANALYSIS ===')
# Sample 5 reviews from same course
course_sample = train[train['Course'] == 'Advanced Neural Networks'].head(5)
for i, row in course_sample.iterrows():
    print(f'Train Index {row["Index"]}: {row["Reviews"][:200]}')
    print()

# Check sentence structure similarity across courses
from sklearn.metrics.pairwise import cosine_similarity
print()
print('=== CROSS-COURSE REVIEW SIMILARITY ===')
texts_nn = train[train['Course'] == 'Advanced Neural Networks']['Reviews'].head(10).tolist()
texts_sql = train[train['Course'] == 'SQL for Beginners']['Reviews'].head(10).tolist()
vec = TfidfVectorizer(ngram_range=(1,2), max_features=5000, stop_words='english')
all_t = texts_nn + texts_sql
mat = vec.fit_transform(all_t)
sim_nn_nn = cosine_similarity(mat[:10], mat[:10])
sim_nn_sql = cosine_similarity(mat[:10], mat[10:])
print(f'Average intra-course (NN-NN) similarity: {sim_nn_nn.mean():.4f}')
print(f'Average cross-course (NN-SQL) similarity: {sim_nn_sql.mean():.4f}')
print()

# Check if there are common template sentences
import re
# Extract first sentence from each review
def first_sent(text):
    sents = re.split(r'[.!?]', str(text))
    return sents[0].strip()

print('First sentences of first 5 Advanced Neural Networks reviews:')
for r in train[train['Course'] == 'Advanced Neural Networks']['Reviews'].head(5):
    print(f'  {first_sent(r)}')

print()
print('First sentences of first 5 SQL for Beginners reviews:')
for r in train[train['Course'] == 'SQL for Beginners']['Reviews'].head(5):
    print(f'  {first_sent(r)}')

# Are there course-specific technical keywords we can extract?
print()
print('=== TECHNICAL KEYWORD FREQUENCY ===')
# What words are most distinctive for Advanced Neural Networks?
vec_full = TfidfVectorizer(ngram_range=(1,1), max_features=20000, stop_words='english')
all_texts = train['Reviews'].tolist()
mat_full = vec_full.fit_transform(all_texts)
nn_idx = train[train['Course'] == 'Advanced Neural Networks'].index
sql_idx = train[train['Course'] == 'SQL for Beginners'].index
nn_mean = mat_full[nn_idx].mean(axis=0).A1
sql_mean = mat_full[sql_idx].mean(axis=0).A1
feat_names = vec_full.get_feature_names_out()
nn_top = feat_names[np.argsort(-nn_mean)[:20]]
sql_top = feat_names[np.argsort(-sql_mean)[:20]]
print(f'Top words for Advanced Neural Networks: {nn_top}')
print(f'Top words for SQL for Beginners: {sql_top}')
