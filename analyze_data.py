#!/usr/bin/env python3
import sys
sys.path.insert(0, r'c:\Users\mpantin\Desktop\Siagro+')

from utils_siagro import cepal_data
import pandas as pd

# Fetch data
df = cepal_data([4470], lang='en')

# Filter
if 'dim_85162' in df.columns:
    df_filtered = df[df['dim_85162'] == 85163].copy()
else:
    df_filtered = df.copy()

print("=" * 80)
print("COLUMN ANALYSIS")
print("=" * 80)
print(f"Total columns: {len(df_filtered.columns)}")
print(f"All columns: {df_filtered.columns.tolist()}")

print("\n" + "=" * 80)
print("FINDING MONTH/REGION COLUMNS")
print("=" * 80)

region_col = None
month_col = None

for col in df_filtered.columns:
    col_lower = col.lower()
    print(f"\n{col}:")
    print(f"  Dtype: {df_filtered[col].dtype}")
    print(f"  Unique count: {df_filtered[col].nunique()}")
    if df_filtered[col].nunique() <= 20:
        print(f"  Unique values: {df_filtered[col].unique()[:10]}")
    
    if 'division' in col_lower or 'country' in col_lower or 'area' in col_lower:
        if region_col is None:
            region_col = col
            print(f"  ^^^ IDENTIFIED AS REGION COLUMN")
    if 'month' in col_lower:
        month_col = col
        print(f"  ^^^ IDENTIFIED AS MONTH COLUMN")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Region column: {region_col}")
print(f"Month column: {month_col}")

if region_col and month_col:
    print("\nSample data for Belize:")
    belize = df_filtered[df_filtered[region_col] == 'Belize']
    print(f"Belize rows: {len(belize)}")
    print(belize[[region_col, month_col, 'value']].head(15).to_string())
