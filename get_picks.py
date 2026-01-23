#!/usr/bin/env python3
"""
Simple interface to get today's CBB picks
Just run it and get your picks!
"""
import sys
from datetime import datetime
from gregs_cbb_parser import GregsCBBParser
from vsin_scraper import VSINScraper
from odds_fetcher import OddsFetcher
from daily_picks_generator import DailyPicksGenerator


def get_picks(confidence_filter=None, top_n=None):
    """
    Get today's picks with minimal output.

    Args:
        confidence_filter: 'high', 'medium-high', or None for all
        top_n: Number of picks to show, or None for all

    Returns:
        List of picks
    """
    # Auto-fetch Greg's lines
    scraper = VSINScraper()

    if scraper.auto_update_check():
        print("Fetching latest lines from VSIN...")
        file_path = scraper.fetch_daily_lines()
        if not file_path:
            # Try to use latest available
            file_path = scraper.get_latest_lines_path()
            if not file_path:
                print("Error: Could not fetch Greg's lines")
                return []
    else:
        file_path = scraper.get_latest_lines_path()

    # Parse Greg's lines
    parser = GregsCBBParser(file_path)
    games = parser.parse_all_sheets()

    if not games:
        print("No games found")
        return []

    # Get sportsbook odds
    fetcher = OddsFetcher()
    sportsbook_data = fetcher.fetch_ncaab_odds('bet365')

    if not sportsbook_data:
        print("Warning: Could not fetch sportsbook odds")
        print("Make sure your API key is configured in .env file")
        return []

    # Generate picks
    generator = DailyPicksGenerator(under_threshold=5.0, over_threshold=3.0)
    picks = generator.generate_picks(games, sportsbook_data)

    # Filter if requested
    if confidence_filter:
        picks = generator.filter_picks(picks, confidence_level=confidence_filter)

    if top_n:
        picks = picks[:top_n]

    return picks


def print_picks_list(picks):
    """Print picks in a clean list format."""
    if not picks:
        print("\nNo picks today that meet the criteria.")
        return

    print(f"\n{'='*70}")
    print(f"TODAY'S CBB TOTALS PICKS - {datetime.now().strftime('%B %d, %Y')}")
    print(f"{'='*70}\n")

    for i, pick in enumerate(picks, 1):
        matchup = pick['matchup']
        pick_type = pick['pick']
        edge = pick['edge']
        gregs = pick['gregs_total']
        sb = pick['sportsbook_total']
        conf = pick['confidence'].upper()

        # Format the pick nicely
        print(f"{i}. {matchup}")
        print(f"   Pick: {pick_type} {sb}")
        print(f"   Edge: {abs(edge):.1f} pts (Greg: {gregs:.1f}, Book: {sb:.1f})")
        print(f"   Confidence: {conf}")
        print()

    print(f"{'='*70}")
    print(f"Strategy: UNDER when Greg ≥5 below | OVER when Greg ≥3 above")
    print(f"{'='*70}\n")


def main():
    """Main entry point."""
    print("\n🏀 Getting today's CBB totals picks...\n")

    # Check for arguments
    confidence = None
    top = None

    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['high', 'h']:
            confidence = 'high'
            print("Filtering for HIGH CONFIDENCE picks only\n")
        elif arg in ['top5', '5']:
            top = 5
            print("Showing TOP 5 picks\n")
        elif arg in ['top3', '3']:
            top = 3
            print("Showing TOP 3 picks\n")

    # Get picks
    picks = get_picks(confidence_filter=confidence, top_n=top)

    # Display
    print_picks_list(picks)


if __name__ == '__main__':
    main()
