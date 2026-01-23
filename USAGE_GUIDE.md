# Sports Gambling Picker - Usage Guide

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run with Sample Data**
   ```bash
   python picker.py data/sample_handicapping_data.xlsx
   ```

3. **Use Your Own Data**
   - Create an Excel file with your handicapping data
   - Follow the format in `data/sample_handicapping_data.xlsx`
   - Run the picker with your file

## Excel Data Format

### Required Columns

| Column | Description | Example |
|--------|-------------|---------|
| `Game` | Game matchup | "Chiefs vs Bills" |
| `Pick` | Your betting pick | "Chiefs -3" |
| `Odds` | American odds | -110, +150 |
| `Confidence` | Your confidence (0-100) | 85 |

### Optional Columns

| Column | Description | Example |
|--------|-------------|---------|
| `Sport` | Sport type | NFL, NBA, MLB, NHL |
| `Edge` | Calculated edge % | 12.5 |
| `Stake` | Recommended stake (units) | 2.0 |
| `Win_Probability` | Estimated win % | 65 |
| `Notes` | Analysis notes | "Strong home advantage" |

**Note:** If optional columns are not provided, the system will calculate them automatically.

## Command Line Options

### Basic Usage
```bash
python picker.py <excel_file>
```

### Filter by Top N Picks
```bash
python picker.py data/picks.xlsx --top 5
```
Shows only the top 5 picks.

### Filter by Confidence
```bash
python picker.py data/picks.xlsx --min-confidence 75
```
Shows only picks with 75% or higher confidence.

### Filter by Edge
```bash
python picker.py data/picks.xlsx --min-edge 10
```
Shows only picks with 10% or higher edge.

### Filter by Expected Value
```bash
python picker.py data/picks.xlsx --min-ev 5
```
Shows only picks with 5% or higher expected value.

### Filter by Sport
```bash
python picker.py data/picks.xlsx --sport NFL
```
Shows only NFL picks.

### Detailed Output
```bash
python picker.py data/picks.xlsx --detailed
```
Shows additional columns including Expected Value and Stake.

### Export Results
```bash
python picker.py data/picks.xlsx --output results.xlsx
```
Saves the top picks to an Excel file.

### Skip Summary Statistics
```bash
python picker.py data/picks.xlsx --no-summary
```
Skips the summary statistics and shows only the picks.

## Advanced Examples

### High-Confidence NFL Picks
```bash
python picker.py data/nfl_week1.xlsx --sport NFL --min-confidence 80 --min-edge 8 --top 3
```

### Export Best Value Plays
```bash
python picker.py data/all_sports.xlsx --min-edge 10 --output best_value.xlsx --detailed
```

### Quick Analysis
```bash
python picker.py data/today.xlsx --no-summary
```

## Understanding the Scoring System

The picker uses a weighted scoring algorithm to rank picks:

1. **Confidence Score (40%)**: Your handicapping confidence
2. **Edge Score (30%)**: The betting edge (win probability - implied probability)
3. **Expected Value Score (20%)**: Calculated expected value
4. **Odds Value Score (10%)**: Relative value of the odds

Higher scores indicate better betting opportunities.

## Understanding the Output

### Color Coding
- **Green (80+)**: Excellent picks with high confidence and edge
- **Yellow (60-79)**: Good picks worth considering
- **White (<60)**: Average picks, use caution

### Key Metrics

- **Conf**: Your confidence level (0-100%)
- **Edge**: Your edge over the bookmaker (%)
- **EV**: Expected Value - the theoretical return on investment (%)
- **Score**: Composite score based on all factors (0-100)
- **Stake**: Recommended stake in units

### Example Output
```
Top Recommended Picks:
+-----+-------------------+-----------+--------+--------+--------+---------+
|   # | Game              | Pick      |   Odds | Conf   | Edge   |   Score |
+=====+===================+===========+========+========+========+=========+
|   1 | Heat vs Bucks     | Bucks ML  |   -150 | 88%    | 15.3%  |    85.0 |
+-----+-------------------+-----------+--------+--------+--------+---------+
```

This indicates:
- The Bucks ML pick has 88% confidence
- 15.3% edge over the implied odds
- Overall score of 85 (excellent)

## Tips for Best Results

1. **Be Honest with Confidence**: Only assign high confidence to picks you truly believe in
2. **Calculate Edge**: If you know the true win probability, calculate edge = win_prob - implied_prob
3. **Use Notes**: Document your reasoning for each pick
4. **Regular Updates**: Update your Excel file regularly with new analysis
5. **Track Results**: Export picks and compare against actual results to improve your handicapping

## Creating Your Own Data File

1. Open Excel or Google Sheets
2. Create columns: `Game`, `Pick`, `Odds`, `Confidence`
3. Add optional columns as needed
4. Fill in your handicapping data
5. Save as `.xlsx` format
6. Run the picker

## Troubleshooting

### Error: "Missing required columns"
- Ensure your Excel file has all required columns: Game, Pick, Odds, Confidence
- Column names must match exactly (case-sensitive)

### Error: "No picks match the specified criteria"
- Your filters are too restrictive
- Lower the thresholds or remove filters

### Warning: "Invalid confidence values"
- Confidence must be between 0-100
- The system will automatically clamp values to this range

## Sample Data

The included sample data (`data/sample_handicapping_data.xlsx`) contains 20 picks across different sports. Use it to:
- Learn the data format
- Test the picker functionality
- See example handicapping analysis

Generate fresh sample data anytime:
```bash
python create_sample_data.py
```

## Getting Help

Run the picker with `--help` to see all available options:
```bash
python picker.py --help
```
