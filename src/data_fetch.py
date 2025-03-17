from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamdashboardbygeneralsplits, commonteamroster, teamgamelog
import numpy as np
import pandas as pd
import os
from sqlalchemy import create_engine

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)
engine = create_engine('sqlite:///data/teams.db')

def get_team_id(team_name):
    team = [t for t in teams.get_teams() if t['full_name'].lower() == team_name.lower()]
    return team[0]['id'] if team else None

def cache_stats(team_name, stats):
    """Cache team stats to SQLite database."""
    pd.DataFrame([stats]).to_sql(team_name.replace(' ', '_'), engine, if_exists='replace', index=False)

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
        if 'index' in cached:
            del cached['index']
        return cached

    team_id = get_team_id(team_name)
    if not team_id:
        return None

    try:
        dashboard = teamdashboardbygeneralsplits.TeamDashboardByGeneralSplits(team_id=team_id)
        data = dashboard.get_dict()['resultSets'][0]
        headers = data['headers']
        stats_row = data['rowSet'][0]
        mapping = dict(zip(headers, stats_row))
        result = {
            'wins': mapping.get('W', None),
            'losses': mapping.get('L', None),
            'ppg': round(mapping.get('PTS', 0), 2) if mapping.get('PTS', None) is not None else None,
            'fg_pct': round(mapping.get('FG_PCT', 0), 3) if mapping.get('FG_PCT', None) is not None else None,
            'fg3_pct': round(mapping.get('FG3_PCT', 0), 3) if mapping.get('FG3_PCT', None) is not None else None,
            'ft_pct': round(mapping.get('FT_PCT', 0), 3) if mapping.get('FT_PCT', None) is not None else None,
            'rebounds': round(mapping.get('REB', 0), 1) if mapping.get('REB', None) is not None else None,
            'assists': round(mapping.get('AST', 0), 1) if mapping.get('AST', None) is not None else None,
            'steals': round(mapping.get('STL', 0), 1) if mapping.get('STL', None) is not None else None,
            'blocks': round(mapping.get('BLK', 0), 1) if mapping.get('BLK', None) is not None else None,
            'turnovers': round(mapping.get('TOV', 0), 1) if mapping.get('TOV', None) is not None else None
        }
        cache_stats(team_name, result)
        return result
    except Exception as e:
        print(f"Error fetching stats for {team_name}: {e}")
        return None

def get_team_roster(team_name):
    """Fetch the team roster and player details."""
    team_id = get_team_id(team_name)
    if not team_id:
        return []
    try:
        roster = commonteamroster.CommonTeamRoster(team_id=team_id)
        headers = roster.get_dict()['resultSets'][0]['headers']
        players = roster.get_dict()['resultSets'][0]['rowSet']
        players_data = [dict(zip(headers, player)) for player in players]
        return players_data
    except Exception as e:
        print(f"Error fetching roster for {team_name}: {e}")
        return []

def get_team_history(team_name, season='2022-23'):
    """Fetch historical game logs for the team."""
    team_id = get_team_id(team_name)
    if not team_id:
        return None
    try:
        gamelog = teamgamelog.TeamGameLog(team_id=team_id, season=season)
        data = gamelog.get_dict()['resultSets'][0]['rowSet']
        columns = gamelog.get_dict()['resultSets'][0]['headers']
        return pd.DataFrame(data, columns=columns)
    except Exception as e:
        print(f"Error fetching historical data for {team_name}: {e}")
        return None
