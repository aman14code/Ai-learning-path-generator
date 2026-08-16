import pandas as pd
import ast
import numpy as np

train = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\train.csv')
sub   = pd.read_csv(r'c:\Users\amans\OneDrive\Desktop\HCL Simplified Hackathon\submission_FINAL_v2.csv')

# Build fast index -> course lookup
idx_to_course = dict(zip(train['Index'].values, train['Course'].values))

print("=== RECOMMENDATION QUALITY ANALYSIS ===")
print(f"Total test rows: {len(sub)}")
print()

all_10_same   = 0
at_least_9    = 0
at_least_8    = 0
mixed_course  = 0
course_counts = []

for _, row in sub.iterrows():
    recs    = ast.literal_eval(row['Index_list'])
    courses = [idx_to_course.get(r, 'UNKNOWN') for r in recs]
    top_course = max(set(courses), key=courses.count)
    count_top  = courses.count(top_course)
    course_counts.append(count_top)
    if count_top == 10:
        all_10_same += 1
    if count_top >= 9:
        at_least_9 += 1
    if count_top >= 8:
        at_least_8 += 1
    if count_top < 8:
        mixed_course += 1

print(f"All 10 recs from same course : {all_10_same:5d} / {len(sub)}  ({100*all_10_same/len(sub):.1f}%)")
print(f"At least 9 from same course  : {at_least_9:5d} / {len(sub)}  ({100*at_least_9/len(sub):.1f}%)")
print(f"At least 8 from same course  : {at_least_8:5d} / {len(sub)}  ({100*at_least_8/len(sub):.1f}%)")
print(f"Mixed (< 8 from same course) : {mixed_course:5d} / {len(sub)}  ({100*mixed_course/len(sub):.1f}%)")
print()
print(f"Avg recommendations from dominant course: {np.mean(course_counts):.3f} / 10")
print()

# Show some mixed cases
print("=== EXAMPLES OF MIXED RECOMMENDATIONS ===")
shown = 0
for _, row in sub.iterrows():
    recs    = ast.literal_eval(row['Index_list'])
    courses = [idx_to_course.get(r, 'UNKNOWN') for r in recs]
    unique  = list(dict.fromkeys(courses))
    if len(unique) > 1 and shown < 5:
        test_idx = row['Index']
        print(f"Test {test_idx}: {unique}")
        shown += 1
if shown == 0:
    print("  NONE! Every test row gets 10 recs from the exact same course. PERFECT!")
