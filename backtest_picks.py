#!/usr/bin/env python3
"""
Backtest Greg Peterson's picks against this season's actual results.

This script analyzes what Greg's record would have been using the flame emoji methodology:
- UNDER picks when Greg's total is 5+ points below actual (proxy for sportsbook line)
- OVER picks when Greg's total is 3+ points above actual (proxy for sportsbook line)

Since we don't have historical sportsbook lines, we use the actual final total as a proxy
for what the sportsbook line would have been (assuming sportsbooks set lines close to actual results).

All picks assume -110 odds (bet $110 to win $100).
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


def calculate_profit_loss(wins: int, losses: int) -> Tuple[float, float]:
    """
    Calculate profit/loss at -110 odds.

    Args:
        wins: Number of winning bets
        losses: Number of losing bets

    Returns:
        (total_profit_loss, roi_percentage)
    """
    # At -110 odds: risk $110 to win $100
    total_risked = (wins + losses) * 110
    profit_from_wins = wins * 100
    loss_from_losses = losses * 110
    total_profit_loss = profit_from_wins - loss_from_losses

    if total_risked > 0:
        roi = (total_profit_loss / total_risked) * 100
    else:
        roi = 0.0

    return total_profit_loss, roi


def backtest_season(start_date: datetime, end_date: datetime):
    """Backtest Greg's picks for a date range."""

    print("🏀 CBB PICKS BACKTEST")
    print("=" * 80)
    print(f"Date Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"Methodology: Betting Greg's totals at -110 odds")
    print(f"Assumption: Sportsbook lines ≈ actual totals (efficient market)")
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
        print("❌ No games matched - cannot run backtest")
        return

    # Strategy: Use actual total as proxy for sportsbook line
    # Apply flame methodology: picks where Greg differs significantly from actual
    # - UNDER when Greg is 5+ below actual (Greg predicts lower-scoring)
    # - OVER when Greg is 3+ above actual (Greg predicts higher-scoring)
    # Then check: if we bet the sportsbook line (≈actual), did the pick win?

    # Since actual ≈ sportsbook, we'll use a small margin (0.5 points)
    # to simulate sportsbook being slightly off from actual

    print("🔥 FLAME EMOJI PICKS (High Conviction Games)")
    print("=" * 80)
    print()

    flame_picks = []

    for match in matches:
        gregs_total = match['gregs_total']
        actual_total = match['actual_total']
        difference = gregs_total - actual_total

        # Simulate: sportsbook line was 0.5 below actual (typical juice adjustment)
        implied_sportsbook_line = actual_total - 0.5

        # UNDER picks: Greg is 5+ below actual (conservative estimate)
        # Greg thinks it'll be low-scoring, we bet UNDER on sportsbook line
        if gregs_total <= implied_sportsbook_line - 5.0:
            # Bet UNDER on sportsbook line
            # UNDER wins if actual < sportsbook line
            pick_wins = actual_total < implied_sportsbook_line
            flame_picks.append({
                **match,
                'pick': 'UNDER',
                'sportsbook_line': implied_sportsbook_line,
                'edge': gregs_total - implied_sportsbook_line,
                'wins': pick_wins
            })

        # OVER picks: Greg is 3+ above actual (aggressive estimate)
        # Greg thinks it'll be high-scoring, we bet OVER on sportsbook line
        elif gregs_total >= implied_sportsbook_line + 3.0:
            # Bet OVER on sportsbook line
            # OVER wins if actual > sportsbook line
            pick_wins = actual_total > implied_sportsbook_line
            flame_picks.append({
                **match,
                'pick': 'OVER',
                'sportsbook_line': implied_sportsbook_line,
                'edge': gregs_total - implied_sportsbook_line,
                'wins': pick_wins
            })

    if len(flame_picks) == 0:
        print("❌ No games met the flame emoji thresholds")
        print("   (UNDER: Greg ≥5 below actual, OVER: Greg ≥3 above actual)")
        return

    # Calculate results
    total_wins = sum(1 for p in flame_picks if p['wins'])
    total_losses = len(flame_picks) - total_wins
    win_pct = (total_wins / len(flame_picks)) * 100

    profit_loss, roi = calculate_profit_loss(total_wins, total_losses)

    # Display overall results
    print(f"📊 OVERALL RESULTS (Flame Picks Only)")
    print(f"Total Picks: {len(flame_picks)}")
    print(f"Record: {total_wins}-{total_losses} ({win_pct:.1f}%)")
    print(f"Profit/Loss: ${profit_loss:+.2f} (risking $110 per game)")
    print(f"ROI: {roi:+.2f}%")
    print(f"Breakeven Win%: 52.4% (needed to profit at -110)")
    print()

    # Break down by pick type
    under_picks = [p for p in flame_picks if p['pick'] == 'UNDER']
    over_picks = [p for p in flame_picks if p['pick'] == 'OVER']

    if under_picks:
        under_wins = sum(1 for p in under_picks if p['wins'])
        under_losses = len(under_picks) - under_wins
        under_pct = (under_wins / len(under_picks)) * 100
        under_pl, under_roi = calculate_profit_loss(under_wins, under_losses)

        print(f"🔵 UNDER PICKS (Greg ≥5 below sportsbook)")
        print(f"Count: {len(under_picks)}")
        print(f"Record: {under_wins}-{under_losses} ({under_pct:.1f}%)")
        print(f"Profit/Loss: ${under_pl:+.2f}")
        print(f"ROI: {under_roi:+.2f}%")
        print()

    if over_picks:
        over_wins = sum(1 for p in over_picks if p['wins'])
        over_losses = len(over_picks) - over_wins
        over_pct = (over_wins / len(over_picks)) * 100
        over_pl, over_roi = calculate_profit_loss(over_wins, over_losses)

        print(f"🔴 OVER PICKS (Greg ≥3 above sportsbook)")
        print(f"Count: {len(over_picks)}")
        print(f"Record: {over_wins}-{over_losses} ({over_pct:.1f}%)")
        print(f"Profit/Loss: ${over_pl:+.2f}")
        print(f"ROI: {over_roi:+.2f}%")
        print()

    # Show sample picks
    print("📋 SAMPLE PICKS (first 10)")
    print("=" * 80)
    for i, pick in enumerate(flame_picks[:10], 1):
        result = "✓ WIN" if pick['wins'] else "✗ LOSS"
        print(f"{i}. {pick['matchup']} - {pick['date'].strftime('%m/%d')}")
        print(f"   Greg: {pick['gregs_total']:.1f} | Sportsbook: {pick['sportsbook_line']:.1f} | Actual: {pick['actual_total']}")
        print(f"   Pick: {pick['pick']} {pick['sportsbook_line']:.1f} | Edge: {pick['edge']:+.1f} | {result}")
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
