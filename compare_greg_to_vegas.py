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
    unmatched_games = []

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
                'vegas_away_runline_odds': vg.get('away_runline_odds'),
                'vegas_home_runline_odds': vg.get('home_runline_odds'),

                # Actual results
                'away_score': vg.get('away_score'),
                'home_score': vg.get('home_score'),
                'status': vg.get('status'),
            }

            matches.append(match)
        else:
            # Track unmatched games
            unmatched_games.append({
                'date': gg['date'],
                'away_team': gg['away_team'],
                'home_team': gg['home_team'],
                'normalized_away': normalize_mlb_team_name(gg['away_team']),
                'normalized_home': normalize_mlb_team_name(gg['home_team']),
                'key': key
            })

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
    print(f"Unmatched games from Greg: {len(unmatched_games)}")

    # Show first 20 unmatched games to help debug
    if unmatched_games:
        print(f"\nFirst 20 unmatched games from Greg:")
        for i, ug in enumerate(unmatched_games[:20]):
            print(f"  {ug['date']} | {ug['normalized_away']} @ {ug['normalized_home']}")
            # Check if date exists in Vegas
            if ug['date'] not in vegas_dates:
                print(f"    ^ Date not in Vegas dataset")
            # Check if teams exist in Vegas
            if ug['normalized_away'] not in vegas_teams:
                print(f"    ^ Away team '{ug['normalized_away']}' not in Vegas dataset")
            if ug['normalized_home'] not in vegas_teams:
                print(f"    ^ Home team '{ug['normalized_home']}' not in Vegas dataset")

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
    print(f"{'Greg Edge':<15} {'Record':<15} {'Win %':<10} {'Avg Greg':<12} {'Avg Vegas':<12} {'Edge Value'}")
    print(f"{'-'*80}")

    for bucket in sorted(results['away_favorites'].keys()):
        stats = results['away_favorites'][bucket]
        win_pct = (stats['wins'] / stats['count'] * 100) if stats['count'] > 0 else 0
        losses = stats['count'] - stats['wins']
        record = f"{stats['wins']}-{losses}"

        # Calculate average prices for this bucket
        bucket_games = [g for g in results['price_differences'] if f"+{(g['away_diff'] // 10) * 10}" == bucket and g['away_diff'] >= 10]
        avg_greg = sum(g['greg_away_ml'] for g in bucket_games) / len(bucket_games) if bucket_games else 0
        avg_vegas = sum(g['vegas_away_ml'] for g in bucket_games) / len(bucket_games) if bucket_games else 0
        edge_value = avg_greg - avg_vegas

        print(f"{bucket:<15} {record:<15} {win_pct:<10.1f}% {avg_greg:<12.0f} {avg_vegas:<12.0f} {edge_value:+.0f}")

    print(f"\n{'='*80}")
    print("HOME TEAMS - Greg's Price Better Than Vegas")
    print(f"{'='*80}")
    print(f"{'Greg Edge':<15} {'Record':<15} {'Win %':<10} {'Avg Greg':<12} {'Avg Vegas':<12} {'Edge Value'}")
    print(f"{'-'*80}")

    for bucket in sorted(results['home_favorites'].keys()):
        stats = results['home_favorites'][bucket]
        win_pct = (stats['wins'] / stats['count'] * 100) if stats['count'] > 0 else 0
        losses = stats['count'] - stats['wins']
        record = f"{stats['wins']}-{losses}"

        # Calculate average prices for this bucket
        bucket_games = [g for g in results['price_differences'] if f"+{(g['home_diff'] // 10) * 10}" == bucket and g['home_diff'] >= 10]
        avg_greg = sum(g['greg_home_ml'] for g in bucket_games) / len(bucket_games) if bucket_games else 0
        avg_vegas = sum(g['vegas_home_ml'] for g in bucket_games) / len(bucket_games) if bucket_games else 0
        edge_value = avg_greg - avg_vegas

        print(f"{bucket:<15} {record:<15} {win_pct:<10.1f}% {avg_greg:<12.0f} {avg_vegas:<12.0f} {edge_value:+.0f}")

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
    print("Greg's Total HIGHER Than Vegas - BET OVER")
    print(f"{'='*80}")
    print(f"{'Greg Edge':<12} {'Record (O-U)':<15} {'Over %':<10} {'Avg Greg':<12} {'Avg Vegas':<12} {'Edge'}")
    print(f"{'-'*80}")

    for bucket in sorted(results['greg_higher'].keys(), key=float):
        stats = results['greg_higher'][bucket]
        over_pct = (stats['over'] / stats['count'] * 100) if stats['count'] > 0 else 0
        record = f"{stats['over']}-{stats['under']}"

        # Calculate average totals for this bucket
        bucket_games = [g for g in results['total_differences'] if f"{g['diff']:.1f}" == bucket and g['diff'] > 0]
        avg_greg = sum(g['greg_total'] for g in bucket_games) / len(bucket_games) if bucket_games else 0
        avg_vegas = sum(g['vegas_total'] for g in bucket_games) / len(bucket_games) if bucket_games else 0
        edge = float(bucket)

        print(f"+{bucket:<11} {record:<15} {over_pct:<10.1f}% {avg_greg:<12.1f} {avg_vegas:<12.1f} {edge:+.1f}")

    print(f"\n{'='*80}")
    print("Greg's Total LOWER Than Vegas - BET UNDER")
    print(f"{'='*80}")
    print(f"{'Greg Edge':<12} {'Record (U-O)':<15} {'Under %':<10} {'Avg Greg':<12} {'Avg Vegas':<12} {'Edge'}")
    print(f"{'-'*80}")

    for bucket in sorted(results['greg_lower'].keys(), key=float, reverse=True):
        stats = results['greg_lower'][bucket]
        under_pct = (stats['under'] / stats['count'] * 100) if stats['count'] > 0 else 0
        record = f"{stats['under']}-{stats['over']}"

        # Calculate average totals for this bucket
        bucket_games = [g for g in results['total_differences'] if f"{g['diff']:.1f}" == bucket and g['diff'] < 0]
        avg_greg = sum(g['greg_total'] for g in bucket_games) / len(bucket_games) if bucket_games else 0
        avg_vegas = sum(g['vegas_total'] for g in bucket_games) / len(bucket_games) if bucket_games else 0
        edge = float(bucket)

        print(f"{bucket:<12} {record:<15} {under_pct:<10.1f}% {avg_greg:<12.1f} {avg_vegas:<12.1f} {edge:+.1f}")

    return results


def analyze_runline_edge(matches: List[Dict]) -> Dict:
    """
    Analyze run line pricing differences.

    Finds cases where Greg's run line price differs from Vegas closing line.

    Args:
        matches: List of matched games

    Returns:
        Analysis results
    """
    print(f"\n{'='*80}")
    print("RUN LINE PRICE COMPARISON")
    print(f"{'='*80}")

    results = {
        'away_runline': defaultdict(lambda: {'count': 0, 'wins': 0, 'losses': 0}),
        'home_runline': defaultdict(lambda: {'count': 0, 'wins': 0, 'losses': 0}),
        'runline_differences': [],
    }

    for match in matches:
        if match['status'] != 'Final':
            continue

        greg_away_rl = match.get('greg_away_runline_odds')
        greg_home_rl = match.get('greg_home_runline_odds')
        vegas_away_rl = match.get('vegas_away_runline_odds')
        vegas_home_rl = match.get('vegas_home_runline_odds')

        if not all([greg_away_rl, greg_home_rl, vegas_away_rl, vegas_home_rl]):
            continue

        away_score = match.get('away_score')
        home_score = match.get('home_score')

        if away_score is None or home_score is None:
            continue

        # Determine run line result (typically ±1.5 runs)
        # Away team covers if they win or lose by less than 1.5
        # Home team covers if they win by more than 1.5
        score_diff = away_score - home_score
        away_rl_won = score_diff > -1.5  # Away covers if they lose by <1.5 or win
        home_rl_won = score_diff < 1.5  # Home covers if away loses by >1.5

        # Calculate price differences
        away_diff = greg_away_rl - vegas_away_rl
        home_diff = greg_home_rl - vegas_home_rl

        results['runline_differences'].append({
            'date': match['date'],
            'away_team': match['away_team'],
            'home_team': match['home_team'],
            'away_diff': away_diff,
            'home_diff': home_diff,
            'away_rl_won': away_rl_won,
            'home_rl_won': home_rl_won,
            'score_diff': score_diff,
            'greg_away_rl': greg_away_rl,
            'vegas_away_rl': vegas_away_rl,
            'greg_home_rl': greg_home_rl,
            'vegas_home_rl': vegas_home_rl,
        })

        # Analyze by price difference buckets
        if away_diff >= 10:  # Greg's away RL price is at least 10 points better
            bucket = f"+{(away_diff // 10) * 10}"
            results['away_runline'][bucket]['count'] += 1
            if away_rl_won:
                results['away_runline'][bucket]['wins'] += 1
            else:
                results['away_runline'][bucket]['losses'] += 1

        if home_diff >= 10:  # Greg's home RL price is at least 10 points better
            bucket = f"+{(home_diff // 10) * 10}"
            results['home_runline'][bucket]['count'] += 1
            if home_rl_won:
                results['home_runline'][bucket]['wins'] += 1
            else:
                results['home_runline'][bucket]['losses'] += 1

    # Print results
    print(f"\nTotal games analyzed: {len(results['runline_differences'])}")

    print(f"\n{'='*80}")
    print("AWAY TEAMS RUN LINE - Greg's Price Better Than Vegas")
    print(f"{'='*80}")
    print(f"{'Greg Edge':<15} {'Record':<15} {'Win %':<10} {'Avg Greg':<12} {'Avg Vegas':<12} {'Edge Value'}")
    print(f"{'-'*80}")

    for bucket in sorted(results['away_runline'].keys()):
        stats = results['away_runline'][bucket]
        win_pct = (stats['wins'] / stats['count'] * 100) if stats['count'] > 0 else 0
        record = f"{stats['wins']}-{stats['losses']}"

        # Calculate average prices for this bucket
        bucket_games = [g for g in results['runline_differences'] if f"+{(g['away_diff'] // 10) * 10}" == bucket and g['away_diff'] >= 10]
        avg_greg = sum(g['greg_away_rl'] for g in bucket_games) / len(bucket_games) if bucket_games else 0
        avg_vegas = sum(g['vegas_away_rl'] for g in bucket_games) / len(bucket_games) if bucket_games else 0
        edge_value = avg_greg - avg_vegas

        print(f"{bucket:<15} {record:<15} {win_pct:<10.1f}% {avg_greg:<12.0f} {avg_vegas:<12.0f} {edge_value:+.0f}")

    print(f"\n{'='*80}")
    print("HOME TEAMS RUN LINE - Greg's Price Better Than Vegas")
    print(f"{'='*80}")
    print(f"{'Greg Edge':<15} {'Record':<15} {'Win %':<10} {'Avg Greg':<12} {'Avg Vegas':<12} {'Edge Value'}")
    print(f"{'-'*80}")

    for bucket in sorted(results['home_runline'].keys()):
        stats = results['home_runline'][bucket]
        win_pct = (stats['wins'] / stats['count'] * 100) if stats['count'] > 0 else 0
        record = f"{stats['wins']}-{stats['losses']}"

        # Calculate average prices for this bucket
        bucket_games = [g for g in results['runline_differences'] if f"+{(g['home_diff'] // 10) * 10}" == bucket and g['home_diff'] >= 10]
        avg_greg = sum(g['greg_home_rl'] for g in bucket_games) / len(bucket_games) if bucket_games else 0
        avg_vegas = sum(g['vegas_home_rl'] for g in bucket_games) / len(bucket_games) if bucket_games else 0
        edge_value = avg_greg - avg_vegas

        print(f"{bucket:<15} {record:<15} {win_pct:<10.1f}% {avg_greg:<12.0f} {avg_vegas:<12.0f} {edge_value:+.0f}")

    return results


def print_summary_report(ml_results: Dict, totals_results: Dict, rl_results: Dict):
    """Print a clean summary of all edges found."""
    print(f"\n{'='*80}")
    print("SUMMARY: ALL BETTING EDGES FOUND")
    print(f"{'='*80}")

    all_edges = []

    # Collect moneyline edges
    for bucket, stats in ml_results['away_favorites'].items():
        win_pct = (stats['wins'] / stats['count'] * 100) if stats['count'] > 0 else 0
        if stats['count'] >= 5:  # Only show edges with 5+ games
            all_edges.append({
                'type': 'Away ML',
                'condition': f"Greg {bucket} better",
                'record': f"{stats['wins']}-{stats['count'] - stats['wins']}",
                'win_pct': win_pct,
                'count': stats['count']
            })

    for bucket, stats in ml_results['home_favorites'].items():
        win_pct = (stats['wins'] / stats['count'] * 100) if stats['count'] > 0 else 0
        if stats['count'] >= 5:
            all_edges.append({
                'type': 'Home ML',
                'condition': f"Greg {bucket} better",
                'record': f"{stats['wins']}-{stats['count'] - stats['wins']}",
                'win_pct': win_pct,
                'count': stats['count']
            })

    # Collect totals edges (Greg higher)
    for bucket, stats in totals_results['greg_higher'].items():
        over_pct = (stats['over'] / stats['count'] * 100) if stats['count'] > 0 else 0
        if stats['count'] >= 5:
            all_edges.append({
                'type': 'Total OVER',
                'condition': f"Greg +{bucket} runs",
                'record': f"{stats['over']}-{stats['under']}",
                'win_pct': over_pct,
                'count': stats['count']
            })

    # Collect totals edges (Greg lower - bet UNDER)
    for bucket, stats in totals_results['greg_lower'].items():
        under_pct = (stats['under'] / stats['count'] * 100) if stats['count'] > 0 else 0
        if stats['count'] >= 5:
            all_edges.append({
                'type': 'Total UNDER',
                'condition': f"Greg {bucket} runs",
                'record': f"{stats['under']}-{stats['over']}",
                'win_pct': under_pct,
                'count': stats['count']
            })

    # Collect run line edges
    for bucket, stats in rl_results['away_runline'].items():
        win_pct = (stats['wins'] / stats['count'] * 100) if stats['count'] > 0 else 0
        if stats['count'] >= 5:
            all_edges.append({
                'type': 'Away RL',
                'condition': f"Greg {bucket} better",
                'record': f"{stats['wins']}-{stats['losses']}",
                'win_pct': win_pct,
                'count': stats['count']
            })

    for bucket, stats in rl_results['home_runline'].items():
        win_pct = (stats['wins'] / stats['count'] * 100) if stats['count'] > 0 else 0
        if stats['count'] >= 5:
            all_edges.append({
                'type': 'Home RL',
                'condition': f"Greg {bucket} better",
                'record': f"{stats['wins']}-{stats['losses']}",
                'win_pct': win_pct,
                'count': stats['count']
            })

    # Sort by win percentage (descending)
    all_edges.sort(key=lambda x: x['win_pct'], reverse=True)

    # Print top edges
    print(f"\n{'Bet Type':<12} {'Condition':<25} {'Record':<12} {'Win %':<10} {'Games'}")
    print(f"{'-'*80}")

    for edge in all_edges:
        print(f"{edge['type']:<12} {edge['condition']:<25} {edge['record']:<12} {edge['win_pct']:<10.1f}% {edge['count']}")

    # Highlight best edges
    print(f"\n{'='*80}")
    print("TOP 5 BETTING EDGES (minimum 5 games)")
    print(f"{'='*80}")

    for i, edge in enumerate(all_edges[:5]):
        print(f"\n{i+1}. {edge['type']} - {edge['condition']}")
        print(f"   Record: {edge['record']} ({edge['win_pct']:.1f}% win rate)")
        print(f"   Sample size: {edge['count']} games")


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
        default=None,
        help='Optional: specific sheet name/date in Greg\'s file (e.g., "11/1/25"). If not specified, parses all sheets.'
    )

    args = parser.parse_args()

    print(f"{'='*80}")
    print("GREG'S MLB PRICES VS VEGAS CLOSING LINES")
    print(f"{'='*80}")

    # Parse Greg's sheet(s)
    print(f"\n{'='*80}")
    print("PARSING GREG'S MLB FILE")
    print(f"{'='*80}")
    print(f"File: {args.gregs_file}")

    greg_parser = GregsMLBParser(args.gregs_file)

    # Load and check sheets
    if not greg_parser.load_file():
        print("\nERROR: Failed to load Greg's Excel file!")
        print("This could mean:")
        print("  1. File doesn't exist")
        print("  2. File is corrupted")
        print("  3. Wrong file format")
        return

    print(f"\n✓ File loaded successfully")
    print(f"Available sheets: {greg_parser.excel_file.sheet_names[:15]}")
    if len(greg_parser.excel_file.sheet_names) > 15:
        print(f"... and {len(greg_parser.excel_file.sheet_names) - 15} more")

    if args.sheet_name:
        print(f"\nParsing specific sheet: {args.sheet_name}")
        greg_games = greg_parser.parse_all_sheets(specific_date=args.sheet_name)
    else:
        print(f"\nParsing ALL sheets ({len(greg_parser.excel_file.sheet_names)} total)...")
        greg_games = greg_parser.parse_all_sheets()

    print(f"\n{'='*80}")
    print(f"GREG'S PARSING RESULTS: {len(greg_games)} games")
    print(f"{'='*80}")

    # Show raw sample data to debug
    if greg_games:
        print("\nFirst 3 games (raw dict):")
        for i, game in enumerate(greg_games[:3]):
            print(f"\nGame {i+1} keys: {list(game.keys())}")
            print(f"  date: {game.get('date')} (type: {type(game.get('date'))})")
            print(f"  away_team: {game.get('away_team')}")
            print(f"  home_team: {game.get('home_team')}")
            print(f"  matchup: {game.get('matchup')}")
            print(f"  away_moneyline: {game.get('away_moneyline')}")
            print(f"  home_moneyline: {game.get('home_moneyline')}")
            print(f"  total: {game.get('total')}")
    else:
        print("\n❌ ERROR: Greg's parser returned 0 games!")
        print("Possible issues:")
        print("  1. No sheets had parseable dates (check sheet name format)")
        print("  2. Sheet structure doesn't match expected format")
        print("  3. All sheets were empty or had no valid data")
        return

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

    # Analyze run line edges
    rl_results = analyze_runline_edge(matches)

    # Print comprehensive summary
    print_summary_report(ml_results, totals_results, rl_results)

    print(f"\n{'='*80}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*80}")


if __name__ == '__main__':
    main()
