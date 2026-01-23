"""
Game Scores Fetcher
Fetches historical game scores for performance tracking
"""
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import time


class ScoresFetcher:
    """Fetches game scores from sports APIs."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize scores fetcher.

        Args:
            api_key: API key for The Odds API or ESPN API
        """
        self.api_key = api_key
        self.base_url = "https://api.the-odds-api.com/v4"
        self.espn_base = "https://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball"

    def fetch_scores_from_espn(self, date: datetime) -> List[Dict]:
        """
        Fetch scores from ESPN API (free, no key required).

        Args:
            date: Date to fetch scores for

        Returns:
            List of completed games with scores
        """
        date_str = date.strftime('%Y%m%d')
        endpoint = f"{self.espn_base}/scoreboard"

        params = {
            'dates': date_str,
            'limit': 1000
        }

        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            games = []
            events = data.get('events', [])

            for event in events:
                game = self._parse_espn_game(event)
                if game:
                    games.append(game)

            return games

        except requests.exceptions.RequestException as e:
            print(f"Error fetching scores from ESPN: {e}")
            return []

    def _parse_espn_game(self, event: Dict) -> Optional[Dict]:
        """Parse ESPN game data."""
        try:
            # Check if game is completed
            status = event.get('status', {})
            if status.get('type', {}).get('name') != 'STATUS_FINAL':
                return None

            competitions = event.get('competitions', [])
            if not competitions:
                return None

            competition = competitions[0]
            competitors = competition.get('competitors', [])

            if len(competitors) != 2:
                return None

            # Get teams and scores
            home_team = None
            away_team = None
            home_score = None
            away_score = None

            for competitor in competitors:
                team_name = competitor.get('team', {}).get('displayName', '')
                score = int(competitor.get('score', 0))

                if competitor.get('homeAway') == 'home':
                    home_team = team_name
                    home_score = score
                else:
                    away_team = team_name
                    away_score = score

            if not all([home_team, away_team, home_score is not None, away_score is not None]):
                return None

            # Calculate total
            total_score = home_score + away_score

            # Determine winner and margin
            if home_score > away_score:
                winner = home_team
                margin = home_score - away_score
            else:
                winner = away_team
                margin = away_score - home_score

            game_date = event.get('date', '')
            if game_date:
                game_date = datetime.fromisoformat(game_date.replace('Z', '+00:00'))

            return {
                'date': game_date,
                'home_team': home_team,
                'away_team': away_team,
                'home_score': home_score,
                'away_score': away_score,
                'total_score': total_score,
                'winner': winner,
                'margin': margin,
                'matchup': f"{away_team} @ {home_team}",
                'final_score': f"{away_team} {away_score}, {home_team} {home_score}"
            }

        except Exception as e:
            print(f"Error parsing ESPN game: {e}")
            return None

    def match_game(self, gregs_game: Dict, scored_games: List[Dict]) -> Optional[Dict]:
        """
        Match Greg's game to a completed game with scores.

        Args:
            gregs_game: Game from Greg's parser
            scored_games: List of games with scores

        Returns:
            Matched game with scores or None
        """
        gregs_fav = gregs_game['favorite'].lower().strip()
        gregs_dog = gregs_game['underdog'].lower().strip()

        for scored_game in scored_games:
            home = scored_game['home_team'].lower().strip()
            away = scored_game['away_team'].lower().strip()

            # Check if teams match (in either order)
            fav_matches_home = self._teams_match(gregs_fav, home)
            fav_matches_away = self._teams_match(gregs_fav, away)
            dog_matches_home = self._teams_match(gregs_dog, home)
            dog_matches_away = self._teams_match(gregs_dog, away)

            if (fav_matches_home and dog_matches_away) or (fav_matches_away and dog_matches_home):
                return scored_game

        return None

    def _teams_match(self, team1: str, team2: str) -> bool:
        """Check if two team names match (fuzzy matching)."""
        team1 = team1.lower().strip()
        team2 = team2.lower().strip()

        # Direct match
        if team1 == team2:
            return True

        # Contains match
        if team1 in team2 or team2 in team1:
            return True

        # Common abbreviations
        abbrevs = {
            'st': 'state',
            'state': 'st',
            'uw': 'wisconsin',
            'usc': 'southern california',
            # Add more as needed
        }

        for abbrev, full in abbrevs.items():
            if abbrev in team1 and full in team2:
                return True
            if full in team1 and abbrev in team2:
                return True

        return False

    def fetch_scores_range(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """
        Fetch scores for a date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            List of all games in date range
        """
        all_games = []
        current_date = start_date

        while current_date <= end_date:
            print(f"Fetching scores for {current_date.strftime('%m/%d/%Y')}...")
            games = self.fetch_scores_from_espn(current_date)
            all_games.extend(games)

            # Rate limiting - be nice to ESPN
            time.sleep(0.5)

            current_date += timedelta(days=1)

        return all_games
