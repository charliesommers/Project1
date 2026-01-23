#!/usr/bin/env python3
"""
Email Greg's daily lines - Simple version without sportsbook comparison
Just shows Greg's handicapped lines for reference
"""
import os
import sys
import smtplib
import requests
from email.message import EmailMessage
from datetime import datetime
from gregs_cbb_parser import GregsCBBParser


# Greg's Google Sheets ID (from VSIN website)
GOOGLE_SHEETS_ID = "1RoqluBp1zE5HduO-QNb5pKIQen98pnIEUZz7CERsPgU"
GOOGLE_SHEETS_URL = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEETS_ID}/export?format=xlsx"


def download_gregs_sheet(output_path="data/gregs_lines_latest.xlsx"):
    """Download Greg's Google Sheet directly."""
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
    """Get Greg's lines as formatted text."""
    # Download Greg's Google Sheet
    file_path = download_gregs_sheet()

    if not file_path:
        return "❌ Could not download Greg's lines from Google Sheets"

    # Parse
    parser = GregsCBBParser(file_path)
    all_games = parser.parse_all_sheets()

    if not all_games:
        return "❌ No games found in Greg's sheet"

    # Get only the most recent date's games
    latest_date = max(game['date'] for game in all_games)
    games = [game for game in all_games if game['date'] == latest_date]

    print(f"Found {len(all_games)} total games, {len(games)} games for {latest_date.strftime('%B %d, %Y')}")

    # Format as text - just show Greg's lines
    text = f"\n📅 {datetime.now().strftime('%B %d, %Y')} - GREG'S CBB LINES\n\n"
    text += f"Total games: {len(games)}\n\n"

    # Group by confidence (if available) or just show all
    # Sort by total (over/under value)
    sorted_games = sorted(games, key=lambda x: x['total'], reverse=True)

    for i, game in enumerate(sorted_games[:20], 1):  # Show top 20
        spread_str = f"{game['spread']:+.1f}"

        text += f"{i}. {game['matchup']}\n"
        text += f"   Spread: {game['favorite']} {spread_str}\n"
        text += f"   Total: {game['total']:.1f}\n"

        if game.get('home_team'):
            text += f"   Home: {game['home_team']}\n"
        if game.get('neutral_court'):
            text += f"   Neutral Court\n"

        text += "\n"

    text += "─"*60 + "\n"
    text += f"📊 Greg's handicapped lines for reference\n"
    text += f"💡 Compare these to your sportsbook for betting edges\n"
    text += f"⬇️ UNDER when Greg is ≥5 below | ⬆️ OVER when Greg is ≥3 above\n"
    text += "─"*60 + "\n"

    return text


def send_email(to_email, subject, body, from_email=None, smtp_server=None, smtp_port=None, password=None):
    """Send email with picks."""
    # Get config from environment variables or parameters
    from_email = from_email or os.getenv('EMAIL_FROM')
    smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(smtp_port or os.getenv('SMTP_PORT', 587))
    password = password or os.getenv('EMAIL_PASSWORD')

    if not from_email or not password:
        print("Error: Email credentials not configured")
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
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                smtp.login(from_email, password)
                smtp.send_message(msg)
        else:
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
    to_email = os.getenv('EMAIL_TO')

    if len(sys.argv) > 1:
        to_email = sys.argv[1]

    if not to_email:
        print("Error: No recipient email specified")
        sys.exit(1)

    print(f"📧 Generating Greg's lines and sending to {to_email}...\n")

    # Get Greg's lines
    picks_text = get_picks_text()

    # Print to console
    print(picks_text)

    # Send email
    subject = f"Greg's CBB Lines - {datetime.now().strftime('%B %d, %Y')}"
    send_email(to_email, subject, picks_text)


if __name__ == '__main__':
    main()
