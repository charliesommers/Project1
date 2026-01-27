#!/usr/bin/env python3
"""
Analyze Greg Peterson's prediction accuracy against actual game results.

This script analyzes how accurate Greg's totals predictions have been:
- Mean absolute error (average difference between Greg's total and actual)
- Distribution of prediction errors
- How often Greg is significantly different from actual (potential edge indicators)
- Directional accuracy (does Greg predict higher/lower than actual)

Note: This is NOT a backtest of betting results since we don't have historical sportsbook lines.
This simply measures prediction accuracy to understand Greg's handicapping performance.
"""

import os
import sys
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional
from gregs_cbb_parser import GregsCBBParser
from scores_fetcher import ScoresFetcher

# Try to import historical odds scraper (optional)
try:
    from historical_odds_scraper import HistoricalOddsScraper
    HAS_HISTORICAL_ODDS = True
except ImportError:
    HAS_HISTORICAL_ODDS = False


# Greg's Google Sheets ID (from VSIN website)
GOOGLE_SHEETS_ID = "1RoqluBp1zE5HduO-QNb5pKIQen98pnIEUZz7CERsPgU"
GOOGLE_SHEETS_URL = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEETS_ID}/export?format=xlsx"


def download_gregs_sheet(output_path="data/gregs_lines_backtest.xlsx"):
    """
    Download Greg's Google Sheet directly.

    Args:
        output_path: Where to save the downloaded file

    Returns:
        Path to downloaded file or None if failed
    """
    try:
        # Create data directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Download the file
        response = requests.get(GOOGLE_SHEETS_URL, timeout=30)
        response.raise_for_status()

        # Save to file
        with open(output_path, 'wb') as f:
            f.write(response.content)

        return output_path

    except Exception as e:
        print(f"Error downloading Google Sheet: {e}")
        return None


def calculate_accuracy_metrics(matches: List[Dict]) -> Dict:
    """
    Calculate prediction accuracy metrics.

    Args:
        matches: List of matched games with Greg's totals and actual totals

    Returns:
        Dictionary with accuracy metrics
    """
    errors = [m['gregs_total'] - m['actual_total'] for m in matches]
    abs_errors = [abs(e) for e in errors]

    return {
        'count': len(matches),
        'mean_error': sum(errors) / len(errors) if errors else 0,
        'mean_absolute_error': sum(abs_errors) / len(abs_errors) if abs_errors else 0,
        'min_error': min(errors) if errors else 0,
        'max_error': max(errors) if errors else 0,
        'std_dev': (sum((e - sum(errors)/len(errors))**2 for e in errors) / len(errors))**0.5 if len(errors) > 1 else 0
    }


def backtest_season(start_date: datetime, end_date: datetime, try_historical_odds: bool = True):
    """
    Analyze Greg's picks for a date range.

    If historical odds are available, calculates actual betting results.
    Otherwise, shows prediction accuracy analysis.

    Args:
        start_date: Start date for analysis
        end_date: End date for analysis
        try_historical_odds: Whether to attempt fetching historical odds (free scraping)
    """

    # Check if we can get historical odds
    use_odds = try_historical_odds and HAS_HISTORICAL_ODDS

    if use_odds:
        print("🏀 GREG'S CBB PICKS BACKTEST (With Historical Odds)")
    else:
        print("🏀 GREG'S CBB TOTALS ACCURACY ANALYSIS")

    print("=" * 80)
    print(f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")

    if use_odds:
        print(f"Mode: Backtesting with actual betting lines (scraped from Covers.com)")
    else:
        print(f"Mode: Prediction accuracy vs actual game totals")

    print("=" * 80)
    print()

    # Download Greg's current sheet (has historical data)
    print("📊 Downloading Greg's totals from Google Sheets...")
    file_path = download_gregs_sheet()
    if not file_path:
        print("❌ Could not download Greg's data")
        return

    # Parse Greg's sheet
    parser = GregsCBBParser(file_path)
    parser.load_file()
    games = parser.parse_all_sheets()

    if not games:
        print("❌ No games found in Greg's sheet")
        return

    print(f"✓ Found {len(games)} total games in Greg's sheet")

    # Filter games to date range
    games_in_range = [
        g for g in games
        if start_date.date() <= g['date'].date() <= end_date.date()
    ]
    print(f"✓ {len(games_in_range)} games in specified date range")
    print()

    # Fetch completed games with scores from ESPN
    print("🏈 Fetching completed game scores from ESPN...")
    fetcher = ScoresFetcher()

    all_completed_games = fetcher.fetch_scores_range(start_date, end_date)

    print(f"✓ Found {len(all_completed_games)} completed games with scores")
    print()

    # Match Greg's games to completed games
    print("🔗 Matching games...")
    print(f"  Processing {len(games_in_range)} games from Greg's sheet...")
    matches = []

    for i, gregs_game in enumerate(games_in_range):
        if (i + 1) % 100 == 0:
            print(f"  Progress: {i+1}/{len(games_in_range)} games processed...")

        try:
            completed_game = fetcher.match_game(gregs_game, all_completed_games)
            if completed_game:
                matches.append({
                    'gregs_game': gregs_game,
                    'completed_game': completed_game,
                    'gregs_total': gregs_game['total'],
                    'actual_total': completed_game['total'],
                    'matchup': gregs_game['matchup'],
                    'date': gregs_game['date']
                })
        except Exception as e:
            print(f"  ⚠️  Error matching game {i+1}: {gregs_game.get('matchup', 'unknown')}")
            print(f"     Error: {e}")
            import traceback
            traceback.print_exc()
            continue

    print(f"✓ Matched {len(matches)}/{len(games_in_range)} games")
    print()

    if len(matches) == 0:
        print("❌ No games matched - cannot run analysis")
        return

    # Try to fetch historical odds if enabled
    historical_odds = {}
    if use_odds:
        print("📈 Fetching historical betting lines from Covers.com...")
        try:
            scraper = HistoricalOddsScraper()
            historical_odds = scraper.fetch_odds_range(start_date, end_date)
            total_games_with_odds = sum(len(games) for games in historical_odds.values())
            print(f"✓ Found betting lines for {total_games_with_odds} games across {len(historical_odds)} dates")

            if total_games_with_odds == 0:
                print("⚠️  No historical odds found - falling back to accuracy analysis")
                use_odds = False

        except Exception as e:
            print(f"⚠️  Could not fetch historical odds: {e}")
            print("   Falling back to accuracy analysis")
            use_odds = False

        print()

    # Match games with historical odds if available
    if use_odds:
        # Run betting backtest
        run_betting_backtest(matches, historical_odds)
    else:
        # Run accuracy analysis
        run_accuracy_analysis(matches)


def run_betting_backtest(matches: List[Dict], historical_odds: Dict[str, List[Dict]]):
    """Run backtest using actual historical betting lines."""

    print("🔥 FLAME EMOJI PICKS BACKTEST")
    print("=" * 80)
    print()

    # Match each game with its historical odds
    picks = []

    for match in matches:
        date_str = match['date'].strftime('%Y-%m-%d')
        if date_str not in historical_odds:
            continue

        # Find matching odds for this game
        for odds_game in historical_odds[date_str]:
            # Try to match teams
            if (match['gregs_game']['favorite'].lower() in odds_game.get('matchup', '').lower() or
                match['gregs_game']['underdog'].lower() in odds_game.get('matchup', '').lower()):

                total_line = odds_game.get('total')
                if not total_line:
                    continue

                gregs_total = match['gregs_total']
                actual_total = match['actual_total']
                diff = gregs_total - total_line

                # Apply flame emoji methodology
                # UNDER: Greg ≥5 below sportsbook
                if diff <= -5.0:
                    pick_wins = actual_total < total_line
                    picks.append({
                        **match,
                        'pick': 'UNDER',
                        'sportsbook_total': total_line,
                        'edge': diff,
                        'wins': pick_wins
                    })

                # OVER: Greg ≥3 above sportsbook
                elif diff >= 3.0:
                    pick_wins = actual_total > total_line
                    picks.append({
                        **match,
                        'pick': 'OVER',
                        'sportsbook_total': total_line,
                        'edge': diff,
                        'wins': pick_wins
                    })

                break  # Found match, move to next game

    if not picks:
        print("❌ No flame emoji picks found in this date range")
        return

    # Calculate results
    wins = sum(1 for p in picks if p['wins'])
    losses = len(picks) - wins
    win_pct = (wins / len(picks)) * 100

    # At -110 odds
    profit_per_win = 100
    loss_per_loss = 110
    total_profit = wins * profit_per_win - losses * loss_per_loss
    total_risked = len(picks) * 110
    roi = (total_profit / total_risked) * 100 if total_risked > 0 else 0

    print(f"📊 OVERALL RESULTS")
    print(f"Total Picks: {len(picks)}")
    print(f"Record: {wins}-{losses} ({win_pct:.1f}%)")
    print(f"Profit/Loss: ${total_profit:+.2f} (risking $110 per game)")
    print(f"ROI: {roi:+.2f}%")
    print(f"Breakeven: 52.4% win rate needed at -110 odds")
    print()

    # Breakdown by pick type
    under_picks = [p for p in picks if p['pick'] == 'UNDER']
    over_picks = [p for p in picks if p['pick'] == 'OVER']

    if under_picks:
        u_wins = sum(1 for p in under_picks if p['wins'])
        u_losses = len(under_picks) - u_wins
        u_pct = (u_wins / len(under_picks)) * 100
        u_profit = u_wins * 100 - u_losses * 110
        u_roi = (u_profit / (len(under_picks) * 110)) * 100 if under_picks else 0

        print(f"🔵 UNDER PICKS (Greg ≥5 below sportsbook)")
        print(f"Count: {len(under_picks)}")
        print(f"Record: {u_wins}-{u_losses} ({u_pct:.1f}%)")
        print(f"P/L: ${u_profit:+.2f} | ROI: {u_roi:+.2f}%")
        print()

    if over_picks:
        o_wins = sum(1 for p in over_picks if p['wins'])
        o_losses = len(over_picks) - o_wins
        o_pct = (o_wins / len(over_picks)) * 100
        o_profit = o_wins * 100 - o_losses * 110
        o_roi = (o_profit / (len(over_picks) * 110)) * 100 if over_picks else 0

        print(f"🔴 OVER PICKS (Greg ≥3 above sportsbook)")
        print(f"Count: {len(over_picks)}")
        print(f"Record: {o_wins}-{o_losses} ({o_pct:.1f}%)")
        print(f"P/L: ${o_profit:+.2f} | ROI: {o_roi:+.2f}%")
        print()

    # Sample picks
    print("📋 SAMPLE PICKS (first 10)")
    print("=" * 80)
    for i, pick in enumerate(picks[:10], 1):
        result = "✓ WIN" if pick['wins'] else "✗ LOSS"
        print(f"{i}. {pick['matchup']} - {pick['date'].strftime('%m/%d')}")
        print(f"   Greg: {pick['gregs_total']:.1f} | Line: {pick['sportsbook_total']:.1f} | Actual: {pick['actual_total']}")
        print(f"   {pick['pick']} {pick['sportsbook_total']:.1f} | Edge: {pick['edge']:+.1f} | {result}")
        print()


def run_accuracy_analysis(matches: List[Dict]):
    """Run prediction accuracy analysis (no historical odds)."""

    # Calculate overall accuracy metrics
    print("📊 OVERALL ACCURACY")
    print("=" * 80)

    metrics = calculate_accuracy_metrics(matches)

    print(f"Total Games Analyzed: {metrics['count']}")
    print(f"Mean Absolute Error: {metrics['mean_absolute_error']:.2f} points")
    print(f"Mean Error (Bias): {metrics['mean_error']:+.2f} points")
    print(f"  → {'Greg predicts HIGHER' if metrics['mean_error'] > 0 else 'Greg predicts LOWER'} on average")
    print(f"Standard Deviation: {metrics['std_dev']:.2f} points")
    print(f"Largest Overestimate: {metrics['max_error']:+.2f} points")
    print(f"Largest Underestimate: {metrics['min_error']:+.2f} points")
    print()

    # Categorize predictions by accuracy
    print("📈 PREDICTION DISTRIBUTION")
    print("=" * 80)

    very_close = [m for m in matches if abs(m['gregs_total'] - m['actual_total']) <= 2]
    close = [m for m in matches if 2 < abs(m['gregs_total'] - m['actual_total']) <= 5]
    moderate = [m for m in matches if 5 < abs(m['gregs_total'] - m['actual_total']) <= 10]
    large = [m for m in matches if abs(m['gregs_total'] - m['actual_total']) > 10]

    print(f"Very Close (±2 pts):  {len(very_close):4d} ({len(very_close)/len(matches)*100:5.1f}%)")
    print(f"Close (2-5 pts):      {len(close):4d} ({len(close)/len(matches)*100:5.1f}%)")
    print(f"Moderate (5-10 pts):  {len(moderate):4d} ({len(moderate)/len(matches)*100:5.1f}%)")
    print(f"Large (>10 pts):      {len(large):4d} ({len(large)/len(matches)*100:5.1f}%)")
    print()

    # Directional analysis
    print("🎯 DIRECTIONAL ANALYSIS")
    print("=" * 80)

    over_predictions = [m for m in matches if m['gregs_total'] > m['actual_total']]
    under_predictions = [m for m in matches if m['gregs_total'] < m['actual_total']]
    exact = [m for m in matches if m['gregs_total'] == m['actual_total']]

    print(f"Greg Higher than Actual: {len(over_predictions):4d} ({len(over_predictions)/len(matches)*100:5.1f}%)")
    if over_predictions:
        over_mae = sum(abs(m['gregs_total'] - m['actual_total']) for m in over_predictions) / len(over_predictions)
        print(f"  → Average overestimate: {over_mae:.2f} points")

    print(f"Greg Lower than Actual:  {len(under_predictions):4d} ({len(under_predictions)/len(matches)*100:5.1f}%)")
    if under_predictions:
        under_mae = sum(abs(m['gregs_total'] - m['actual_total']) for m in under_predictions) / len(under_predictions)
        print(f"  → Average underestimate: {under_mae:.2f} points")

    print(f"Exact Match:             {len(exact):4d} ({len(exact)/len(matches)*100:5.1f}%)")
    print()

    # Potential edge games (significant differences)
    print("🔥 POTENTIAL EDGE INDICATORS")
    print("=" * 80)
    print("(Games where Greg differed significantly from actual - possible betting opportunities)")
    print()

    # Significant UNDER indicators (Greg 5+ below actual)
    under_edges = [m for m in matches if m['gregs_total'] <= m['actual_total'] - 5]
    print(f"🔵 UNDER Indicators (Greg ≥5 below actual): {len(under_edges)}")
    if under_edges:
        under_edge_mae = sum(abs(m['gregs_total'] - m['actual_total']) for m in under_edges) / len(under_edges)
        print(f"   Average difference: {under_edge_mae:.2f} points")

    # Significant OVER indicators (Greg 3+ above actual)
    over_edges = [m for m in matches if m['gregs_total'] >= m['actual_total'] + 3]
    print(f"🔴 OVER Indicators (Greg ≥3 above actual): {len(over_edges)}")
    if over_edges:
        over_edge_mae = sum(abs(m['gregs_total'] - m['actual_total']) for m in over_edges) / len(over_edges)
        print(f"   Average difference: {over_edge_mae:.2f} points")

    print()
    print(f"Total Edge Indicators: {len(under_edges) + len(over_edges)} games")
    print(f"  ({(len(under_edges) + len(over_edges))/len(matches)*100:.1f}% of all games)")
    print()

    # Sample games with largest differences
    print("📋 LARGEST PREDICTION DIFFERENCES (Top 10)")
    print("=" * 80)

    sorted_by_diff = sorted(matches, key=lambda m: abs(m['gregs_total'] - m['actual_total']), reverse=True)

    for i, match in enumerate(sorted_by_diff[:10], 1):
        diff = match['gregs_total'] - match['actual_total']
        direction = "OVER" if diff > 0 else "UNDER"
        print(f"{i}. {match['matchup']} - {match['date'].strftime('%m/%d')}")
        print(f"   Greg: {match['gregs_total']:.1f} | Actual: {match['actual_total']} | Diff: {diff:+.1f} ({direction})")
        print()


if __name__ == '__main__':
    # Default to current season (Nov 2025 - current)
    season_start = datetime(2025, 11, 1)
    season_end = datetime.now()

    if len(sys.argv) > 1:
        # Allow custom date range
        # Usage: python backtest_picks.py 2025-11-01 2026-01-26
        season_start = datetime.strptime(sys.argv[1], '%Y-%m-%d')
        if len(sys.argv) > 2:
            season_end = datetime.strptime(sys.argv[2], '%Y-%m-%d')

    backtest_season(season_start, season_end)
