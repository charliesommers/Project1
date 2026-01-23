"""
Excel Data Parser for Sports Gambling Handicapping Data
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import sys


class HandicappingDataParser:
    """Parses and validates Excel handicapping data."""

    REQUIRED_COLUMNS = ['Game', 'Pick', 'Odds', 'Confidence']
    OPTIONAL_COLUMNS = ['Sport', 'Edge', 'Stake', 'Win_Probability', 'Notes']

    def __init__(self, file_path: str):
        """
        Initialize the parser with an Excel file path.

        Args:
            file_path: Path to Excel file containing handicapping data
        """
        self.file_path = file_path
        self.data = None
        self.raw_data = None

    def load_data(self) -> pd.DataFrame:
        """
        Load and validate Excel data.

        Returns:
            Pandas DataFrame with validated handicapping data
        """
        try:
            # Try reading Excel file
            self.raw_data = pd.read_excel(self.file_path, engine='openpyxl')
        except FileNotFoundError:
            print(f"Error: File not found: {self.file_path}")
            sys.exit(1)
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            sys.exit(1)

        # Validate required columns
        missing_cols = [col for col in self.REQUIRED_COLUMNS if col not in self.raw_data.columns]
        if missing_cols:
            print(f"Error: Missing required columns: {', '.join(missing_cols)}")
            print(f"Required columns: {', '.join(self.REQUIRED_COLUMNS)}")
            print(f"Found columns: {', '.join(self.raw_data.columns)}")
            sys.exit(1)

        # Create working copy
        self.data = self.raw_data.copy()

        # Clean and validate data
        self._clean_data()
        self._validate_data()
        self._calculate_derived_metrics()

        return self.data

    def _clean_data(self):
        """Clean and standardize data."""
        # Remove rows with missing required fields
        for col in self.REQUIRED_COLUMNS:
            self.data = self.data[self.data[col].notna()]

        # Strip whitespace from string columns
        string_cols = ['Game', 'Pick', 'Sport', 'Notes']
        for col in string_cols:
            if col in self.data.columns:
                self.data[col] = self.data[col].astype(str).str.strip()

        # Convert numeric columns
        self.data['Confidence'] = pd.to_numeric(self.data['Confidence'], errors='coerce')

        if 'Edge' in self.data.columns:
            self.data['Edge'] = pd.to_numeric(self.data['Edge'], errors='coerce')

        if 'Stake' in self.data.columns:
            self.data['Stake'] = pd.to_numeric(self.data['Stake'], errors='coerce')

        if 'Win_Probability' in self.data.columns:
            self.data['Win_Probability'] = pd.to_numeric(self.data['Win_Probability'], errors='coerce')

        # Remove rows with invalid confidence values
        self.data = self.data[self.data['Confidence'].notna()]

    def _validate_data(self):
        """Validate data ranges and formats."""
        # Confidence should be 0-100
        invalid_confidence = (self.data['Confidence'] < 0) | (self.data['Confidence'] > 100)
        if invalid_confidence.any():
            print(f"Warning: {invalid_confidence.sum()} rows have invalid confidence values (not 0-100). These will be clamped.")
            self.data.loc[self.data['Confidence'] < 0, 'Confidence'] = 0
            self.data.loc[self.data['Confidence'] > 100, 'Confidence'] = 100

        # Win_Probability should be 0-100 if present
        if 'Win_Probability' in self.data.columns:
            self.data['Win_Probability'] = self.data['Win_Probability'].fillna(self.data['Confidence'])
            self.data.loc[self.data['Win_Probability'] < 0, 'Win_Probability'] = 0
            self.data.loc[self.data['Win_Probability'] > 100, 'Win_Probability'] = 100

    def _calculate_derived_metrics(self):
        """Calculate additional metrics from the data."""
        # Convert American odds to implied probability
        self.data['Implied_Probability'] = self.data['Odds'].apply(self._american_odds_to_probability)

        # Calculate edge if not provided
        if 'Edge' not in self.data.columns or self.data['Edge'].isna().all():
            if 'Win_Probability' in self.data.columns:
                self.data['Edge'] = self.data['Win_Probability'] - self.data['Implied_Probability']
            else:
                # Use confidence as proxy for win probability
                self.data['Edge'] = self.data['Confidence'] - self.data['Implied_Probability']

        # Calculate expected value (EV)
        self.data['Expected_Value'] = self._calculate_expected_value(
            self.data['Win_Probability'] if 'Win_Probability' in self.data.columns else self.data['Confidence'],
            self.data['Odds']
        )

        # Set default stake if not provided
        if 'Stake' not in self.data.columns or self.data['Stake'].isna().all():
            self.data['Stake'] = 1.0
        else:
            self.data['Stake'] = self.data['Stake'].fillna(1.0)

    @staticmethod
    def _american_odds_to_probability(odds) -> float:
        """
        Convert American odds to implied probability percentage.

        Args:
            odds: American odds (e.g., -110, +150)

        Returns:
            Implied probability as percentage (0-100)
        """
        try:
            odds = float(odds)
            if odds < 0:
                # Favorite
                prob = (-odds) / (-odds + 100) * 100
            else:
                # Underdog
                prob = 100 / (odds + 100) * 100
            return prob
        except (ValueError, TypeError):
            return 50.0  # Default to 50% if odds can't be parsed

    @staticmethod
    def _calculate_expected_value(win_prob: pd.Series, odds: pd.Series) -> pd.Series:
        """
        Calculate expected value (EV) for each bet.

        Args:
            win_prob: Win probability (0-100)
            odds: American odds

        Returns:
            Expected value as percentage
        """
        def calc_ev(prob, odd):
            try:
                prob = float(prob) / 100  # Convert to decimal
                odd = float(odd)

                if odd < 0:
                    win_amount = 100 / (-odd)
                else:
                    win_amount = odd / 100

                ev = (prob * win_amount) - ((1 - prob) * 1)
                return ev * 100  # Return as percentage
            except (ValueError, TypeError):
                return 0.0

        return pd.Series([calc_ev(p, o) for p, o in zip(win_prob, odds)])

    def get_summary_stats(self) -> Dict:
        """Get summary statistics about the dataset."""
        if self.data is None:
            return {}

        return {
            'total_picks': len(self.data),
            'avg_confidence': self.data['Confidence'].mean(),
            'avg_edge': self.data['Edge'].mean() if 'Edge' in self.data.columns else 0,
            'avg_expected_value': self.data['Expected_Value'].mean(),
            'sports': self.data['Sport'].unique().tolist() if 'Sport' in self.data.columns else ['All'],
            'positive_ev_picks': (self.data['Expected_Value'] > 0).sum(),
        }
