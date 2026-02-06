#!/usr/bin/env python3
"""
Analyze Greg's MLB Moneyline Edge
Compares Greg's implied probabilities to actual win rates to find value.
"""
import sys
from datetime import datetime
from gregs_mlb_parser import GregsMLBParser
from find_mlb_edge import fetch_espn_scores, match_teams, download_gregs_sheet
from typing import List, Dict


def moneyline_to_implied_prob(moneyline: int) -> float:
    """
    Convert American odds moneyline to implied probability.

    Args:
        moneyline: American odds (e.g., -150, +130)

    Returns:
        Implied probability as decimal (0.60 = 60%)
    """
    if moneyline < 0:
        # Favorite: -150 means risk $150 to win $100
        return abs(moneyline) / (abs(moneyline) + 100)
    else:
        # Underdog: +130 means risk $100 to win $130
        return 100 / (moneyline + 100)


def calculate_ml_roi(wins: int, losses: int, avg_odds: float) -> tuple:
    """
    Calculate ROI for moneyline bets.

    Args:
        wins: Number of wins
        losses: Number of losses
        avg_odds: Average moneyline odds

    Returns:
        (profit, roi) tuple
    """
    if wins + losses == 0:
        return 0.0, 0.0

    # Calculate profit based on average odds
    if avg_odds < 0:
        # Favorite: risk abs(odds) to win 100
        win_amount = 100
        risk_amount = abs(avg_odds)
    else:
        # Underdog: risk 100 to win odds
        win_amount = avg_odds
        risk_amount = 100

    total_won = wins * win_amount
    total_lost = losses * risk_amount
    profit = total_won - total_lost

    total_risked = (wins + losses) * risk_amount
    roi = (profit / total_risked) * 100 if total_risked > 0 else 0

    return profit, roi


def analyze_moneyline_edge(start_date: datetime, end_date: datetime):
    """Analyze Greg's moneyline pricing edge."""

    print("⚾ ANALYZING GREG'S MLB MONEYLINE EDGE")
    print("=" * 80)
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print("=" * 80)
    print()

    # Load Greg's data
    print("📊 Loading data...")
    file_path = download_gregs_sheet()
    parser = GregsMLBParser(file_path)
    parser.load_file()
    games = parser.parse_all_sheets()

    games_in_range = [g for g in games if start_date.date() <= g['date'].date() <= end_date.date()]
    print(f"✓ {len(games_in_range)} games from Greg")

    # Fetch actual results
    print("\n📈 Fetching results...")
    from datetime import timedelta
    all_scores = []
    current_date = start_date

    while current_date <= end_date:
        scores = fetch_espn_scores(current_date)
        all_scores.extend(scores)
        current_date += timedelta(days=1)

    print(f"✓ {len(all_scores)} completed games")

    # Match games
    print("\n🔗 Matching games...")
    matches = []

    for gregs_game in games_in_range:
        for score_game in all_scores:
            if match_teams(gregs_game['away_team'], score_game['away_team']) and \
               match_teams(gregs_game['home_team'], score_game['home_team']):

                # Determine who won
                away_won = score_game['away_score'] > score_game['home_score']

                # Get moneylines
                away_ml = gregs_game.get('away_moneyline')
                home_ml = gregs_game.get('home_moneyline')

                if away_ml is not None and home_ml is not None:
                    matches.append({
                        'away_team': gregs_game['away_team'],
                        'home_team': gregs_game['home_team'],
                        'away_ml': away_ml,
                        'home_ml': home_ml,
                        'away_won': away_won,
                        'home_won': not away_won
                    })
                break

    print(f"✓ Matched {len(matches)} games with moneylines")
    print()

    if len(matches) < 10:
        print("❌ Not enough matched games")
        return

    # Analyze by price ranges
    print("🎯 MONEYLINE EDGE BY PRICE RANGE")
    print("=" * 80)
    print()

    # Define price ranges
    favorite_ranges = [
        (-120, -100, "Light Favorites (-120 to -100)"),
        (-150, -121, "Moderate Favorites (-150 to -121)"),
        (-200, -151, "Strong Favorites (-200 to -151)"),
        (-999, -201, "Heavy Favorites (-201+)")
    ]

    underdog_ranges = [
        (100, 120, "Light Underdogs (+100 to +120)"),
        (121, 150, "Moderate Underdogs (+121 to +150)"),
        (151, 200, "Strong Underdogs (+151 to +200)"),
        (201, 999, "Heavy Underdogs (+201+)")
    ]

    print("FAVORITES:")
    print("-" * 80)
    for min_odds, max_odds, label in favorite_ranges:
        results = []
        total_odds = 0

        # Check both home and away favorites in this range
        for match in matches:
            # Home favorite
            if max_odds >= match['home_ml'] >= min_odds:
                results.append(1 if match['home_won'] else 0)
                total_odds += match['home_ml']
            # Away favorite
            if max_odds >= match['away_ml'] >= min_odds:
                results.append(1 if match['away_won'] else 0)
                total_odds += match['away_ml']

        if results:
            wins = sum(results)
            losses = len(results) - wins
            win_rate = (wins / len(results)) * 100
            avg_odds = total_odds / len(results)
            implied_prob = moneyline_to_implied_prob(int(avg_odds)) * 100
            profit, roi = calculate_ml_roi(wins, losses, avg_odds)

            edge = win_rate - implied_prob

            print(f"\n{label}")
            print(f"  Games: {len(results)} | W-L: {wins}-{losses} ({win_rate:.1f}%)")
            print(f"  Avg Odds: {avg_odds:.0f} (Implied: {implied_prob:.1f}%)")
            print(f"  Edge: {edge:+.1f}% | ROI: {roi:+.1f}%")

    print("\n\nUNDERDOGS:")
    print("-" * 80)
    for min_odds, max_odds, label in underdog_ranges:
        results = []
        total_odds = 0

        # Check both home and away underdogs in this range
        for match in matches:
            # Home underdog
            if min_odds <= match['home_ml'] <= max_odds:
                results.append(1 if match['home_won'] else 0)
                total_odds += match['home_ml']
            # Away underdog
            if min_odds <= match['away_ml'] <= max_odds:
                results.append(1 if match['away_won'] else 0)
                total_odds += match['away_ml']

        if results:
            wins = sum(results)
            losses = len(results) - wins
            win_rate = (wins / len(results)) * 100
            avg_odds = total_odds / len(results)
            implied_prob = moneyline_to_implied_prob(int(avg_odds)) * 100
            profit, roi = calculate_ml_roi(wins, losses, avg_odds)

            edge = win_rate - implied_prob

            print(f"\n{label}")
            print(f"  Games: {len(results)} | W-L: {wins}-{losses} ({win_rate:.1f}%)")
            print(f"  Avg Odds: {avg_odds:.0f} (Implied: {implied_prob:.1f}%)")
            print(f"  Edge: {edge:+.1f}% | ROI: {roi:+.1f}%")

    print("\n" + "=" * 80)
    print("\n💡 INTERPRETATION:")
    print("  - Positive Edge = Greg's teams win more than his prices imply")
    print("  - Positive ROI = Betting at Greg's prices would be profitable")
    print("  - Look for ranges with consistent positive edge and ROI")
    print()


if __name__ == '__main__':
    # Default: 2025 season
    season_start = datetime(2025, 3, 28)
    season_end = datetime(2025, 9, 28)

    if len(sys.argv) > 1:
        season_start = datetime.strptime(sys.argv[1], '%Y-%m-%d')
        if len(sys.argv) > 2:
            season_end = datetime.strptime(sys.argv[2], '%Y-%m-%d')

    analyze_moneyline_edge(season_start, season_end)
