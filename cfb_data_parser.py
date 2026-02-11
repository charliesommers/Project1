"""
College Football Data Parser
Parses historical CFB game data from collegefootballdata.com API.
"""
import pandas as pd
import requests
from datetime import datetime
from typing import Dict, List, Optional

# CFB API configuration
CFB_API_BASE = "https://api.collegefootballdata.com"
CFB_API_KEY = "j7wLOx+5DDn/0NLX3r5n5oQ83Qmj3ILFQCI2JYf8m4rb2Pyo0rWBcQzU60T3FDEP"


class CFBDataParser:
    """Parser for College Football data from collegefootballdata.com API."""

    def __init__(self, api_key: str = CFB_API_KEY):
        """
        Initialize parser.

        Args:
            api_key: API key for collegefootballdata.com
        """
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Accept': 'application/json'
        }
        self.all_games = []

    def fetch_games(self, year: int, week: Optional[int] = None,
                    season_type: str = "regular") -> List[Dict]:
        """
        Fetch games from CFB API.

        Args:
            year: Season year (e.g., 2024)
            week: Optional week number
            season_type: 'regular' or 'postseason'

        Returns:
            List of raw game data from API
        """
        try:
            url = f"{CFB_API_BASE}/games"
            params = {
                'year': year,
                'seasonType': season_type
            }

            if week:
                params['week'] = week

            print(f"Fetching CFB games: year={year}, week={week}, type={season_type}")
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()

            games = response.json()
            print(f"✓ Fetched {len(games)} games from API")
            return games

        except Exception as e:
            print(f"Error fetching CFB games: {e}")
            return []

    def fetch_betting_lines(self, year: int, week: Optional[int] = None,
                           season_type: str = "regular") -> Dict:
        """
        Fetch betting lines for games.

        Args:
            year: Season year
            week: Optional week number
            season_type: 'regular' or 'postseason'

        Returns:
            Dictionary mapping game_id to betting lines
        """
        try:
            url = f"{CFB_API_BASE}/lines"
            params = {
                'year': year,
                'seasonType': season_type
            }

            if week:
                params['week'] = week

            print(f"Fetching CFB betting lines: year={year}, week={week}")
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            response.raise_for_status()

            lines_data = response.json()
            print(f"✓ Fetched betting lines for {len(lines_data)} games")

            # Build lookup by game_id
            lines_lookup = {}
            for game_lines in lines_data:
                game_id = game_lines.get('id')
                if game_id and game_lines.get('lines'):
                    # Use consensus or first available line
                    lines = game_lines['lines']
                    if lines:
                        # Prefer consensus, otherwise first line
                        consensus = next((l for l in lines if l.get('provider') == 'consensus'), lines[0])
                        lines_lookup[game_id] = consensus

            return lines_lookup

        except Exception as e:
            print(f"Error fetching betting lines: {e}")
            return {}

    def parse_games(self, year: int, week: Optional[int] = None,
                    season_type: str = "regular", include_lines: bool = True) -> List[Dict]:
        """
        Parse CFB games with optional betting lines.

        Args:
            year: Season year (e.g., 2024)
            week: Optional week number
            season_type: 'regular' or 'postseason'
            include_lines: Whether to fetch betting lines

        Returns:
            List of parsed game dictionaries
        """
        # Fetch games
        raw_games = self.fetch_games(year, week, season_type)
        if not raw_games:
            return []

        # Fetch betting lines if requested
        lines_lookup = {}
        if include_lines:
            lines_lookup = self.fetch_betting_lines(year, week, season_type)

        games = []

        for raw_game in raw_games:
            try:
                game_id = raw_game.get('id')

                # Parse date
                start_date = raw_game.get('start_date')
                if start_date:
                    game_date = pd.to_datetime(start_date).date()
                else:
                    continue

                # Get betting lines for this game
                lines = lines_lookup.get(game_id, {})

                # Parse spread (formatted as "-7.0" for favorite)
                spread = lines.get('formattedSpread')
                spread_value = None
                if spread:
                    try:
                        spread_value = float(spread.replace('+', ''))
                    except:
                        pass

                # Parse total
                total = lines.get('overUnder')
                if total:
                    try:
                        total = float(total)
                    except:
                        total = None

                game = {
                    'game_id': game_id,
                    'season': int(raw_game['season']),
                    'week': int(raw_game['week']),
                    'season_type': raw_game.get('season_type'),
                    'date': game_date,
                    'away_team': raw_game.get('away_team'),
                    'home_team': raw_game.get('home_team'),
                    'away_points': int(raw_game['away_points']) if raw_game.get('away_points') else None,
                    'home_points': int(raw_game['home_points']) if raw_game.get('home_points') else None,
                    'away_conference': raw_game.get('away_conference'),
                    'home_conference': raw_game.get('home_conference'),

                    # Betting lines (if available)
                    'spread': spread_value,
                    'spread_open': lines.get('spreadOpen'),
                    'total': total,
                    'over_under_open': lines.get('overUnderOpen'),
                    'home_moneyline': lines.get('homeMoneyline'),
                    'away_moneyline': lines.get('awayMoneyline'),

                    # Game details
                    'venue': raw_game.get('venue'),
                    'attendance': raw_game.get('attendance'),
                    'completed': raw_game.get('completed', False),
                }

                games.append(game)

            except Exception as e:
                # Skip problematic games
                continue

        print(f"\nParsed {len(games)} CFB games")

        # Show sample
        if games:
            print("\nSample games:")
            for i, game in enumerate(games[:3]):
                print(f"\nGame {i+1}:")
                print(f"  {game['away_team']} @ {game['home_team']}")
                print(f"  Date: {game['date']}")
                if game['completed']:
                    print(f"  Score: {game['away_points']}-{game['home_points']}")
                if game['spread']:
                    print(f"  Spread: {game['spread']}, Total: {game['total']}")

        self.all_games = games
        return games


if __name__ == '__main__':
    import sys

    parser = CFBDataParser()

    # Parse arguments
    year = int(sys.argv[1]) if len(sys.argv) > 1 else 2024
    week = int(sys.argv[2]) if len(sys.argv) > 2 else None
    season_type = sys.argv[3] if len(sys.argv) > 3 else "regular"

    games = parser.parse_games(year=year, week=week, season_type=season_type)

    print(f"\n{'='*80}")
    print(f"Total CFB games: {len(games)}")
    print(f"{'='*80}")
