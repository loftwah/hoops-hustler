from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamdashboardbygeneralsplits
import numpy as np
import pandas as pd
import os

# Enable SQLite caching
from sqlalchemy import create_engine
import os.path

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)
engine = create_engine('sqlite:///data/teams.db')

def get_team_id(team_name):
    team = [t for t in teams.get_teams() if t['full_name'].lower() == team_name.lower()]
    return team[0]['id'] if team else None

def cache_stats(team_name, stats):
    """Cache team stats to SQLite database."""
    pd.DataFrame([stats]).to_sql(team_name.replace(' ', '_'), engine, if_exists='replace')

def get_cached_stats(team_name):
    """Retrieve cached stats if available."""
    table_name = team_name.replace(' ', '_')
    try:
        if engine.has_table(table_name):
            return pd.read_sql(f"SELECT * FROM {table_name}", engine).iloc[0].to_dict()
    except Exception:
        pass
    return None

def get_team_stats(team_name):
    # Try to get stats from cache first
    cached = get_cached_stats(team_name)
    if cached:
        # Remove index column if present
        if 'index' in cached:
            del cached['index']
        return cached
    
    team_id = get_team_id(team_name)
    if not team_id:
        return None
    
    try:
        dashboard = teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits(team_id=team_id)
        stats = dashboard.get_dict()['resultSets'][0]['rowSet'][0]
        
        # Expanded stats collection
        result = pd.Series({
            'wins': stats[8],
            'losses': stats[9],
            'ppg': np.round(stats[20], 2),  # Points per game
            'fg_pct': np.round(stats[10], 3),  # Field goal percentage
            'fg3_pct': np.round(stats[13], 3),  # 3-point percentage
            'ft_pct': np.round(stats[16], 3),  # Free throw percentage
            'rebounds': np.round(stats[23], 1),  # Total rebounds
            'assists': np.round(stats[24], 1),  # Assists
            'steals': np.round(stats[26], 1),  # Steals
            'blocks': np.round(stats[27], 1),  # Blocks
            'turnovers': np.round(stats[25], 1)  # Turnovers
        }).to_dict()
        
        # Cache the stats
        cache_stats(team_name, result)
        
        return result
    except Exception as e:
        print(f"Error fetching stats for {team_name}: {e}")
        return None