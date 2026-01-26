"""
Sportsbook Odds Fetcher
Fetches live betting lines from various sportsbooks
"""
import requests
from typing import Dict, List, Optional
from datetime import datetime
import os
from pathlib import Path

# Try to load .env file if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class OddsFetcher:
    """Fetches odds from sports betting APIs."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize odds fetcher.

        Args:
            api_key: API key for The Odds API (get free key at the-odds-api.com)
        """
        self.api_key = api_key or os.environ.get('ODDS_API_KEY')
        self.base_url = "https://api.the-odds-api.com/v4"

    def fetch_ncaab_odds_all_bookmakers(self) -> List[Dict]:
        """
        Fetch NCAA Basketball odds from ALL bookmakers in a single API request.
        More efficient than calling fetch_ncaab_odds() multiple times.

        Returns:
            List of games with odds from all available bookmakers
        """
        if not self.api_key:
            print("ERROR: No API key provided. Set ODDS_API_KEY environment variable")
            return []

        print(f"Using API key: {self.api_key[:8]}...{self.api_key[-4:]}")

        endpoint = f"{self.base_url}/sports/basketball_ncaab/odds"

        # Don't specify bookmakers parameter to get ALL bookmakers
        params = {
            'apiKey': self.api_key,
            'regions': 'us',
            'markets': 'h2h,spreads,totals',
            'oddsFormat': 'american'
        }

        print(f"Fetching odds from: {endpoint}")
        print(f"Getting ALL US bookmakers in single request")

        try:
            response = requests.get(endpoint, params=params, timeout=30)
            print(f"API Response Status: {response.status_code}")

            if response.status_code == 401:
                print("ERROR: 401 Unauthorized - API key is invalid")
                return []
            elif response.status_code == 429:
                print("ERROR: 429 Rate limit exceeded - API quota exhausted")
                return []

            response.raise_for_status()
            games = response.json()

            # Parse and structure the data
            structured_games = []

            for game in games:
                home_team = game.get('home_team', '')
                away_team = game.get('away_team', '')
                commence_time = game.get('commence_time', '')

                # Get bookmakers data
                bookmakers_data = game.get('bookmakers', [])

                # Process each bookmaker's odds for this game
                for bookmaker_info in bookmakers_data:
                    bookmaker_name = bookmaker_info.get('key', '')
                    markets = bookmaker_info.get('markets', [])

                    # Extract totals and spreads
                    total = None
                    spread = None

                    for market in markets:
                        if market.get('key') == 'totals':
                            outcomes = market.get('outcomes', [])
                            if outcomes:
                                total = outcomes[0].get('point')  # Over/Under line
                        elif market.get('key') == 'spreads':
                            outcomes = market.get('outcomes', [])
                            # Find home team spread
                            for outcome in outcomes:
                                if outcome.get('name') == home_team:
                                    spread = outcome.get('point')
                                    break

                    if total or spread:
                        structured_games.append({
                            'home_team': home_team,
                            'away_team': away_team,
                            'commence_time': commence_time,
                            'total': total,
                            'spread': spread,
                            'source_bookmaker': bookmaker_name
                        })

            print(f"✓ Fetched {len(structured_games)} game-bookmaker combinations")
            return structured_games

        except requests.exceptions.RequestException as e:
            print(f"Error fetching odds: {e}")
            return []

    def fetch_ncaab_odds(self, bookmaker: str = 'bet365') -> List[Dict]:
        """
        Fetch NCAA Basketball odds.

        Args:
            bookmaker: Bookmaker to get odds from (default: bet365)
                      Options: bet365, fanduel, draftkings, betmgm, etc.

        Returns:
            List of games with odds
        """
        if not self.api_key:
            print("ERROR: No API key provided. Set ODDS_API_KEY environment variable")
            print("Get a free key at: https://the-odds-api.com")
            print(f"Current API key value: {self.api_key}")
            return []

        print(f"Using API key: {self.api_key[:8]}...{self.api_key[-4:]}")  # Show partial key

        endpoint = f"{self.base_url}/sports/basketball_ncaab/odds"

        params = {
            'apiKey': self.api_key,
            'regions': 'us',
            'markets': 'h2h,spreads,totals',
            'oddsFormat': 'american',
            'bookmakers': bookmaker
        }

        print(f"Fetching odds from: {endpoint}")
        print(f"Bookmaker: {bookmaker}")

        try:
            response = requests.get(endpoint, params=params, timeout=30)
            print(f"API Response Status: {response.status_code}")

            if response.status_code == 401:
                print("ERROR: 401 Unauthorized - API key is invalid")
                print(f"API key used: {self.api_key}")
                return []
            elif response.status_code == 429:
                print("ERROR: 429 Rate limit exceeded - API quota exhausted")
                return []

            response.raise_for_status()
            games = response.json()

            # Parse and structure the data
            structured_games = []
            for game in games:
                parsed_game = self._parse_odds_response(game, bookmaker)
                if parsed_game:
                    structured_games.append(parsed_game)

            return structured_games

        except requests.exceptions.RequestException as e:
            print(f"Error fetching odds: {e}")
            return []

    def _parse_odds_response(self, game: Dict, bookmaker: str) -> Optional[Dict]:
        """Parse API response into structured format."""
        try:
            away_team = game.get('away_team', '')
            home_team = game.get('home_team', '')
            commence_time = game.get('commence_time', '')

            # Find bookmaker data
            bookmakers_data = game.get('bookmakers', [])
            bookmaker_data = None

            for bm in bookmakers_data:
                if bm.get('key') == bookmaker:
                    bookmaker_data = bm
                    break

            if not bookmaker_data:
                return None

            markets = bookmaker_data.get('markets', [])

            # Extract spreads and totals
            spread_data = None
            total_data = None

            for market in markets:
                if market['key'] == 'spreads':
                    spread_data = market
                elif market['key'] == 'totals':
                    total_data = market

            result = {
                'home_team': home_team,
                'away_team': away_team,
                'matchup': f"{away_team} @ {home_team}",
                'commence_time': commence_time,
                'bookmaker': bookmaker,
            }

            # Parse spread
            if spread_data:
                outcomes = spread_data.get('outcomes', [])
                for outcome in outcomes:
                    if outcome['name'] == home_team:
                        result['home_spread'] = outcome.get('point')
                        result['home_spread_odds'] = outcome.get('price')
                    elif outcome['name'] == away_team:
                        result['away_spread'] = outcome.get('point')
                        result['away_spread_odds'] = outcome.get('price')

            # Parse total
            if total_data:
                outcomes = total_data.get('outcomes', [])
                for outcome in outcomes:
                    if outcome['name'] == 'Over':
                        result['total'] = outcome.get('point')
                        result['over_odds'] = outcome.get('price')
                    elif outcome['name'] == 'Under':
                        result['under_odds'] = outcome.get('price')

            return result

        except Exception as e:
            print(f"Error parsing game data: {e}")
            return None

    def match_teams(self, gregs_team: str, odds_teams: List[str]) -> Optional[str]:
        """
        Match Greg's team name to sportsbook team name.

        Args:
            gregs_team: Team name from Greg's spreadsheet
            odds_teams: List of team names from odds API

        Returns:
            Matched team name or None
        """
        # Simple matching - can be improved with fuzzy matching
        gregs_team_lower = gregs_team.lower().strip()

        for team in odds_teams:
            team_lower = team.lower().strip()

            # Direct match
            if gregs_team_lower == team_lower:
                return team

            # Contains match
            if gregs_team_lower in team_lower or team_lower in gregs_team_lower:
                return team

            # Common abbreviations and variations
            # This can be expanded with a mapping dictionary

        return None

    def get_manual_odds_template(self, games: List[Dict]) -> str:
        """
        Generate a CSV template for manually entering odds.

        Args:
            games: List of games from Greg's parser

        Returns:
            CSV string template
        """
        csv_lines = ["Matchup,Favorite,Spread,Total,Sportsbook_Spread,Sportsbook_Total"]

        for game in games:
            csv_lines.append(
                f"{game['matchup']},{game['favorite']},{game['spread']},{game['total']},,")

        return "\n".join(csv_lines)

    def load_manual_odds(self, csv_file: str) -> List[Dict]:
        """
        Load manually entered odds from CSV file.

        Args:
            csv_file: Path to CSV file with sportsbook odds

        Returns:
            List of games with both Greg's and sportsbook odds
        """
        import csv

        games = []
        try:
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get('Sportsbook_Spread') and row.get('Sportsbook_Total'):
                        games.append({
                            'matchup': row['Matchup'],
                            'favorite': row['Favorite'],
                            'gregs_spread': float(row['Spread']),
                            'gregs_total': float(row['Total']),
                            'sportsbook_spread': float(row['Sportsbook_Spread']),
                            'sportsbook_total': float(row['Sportsbook_Total']),
                        })
        except Exception as e:
            print(f"Error loading manual odds: {e}")

        return games
