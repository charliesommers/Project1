# Quick Start Guide - CBB Totals Picker

Get started with Greg Peterson's CBB Totals Picker in 3 steps.

## Step 1: Install Dependencies

```bash
cd /home/user/Project1
pip install -r requirements.txt
```

## Step 2: Get Free API Key (Optional but Recommended)

1. Visit https://the-odds-api.com
2. Sign up (free - 500 requests/month)
3. Copy your API key

## Step 3: Run Daily Picks

### Option A: Auto-fetch from VSIN (Recommended)

```bash
python cbb_picker.py picks --auto-fetch --use-api --api-key YOUR_API_KEY
```

### Option B: Use Your Own File

If you already have Greg's Excel file:

```bash
python cbb_picker.py picks --file path/to/gregs_file.xlsx --use-api --api-key YOUR_API_KEY
```

### Option C: Without API (Manual Odds)

You'll need to manually enter sportsbook odds in a CSV file.

```bash
python cbb_picker.py picks --file path/to/gregs_file.xlsx --manual-odds odds.csv
```

## What You'll See

The system will:
1. Load Greg's handicapped totals
2. Fetch current Bet365 totals
3. Compare and find edges
4. Show recommendations like:

```
RECOMMENDED PICKS - TOTALS ONLY
================================================================================

Matchup                   Pick    Greg's  Sportsbook  Edge    Confidence
----------------------------------------------------------------------------------
Wisconsin vs Penn St      UNDER   149.5   154.5       -5.0    high
Duke vs UNC              OVER    148.5   145.0       +3.5    medium-high

Strategy:
  • UNDER: Greg's total is ≥5 points BELOW sportsbook
  • OVER: Greg's total is ≥3 points ABOVE sportsbook
```

## Understanding the Output

- **Pick**: OVER or UNDER recommendation
- **Greg's**: Greg Peterson's handicapped total
- **Sportsbook**: Current Bet365 total
- **Edge**: Difference (Greg's - Sportsbook)
- **Confidence**:
  - High: Edge ≥7 for under, ≥5 for over
  - Medium-high: Edge ≥6 for under, ≥4 for over
  - Medium: Meets minimum threshold

## Common Commands

### Show only top 5 picks:
```bash
python cbb_picker.py picks --auto-fetch --use-api --api-key YOUR_KEY --top 5
```

### Show only high-confidence picks:
```bash
python cbb_picker.py picks --auto-fetch --use-api --api-key YOUR_KEY --confidence high
```

### Export to Excel:
```bash
python cbb_picker.py picks --auto-fetch --use-api --api-key YOUR_KEY --output picks.xlsx
```

### Analyze historical performance:
```bash
python cbb_picker.py performance path/to/gregs_file.xlsx
```

## Next Steps

- Read [CBB_PICKER_README.md](CBB_PICKER_README.md) for full documentation
- Set up daily automation (cron job or task scheduler)
- Track your results to validate the strategy
- Adjust thresholds based on performance analysis

## Need Help?

- Run `python cbb_picker.py picks --help` for all options
- Check CBB_PICKER_README.md for troubleshooting
- Verify your API key is valid
- Make sure Greg's file format matches expected structure

## Strategy Reminder

✅ **Bet UNDER** when Greg's total is ≥5 points below sportsbook
✅ **Bet OVER** when Greg's total is ≥3 points above sportsbook
❌ **No bet** when edge is smaller

Good luck! 🏀
