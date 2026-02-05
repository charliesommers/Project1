#!/usr/bin/env python3
"""
Test MLB team name matching to diagnose the issue.
"""
import os
import requests
from gregs_mlb_parser import GregsMLBParser
from datetime import datetime


def download_sheet():
    """Download Greg's MLB sheet."""
    url = "https://docs.google.com/spreadsheets/d/1QvkPvE8CtGabeYphECyMY2zYilPBkbOBeEL6mEwJTLs/export?format=xlsx"
    response = requests.get(url, timeout=30)

    file_path = 'data/gregs_mlb_latest.xlsx'
    os.makedirs('data', exist_ok=True)

    with open(file_path, 'wb') as f:
        f.write(response.content)

    return file_path


def get_espn_mlb_teams():
    """Get MLB teams from ESPN API."""
    url = "http://site.api.espn.com/apis/site/v2/sports/baseball/mlb/teams"
    response = requests.get(url, timeout=10)
    data = response.json()

    teams = []
    if 'sports' in data:
        for sport in data['sports']:
            for league in sport.get('leagues', []):
                for team in league.get('teams', []):
                    team_info = team.get('team', {})
                    teams.append({
                        'name': team_info.get('displayName'),
                        'location': team_info.get('location'),
                        'nickname': team_info.get('nickname'),
                        'abbreviation': team_info.get('abbreviation')
                    })

    return teams


def main():
    print("Testing MLB team name matching\n")
    print("=" * 70)

    # Download and parse Greg's sheet
    print("\n1. Downloading Greg's MLB sheet...")
    file_path = download_sheet()

    parser = GregsMLBParser(file_path)
    parser.load_file()

    # Get first sheet with data
    sheet_name = parser.excel_file.sheet_names[0]
    print(f"   Parsing sheet: {sheet_name}")

    games = parser.parse_sheet(sheet_name)
    print(f"   Found {len(games)} games from Greg")

    # Extract unique team names
    greg_teams = set()
    for game in games:
        if game.get('away_team'):
            greg_teams.add(game['away_team'])
        if game.get('home_team'):
            greg_teams.add(game['home_team'])

    print(f"\n2. Greg's team names ({len(greg_teams)}):")
    for team in sorted(greg_teams):
        print(f"   - {team}")

    # Get ESPN teams
    print(f"\n3. Fetching ESPN MLB teams...")
    espn_teams = get_espn_mlb_teams()
    print(f"   Found {len(espn_teams)} teams from ESPN")

    print(f"\n4. ESPN team formats:")
    for team in espn_teams[:5]:  # Show first 5 as examples
        print(f"   - {team['name']} ({team['abbreviation']})")
        print(f"     Location: {team['location']}, Nickname: {team['nickname']}")

    # Try to match
    print(f"\n5. Matching analysis:")
    print(f"   {'Greg Name':<20} {'Best ESPN Match':<30} {'Match Type'}")
    print(f"   {'-'*20} {'-'*30} {'-'*10}")

    for greg_team in sorted(greg_teams):
        best_match = None
        match_type = None

        greg_lower = greg_team.lower()

        for espn_team in espn_teams:
            # Try different matching strategies
            if espn_team['nickname'] and espn_team['nickname'].lower() == greg_lower:
                best_match = espn_team['name']
                match_type = "nickname"
                break
            elif espn_team['abbreviation'] and espn_team['abbreviation'].lower() == greg_lower:
                best_match = espn_team['name']
                match_type = "abbrev"
                break
            elif espn_team['name'] and greg_lower in espn_team['name'].lower():
                best_match = espn_team['name']
                match_type = "contains"
                break

        if best_match:
            print(f"   {greg_team:<20} {best_match:<30} {match_type}")
        else:
            print(f"   {greg_team:<20} {'NO MATCH':<30} {'---'}")

    print("\n" + "=" * 70)


if __name__ == '__main__':
    main()
