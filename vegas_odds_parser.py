"""
Vegas MLB Odds Parser
Parses historical closing lines from Vegas odds spreadsheet.
"""
import pandas as pd
import requests
from datetime import datetime
from typing import Dict, List, Optional

# Google Sheets ID for Vegas closing lines
VEGAS_ODDS_GSHEET_ID = "1E7TIssWO964m7V-JPABPbrAGgOw8cHkQ"
VEGAS_ODDS_URL = f"https://docs.google.com/spreadsheets/d/{VEGAS_ODDS_GSHEET_ID}/export?format=xlsx"


class VegasOddsParser:
    """Parser for Vegas MLB closing lines spreadsheet."""

    def __init__(self, file_path: str):
        """
        Initialize parser.

        Args:
            file_path: Path to Excel file or URL
        """
        self.file_path = file_path
        self.excel_file = None
        self.all_games = []

    def load_file(self):
        """Load the Excel file from URL or path."""
        try:
            if self.file_path.startswith('http'):
                import os
                os.makedirs('data', exist_ok=True)
                local_path = 'data/vegas_odds.xlsx'

                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }

                # For Google Sheets export, direct download should work
                response = requests.get(self.file_path, headers=headers, timeout=30)
                response.raise_for_status()

                # Save locally
                with open(local_path, 'wb') as f:
                    f.write(response.content)

                # Specify engine explicitly for Excel files
                self.excel_file = pd.ExcelFile(local_path, engine='openpyxl')
            else:
                self.excel_file = pd.ExcelFile(self.file_path, engine='openpyxl')

            return True
        except Exception as e:
            print(f"Error loading Excel file: {e}")
            return False

    def parse_sheet(self, sheet_name: str) -> List[Dict]:
        """
        Parse a single sheet.

        Args:
            sheet_name: Sheet name to parse

        Returns:
            List of games with Vegas odds
        """
        try:
            # Read with header row
            df = pd.read_excel(self.excel_file, sheet_name=sheet_name)

            print(f"\nParsing sheet: {sheet_name}")
            print(f"Columns: {df.columns.tolist()}")
            print(f"Rows: {len(df)}")

            # Display first few rows to understand structure
            print("\nFirst 5 rows:")
            print(df.head().to_string())

            games = []

            # Parse based on actual structure
            # (Will need to adjust once we see the data)

            return games

        except Exception as e:
            print(f"Error parsing sheet {sheet_name}: {e}")
            return []

    def parse_all_sheets(self) -> List[Dict]:
        """Parse all sheets."""
        if not self.excel_file:
            success = self.load_file()
            if not success or not self.excel_file:
                print("Failed to load Excel file")
                return []

        all_games = []

        print(f"\nSheet names: {self.excel_file.sheet_names}")

        # Parse first sheet to understand structure
        if self.excel_file.sheet_names:
            first_sheet = self.excel_file.sheet_names[0]
            games = self.parse_sheet(first_sheet)
            all_games.extend(games)

        self.all_games = all_games
        return all_games


if __name__ == '__main__':
    import sys

    # Allow local file path as command line argument
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"Using local file: {file_path}")
    else:
        file_path = VEGAS_ODDS_URL
        print(f"Attempting to download from: {file_path}")

    parser = VegasOddsParser(file_path)

    if parser.load_file():
        print("✓ File loaded successfully")
        parser.parse_all_sheets()
    else:
        print("\n❌ Failed to load file")
        print("\nNote: If download fails due to network restrictions, you can:")
        print("1. Download the file manually from:")
        print(f"   https://docs.google.com/spreadsheets/d/{VEGAS_ODDS_GSHEET_ID}/edit")
        print("   (File -> Download -> Microsoft Excel)")
        print("2. Save it as: data/vegas_odds.xlsx")
        print("3. Run: python vegas_odds_parser.py data/vegas_odds.xlsx")
        print("\nOr run this via GitHub Actions workflow which doesn't have network restrictions.")
