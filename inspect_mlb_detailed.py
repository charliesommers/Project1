#!/usr/bin/env python3
"""
Enhanced MLB sheet inspector to find where team names are located.
"""
import requests
import pandas as pd
import os

GOOGLE_SHEETS_ID = "1QvkPvE8CtGabeYphECyMY2zYilPBkbOBeEL6mEwJTLs"
GOOGLE_SHEETS_URL = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEETS_ID}/export?format=xlsx"

def download_sheet():
    os.makedirs("data", exist_ok=True)
    response = requests.get(GOOGLE_SHEETS_URL, timeout=30)
    response.raise_for_status()

    path = "data/gregs_mlb_inspect.xlsx"
    with open(path, 'wb') as f:
        f.write(response.content)
    return path

print("Downloading Greg's MLB sheet...")
file_path = download_sheet()

print("\nInspecting sheet structure...")
excel_file = pd.ExcelFile(file_path)

print(f"\nFound {len(excel_file.sheet_names)} sheets")
print(f"First 10 sheet names: {excel_file.sheet_names[:10]}")

# Look at a few date sheets
date_sheets = [s for s in excel_file.sheet_names if '/' in s or (s.isdigit() and len(s) >= 4)][:3]

print(f"\nInspecting {len(date_sheets)} date sheets...")

for sheet_name in date_sheets:
    print(f"\n{'='*80}")
    print(f"SHEET: {sheet_name}")
    print('='*80)

    # Read raw data
    df = pd.read_excel(excel_file, sheet_name=sheet_name, header=None)

    print(f"Dimensions: {df.shape[0]} rows x {df.shape[1]} columns")

    # Check row 0 across columns (might have team names as headers)
    print("\nRow 0 across first 15 columns:")
    for i in range(min(15, len(df.columns))):
        val = df.iloc[0, i] if not pd.isna(df.iloc[0, i]) else ""
        if val:
            print(f"  Col {i}: '{val}'")

    # Look at column B/C (indices 1/2) which parser currently reads
    print("\nColumn B (1) and C (2) - first 12 rows:")
    for row in range(min(12, len(df))):
        col_b = df.iloc[row, 1] if len(df.columns) > 1 and not pd.isna(df.iloc[row, 1]) else "---"
        col_c = df.iloc[row, 2] if len(df.columns) > 2 and not pd.isna(df.iloc[row, 2]) else "---"
        print(f"  Row {row}: B='{col_b}' | C='{col_c}'")

    # Check if column A might have team names
    print("\nColumn A (0) - first 12 rows:")
    for row in range(min(12, len(df))):
        col_a = df.iloc[row, 0] if not pd.isna(df.iloc[row, 0]) else "---"
        if col_a != "---":
            print(f"  Row {row}: '{col_a}'")

    # Look at a second column section (E/F = indices 4/5)
    if len(df.columns) > 5:
        print("\nColumn E (4) and F (5) - first 8 rows:")
        for row in range(min(8, len(df))):
            col_e = df.iloc[row, 4] if not pd.isna(df.iloc[row, 4]) else "---"
            col_f = df.iloc[row, 5] if not pd.isna(df.iloc[row, 5]) else "---"
            if col_e != "---" or col_f != "---":
                print(f"  Row {row}: E='{col_e}' | F='{col_f}'")

print("\n" + "="*80)
print("ANALYSIS:")
print("="*80)
print("Looking for where TEAM NAMES are stored...")
print("Parser currently reads column B (index 1), but getting pitcher names.")
print("Need to find where actual team names (Dodgers, Blue Jays, etc.) are.")
