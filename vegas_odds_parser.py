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
        Parse a single sheet containing Vegas closing lines.

        Expected columns:
        - Date: Game date (YYYY-MM-DD)
        - Start Time (EDT): Game start time
        - Away: Away team name
        - Home: Home team name
        - Away Score: Final away score
        - Home Score: Final home score
        - Status: Game status (Final, etc.)
        - Away Starter: Away pitcher
        - Home Starter: Home pitcher
        - O/U: Total (over/under line)
        - Over: Odds for over
        - Under: Odds for under
        - Away ML: Away moneyline odds
        - Home ML: Home moneyline odds

        Args:
            sheet_name: Sheet name to parse

        Returns:
            List of games with Vegas closing lines
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

            # Parse each row as a game
            for idx, row in df.iterrows():
                try:
                    # Skip rows without valid data
                    if pd.isna(row.get('Date')) or pd.isna(row.get('Away')) or pd.isna(row.get('Home')):
                        continue

                    # Extract game info
                    game_date_str = str(row.get('Date', '')).strip()

                    # Parse date
                    if game_date_str:
                        try:
                            game_date = pd.to_datetime(game_date_str).date()
                        except:
                            continue
                    else:
                        continue

                    away_team = str(row.get('Away', '')).strip()
                    home_team = str(row.get('Home', '')).strip()

                    if not away_team or not home_team:
                        continue

                    # Extract odds
                    away_ml = row.get('Away ML')
                    home_ml = row.get('Home ML')
                    total = row.get('O/U')
                    over_odds = row.get('Over')
                    under_odds = row.get('Under')
                    rl_away = row.get('RL Away')
                    rl_home = row.get('RL Home')

                    # Parse integers for odds (may have +/- signs)
                    def parse_odds(val):
                        if pd.isna(val):
                            return None
                        try:
                            return int(str(val).replace('+', '').strip())
                        except:
                            return None

                    away_ml = parse_odds(away_ml)
                    home_ml = parse_odds(home_ml)
                    over_odds = parse_odds(over_odds)
                    under_odds = parse_odds(under_odds)
                    rl_away = parse_odds(rl_away)
                    rl_home = parse_odds(rl_home)

                    # Parse total (float)
                    try:
                        total = float(total) if not pd.isna(total) else None
                    except:
                        total = None

                    # Extract scores and status
                    away_score = row.get('Away Score')
                    home_score = row.get('Home Score')
                    status = str(row.get('Status', '')).strip()

                    # Parse scores
                    try:
                        away_score = int(away_score) if not pd.isna(away_score) else None
                        home_score = int(home_score) if not pd.isna(home_score) else None
                    except:
                        away_score = None
                        home_score = None

                    game = {
                        'date': game_date,
                        'away_team': away_team,
                        'home_team': home_team,
                        'away_moneyline': away_ml,
                        'home_moneyline': home_ml,
                        'total': total,
                        'over_odds': over_odds,
                        'under_odds': under_odds,
                        'away_runline_odds': rl_away,
                        'home_runline_odds': rl_home,
                        'away_score': away_score,
                        'home_score': home_score,
                        'status': status,
                        'away_starter': str(row.get('Away Starter', '')).strip(),
                        'home_starter': str(row.get('Home Starter', '')).strip(),
                    }

                    games.append(game)

                except Exception as e:
                    # Skip problematic rows
                    continue

            print(f"\nParsed {len(games)} games from sheet {sheet_name}")

            # Show sample parsed games
            if games:
                print("\nSample parsed games:")
                for i, game in enumerate(games[:3]):
                    print(f"\nGame {i+1}:")
                    print(f"  Date: {game['date']}")
                    print(f"  Matchup: {game['away_team']} @ {game['home_team']}")
                    print(f"  Moneylines: {game['away_moneyline']} / {game['home_moneyline']}")
                    print(f"  Total: {game['total']} (Over: {game['over_odds']}, Under: {game['under_odds']})")
                    if game['status'] == 'Final':
                        print(f"  Final: {game['away_score']}-{game['home_score']}")

            return games

        except Exception as e:
            print(f"Error parsing sheet {sheet_name}: {e}")
            import traceback
            traceback.print_exc()
            return []

    def parse_all_sheets(self, max_sheets: int = None, sheet_filter: str = None) -> List[Dict]:
        """
        Parse all sheets or up to max_sheets.

        Args:
            max_sheets: Optional limit on number of sheets to parse (for testing)
            sheet_filter: Optional sheet name to parse (e.g., "Betting Odds")

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
        print(f"Sheet names: {', '.join(sheet_names)}")

        # Filter to specific sheet if specified
        if sheet_filter:
            if sheet_filter in sheet_names:
                sheets_to_parse = [sheet_filter]
                print(f"\nParsing sheet: {sheet_filter}")
            else:
                print(f"\nWarning: Sheet '{sheet_filter}' not found. Available sheets: {', '.join(sheet_names)}")
                return []
        else:
            # Limit sheets if specified (for initial inspection)
            sheets_to_parse = sheet_names[:max_sheets] if max_sheets else sheet_names
            print(f"\nParsing {len(sheets_to_parse)} sheet(s)...")

        for i, sheet_name in enumerate(sheets_to_parse, 1):
            print(f"\n{'='*80}")
            print(f"Sheet {i}/{len(sheets_to_parse)}: {sheet_name}")
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
    sheet_filter = "Betting Odds"  # Default: parse the main betting odds sheet
    max_sheets = None

    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        print(f"Using local file: {file_path}")

        # Optional: parse all sheets if --all flag is provided
        if '--all' in sys.argv:
            sheet_filter = None
            max_sheets = None
            print("Parsing all sheets")
        elif '--inspect' in sys.argv:
            # Just inspect first sheet
            sheet_filter = None
            max_sheets = 1
            print("Inspecting first sheet only")
    else:
        print(f"Attempting to download from: {file_path}")

    parser = VegasOddsParser(file_path)

    if parser.load_file():
        print("✓ File loaded successfully\n")
        parser.parse_all_sheets(max_sheets=max_sheets, sheet_filter=sheet_filter)
    else:
        print("\n❌ Failed to load file")
        print("\nNote: If download fails due to network restrictions, you can:")
        print("1. Download the file manually from:")
        print(f"   https://docs.google.com/spreadsheets/d/{VEGAS_ODDS_GSHEET_ID}/edit")
        print("   (File -> Download -> Microsoft Excel)")
        print("2. Save it as: data/vegas_odds.xlsx")
        print("3. Run: python vegas_odds_parser.py data/vegas_odds.xlsx")
        print("\nOr run this via GitHub Actions workflow which doesn't have network restrictions.")
