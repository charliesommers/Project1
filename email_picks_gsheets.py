#!/usr/bin/env python3
"""
Email daily picks - Downloads from Google Sheets directly
Uses Greg's public Google Sheet instead of VSIN scraping
"""
import os
import sys
import smtplib
import requests
from email.message import EmailMessage
from datetime import datetime
from gregs_cbb_parser import GregsCBBParser
from odds_fetcher import OddsFetcher
from daily_picks_generator import DailyPicksGenerator


# Greg's Google Sheets ID (from VSIN website)
GOOGLE_SHEETS_ID = "1RoqluBp1zE5HduO-QNb5pKIQen98pnIEUZz7CERsPgU"
GOOGLE_SHEETS_URL = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEETS_ID}/export?format=xlsx"


def download_gregs_sheet(output_path="data/gregs_lines_latest.xlsx"):
    """
    Download Greg's Google Sheet directly.

    Args:
        output_path: Where to save the downloaded file

    Returns:
        Path to downloaded file or None if failed
    """
    try:
        print(f"Downloading Greg's lines from Google Sheets...")

        # Create data directory if needed
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Download the file
        response = requests.get(GOOGLE_SHEETS_URL, timeout=30)
        response.raise_for_status()

        # Save to file
        with open(output_path, 'wb') as f:
            f.write(response.content)

        print(f"✓ Downloaded to {output_path}")
        return output_path

    except Exception as e:
        print(f"Error downloading Google Sheet: {e}")
        return None


def get_picks_text():
    """Get picks as formatted text."""
    # Download Greg's Google Sheet
    file_path = download_gregs_sheet()

    if not file_path:
        return "❌ Could not download Greg's lines from Google Sheets"

    # Parse
    parser = GregsCBBParser(file_path)
    all_games = parser.parse_all_sheets()

    if not all_games:
        return "❌ No games found in Greg's sheet"

    # Get today's games only
    from datetime import timedelta
    today = datetime.now().date()  # Just the date, not time
    tomorrow = today + timedelta(days=1)

    # Try today's games first
    todays_games = [game for game in all_games if game['date'].date() == today]

    if todays_games:
        games = todays_games
        print(f"Found {len(games)} games for TODAY ({today.strftime('%B %d, %Y')})")
    else:
        # If no games today, try tomorrow
        tomorrows_games = [game for game in all_games if game['date'].date() == tomorrow]
        if tomorrows_games:
            games = tomorrows_games
            print(f"No games today, found {len(games)} games for TOMORROW ({tomorrow.strftime('%B %d, %Y')})")
        else:
            # Fallback: get next available date
            future_games = [game for game in all_games if game['date'].date() >= today]
            if future_games:
                next_date = min(game['date'] for game in future_games).date()
                games = [game for game in all_games if game['date'].date() == next_date]
                print(f"No games today/tomorrow, found {len(games)} games for {next_date.strftime('%B %d, %Y')}")
            else:
                games = all_games[:10]  # Just show some games
                print(f"No future games found, showing sample of {len(games)} games")

    # Get odds
    fetcher = OddsFetcher()
    sportsbook_data = fetcher.fetch_ncaab_odds('bet365')

    # If no sportsbook odds available, show Greg's lines only
    if not sportsbook_data:
        print(f"ℹ️  No Bet365 odds available - showing Greg's lines only")
        text = f"\n📅 {datetime.now().strftime('%B %d, %Y')} - GREG'S CBB LINES\n\n"
        text += f"⚠️  No Bet365 odds available right now\n"
        text += f"Total games from Greg: {len(games)}\n\n"

        # Show top games sorted by total
        sorted_games = sorted(games, key=lambda x: x['total'], reverse=True)
        for i, game in enumerate(sorted_games[:15], 1):
            spread_str = f"{game['spread']:+.1f}"
            text += f"{i}. {game['matchup']}\n"
            text += f"   Spread: {game['favorite']} {spread_str}\n"
            text += f"   Total: {game['total']:.1f}\n\n"

        text += "─"*60 + "\n"
        text += "💡 Compare to your sportsbook when odds are posted\n"
        text += "⬇️ UNDER when Greg ≥5 below | ⬆️ OVER when Greg ≥3 above\n"
        text += "─"*60 + "\n"
        return text

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


def send_email(to_email, subject, body, from_email=None, smtp_server=None, smtp_port=None, password=None):
    """
    Send email with picks.

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body (plain text)
        from_email: Sender email (defaults to env var EMAIL_FROM)
        smtp_server: SMTP server (defaults to env var SMTP_SERVER or Gmail)
        smtp_port: SMTP port (defaults to env var SMTP_PORT or 587)
        password: Email password/app password (defaults to env var EMAIL_PASSWORD)
    """
    # Get config from environment variables or parameters
    from_email = from_email or os.getenv('EMAIL_FROM')
    smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(smtp_port or os.getenv('SMTP_PORT', 587))
    password = password or os.getenv('EMAIL_PASSWORD')

    if not from_email or not password:
        print("Error: Email credentials not configured")
        print("Set EMAIL_FROM and EMAIL_PASSWORD in .env file")
        print("\nExample .env:")
        print("EMAIL_FROM=your@gmail.com")
        print("EMAIL_PASSWORD=your_app_password")
        return False

    try:
        # Create message
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        msg.set_content(body)

        # Send email
        if smtp_port == 465:
            # SSL
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                smtp.login(from_email, password)
                smtp.send_message(msg)
        else:
            # TLS (default for most services)
            with smtplib.SMTP(smtp_server, smtp_port) as smtp:
                smtp.starttls()
                smtp.login(from_email, password)
                smtp.send_message(msg)

        print(f"✅ Email sent to {to_email}")
        return True

    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        return False


def main():
    """Main entry point."""
    # Get email from environment or command line
    to_email = os.getenv('EMAIL_TO')

    if len(sys.argv) > 1:
        to_email = sys.argv[1]

    if not to_email:
        print("Error: No recipient email specified")
        print("\nUsage:")
        print("  python email_picks_gsheets.py your@email.com")
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
