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


def clean_team_name(team_name: str) -> str:
    """Remove mascots from team names for cleaner display."""
    # Multi-word mascots first (longer patterns)
    mascots = [
        'blue devils', 'crimson tide', 'fighting irish', 'golden eagles', 'golden gophers',
        'nittany lions', 'ragin cajuns', 'red flash', 'red raiders', 'red storm',
        'river hawks', 'sun devils', 'tar heels', 'green wave',
        # Single-word mascots
        'aggies', 'aztecs', 'badgers', 'bears', 'bearcats', 'beavers', 'bengals',
        'bobcats', 'broncos', 'bruins', 'buccaneers', 'buckeyes', 'buffalo',
        'bulldogs', 'cardinals', 'chanticleers', 'cougars', 'cowboys', 'crusaders',
        'cyclones', 'demons', 'deacons', 'ducks', 'eagles', 'falcons', 'gators', 'grizzlies',
        'hawkeyes', 'hilltoppers', 'hokies', 'hornets', 'huskies', 'hurricanes',
        'jayhawks', 'jaguars', 'knights', 'lancers', 'lions', 'lobos', 'miners', 'mountaineers',
        'musketeers', 'orangemen', 'orange', 'owls', 'panthers', 'pirates', 'ramblers', 'rams',
        'razorbacks', 'rebels', 'salukis', 'seminoles', 'sharks', 'skyhawks',
        'sooners', 'spartans', 'terrapins', 'terriers', 'tigers', 'titans', 'trojans', 'utes',
        'volunteers', 'wildcats', 'wolverines', 'wolfpack', 'wave'
    ]

    name = team_name.strip()
    name_lower = name.lower()

    # First pass: Remove mascots at the end
    for mascot in mascots:
        # Pattern: "Team Mascot" -> "Team"
        if name_lower.endswith(' ' + mascot):
            name = name[:-(len(mascot) + 1)].strip()
            name_lower = name.lower()
            break

    # Second pass: Remove mascots in parentheses or after "the"
    for mascot in mascots:
        # Pattern: "Team (Mascot)"
        if f' ({mascot})' in name_lower:
            idx = name_lower.find(f' ({mascot})')
            name = name[:idx].strip()
            name_lower = name.lower()
            break
        # Pattern: "The Mascot"
        if name_lower.startswith('the ' + mascot):
            # This is just a mascot with no team name, keep original
            break

    return name


def get_picks_text():
    """Get picks as formatted text."""
    # Download Greg's Google Sheet
    file_path = download_gregs_sheet()

    if not file_path:
        return "❌ Could not download Greg's lines from Google Sheets"

    # Parse
    parser = GregsCBBParser(file_path)
    parser.load_file()

    print(f"DEBUG - Sheet names in Greg's file: {parser.excel_file.sheet_names}")

    all_games = parser.parse_all_sheets()

    if not all_games:
        return "❌ No games found in Greg's sheet"

    print(f"DEBUG - Total games parsed from all sheets: {len(all_games)}")

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

    # Get odds from ALL bookmakers in a SINGLE API request (saves credits!)
    fetcher = OddsFetcher()

    print(f"Fetching odds from ALL bookmakers in single API request...")
    all_sportsbook_data = fetcher.fetch_ncaab_odds_all_bookmakers()

    # Get list of unique bookmakers found
    bookmakers_found = list(set(game['source_bookmaker'] for game in all_sportsbook_data if game.get('source_bookmaker')))

    if not all_sportsbook_data:
        print(f"ℹ️  No sportsbook odds available from any source")
        text = f"\n📅 {datetime.now().strftime('%B %d, %Y')} - GREG'S CBB LINES\n\n"
        text += f"⚠️  No sportsbook odds available right now\n"
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

    print(f"✓ Total combined: {len(all_sportsbook_data)} games from {len(bookmakers_found)} bookmakers")

    # Debug: Show what we're trying to match
    print(f"\nDEBUG - Greg's games ({len(games)}):")
    for game in games[:5]:
        print(f"  {game['matchup']}")

    print(f"\nDEBUG - Sportsbook games ({len(all_sportsbook_data)}):")
    for game in all_sportsbook_data[:5]:
        home = game.get('home_team', '')
        away = game.get('away_team', '')
        print(f"  {away} @ {home}")

    # Generate picks for games WITH odds
    generator = DailyPicksGenerator(under_threshold=5.0, over_threshold=3.0)
    picks_with_odds = generator.generate_picks(games, all_sportsbook_data)

    # Sort by game time first, then alphabetically by away team (Bet365 style)
    if picks_with_odds:
        # Sort by: 1) game time, 2) away team alphabetically
        picks_with_odds.sort(key=lambda x: (
            x.get('game_time', 'ZZZ'),  # Primary: time
            x.get('away_team', '').lower()  # Secondary: away team alphabetically
        ))

    # Separate top picks (flame emoji worthy)
    top_picks = []
    for pick in picks_with_odds:
        edge = abs(pick['edge'])
        if (pick['pick'] == 'UNDER' and edge >= 5.0) or (pick['pick'] == 'OVER' and edge >= 3.0):
            top_picks.append(pick)

    # Find games WITHOUT odds
    games_with_picks = set(pick['matchup'] for pick in picks_with_odds)
    games_without_odds = [game for game in games if game['matchup'] not in games_with_picks]

    print(f"\nMATCHING RESULTS:")
    print(f"✓ Games with odds: {len(picks_with_odds)}")
    print(f"✗ Games without odds: {len(games_without_odds)}")

    if games_without_odds:
        print(f"\nGames that didn't match:")
        for game in games_without_odds[:10]:
            print(f"  - {game['matchup']}")

    # Try to get game times from ESPN for pending games
    if games_without_odds:
        print(f"\nFetching game schedule from ESPN for {len(games_without_odds)} pending games...")
        try:
            from scores_fetcher import ScoresFetcher
            espn_fetcher = ScoresFetcher()

            # Get unique dates from pending games
            pending_dates = set(game['date'].date() for game in games_without_odds)

            # Fetch ESPN schedule for each date
            espn_schedule = []
            for game_date in pending_dates:
                print(f"  Fetching ESPN schedule for {game_date.strftime('%Y-%m-%d')}...")
                schedule = espn_fetcher.fetch_schedule_from_espn(datetime.combine(game_date, datetime.min.time()))
                espn_schedule.extend(schedule)
                print(f"    Found {len(schedule)} games on ESPN for this date")

            print(f"✓ Total ESPN games fetched: {len(espn_schedule)}")

            if len(espn_schedule) == 0:
                print("  ⚠️  ESPN returned no games - times will show as TBD")

            # Try to match pending games with ESPN schedule to get game times and home/away teams
            matched_count = 0
            for game in games_without_odds:
                espn_game = espn_fetcher.match_game(game, espn_schedule)
                if espn_game:
                    game['espn_time'] = espn_game.get('commence_time')
                    game['espn_home'] = espn_game.get('home_team')
                    game['espn_away'] = espn_game.get('away_team')
                    matched_count += 1
                    print(f"  ✓ Found time for {game['matchup']}: {espn_game.get('commence_time')}")
                else:
                    print(f"  ✗ No ESPN match for {game['matchup']}")

            print(f"\nESPN matching summary: {matched_count}/{len(games_without_odds)} pending games matched")

        except Exception as e:
            print(f"Warning: Could not fetch ESPN schedule: {e}")
            # Continue without ESPN times

    # Generate top spread edges for major conferences
    major_conferences = ['ACC', 'Big 12', 'Big Ten', 'SEC', 'Big East']
    spread_picks = generator.generate_spread_picks(games, all_sportsbook_data, major_conferences)
    top_spread_picks = spread_picks[:5]  # Top 5 biggest edges

    # Format as text
    text = f"\n📅 {datetime.now().strftime('%B %d, %Y')}\n"
    text += f"CBB TOTALS PICKS\n\n"
    text += f"{len(picks_with_odds)} games with odds\n"
    text += f"{len(games_without_odds)} pending\n"

    # Display TOP SPREAD EDGES (major conferences only)
    if top_spread_picks:
        text += "\n" + "="*50 + "\n"
        text += "🏀 TOP SPREAD EDGES (Major Conferences)\n"
        text += "="*50 + "\n\n"

        for i, pick in enumerate(top_spread_picks, 1):
            # Format game time
            game_time_str = ""
            if pick.get('game_time'):
                try:
                    import pytz
                    game_time_utc = datetime.fromisoformat(pick['game_time'].replace('Z', '+00:00'))
                    central = pytz.timezone('America/Chicago')
                    game_time_cst = game_time_utc.astimezone(central)
                    game_time_str = game_time_cst.strftime('%I:%M %p')
                except:
                    game_time_str = "TBD"
            else:
                game_time_str = "TBD"

            # Format as "Away @ Home" with clean names
            away = clean_team_name(pick.get('away_team', ''))
            home = clean_team_name(pick.get('home_team', ''))
            if away and home:
                matchup_display = f"{away} @ {home}"
            else:
                matchup_display = pick['matchup']

            # Determine which team Greg is betting on
            # If Greg's spread is MORE negative, he favors the FAVORITE more
            # If Greg's spread is LESS negative, he favors the UNDERDOG
            favorite = clean_team_name(pick['favorite'])
            underdog = clean_team_name(pick['underdog'])

            if pick['gregs_spread'] < pick['sportsbook_spread']:
                # Greg's line is more negative = bet FAVORITE
                greg_pick = f"BET {favorite}"
            else:
                # Greg's line is less negative = bet UNDERDOG
                greg_pick = f"BET {underdog}"

            text += f"{i}. {greg_pick}\n"
            text += f"{matchup_display} ({pick['conference']})\n"
            text += f"{game_time_str} CST\n"
            text += f"Edge: {pick['edge']:.1f} pts\n"
            text += f"Greg: {pick['gregs_spread']:+.1f} | Book: {pick['sportsbook_spread']:+.1f}\n\n"

        text += "="*50 + "\n\n"

    # Display ALL games (with and without odds) in chronological order
    # Create a combined list with pending games marked
    all_games_list = []

    # Add games with odds
    for pick in picks_with_odds:
        all_games_list.append({
            'type': 'with_odds',
            'data': pick,
            'sort_time': pick.get('game_time', 'ZZZ'),
            'sort_team': pick.get('away_team', '').lower()
        })

    # Add games without odds (pending) - sorted by date/time
    for game in games_without_odds:
        # Try to use ESPN time if available, otherwise use date
        espn_time = game.get('espn_time')
        if espn_time:
            # Use actual game time from ESPN
            sort_time = espn_time
        else:
            # Use date from game to create sort key that puts pending games
            # after timed games on the same date (using 23:59:59)
            game_date = game.get('date')
            if game_date:
                # Create ISO timestamp for end of day to sort after actual game times
                sort_time = game_date.strftime('%Y-%m-%dT23:59:59Z')
            else:
                sort_time = 'ZZZZ'

        all_games_list.append({
            'type': 'pending',
            'data': game,
            'sort_time': sort_time,
            'sort_team': game['favorite'].lower()  # Sort by favorite team alphabetically
        })

    # Sort combined list by time, then away team
    all_games_list.sort(key=lambda x: (x['sort_time'], x['sort_team']))

    for i, item in enumerate(all_games_list, 1):
        if item['type'] == 'with_odds':
            pick = item['data']
            edge = abs(pick['edge'])

            # Determine emoji (no text, just emoji)
            emoji = ""
            if pick['pick'] == 'UNDER' and edge >= 5.0:
                emoji = "🔥 "
            elif pick['pick'] == 'OVER' and edge >= 3.0:
                emoji = "🔥 "
            elif pick['pick'] == 'UNDER' and edge >= 3.0:
                emoji = "⚠️  "
            elif pick['pick'] == 'OVER' and edge >= 1.0:
                emoji = "⚠️  "

            # Format game time
            game_time_str = ""
            if pick.get('game_time'):
                try:
                    import pytz
                    # Parse ISO format time
                    game_time_utc = datetime.fromisoformat(pick['game_time'].replace('Z', '+00:00'))
                    # Convert to Central Time
                    central = pytz.timezone('America/Chicago')
                    game_time_cst = game_time_utc.astimezone(central)
                    game_time_str = game_time_cst.strftime('%I:%M %p')
                except:
                    game_time_str = "TBD"

            # Format as "Away @ Home" with clean names
            away = clean_team_name(pick.get('away_team', ''))
            home = clean_team_name(pick.get('home_team', ''))
            if away and home:
                matchup_display = f"{away} @ {home}"
            else:
                matchup_display = pick['matchup']

            text += f"{emoji}{pick['pick']} {pick['sportsbook_total']:.1f}\n"
            text += f"{matchup_display} • {game_time_str}\n"
            text += f"Edge: {edge:.1f} | Greg: {pick['gregs_total']:.1f} | Book: {pick['sportsbook_total']:.1f}\n"

        else:  # pending game
            game = item['data']

            # Determine away/home teams
            # Priority: 1) ESPN data (most accurate), 2) Greg's home_team field
            espn_away = game.get('espn_away')
            espn_home = game.get('espn_home')

            if espn_away and espn_home:
                # Use ESPN's home/away determination (most reliable)
                away = clean_team_name(espn_away)
                home = clean_team_name(espn_home)
            else:
                # Fall back to Greg's data
                # In Greg's format: home_team field tells us which team is home
                home_team_name = game.get('home_team')
                favorite = game['favorite']
                underdog = game['underdog']

                if home_team_name:
                    # Determine which is away based on who is home
                    if home_team_name.lower() == underdog.lower():
                        away = clean_team_name(favorite)
                        home = clean_team_name(underdog)
                    else:
                        away = clean_team_name(underdog)
                        home = clean_team_name(favorite)
                else:
                    # Neutral court - show as favorite @ underdog
                    away = clean_team_name(favorite)
                    home = clean_team_name(underdog)

            # Format game time if available from ESPN
            game_time_str = "TBD"
            espn_time = game.get('espn_time')
            if espn_time:
                try:
                    import pytz
                    # Handle both string and datetime objects
                    if isinstance(espn_time, str):
                        game_time_utc = datetime.fromisoformat(espn_time.replace('Z', '+00:00'))
                    else:
                        game_time_utc = espn_time

                    central = pytz.timezone('America/Chicago')
                    game_time_cst = game_time_utc.astimezone(central)
                    game_time_str = game_time_cst.strftime('%I:%M %p')
                except Exception as e:
                    print(f"Warning: Failed to parse ESPN time for {game.get('matchup')}: {e}")
                    game_time_str = "TBD"

            matchup_display = f"{away} @ {home}"

            text += f"⏳ PENDING\n"
            text += f"{matchup_display} • {game_time_str}\n"
            text += f"Greg's Total: {game['total']:.1f}\n"

        if i < len(all_games_list):
            text += "\n"

    text += "\n" + "-"*50 + "\n"
    text += "🔥 Strong bet (UNDER ≥5 | OVER ≥3)\n"
    text += "⚠️  Close (within 2 pts)\n"
    text += "-"*50 + "\n"

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
