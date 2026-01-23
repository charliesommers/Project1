"""
Sports Gambling Picker Engine
Analyzes handicapping data and recommends optimal picks
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional


class PickerEngine:
    """Engine for analyzing and ranking betting picks."""

    def __init__(self, data: pd.DataFrame, config: Optional[Dict] = None):
        """
        Initialize the picker engine.

        Args:
            data: DataFrame with handicapping data
            config: Configuration dictionary with scoring weights and thresholds
        """
        self.data = data.copy()
        self.config = config or self._default_config()

    @staticmethod
    def _default_config() -> Dict:
        """Default configuration for the picker engine."""
        return {
            'weights': {
                'confidence': 0.40,
                'edge': 0.30,
                'expected_value': 0.20,
                'odds_value': 0.10,
            },
            'thresholds': {
                'min_confidence': 0,
                'min_edge': -100,
                'min_expected_value': -100,
            }
        }

    def calculate_scores(self) -> pd.DataFrame:
        """
        Calculate composite scores for each pick.

        Returns:
            DataFrame with added score columns
        """
        # Normalize metrics to 0-100 scale
        self.data['confidence_score'] = self.data['Confidence']

        # Edge score: Convert edge to 0-100 scale (assuming edge range -20 to +20)
        self.data['edge_score'] = self._normalize_to_score(
            self.data['Edge'],
            min_val=-20,
            max_val=20,
            center=0
        )

        # Expected Value score: Convert EV to 0-100 scale
        self.data['ev_score'] = self._normalize_to_score(
            self.data['Expected_Value'],
            min_val=-50,
            max_val=50,
            center=0
        )

        # Odds value score: Better odds get higher scores
        self.data['odds_score'] = self.data['Odds'].apply(self._odds_to_score)

        # Calculate weighted composite score
        weights = self.config['weights']
        self.data['Total_Score'] = (
            self.data['confidence_score'] * weights['confidence'] +
            self.data['edge_score'] * weights['edge'] +
            self.data['ev_score'] * weights['expected_value'] +
            self.data['odds_score'] * weights['odds_value']
        )

        # Round scores
        self.data['Total_Score'] = self.data['Total_Score'].round(2)

        return self.data

    @staticmethod
    def _normalize_to_score(series: pd.Series, min_val: float, max_val: float, center: float = 0) -> pd.Series:
        """
        Normalize a series to 0-100 score.

        Args:
            series: Data series to normalize
            min_val: Minimum expected value
            max_val: Maximum expected value
            center: Center point (maps to 50)

        Returns:
            Normalized series
        """
        def normalize(val):
            if pd.isna(val):
                return 50.0

            if val >= center:
                # Map center to max_val -> 50 to 100
                if max_val == center:
                    return 50.0
                score = 50 + (val - center) / (max_val - center) * 50
            else:
                # Map min_val to center -> 0 to 50
                if center == min_val:
                    return 50.0
                score = 50 - (center - val) / (center - min_val) * 50

            # Clamp to 0-100
            return max(0, min(100, score))

        return series.apply(normalize)

    @staticmethod
    def _odds_to_score(odds) -> float:
        """
        Convert odds to a value score.
        Positive odds (underdogs) get higher scores for better value.

        Args:
            odds: American odds

        Returns:
            Score 0-100
        """
        try:
            odds = float(odds)
            if odds >= 200:
                return 90
            elif odds >= 150:
                return 80
            elif odds >= 100:
                return 70
            elif odds >= 0:
                return 60
            elif odds >= -110:
                return 50
            elif odds >= -150:
                return 40
            elif odds >= -200:
                return 30
            else:
                return 20
        except (ValueError, TypeError):
            return 50

    def filter_picks(
        self,
        min_confidence: Optional[float] = None,
        min_edge: Optional[float] = None,
        min_ev: Optional[float] = None,
        sport: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Filter picks based on thresholds.

        Args:
            min_confidence: Minimum confidence threshold
            min_edge: Minimum edge threshold
            min_ev: Minimum expected value threshold
            sport: Sport to filter by

        Returns:
            Filtered DataFrame
        """
        filtered = self.data.copy()

        if min_confidence is not None:
            filtered = filtered[filtered['Confidence'] >= min_confidence]

        if min_edge is not None:
            filtered = filtered[filtered['Edge'] >= min_edge]

        if min_ev is not None:
            filtered = filtered[filtered['Expected_Value'] >= min_ev]

        if sport is not None and 'Sport' in filtered.columns:
            filtered = filtered[filtered['Sport'].str.upper() == sport.upper()]

        return filtered

    def get_top_picks(
        self,
        n: int = 10,
        min_confidence: Optional[float] = None,
        min_edge: Optional[float] = None,
        min_ev: Optional[float] = None,
        sport: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get top N picks based on score.

        Args:
            n: Number of picks to return
            min_confidence: Minimum confidence threshold
            min_edge: Minimum edge threshold
            min_ev: Minimum expected value threshold
            sport: Sport to filter by

        Returns:
            DataFrame with top picks sorted by score
        """
        # Calculate scores if not already done
        if 'Total_Score' not in self.data.columns:
            self.calculate_scores()

        # Filter picks
        filtered = self.filter_picks(min_confidence, min_edge, min_ev, sport)

        # Sort by score and get top N
        top_picks = filtered.sort_values('Total_Score', ascending=False).head(n)

        return top_picks

    def get_recommendations_summary(self, top_picks: pd.DataFrame) -> Dict:
        """
        Generate a summary of recommendations.

        Args:
            top_picks: DataFrame of top picks

        Returns:
            Dictionary with summary statistics
        """
        if len(top_picks) == 0:
            return {
                'total_recommendations': 0,
                'avg_confidence': 0,
                'avg_edge': 0,
                'avg_expected_value': 0,
                'total_stake': 0,
                'potential_roi': 0,
            }

        return {
            'total_recommendations': len(top_picks),
            'avg_confidence': top_picks['Confidence'].mean(),
            'avg_edge': top_picks['Edge'].mean(),
            'avg_expected_value': top_picks['Expected_Value'].mean(),
            'total_stake': top_picks['Stake'].sum(),
            'potential_roi': top_picks['Expected_Value'].mean(),
            'sports_breakdown': top_picks['Sport'].value_counts().to_dict() if 'Sport' in top_picks.columns else {},
        }

    def export_picks(self, picks: pd.DataFrame, output_file: str):
        """
        Export picks to Excel file.

        Args:
            picks: DataFrame of picks to export
            output_file: Path to output file
        """
        # Select relevant columns
        columns_to_export = [
            'Game', 'Pick', 'Odds', 'Confidence', 'Edge',
            'Expected_Value', 'Total_Score', 'Stake'
        ]

        # Add optional columns if they exist
        if 'Sport' in picks.columns:
            columns_to_export.insert(0, 'Sport')
        if 'Notes' in picks.columns:
            columns_to_export.append('Notes')

        export_data = picks[[col for col in columns_to_export if col in picks.columns]].copy()

        # Save to Excel
        export_data.to_excel(output_file, index=False, engine='openpyxl')
        print(f"Picks exported to: {output_file}")
