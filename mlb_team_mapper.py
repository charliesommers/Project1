"""
MLB Team Name Mapper
Maps Greg's abbreviated team names to full ESPN team names.
"""

# MLB team name mappings: Greg's name -> ESPN full name
MLB_TEAM_MAPPINGS = {
    # American League East
    'yankees': 'New York Yankees',
    'red sox': 'Boston Red Sox',
    'blue jays': 'Toronto Blue Jays',
    'rays': 'Tampa Bay Rays',
    'orioles': 'Baltimore Orioles',

    # American League Central
    'white sox': 'Chicago White Sox',
    'guardians': 'Cleveland Guardians',
    'indians': 'Cleveland Guardians',  # Old name
    'tigers': 'Detroit Tigers',
    'royals': 'Kansas City Royals',
    'twins': 'Minnesota Twins',

    # American League West
    'astros': 'Houston Astros',
    'angels': 'Los Angeles Angels',
    'athletics': 'Oakland Athletics',
    "a's": 'Oakland Athletics',
    'mariners': 'Seattle Mariners',
    'rangers': 'Texas Rangers',

    # National League East
    'braves': 'Atlanta Braves',
    'marlins': 'Miami Marlins',
    'mets': 'New York Mets',
    'phillies': 'Philadelphia Phillies',
    'nationals': 'Washington Nationals',

    # National League Central
    'cubs': 'Chicago Cubs',
    'reds': 'Cincinnati Reds',
    'brewers': 'Milwaukee Brewers',
    'pirates': 'Pittsburgh Pirates',
    'cardinals': 'St. Louis Cardinals',
    'st louis cardinals': 'St. Louis Cardinals',
    'st. louis cardinals': 'St. Louis Cardinals',

    # National League West
    'diamondbacks': 'Arizona Diamondbacks',
    'd-backs': 'Arizona Diamondbacks',
    'dbacks': 'Arizona Diamondbacks',
    'rockies': 'Colorado Rockies',
    'dodgers': 'Los Angeles Dodgers',
    'padres': 'San Diego Padres',
    'giants': 'San Francisco Giants',
}

# Additional abbreviations
MLB_ABBREVIATIONS = {
    'nyy': 'New York Yankees',
    'bos': 'Boston Red Sox',
    'tor': 'Toronto Blue Jays',
    'tb': 'Tampa Bay Rays',
    'bal': 'Baltimore Orioles',

    'chw': 'Chicago White Sox',
    'cle': 'Cleveland Guardians',
    'det': 'Detroit Tigers',
    'kc': 'Kansas City Royals',
    'min': 'Minnesota Twins',

    'hou': 'Houston Astros',
    'laa': 'Los Angeles Angels',
    'oak': 'Oakland Athletics',
    'sea': 'Seattle Mariners',
    'tex': 'Texas Rangers',

    'atl': 'Atlanta Braves',
    'mia': 'Miami Marlins',
    'nym': 'New York Mets',
    'phi': 'Philadelphia Phillies',
    'wsh': 'Washington Nationals',

    'chc': 'Chicago Cubs',
    'cin': 'Cincinnati Reds',
    'mil': 'Milwaukee Brewers',
    'pit': 'Pittsburgh Pirates',
    'stl': 'St. Louis Cardinals',

    'ari': 'Arizona Diamondbacks',
    'az': 'Arizona Diamondbacks',
    'col': 'Colorado Rockies',
    'lad': 'Los Angeles Dodgers',
    'sd': 'San Diego Padres',
    'sf': 'San Francisco Giants',
}


def normalize_mlb_team_name(team_name: str) -> str:
    """
    Normalize Greg's abbreviated MLB team name to full ESPN name.

    Args:
        team_name: Team name from Greg's sheet (e.g., "Dodgers", "Blue Jays")

    Returns:
        Full ESPN team name (e.g., "Los Angeles Dodgers", "Toronto Blue Jays")
    """
    if not team_name:
        return team_name

    team_lower = team_name.lower().strip()

    # Check direct mapping
    if team_lower in MLB_TEAM_MAPPINGS:
        return MLB_TEAM_MAPPINGS[team_lower]

    # Check abbreviations
    if team_lower in MLB_ABBREVIATIONS:
        return MLB_ABBREVIATIONS[team_lower]

    # Return original if no mapping found
    return team_name


def match_mlb_teams(team1: str, team2: str) -> bool:
    """
    Check if two MLB team names refer to the same team.

    Args:
        team1: First team name
        team2: Second team name

    Returns:
        True if teams match, False otherwise
    """
    if not team1 or not team2:
        return False

    # Normalize both names
    norm1 = normalize_mlb_team_name(team1)
    norm2 = normalize_mlb_team_name(team2)

    # Direct match after normalization
    if norm1.lower() == norm2.lower():
        return True

    # Check if one contains the other (for cases like "Los Angeles Dodgers" vs "Dodgers")
    t1 = norm1.lower()
    t2 = norm2.lower()

    if len(t1) >= 4 and len(t2) >= 4:
        if t1 in t2 or t2 in t1:
            return True

    return False
