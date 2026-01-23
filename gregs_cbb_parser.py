"""
Greg's CBB Handicapping Data Parser
Parses Greg Peterson's college basketball handicapping Excel files
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sys


class GregsCBBParser:
    """Parser for Greg's CBB handicapping spreadsheets."""

    def __init__(self, file_path: str):
        """
        Initialize parser with Excel file path.

        Args:
            file_path: Path to Greg's CBB handicapping Excel file
        """
        self.file_path = file_path
        self.excel_file = None
        self.all_games = []

    def parse_sheet_date(self, sheet_name: str) -> Optional[datetime]:
        """
        Parse date from sheet name in MDDYY format.

        Args:
            sheet_name: Sheet name (e.g., "12226" for Jan 22, 2026)

        Returns:
            datetime object or None if invalid
        """
        try:
            # Handle various formats
            sheet_name = str(sheet_name).strip()

            # MDDYY format (e.g., "12226" = 1/22/26)
            if len(sheet_name) == 5:
                month = int(sheet_name[0])
                day = int(sheet_name[1:3])
                year = 2000 + int(sheet_name[3:5])
            # MMDDYY format (e.g., "012226" = 1/22/26)
            elif len(sheet_name) == 6:
                month = int(sheet_name[0:2])
                day = int(sheet_name[2:4])
                year = 2000 + int(sheet_name[4:6])
            else:
                return None

            return datetime(year, month, day)
        except (ValueError, IndexError):
            return None

    def load_file(self) -> pd.ExcelFile:
        """Load Excel file and return ExcelFile object."""
        try:
            self.excel_file = pd.ExcelFile(self.file_path, engine='openpyxl')
            return self.excel_file
        except FileNotFoundError:
            print(f"Error: File not found: {self.file_path}")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            sys.exit(1)

    def parse_game_pair(self, row1: pd.Series, row2: pd.Series, game_date: datetime) -> Dict:
        """
        Parse a pair of rows into a single game.

        Format:
        - 2 rows per game
        - Favorite has spread (negative number)
        - Underdog has total (3-digit number with decimal)
        - Home team on bottom unless marked with *

        Args:
            row1: First row
            row2: Second row
            game_date: Date of the game

        Returns:
            Dictionary with game information
        """
        team1 = str(row1.get('Team', '')).strip()
        team2 = str(row2.get('Team', '')).strip()
        line1 = row1.get("Greg's Line", None)
        line2 = row2.get("Greg's Line", None)

        # Skip if no data
        if not team1 or not team2 or pd.isna(line1) or pd.isna(line2):
            return None

        # Check for neutral court
        neutral_court = False
        if '*' in team1:
            team1 = team1.replace('*', '').strip()
            neutral_court = True
        if '*' in team2:
            team2 = team2.replace('*', '').strip()
            neutral_court = True

        # Convert lines to floats
        try:
            line1 = float(line1)
            line2 = float(line2)
        except (ValueError, TypeError):
            return None

        # Determine which is spread and which is total
        # Spread is negative, total is positive (usually 3 digits)
        if line1 < 0 and line2 > 100:
            # Team 1 is favorite with spread, Team 2 is underdog with total
            favorite = team1
            underdog = team2
            spread = line1
            total = line2
            home_team = team2 if not neutral_court else None
        elif line2 < 0 and line1 > 100:
            # Team 2 is favorite with spread, Team 1 is underdog with total
            favorite = team2
            underdog = team1
            spread = line2
            total = line1
            home_team = team1 if not neutral_court else None
        else:
            # Invalid format
            return None

        return {
            'date': game_date,
            'favorite': favorite,
            'underdog': underdog,
            'spread': spread,  # Negative number (favorite giving points)
            'total': total,
            'home_team': home_team,
            'neutral_court': neutral_court,
            'matchup': f"{favorite} vs {underdog}",
            # For display purposes
            'spread_line': f"{favorite} {spread}",
            'total_line': f"O/U {total}"
        }

    def parse_sheet(self, sheet_name: str) -> List[Dict]:
        """
        Parse a single sheet (one day's games).

        Args:
            sheet_name: Name of the sheet to parse

        Returns:
            List of game dictionaries
        """
        # Parse date from sheet name
        game_date = self.parse_sheet_date(sheet_name)
        if not game_date:
            print(f"Warning: Could not parse date from sheet name: {sheet_name}")
            return []

        # Read sheet
        try:
            df = pd.read_excel(self.excel_file, sheet_name=sheet_name)
        except Exception as e:
            print(f"Warning: Could not read sheet {sheet_name}: {e}")
            return []

        # Check for required columns
        if 'Team' not in df.columns or "Greg's Line" not in df.columns:
            print(f"Warning: Sheet {sheet_name} missing required columns")
            return []

        games = []

        # Process rows in pairs
        for i in range(0, len(df) - 1, 2):
            row1 = df.iloc[i]
            row2 = df.iloc[i + 1]

            game = self.parse_game_pair(row1, row2, game_date)
            if game:
                games.append(game)

        return games

    def parse_all_sheets(self, specific_date: Optional[str] = None) -> List[Dict]:
        """
        Parse all sheets in the Excel file.

        Args:
            specific_date: Optional sheet name to parse only one date

        Returns:
            List of all games from all sheets
        """
        if not self.excel_file:
            self.load_file()

        all_games = []

        if specific_date:
            # Parse only specific sheet
            if specific_date in self.excel_file.sheet_names:
                games = self.parse_sheet(specific_date)
                all_games.extend(games)
            else:
                print(f"Error: Sheet '{specific_date}' not found")
                print(f"Available sheets: {', '.join(self.excel_file.sheet_names)}")
        else:
            # Parse all sheets
            for sheet_name in self.excel_file.sheet_names:
                games = self.parse_sheet(sheet_name)
                all_games.extend(games)

        self.all_games = all_games
        return all_games

    def get_games_dataframe(self) -> pd.DataFrame:
        """
        Convert parsed games to DataFrame.

        Returns:
            DataFrame with all games
        """
        if not self.all_games:
            return pd.DataFrame()

        return pd.DataFrame(self.all_games)

    def get_dates(self) -> List[str]:
        """Get list of all date sheets in the file."""
        if not self.excel_file:
            self.load_file()
        return self.excel_file.sheet_names

    def get_summary(self) -> Dict:
        """Get summary statistics."""
        if not self.all_games:
            return {}

        df = self.get_games_dataframe()

        return {
            'total_games': len(df),
            'dates': df['date'].nunique(),
            'date_range': f"{df['date'].min().strftime('%m/%d/%Y')} to {df['date'].max().strftime('%m/%d/%Y')}",
            'avg_total': df['total'].mean(),
            'avg_spread': df['spread'].mean(),
            'neutral_court_games': df['neutral_court'].sum(),
        }
