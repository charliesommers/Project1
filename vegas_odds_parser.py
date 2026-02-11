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

    def parse_sheet_date(self, sheet_name: str) -> Optional[datetime]:
        """
        Parse date from sheet name.

        Args:
            sheet_name: Sheet name (e.g., "7/28/25", "72825", or "2025-07-28")

        Returns:
            datetime object or None if invalid
        """
        try:
            sheet_name = str(sheet_name).strip()

            # Try M/D/YY or MM/DD/YY format first
            if '/' in sheet_name:
                parts = sheet_name.split('/')
                if len(parts) == 3:
                    month = int(parts[0])
                    day = int(parts[1])
                    year_str = parts[2]
                    year = int(year_str) if len(year_str) == 4 else 2000 + int(year_str)
                    return datetime(year, month, day)

            # Try ISO format (YYYY-MM-DD)
            if '-' in sheet_name:
                parts = sheet_name.split('-')
                if len(parts) == 3:
                    year = int(parts[0])
                    month = int(parts[1])
                    day = int(parts[2])
                    return datetime(year, month, day)

            # Try MDDYY or MMDDYY format
            if len(sheet_name) == 4:
                month = int(sheet_name[0])
                day = int(sheet_name[1])
                year = 2000 + int(sheet_name[2:4])
            elif len(sheet_name) == 5:
                month = int(sheet_name[0])
                day = int(sheet_name[1:3])
                year = 2000 + int(sheet_name[3:5])
            elif len(sheet_name) == 6:
                month = int(sheet_name[0:2])
                day = int(sheet_name[2:4])
                year = 2000 + int(sheet_name[4:6])
            else:
                return None

            return datetime(year, month, day)

        except (ValueError, IndexError):
            return None

    def parse_sheet(self, sheet_name: str) -> List[Dict]:
        """
        Parse a single sheet.

        Args:
            sheet_name: Sheet name to parse

        Returns:
            List of games with Vegas odds
        """
        try:
            game_date = self.parse_sheet_date(sheet_name)

            # Read with header row
            df = pd.read_excel(self.excel_file, sheet_name=sheet_name)

            print(f"\nParsing sheet: {sheet_name}")
            if game_date:
                print(f"Date: {game_date.strftime('%Y-%m-%d')}")
            print(f"Columns: {df.columns.tolist()}")
            print(f"Rows: {len(df)}")

            # Display first few rows to understand structure
            print("\nFirst 5 rows:")
            print(df.head().to_string())

            print("\nLast 2 rows:")
            print(df.tail(2).to_string())

            games = []

            # Parse based on actual structure
            # Common Vegas odds formats include:
            # - Date, Away Team, Home Team, Away ML, Home ML, Away RL, Home RL, Total, Over Price, Under Price
            # - Or team rows with rotation numbers

            # Will implement full parsing once we see the actual structure

            return games

        except Exception as e:
            print(f"Error parsing sheet {sheet_name}: {e}")
            import traceback
            traceback.print_exc()
            return []

    def parse_all_sheets(self, max_sheets: int = None) -> List[Dict]:
        """
        Parse all sheets or up to max_sheets.

        Args:
            max_sheets: Optional limit on number of sheets to parse (for testing)

        Returns:
            List of all games
        """
        if not self.excel_file:
            success = self.load_file()
            if not success or not self.excel_file:
                print("Failed to load Excel file")
                return []

        all_games = []
        sheet_names = self.excel_file.sheet_names

        print(f"\n{'='*80}")
        print(f"VEGAS ODDS FILE STRUCTURE")
        print(f"{'='*80}")
        print(f"\nTotal sheets: {len(sheet_names)}")
        print(f"Sheet names: {', '.join(sheet_names[:10])}")
        if len(sheet_names) > 10:
            print(f"... and {len(sheet_names) - 10} more")

        # Limit sheets if specified (for initial inspection)
        sheets_to_parse = sheet_names[:max_sheets] if max_sheets else sheet_names

        print(f"\nParsing {len(sheets_to_parse)} sheet(s)...")

        for i, sheet_name in enumerate(sheets_to_parse, 1):
            print(f"\n{'='*80}")
            print(f"Sheet {i}/{len(sheets_to_parse)}")
            print(f"{'='*80}")
            games = self.parse_sheet(sheet_name)
            all_games.extend(games)

        print(f"\n{'='*80}")
        print(f"Total games parsed: {len(all_games)}")
        print(f"{'='*80}")

        self.all_games = all_games
        return all_games


if __name__ == '__main__':
    import sys

    # Allow local file path as command line argument
    file_path = VEGAS_ODDS_URL
    max_sheets = 3  # Default: inspect first 3 sheets

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"Using local file: {file_path}")

        # Optional: parse all sheets if --all flag is provided
        if '--all' in sys.argv:
            max_sheets = None
            print("Parsing all sheets")
    else:
        print(f"Attempting to download from: {file_path}")

    parser = VegasOddsParser(file_path)

    if parser.load_file():
        print("✓ File loaded successfully\n")
        parser.parse_all_sheets(max_sheets=max_sheets)
    else:
        print("\n❌ Failed to load file")
        print("\nNote: If download fails due to network restrictions, you can:")
        print("1. Download the file manually from:")
        print(f"   https://docs.google.com/spreadsheets/d/{VEGAS_ODDS_GSHEET_ID}/edit")
        print("   (File -> Download -> Microsoft Excel)")
        print("2. Save it as: data/vegas_odds.xlsx")
        print("3. Run: python vegas_odds_parser.py data/vegas_odds.xlsx")
        print("\nOr run this via GitHub Actions workflow which doesn't have network restrictions.")
