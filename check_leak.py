import pandas as pd
import os
import re

desk = r'c:\Users\amans\OneDrive\Desktop'
train = pd.read_csv(os.path.join(desk, 'train.csv'))

def clean(t):
    if pd.isna(t): return ""
    return re.sub(r'[^a-z0-9\s]', ' ', str(t).lower())

train['c'] = train['Reviews'].apply(clean)

match = 0
for i, r in train.iterrows():
    c_clean = clean(r['Course']).strip()
    if c_clean in r['c']:
        match += 1

print(f"Train exact course match: {match} / {len(train)}")
