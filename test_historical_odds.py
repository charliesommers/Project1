#!/usr/bin/env python3
"""
Test script to find free sources of historical CBB betting lines.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def test_covers():
    """Test if Covers.com has accessible historical data."""
    print("Testing Covers.com...")

    # Try to fetch a recent date's odds
    # Covers uses format: /sports/basketball/ncaab/matchups?selectedDate=2026-01-25
    test_date = "2026-01-25"
    url = f"https://www.covers.com/sports/basketball/ncaab/matchups?selectedDate={test_date}"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Look for game elements
            games = soup.find_all('div', class_='cmg_matchup_game_box')
            print(f"  Found {len(games)} game boxes")

            if games:
                print("  ✓ Covers has data!")
                return True
            else:
                print("  ✗ No games found in expected format")
        else:
            print(f"  ✗ HTTP {response.status_code}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    return False


def test_oddsportal():
    """Test if OddsPortal has accessible historical data."""
    print("\nTesting OddsPortal.com...")

    # OddsPortal format: /basketball/usa/ncaa/results/
    url = "https://www.oddsportal.com/basketball/usa/ncaa/results/"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            print(f"  Response length: {len(response.content)} bytes")
            print("  ✓ OddsPortal accessible")
            # Check if we can see content
            if 'cloudflare' in response.text.lower():
                print("  ⚠️  Cloudflare protection detected")
                return False
            return True
        else:
            print(f"  ✗ HTTP {response.status_code}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    return False


def test_teamrankings():
    """Test if TeamRankings has accessible historical data."""
    print("\nTesting TeamRankings.com...")

    url = "https://www.teamrankings.com/ncb/odds/"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            print(f"  Response length: {len(response.content)} bytes")
            print("  ✓ TeamRankings accessible")
            return True
        else:
            print(f"  ✗ HTTP {response.status_code}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    return False


def test_sports_reference():
    """Test if Sports-Reference has betting data."""
    print("\nTesting Sports-Reference.com...")

    # Sports-Reference box score example
    url = "https://www.sports-reference.com/cbb/boxscores/2026-01-25.html"

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            # Check if there's betting data
            content = response.text
            has_spread = 'spread' in content.lower() or 'line' in content.lower()
            has_total = 'over/under' in content.lower() or 'total' in content.lower()

            print(f"  Has spread mention: {has_spread}")
            print(f"  Has total mention: {has_total}")

            if has_spread or has_total:
                print("  ✓ May have betting data")
                return True
            else:
                print("  ✗ No betting data found")
        else:
            print(f"  ✗ HTTP {response.status_code}")

    except Exception as e:
        print(f"  ✗ Error: {e}")

    return False


if __name__ == '__main__':
    print("=" * 80)
    print("TESTING FREE HISTORICAL ODDS SOURCES")
    print("=" * 80)
    print()

    results = {
        'Covers': test_covers(),
        'OddsPortal': test_oddsportal(),
        'TeamRankings': test_teamrankings(),
        'Sports-Reference': test_sports_reference()
    }

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)

    working_sources = [name for name, works in results.items() if works]

    if working_sources:
        print(f"✓ Accessible sources: {', '.join(working_sources)}")
        print("\nRECOMMENDATION: Can proceed with historical odds scraping")
    else:
        print("✗ No accessible free sources found")
        print("\nRECOMMENDATION: Cannot backtest without API credits or manual data")
