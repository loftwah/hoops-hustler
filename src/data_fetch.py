from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamdashboardbygeneralsplits
import numpy as np
import pandas as pd

def get_team_id(team_name):
    team = [t for t in teams.get_teams() if t['full_name'].lower() == team_name.lower()]
    return team[0]['id'] if team else None

def get_team_stats(team_name):
    team_id = get_team_id(team_name)
    if not team_id:
        return None
    
    try:
        dashboard = teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits(team_id=team_id)
        stats = dashboard.get_dict()['resultSets'][0]['rowSet'][0]
        
        # Use numpy for basic calculations if needed (e.g., averaging)
        wins = stats[8]
        losses = stats[9]
        ppg = np.round(stats[20], 2)  # Points per game, rounded
        
        # Return as a pandas Series for consistency
        return pd.Series({
            'wins': wins,
            'losses': losses,
            'ppg': ppg
        }).to_dict()
    except Exception:
        return None

# Optional SQLite caching (uncomment to use with sqlalchemy)
# from sqlalchemy import create_engine
# engine = create_engine('sqlite:///../data/teams.db')
# def cache_stats(team_name, stats):
#     pd.DataFrame([stats]).to_sql(team_name.replace(' ', '_'), engine, if_exists='replace')