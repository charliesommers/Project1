#!/usr/bin/env python3
"""
Email daily picks - Downloads from Google Sheets directly
Uses Greg's public Google Sheet instead of VSIN scraping
"""
import os
import sys
import requests
from datetime import datetime
from gregs_cbb_parser import GregsCBBParser
from odds_fetcher import OddsFetcher
from daily_picks_generator import DailyPicksGenerator


# Greg's Google Sheets ID (from VSIN website)
GOOGLE_SHEETS_ID = "1WcpH4nYnwXRLEWz8VCgVsVkzu2Y4-wueb1zGZf1KOlM"
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


def game_sort_time(value):
    """Sort valid tipoffs by instant, with unknown/invalid times last."""
    try:
        tipoff = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return tipoff.timestamp() if tipoff.tzinfo else float("inf")
    except (AttributeError, TypeError, ValueError):
        return float("inf")


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
                return "No current or upcoming games in Greg\'s sheet; no comparisons generated."

    # Get odds from ALL bookmakers in a SINGLE API request (saves credits!)
    fetcher = OddsFetcher()

    print("Fetching FanDuel odds only...")
    all_sportsbook_data = fetcher.fetch_ncaab_odds_all_bookmakers()

    # Get list of unique bookmakers found
    bookmakers_found = list(set(game['source_bookmaker'] for game in all_sportsbook_data if game.get('source_bookmaker')))

    if not all_sportsbook_data:
        print("No sportsbook odds available; listing every game as pending.")

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

    # Note: Pending games will show with TBD for game times
    # Team name matching between sources is too unreliable for consistent results
    if games_without_odds:
        print(f"\n{len(games_without_odds)} pending games (no odds yet) - times will show as TBD")

    # Rank spread discrepancies across all conferences.
    spread_picks = generator.generate_spread_picks(games, all_sportsbook_data)
    top_spread_picks = spread_picks[:10]  # Top 10 biggest discrepancies

    # Format as text
    text = f"\n📅 Games for {games[0]['date'].strftime('%B %d, %Y')}\n"
    text += "**FanDuel • Daily CBB Report**\n\n"
    text += f"{len(picks_with_odds)} games with odds\n"
    text += f"{len(games_without_odds)} pending\n"

    # Display TOP SPREAD EDGES (major conferences only)
    if top_spread_picks:
        text += "\n" + "─"*16 + "\n"
        text += "**🏀 TOP 10 SPREAD GAPS**\n"
        text += "─"*16 + "\n\n"

        for i, pick in enumerate(top_spread_picks, 1):
            # Format game time
            game_time_str = "TBD"
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

            # Use the pre-calculated recommended team and spread
            recommended_team = clean_team_name(pick['recommended_team'])
            recommended_spread = pick['recommended_spread']

            text += f"**{i}. {recommended_team} {recommended_spread:+.1f}**\n"
            text += f"{matchup_display}\n"
            text += f"{game_time_str} CT\n"
            text += f"**Gap: {pick['edge']:.1f} pts**\n"
            text += f"Greg: {pick['gregs_spread']:+.1f} | FanDuel: {pick['sportsbook_spread']:+.1f}\n\n"

        text += "─"*16 + "\n\n"

    text += "\n**📋 ALL GAMES · CENTRAL TIME**\n"
    if not all_sportsbook_data:
        text += "No sportsbook odds available; spread rankings unavailable.\n"
    text += "Unknown tipoff times appear last, alphabetically.\n\n"

    # Display ALL games (with and without odds) in chronological order
    # Create a combined list with pending games marked
    all_games_list = []

    # Add games with odds
    for pick in picks_with_odds:
        all_games_list.append({
            'type': 'with_odds',
            'data': pick,
            'sort_time': game_sort_time(pick.get('game_time')),
            'sort_team': pick.get('away_team', '').lower()
        })

    # Add games without odds (pending) - sort alphabetically at bottom (Bet365 style)
    for idx, game in enumerate(games_without_odds):
        # Put ALL pending games at the very bottom (after all timed games)
        # Sort alphabetically by away team

        # Determine away team for sorting
        home_team_name = game.get('home_team')
        favorite = game.get('favorite', '')
        underdog = game.get('underdog', '')

        # Figure out which is away based on who is home
        if home_team_name:
            if home_team_name.lower() == underdog.lower():
                away_team = favorite
            else:
                away_team = underdog
        else:
            away_team = favorite

        all_games_list.append({
            'type': 'pending',
            'data': game,
            'sort_time': float('inf'),  # All pending games at very end
            'sort_team': away_team.lower()  # Sort alphabetically by away team
        })

    # Sort combined list by time, then away team
    all_games_list.sort(key=lambda x: (x['sort_time'], x['sort_team']))

    for i, item in enumerate(all_games_list, 1):
        text += f"{i}. "
        if item['type'] == 'with_odds':
            pick = item['data']
            edge = abs(pick['edge'])

            # Determine emoji (no text, just emoji)
            emoji = ""
            if pick['pick'] == 'UNDER' and edge >= 5.0:
                emoji = "🔥 "
            elif pick['pick'] == 'OVER' and edge >= 1.0:
                emoji = "🔥 "
            elif pick['pick'] == 'UNDER' and edge >= 3.0:
                emoji = "⚠️  "
            elif pick['pick'] == 'OVER' and edge >= 3.0:
                emoji = "⚠️  "

            # Format game time
            game_time_str = "TBD"
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

            text += f"**{emoji}{pick['pick']} {pick['sportsbook_total']:.1f}**\n"
            text += f"{matchup_display} • {game_time_str}\n"
            text += f"Edge: {edge:.1f} | Greg: {pick['gregs_total']:.1f} | FanDuel: {pick['sportsbook_total']:.1f}\n"

        else:  # pending game
            game = item['data']

            # Use Greg's data for pending games
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
                # Neutral court - show as favorite vs underdog
                away = clean_team_name(favorite)
                home = clean_team_name(underdog)

            matchup_display = f"{away} @ {home}"

            text += f"⏳ PENDING\n"
            text += f"{matchup_display} • TBD\n"
            text += f"Greg's Total: {game['total']:.1f}\n"

        if i < len(all_games_list):
            text += "\n"

    text += "\n" + "─"*16 + "\n"
    text += "**🔥 Trigger met** · UNDER ≥5 above Greg | OVER ≥3 below Greg\n"
    text += "⚠️  Close (within 2 pts)\n"
    text += "─"*16 + "\n"

    return text


def send_email(*args, **kwargs):
    """Legacy email delivery is disabled."""
    raise RuntimeError("Pick emails are disabled; delivery is Discord only.")


def discord_chunks(text, limit=3800):
    """Keep each game together where possible; never truncate the report."""
    chunks, chunk = [], ""
    for paragraph in text.strip().split("\n\n"):
        for offset in range(0, max(1, len(paragraph)), limit):
            part = paragraph[offset:offset + limit]
            if chunk and len(chunk) + len(part) + 2 > limit:
                chunks.append(chunk)
                chunk = ""
            chunk += ("\n\n" if chunk else "") + part
    if chunk:
        chunks.append(chunk)
    return chunks


def send_discord(webhook_url, subject, body):
    """Publish readable blue cards directly in the channel."""
    import time
    parts = webhook_url.split()
    if not parts or len(set(parts)) != 1:
        print("Discord delivery failed: configure one webhook URL")
        return False
    webhook_url = parts[0]
    chunks = discord_chunks(body)
    for index, chunk in enumerate(chunks, 1):
        payload = {
            "allowed_mentions": {"parse": []},
            "embeds": [{
                "title": subject if index == 1 else f"All games · continued ({index}/{len(chunks)})",
                "description": chunk,
                "color": 0x168BDE,
                "footer": {"text": f"FanDuel only • Central Time • {index}/{len(chunks)}"}
            }]
        }
        for attempt in range(3):
            try:
                response = requests.post(webhook_url, params={"wait": "true"},
                                         json=payload, timeout=30)
                if response.status_code == 429 and attempt < 2:
                    delay = float(response.json().get("retry_after", 1))
                    time.sleep(min(max(delay, 0), 10))
                    continue
                if not response.ok:
                    print(f"Discord delivery failed (HTTP {response.status_code})")
                    return False
                break
            except (requests.RequestException, ValueError):
                print("Discord delivery failed: network or response error")
                return False
        if index < len(chunks):
            time.sleep(1)
    print("Discord report delivered")
    return True


def main():
    """Discord-only delivery; email credentials are never used."""
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")
    if not webhook_url:
        print("DISCORD_WEBHOOK_URL is required; email delivery is disabled.")
        sys.exit(1)
    picks_text = get_picks_text()
    print(picks_text)
    subject = f"CBB Picks · {datetime.now().strftime('%B %d, %Y')}"
    if not send_discord(webhook_url, subject, picks_text):
        sys.exit(1)


if __name__ == '__main__':
    main()
