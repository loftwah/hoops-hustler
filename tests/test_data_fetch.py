import pytest
from src.data_fetch import get_team_stats

def test_get_team_stats_valid():
    stats = get_team_stats("Los Angeles Lakers")
    assert stats is not None
    assert 'wins' in stats
    assert 'losses' in stats
    assert 'ppg' in stats

def test_get_team_stats_invalid():
    stats = get_team_stats("Fake Team")
    assert stats is None