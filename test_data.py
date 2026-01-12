#!/usr/bin/env python3
import sys
sys.path.insert(0, 'c:\\Users\\mpantin\\Desktop\\Siagro+')

from utils_siagro import cepal_data

# Fetch the climate change temperature data
df = cepal_data([4470], lang='en')

print("="*80)
print("DATAFRAME INFO")
print("="*80)
print(f"\nShape: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")

print("\n" + "="*80)
print("FIRST 20 ROWS")
print("="*80)
print(df.head(20).to_string())

print("\n" + "="*80)
print("COLUMN DETAILS")
print("="*80)
for col in df.columns:
    print(f"\n{col}:")
    print(f"  Dtype: {df[col].dtype}")
    print(f"  Unique values: {df[col].nunique()}")
    if df[col].nunique() <= 20:
        print(f"  Values: {df[col].unique()}")

print("\n" + "="*80)
print("CHECKING FOR KEY COLUMNS")
print("="*80)
print(f"'Months' in columns: {'Months' in df.columns}")
print(f"'Subnational administrative division' in columns: {'Subnational administrative division' in df.columns}")
print(f"'value' in columns: {'value' in df.columns}")

if 'Months' in df.columns:
    print(f"\nUnique Months: {df['Months'].unique()}")
    
if 'Subnational administrative division' in df.columns:
    print(f"\nUnique regions (first 20): {df['Subnational administrative division'].unique()[:20]}")
