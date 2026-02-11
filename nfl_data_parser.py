"""
NFL Data Parser
Parses historical NFL game data from nflverse dataset.
"""
import pandas as pd
import requests
from datetime import datetime
from typing import Dict, List, Optional

# NFL data source
NFL_DATA_URL = "https://raw.githubusercontent.com/nflverse/nfldata/master/data/games.csv"


class NFLDataParser:
    """Parser for NFL historical game data from nflverse."""

    def __init__(self, data_url: str = NFL_DATA_URL):
        """
        Initialize parser.

        Args:
            data_url: URL to NFL games CSV
        """
        self.data_url = data_url
        self.df = None
        self.all_games = []

    def load_data(self) -> bool:
        """Load NFL data from URL."""
        try:
            print(f"Loading NFL data from: {self.data_url}")
            self.df = pd.read_csv(self.data_url)
            print(f"✓ Loaded {len(self.df)} NFL games")
            return True
        except Exception as e:
            print(f"Error loading NFL data: {e}")
            return False

    def parse_games(self, season: Optional[int] = None, week: Optional[int] = None) -> List[Dict]:
        """
        Parse NFL games.

        Args:
            season: Optional season filter (e.g., 2024)
            week: Optional week filter (e.g., 1-18)

        Returns:
            List of game dictionaries
        """
        if self.df is None:
            if not self.load_data():
                return []

        df = self.df.copy()

        # Apply filters
        if season:
            df = df[df['season'] == season]
            print(f"Filtered to season {season}: {len(df)} games")

        if week:
            df = df[df['week'] == week]
            print(f"Filtered to week {week}: {len(df)} games")

        games = []

        for idx, row in df.iterrows():
            try:
                # Parse game date
                game_date = pd.to_datetime(row['gameday']).date()

                game = {
                    'game_id': row.get('game_id'),
                    'season': int(row['season']),
                    'week': int(row['week']),
                    'game_type': row.get('game_type'),  # REG, POST, etc.
                    'date': game_date,
                    'away_team': row.get('away_team'),
                    'home_team': row.get('home_team'),
                    'away_score': int(row['away_score']) if pd.notna(row.get('away_score')) else None,
                    'home_score': int(row['home_score']) if pd.notna(row.get('home_score')) else None,
                    'total': float(row['total_line']) if pd.notna(row.get('total_line')) else None,
                    'away_spread': float(row['spread_line']) if pd.notna(row.get('spread_line')) else None,
                    'away_moneyline': int(row['away_moneyline']) if pd.notna(row.get('away_moneyline')) else None,
                    'home_moneyline': int(row['home_moneyline']) if pd.notna(row.get('home_moneyline')) else None,
                    'over_odds': int(row['over_odds']) if pd.notna(row.get('over_odds')) else None,
                    'under_odds': int(row['under_odds']) if pd.notna(row.get('under_odds')) else None,
                    'stadium': row.get('stadium'),
                    'location': row.get('location'),
                }

                games.append(game)

            except Exception as e:
                # Skip problematic rows
                continue

        print(f"\nParsed {len(games)} NFL games")

        # Show sample
        if games:
            print("\nSample games:")
            for i, game in enumerate(games[:3]):
                print(f"\nGame {i+1}:")
                print(f"  {game['away_team']} @ {game['home_team']}")
                print(f"  Date: {game['date']}")
                print(f"  Score: {game['away_score']}-{game['home_score']}")
                print(f"  Spread: {game['away_spread']}, Total: {game['total']}")

        self.all_games = games
        return games


if __name__ == '__main__':
    import sys

    parser = NFLDataParser()

    # Parse season from command line or use current season
    season = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
    week = int(sys.argv[2]) if len(sys.argv) > 2 else None

    games = parser.parse_games(season=season, week=week)

    print(f"\n{'='*80}")
    print(f"Total NFL games: {len(games)}")
    print(f"{'='*80}")
