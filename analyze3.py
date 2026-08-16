import pandas as pd
import ast, numpy as np

train = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\train.csv')
test = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\test.csv')
sample = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\sample_submission.csv')

# Key question: Is the task finding similar REVIEWS or recommending COURSES?
# The sample submission recommends reviews from totally different courses
# This suggests it could be: 
# 1. Find train reviews most similar to the given test review (review-level similarity)
# 2. Or recommend courses based on patterns

# Let's look at what INDEX values are in the train index_list from sample
# Are they randomly chosen or does the test review TEXT have connection to those train reviews?

# Let's compare test[0] with the recommended train reviews
test0_review = test[test['Index'] == 109776]['Reviews'].values[0]
print('TEST REVIEW 109776:')
print(test0_review)
print()
print('='*60)
print()

# Look at the recommended train reviews
recs = ast.literal_eval(sample[sample['Index'] == 109776]['Index_list'].values[0])
for ri in recs:
    train_row = train[train['Index'] == ri]
    print(f'TRAIN INDEX {ri}:')
    print(f'  Course: {train_row["Course"].values[0]}')
    print(f'  Review: {train_row["Reviews"].values[0]}')
    print()

# Now compute actual cosine similarity to see if there's a pattern
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

all_texts = [test0_review] + train['Reviews'].tolist()
vec = TfidfVectorizer(ngram_range=(1,2), max_features=10000, stop_words='english')
mat = vec.fit_transform(all_texts)
sims = cosine_similarity(mat[0:1], mat[1:]).flatten()
top10_indices = np.argsort(-sims)[:20]
print('='*60)
print('ACTUAL TOP-20 TF-IDF SIMILAR TRAIN REVIEWS for test 109776:')
for pos in top10_indices[:20]:
    print(f'  Train Index {pos}: sim={sims[pos]:.4f} | Course: {train["Course"].iloc[pos]}')
print()
print('Sample submission recommended indices:', recs)
print('Are sample recs among actual top similar?', [r for r in recs if r in top10_indices.tolist()])
