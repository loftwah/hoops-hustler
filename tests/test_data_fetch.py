import pytest
import os
import sqlite3
from src.data_fetch import get_team_stats, cache_stats, get_cached_stats

def test_get_team_stats_valid():
    stats = get_team_stats("Los Angeles Lakers")
    assert stats is not None
    assert 'wins' in stats
    assert 'losses' in stats
    assert 'ppg' in stats
    # Test expanded stats
    assert 'fg_pct' in stats
    assert 'rebounds' in stats
    assert 'assists' in stats

def test_get_team_stats_invalid():
    stats = get_team_stats("Fake Team")
    assert stats is None

def test_cache_functionality():
    # First ensure database exists
    assert os.path.exists('data/teams.db'), "Database file not found"
    
    # Get team stats which should trigger caching
    team_name = "Golden State Warriors"
    original_stats = get_team_stats(team_name)
    assert original_stats is not None
    
    # Verify the stats were cached
    cached_stats = get_cached_stats(team_name)
    assert cached_stats is not None
    
    # Compare important keys
    for key in ['wins', 'losses', 'ppg']:
        assert key in cached_stats
        assert cached_stats[key] == original_stats[key]
    
    # Verify directly from database
    conn = sqlite3.connect('data/teams.db')
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{team_name.replace(' ', '_')}'")
    result = cursor.fetchone()
    assert result is not None, "Team data wasn't cached in the database"
    conn.close()