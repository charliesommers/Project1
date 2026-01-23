#!/usr/bin/env python3
"""
Save daily picks to a file - Can be synced to Dropbox/iCloud/Drive
"""
import os
from datetime import datetime
from pathlib import Path
from gregs_cbb_parser import GregsCBBParser
from vsin_scraper import VSINScraper
from odds_fetcher import OddsFetcher
from daily_picks_generator import DailyPicksGenerator


def save_picks(output_dir='daily_picks'):
    """
    Generate picks and save to timestamped file.

    Args:
        output_dir: Directory to save picks (default: daily_picks/)
    """
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)

    # Auto-fetch Greg's lines
    scraper = VSINScraper()

    if scraper.auto_update_check():
        file_path = scraper.fetch_daily_lines()
        if not file_path:
            file_path = scraper.get_latest_lines_path()
    else:
        file_path = scraper.get_latest_lines_path()

    if not file_path:
        error_msg = f"❌ {datetime.now()} - Could not get Greg's lines from VSIN\n"
        print(error_msg)

        # Save error log
        error_file = Path(output_dir) / 'error.log'
        with open(error_file, 'a') as f:
            f.write(error_msg)
        return None

    # Parse
    parser = GregsCBBParser(file_path)
    games = parser.parse_all_sheets()

    if not games:
        error_msg = f"❌ {datetime.now()} - No games found in file\n"
        print(error_msg)

        error_file = Path(output_dir) / 'error.log'
        with open(error_file, 'a') as f:
            f.write(error_msg)
        return None

    # Get odds
    fetcher = OddsFetcher()
    sportsbook_data = fetcher.fetch_ncaab_odds('bet365')

    if not sportsbook_data:
        error_msg = f"❌ {datetime.now()} - Could not fetch sportsbook odds\n"
        print(error_msg)

        error_file = Path(output_dir) / 'error.log'
        with open(error_file, 'a') as f:
            f.write(error_msg)
        return None

    # Generate picks
    generator = DailyPicksGenerator(under_threshold=5.0, over_threshold=3.0)
    picks = generator.generate_picks(games, sportsbook_data)

    # Format as text
    today = datetime.now()
    date_str = today.strftime('%B %d, %Y')
    file_date = today.strftime('%Y%m%d')

    if not picks:
        text = f"""
📅 {date_str} - CBB TOTALS PICKS

❌ No picks today (no edges meet criteria)

Strategy: UNDER ≥5 below | OVER ≥3 above
"""
    else:
        text = f"\n📅 {date_str} - CBB TOTALS PICKS\n\n"

        for i, pick in enumerate(picks, 1):
            conf_emoji = "🔥" if pick['confidence'] == 'high' else "✓"
            pick_emoji = "🔵" if pick['pick'] == 'UNDER' else "🔴"

            text += f"{conf_emoji} {pick_emoji} {pick['pick']} {pick['sportsbook_total']:.1f} - {pick['matchup']}\n"
            text += f"   Edge: {abs(pick['edge']):.1f} pts | Greg: {pick['gregs_total']:.1f} | Book: {pick['sportsbook_total']:.1f}\n"
            if i < len(picks):
                text += "\n"

        text += "\n" + "─"*60 + "\n"
        text += "🔥 = High confidence | ✓ = Good bet\n"
        text += "🔵 = Under | 🔴 = Over\n"
        text += "Strategy: UNDER ≥5 below | OVER ≥3 above\n"
        text += "─"*60 + "\n"

    # Save to file with date
    output_file = Path(output_dir) / f'picks_{file_date}.txt'
    with open(output_file, 'w') as f:
        f.write(text)

    # Also save as "latest.txt" for easy access
    latest_file = Path(output_dir) / 'latest.txt'
    with open(latest_file, 'w') as f:
        f.write(text)

    print(f"✅ Picks saved to:")
    print(f"   - {output_file}")
    print(f"   - {latest_file}")

    # Print to console
    print(text)

    return str(output_file)


if __name__ == '__main__':
    import sys

    output_dir = sys.argv[1] if len(sys.argv) > 1 else 'daily_picks'
    save_picks(output_dir)
