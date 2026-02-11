"""
Compare Greg's MLB Prices to Vegas Closing Lines
Finds pricing edges and analyzes profitability.
"""
import argparse
from datetime import datetime, date
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

from gregs_mlb_parser import GregsMLBParser
from vegas_odds_parser import VegasOddsParser, VEGAS_ODDS_URL
from mlb_team_mapper import normalize_mlb_team_name


def match_teams(greg_team: str, vegas_team: str) -> bool:
    """
    Check if two team names match.

    Args:
        greg_team: Team name from Greg's sheet
        vegas_team: Team name from Vegas odds

    Returns:
        True if teams match
    """
    greg_normalized = normalize_mlb_team_name(greg_team)
    vegas_normalized = normalize_mlb_team_name(vegas_team)

    if not greg_normalized or not vegas_normalized:
        return False

    return greg_normalized == vegas_normalized


def match_games(greg_games: List[Dict], vegas_games: List[Dict]) -> List[Dict]:
    """
    Match Greg's games to Vegas closing lines by date and teams.

    Args:
        greg_games: List of games from Greg's sheet
        vegas_games: List of games from Vegas odds

    Returns:
        List of matched games with both Greg and Vegas odds
    """
    matches = []

    # Build Vegas lookup by date and teams
    vegas_lookup = {}
    vegas_dates = set()
    vegas_teams = set()

    for vg in vegas_games:
        if not vg.get('date') or not vg.get('away_team') or not vg.get('home_team'):
            continue

        vegas_dates.add(vg['date'])
        vegas_teams.add(normalize_mlb_team_name(vg['away_team']))
        vegas_teams.add(normalize_mlb_team_name(vg['home_team']))

        key = (
            vg['date'],
            normalize_mlb_team_name(vg['away_team']),
            normalize_mlb_team_name(vg['home_team'])
        )
        vegas_lookup[key] = vg

    print(f"\nBuilt Vegas lookup with {len(vegas_lookup)} games")
    print(f"Vegas date range: {min(vegas_dates)} to {max(vegas_dates)}")
    print(f"Sample Vegas teams: {list(sorted(vegas_teams))[:10]}")

    # Debug: Show sample Vegas keys
    print(f"\nSample Vegas lookup keys:")
    for i, key in enumerate(list(vegas_lookup.keys())[:5]):
        print(f"  {key}")

    # Match Greg's games
    greg_dates = set()
    greg_teams = set()

    for gg in greg_games:
        if not gg.get('date') or not gg.get('away_team') or not gg.get('home_team'):
            continue

        greg_dates.add(gg['date'])
        greg_teams.add(normalize_mlb_team_name(gg['away_team']))
        greg_teams.add(normalize_mlb_team_name(gg['home_team']))

        key = (
            gg['date'],
            normalize_mlb_team_name(gg['away_team']),
            normalize_mlb_team_name(gg['home_team'])
        )

        if key in vegas_lookup:
            vg = vegas_lookup[key]

            # Create combined game record
            match = {
                'date': gg['date'],
                'away_team': gg['away_team'],
                'home_team': gg['home_team'],

                # Greg's odds
                'greg_away_ml': gg.get('away_moneyline'),
                'greg_home_ml': gg.get('home_moneyline'),
                'greg_total': gg.get('total'),
                'greg_away_runline_odds': gg.get('away_runline_odds'),
                'greg_home_runline_odds': gg.get('home_runline_odds'),

                # Vegas closing lines
                'vegas_away_ml': vg.get('away_moneyline'),
                'vegas_home_ml': vg.get('home_moneyline'),
                'vegas_total': vg.get('total'),
                'vegas_over_odds': vg.get('over_odds'),
                'vegas_under_odds': vg.get('under_odds'),

                # Actual results
                'away_score': vg.get('away_score'),
                'home_score': vg.get('home_score'),
                'status': vg.get('status'),
            }

            matches.append(match)

    if greg_dates:
        print(f"\nGreg's date range: {min(greg_dates)} to {max(greg_dates)}")
        print(f"Sample Greg's teams: {list(sorted(greg_teams))[:10]}")

        # Show sample Greg's keys
        print(f"\nSample Greg's lookup keys:")
        sample_count = 0
        for gg in greg_games[:5]:
            if gg.get('date') and gg.get('away_team') and gg.get('home_team'):
                key = (
                    gg['date'],
                    normalize_mlb_team_name(gg['away_team']),
                    normalize_mlb_team_name(gg['home_team'])
                )
                print(f"  {key}")
                sample_count += 1
                if sample_count >= 5:
                    break
    else:
        print("\nWarning: No valid dates found in Greg's games!")

    print(f"\nMatched {len(matches)} games between Greg and Vegas")

    return matches


def analyze_moneyline_edge(matches: List[Dict]) -> Dict:
    """
    Analyze moneyline pricing differences.

    Finds cases where Greg's price differs from Vegas closing line
    and calculates profitability.

    Args:
        matches: List of matched games

    Returns:
        Analysis results
    """
    print(f"\n{'='*80}")
    print("MONEYLINE PRICE COMPARISON")
    print(f"{'='*80}")

    results = {
        'away_favorites': defaultdict(lambda: {'count': 0, 'wins': 0, 'total_roi': 0}),
        'home_favorites': defaultdict(lambda: {'count': 0, 'wins': 0, 'total_roi': 0}),
        'price_differences': [],
    }

    for match in matches:
        if match['status'] != 'Final':
            continue

        greg_away_ml = match.get('greg_away_ml')
        greg_home_ml = match.get('greg_home_ml')
        vegas_away_ml = match.get('vegas_away_ml')
        vegas_home_ml = match.get('vegas_home_ml')

        if not all([greg_away_ml, greg_home_ml, vegas_away_ml, vegas_home_ml]):
            continue

        away_score = match.get('away_score')
        home_score = match.get('home_score')

        if away_score is None or home_score is None:
            continue

        away_won = away_score > home_score

        # Calculate price differences
        away_diff = greg_away_ml - vegas_away_ml
        home_diff = greg_home_ml - vegas_home_ml

        # Store all price differences for analysis
        results['price_differences'].append({
            'date': match['date'],
            'away_team': match['away_team'],
            'home_team': match['home_team'],
            'away_diff': away_diff,
            'home_diff': home_diff,
            'away_won': away_won,
            'greg_away_ml': greg_away_ml,
            'vegas_away_ml': vegas_away_ml,
            'greg_home_ml': greg_home_ml,
            'vegas_home_ml': vegas_home_ml,
        })

        # Analyze by price difference buckets
        # Look for cases where Greg is higher (better value) than Vegas
        if away_diff >= 10:  # Greg's away price is at least 10 points better
            bucket = f"+{(away_diff // 10) * 10}"
            results['away_favorites'][bucket]['count'] += 1
            if away_won:
                results['away_favorites'][bucket]['wins'] += 1

        if home_diff >= 10:  # Greg's home price is at least 10 points better
            bucket = f"+{(home_diff // 10) * 10}"
            results['home_favorites'][bucket]['count'] += 1
            if not away_won:
                results['home_favorites'][bucket]['wins'] += 1

    # Print results
    print(f"\nTotal games analyzed: {len(results['price_differences'])}")

    print(f"\n{'='*80}")
    print("AWAY TEAMS - Greg's Price Better Than Vegas")
    print(f"{'='*80}")
    print(f"{'Diff Bucket':<15} {'Count':<10} {'Wins':<10} {'Win %':<10} {'Edge'}")
    print(f"{'-'*80}")

    for bucket in sorted(results['away_favorites'].keys()):
        stats = results['away_favorites'][bucket]
        win_pct = (stats['wins'] / stats['count'] * 100) if stats['count'] > 0 else 0
        # Implied probability at average Vegas price would need to be calculated
        print(f"{bucket:<15} {stats['count']:<10} {stats['wins']:<10} {win_pct:<10.1f}%")

    print(f"\n{'='*80}")
    print("HOME TEAMS - Greg's Price Better Than Vegas")
    print(f"{'='*80}")
    print(f"{'Diff Bucket':<15} {'Count':<10} {'Wins':<10} {'Win %':<10} {'Edge'}")
    print(f"{'-'*80}")

    for bucket in sorted(results['home_favorites'].keys()):
        stats = results['home_favorites'][bucket]
        win_pct = (stats['wins'] / stats['count'] * 100) if stats['count'] > 0 else 0
        print(f"{bucket:<15} {stats['count']:<10} {stats['wins']:<10} {win_pct:<10.1f}%")

    return results


def analyze_totals_edge(matches: List[Dict]) -> Dict:
    """
    Analyze totals pricing differences.

    Finds cases where Greg's total differs from Vegas closing line.

    Args:
        matches: List of matched games

    Returns:
        Analysis results
    """
    print(f"\n{'='*80}")
    print("TOTALS COMPARISON")
    print(f"{'='*80}")

    results = {
        'greg_higher': defaultdict(lambda: {'count': 0, 'over': 0, 'under': 0}),
        'greg_lower': defaultdict(lambda: {'count': 0, 'over': 0, 'under': 0}),
        'total_differences': [],
    }

    for match in matches:
        if match['status'] != 'Final':
            continue

        greg_total = match.get('greg_total')
        vegas_total = match.get('vegas_total')

        if greg_total is None or vegas_total is None:
            continue

        away_score = match.get('away_score')
        home_score = match.get('home_score')

        if away_score is None or home_score is None:
            continue

        total_runs = away_score + home_score
        went_over = total_runs > vegas_total

        # Calculate difference
        diff = greg_total - vegas_total

        results['total_differences'].append({
            'date': match['date'],
            'away_team': match['away_team'],
            'home_team': match['home_team'],
            'diff': diff,
            'greg_total': greg_total,
            'vegas_total': vegas_total,
            'actual_total': total_runs,
            'went_over': went_over,
        })

        # Analyze by difference buckets (0.1 run increments)
        if abs(diff) >= 0.1:
            bucket = f"{diff:.1f}"

            if diff > 0:  # Greg higher than Vegas
                results['greg_higher'][bucket]['count'] += 1
                if went_over:
                    results['greg_higher'][bucket]['over'] += 1
                else:
                    results['greg_higher'][bucket]['under'] += 1
            else:  # Greg lower than Vegas
                results['greg_lower'][bucket]['count'] += 1
                if went_over:
                    results['greg_lower'][bucket]['over'] += 1
                else:
                    results['greg_lower'][bucket]['under'] += 1

    # Print results
    print(f"\nTotal games analyzed: {len(results['total_differences'])}")

    print(f"\n{'='*80}")
    print("Greg's Total HIGHER Than Vegas")
    print(f"{'='*80}")
    print(f"{'Diff':<10} {'Count':<10} {'Overs':<10} {'Unders':<10} {'Over %'}")
    print(f"{'-'*80}")

    for bucket in sorted(results['greg_higher'].keys(), key=float):
        stats = results['greg_higher'][bucket]
        over_pct = (stats['over'] / stats['count'] * 100) if stats['count'] > 0 else 0
        print(f"{bucket:<10} {stats['count']:<10} {stats['over']:<10} {stats['under']:<10} {over_pct:.1f}%")

    print(f"\n{'='*80}")
    print("Greg's Total LOWER Than Vegas")
    print(f"{'='*80}")
    print(f"{'Diff':<10} {'Count':<10} {'Overs':<10} {'Unders':<10} {'Over %'}")
    print(f"{'-'*80}")

    for bucket in sorted(results['greg_lower'].keys(), key=float, reverse=True):
        stats = results['greg_lower'][bucket]
        over_pct = (stats['over'] / stats['count'] * 100) if stats['count'] > 0 else 0
        print(f"{bucket:<10} {stats['count']:<10} {stats['over']:<10} {stats['under']:<10} {over_pct:.1f}%")

    return results


def main():
    parser = argparse.ArgumentParser(
        description='Compare Greg\'s MLB prices to Vegas closing lines'
    )
    parser.add_argument(
        '--gregs-file',
        required=True,
        help='Path to Greg\'s MLB handicapping sheet'
    )
    parser.add_argument(
        '--vegas-file',
        default=VEGAS_ODDS_URL,
        help='Path or URL to Vegas odds file (default: Google Sheets URL)'
    )
    parser.add_argument(
        '--sheet-name',
        default='2025',
        help='Sheet name in Greg\'s file (default: 2025)'
    )

    args = parser.parse_args()

    print(f"{'='*80}")
    print("GREG'S MLB PRICES VS VEGAS CLOSING LINES")
    print(f"{'='*80}")

    # Parse Greg's sheet
    print(f"\nParsing Greg's file: {args.gregs_file}")
    greg_parser = GregsMLBParser(args.gregs_file)
    greg_games = greg_parser.parse_sheet(args.sheet_name)
    print(f"Parsed {len(greg_games)} games from Greg's sheet")

    # Show sample Greg games
    if greg_games:
        print("\nSample Greg's games:")
        for i, game in enumerate(greg_games[:3]):
            print(f"\nGame {i+1}:")
            print(f"  Date: {game.get('date')}")
            print(f"  Matchup: {game.get('away_team')} @ {game.get('home_team')}")
            print(f"  Moneylines: {game.get('away_moneyline')} / {game.get('home_moneyline')}")
            print(f"  Total: {game.get('total')}")
    else:
        print("\nWarning: Greg's parser returned no games!")

    # Parse Vegas odds
    print(f"\nParsing Vegas odds: {args.vegas_file}")
    vegas_parser = VegasOddsParser(args.vegas_file)
    if not vegas_parser.load_file():
        print("Failed to load Vegas odds file")
        return

    vegas_games = vegas_parser.parse_all_sheets(sheet_filter="Betting Odds")
    print(f"Parsed {len(vegas_games)} games from Vegas odds")

    # Match games
    matches = match_games(greg_games, vegas_games)

    if not matches:
        print("\nNo matching games found!")
        return

    # Analyze moneyline edges
    ml_results = analyze_moneyline_edge(matches)

    # Analyze totals edges
    totals_results = analyze_totals_edge(matches)

    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()
