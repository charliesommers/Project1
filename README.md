# Sports Gambling Picker

Two powerful systems for sports betting analysis:

## 1. Greg Peterson's CBB Totals Picker (NEW! 🏀)

**Specialized system for college basketball totals betting** using Greg Peterson's daily handicapping lines.

- **Auto-fetches** daily lines from VSIN
- **Compares** Greg's totals vs Bet365
- **Generates picks** using proven strategy (Under ≥5 below, Over ≥3 above)
- **Tracks performance** with historical analysis
- **Totals only** - no spread betting

👉 **[Quick Start Guide](QUICKSTART.md)** | **[Full Documentation](CBB_PICKER_README.md)**

### Quick Start - CBB Picker

```bash
# Auto-fetch Greg's lines and generate picks
python cbb_picker.py picks --auto-fetch --use-api --api-key YOUR_KEY

# View historical performance
python cbb_picker.py performance gregs_lines.xlsx
```

---

## 2. General Sports Picker

An automatic sports gambling picker that analyzes Excel forecasting and handicapping data to recommend optimal betting picks.

### Features

- **Excel Data Import**: Read handicapping data from Excel spreadsheets
- **Multi-Factor Analysis**: Evaluate picks based on multiple metrics (odds, confidence, edge, etc.)
- **Configurable Scoring**: Weighted scoring system for different handicapping factors
- **Pick Recommendations**: Automatically rank and recommend best betting opportunities
- **Detailed Reports**: View comprehensive analysis with win probabilities and expected value

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python picker.py data/your_data.xlsx
```

### Command Line Options

```bash
python picker.py <excel_file> [options]

Options:
  --top N              Show top N picks (default: 10)
  --min-confidence X   Minimum confidence threshold (0-100, default: 60)
  --min-edge X        Minimum edge percentage (default: 5)
  --sport SPORT       Filter by sport type
  --output FILE       Save results to file
```

### Example

```bash
python picker.py data/nfl_week1.xlsx --top 5 --min-confidence 70 --min-edge 10
```

## Excel Data Format

Your Excel file should contain the following columns:

### Required Columns:
- **Game**: Game description (e.g., "Team A vs Team B")
- **Pick**: Your betting pick (team, over/under, spread, etc.)
- **Odds**: Betting odds (American format, e.g., -110, +150)
- **Confidence**: Your confidence level (0-100)

### Optional Columns:
- **Sport**: Sport type (NFL, NBA, MLB, etc.)
- **Edge**: Calculated edge percentage
- **Stake**: Recommended stake amount (units)
- **Win_Probability**: Estimated win probability (0-100)
- **Notes**: Additional analysis notes

See `data/sample_handicapping_data.xlsx` for an example template.

## How It Works

The picker analyzes your handicapping data using a weighted scoring algorithm:

1. **Confidence Score** (40%): Your handicapping confidence
2. **Edge Score** (30%): Expected value and betting edge
3. **Odds Value** (20%): Relative value of the odds
4. **Win Probability** (10%): Calculated win probability

Picks are ranked by total score, and the system recommends the highest-scoring opportunities that meet your thresholds.

## Sample Output

```
Top 5 Recommended Picks:
╔════╦═══════════════════════╦═══════════╦════════╦═══════════╦═════════╦═══════╗
║ #  ║ Game                  ║ Pick      ║ Odds   ║ Confidence║ Edge %  ║ Score ║
╠════╬═══════════════════════╬═══════════╬════════╬═══════════╬═════════╬═══════╣
║ 1  ║ Chiefs vs Bills       ║ Chiefs -3 ║ -110   ║ 85        ║ 12.5    ║ 92.3  ║
║ 2  ║ Lakers vs Celtics     ║ Over 215  ║ -105   ║ 80        ║ 10.2    ║ 88.7  ║
...
```

## License

MIT License
