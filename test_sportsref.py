#!/usr/bin/env python3
"""
Test Sports-Reference scraper
"""
from datetime import datetime
from scores_fetcher import ScoresFetcher

# Create fetcher
fetcher = ScoresFetcher()

# Test today's date (Jan 26, 2026)
test_date = datetime(2026, 1, 26)

print(f"Testing Sports-Reference scraper for {test_date.strftime('%m/%d/%Y')}...")
print("=" * 80)

# Fetch schedule
games = fetcher.fetch_schedule_from_sportsref(test_date)

print("\n" + "=" * 80)
print(f"\nTotal games found: {len(games)}")

if games:
    print("\nFirst 5 games:")
    for i, game in enumerate(games[:5]):
        print(f"\n  {i+1}. {game['away_team']} @ {game['home_team']}")
        print(f"     Time: {game.get('commence_time', 'N/A')}")
        print(f"     Status: {game.get('status', 'N/A')}")
else:
    print("\n❌ No games found - scraper may not be working")
