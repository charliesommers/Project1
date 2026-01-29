#!/usr/bin/env python3
"""
Backtest Greg's 2025 MLB season performance.

Analyzes:
1. Moneyline picks record
2. Totals picks record
3. Profit/Loss at actual odds

Requires:
- Greg's historical MLB totals from Google Sheets
- Historical MLB scores (ESPN API)
- Historical closing odds (The Odds API)
"""

import os
import sys
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from gregs_mlb_parser import GregsMLBParser


GOOGLE_SHEETS_ID = "1QvkPvE8CtGabeYphECyMY2zYilPBkbOBeEL6mEwJTLs"
GOOGLE_SHEETS_URL = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEETS_ID}/export?format=xlsx"


def download_gregs_sheet(output_path="data/gregs_mlb_backtest.xlsx"):
    """Download Greg's MLB sheet."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        response = requests.get(GOOGLE_SHEETS_URL, timeout=30)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return output_path
    except Exception as e:
        print(f"Error downloading sheet: {e}")
        return None


def fetch_mlb_scores_espn(date: datetime) -> List[Dict]:
    """Fetch completed MLB games with scores from ESPN."""
    date_str = date.strftime('%Y%m%d')
    url = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/scoreboard"
    params = {'dates': date_str, 'limit': 100}

    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()

        games = []
        for event in data.get('events', []):
            status = event.get('status', {}).get('type', {}).get('name')
            if status != 'STATUS_FINAL':
                continue

            comps = event.get('competitions', [{}])[0]
            competitors = comps.get('competitors', [])

            if len(competitors) != 2:
                continue

            home_team = None
            away_team = None
            home_score = None
            away_score = None

            for comp in competitors:
                team_name = comp.get('team', {}).get('displayName', '')
                score = int(comp.get('score', 0))

                if comp.get('homeAway') == 'home':
                    home_team = team_name
                    home_score = score
                else:
                    away_team = team_name
                    away_score = score

            if all([home_team, away_team, home_score is not None, away_score is not None]):
                games.append({
                    'date': date,
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_score': home_score,
                    'away_score': away_score,
                    'total': home_score + away_score
                })

        return games

    except Exception as e:
        print(f"Error fetching scores for {date_str}: {e}")
        return []


def fetch_historical_odds_api(date: datetime, api_key: str) -> List[Dict]:
    """
    Fetch historical closing odds from The Odds API.

    Note: This uses API credits. Estimate: ~180 days × 1 request = 180 credits
    (within 500/month free tier if done over multiple months)
    """
    # The Odds API historical endpoint
    date_str = date.strftime('%Y-%m-%dT12:00:00Z')  # Noon UTC (closing lines)

    url = f"https://api.the-odds-api.com/v4/historical/sports/baseball_mlb/odds"
    params = {
        'apiKey': api_key,
        'regions': 'us',
        'markets': 'h2h,totals',
        'oddsFormat': 'american',
        'date': date_str
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching odds for {date_str}: {e}")
        return []


def backtest_season(start_date: datetime, end_date: datetime, use_api: bool = False):
    """Backtest Greg's MLB season."""

    print("⚾ GREG'S 2025 MLB SEASON BACKTEST")
    print("=" * 80)
    print(f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print("=" * 80)
    print()

    # Download Greg's sheet
    print("📊 Downloading Greg's historical MLB totals...")
    file_path = download_gregs_sheet()
    if not file_path:
        print("❌ Could not download Greg's data")
        return

    # Parse
    parser = GregsMLBParser(file_path)
    parser.load_file()
    games = parser.parse_all_sheets()

    if not games:
        print("❌ No games found in Greg's sheet")
        return

    print(f"✓ Found {len(games)} total games in Greg's sheet")

    # Filter to date range
    games_in_range = [
        g for g in games
        if start_date.date() <= g['date'].date() <= end_date.date()
    ]
    print(f"✓ {len(games_in_range)} games in specified date range")
    print()

    # Fetch historical scores
    print("📈 Fetching historical MLB scores from ESPN...")
    all_scores = []
    current_date = start_date

    while current_date <= end_date:
        print(f"  Fetching {current_date.strftime('%m/%d/%Y')}...", end='')
        scores = fetch_mlb_scores_espn(current_date)
        all_scores.extend(scores)
        print(f" {len(scores)} games")
        current_date += timedelta(days=1)

    print(f"✓ Found {len(all_scores)} completed games with scores")
    print()

    if use_api:
        print("💰 Fetching historical closing odds from The Odds API...")
        api_key = os.getenv('ODDS_API_KEY')
        if not api_key:
            print("❌ ODDS_API_KEY not set. Cannot fetch historical odds.")
            print("   Continuing with scores-only analysis...")
            use_api = False
        else:
            # Calculate API cost
            days_in_range = (end_date - start_date).days + 1
            print(f"   Estimated API requests needed: {days_in_range}")
            print(f"   FREE tier: 500 requests/month")
            if days_in_range > 500:
                print(f"   ⚠️  This will use {days_in_range - 500} requests over free tier")

            response = input(f"\n   Proceed with fetching odds? (y/n): ")
            if response.lower() != 'y':
                print("   Skipping odds fetch. Continuing with scores-only analysis...")
                use_api = False

    # Match games
    print("🔗 Matching games...")
    matches = []

    for gregs_game in games_in_range:
        for score_game in all_scores:
            # Simple team matching
            if (gregs_game['away_team'].lower() in score_game['away_team'].lower() or
                score_game['away_team'].lower() in gregs_game['away_team'].lower()) and \
               (gregs_game['home_team'].lower() in score_game['home_team'].lower() or
                score_game['home_team'].lower() in gregs_game['home_team'].lower()):

                matches.append({
                    'gregs_game': gregs_game,
                    'score_game': score_game,
                    'gregs_total': gregs_game['total'],
                    'actual_total': score_game['total'],
                    'matchup': gregs_game['matchup'],
                    'date': gregs_game['date']
                })
                break

    print(f"✓ Matched {len(matches)}/{len(games_in_range)} games")
    print()

    if len(matches) == 0:
        print("❌ No games matched - cannot run backtest")
        return

    # Analyze totals performance
    print("🎯 TOTALS ANALYSIS")
    print("=" * 80)
    print()

    # Calculate picks using flame methodology
    under_threshold = 5.0
    over_threshold = 3.0

    totals_picks = []

    for match in matches:
        gregs_total = match['gregs_total']
        actual_total = match['actual_total']
        difference = gregs_total - actual_total

        pick = None
        if difference <= -under_threshold:
            pick = 'UNDER'
            # Hypothetical: bet UNDER at Greg's total
            wins = actual_total < gregs_total
        elif difference >= over_threshold:
            pick = 'OVER'
            # Hypothetical: bet OVER at Greg's total
            wins = actual_total > gregs_total

        if pick:
            totals_picks.append({
                **match,
                'pick': pick,
                'wins': wins,
                'edge': abs(difference)
            })

    if totals_picks:
        total_wins = sum(1 for p in totals_picks if p['wins'])
        total_losses = len(totals_picks) - total_wins
        win_pct = (total_wins / len(totals_picks)) * 100

        # At -110 odds
        profit = total_wins * 100 - total_losses * 110
        roi = (profit / (len(totals_picks) * 110)) * 100

        print(f"Total Picks (Flame methodology): {len(totals_picks)}")
        print(f"Record: {total_wins}-{total_losses} ({win_pct:.1f}%)")
        print(f"Profit/Loss: ${profit:+.2f} (at -110 odds)")
        print(f"ROI: {roi:+.2f}%")
        print(f"Breakeven: 52.4%")
        print()

        # Breakdown
        under_picks = [p for p in totals_picks if p['pick'] == 'UNDER']
        over_picks = [p for p in totals_picks if p['pick'] == 'OVER']

        if under_picks:
            u_wins = sum(1 for p in under_picks if p['wins'])
            u_losses = len(under_picks) - u_wins
            print(f"UNDER picks: {u_wins}-{u_losses} ({(u_wins/len(under_picks)*100):.1f}%)")

        if over_picks:
            o_wins = sum(1 for p in over_picks if p['wins'])
            o_losses = len(over_picks) - o_wins
            print(f"OVER picks: {o_wins}-{o_losses} ({(o_wins/len(over_picks)*100):.1f}%)")

    else:
        print("No flame picks met thresholds in this date range")

    print()
    print("=" * 80)
    print("NOTE: This analysis uses Greg's totals as betting lines.")
    print("For accurate P/L, need historical closing odds from sportsbooks.")
    print("API cost estimate: ~180 requests for full season (within free tier)")
    print("=" * 80)


if __name__ == '__main__':
    # Default: 2025 MLB season (April - October)
    season_start = datetime(2025, 4, 1)
    season_end = datetime(2025, 10, 31)

    if len(sys.argv) > 1:
        season_start = datetime.strptime(sys.argv[1], '%Y-%m-%d')
        if len(sys.argv) > 2:
            season_end = datetime.strptime(sys.argv[2], '%Y-%m-%d')

    backtest_season(season_start, season_end, use_api=False)
