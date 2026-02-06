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
        MLB format: Row 1 (B2) = Away team, Row 2 (B3) = Home team
        Example: B2="Reds", B3="Mets" -> "Reds @ Mets"

        Args:
            row1: First row (away team)
            row2: Second row (home team)
            game_date: Date of the game

        Returns:
            Dictionary with game data or None if invalid
        """
        away_team = row1.get('Team', '')  # B2 = away
        home_team = row2.get('Team', '')  # B3 = home
        away_run_line = row1.get("Greg's Line")
        home_run_line = row2.get("Greg's Line")
        total = row1.get('Total')  # Shared total from column F
        away_moneyline = row1.get('Moneyline')  # Greg's moneyline for away
        home_moneyline = row2.get('Moneyline')  # Greg's moneyline for home

        # Skip if no data
        if not home_team or not away_team or pd.isna(away_run_line) or pd.isna(home_run_line) or pd.isna(total):
            return None

        # Convert to floats
        try:
            away_run_line = float(away_run_line)
            home_run_line = float(home_run_line)
            total = float(total)
        except (ValueError, TypeError):
            return None

        # Determine favorite/underdog based on run lines
        # One team will have negative run line (favorite), other positive (underdog)
        if away_run_line < 0:
            favorite = away_team
            underdog = home_team
            run_line = abs(away_run_line)
        elif home_run_line < 0:
            favorite = home_team
            underdog = away_team
            run_line = abs(home_run_line)
        else:
            # Can't determine favorite, skip
            return None

        return {
            'date': game_date,
            'away_team': away_team,
            'home_team': home_team,
            'favorite': favorite,
            'underdog': underdog,
            'run_line': run_line,  # Already stored as positive
            'total': total,
            'away_moneyline': away_moneyline,  # Greg's moneyline for away team
            'home_moneyline': home_moneyline,  # Greg's moneyline for home team
            'matchup': f"{away_team} @ {home_team}",
            'run_line_display': f"{favorite} {-run_line:+.1f}",
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

        # MLB format (per sheet header):
        # Column A (0): Rotation #
        # Column B (1): Team name
        # Column C (2): Starting Pitcher
        # Column D (3): Moneyline Price
        # Column E (4): Run Line Price (e.g., "-1.5 +112")
        # Column F (5): Total Runs (shared between both teams)
        # Column G (6): Team Runs
        # Pattern repeats every 7 columns
        team_columns = [1, 8, 15, 22, 29]  # Columns B, I, P, W, ...

        for team_col in team_columns:
            moneyline_col = team_col + 2  # Column D (moneyline price)
            line_col = team_col + 3  # Column E (run line price)
            total_col = team_col + 4  # Column F (total)

            if team_col >= len(df_raw.columns) or total_col >= len(df_raw.columns):
                continue

            # Process rows in pairs based on shared totals (skip header row 0)
            for i in range(1, len(df_raw) - 1, 2):
                team1 = df_raw.iloc[i, team_col]
                moneyline1 = df_raw.iloc[i, moneyline_col]
                line1 = df_raw.iloc[i, line_col]
                total1 = df_raw.iloc[i, total_col]

                team2 = df_raw.iloc[i + 1, team_col]
                moneyline2 = df_raw.iloc[i + 1, moneyline_col]
                line2 = df_raw.iloc[i + 1, line_col]
                total2 = df_raw.iloc[i + 1, total_col]

                # Skip if missing data
                if pd.isna(team1) or pd.isna(team2) or pd.isna(line1) or pd.isna(line2):
                    continue

                # Parse run line from strings like "-1.5 +112" or "(+1.5) +112"
                # Extract just the spread value (-1.5 or +1.5)
                try:
                    line1_str = str(line1).strip()
                    line2_str = str(line2).strip()

                    # Remove parentheses
                    line1_str = line1_str.replace('(', '').replace(')', '')
                    line2_str = line2_str.replace('(', '').replace(')', '')

                    # Split on space and take first part (the spread)
                    line1_parsed = float(line1_str.split()[0])
                    line2_parsed = float(line2_str.split()[0])
                except (ValueError, IndexError, AttributeError):
                    continue

                # Replace line1/line2 with parsed spreads
                line1 = line1_parsed
                line2 = line2_parsed

                # Verify rows are same game by checking if they share a total
                if not pd.isna(total1) and not pd.isna(total2):
                    try:
                        if abs(float(total1) - float(total2)) > 0.1:
                            # Different totals = not same game, skip
                            continue
                    except (ValueError, TypeError):
                        pass

                team1_str = str(team1).strip()
                team2_str = str(team2).strip()

                # Use total1 as the shared total (both should be same)
                total = total1 if not pd.isna(total1) else total2

                # Parse moneyline prices (e.g., "+146", "-133")
                ml1 = None
                ml2 = None
                if not pd.isna(moneyline1):
                    try:
                        ml1 = int(str(moneyline1).strip().replace('+', ''))
                    except (ValueError, AttributeError):
                        pass
                if not pd.isna(moneyline2):
                    try:
                        ml2 = int(str(moneyline2).strip().replace('+', ''))
                    except (ValueError, AttributeError):
                        pass

                row1 = pd.Series({'Team': team1_str, "Greg's Line": line1, 'Total': total, 'Moneyline': ml1})
                row2 = pd.Series({'Team': team2_str, "Greg's Line": line2, 'Total': total, 'Moneyline': ml2})

                game = self.parse_game_pair(row1, row2, game_date)
                if game:
                    # DEBUG: Print first few games to verify team names
                    if len(games) < 3:
                        print(f"DEBUG - Parsed game: {team1_str} @ {team2_str} (Total: {total1 if not pd.isna(total1) else 'N/A'})")
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
