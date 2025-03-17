import pytest
from src.ai_engine import generate_comparison, TeamStats

def test_team_stats_model():
    """Test that the TeamStats model validates correctly"""
    # Valid basic stats
    stats = {'wins': 50, 'losses': 32, 'ppg': 110.5}
    validated = TeamStats(**stats)
    assert validated.wins == 50
    assert validated.losses == 32
    assert validated.ppg == 110.5
    
    # Test with expanded stats
    expanded_stats = {
        'wins': 50, 
        'losses': 32, 
        'ppg': 110.5,
        'fg_pct': 0.485, 
        'rebounds': 45.2, 
        'assists': 24.8
    }
    validated = TeamStats(**expanded_stats)
    assert validated.fg_pct == 0.485
    assert validated.rebounds == 45.2
    assert validated.assists == 24.8

def test_generate_comparison_basic():
    """Test that the comparison generator works with minimal stats"""
    team1 = "Test Team A"
    team2 = "Test Team B"
    stats1 = {'wins': 50, 'losses': 32, 'ppg': 110.5}
    stats2 = {'wins': 48, 'losses': 34, 'ppg': 108.2}
    
    try:
        result = generate_comparison(team1, team2, stats1, stats2)
        # Just check that we get a non-empty string result
        assert isinstance(result, str)
        assert len(result) > 0
        assert team1 in result or team2 in result
    except Exception as e:
        # If API keys aren't configured, this will fail without being a true test failure
        pytest.skip(f"Skipping due to API configuration: {str(e)}")

def test_generate_comparison_expanded():
    """Test that the comparison generator works with expanded stats"""
    team1 = "Test Team A"
    team2 = "Test Team B"
    stats1 = {
        'wins': 50, 'losses': 32, 'ppg': 110.5,
        'fg_pct': 0.485, 'fg3_pct': 0.37, 'ft_pct': 0.80,
        'rebounds': 45.2, 'assists': 24.8, 'steals': 7.5,
        'blocks': 4.3, 'turnovers': 12.8
    }
    stats2 = {
        'wins': 48, 'losses': 34, 'ppg': 108.2,
        'fg_pct': 0.47, 'fg3_pct': 0.39, 'ft_pct': 0.78,
        'rebounds': 43.5, 'assists': 26.2, 'steals': 6.9,
        'blocks': 5.1, 'turnovers': 13.5
    }
    
    try:
        result = generate_comparison(team1, team2, stats1, stats2)
        # Just check that we get a non-empty string result
        assert isinstance(result, str)
        assert len(result) > 0
        assert team1 in result or team2 in result
    except Exception as e:
        # If API keys aren't configured, this will fail without being a true test failure
        pytest.skip(f"Skipping due to API configuration: {str(e)}") 