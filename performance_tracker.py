"""
Performance Tracker
Analyzes Greg's historical performance by comparing lines to actual results
"""
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime


class PerformanceTracker:
    """Tracks and analyzes Greg's handicapping performance."""

    def __init__(self):
        """Initialize performance tracker."""
        self.results = []

    def analyze_game(self, gregs_game: Dict, actual_scores: Dict) -> Dict:
        """
        Analyze a single game's performance.

        Args:
            gregs_game: Game data from Greg's parser (includes spread and total)
            actual_scores: Actual game scores

        Returns:
            Dictionary with performance metrics
        """
        result = {
            'date': gregs_game['date'],
            'matchup': gregs_game['matchup'],
            'favorite': gregs_game['favorite'],
            'underdog': gregs_game['underdog'],
            'gregs_spread': gregs_game['spread'],
            'gregs_total': gregs_game['total'],
            'actual_total': actual_scores['total_score'],
            'actual_margin': actual_scores['margin'],
            'home_score': actual_scores['home_score'],
            'away_score': actual_scores['away_score'],
        }

        # Determine which team is home/away for actual margin calculation
        if gregs_game['favorite'] == actual_scores['home_team']:
            # Favorite is home
            actual_spread_result = actual_scores['home_score'] - actual_scores['away_score']
        elif gregs_game['favorite'] == actual_scores['away_team']:
            # Favorite is away
            actual_spread_result = actual_scores['away_score'] - actual_scores['home_score']
        else:
            # Team names don't match exactly - try to infer
            if actual_scores['home_score'] > actual_scores['away_score']:
                actual_spread_result = actual_scores['home_score'] - actual_scores['away_score']
            else:
                actual_spread_result = actual_scores['away_score'] - actual_scores['home_score']

        result['actual_spread_result'] = actual_spread_result

        # Calculate spread accuracy
        # Greg's spread is negative (favorite giving points)
        # If spread is -5.5, favorite needs to win by more than 5.5
        gregs_spread_abs = abs(gregs_game['spread'])

        if actual_spread_result > gregs_spread_abs:
            result['spread_pick'] = gregs_game['favorite']
            result['spread_correct'] = True
        elif actual_spread_result < gregs_spread_abs:
            result['spread_pick'] = gregs_game['underdog']
            result['spread_correct'] = False
        else:
            result['spread_pick'] = 'push'
            result['spread_correct'] = None

        # Calculate spread error (how far off was Greg)
        result['spread_error'] = actual_spread_result - gregs_spread_abs

        # Calculate total accuracy
        if actual_scores['total_score'] > gregs_game['total']:
            result['total_result'] = 'over'
        elif actual_scores['total_score'] < gregs_game['total']:
            result['total_result'] = 'under'
        else:
            result['total_result'] = 'push'

        # Calculate total error (how far off was Greg)
        result['total_error'] = actual_scores['total_score'] - gregs_game['total']

        return result

    def analyze_all_games(self, gregs_games: List[Dict], scored_games: List[Dict]) -> pd.DataFrame:
        """
        Analyze all games with scores.

        Args:
            gregs_games: List of games from Greg's parser
            scored_games: List of games with actual scores

        Returns:
            DataFrame with all results
        """
        from scores_fetcher import ScoresFetcher

        fetcher = ScoresFetcher()
        results = []

        for gregs_game in gregs_games:
            # Find matching scored game
            scored_game = fetcher.match_game(gregs_game, scored_games)

            if scored_game:
                result = self.analyze_game(gregs_game, scored_game)
                results.append(result)

        self.results = results
        return pd.DataFrame(results)

    def get_performance_summary(self, df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Generate performance summary statistics.

        Args:
            df: Results DataFrame (uses self.results if None)

        Returns:
            Dictionary with summary statistics
        """
        if df is None:
            df = pd.DataFrame(self.results)

        if len(df) == 0:
            return {'error': 'No results to analyze'}

        # Spread performance
        spread_results = df[df['spread_correct'].notna()]
        spread_wins = spread_results['spread_correct'].sum()
        spread_total = len(spread_results)
        spread_win_rate = (spread_wins / spread_total * 100) if spread_total > 0 else 0

        # Total performance
        total_overs = (df['total_result'] == 'over').sum()
        total_unders = (df['total_result'] == 'under').sum()
        total_pushes = (df['total_result'] == 'push').sum()

        # Accuracy metrics
        avg_spread_error = df['spread_error'].abs().mean()
        avg_total_error = df['total_error'].abs().mean()

        return {
            'total_games_analyzed': len(df),
            'spread_win_rate': spread_win_rate,
            'spread_wins': int(spread_wins),
            'spread_losses': spread_total - int(spread_wins),
            'spread_total': spread_total,
            'total_overs': int(total_overs),
            'total_unders': int(total_unders),
            'total_pushes': int(total_pushes),
            'avg_spread_error': avg_spread_error,
            'avg_total_error': avg_total_error,
            'date_range': f"{df['date'].min()} to {df['date'].max()}" if 'date' in df.columns else 'N/A'
        }

    def get_strategy_performance(
        self,
        df: pd.DataFrame,
        sportsbook_lines: Dict[str, float],
        under_threshold: float = 5.0,
        over_threshold: float = 3.0
    ) -> Dict:
        """
        Analyze performance of the betting strategy.

        Strategy:
        - Bet UNDER when Greg's total is ≥5 points below sportsbook
        - Bet OVER when Greg's total is ≥3 points above sportsbook

        Args:
            df: Results DataFrame
            sportsbook_lines: Dictionary mapping matchup to sportsbook total
            under_threshold: Points below sportsbook to bet under (default: 5)
            over_threshold: Points above sportsbook to bet over (default: 3)

        Returns:
            Strategy performance statistics
        """
        strategy_picks = []

        for _, row in df.iterrows():
            matchup = row['matchup']
            sportsbook_total = sportsbook_lines.get(matchup)

            if not sportsbook_total:
                continue

            gregs_total = row['gregs_total']
            edge = gregs_total - sportsbook_total

            # Apply strategy
            if edge <= -under_threshold:
                # Bet UNDER (Greg's line is significantly below sportsbook)
                pick = 'under'
                correct = row['total_result'] == 'under'
            elif edge >= over_threshold:
                # Bet OVER (Greg's line is significantly above sportsbook)
                pick = 'over'
                correct = row['total_result'] == 'over'
            else:
                # No bet
                continue

            strategy_picks.append({
                'matchup': matchup,
                'pick': pick,
                'edge': edge,
                'correct': correct,
                'gregs_total': gregs_total,
                'sportsbook_total': sportsbook_total,
                'actual_total': row['actual_total']
            })

        if not strategy_picks:
            return {'error': 'No qualifying picks'}

        picks_df = pd.DataFrame(strategy_picks)

        wins = picks_df['correct'].sum()
        total = len(picks_df)
        win_rate = (wins / total * 100) if total > 0 else 0

        # Calculate ROI (assuming -110 odds)
        # Win: +0.909 units, Loss: -1 unit
        roi = (wins * 0.909 - (total - wins)) / total * 100 if total > 0 else 0

        return {
            'total_picks': total,
            'wins': int(wins),
            'losses': total - int(wins),
            'win_rate': win_rate,
            'roi': roi,
            'avg_edge': picks_df['edge'].abs().mean(),
            'under_picks': int((picks_df['pick'] == 'under').sum()),
            'over_picks': int((picks_df['pick'] == 'over').sum()),
        }
