#!/usr/bin/env python3
"""
Sports Gambling Picker - Main CLI Interface
"""
import argparse
import sys
from pathlib import Path
import pandas as pd
from tabulate import tabulate
from colorama import Fore, Style, init

from data_parser import HandicappingDataParser
from picker_engine import PickerEngine

# Initialize colorama for cross-platform colored output
init(autoreset=True)


def print_banner():
    """Print application banner."""
    banner = """
    ╔═══════════════════════════════════════════════════════╗
    ║      SPORTS GAMBLING PICKER - Automated Analysis      ║
    ╚═══════════════════════════════════════════════════════╝
    """
    print(Fore.CYAN + banner)


def print_summary_stats(stats: dict):
    """Print summary statistics."""
    print(f"\n{Fore.YELLOW}{'='*60}")
    print(f"{Fore.YELLOW}Dataset Summary:")
    print(f"{Fore.YELLOW}{'='*60}")
    print(f"Total Picks: {stats['total_picks']}")
    print(f"Average Confidence: {stats['avg_confidence']:.1f}%")
    print(f"Average Edge: {stats['avg_edge']:.2f}%")
    print(f"Average Expected Value: {stats['avg_expected_value']:.2f}%")
    print(f"Positive EV Picks: {stats['positive_ev_picks']}")
    print(f"Sports: {', '.join(stats['sports'])}")


def print_recommendations_summary(summary: dict):
    """Print recommendations summary."""
    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"{Fore.GREEN}Recommendations Summary:")
    print(f"{Fore.GREEN}{'='*60}")
    print(f"Total Recommendations: {summary['total_recommendations']}")
    print(f"Average Confidence: {summary['avg_confidence']:.1f}%")
    print(f"Average Edge: {summary['avg_edge']:.2f}%")
    print(f"Average Expected Value: {summary['avg_expected_value']:.2f}%")
    print(f"Total Stake: {summary['total_stake']:.1f} units")
    print(f"Estimated ROI: {summary['potential_roi']:.2f}%")

    if summary.get('sports_breakdown'):
        print(f"\nSports Breakdown:")
        for sport, count in summary['sports_breakdown'].items():
            print(f"  {sport}: {count} picks")


def print_top_picks(picks, show_detailed=False):
    """Print top picks in a formatted table."""
    if len(picks) == 0:
        print(f"\n{Fore.RED}No picks match the specified criteria.")
        return

    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"{Fore.GREEN}Top Recommended Picks:")
    print(f"{Fore.GREEN}{'='*60}\n")

    # Prepare table data
    table_data = []
    for idx, (_, row) in enumerate(picks.iterrows(), 1):
        # Color code based on score
        score = row['Total_Score']
        if score >= 80:
            score_color = Fore.GREEN
        elif score >= 60:
            score_color = Fore.YELLOW
        else:
            score_color = Fore.WHITE

        # Format odds
        odds = row['Odds']
        if isinstance(odds, (int, float)):
            odds_str = f"{int(odds):+d}" if odds != int(odds) else f"{int(odds):+d}"
        else:
            odds_str = str(odds)

        row_data = [
            idx,
            row['Game'][:35] if len(str(row['Game'])) > 35 else row['Game'],
            row['Pick'][:20] if len(str(row['Pick'])) > 20 else row['Pick'],
            odds_str,
            f"{row['Confidence']:.0f}%",
            f"{row['Edge']:.1f}%",
            f"{score_color}{score:.1f}{Style.RESET_ALL}",
        ]

        if show_detailed:
            row_data.extend([
                f"{row['Expected_Value']:.1f}%",
                f"{row['Stake']:.1f}u"
            ])

        table_data.append(row_data)

    # Define headers
    headers = ['#', 'Game', 'Pick', 'Odds', 'Conf', 'Edge', 'Score']
    if show_detailed:
        headers.extend(['EV', 'Stake'])

    # Print table
    print(tabulate(table_data, headers=headers, tablefmt='grid'))

    # Print notes for top picks if available
    if 'Notes' in picks.columns and show_detailed:
        print(f"\n{Fore.CYAN}Notes:")
        for idx, (_, row) in enumerate(picks.head(5).iterrows(), 1):
            if pd.notna(row.get('Notes')) and str(row['Notes']).strip():
                print(f"{idx}. {row['Game']}: {row['Notes']}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Automatic Sports Gambling Picker - Analyze handicapping data and recommend picks',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s data/nfl_week1.xlsx
  %(prog)s data/nfl_week1.xlsx --top 5 --min-confidence 70
  %(prog)s data/nfl_week1.xlsx --min-edge 10 --sport NFL
  %(prog)s data/nfl_week1.xlsx --output results.xlsx
        """
    )

    parser.add_argument(
        'file',
        help='Path to Excel file with handicapping data'
    )

    parser.add_argument(
        '--top',
        type=int,
        default=10,
        help='Number of top picks to display (default: 10)'
    )

    parser.add_argument(
        '--min-confidence',
        type=float,
        default=0,
        help='Minimum confidence threshold 0-100 (default: 0)'
    )

    parser.add_argument(
        '--min-edge',
        type=float,
        default=-100,
        help='Minimum edge percentage (default: -100)'
    )

    parser.add_argument(
        '--min-ev',
        type=float,
        default=None,
        help='Minimum expected value percentage (default: None)'
    )

    parser.add_argument(
        '--sport',
        type=str,
        default=None,
        help='Filter by sport type (e.g., NFL, NBA, MLB)'
    )

    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Export results to Excel file'
    )

    parser.add_argument(
        '--detailed',
        action='store_true',
        help='Show detailed analysis including EV and stake'
    )

    parser.add_argument(
        '--no-summary',
        action='store_true',
        help='Skip summary statistics'
    )

    args = parser.parse_args()

    # Print banner
    print_banner()

    # Validate file exists
    if not Path(args.file).exists():
        print(f"{Fore.RED}Error: File not found: {args.file}")
        sys.exit(1)

    # Load and parse data
    print(f"Loading data from: {args.file}")
    parser = HandicappingDataParser(args.file)
    data = parser.load_data()
    print(f"{Fore.GREEN}✓ Loaded {len(data)} picks successfully")

    # Print summary stats
    if not args.no_summary:
        stats = parser.get_summary_stats()
        print_summary_stats(stats)

    # Initialize picker engine
    engine = PickerEngine(data)

    # Get top picks
    print(f"\n{Fore.CYAN}Analyzing picks...")
    top_picks = engine.get_top_picks(
        n=args.top,
        min_confidence=args.min_confidence,
        min_edge=args.min_edge,
        min_ev=args.min_ev,
        sport=args.sport
    )

    # Print recommendations summary
    if not args.no_summary:
        rec_summary = engine.get_recommendations_summary(top_picks)
        print_recommendations_summary(rec_summary)

    # Print top picks
    print_top_picks(top_picks, show_detailed=args.detailed)

    # Export if requested
    if args.output:
        engine.export_picks(top_picks, args.output)

    # Print closing message
    print(f"\n{Fore.CYAN}Analysis complete!")
    if len(top_picks) > 0:
        print(f"{Fore.GREEN}Good luck with your picks! 🎲")
    print()


if __name__ == '__main__':
    main()
