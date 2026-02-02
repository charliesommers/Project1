"""
Daily Picks Generator
Generates betting recommendations based on Greg's totals vs sportsbook totals
FOCUS: Totals only (Over/Under), no spread betting
"""
import pandas as pd
from typing import Dict, List, Optional
from datetime import datetime
from team_conferences import get_conference


class DailyPicksGenerator:
    """
    Generates daily betting picks based on totals strategy.

    Strategy:
    - Bet UNDER when Greg's total is ≥5 points below sportsbook total
    - Bet OVER when Greg's total is ≥3 points above sportsbook total
    """

    def __init__(
        self,
        under_threshold: float = 5.0,
        over_threshold: float = 3.0
    ):
        """
        Initialize picks generator.

        Args:
            under_threshold: Points below sportsbook to bet under (default: 5)
            over_threshold: Points above sportsbook to bet over (default: 3)
        """
        self.under_threshold = under_threshold
        self.over_threshold = over_threshold

    def generate_spread_picks(
        self,
        gregs_games: List[Dict],
        sportsbook_data: List[Dict],
        conferences: List[str] = None
    ) -> List[Dict]:
        """
        Generate spread picks for specific conferences.

        Args:
            gregs_games: List of games from Greg's parser
            sportsbook_data: List of games with sportsbook odds
            conferences: List of conferences to filter (e.g., ['ACC', 'SEC', 'Big Ten'])

        Returns:
            List of spread picks with edges
        """
        spread_picks = []

        for gregs_game in gregs_games:
            # Find matching sportsbook game
            sportsbook_game = self._match_game(gregs_game, sportsbook_data)

            if not sportsbook_game:
                continue

            # Get spreads
            gregs_spread = gregs_game.get('spread')  # Always favorite's spread (negative)
            sportsbook_home_spread = sportsbook_game.get('spread')  # Home team's spread

            if gregs_spread is None or sportsbook_home_spread is None:
                continue

            # Get teams
            favorite = gregs_game['favorite']
            underdog = gregs_game['underdog']
            home_team = sportsbook_game.get('home_team', '')
            away_team = sportsbook_game.get('away_team', '')

            # Normalize sportsbook spread to favorite's perspective
            # If favorite is home, use home spread directly
            # If favorite is away, flip the spread sign
            from scores_fetcher import ScoresFetcher
            fetcher = ScoresFetcher()

            if fetcher._teams_match(favorite, home_team):
                # Favorite is home
                sportsbook_spread = sportsbook_home_spread
            elif fetcher._teams_match(favorite, away_team):
                # Favorite is away, flip the spread
                sportsbook_spread = -sportsbook_home_spread
            else:
                # Can't determine which team is favorite in sportsbook data
                continue

            # Now both spreads are from favorite's perspective (both negative)
            # Calculate edge
            edge = abs(gregs_spread - sportsbook_spread)

            # Determine pick recommendation
            # If Greg's spread is MORE negative (e.g., -10 vs -7):
            #   Greg thinks favorite will win by more → Bet FAVORITE at sportsbook line (-7)
            # If Greg's spread is LESS negative (e.g., -5 vs -10):
            #   Greg thinks favorite will win by less → Bet UNDERDOG at sportsbook line (+10)
            if gregs_spread < sportsbook_spread:
                recommended_team = favorite
                recommended_spread = sportsbook_spread
            else:
                recommended_team = underdog
                recommended_spread = -sportsbook_spread  # Flip to underdog's perspective

            # Validation: Edge should make sense
            # If edge is very large (>10), print warning for manual review
            if edge > 10:
                print(f"⚠️  Large edge detected ({edge:.1f}): {favorite} vs {underdog}")
                print(f"   Greg: {gregs_spread:+.1f} | Book: {sportsbook_spread:+.1f}")
                print(f"   Recommendation: {recommended_team} {recommended_spread:+.1f}")

            # Get conference
            conference = get_conference(favorite)
            if conference == 'Other':
                conference = get_conference(underdog)

            # Filter by conference if specified
            if conferences and conference not in conferences:
                continue

            spread_picks.append({
                'date': gregs_game['date'],
                'matchup': gregs_game['matchup'],
                'favorite': favorite,
                'underdog': underdog,
                'gregs_spread': gregs_spread,
                'sportsbook_spread': sportsbook_spread,
                'sportsbook_home_spread': sportsbook_home_spread,  # Original for reference
                'edge': edge,
                'recommended_team': recommended_team,
                'recommended_spread': recommended_spread,
                'conference': conference,
                'game_time': sportsbook_game.get('commence_time', ''),
                'bookmaker': sportsbook_game.get('source_bookmaker', ''),
                'away_team': away_team,
                'home_team': home_team
            })

        # Sort by edge (biggest edges first)
        spread_picks.sort(key=lambda x: x['edge'], reverse=True)

        return spread_picks

    def generate_picks(
        self,
        gregs_games: List[Dict],
        sportsbook_data: List[Dict]
    ) -> List[Dict]:
        """
        Generate picks by comparing Greg's totals to sportsbook totals.

        Args:
            gregs_games: List of games from Greg's parser
            sportsbook_data: List of games with sportsbook totals

        Returns:
            List of recommended picks
        """
        picks = []

        for gregs_game in gregs_games:
            # Find matching sportsbook game
            sportsbook_game = self._match_game(gregs_game, sportsbook_data)

            if not sportsbook_game:
                continue

            # Get totals
            gregs_total = gregs_game['total']
            sportsbook_total = sportsbook_game.get('total')

            if not sportsbook_total:
                continue

            # Calculate edge
            edge = gregs_total - sportsbook_total

            # Always determine a pick based on Greg vs sportsbook
            # (regardless of threshold)
            if edge < 0:
                # Greg's line is LOWER - bet UNDER
                pick = 'UNDER'
            else:
                # Greg's line is HIGHER or EQUAL - bet OVER
                pick = 'OVER'

            # Determine confidence
            confidence = 'medium'
            if pick == 'UNDER':
                if abs(edge) >= 7:
                    confidence = 'high'
                elif abs(edge) >= 6:
                    confidence = 'medium-high'
            elif pick == 'OVER':
                if edge >= 5:
                    confidence = 'high'
                elif edge >= 4:
                    confidence = 'medium-high'

            # Get conference (try both teams, prefer favorite)
            conference = get_conference(gregs_game['favorite'])
            if conference == 'Other':
                conference = get_conference(gregs_game['underdog'])

            # Get away/home teams for Bet365-style display
            away_team = sportsbook_game.get('away_team', '')
            home_team = sportsbook_game.get('home_team', '')

            picks.append({
                'date': gregs_game['date'],
                'matchup': gregs_game['matchup'],
                'favorite': gregs_game['favorite'],
                'underdog': gregs_game['underdog'],
                'pick': pick,
                'gregs_total': gregs_total,
                'sportsbook_total': sportsbook_total,
                'edge': edge,
                'confidence': confidence,
                'reasoning': self._get_reasoning(pick, edge),
                'game_time': sportsbook_game.get('commence_time', ''),
                'bookmaker': sportsbook_game.get('source_bookmaker', ''),
                'conference': conference,
                'away_team': away_team,
                'home_team': home_team
            })

        # Sort by absolute edge (biggest edges first)
        picks.sort(key=lambda x: abs(x['edge']), reverse=True)

        return picks

    def _match_game(self, gregs_game: Dict, sportsbook_games: List[Dict]) -> Optional[Dict]:
        """Match Greg's game to sportsbook game."""
        from scores_fetcher import ScoresFetcher
        fetcher = ScoresFetcher()

        gregs_fav = gregs_game['favorite']
        gregs_dog = gregs_game['underdog']

        for sb_game in sportsbook_games:
            home = sb_game.get('home_team', '')
            away = sb_game.get('away_team', '')

            # Check if teams match
            if (fetcher._teams_match(gregs_fav, home) and fetcher._teams_match(gregs_dog, away)) or \
               (fetcher._teams_match(gregs_fav, away) and fetcher._teams_match(gregs_dog, home)):
                return sb_game

        return None

    def _get_reasoning(self, pick: str, edge: float) -> str:
        """Generate reasoning text for the pick."""
        edge_abs = abs(edge)

        if pick == 'UNDER':
            return f"Greg's total is {edge_abs:.1f} points lower than sportsbook (edge ≥{self.under_threshold})"
        elif pick == 'OVER':
            return f"Greg's total is {edge_abs:.1f} points higher than sportsbook (edge ≥{self.over_threshold})"

        return ""

    def get_picks_dataframe(self, picks: List[Dict]) -> pd.DataFrame:
        """Convert picks to DataFrame."""
        if not picks:
            return pd.DataFrame()

        df = pd.DataFrame(picks)

        # Reorder columns
        column_order = [
            'matchup', 'pick', 'edge', 'confidence',
            'gregs_total', 'sportsbook_total', 'reasoning'
        ]

        return df[[col for col in column_order if col in df.columns]]

    def get_picks_summary(self, picks: List[Dict]) -> Dict:
        """Get summary of picks."""
        if not picks:
            return {'total_picks': 0}

        over_picks = [p for p in picks if p['pick'] == 'OVER']
        under_picks = [p for p in picks if p['pick'] == 'UNDER']

        high_conf = [p for p in picks if p['confidence'] == 'high']

        return {
            'total_picks': len(picks),
            'over_picks': len(over_picks),
            'under_picks': len(under_picks),
            'high_confidence_picks': len(high_conf),
            'avg_edge': sum(abs(p['edge']) for p in picks) / len(picks),
            'max_edge': max(abs(p['edge']) for p in picks),
            'confidence_breakdown': self._get_confidence_breakdown(picks)
        }

    def _get_confidence_breakdown(self, picks: List[Dict]) -> Dict:
        """Get breakdown of picks by confidence level."""
        breakdown = {}
        for pick in picks:
            conf = pick['confidence']
            breakdown[conf] = breakdown.get(conf, 0) + 1
        return breakdown

    def filter_picks(
        self,
        picks: List[Dict],
        min_edge: Optional[float] = None,
        confidence_level: Optional[str] = None,
        pick_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Filter picks based on criteria.

        Args:
            picks: List of picks
            min_edge: Minimum absolute edge
            confidence_level: Filter by confidence (high, medium-high, medium)
            pick_type: Filter by pick type (OVER, UNDER)

        Returns:
            Filtered list of picks
        """
        filtered = picks

        if min_edge:
            filtered = [p for p in filtered if abs(p['edge']) >= min_edge]

        if confidence_level:
            filtered = [p for p in filtered if p['confidence'] == confidence_level]

        if pick_type:
            filtered = [p for p in filtered if p['pick'] == pick_type.upper()]

        return filtered
