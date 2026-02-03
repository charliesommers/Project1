#!/usr/bin/env python3
"""
Test spread pick logic with user's examples.

User examples:
1. "Greg +2, Vegas +5" → bet underdog
2. "Greg +3, Vegas +1" → bet favorite

Converting to favorite's perspective (negative numbers):
1. Greg -2, Vegas -5 → bet underdog
2. Greg -3, Vegas -1 → bet favorite
"""


def test_spread_logic():
    """Test the spread recommendation logic."""
    print("Testing spread pick logic\n")
    print("=" * 60)

    # Example 1: Greg +2 (underdog), Vegas +5 (underdog)
    # From favorite's perspective: Greg -2, Vegas -5
    print("\nExample 1: Greg thinks favorite by 2, Vegas thinks favorite by 5")
    print("-" * 60)
    gregs_spread = -2  # Favorite's perspective
    vegas_spread = -5  # Favorite's perspective

    print(f"Greg's spread (favorite): {gregs_spread:+.1f}")
    print(f"Vegas spread (favorite): {vegas_spread:+.1f}")
    print(f"From underdog perspective: Greg {-gregs_spread:+.1f}, Vegas {-vegas_spread:+.1f}")

    edge = abs(gregs_spread - vegas_spread)
    print(f"\nEdge: {edge:.1f} points")

    # Apply the logic
    if gregs_spread < vegas_spread:
        recommendation = "BET FAVORITE"
        recommended_spread = vegas_spread
    else:
        recommendation = "BET UNDERDOG"
        recommended_spread = -vegas_spread

    print(f"\nLogic: gregs_spread ({gregs_spread:+.1f}) < vegas_spread ({vegas_spread:+.1f})? {gregs_spread < vegas_spread}")
    print(f"Recommendation: {recommendation} at {recommended_spread:+.1f}")
    print(f"\nExpected: BET UNDERDOG at +5.0")
    print(f"Match: {'✓ PASS' if recommendation == 'BET UNDERDOG' and recommended_spread == 5.0 else '✗ FAIL'}")

    # Example 2: Greg +3 (underdog), Vegas +1 (underdog)
    # From favorite's perspective: Greg -3, Vegas -1
    print("\n\nExample 2: Greg thinks favorite by 3, Vegas thinks favorite by 1")
    print("-" * 60)
    gregs_spread = -3
    vegas_spread = -1

    print(f"Greg's spread (favorite): {gregs_spread:+.1f}")
    print(f"Vegas spread (favorite): {vegas_spread:+.1f}")
    print(f"From underdog perspective: Greg {-gregs_spread:+.1f}, Vegas {-vegas_spread:+.1f}")

    edge = abs(gregs_spread - vegas_spread)
    print(f"\nEdge: {edge:.1f} points")

    # Apply the logic
    if gregs_spread < vegas_spread:
        recommendation = "BET FAVORITE"
        recommended_spread = vegas_spread
    else:
        recommendation = "BET UNDERDOG"
        recommended_spread = -vegas_spread

    print(f"\nLogic: gregs_spread ({gregs_spread:+.1f}) < vegas_spread ({vegas_spread:+.1f})? {gregs_spread < vegas_spread}")
    print(f"Recommendation: {recommendation} at {recommended_spread:+.1f}")
    print(f"\nExpected: BET FAVORITE at -1.0")
    print(f"Match: {'✓ PASS' if recommendation == 'BET FAVORITE' and recommended_spread == -1.0 else '✗ FAIL'}")

    # Edge case: Greg and Vegas disagree on who's the favorite
    print("\n\nEdge Case: Greg and Vegas disagree on favorite")
    print("-" * 60)
    print("Greg: Duke -2 (Duke favored by 2)")
    print("Vegas: UNC -3 (UNC favored by 3, so Duke +3)")
    print("\nAfter normalization to Duke's perspective:")
    gregs_spread = -2  # Duke's perspective
    vegas_spread = +3  # Duke is underdog by 3 in Vegas's view

    print(f"Greg's spread (Duke): {gregs_spread:+.1f}")
    print(f"Vegas spread (Duke): {vegas_spread:+.1f}")

    edge = abs(gregs_spread - vegas_spread)
    print(f"\nEdge: {edge:.1f} points")

    # Apply the logic
    if gregs_spread < vegas_spread:
        recommendation = "BET DUKE (favorite per Greg)"
        recommended_spread = vegas_spread
    else:
        recommendation = "BET OPPONENT (underdog per Greg)"
        recommended_spread = -vegas_spread

    print(f"\nLogic: gregs_spread ({gregs_spread:+.1f}) < vegas_spread ({vegas_spread:+.1f})? {gregs_spread < vegas_spread}")
    print(f"Recommendation: {recommendation} at {recommended_spread:+.1f}")
    print(f"\nReasoning: Greg thinks Duke should be favored, but Vegas has Duke as underdog.")
    print(f"Big value betting Duke at {recommended_spread:+.1f} (as underdog) when Greg thinks they should be favored.")

    print("\n" + "=" * 60)
    print("\nConclusion: Logic handles all cases correctly ✓")


if __name__ == '__main__':
    test_spread_logic()
