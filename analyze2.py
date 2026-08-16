import pandas as pd
import ast, numpy as np

train = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\train.csv')
test = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\test.csv')
sample = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\sample_submission.csv')

# KEY INSIGHT: Sample submission doesn't seem to be doing direct text similarity
# Let's check if test reviews mention course names directly
print('=== CHECKING IF TEST REVIEWS MENTION COURSE NAMES ===')
courses = train['Course'].unique().tolist()
print('Total courses:', len(courses))
print()

# Check the first test review
test_review_0 = test['Reviews'].iloc[0].lower()
print('Test review 0 (lowercased):')
print(test_review_0[:300])
print()
print('Course keywords found in test review 0:')
for c in courses:
    # Check keywords
    keywords = c.lower().split()
    if any(kw in test_review_0 for kw in keywords if len(kw) > 4):
        print(f'  MATCH: {c}')

print()
test_review_1 = test['Reviews'].iloc[1].lower()
print('Test review 1 (lowercased):')
print(test_review_1[:300])
print()
print('Course keywords found in test review 1:')
for c in courses:
    keywords = c.lower().split()
    if any(kw in test_review_1 for kw in keywords if len(kw) > 4):
        print(f'  MATCH: {c}')

# Now look at sample submission vs. course matching
print()
print('=== SAMPLE SUBMISSION ANALYSIS ===')
# For test[0], what course should it be? 
# "Attention mechanisms, residual connections, batch normalization, dropout" -> Advanced Neural Networks / Deep Learning
test0 = test[test['Index'] == 109776]['Reviews'].values[0]
print(f'Test 109776 review keywords: attention mechanisms, residual connections, batch normalization, dropout')
print('Sample recommends these courses:')
recs = ast.literal_eval(sample[sample['Index'] == 109776]['Index_list'].values[0])
for ri in recs:
    course = train[train['Index'] == ri]['Course'].values[0]
    rev = train[train['Index'] == ri]['Reviews'].values[0][:100]
    print(f'  [{ri}] Course: {course}')
    print(f'        Review: {rev}...')
    print()
