# Your Personal CBB Picker Setup Guide

Your API key has been configured and the system is ready to use!

## ✅ What's Already Set Up

1. **API Key Configured**: Your Odds API key is saved in `.env` file
2. **System Tested**: Sample data test passed successfully
3. **All Dependencies**: Installed and working

## 🚀 How to Use (On Your Local Machine)

### Step 1: Install Dependencies

```bash
cd /home/user/Project1
pip install -r requirements.txt
```

### Step 2: Daily Picks - Auto Mode

The easiest way to get picks:

```bash
python cbb_picker.py picks --auto-fetch --use-api
```

**What this does:**
1. Checks VSIN for Greg's latest lines
2. Downloads if new
3. Fetches Bet365 odds using your API key (from .env file)
4. Compares Greg's totals to Bet365
5. Shows picks where edge meets your strategy

### Step 3: View Results

You'll see output like this:

```
RECOMMENDED PICKS - TOTALS ONLY
═══════════════════════════════════════════════════════════════

#  Matchup                Pick   Greg's  Sportsbook  Edge    Confidence
1  Purdue vs Indiana      UNDER  138.5   145.5       -7.0    high
2  Gonzaga vs St Marys    OVER   156.5   150.0       +6.5    high
3  Wisconsin vs Penn St   UNDER  149.5   154.5       -5.0    medium
4  Duke vs UNC           OVER   148.5   145.0       +3.5    medium

Strategy:
  • UNDER: Greg's total is ≥5 points BELOW sportsbook
  • OVER: Greg's total is ≥3 points ABOVE sportsbook
```

## 📊 Your Betting Strategy

**Current Thresholds:**
- ✅ **Bet UNDER**: When Greg's total is **≥5 points** below Bet365
- ✅ **Bet OVER**: When Greg's total is **≥3 points** above Bet365

**Confidence Levels:**
- **High**: Large edge (≥7 under, ≥5 over)
- **Medium-High**: Good edge (≥6 under, ≥4 over)
- **Medium**: Meets minimum threshold

## 💡 Useful Commands

### Filter to High-Confidence Only
```bash
python cbb_picker.py picks --auto-fetch --use-api --confidence high
```

### Top 5 Picks by Edge
```bash
python cbb_picker.py picks --auto-fetch --use-api --top 5
```

### Export to Excel
```bash
python cbb_picker.py picks --auto-fetch --use-api --output today_picks.xlsx
```

### Use Your Own Greg's File
If you manually download from VSIN:
```bash
python cbb_picker.py picks --file gregs_lines.xlsx --use-api
```

### Specific Date Sheet
If Greg's Excel has multiple dates:
```bash
python cbb_picker.py picks --file gregs_lines.xlsx --date 12326 --use-api
```
*Date format: MDDYY (e.g., 12326 = January 23, 2026)*

### Adjust Strategy Thresholds
Want to be more conservative? Increase thresholds:
```bash
python cbb_picker.py picks --auto-fetch --use-api --under-threshold 6 --over-threshold 4
```

## 📈 Historical Performance Analysis

Track how accurate Greg's totals have been:

```bash
python cbb_picker.py performance gregs_lines.xlsx
```

This will:
1. Parse all games from Greg's file
2. Fetch actual scores from ESPN
3. Show accuracy statistics
4. Calculate average total error

Export results:
```bash
python cbb_picker.py performance gregs_lines.xlsx --output performance.xlsx
```

## 🔄 Automation - Daily Picks

### Set Up Daily Auto-Run (Linux/Mac)

1. Open crontab:
```bash
crontab -e
```

2. Add this line (runs daily at 10 AM):
```
0 10 * * * cd /home/user/Project1 && python cbb_picker.py picks --auto-fetch --use-api >> picks_$(date +\%Y\%m\%d).log 2>&1
```

### Set Up Daily Auto-Run (Windows)

Create `daily_picks.bat`:
```batch
@echo off
cd C:\path\to\Project1
python cbb_picker.py picks --auto-fetch --use-api > picks_%date:~-4,4%%date:~-10,2%%date:~-7,2%.txt
```

Schedule in Windows Task Scheduler to run daily.

## 🔍 Troubleshooting

### API Key Issues

If you get "No API key provided":
- Check that `.env` file exists in `/home/user/Project1/`
- Or manually specify: `--api-key 32a952b95065c6b8c74f1e72ac125602`

### VSIN Fetch Fails

If auto-fetch from VSIN fails:
1. Manually download Greg's Excel from VSIN
2. Save to `data/` folder
3. Run: `python cbb_picker.py picks --file data/your_file.xlsx --use-api`

### No Matching Games

If API has games but no matches:
- Team names may differ between Greg and sportsbook
- Try running closer to game time (more games available)
- Check that it's the right sport (basketball_ncaab)

### Rate Limits

Free API tier: 500 requests/month
- Each run uses 1 request
- ~16 requests/day if running daily
- Should be fine for daily use

## 📝 Example Workflow

**Morning Routine:**

1. **Get Picks**:
   ```bash
   python cbb_picker.py picks --auto-fetch --use-api --confidence high --top 5
   ```

2. **Review**: Check the recommendations

3. **Place Bets**: On games with high confidence and good edge

4. **Track**: Save picks to compare later
   ```bash
   python cbb_picker.py picks --auto-fetch --use-api --output picks_0123.xlsx
   ```

**End of Season:**

5. **Analyze Performance**:
   ```bash
   python cbb_picker.py performance gregs_full_season.xlsx --output season_results.xlsx
   ```

6. **Optimize**: Adjust thresholds based on what worked

## 🎯 Tips for Best Results

1. **Run close to game time** - Odds are freshest
2. **Focus on high confidence** - Better win rate
3. **Track your results** - Know your actual ROI
4. **Adjust thresholds** - Based on performance data
5. **Don't chase** - Only bet when edge meets criteria

## 📞 Quick Reference

**Daily picks (simple):**
```bash
python cbb_picker.py picks --auto-fetch --use-api
```

**High confidence only:**
```bash
python cbb_picker.py picks --auto-fetch --use-api --confidence high
```

**Historical analysis:**
```bash
python cbb_picker.py performance gregs_lines.xlsx
```

**All options:**
```bash
python cbb_picker.py picks --help
python cbb_picker.py performance --help
```

## 🎲 Remember

- Your API key: `32a952b95065c6b8c74f1e72ac125602` (saved in `.env`)
- Greg's lines: https://vsin.com/college-basketball/greg-petersons-daily-college-basketball-lines/
- Strategy: UNDER ≥5 below, OVER ≥3 above
- Totals only - no spreads

Good luck and bet responsibly! 🏀
