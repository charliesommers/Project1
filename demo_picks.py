#!/usr/bin/env python3
"""
Demo version showing what the simple picks interface looks like
Uses sample data instead of live data
"""
from datetime import datetime
from daily_picks_generator import DailyPicksGenerator


# Sample Greg's lines
sample_games = [
    {
        'date': datetime(2026, 1, 23),
        'favorite': 'Wisconsin',
        'underdog': 'Penn St',
        'spread': -4.5,
        'total': 149.5,
        'home_team': 'Penn St',
        'neutral_court': False,
        'matchup': 'Wisconsin vs Penn St',
        'spread_line': 'Wisconsin -4.5',
        'total_line': 'O/U 149.5'
    },
    {
        'date': datetime(2026, 1, 23),
        'favorite': 'Duke',
        'underdog': 'UNC',
        'spread': -6.5,
        'total': 148.5,
        'home_team': 'UNC',
        'neutral_court': False,
        'matchup': 'Duke vs UNC',
        'spread_line': 'Duke -6.5',
        'total_line': 'O/U 148.5'
    },
    {
        'date': datetime(2026, 1, 23),
        'favorite': 'Gonzaga',
        'underdog': 'Saint Marys',
        'spread': -8.5,
        'total': 156.5,
        'home_team': 'Saint Marys',
        'neutral_court': False,
        'matchup': 'Gonzaga vs Saint Marys',
        'spread_line': 'Gonzaga -8.5',
        'total_line': 'O/U 156.5'
    },
    {
        'date': datetime(2026, 1, 23),
        'favorite': 'Purdue',
        'underdog': 'Indiana',
        'spread': -5.0,
        'total': 138.5,
        'home_team': 'Indiana',
        'neutral_court': False,
        'matchup': 'Purdue vs Indiana',
        'spread_line': 'Purdue -5.0',
        'total_line': 'O/U 138.5'
    },
]

# Sample sportsbook data
sportsbook_data = [
    {
        'home_team': 'Penn St',
        'away_team': 'Wisconsin',
        'matchup': 'Wisconsin @ Penn St',
        'total': 154.5,
        'over_odds': -110,
        'under_odds': -110,
    },
    {
        'home_team': 'UNC',
        'away_team': 'Duke',
        'matchup': 'Duke @ UNC',
        'total': 145.0,
        'over_odds': -110,
        'under_odds': -110,
    },
    {
        'home_team': 'Saint Marys',
        'away_team': 'Gonzaga',
        'matchup': 'Gonzaga @ Saint Marys',
        'total': 150.0,
        'over_odds': -110,
        'under_odds': -110,
    },
    {
        'home_team': 'Indiana',
        'away_team': 'Purdue',
        'matchup': 'Purdue @ Indiana',
        'total': 145.5,
        'over_odds': -110,
        'under_odds': -110,
    },
]


def main():
    """Demo the simple picks interface."""
    print("=" * 70)
    print("DEMO - This is what you'll see when you run './picks' or 'python picks'")
    print("=" * 70)

    # Generate picks
    generator = DailyPicksGenerator(under_threshold=5.0, over_threshold=3.0)
    picks = generator.generate_picks(sample_games, sportsbook_data)

    # Display
    print(f"\n📅 {datetime.now().strftime('%B %d, %Y')} - CBB TOTALS PICKS\n")

    for i, pick in enumerate(picks, 1):
        conf_emoji = "🔥" if pick['confidence'] == 'high' else "✓"
        pick_emoji = "⬇️" if pick['pick'] == 'UNDER' else "⬆️"

        print(f"{conf_emoji} {pick_emoji} {pick['pick']} {pick['sportsbook_total']:.1f} - {pick['matchup']}")
        print(f"   Edge: {abs(pick['edge']):.1f} pts | Greg: {pick['gregs_total']:.1f} | Book: {pick['sportsbook_total']:.1f}")
        if i < len(picks):
            print()

    print(f"\n{'─'*60}")
    print(f"🔥 = High confidence | ✓ = Good bet")
    print(f"⬇️ = Under | ⬆️ = Over")
    print(f"Strategy: UNDER ≥5 below | OVER ≥3 above")
    print(f"{'─'*60}\n")


if __name__ == '__main__':
    main()
