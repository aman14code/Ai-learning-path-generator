import pandas as pd
import ast, numpy as np

train = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\train.csv')
test = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\test.csv')
sample = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\sample_submission.csv')

print('=== FULL UNDERSTANDING ===')
print('Train:', train.shape, '| Cols:', train.columns.tolist())
print('Test:', test.shape, '| Cols:', test.columns.tolist())
print()
print('Train Index range:', train['Index'].min(), '-', train['Index'].max())
print('Test Index range:', test['Index'].min(), '-', test['Index'].max())
print()
print('Unique Courses:', train['Course'].nunique())
print('Course distribution:')
print(train['Course'].value_counts().to_string())
print()

print('TASK: For each test review, find 10 most similar train reviews')
print('Output: 10 train Index values (sorted by relevance)')
print()
print('Test review[0]:')
print(test['Reviews'].iloc[0])
print()
print('Test review[1]:')
print(test['Reviews'].iloc[1])
print()

# Understand what courses in sample look like
print('Sample submission pairs:')
for i in range(5):
    test_idx = sample['Index'].iloc[i]
    test_review = test[test['Index'] == test_idx]['Reviews'].values[0][:100]
    rec_indices = ast.literal_eval(sample['Index_list'].iloc[i])
    courses = [train[train['Index'] == ri]['Course'].values[0] for ri in rec_indices[:5]]
    print(f'  Test {test_idx}: "{test_review[:80]}..."')
    print(f'   -> Courses: {courses}')
    print()

# Check if test reviews have course-specific keywords
print('=== COURSE KEYWORD ANALYSIS ===')
print('Each test review mentions specific topics - need to match to correct course')
print()
# Check how many unique courses are recommended per test row in sample
course_counts = []
for i in range(len(sample)):
    recs = ast.literal_eval(sample['Index_list'].iloc[i])
    courses = set([train[train['Index'] == ri]['Course'].values[0] for ri in recs])
    course_counts.append(len(courses))
print(f'Average unique courses per recommendation: {np.mean(course_counts):.2f}')
print(f'Min: {min(course_counts)}, Max: {max(course_counts)}')
