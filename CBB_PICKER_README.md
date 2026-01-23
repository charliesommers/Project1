# Greg Peterson's College Basketball Totals Picker

Automated system for analyzing college basketball betting opportunities using Greg Peterson's daily handicapping lines and sportsbook totals.

**Focus**: Over/Under (Totals) betting only - no spread betting.

## Overview

This system:
1. **Auto-fetches** Greg Peterson's daily CBB lines from VSIN
2. **Compares** Greg's totals vs sportsbook totals (Bet365, etc.)
3. **Generates picks** using proven strategy
4. **Tracks performance** by analyzing historical results

## Strategy

**Betting Rules:**
- ✅ **Bet UNDER** when Greg's total is **≥5 points BELOW** sportsbook total
- ✅ **Bet OVER** when Greg's total is **≥3 points ABOVE** sportsbook total
- ❌ **No bet** when edge is smaller than thresholds

**Example:**
- Greg's Total: 140.5
- Sportsbook Total: 146.0
- Edge: -5.5 points
- **Pick: UNDER** (Greg is 5.5 below sportsbook)

## Installation

```bash
cd /home/user/Project1
pip install -r requirements.txt
```

## Usage

### Daily Picks (Automated)

Auto-fetch from VSIN and generate picks:

```bash
python cbb_picker.py picks --auto-fetch --use-api --api-key YOUR_API_KEY
```

**What it does:**
1. Checks VSIN for today's lines
2. Downloads if new
3. Fetches current Bet365 odds via API
4. Generates picks using your strategy
5. Displays recommendations

### Daily Picks (Manual File)

If you already have Greg's Excel file:

```bash
python cbb_picker.py picks --file data/gregs_lines.xlsx --use-api --api-key YOUR_KEY
```

### View Specific Date

View picks for a specific date sheet:

```bash
python cbb_picker.py picks --file data/gregs_lines.xlsx --date 12226 --use-api --api-key YOUR_KEY
```

*Date format: MDDYY (e.g., 12226 = January 22, 2026)*

### Filter Picks

Show only high-confidence picks:

```bash
python cbb_picker.py picks --auto-fetch --use-api --api-key YOUR_KEY --confidence high
```

Show top 5 picks by edge:

```bash
python cbb_picker.py picks --auto-fetch --use-api --api-key YOUR_KEY --top 5
```

Minimum edge of 6 points:

```bash
python cbb_picker.py picks --auto-fetch --use-api --api-key YOUR_KEY --min-edge 6
```

### Historical Performance Analysis

Analyze Greg's past performance:

```bash
python cbb_picker.py performance data/gregs_lines.xlsx
```

**What it does:**
1. Parses all historical games from Excel
2. Fetches actual scores from ESPN
3. Compares Greg's totals to actual results
4. Shows accuracy statistics

Export results:

```bash
python cbb_picker.py performance data/gregs_lines.xlsx --output results.xlsx
```

## Getting API Key (Free)

To fetch live sportsbook odds:

1. Visit https://the-odds-api.com
2. Sign up for free account
3. Get your API key (500 free requests/month)
4. Use with `--api-key YOUR_KEY`

Or set environment variable:

```bash
export ODDS_API_KEY=your_key_here
python cbb_picker.py picks --auto-fetch --use-api
```

## Manual Odds Entry (No API)

If you don't want to use the API, you can manually enter sportsbook odds:

1. Generate template:
```bash
python cbb_picker.py picks --file data/gregs_lines.xlsx --generate-template
```

2. Fill in sportsbook totals in the CSV

3. Run with manual odds:
```bash
python cbb_picker.py picks --file data/gregs_lines.xlsx --manual-odds odds.csv
```

## Greg's Excel Format

The system automatically parses Greg Peterson's format:

**Sheet Names**: Date in MDDYY format (e.g., `12226` = Jan 22, 2026)

**Columns**:
- `Team`: Team name
- `Greg's Line`: Spread (negative) for favorite, Total (3-digit) for underdog

**Game Structure**:
- 2 rows per game
- Row 1: Favorite with spread (e.g., -5.5)
- Row 2: Underdog with total (e.g., 145.5)
- Home team on bottom (unless * = neutral court)

## Output Example

```
RECOMMENDED PICKS - TOTALS ONLY
================================================================================

+-----+---------------------------+--------+---------+------------+--------+--------------+
|   # | Matchup                   | Pick   | Greg's  | Sportsbook | Edge   | Confidence   |
+=====+===========================+========+=========+============+========+==============+
|   1 | Wisconsin vs Penn St      | UNDER  | 149.5   | 154.5      | -5.0   | high         |
+-----+---------------------------+--------+---------+------------+--------+--------------+
|   2 | Duke vs UNC               | OVER   | 148.5   | 145.0      | +3.5   | medium-high  |
+-----+---------------------------+--------+---------+------------+--------+--------------+

Strategy:
  • UNDER: Greg's total is ≥5 points BELOW sportsbook
  • OVER: Greg's total is ≥3 points ABOVE sportsbook
```

## Customizing Strategy

Adjust thresholds:

```bash
python cbb_picker.py picks --auto-fetch --use-api --api-key YOUR_KEY \
  --under-threshold 6 \
  --over-threshold 4
```

This changes the strategy to:
- UNDER when Greg is ≥6 below sportsbook
- OVER when Greg is ≥4 above sportsbook

## Automation (Daily Updates)

### Linux/Mac Cron Job

Add to crontab to run daily at 10 AM:

```bash
crontab -e
```

Add line:
```
0 10 * * * cd /home/user/Project1 && python cbb_picker.py picks --auto-fetch --use-api --api-key YOUR_KEY > picks_$(date +\%Y\%m\%d).txt
```

### Windows Task Scheduler

Create batch file `daily_picks.bat`:
```batch
cd C:\path\to\Project1
python cbb_picker.py picks --auto-fetch --use-api --api-key YOUR_KEY > picks_%date%.txt
```

Schedule in Task Scheduler to run daily.

## Files Structure

```
Project1/
├── cbb_picker.py              # Main CLI interface
├── gregs_cbb_parser.py        # Parses Greg's Excel format
├── vsin_scraper.py            # Auto-fetches from VSIN
├── odds_fetcher.py            # Fetches sportsbook odds
├── scores_fetcher.py          # Fetches game scores
├── performance_tracker.py     # Analyzes historical performance
├── daily_picks_generator.py   # Generates picks using strategy
├── data/
│   └── gregs_lines_*.xlsx     # Downloaded Greg's lines
└── requirements.txt           # Python dependencies
```

## Troubleshooting

### "No API key provided"
- Get free key at https://the-odds-api.com
- Use `--api-key YOUR_KEY` or set environment variable

### "Failed to fetch from VSIN"
- VSIN website may have changed structure
- Manually download Excel file from VSIN
- Use `--file` instead of `--auto-fetch`

### "No games found"
- Check sheet name format (should be MDDYY)
- Verify Excel has "Team" and "Greg's Line" columns
- Check file path is correct

### "No matching games"
- Team names may not match exactly
- API may not have all games yet
- Try manual odds entry

## Tips for Best Results

1. **Run daily** around game time to get fresh odds
2. **Track results** to validate strategy performance
3. **Adjust thresholds** based on historical analysis
4. **Focus on high-confidence** picks for better win rate
5. **Use performance analysis** to see Greg's accuracy trends

## Advanced Usage

### Combine with Performance Analysis

1. Download historical lines
2. Run performance analysis
3. Adjust thresholds based on results
4. Generate picks with optimized strategy

### Export for Tracking

Export picks daily:
```bash
python cbb_picker.py picks --auto-fetch --use-api --api-key YOUR_KEY \
  --output picks_$(date +%Y%m%d).xlsx
```

Compare later with actual results to track ROI.

## Support

For issues or questions:
- Check troubleshooting section above
- Review error messages carefully
- Ensure all dependencies installed
- Verify API key is valid

## Disclaimer

This tool is for informational and educational purposes only. Always gamble responsibly and within your means. Past performance does not guarantee future results.
