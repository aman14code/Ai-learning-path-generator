import pandas as pd
import ast
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

train  = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\train.csv')
test   = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\test.csv')
sub_v2 = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\HCL Simplified Hackathon\submission_FINAL_v2.csv')

print("=== SCORE ANALYSIS: Why 65.72 and not higher? ===")
print()

idx_to_course = dict(zip(train['Index'].values, train['Course'].values))

# Check 1: How many unique courses per recommendation?
unique_per_row = []
for _, row in sub_v2.iterrows():
    recs = ast.literal_eval(row['Index_list'])
    courses = [idx_to_course.get(r,'?') for r in recs]
    unique_per_row.append(len(set(courses)))

print(f"Avg unique courses per recommendation: {np.mean(unique_per_row):.2f}")
print(f"All recommend exactly 1 unique course: {sum(1 for x in unique_per_row if x == 1)}/{len(sub_v2)}")
print()

# Check 2: How does our submission compare to sample submission diversity?
sample = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\sample_submission.csv')
sample_unique = []
for _, row in sample.iterrows():
    recs = ast.literal_eval(row['Index_list'])
    courses = [idx_to_course.get(r,'?') for r in recs]
    sample_unique.append(len(set(courses)))
print(f"Sample submission avg unique courses: {np.mean(sample_unique):.2f}")
print()

# Check 3: Maybe ground truth expects DIVERSE course recommendations
# Let's check: if we recommend 1 per course (10 different courses), what score would we expect?
print("=== KEY INSIGHT ===")
print("Our submission: 10 recs ALL from same course (e.g., Advanced Neural Networks)")
print("Sample baseline: 8-9 unique courses per recommendation")
print()
print("If ground truth expects DIVERSE recs from multiple courses,")
print("recommending all 10 from 1 course = only 1/10 courses covered = ~10% coverage")
print("This would severely limit our score!")
print()
print("Solution: Recommend top 10 DIFFERENT courses, 1 rep review each")
print()

# Let's verify: what does test review 109776 look like vs what we recommended
test0 = test[test['Index'] == 109776]['Reviews'].values[0]
print(f"Test 109776 review (first 200 chars): {test0[:200]}")
print()
recs_v2 = ast.literal_eval(sub_v2[sub_v2['Index'] == 109776]['Index_list'].values[0])
courses_v2 = [idx_to_course[r] for r in recs_v2]
print(f"Our recommendations courses: {list(set(courses_v2))}")
print(f"(All same course: {len(set(courses_v2))==1})")
