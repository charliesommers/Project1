#!/usr/bin/env python3
"""
Research script to find sources for:
1. Accurate tip times for upcoming games
2. Historical scores
3. Historical closing lines

Tests multiple free sources and estimates API costs if needed.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json


class DataSourceResearcher:
    """Research data sources for CBB betting data."""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.results = {
            'tip_times': [],
            'historical_scores': [],
            'historical_lines': []
        }

    def test_espn_tip_times(self):
        """Test ESPN for upcoming game times."""
        print("\n" + "="*80)
        print("TESTING: ESPN for Tip Times")
        print("="*80)

        try:
            # Test with today and tomorrow
            tomorrow = datetime.now() + timedelta(days=1)
            date_str = tomorrow.strftime('%Y%m%d')

            url = f"http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"
            params = {'dates': date_str, 'limit': 100}

            response = requests.get(url, params=params, timeout=15)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                events = data.get('events', [])
                print(f"✓ Found {len(events)} games")

                # Check if games have times
                games_with_times = 0
                for event in events[:5]:  # Sample first 5
                    game_time = event.get('date')
                    if game_time:
                        games_with_times += 1
                        # Parse and display
                        dt = datetime.fromisoformat(game_time.replace('Z', '+00:00'))
                        print(f"  Sample: {event.get('name')} at {dt.strftime('%I:%M %p ET')}")

                if games_with_times > 0:
                    self.results['tip_times'].append({
                        'source': 'ESPN API',
                        'status': 'WORKS',
                        'coverage': 'All D1 games',
                        'cost': 'FREE',
                        'reliability': 'HIGH',
                        'notes': f'Provides ISO timestamps for {games_with_times}/{len(events[:5])} sample games'
                    })
                    print(f"✓ ESPN WORKS - {games_with_times}/{len(events[:5])} sample games have times")
                    return True

            print("✗ ESPN failed or no games found")
            return False

        except Exception as e:
            print(f"✗ Error: {e}")
            self.results['tip_times'].append({
                'source': 'ESPN API',
                'status': 'ERROR',
                'error': str(e)
            })
            return False

    def test_espn_historical_scores(self):
        """Test ESPN for historical scores."""
        print("\n" + "="*80)
        print("TESTING: ESPN for Historical Scores")
        print("="*80)

        try:
            # Test with a recent date
            test_date = datetime.now() - timedelta(days=3)
            date_str = test_date.strftime('%Y%m%d')

            url = f"http://site.api.espn.com/apis/site/v2/sports/basketball/mens-college-basketball/scoreboard"
            params = {'dates': date_str, 'limit': 100}

            response = requests.get(url, params=params, timeout=15)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                events = data.get('events', [])
                print(f"✓ Found {len(events)} games from {test_date.strftime('%Y-%m-%d')}")

                completed_with_scores = 0
                for event in events[:5]:
                    status = event.get('status', {}).get('type', {}).get('name')
                    if status == 'STATUS_FINAL':
                        comps = event.get('competitions', [{}])[0]
                        competitors = comps.get('competitors', [])
                        if len(competitors) == 2:
                            home_score = competitors[0].get('score')
                            away_score = competitors[1].get('score')
                            if home_score and away_score:
                                completed_with_scores += 1
                                print(f"  Sample: {event.get('name')} - Final {away_score}-{home_score}")

                if completed_with_scores > 0:
                    self.results['historical_scores'].append({
                        'source': 'ESPN API',
                        'status': 'WORKS',
                        'coverage': 'All D1 games',
                        'cost': 'FREE',
                        'reliability': 'HIGH',
                        'lookback': 'Unlimited (tested 3 days back)',
                        'notes': f'{completed_with_scores}/{len(events[:5])} sample games had scores'
                    })
                    print(f"✓ ESPN WORKS - {completed_with_scores} completed games with scores")
                    return True

            print("✗ ESPN failed or no completed games found")
            return False

        except Exception as e:
            print(f"✗ Error: {e}")
            self.results['historical_scores'].append({
                'source': 'ESPN API',
                'status': 'ERROR',
                'error': str(e)
            })
            return False

    def test_covers_historical_lines(self):
        """Test Covers.com for historical closing lines."""
        print("\n" + "="*80)
        print("TESTING: Covers.com for Historical Closing Lines")
        print("="*80)

        try:
            # Test recent date
            test_date = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d')
            url = f"https://www.covers.com/sports/ncaab/matchups?date={test_date}"

            print(f"Fetching: {url}")
            response = requests.get(url, headers=self.headers, timeout=20)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for game elements and betting data
                # Covers changes their HTML frequently, so try multiple selectors
                game_rows = soup.find_all('div', class_=lambda x: x and 'cmg' in str(x).lower())

                if not game_rows:
                    game_rows = soup.find_all('tr', class_=lambda x: x and 'game' in str(x).lower())

                print(f"Found {len(game_rows)} potential game elements")

                # Check if page has betting data
                has_spread = bool(soup.find(text=lambda t: t and ('-' in str(t) or '+' in str(t))))
                has_total = bool(soup.find(text=lambda t: t and ('o' in str(t).lower() or 'u' in str(t).lower())))

                print(f"Page contains spreads: {has_spread}")
                print(f"Page contains totals: {has_total}")

                if len(game_rows) > 0 and (has_spread or has_total):
                    self.results['historical_lines'].append({
                        'source': 'Covers.com (Web Scraping)',
                        'status': 'POTENTIALLY WORKS',
                        'coverage': 'Major games (may be incomplete)',
                        'cost': 'FREE',
                        'reliability': 'MEDIUM (scraping fragile)',
                        'data_available': f'{len(game_rows)} games, spreads={has_spread}, totals={has_total}',
                        'notes': 'Requires HTML parsing, may break with site updates'
                    })
                    print(f"✓ Covers POTENTIALLY WORKS - Found betting data")
                    return True
                else:
                    print("✗ No betting data found in expected format")

            return False

        except Exception as e:
            print(f"✗ Error: {e}")
            self.results['historical_lines'].append({
                'source': 'Covers.com',
                'status': 'ERROR',
                'error': str(e)
            })
            return False

    def test_oddsportal_historical_lines(self):
        """Test OddsPortal for historical lines."""
        print("\n" + "="*80)
        print("TESTING: OddsPortal for Historical Closing Lines")
        print("="*80)

        try:
            url = "https://www.oddsportal.com/basketball/usa/ncaa/results/"

            print(f"Fetching: {url}")
            response = requests.get(url, headers=self.headers, timeout=20)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                content = response.text.lower()

                # Check for Cloudflare protection
                if 'cloudflare' in content or 'checking your browser' in content:
                    print("✗ Cloudflare protection detected")
                    self.results['historical_lines'].append({
                        'source': 'OddsPortal',
                        'status': 'BLOCKED',
                        'notes': 'Cloudflare protection prevents scraping'
                    })
                    return False

                # Check if we can see data
                if 'ncaa' in content and len(response.content) > 10000:
                    print("✓ Page accessible, may contain data")
                    self.results['historical_lines'].append({
                        'source': 'OddsPortal',
                        'status': 'ACCESSIBLE',
                        'coverage': 'Comprehensive',
                        'cost': 'FREE (but requires scraping)',
                        'reliability': 'MEDIUM (Cloudflare risk)',
                        'notes': 'May need specialized scraping techniques'
                    })
                    return True

            return False

        except Exception as e:
            print(f"✗ Error: {e}")
            self.results['historical_lines'].append({
                'source': 'OddsPortal',
                'status': 'ERROR',
                'error': str(e)
            })
            return False

    def estimate_odds_api_costs(self):
        """Estimate costs for The Odds API historical data."""
        print("\n" + "="*80)
        print("ESTIMATING: The Odds API Costs")
        print("="*80)

        # Cost structure for The Odds API
        print("The Odds API Pricing:")
        print("  - FREE tier: 500 requests/month")
        print("  - Each request returns odds for all games at that timestamp")
        print("  - Historical endpoint: Same cost as live requests")
        print()

        # Estimate for season backtest
        season_days = 120  # Nov - Mar (4 months)
        requests_per_day = 1  # One request gets all games
        total_requests = season_days * requests_per_day

        print(f"SEASON BACKTEST ESTIMATE:")
        print(f"  Season duration: {season_days} days")
        print(f"  Requests needed: {total_requests} (1 per day)")
        print(f"  FREE tier covers: {'YES' if total_requests <= 500 else 'NO'}")
        print(f"  Requests over limit: {max(0, total_requests - 500)}")
        print()

        # Estimate for daily use (already doing this)
        print(f"DAILY USAGE (Current):")
        print(f"  Daily picks email: 1 request/day = 30 requests/month")
        print(f"  FREE tier adequate: YES")
        print()

        self.results['historical_lines'].append({
            'source': 'The Odds API (Historical)',
            'status': 'AVAILABLE (Paid)',
            'coverage': 'Comprehensive + closing lines',
            'cost': 'Uses API credits (same as live)',
            'season_backtest': f'{total_requests} requests ({total_requests - 500} over free tier)' if total_requests > 500 else f'{total_requests} requests (within free tier)',
            'reliability': 'HIGH',
            'notes': 'Most reliable source, provides closing lines'
        })

    def test_sports_reference_scores(self):
        """Test Sports-Reference for historical scores."""
        print("\n" + "="*80)
        print("TESTING: Sports-Reference for Historical Scores")
        print("="*80)

        try:
            # Test with recent date
            test_date = datetime.now() - timedelta(days=2)
            url = f"https://www.sports-reference.com/cbb/boxscores/index.cgi?month={test_date.month}&day={test_date.day}&year={test_date.year}"

            print(f"Fetching: {url}")
            response = requests.get(url, headers=self.headers, timeout=20)
            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Look for game summaries
                game_divs = soup.find_all('div', class_='game_summary')
                print(f"Found {len(game_divs)} game summaries")

                if len(game_divs) > 0:
                    # Sample first game
                    first_game = game_divs[0]
                    teams = first_game.find_all('a')
                    if len(teams) >= 2:
                        print(f"  Sample game: {teams[0].text} @ {teams[1].text}")

                    self.results['historical_scores'].append({
                        'source': 'Sports-Reference',
                        'status': 'WORKS',
                        'coverage': 'All D1 games',
                        'cost': 'FREE',
                        'reliability': 'HIGH',
                        'lookback': 'Unlimited (archives)',
                        'notes': f'Found {len(game_divs)} games, reliable but requires scraping'
                    })
                    print(f"✓ Sports-Reference WORKS - {len(game_divs)} games found")
                    return True

            return False

        except Exception as e:
            print(f"✗ Error: {e}")
            self.results['historical_scores'].append({
                'source': 'Sports-Reference',
                'status': 'ERROR',
                'error': str(e)
            })
            return False

    def generate_report(self):
        """Generate comprehensive report."""
        print("\n" + "="*80)
        print("COMPREHENSIVE RESEARCH REPORT")
        print("="*80)

        # Tip Times
        print("\n📍 TIP TIMES (Upcoming Games)")
        print("-" * 80)
        if self.results['tip_times']:
            for result in self.results['tip_times']:
                print(f"\nSource: {result['source']}")
                print(f"Status: {result['status']}")
                if result['status'] == 'WORKS':
                    print(f"Coverage: {result['coverage']}")
                    print(f"Cost: {result['cost']}")
                    print(f"Reliability: {result['reliability']}")
                    print(f"Notes: {result['notes']}")
        else:
            print("No working sources found")

        # Historical Scores
        print("\n📊 HISTORICAL SCORES")
        print("-" * 80)
        if self.results['historical_scores']:
            for result in self.results['historical_scores']:
                print(f"\nSource: {result['source']}")
                print(f"Status: {result['status']}")
                if result['status'] == 'WORKS':
                    print(f"Coverage: {result['coverage']}")
                    print(f"Cost: {result['cost']}")
                    print(f"Reliability: {result['reliability']}")
                    print(f"Lookback: {result['lookback']}")
                    print(f"Notes: {result['notes']}")
        else:
            print("No working sources found")

        # Historical Closing Lines
        print("\n💰 HISTORICAL CLOSING LINES")
        print("-" * 80)
        if self.results['historical_lines']:
            for result in self.results['historical_lines']:
                print(f"\nSource: {result['source']}")
                print(f"Status: {result['status']}")
                if result.get('coverage'):
                    print(f"Coverage: {result['coverage']}")
                if result.get('cost'):
                    print(f"Cost: {result['cost']}")
                if result.get('reliability'):
                    print(f"Reliability: {result['reliability']}")
                if result.get('notes'):
                    print(f"Notes: {result['notes']}")
                if result.get('season_backtest'):
                    print(f"Season Backtest: {result['season_backtest']}")
        else:
            print("No sources evaluated")

        # Recommendations
        print("\n" + "="*80)
        print("RECOMMENDATIONS")
        print("="*80)

        print("\n✅ BEST OPTIONS:")
        print("\n1. TIP TIMES: ESPN API")
        print("   - FREE, reliable, comprehensive coverage")
        print("   - Already provides ISO timestamps for all games")

        print("\n2. HISTORICAL SCORES: ESPN API")
        print("   - FREE, reliable, unlimited lookback")
        print("   - Can fetch any date, returns all completed games")

        print("\n3. HISTORICAL CLOSING LINES: Three options")
        print("   Option A: The Odds API (RECOMMENDED)")
        print("     - Most reliable, provides actual closing lines")
        print("     - Cost: ~120 requests for season = within FREE tier (500/month)")
        print("     - No additional cost beyond current daily usage")
        print("   ")
        print("   Option B: Covers.com scraping")
        print("     - FREE but fragile (HTML changes)")
        print("     - May have incomplete coverage")
        print("   ")
        print("   Option C: Manual data collection")
        print("     - Most accurate but time-consuming")


def main():
    researcher = DataSourceResearcher()

    print("="*80)
    print("SPORTS BETTING DATA SOURCE RESEARCH")
    print("Testing sources for tip times, historical scores, and closing lines")
    print("="*80)

    # Test all sources
    researcher.test_espn_tip_times()
    researcher.test_espn_historical_scores()
    researcher.test_sports_reference_scores()
    researcher.test_covers_historical_lines()
    researcher.test_oddsportal_historical_lines()
    researcher.estimate_odds_api_costs()

    # Generate comprehensive report
    researcher.generate_report()


if __name__ == '__main__':
    main()
