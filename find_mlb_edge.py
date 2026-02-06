#!/usr/bin/env python3
"""
Find Greg's MLB betting edge by testing different strategies and thresholds.

Tests:
1. Totals (OVER/UNDER) at various thresholds
2. Moneyline picks based on run line predictions
3. Combinations of both

Goal: Find optimal betting thresholds that maximize ROI
"""

import os
import sys
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from gregs_mlb_parser import GregsMLBParser
import itertools


GOOGLE_SHEETS_ID = "1QvkPvE8CtGabeYphECyMY2zYilPBkbOBeEL6mEwJTLs"
GOOGLE_SHEETS_URL = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEETS_ID}/export?format=xlsx"


def download_gregs_sheet(output_path="data/gregs_mlb_edge.xlsx"):
    """Download Greg's MLB sheet."""
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        response = requests.get(GOOGLE_SHEETS_URL, timeout=30)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
        return output_path
    except Exception as e:
        print(f"Error: {e}")
        return None


def fetch_espn_scores(date: datetime) -> List[Dict]:
    """Fetch MLB scores from ESPN."""
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

            home_team, away_team, home_score, away_score = None, None, None, None
            for comp in competitors:
                team_name = comp.get('team', {}).get('displayName', '')
                score = int(comp.get('score', 0))
                if comp.get('homeAway') == 'home':
                    home_team, home_score = team_name, score
                else:
                    away_team, away_score = team_name, score

            if all([home_team, away_team, home_score is not None, away_score is not None]):
                games.append({
                    'home_team': home_team,
                    'away_team': away_team,
                    'home_score': home_score,
                    'away_score': away_score,
                    'total': home_score + away_score,
                    'home_won': home_score > away_score
                })

        return games
    except:
        return []


def match_teams(team1: str, team2: str) -> bool:
    """Check if MLB team names match using the MLB team mapper."""
    from mlb_team_mapper import match_mlb_teams
    return match_mlb_teams(team1, team2)


def calculate_roi(wins: int, losses: int) -> Tuple[float, float]:
    """Calculate profit and ROI at -110 odds."""
    if wins + losses == 0:
        return 0.0, 0.0
    profit = wins * 100 - losses * 110
    total_risked = (wins + losses) * 110
    roi = (profit / total_risked) * 100
    return profit, roi


def test_totals_strategy(matches: List[Dict], under_threshold: float, over_threshold: float) -> Dict:
    """Test totals picks at given thresholds."""
    picks = []

    for match in matches:
        gregs_total = match['gregs_total']
        actual_total = match['actual_total']
        diff = gregs_total - actual_total

        if diff <= -under_threshold:
            # Bet UNDER at implied line (actual total)
            wins = actual_total < gregs_total
            picks.append({'pick': 'UNDER', 'wins': wins, 'edge': abs(diff)})
        elif diff >= over_threshold:
            # Bet OVER at implied line (actual total)
            wins = actual_total > gregs_total
            picks.append({'pick': 'OVER', 'wins': wins, 'edge': abs(diff)})

    if not picks:
        return None

    total_wins = sum(1 for p in picks if p['wins'])
    total_losses = len(picks) - total_wins
    profit, roi = calculate_roi(total_wins, total_losses)
    win_pct = (total_wins / len(picks)) * 100

    return {
        'strategy': 'TOTALS',
        'under_threshold': under_threshold,
        'over_threshold': over_threshold,
        'picks': len(picks),
        'wins': total_wins,
        'losses': total_losses,
        'win_pct': win_pct,
        'profit': profit,
        'roi': roi
    }


def test_moneyline_strategy(matches: List[Dict], run_line_threshold: float) -> Dict:
    """
    Test moneyline picks based on Greg's run line predictions.

    Theory: If Greg's run line is significantly different from implied (0),
    his favorite/underdog picks might have value.
    """
    picks = []

    for match in matches:
        gregs_run_line = match.get('gregs_run_line', 0)
        home_won = match['home_won']

        # Determine Greg's favorite
        if 'favorite' in match:
            gregs_favorite = match['favorite']
            gregs_underdog = match['underdog']
        else:
            continue

        # Check if Greg's conviction (abs run line) is strong enough
        if abs(gregs_run_line) >= run_line_threshold:
            # Bet Greg's favorite on moneyline
            # Win if favorite won the game
            away_team = match['gregs_game']['away_team']
            home_team = match['gregs_game']['home_team']

            greg_pick_won = (gregs_favorite == home_team and home_won) or \
                           (gregs_favorite == away_team and not home_won)

            picks.append({
                'pick': f'ML {gregs_favorite}',
                'wins': greg_pick_won,
                'run_line': abs(gregs_run_line)
            })

    if not picks:
        return None

    total_wins = sum(1 for p in picks if p['wins'])
    total_losses = len(picks) - total_wins
    profit, roi = calculate_roi(total_wins, total_losses)
    win_pct = (total_wins / len(picks)) * 100

    return {
        'strategy': 'MONEYLINE',
        'run_line_threshold': run_line_threshold,
        'picks': len(picks),
        'wins': total_wins,
        'losses': total_losses,
        'win_pct': win_pct,
        'profit': profit,
        'roi': roi
    }


def find_edge(start_date: datetime, end_date: datetime):
    """Find optimal betting thresholds."""

    print("⚾ FINDING GREG'S MLB EDGE")
    print("=" * 80)
    print(f"Testing period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print("=" * 80)
    print()

    # Load data
    print("📊 Loading Greg's data...")
    file_path = download_gregs_sheet()
    if not file_path:
        return

    parser = GregsMLBParser(file_path)
    parser.load_file()
    games = parser.parse_all_sheets()

    games_in_range = [g for g in games if start_date.date() <= g['date'].date() <= end_date.date()]
    print(f"✓ {len(games_in_range)} games from Greg")

    # Fetch scores
    print("\n📈 Fetching historical scores...")
    all_scores = []
    current_date = start_date

    while current_date <= end_date:
        scores = fetch_espn_scores(current_date)
        all_scores.extend(scores)
        if len(all_scores) % 50 == 0:
            print(f"  Progress: {len(all_scores)} games fetched...")
        current_date += timedelta(days=1)

    print(f"✓ {len(all_scores)} completed games with scores")

    # Match games
    print("\n🔗 Matching games...")

    # DEBUG: Show sample team names
    print("\nDEBUG - Sample Greg's team names:")
    for i, game in enumerate(games_in_range[:5]):
        print(f"  {i+1}. Away: '{game['away_team']}' | Home: '{game['home_team']}'")

    print("\nDEBUG - Sample ESPN team names:")
    for i, game in enumerate(all_scores[:5]):
        print(f"  {i+1}. Away: '{game['away_team']}' | Home: '{game['home_team']}'")
    print()

    matches = []
    unmatched_count = 0

    for gregs_game in games_in_range:
        matched = False
        for score_game in all_scores:
            if match_teams(gregs_game['away_team'], score_game['away_team']) and \
               match_teams(gregs_game['home_team'], score_game['home_team']):
                matches.append({
                    'gregs_game': gregs_game,
                    'score_game': score_game,
                    'gregs_total': gregs_game['total'],
                    'gregs_run_line': gregs_game.get('run_line', 0),
                    'actual_total': score_game['total'],
                    'home_won': score_game['home_won'],
                    'favorite': gregs_game.get('favorite'),
                    'underdog': gregs_game.get('underdog')
                })
                matched = True
                break

        if not matched:
            unmatched_count += 1
            if unmatched_count <= 5:  # Show first 5 unmatched
                print(f"  ✗ No match: {gregs_game['away_team']} @ {gregs_game['home_team']}")

    print(f"\n✓ Matched {len(matches)} games")
    print(f"✗ Unmatched {unmatched_count} games")
    print()

    if len(matches) < 10:
        print("❌ Not enough matched games for meaningful analysis")
        return

    # Test strategies
    print("🎯 TESTING STRATEGIES")
    print("=" * 80)
    print()

    results = []

    # Test totals at various thresholds (decimal increments for MLB)
    print("Testing TOTALS strategies...")
    under_thresholds = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]
    over_thresholds = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0]

    for under_t, over_t in itertools.product(under_thresholds, over_thresholds):
        result = test_totals_strategy(matches, under_t, over_t)
        if result:
            results.append(result)
            print(f"  UNDER≥{under_t}, OVER≥{over_t}: {result['wins']}-{result['losses']} "
                  f"({result['win_pct']:.1f}%) ROI: {result['roi']:+.1f}%")

    # Test moneyline at various thresholds
    print("\nTesting MONEYLINE strategies...")
    run_line_thresholds = [1.0, 1.5, 2.0, 2.5, 3.0]

    for threshold in run_line_thresholds:
        result = test_moneyline_strategy(matches, threshold)
        if result:
            results.append(result)
            print(f"  RunLine≥{threshold}: {result['wins']}-{result['losses']} "
                  f"({result['win_pct']:.1f}%) ROI: {result['roi']:+.1f}%")

    # Find best strategies
    print("\n" + "=" * 80)
    print("🏆 TOP 10 STRATEGIES BY ROI")
    print("=" * 80)
    print()

    results.sort(key=lambda x: x['roi'], reverse=True)

    for i, result in enumerate(results[:10], 1):
        if result['strategy'] == 'TOTALS':
            strategy_desc = f"TOTALS (UNDER≥{result['under_threshold']}, OVER≥{result['over_threshold']})"
        else:
            strategy_desc = f"MONEYLINE (RunLine≥{result['run_line_threshold']})"

        print(f"{i}. {strategy_desc}")
        print(f"   Record: {result['wins']}-{result['losses']} ({result['win_pct']:.1f}%)")
        print(f"   Picks: {result['picks']} games")
        print(f"   Profit: ${result['profit']:+.2f}")
        print(f"   ROI: {result['roi']:+.2f}%")
        print()

    # Recommendations
    print("=" * 80)
    print("💡 RECOMMENDATIONS")
    print("=" * 80)
    print()

    best_result = results[0] if results else None
    if best_result:
        if best_result['strategy'] == 'TOTALS':
            print(f"✅ Best Strategy: TOTALS")
            print(f"   UNDER when Greg ≥{best_result['under_threshold']} below")
            print(f"   OVER when Greg ≥{best_result['over_threshold']} above")
        else:
            print(f"✅ Best Strategy: MONEYLINE")
            print(f"   Bet favorite when run line ≥{best_result['run_line_threshold']}")

        print(f"\n   Expected Results:")
        print(f"   Win Rate: {best_result['win_pct']:.1f}%")
        print(f"   ROI: {best_result['roi']:+.1f}%")
        print(f"   Based on {result['picks']} picks over test period")

    # Sample size warning
    print(f"\n⚠️  Note: Results based on {len(matches)} matched games")
    if len(matches) < 100:
        print("   Small sample size - results may not be statistically significant")


if __name__ == '__main__':
    # Default: 2025 season so far
    season_start = datetime(2025, 3, 1)  # Spring training / early season
    season_end = datetime.now()

    if len(sys.argv) > 1:
        season_start = datetime.strptime(sys.argv[1], '%Y-%m-%d')
        if len(sys.argv) > 2:
            season_end = datetime.strptime(sys.argv[2], '%Y-%m-%d')

    find_edge(season_start, season_end)
