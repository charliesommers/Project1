#!/usr/bin/env python3
"""
Greg Peterson's CBB Totals Picker
Automated system for analyzing college basketball totals betting opportunities
"""
import argparse
import sys
from pathlib import Path
import pandas as pd
from tabulate import tabulate
from colorama import Fore, Style, init
from datetime import datetime

from gregs_cbb_parser import GregsCBBParser
from vsin_scraper import VSINScraper
from odds_fetcher import OddsFetcher
from scores_fetcher import ScoresFetcher
from performance_tracker import PerformanceTracker
from daily_picks_generator import DailyPicksGenerator

# Initialize colorama
init(autoreset=True)


def print_banner():
    """Print application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║   GREG PETERSON'S CBB TOTALS PICKER - Automated System   ║
    ║             Over/Under Analysis & Recommendations          ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(Fore.CYAN + banner)


def print_picks_table(picks: list):
    """Print picks in formatted table."""
    if not picks:
        print(f"\n{Fore.YELLOW}No picks meet the criteria today.")
        return

    print(f"\n{Fore.GREEN}{'='*80}")
    print(f"{Fore.GREEN}RECOMMENDED PICKS - TOTALS ONLY")
    print(f"{Fore.GREEN}{'='*80}\n")

    table_data = []
    for idx, pick in enumerate(picks, 1):
        # Color code by confidence
        conf = pick['confidence']
        if conf == 'high':
            conf_color = Fore.GREEN
        elif conf == 'medium-high':
            conf_color = Fore.YELLOW
        else:
            conf_color = Fore.WHITE

        # Color code pick
        pick_type = pick['pick']
        if pick_type == 'OVER':
            pick_color = Fore.RED
        else:
            pick_color = Fore.BLUE

        edge = pick['edge']
        edge_str = f"{edge:+.1f}"

        row = [
            idx,
            pick['matchup'][:40],
            f"{pick_color}{pick_type}{Style.RESET_ALL}",
            f"{pick['gregs_total']:.1f}",
            f"{pick['sportsbook_total']:.1f}",
            edge_str,
            f"{conf_color}{conf}{Style.RESET_ALL}"
        ]

        table_data.append(row)

    headers = ['#', 'Matchup', 'Pick', "Greg's", 'Sportsbook', 'Edge', 'Confidence']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))

    # Print strategy reminder
    print(f"\n{Fore.CYAN}Strategy:")
    print(f"  • UNDER: Greg's total is ≥5 points BELOW sportsbook")
    print(f"  • OVER: Greg's total is ≥3 points ABOVE sportsbook")


def cmd_daily_picks(args):
    """Generate daily picks."""
    print_banner()
    print(f"{Fore.CYAN}Generating daily picks...\n")

    # Auto-fetch from VSIN if needed
    file_path = args.file

    if args.auto_fetch:
        print(f"{Fore.CYAN}Checking for Greg's latest lines from VSIN...")
        scraper = VSINScraper()

        if scraper.auto_update_check():
            print(f"{Fore.YELLOW}Fetching latest lines from VSIN...")
            file_path = scraper.fetch_daily_lines()

            if not file_path:
                print(f"{Fore.RED}Failed to fetch from VSIN. Please provide file manually.")
                sys.exit(1)
        else:
            file_path = scraper.get_latest_lines_path()
            print(f"{Fore.GREEN}Using today's lines: {file_path}")

    if not file_path:
        print(f"{Fore.RED}Error: No file specified. Use --file or --auto-fetch")
        sys.exit(1)

    # Parse Greg's lines
    print(f"{Fore.CYAN}Parsing Greg's lines from: {file_path}")
    parser = GregsCBBParser(file_path)
    games = parser.parse_all_sheets(specific_date=args.date)

    if not games:
        print(f"{Fore.RED}No games found in file")
        sys.exit(1)

    print(f"{Fore.GREEN}✓ Loaded {len(games)} games")

    # Get sportsbook lines
    sportsbook_data = []

    if args.api_key or args.use_api:
        print(f"\n{Fore.CYAN}Fetching sportsbook lines from API...")
        fetcher = OddsFetcher(api_key=args.api_key)
        sportsbook_data = fetcher.fetch_ncaab_odds(bookmaker='bet365')

        if sportsbook_data:
            print(f"{Fore.GREEN}✓ Fetched {len(sportsbook_data)} games from API")
        else:
            print(f"{Fore.YELLOW}Warning: No API data. Use manual CSV if available.")

    elif args.manual_odds:
        print(f"\n{Fore.CYAN}Loading manual sportsbook lines from: {args.manual_odds}")
        # TODO: Load from CSV
        print(f"{Fore.YELLOW}Manual odds loading not yet implemented")

    if not sportsbook_data:
        print(f"\n{Fore.YELLOW}No sportsbook data available.")
        print(f"Options:")
        print(f"  1. Use --api-key YOUR_KEY to fetch from API")
        print(f"  2. Use --manual-odds file.csv with sportsbook lines")
        sys.exit(1)

    # Generate picks
    generator = DailyPicksGenerator(
        under_threshold=args.under_threshold,
        over_threshold=args.over_threshold
    )

    picks = generator.generate_picks(games, sportsbook_data)

    # Filter if requested
    if args.min_edge:
        picks = generator.filter_picks(picks, min_edge=args.min_edge)

    if args.confidence:
        picks = generator.filter_picks(picks, confidence_level=args.confidence)

    # Get summary
    summary = generator.get_picks_summary(picks)

    # Print summary
    print(f"\n{Fore.YELLOW}{'='*60}")
    print(f"{Fore.YELLOW}PICKS SUMMARY:")
    print(f"{Fore.YELLOW}{'='*60}")
    print(f"Total Picks: {summary['total_picks']}")
    print(f"Over Picks: {summary['over_picks']}")
    print(f"Under Picks: {summary['under_picks']}")
    print(f"High Confidence: {summary['high_confidence_picks']}")
    if summary['total_picks'] > 0:
        print(f"Average Edge: {summary['avg_edge']:.2f} points")
        print(f"Max Edge: {summary['max_edge']:.2f} points")

    # Print picks
    print_picks_table(picks[:args.top] if args.top else picks)

    # Export if requested
    if args.output:
        df = generator.get_picks_dataframe(picks)
        df.to_excel(args.output, index=False, engine='openpyxl')
        print(f"\n{Fore.GREEN}Picks exported to: {args.output}")

    print(f"\n{Fore.CYAN}Good luck! 🏀")


def cmd_performance(args):
    """Analyze historical performance."""
    print_banner()
    print(f"{Fore.CYAN}Analyzing historical performance...\n")

    # Parse Greg's lines
    print(f"{Fore.CYAN}Loading Greg's lines from: {args.file}")
    parser = GregsCBBParser(args.file)
    games = parser.parse_all_sheets()

    print(f"{Fore.GREEN}✓ Loaded {len(games)} games")

    # Get date range
    df_games = parser.get_games_dataframe()
    start_date = df_games['date'].min()
    end_date = df_games['date'].max()

    # Fetch scores
    print(f"\n{Fore.CYAN}Fetching game scores from {start_date.strftime('%m/%d/%Y')} to {end_date.strftime('%m/%d/%Y')}...")
    scores_fetcher = ScoresFetcher()
    scores = scores_fetcher.fetch_scores_range(start_date, end_date)

    print(f"{Fore.GREEN}✓ Fetched {len(scores)} completed games")

    # Analyze performance
    tracker = PerformanceTracker()
    results_df = tracker.analyze_all_games(games, scores)

    if len(results_df) == 0:
        print(f"\n{Fore.RED}No matching games found for analysis")
        sys.exit(1)

    print(f"{Fore.GREEN}✓ Matched {len(results_df)} games")

    # Get summary
    summary = tracker.get_performance_summary(results_df)

    # Print summary
    print(f"\n{Fore.YELLOW}{'='*60}")
    print(f"{Fore.YELLOW}GREG'S TOTALS PERFORMANCE:")
    print(f"{Fore.YELLOW}{'='*60}")
    print(f"Games Analyzed: {summary['total_games_analyzed']}")
    print(f"Overs: {summary['total_overs']}")
    print(f"Unders: {summary['total_unders']}")
    print(f"Pushes: {summary['total_pushes']}")
    print(f"Average Total Error: {summary['avg_total_error']:.2f} points")
    print(f"Date Range: {summary['date_range']}")

    # Export if requested
    if args.output:
        results_df.to_excel(args.output, index=False, engine='openpyxl')
        print(f"\n{Fore.GREEN}Results exported to: {args.output}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Greg Peterson CBB Totals Picker - Over/Under Analysis',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Daily picks command
    picks_parser = subparsers.add_parser('picks', help='Generate daily picks')
    picks_parser.add_argument('--file', help='Path to Greg\'s Excel file')
    picks_parser.add_argument('--auto-fetch', action='store_true', help='Auto-fetch from VSIN')
    picks_parser.add_argument('--date', help='Specific date sheet to analyze (e.g., 12226)')
    picks_parser.add_argument('--api-key', help='API key for odds service')
    picks_parser.add_argument('--use-api', action='store_true', help='Use API to fetch odds')
    picks_parser.add_argument('--manual-odds', help='CSV file with manual sportsbook odds')
    picks_parser.add_argument('--under-threshold', type=float, default=5.0,
                             help='Threshold for under bets (default: 5)')
    picks_parser.add_argument('--over-threshold', type=float, default=3.0,
                             help='Threshold for over bets (default: 3)')
    picks_parser.add_argument('--top', type=int, help='Show only top N picks')
    picks_parser.add_argument('--min-edge', type=float, help='Minimum edge threshold')
    picks_parser.add_argument('--confidence', choices=['high', 'medium-high', 'medium'],
                             help='Filter by confidence level')
    picks_parser.add_argument('--output', help='Export picks to Excel file')

    # Performance command
    perf_parser = subparsers.add_parser('performance', help='Analyze historical performance')
    perf_parser.add_argument('file', help='Path to Greg\'s Excel file')
    perf_parser.add_argument('--output', help='Export results to Excel file')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == 'picks':
        cmd_daily_picks(args)
    elif args.command == 'performance':
        cmd_performance(args)


if __name__ == '__main__':
    main()
