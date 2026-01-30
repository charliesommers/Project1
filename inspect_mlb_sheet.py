#!/usr/bin/env python3
"""
Inspect Greg's MLB sheet structure to understand the format.
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

print(f"\nSheet names: {excel_file.sheet_names}")

# Look at first date sheet
if excel_file.sheet_names:
    first_sheet = excel_file.sheet_names[0]
    print(f"\nInspecting sheet: {first_sheet}")

    # Read raw data
    df = pd.read_excel(excel_file, sheet_name=first_sheet, header=None)

    print(f"\nSheet dimensions: {df.shape[0]} rows x {df.shape[1]} columns")

    print("\nFirst 10 rows, first 10 columns:")
    print(df.iloc[:10, :10].to_string())

    print("\n\nColumn B (index 1) and C (index 2) - first 15 rows:")
    for i in range(15):
        col_b = df.iloc[i, 1] if len(df.columns) > 1 else "N/A"
        col_c = df.iloc[i, 2] if len(df.columns) > 2 else "N/A"
        print(f"Row {i}: B='{col_b}' | C='{col_c}'")
