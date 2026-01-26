#!/usr/bin/env python3
"""
Scrape historical betting lines from free sources (Covers.com).
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import time


class HistoricalOddsScraper:
    """Scrape historical betting lines from free sources."""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def fetch_covers_odds(self, date: datetime) -> List[Dict]:
        """
        Fetch historical odds from Covers.com.

        Args:
            date: Date to fetch odds for

        Returns:
            List of games with betting lines
        """
        date_str = date.strftime('%Y-%m-%d')
        url = f"https://www.covers.com/sports/basketball/ncaab/matchups?selectedDate={date_str}"

        try:
            print(f"    Fetching Covers.com for {date_str}...")
            response = requests.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            games = []

            # Covers uses various class names, try multiple approaches
            game_elements = soup.find_all('div', class_=lambda x: x and 'matchup' in x.lower())

            if not game_elements:
                # Try alternative selectors
                game_elements = soup.find_all('tr', class_=lambda x: x and 'game' in x.lower())

            print(f"    Found {len(game_elements)} potential game elements")

            for elem in game_elements:
                try:
                    game_data = self._parse_covers_game(elem)
                    if game_data:
                        games.append(game_data)
                except Exception as e:
                    print(f"    Error parsing game: {e}")
                    continue

            print(f"    Successfully parsed {len(games)} games with odds")
            return games

        except Exception as e:
            print(f"    Error fetching from Covers.com: {e}")
            return []

    def _parse_covers_game(self, element) -> Optional[Dict]:
        """Parse a single game element from Covers."""
        # This is a template - actual parsing depends on Covers' HTML structure
        # Will need to inspect the actual page to get correct selectors

        try:
            # Look for team names
            team_elements = element.find_all('a', class_=lambda x: x and 'team' in x.lower())
            if len(team_elements) < 2:
                team_elements = element.find_all('span', class_=lambda x: x and 'team' in x.lower())

            if len(team_elements) >= 2:
                away_team = team_elements[0].get_text(strip=True)
                home_team = team_elements[1].get_text(strip=True)

                # Look for total (over/under)
                total_elem = element.find(text=lambda t: t and ('o' in t.lower() or 'u' in t.lower()))
                total = None

                if total_elem:
                    # Try to extract number from text like "o145.5" or "U 145"
                    import re
                    total_match = re.search(r'(\d+\.?\d*)', str(total_elem))
                    if total_match:
                        total = float(total_match.group(1))

                # Look for spread
                spread_elem = element.find(text=lambda t: t and ('+' in str(t) or '-' in str(t)))
                spread = None

                if spread_elem:
                    import re
                    spread_match = re.search(r'([+-]?\d+\.?\d*)', str(spread_elem))
                    if spread_match:
                        spread = float(spread_match.group(1))

                if total or spread:
                    return {
                        'away_team': away_team,
                        'home_team': home_team,
                        'total': total,
                        'spread': spread,
                        'matchup': f"{away_team} @ {home_team}"
                    }

        except Exception as e:
            print(f"    Parse error: {e}")

        return None

    def fetch_odds_range(self, start_date: datetime, end_date: datetime) -> Dict[str, List[Dict]]:
        """
        Fetch odds for a date range.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            Dictionary mapping date strings to lists of games
        """
        odds_by_date = {}
        current_date = start_date

        while current_date <= end_date:
            date_str = current_date.strftime('%Y-%m-%d')
            games = self.fetch_covers_odds(current_date)

            if games:
                odds_by_date[date_str] = games

            # Rate limiting
            time.sleep(2)

            current_date += timedelta(days=1)

        return odds_by_date


if __name__ == '__main__':
    # Test the scraper
    print("Testing Historical Odds Scraper")
    print("=" * 80)

    scraper = HistoricalOddsScraper()

    # Test with a recent date
    test_date = datetime(2026, 1, 25)
    print(f"\nFetching odds for {test_date.strftime('%Y-%m-%d')}...")

    games = scraper.fetch_covers_odds(test_date)

    if games:
        print(f"\n✓ Successfully fetched {len(games)} games")
        print("\nSample games:")
        for i, game in enumerate(games[:3], 1):
            print(f"\n{i}. {game['matchup']}")
            if game.get('total'):
                print(f"   Total: {game['total']}")
            if game.get('spread'):
                print(f"   Spread: {game['spread']:+.1f}")
    else:
        print("\n✗ No games fetched - scraper needs adjustment or source unavailable")
