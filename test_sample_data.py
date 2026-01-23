#!/usr/bin/env python3
"""
Test script to demonstrate the CBB picker with sample data
"""
import pandas as pd
from datetime import datetime
from gregs_cbb_parser import GregsCBBParser
from daily_picks_generator import DailyPicksGenerator
from tabulate import tabulate
from colorama import Fore, Style, init

init(autoreset=True)

# Create sample Greg's lines
print(f"{Fore.CYAN}Creating sample Greg's lines...")
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
        'favorite': 'Kansas',
        'underdog': 'Baylor',
        'spread': -3.0,
        'total': 142.5,
        'home_team': 'Baylor',
        'neutral_court': False,
        'matchup': 'Kansas vs Baylor',
        'spread_line': 'Kansas -3.0',
        'total_line': 'O/U 142.5'
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

print(f"{Fore.GREEN}✓ Created {len(sample_games)} sample games")

# Create sample sportsbook data
print(f"\n{Fore.CYAN}Creating sample sportsbook lines...")
sportsbook_data = [
    {
        'home_team': 'Penn St',
        'away_team': 'Wisconsin',
        'matchup': 'Wisconsin @ Penn St',
        'total': 154.5,  # 5 points higher than Greg's 149.5 -> BET UNDER
        'over_odds': -110,
        'under_odds': -110,
    },
    {
        'home_team': 'UNC',
        'away_team': 'Duke',
        'matchup': 'Duke @ UNC',
        'total': 145.0,  # 3.5 points lower than Greg's 148.5 -> BET OVER
        'over_odds': -110,
        'under_odds': -110,
    },
    {
        'home_team': 'Baylor',
        'away_team': 'Kansas',
        'matchup': 'Kansas @ Baylor',
        'total': 144.0,  # 1.5 points higher than Greg's 142.5 -> NO BET (under threshold)
        'over_odds': -110,
        'under_odds': -110,
    },
    {
        'home_team': 'Saint Marys',
        'away_team': 'Gonzaga',
        'matchup': 'Gonzaga @ Saint Marys',
        'total': 150.0,  # 6.5 points lower than Greg's 156.5 -> BET OVER
        'over_odds': -110,
        'under_odds': -110,
    },
    {
        'home_team': 'Indiana',
        'away_team': 'Purdue',
        'matchup': 'Purdue @ Indiana',
        'total': 145.5,  # 7 points higher than Greg's 138.5 -> BET UNDER
        'over_odds': -110,
        'under_odds': -110,
    },
]

print(f"{Fore.GREEN}✓ Created {len(sportsbook_data)} sportsbook lines")

# Generate picks
print(f"\n{Fore.CYAN}Generating picks using strategy...")
print(f"{Fore.CYAN}  • Bet UNDER when Greg's total is ≥5 points BELOW sportsbook")
print(f"{Fore.CYAN}  • Bet OVER when Greg's total is ≥3 points ABOVE sportsbook")

generator = DailyPicksGenerator(under_threshold=5.0, over_threshold=3.0)
picks = generator.generate_picks(sample_games, sportsbook_data)

print(f"{Fore.GREEN}✓ Generated {len(picks)} picks")

# Display results
print(f"\n{Fore.GREEN}{'='*80}")
print(f"{Fore.GREEN}RECOMMENDED PICKS - TOTALS ONLY")
print(f"{Fore.GREEN}{'='*80}\n")

if picks:
    table_data = []
    for idx, pick in enumerate(picks, 1):
        conf = pick['confidence']
        if conf == 'high':
            conf_color = Fore.GREEN
        elif conf == 'medium-high':
            conf_color = Fore.YELLOW
        else:
            conf_color = Fore.WHITE

        pick_type = pick['pick']
        if pick_type == 'OVER':
            pick_color = Fore.RED
        else:
            pick_color = Fore.BLUE

        edge = pick['edge']
        edge_str = f"{edge:+.1f}"

        row = [
            idx,
            pick['matchup'],
            f"{pick_color}{pick_type}{Style.RESET_ALL}",
            f"{pick['gregs_total']:.1f}",
            f"{pick['sportsbook_total']:.1f}",
            edge_str,
            f"{conf_color}{conf}{Style.RESET_ALL}",
            pick['reasoning'][:50]
        ]

        table_data.append(row)

    headers = ['#', 'Matchup', 'Pick', "Greg's", 'Sportsbook', 'Edge', 'Confidence', 'Reasoning']
    print(tabulate(table_data, headers=headers, tablefmt='grid'))

    # Summary
    summary = generator.get_picks_summary(picks)
    print(f"\n{Fore.YELLOW}{'='*60}")
    print(f"{Fore.YELLOW}PICKS SUMMARY:")
    print(f"{Fore.YELLOW}{'='*60}")
    print(f"Total Picks: {summary['total_picks']}")
    print(f"Over Picks: {summary['over_picks']}")
    print(f"Under Picks: {summary['under_picks']}")
    print(f"High Confidence: {summary['high_confidence_picks']}")
    print(f"Average Edge: {summary['avg_edge']:.2f} points")
    print(f"Max Edge: {summary['max_edge']:.2f} points")

    print(f"\n{Fore.CYAN}Strategy:")
    print(f"  • UNDER: Greg's total is ≥5 points BELOW sportsbook")
    print(f"  • OVER: Greg's total is ≥3 points ABOVE sportsbook")

    print(f"\n{Fore.GREEN}Test completed successfully! 🏀")
else:
    print(f"{Fore.YELLOW}No picks meet the criteria.")
