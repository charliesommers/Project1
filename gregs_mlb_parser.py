"""
Greg's MLB Handicapping Data Parser
Parses Greg Peterson's MLB totals Excel files
"""
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class GregsMLBParser:
    """Parser for Greg's MLB handicapping spreadsheets."""

    def __init__(self, file_path: str):
        """
        Initialize parser with Excel file path.

        Args:
            file_path: Path to Greg's MLB handicapping Excel file
        """
        self.file_path = file_path
        self.excel_file = None
        self.all_games = []

    def parse_sheet_date(self, sheet_name: str) -> Optional[datetime]:
        """
        Parse date from sheet name.

        Args:
            sheet_name: Sheet name (e.g., "7/28/25" or "72825")

        Returns:
            datetime object or None if invalid
        """
        try:
            sheet_name = str(sheet_name).strip()

            # Skip sheets that start with "Copy of"
            if sheet_name.startswith("Copy of"):
                return None

            # Try M/D/YY or MM/DD/YY format first (e.g., "7/28/25")
            if '/' in sheet_name:
                parts = sheet_name.split('/')
                if len(parts) == 3:
                    month = int(parts[0])
                    day = int(parts[1])
                    year_str = parts[2]
                    # Handle 2-digit or 4-digit year
                    year = int(year_str) if len(year_str) == 4 else 2000 + int(year_str)
                    return datetime(year, month, day)

            # Fall back to MDDYY format without slashes
            # MDYY format (e.g., "4125" = 4/1/25)
            if len(sheet_name) == 4:
                month = int(sheet_name[0])
                day = int(sheet_name[1])
                year = 2000 + int(sheet_name[2:4])
            # MDDYY format (e.g., "42425" = 4/24/25)
            elif len(sheet_name) == 5:
                month = int(sheet_name[0])
                day = int(sheet_name[1:3])
                year = 2000 + int(sheet_name[3:5])
            # MMDDYY format (e.g., "102425" = 10/24/25)
            elif len(sheet_name) == 6:
                month = int(sheet_name[0:2])
                day = int(sheet_name[2:4])
                year = 2000 + int(sheet_name[4:6])
            else:
                return None

            return datetime(year, month, day)

        except (ValueError, IndexError):
            return None

    def load_file(self):
        """Load the Excel file."""
        try:
            self.excel_file = pd.ExcelFile(self.file_path)
            return True
        except Exception as e:
            print(f"Error loading Excel file: {e}")
            return False

    def parse_game_pair(self, row1: pd.Series, row2: pd.Series, game_date: datetime) -> Optional[Dict]:
        """
        Parse a pair of rows representing one game.
        MLB format: Row 1 = Away team, Row 2 = Home team

        Args:
            row1: First row (away team)
            row2: Second row (home team)
            game_date: Date of the game

        Returns:
            Dictionary with game data or None if invalid
        """
        team1 = row1.get('Team', '')
        team2 = row2.get('Team', '')
        line1 = row1.get("Greg's Line")
        line2 = row2.get("Greg's Line")

        # Skip if no data
        if not team1 or not team2 or pd.isna(line1) or pd.isna(line2):
            return None

        # Convert lines to floats
        try:
            line1 = float(line1)
            line2 = float(line2)
        except (ValueError, TypeError):
            return None

        # MLB format: line1 is run line, line2 is total
        # Run line is typically -1.5/+1.5
        # Total is typically 7-12 range
        if abs(line1) < 5 and line2 > 5:
            # Team 1 (away) has run line, Team 2 (home) has total
            away_team = team1
            home_team = team2
            run_line = line1
            total = line2
        elif abs(line2) < 5 and line1 > 5:
            # Team 2 (home) has run line, Team 1 (away) has total
            away_team = team2
            home_team = team1
            run_line = line2
            total = line1
        else:
            # Try to determine based on which is negative (favorite)
            if line1 < 0:
                away_team = team1
                home_team = team2
                run_line = line1
                total = line2
            else:
                away_team = team2
                home_team = team1
                run_line = line2
                total = line1

        # Determine favorite/underdog based on run line
        if run_line < 0:
            favorite = away_team
            underdog = home_team
        else:
            favorite = home_team
            underdog = away_team

        return {
            'date': game_date,
            'away_team': away_team,
            'home_team': home_team,
            'favorite': favorite,
            'underdog': underdog,
            'run_line': run_line,
            'total': total,
            'matchup': f"{away_team} @ {home_team}",
            'run_line_display': f"{favorite} {run_line:+.1f}",
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
        game_date = self.parse_sheet_date(sheet_name)
        if not game_date:
            print(f"Warning: Could not parse date from sheet name: {sheet_name}")
            return []

        try:
            df_raw = pd.read_excel(self.excel_file, sheet_name=sheet_name, header=None)
        except Exception as e:
            print(f"Warning: Could not read sheet {sheet_name}: {e}")
            return []

        games = []

        # MLB typically has games in columns B/C
        # Try columns B(1), E(4), H(7), etc. similar to CBB
        team_columns = [1, 4, 7, 10, 13, 16, 19, 22, 25]

        for team_col in team_columns:
            line_col = team_col + 1

            if team_col >= len(df_raw.columns) or line_col >= len(df_raw.columns):
                continue

            # Process rows in pairs (skip header row 0)
            for i in range(1, len(df_raw) - 1, 2):
                team1 = df_raw.iloc[i, team_col]
                line1 = df_raw.iloc[i, line_col]
                team2 = df_raw.iloc[i + 1, team_col]
                line2 = df_raw.iloc[i + 1, line_col]

                if pd.isna(team1) or pd.isna(team2) or pd.isna(line1) or pd.isna(line2):
                    continue

                row1 = pd.Series({'Team': str(team1).strip(), "Greg's Line": line1})
                row2 = pd.Series({'Team': str(team2).strip(), "Greg's Line": line2})

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
            if specific_date in self.excel_file.sheet_names:
                games = self.parse_sheet(specific_date)
                all_games.extend(games)
            else:
                print(f"Error: Sheet '{specific_date}' not found")
                print(f"Available sheets: {', '.join(self.excel_file.sheet_names)}")
        else:
            for sheet_name in self.excel_file.sheet_names:
                games = self.parse_sheet(sheet_name)
                all_games.extend(games)

        self.all_games = all_games
        return all_games
