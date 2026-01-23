# How to Get Your Daily Picks

Three super simple ways to get your CBB totals picks!

## 🚀 Method 1: Simplest (Just the List)

Run this single command:

```bash
python picks
```

or

```bash
./picks
```

**Output:**
```
📅 January 23, 2026 - CBB TOTALS PICKS

🔥 🔵 UNDER 145.5 - Purdue vs Indiana
   Edge: 7.0 pts | Greg: 138.5 | Book: 145.5

🔥 🔴 OVER 150.0 - Gonzaga vs Saint Marys
   Edge: 6.5 pts | Greg: 156.5 | Book: 150.0

✓ 🔵 UNDER 154.5 - Wisconsin vs Penn St
   Edge: 5.0 pts | Greg: 149.5 | Book: 154.5

✓ 🔴 OVER 145.0 - Duke vs UNC
   Edge: 3.5 pts | Greg: 148.5 | Book: 145.0

────────────────────────────────────────────────────────────
🔥 = High confidence | ✓ = Good bet
🔵 = Under | 🔴 = Over
────────────────────────────────────────────────────────────
```

**What it does:**
- ✅ Auto-fetches Greg's lines from VSIN
- ✅ Gets Bet365 odds via API
- ✅ Shows picks in clean list
- ✅ Emojis for quick scanning

---

## 📋 Method 2: Formatted List

Run this for a numbered list format:

```bash
python get_picks.py
```

**Output:**
```
======================================================================
TODAY'S CBB TOTALS PICKS - January 23, 2026
======================================================================

1. Purdue vs Indiana
   Pick: UNDER 145.5
   Edge: 7.0 pts (Greg: 138.5, Book: 145.5)
   Confidence: HIGH

2. Gonzaga vs Saint Marys
   Pick: OVER 150.0
   Edge: 6.5 pts (Greg: 156.5, Book: 150.0)
   Confidence: HIGH

3. Wisconsin vs Penn St
   Pick: UNDER 154.5
   Edge: 5.0 pts (Greg: 149.5, Book: 154.5)
   Confidence: MEDIUM

======================================================================
Strategy: UNDER when Greg ≥5 below | OVER when Greg ≥3 above
======================================================================
```

**Filtering options:**

High confidence only:
```bash
python get_picks.py high
```

Top 5 picks:
```bash
python get_picks.py top5
```

Top 3 picks:
```bash
python get_picks.py top3
```

---

## 🎨 Method 3: Full Analysis (Original)

For detailed analysis with tables:

```bash
python cbb_picker.py picks --auto-fetch --use-api
```

**Output:**
```
RECOMMENDED PICKS - TOTALS ONLY
================================================================================

+-----+------------------------+--------+----------+--------------+--------+--------------+
|   # | Matchup                | Pick   |   Greg's |   Sportsbook |   Edge | Confidence   |
+=====+========================+========+==========+==============+========+==============+
|   1 | Purdue vs Indiana      | UNDER  |    138.5 |        145.5 |   -7.0 | high         |
+-----+------------------------+--------+----------+--------------+--------+--------------+
|   2 | Gonzaga vs Saint Marys | OVER   |    156.5 |        150.0 |    6.5 | high         |
+-----+------------------------+--------+----------+--------------+--------+--------------+

PICKS SUMMARY:
Total Picks: 4
Over Picks: 2
Under Picks: 2
High Confidence: 2
Average Edge: 5.50 points
```

---

## 🎯 Quick Reference

| What You Want | Command |
|---------------|---------|
| **Just the picks** | `python picks` |
| **Numbered list** | `python get_picks.py` |
| **High confidence only** | `python get_picks.py high` |
| **Top 5** | `python get_picks.py top5` |
| **Full analysis** | `python cbb_picker.py picks --auto-fetch --use-api` |
| **See demo** | `python demo_picks.py` |

---

## 💡 Pro Tips

### Save Picks to File

```bash
python picks > todays_picks.txt
```

### Morning Routine

```bash
# Get your picks
python picks

# If you want to save them
python picks > picks_$(date +%m%d).txt
```

### Check Multiple Times

```bash
# Morning
python picks > morning_picks.txt

# Closer to game time (if lines changed)
python picks > evening_picks.txt
```

### High Confidence Only for Conservative Betting

```bash
python get_picks.py high
```

---

## 📱 What the Symbols Mean

**Confidence:**
- 🔥 = High confidence (Large edge: ≥7 under, ≥5 over)
- ✓ = Good bet (Meets minimum threshold)

**Pick Type:**
- 🔵 = UNDER bet
- 🔴 = OVER bet

**Edge:**
- The difference between Greg's total and sportsbook total
- Larger edge = stronger play

---

## ⚙️ How It Works Behind the Scenes

When you run any of these commands, the system:

1. **Checks VSIN** for Greg's latest lines (auto-downloads if new)
2. **Fetches Bet365 odds** using your API key from .env
3. **Compares totals** to find edges
4. **Applies strategy**:
   - UNDER if Greg ≥5 points below sportsbook
   - OVER if Greg ≥3 points above sportsbook
5. **Ranks by edge** (biggest edges first)
6. **Displays results** in your chosen format

---

## 🔧 Troubleshooting

**"Could not get Greg's lines"**
- VSIN website may be down or changed
- Manually download from: https://vsin.com/college-basketball/greg-petersons-daily-college-basketball-lines/
- Save to `data/` folder
- Run: `python cbb_picker.py picks --file data/your_file.xlsx --use-api`

**"Could not fetch sportsbook odds"**
- Check .env file has your API key
- Verify: `cat .env` should show `ODDS_API_KEY=32a952b95065c6b8c74f1e72ac125602`
- Check API quota at https://the-odds-api.com

**"No picks today"**
- No games have enough edge to meet criteria
- Try relaxing thresholds: `python cbb_picker.py picks --auto-fetch --use-api --under-threshold 4 --over-threshold 2`

---

## 🎲 Remember

- **Under ≥5**: Greg's total is 5+ points BELOW sportsbook
- **Over ≥3**: Greg's total is 3+ points ABOVE sportsbook
- Run once in the morning before games
- Focus on high confidence picks
- Track your results!

Happy betting! 🏀
