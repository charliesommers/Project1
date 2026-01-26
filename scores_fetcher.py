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
        self.sr_base = "https://www.sports-reference.com/cbb"

    def fetch_schedule_from_espn(self, date: datetime) -> List[Dict]:
        """
        Fetch game schedule from ESPN API (includes upcoming games with times).

        Args:
            date: Date to fetch schedule for

        Returns:
            List of all games (completed and upcoming) with times
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
                game = self._parse_espn_schedule_event(event)
                if game:
                    games.append(game)

            return games

        except requests.exceptions.RequestException as e:
            print(f"Error fetching schedule from ESPN: {e}")
            return []

    def fetch_schedule_from_sportsref(self, date: datetime) -> List[Dict]:
        """
        Fetch game schedule from Sports-Reference (comprehensive D1 coverage).

        Args:
            date: Date to fetch schedule for

        Returns:
            List of all games with times from Sports-Reference
        """
        from bs4 import BeautifulSoup

        # Sports-Reference URL format
        url = f"{self.sr_base}/boxscores/index.cgi?month={date.month}&day={date.day}&year={date.year}"

        print(f"    Fetching from URL: {url}")

        try:
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            print(f"    Response status: {response.status_code}")

            soup = BeautifulSoup(response.content, 'html.parser')
            games = []

            # Find all game divs
            game_divs = soup.find_all('div', class_='game_summary')
            print(f"    Found {len(game_divs)} game divs on page")

            if len(game_divs) == 0:
                # Try alternative selectors
                print("    Trying alternative selector: div.teams")
                game_divs = soup.find_all('div', class_='teams')
                print(f"    Found {len(game_divs)} with alternative selector")

            for idx, game_div in enumerate(game_divs):
                try:
                    # Get teams
                    teams = game_div.find_all('tr')
                    if len(teams) < 2:
                        print(f"    Game {idx}: Not enough team rows ({len(teams)})")
                        continue

                    away_team_elem = teams[0].find('a')
                    home_team_elem = teams[1].find('a')

                    if not away_team_elem or not home_team_elem:
                        print(f"    Game {idx}: Missing team links")
                        continue

                    away_team = away_team_elem.text.strip()
                    home_team = home_team_elem.text.strip()

                    # Get game time
                    time_elem = game_div.find('td', class_='right gamelink')
                    if not time_elem:
                        # Try alternative selector
                        time_elem = game_div.find('td', class_='gamelink')

                    if time_elem:
                        time_text = time_elem.text.strip()
                        print(f"    Game {idx}: {away_team} @ {home_team} - Time: {time_text}")
                        # Parse time like "7:00 pm" or "12:00 pm"
                        game_time = self._parse_sportsref_time(date, time_text)
                    else:
                        print(f"    Game {idx}: {away_team} @ {home_team} - No time element found")
                        game_time = None

                    if game_time:
                        games.append({
                            'date': game_time,
                            'home_team': home_team,
                            'away_team': away_team,
                            'matchup': f"{away_team} @ {home_team}",
                            'commence_time': game_time.isoformat(),
                            'status': 'scheduled'
                        })
                    else:
                        print(f"    Game {idx}: Skipping - no valid time")

                except Exception as e:
                    print(f"    Error parsing Sports-Reference game {idx}: {e}")
                    continue

            print(f"    Successfully parsed {len(games)} games with valid times")
            return games

        except requests.exceptions.RequestException as e:
            print(f"    Error fetching schedule from Sports-Reference: {e}")
            return []

    def _parse_sportsref_time(self, date: datetime, time_str: str) -> Optional[datetime]:
        """Parse Sports-Reference time string to datetime."""
        try:
            import pytz
            from datetime import time as dt_time

            # Remove any extra whitespace
            time_str = time_str.strip().lower()

            # Parse time like "7:00 pm" or "12:30 pm"
            if 'pm' in time_str or 'am' in time_str:
                time_part = time_str.replace('pm', '').replace('am', '').strip()
                hour, minute = map(int, time_part.split(':'))

                if 'pm' in time_str and hour != 12:
                    hour += 12
                elif 'am' in time_str and hour == 12:
                    hour = 0

                # Combine date with parsed time (assume Eastern Time for Sports-Reference)
                eastern = pytz.timezone('US/Eastern')
                game_time = eastern.localize(datetime(date.year, date.month, date.day, hour, minute))

                # Convert to UTC
                utc_time = game_time.astimezone(pytz.UTC)
                return utc_time

            return None

        except Exception as e:
            print(f"Error parsing time '{time_str}': {e}")
            return None

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

    def _parse_espn_schedule_event(self, event: Dict) -> Optional[Dict]:
        """Parse ESPN schedule event (upcoming or completed games)."""
        try:
            status = event.get('status', {})
            status_type = status.get('type', {}).get('name', '')

            competitions = event.get('competitions', [])
            if not competitions:
                return None

            competition = competitions[0]
            competitors = competition.get('competitors', [])

            if len(competitors) != 2:
                return None

            # Get teams
            home_team = None
            away_team = None

            for competitor in competitors:
                team_name = competitor.get('team', {}).get('displayName', '')
                if competitor.get('homeAway') == 'home':
                    home_team = team_name
                else:
                    away_team = team_name

            if not home_team or not away_team:
                return None

            # Get game date/time
            game_date = event.get('date', '')
            if game_date:
                game_date = datetime.fromisoformat(game_date.replace('Z', '+00:00'))
            else:
                return None

            return {
                'date': game_date,
                'home_team': home_team,
                'away_team': away_team,
                'matchup': f"{away_team} @ {home_team}",
                'commence_time': game_date.isoformat(),
                'status': status_type
            }

        except Exception as e:
            print(f"Error parsing ESPN schedule event: {e}")
            return None

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

        # Remove common mascots/nicknames from sportsbook names
        mascots = [
            'aggies', 'aztecs', 'badgers', 'bears', 'bearcats', 'beavers', 'bengals',
            'blue devils', 'bobcats', 'broncos', 'bruins', 'buccaneers', 'buckeyes',
            'buffalo', 'bulldogs', 'cardinals', 'chanticleers', 'cougars', 'cowboys',
            'crimson tide', 'crusaders', 'cyclones', 'demons', 'ducks', 'eagles',
            'falcons', 'fighting irish', 'gators', 'golden eagles', 'golden gophers',
            'grizzlies', 'hawkeyes', 'hilltoppers', 'hokies', 'hornets', 'huskies',
            'hurricanes', 'jayhawks', 'knights', 'lancers', 'lions', 'lobos',
            'miners', 'mountaineers', 'musketeers', 'nittany lions', 'orangemen',
            'owls', 'panthers', 'pirates', 'ragin cajuns', 'ramblers', 'rams',
            'razorbacks', 'red flash', 'red raiders', 'red storm', 'rebels',
            'river hawks', 'salukis', 'seminoles', 'sharks', 'skyhawks', 'sooners',
            'spartans', 'sun devils', 'tar heels', 'terrapins', 'tigers', 'titans',
            'trojans', 'utes', 'volunteers', 'wildcats', 'wolverines', 'wolfpack'
        ]

        for mascot in mascots:
            team1 = team1.replace(mascot, '').strip()
            team2 = team2.replace(mascot, '').strip()

        # Direct match
        if team1 == team2:
            return True

        # Contains match
        if team1 in team2 or team2 in team1:
            return True

        # Common abbreviations and variations
        replacements = {
            'st.': 'state', 'st ': 'state ', ' st': ' state',
            'fl ': 'florida ', 'fl.': 'florida',
            'nc ': 'north carolina ', 'nc.': 'north carolina',
            'uconn': 'connecticut',
            'coast carolina': 'coastal carolina',
            'southern miss': 'southern mississippi',
            'new mexico st': 'new mexico state',
            'florida international': 'fl international',
            'fiu': 'florida international',
            'ucf': 'central florida',
            'lsu': 'louisiana state',
            'ole miss': 'mississippi',
            'miami fl': 'miami',
            'miami oh': 'miami ohio',
            'vcu': 'virginia commonwealth',
            'usc': 'southern california',
            'unc': 'north carolina',
            'unlv': 'nevada las vegas',
        }

        # Apply replacements to both teams
        t1_normalized = team1
        t2_normalized = team2

        for abbrev, full in replacements.items():
            t1_normalized = t1_normalized.replace(abbrev, full)
            t2_normalized = t2_normalized.replace(abbrev, full)

        # Check normalized versions
        if t1_normalized == t2_normalized:
            return True

        if t1_normalized in t2_normalized or t2_normalized in t1_normalized:
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
