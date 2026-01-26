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
from typing import List, Dict, Tuple
from gregs_cbb_parser import GregsCBBParser
from scores_fetcher import ScoresFetcher


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


def backtest_season(start_date: datetime, end_date: datetime):
    """Analyze Greg's prediction accuracy for a date range."""

    print("🏀 GREG'S CBB TOTALS ACCURACY ANALYSIS")
    print("=" * 80)
    print(f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Analysis: Prediction accuracy vs actual game totals")
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
    matches = []
    for gregs_game in games_in_range:
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

    print(f"✓ Matched {len(matches)}/{len(games_in_range)} games")
    print()

    if len(matches) == 0:
        print("❌ No games matched - cannot run analysis")
        return

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
