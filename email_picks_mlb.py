#!/usr/bin/env python3
"""
Email daily MLB picks - Downloads from Google Sheets
Uses Greg's public Google Sheet for MLB totals
"""
import os
import sys
import smtplib
import requests
from email.message import EmailMessage
from datetime import datetime, timedelta
from gregs_mlb_parser import GregsMLBParser
from odds_fetcher import OddsFetcher


# Greg's MLB Google Sheets ID
GOOGLE_SHEETS_ID = "1QvkPvE8CtGabeYphECyMY2zYilPBkbOBeEL6mEwJTLs"
GOOGLE_SHEETS_URL = f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEETS_ID}/export?format=xlsx"


def download_gregs_sheet(output_path="data/gregs_mlb_latest.xlsx"):
    """Download Greg's MLB Google Sheet."""
    try:
        print(f"Downloading Greg's MLB totals from Google Sheets...")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        response = requests.get(GOOGLE_SHEETS_URL, timeout=30)
        response.raise_for_status()
        with open(output_path, 'wb') as f:
            f.write(response.content)
        print(f"✓ Downloaded to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error downloading Google Sheet: {e}")
        return None


def clean_team_name(team_name: str) -> str:
    """Remove extra text from team names."""
    # Remove common suffixes
    team_name = team_name.replace(' Baseball', '')
    team_name = team_name.replace(' MLB', '')
    return team_name.strip()


def get_picks_text():
    """Get MLB picks as formatted text."""
    file_path = download_gregs_sheet()
    if not file_path:
        return "❌ Could not download Greg's MLB totals from Google Sheets"

    # Parse
    parser = GregsMLBParser(file_path)
    parser.load_file()
    all_games = parser.parse_all_sheets()

    if not all_games:
        return "❌ No games found in Greg's MLB sheet"

    print(f"✓ Total games parsed: {len(all_games)}")

    # Get today's games
    today = datetime.now().date()
    tomorrow = today + timedelta(days=1)

    todays_games = [game for game in all_games if game['date'].date() == today]

    if todays_games:
        games = todays_games
        print(f"Found {len(games)} games for TODAY ({today.strftime('%B %d, %Y')})")
    else:
        tomorrows_games = [game for game in all_games if game['date'].date() == tomorrow]
        if tomorrows_games:
            games = tomorrows_games
            print(f"No games today, found {len(games)} games for TOMORROW ({tomorrow.strftime('%B %d, %Y')})")
        else:
            future_games = [game for game in all_games if game['date'].date() >= today]
            if future_games:
                next_date = min(game['date'] for game in future_games).date()
                games = [game for game in all_games if game['date'].date() == next_date]
                print(f"Found {len(games)} games for {next_date.strftime('%B %d, %Y')}")
            else:
                games = all_games[:10]
                print(f"Showing sample of {len(games)} games")

    print(f"\nGreg's games for the day:")
    for game in games:
        print(f"  {game['matchup']}")

    # Get odds from The Odds API
    fetcher = OddsFetcher()
    print(f"\nFetching MLB odds from The Odds API...")

    # Fetch MLB odds
    endpoint = f"{fetcher.base_url}/sports/baseball_mlb/odds"
    params = {
        'apiKey': fetcher.api_key,
        'regions': 'us',
        'markets': 'h2h,spreads,totals',
        'oddsFormat': 'american'
    }

    try:
        response = requests.get(endpoint, params=params, timeout=30)
        response.raise_for_status()
        mlb_games = response.json()

        all_sportsbook_data = []
        for game in mlb_games:
            home_team = game.get('home_team', '')
            away_team = game.get('away_team', '')
            commence_time = game.get('commence_time', '')

            bookmakers_data = game.get('bookmakers', [])
            for bookmaker_info in bookmakers_data:
                bookmaker_name = bookmaker_info.get('key', '')
                markets = bookmaker_info.get('markets', [])

                total = None
                spread = None

                for market in markets:
                    if market.get('key') == 'totals':
                        outcomes = market.get('outcomes', [])
                        if outcomes:
                            total = outcomes[0].get('point')
                    elif market.get('key') == 'spreads':
                        outcomes = market.get('outcomes', [])
                        for outcome in outcomes:
                            if outcome.get('name') == home_team:
                                spread = outcome.get('point')
                                break

                if total or spread:
                    all_sportsbook_data.append({
                        'home_team': home_team,
                        'away_team': away_team,
                        'commence_time': commence_time,
                        'total': total,
                        'spread': spread,
                        'source_bookmaker': bookmaker_name
                    })

        print(f"✓ Fetched {len(all_sportsbook_data)} MLB game-bookmaker combinations")

    except Exception as e:
        print(f"Error fetching MLB odds: {e}")
        all_sportsbook_data = []

    if not all_sportsbook_data:
        return "⚠️  No MLB sportsbook odds available right now"

    # Match and generate picks
    from daily_picks_generator import DailyPicksGenerator
    generator = DailyPicksGenerator(under_threshold=5.0, over_threshold=3.0)

    picks_with_odds = []
    games_without_odds = []

    for gregs_game in games:
        matched = False
        for sb_game in all_sportsbook_data:
            # Simple team matching
            if (gregs_game['away_team'].lower() in sb_game['away_team'].lower() or
                sb_game['away_team'].lower() in gregs_game['away_team'].lower()) and \
               (gregs_game['home_team'].lower() in sb_game['home_team'].lower() or
                sb_game['home_team'].lower() in gregs_game['home_team'].lower()):

                gregs_total = gregs_game['total']
                sportsbook_total = sb_game.get('total')

                if not sportsbook_total:
                    continue

                difference = gregs_total - sportsbook_total

                if difference <= -generator.under_threshold:
                    pick = 'UNDER'
                elif difference >= generator.over_threshold:
                    pick = 'OVER'
                else:
                    pick = None

                if pick:
                    picks_with_odds.append({
                        'matchup': gregs_game['matchup'],
                        'away_team': sb_game['away_team'],
                        'home_team': sb_game['home_team'],
                        'pick': pick,
                        'gregs_total': gregs_total,
                        'sportsbook_total': sportsbook_total,
                        'edge': abs(difference),
                        'game_time': sb_game.get('commence_time', ''),
                        'bookmaker': sb_game.get('source_bookmaker', '')
                    })
                    matched = True
                    break

        if not matched:
            games_without_odds.append(gregs_game)

    # Sort by game time
    picks_with_odds.sort(key=lambda x: x.get('game_time', 'ZZZ'))

    # Format email
    text = f"\n⚾ {datetime.now().strftime('%B %d, %Y')}\n"
    text += f"MLB TOTALS PICKS\n\n"
    text += f"{len(picks_with_odds)} games with odds\n"
    text += f"{len(games_without_odds)} pending\n\n"

    text += "=" * 50 + "\n"
    text += "PICKS\n"
    text += "=" * 50 + "\n\n"

    for i, pick in enumerate(picks_with_odds, 1):
        import pytz
        game_time_str = "TBD"
        if pick.get('game_time'):
            try:
                game_time_utc = datetime.fromisoformat(pick['game_time'].replace('Z', '+00:00'))
                central = pytz.timezone('America/Chicago')
                game_time_cst = game_time_utc.astimezone(central)
                game_time_str = game_time_cst.strftime('%I:%M %p')
            except:
                pass

        away = clean_team_name(pick['away_team'])
        home = clean_team_name(pick['home_team'])

        flame = "🔥 " if abs(pick['edge']) >= 5 else ""

        text += f"{i}. {flame}{pick['pick']} {pick['sportsbook_total']:.1f}\n"
        text += f"{away} @ {home}\n"
        text += f"{game_time_str} CST\n"
        text += f"Greg: {pick['gregs_total']:.1f} | Book: {pick['sportsbook_total']:.1f} | Edge: {pick['edge']:.1f}\n\n"

    if games_without_odds:
        text += "\n" + "=" * 50 + "\n"
        text += "PENDING (No odds yet)\n"
        text += "=" * 50 + "\n\n"

        for game in games_without_odds:
            away = clean_team_name(game['away_team'])
            home = clean_team_name(game['home_team'])
            text += f"⏳ {away} @ {home}\n"
            text += f"Greg's Total: {game['total']:.1f}\n\n"

    text += "-" * 50 + "\n"
    text += "🔥 Strong bet (edge ≥5)\n"
    text += "⬇️ UNDER when Greg ≥5 below | ⬆️ OVER when Greg ≥3 above\n"
    text += "-" * 50 + "\n"

    return text


def send_email(to_email, subject, body, from_email=None, smtp_server=None, smtp_port=None, password=None):
    """Send email with picks."""
    from_email = from_email or os.getenv('EMAIL_FROM')
    password = password or os.getenv('EMAIL_PASSWORD')
    smtp_server = smtp_server or os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(smtp_port or os.getenv('SMTP_PORT', 587))

    if not from_email or not password:
        raise ValueError("Email credentials not configured")

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email
    msg.set_content(body)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(from_email, password)
        server.send_message(msg)


if __name__ == '__main__':
    to_email = sys.argv[1] if len(sys.argv) > 1 else os.getenv('EMAIL_TO')

    if not to_email:
        print("Error: No recipient email specified")
        sys.exit(1)

    print(f"📧 Generating MLB picks and sending to {to_email}...\n")

    picks_text = get_picks_text()
    print(f"\n{picks_text}")

    try:
        send_email(
            to_email=to_email,
            subject=f"⚾ MLB Totals Picks - {datetime.now().strftime('%B %d')}",
            body=picks_text
        )
        print(f"\n✅ Email sent successfully to {to_email}")
    except Exception as e:
        print(f"\n❌ Failed to send email: {e}")
        sys.exit(1)
