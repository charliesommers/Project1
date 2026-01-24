"""
NCAA Basketball Team Conference Mappings
Maps team names to their conferences for the 2025-26 season
"""

TEAM_CONFERENCES = {
    # ACC
    'boston college': 'ACC',
    'california': 'ACC',
    'clemson': 'ACC',
    'duke': 'ACC',
    'florida state': 'ACC',
    'georgia tech': 'ACC',
    'louisville': 'ACC',
    'miami': 'ACC',
    'north carolina': 'UNC',
    'nc state': 'ACC',
    'north carolina state': 'ACC',
    'notre dame': 'ACC',
    'pittsburgh': 'ACC',
    'stanford': 'ACC',
    'syracuse': 'ACC',
    'virginia': 'ACC',
    'virginia tech': 'ACC',
    'wake forest': 'ACC',

    # Big Ten
    'illinois': 'Big Ten',
    'indiana': 'Big Ten',
    'iowa': 'Big Ten',
    'maryland': 'Big Ten',
    'michigan': 'Big Ten',
    'michigan state': 'Big Ten',
    'minnesota': 'Big Ten',
    'nebraska': 'Big Ten',
    'northwestern': 'Big Ten',
    'ohio state': 'Big Ten',
    'oregon': 'Big Ten',
    'penn state': 'Big Ten',
    'purdue': 'Big Ten',
    'rutgers': 'Big Ten',
    'ucla': 'Big Ten',
    'usc': 'Big Ten',
    'southern california': 'Big Ten',
    'washington': 'Big Ten',
    'wisconsin': 'Big Ten',

    # Big 12
    'arizona': 'Big 12',
    'arizona state': 'Big 12',
    'baylor': 'Big 12',
    'byu': 'Big 12',
    'cincinnati': 'Big 12',
    'colorado': 'Big 12',
    'houston': 'Big 12',
    'iowa state': 'Big 12',
    'kansas': 'Big 12',
    'kansas state': 'Big 12',
    'oklahoma state': 'Big 12',
    'tcu': 'Big 12',
    'texas tech': 'Big 12',
    'ucf': 'Big 12',
    'utah': 'Big 12',
    'west virginia': 'Big 12',

    # SEC
    'alabama': 'SEC',
    'arkansas': 'SEC',
    'auburn': 'SEC',
    'florida': 'SEC',
    'georgia': 'SEC',
    'kentucky': 'SEC',
    'lsu': 'SEC',
    'louisiana state': 'SEC',
    'ole miss': 'SEC',
    'mississippi': 'SEC',
    'mississippi state': 'SEC',
    'missouri': 'SEC',
    'oklahoma': 'SEC',
    'south carolina': 'SEC',
    'tennessee': 'SEC',
    'texas': 'SEC',
    'texas a&m': 'SEC',
    'vanderbilt': 'SEC',

    # Big East
    'butler': 'Big East',
    'connecticut': 'Big East',
    'uconn': 'Big East',
    'creighton': 'Big East',
    'depaul': 'Big East',
    'georgetown': 'Big East',
    'marquette': 'Big East',
    'providence': 'Big East',
    'seton hall': 'Big East',
    'st. john\'s': 'Big East',
    'villanova': 'Big East',
    'xavier': 'Big East',

    # American Athletic
    'charlotte': 'AAC',
    'east carolina': 'AAC',
    'florida atlantic': 'AAC',
    'memphis': 'AAC',
    'navy': 'AAC',
    'north texas': 'AAC',
    'rice': 'AAC',
    'south florida': 'AAC',
    'temple': 'AAC',
    'tulane': 'AAC',
    'tulsa': 'AAC',
    'uab': 'AAC',
    'utsa': 'AAC',

    # Atlantic 10
    'davidson': 'A-10',
    'dayton': 'A-10',
    'duquesne': 'A-10',
    'fordham': 'A-10',
    'george mason': 'A-10',
    'george washington': 'A-10',
    'la salle': 'A-10',
    'loyola chicago': 'A-10',
    'massachusetts': 'A-10',
    'rhode island': 'A-10',
    'richmond': 'A-10',
    'saint joseph\'s': 'A-10',
    'saint louis': 'A-10',
    'st. bonaventure': 'A-10',
    'vcu': 'A-10',
    'virginia commonwealth': 'A-10',

    # Mountain West
    'air force': 'MWC',
    'boise state': 'MWC',
    'colorado state': 'MWC',
    'fresno state': 'MWC',
    'nevada': 'MWC',
    'new mexico': 'MWC',
    'san diego state': 'MWC',
    'san jose state': 'MWC',
    'unlv': 'MWC',
    'nevada las vegas': 'MWC',
    'utah state': 'MWC',
    'wyoming': 'MWC',

    # WCC
    'gonzaga': 'WCC',
    'loyola marymount': 'WCC',
    'pacific': 'WCC',
    'pepperdine': 'WCC',
    'portland': 'WCC',
    'saint mary\'s': 'WCC',
    'san diego': 'WCC',
    'san francisco': 'WCC',
    'santa clara': 'WCC',

    # Additional major conferences and teams
    'wichita state': 'AAC',
    'gonzaga': 'WCC',
    'saint mary\'s': 'WCC',
}

def get_conference(team_name: str) -> str:
    """
    Get conference for a team name.

    Args:
        team_name: Team name to look up

    Returns:
        Conference abbreviation or 'Other' if not found
    """
    team_lower = team_name.lower().strip()

    # Direct lookup
    if team_lower in TEAM_CONFERENCES:
        return TEAM_CONFERENCES[team_lower]

    # Partial match
    for team_key, conference in TEAM_CONFERENCES.items():
        if team_key in team_lower or team_lower in team_key:
            return conference

    return 'Other'
