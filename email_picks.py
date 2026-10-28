#!/usr/bin/env python3
"""
Email daily picks - Run this to get picks sent to your email
"""
import os
import sys
import smtplib
from email.message import EmailMessage
from datetime import datetime
from gregs_cbb_parser import GregsCBBParser
from vsin_scraper import VSINScraper
from odds_fetcher import OddsFetcher
from daily_picks_generator import DailyPicksGenerator


def get_picks_text():
    """Get picks as formatted text."""
    # Auto-fetch Greg's lines
    scraper = VSINScraper()

    if scraper.auto_update_check():
        file_path = scraper.fetch_daily_lines()
        if not file_path:
            file_path = scraper.get_latest_lines_path()
    else:
        file_path = scraper.get_latest_lines_path()

    if not file_path:
        return "❌ Could not get Greg's lines from VSIN"

    # Parse
    parser = GregsCBBParser(file_path)
    games = parser.parse_all_sheets()

    if not games:
        return "❌ No games found in file"

    # Get odds
    fetcher = OddsFetcher()
    sportsbook_data = fetcher.fetch_ncaab_odds('bet365')

    if not sportsbook_data:
        return "❌ Could not fetch sportsbook odds. Check API key."

    # Generate picks
    generator = DailyPicksGenerator(under_threshold=5.0, over_threshold=3.0)
    picks = generator.generate_picks(games, sportsbook_data)

    # Format as text
    if not picks:
        return f"""
📅 {datetime.now().strftime('%B %d, %Y')} - CBB TOTALS PICKS

❌ No picks today (no edges meet criteria)

Strategy: UNDER ≥5 below | OVER ≥3 above
"""

    text = f"\n📅 {datetime.now().strftime('%B %d, %Y')} - CBB TOTALS PICKS\n\n"

    for i, pick in enumerate(picks, 1):
        conf_emoji = "🔥" if pick['confidence'] == 'high' else "✓"
        pick_emoji = "⬇️" if pick['pick'] == 'UNDER' else "⬆️"

        text += f"{conf_emoji} {pick_emoji} {pick['pick']} {pick['sportsbook_total']:.1f} - {pick['matchup']}\n"
        text += f"   Edge: {abs(pick['edge']):.1f} pts | Greg: {pick['gregs_total']:.1f} | Book: {pick['sportsbook_total']:.1f}\n"
        if i < len(picks):
            text += "\n"

    text += "\n" + "─"*60 + "\n"
    text += "🔥 = High confidence | ✓ = Good bet\n"
    text += "⬇️ = Under | ⬆️ = Over\n"
    text += "Strategy: UNDER ≥5 below | OVER ≥3 above\n"
    text += "─"*60 + "\n"

    return text


def send_email(*args, **kwargs):
    """Email delivery has been disabled by the user."""
    raise RuntimeError("Pick emails are disabled; use Discord.")


def main():
    """Main entry point."""
    # Get email from environment or command line
    to_email = os.getenv('EMAIL_TO')

    if len(sys.argv) > 1:
        to_email = sys.argv[1]

    if not to_email:
        print("Error: No recipient email specified")
        print("\nUsage:")
        print("  python email_picks.py your@email.com")
        print("\nOr set EMAIL_TO in .env file")
        sys.exit(1)

    print(f"📧 Generating picks and sending to {to_email}...\n")

    # Get picks
    picks_text = get_picks_text()

    # Print to console
    print(picks_text)

    # Send email
    subject = f"CBB Picks - {datetime.now().strftime('%B %d, %Y')}"
    send_email(to_email, subject, picks_text)


if __name__ == '__main__':
    main()
