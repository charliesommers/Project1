"""
Vegas MLB Odds Parser
Parses historical closing lines from Vegas odds spreadsheet.
"""
import pandas as pd
import requests
from datetime import datetime
from typing import Dict, List, Optional


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
                # Add headers to avoid 406 errors
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                response = requests.get(self.file_path, headers=headers, timeout=30)
                response.raise_for_status()

                # Save locally
                local_path = 'data/vegas_odds.xlsx'
                import os
                os.makedirs('data', exist_ok=True)

                with open(local_path, 'wb') as f:
                    f.write(response.content)

                self.excel_file = pd.ExcelFile(local_path)
            else:
                self.excel_file = pd.ExcelFile(self.file_path)

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
            self.load_file()

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
    # Test parsing
    url = "https://shanemcd.org/wp-content/uploads/2025/07/mlb-odds.xlsx"
    parser = VegasOddsParser(url)
    parser.parse_all_sheets()
