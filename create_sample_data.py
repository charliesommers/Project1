#!/usr/bin/env python3
"""
Script to create sample handicapping data Excel file
"""
import pandas as pd
from pathlib import Path

# Create sample data
sample_data = {
    'Sport': [
        'NFL', 'NFL', 'NFL', 'NBA', 'NBA', 'NBA', 'NHL', 'NHL',
        'NFL', 'NBA', 'MLB', 'MLB', 'NHL', 'NFL', 'NBA',
        'NFL', 'NBA', 'NHL', 'MLB', 'NFL'
    ],
    'Game': [
        'Chiefs vs Bills',
        'Cowboys vs Eagles',
        'Packers vs Vikings',
        'Lakers vs Celtics',
        'Warriors vs Nets',
        'Heat vs Bucks',
        'Penguins vs Capitals',
        'Maple Leafs vs Bruins',
        'Bengals vs Ravens',
        'Suns vs Nuggets',
        'Yankees vs Red Sox',
        'Dodgers vs Giants',
        'Lightning vs Panthers',
        '49ers vs Seahawks',
        'Clippers vs Mavericks',
        'Steelers vs Browns',
        'Knicks vs 76ers',
        'Oilers vs Flames',
        'Astros vs Rangers',
        'Rams vs Cardinals'
    ],
    'Pick': [
        'Chiefs -3',
        'Over 48.5',
        'Vikings +7',
        'Over 215',
        'Warriors -5.5',
        'Bucks ML',
        'Under 6.5',
        'Bruins -1.5',
        'Bengals -2.5',
        'Nuggets -8',
        'Yankees -145',
        'Over 8.5',
        'Lightning ML',
        '49ers -6.5',
        'Under 228',
        'Steelers +3.5',
        'Knicks +4',
        'Oilers -1.5',
        'Astros ML',
        'Rams -7'
    ],
    'Odds': [
        -110, -105, -110, -110, -108, -150, -115, -120,
        -112, -110, -145, -110, -130, -110, -105,
        -110, +120, -125, -160, -115
    ],
    'Confidence': [
        85, 75, 70, 80, 65, 88, 72, 68,
        77, 60, 82, 55, 78, 71, 62,
        69, 73, 66, 84, 58
    ],
    'Edge': [
        12.5, 8.2, 5.5, 10.2, 2.8, 15.3, 6.7, 3.4,
        9.1, 1.5, 11.8, -2.3, 8.9, 4.2, 0.8,
        5.1, 7.6, 3.9, 13.2, -1.5
    ],
    'Stake': [
        2.0, 1.5, 1.0, 1.5, 1.0, 2.5, 1.0, 1.0,
        1.5, 0.5, 2.0, 0.5, 1.5, 1.0, 0.5,
        1.0, 1.0, 1.0, 2.0, 0.5
    ],
    'Win_Probability': [
        85, 75, 72, 80, 67, 88, 74, 70,
        79, 62, 83, 52, 80, 73, 64,
        71, 75, 68, 85, 60
    ],
    'Notes': [
        'Strong home advantage, Chiefs offense clicking',
        'Both teams averaging 27+ PPG, expect shootout',
        'Vikings defense underrated, good value',
        'High pace game, both teams elite offensively',
        'Warriors bounce-back spot after 2 losses',
        'Bucks at home against weak opponent',
        'Strong goaltending matchup favors under',
        'Bruins dominant at home this season',
        'Division rivalry, Bengals need this win',
        'Nuggets covering big spreads lately',
        'Yankees ace on mound, favorable matchup',
        'Bullpens struggling, weather favorable for over',
        'Lightning in playoff form, great value',
        '49ers injury concerns but still talented',
        'Defensive matchup, expect lower scoring',
        'Steelers getting healthy, Browns overvalued',
        'Knicks playing well on road recently',
        'Battle of Alberta, Oilers have edge',
        'Astros bullpen advantage in late innings',
        'Cardinals injuries mounting on defense'
    ]
}

# Create DataFrame
df = pd.DataFrame(sample_data)

# Ensure data directory exists
Path('data').mkdir(exist_ok=True)

# Save to Excel
output_file = 'data/sample_handicapping_data.xlsx'
df.to_excel(output_file, index=False, engine='openpyxl')

print(f"Sample data created: {output_file}")
print(f"Total picks: {len(df)}")
print(f"\nSports breakdown:")
print(df['Sport'].value_counts())
print(f"\nAverage confidence: {df['Confidence'].mean():.1f}%")
print(f"Average edge: {df['Edge'].mean():.2f}%")
