import pytest
import os
from src.web_insights import get_web_insights

def test_get_web_insights_no_api_key():
    """Test that web insights gracefully handles missing API key"""
    # Temporarily unset the API key if it exists
    original_key = os.environ.get("NEWSAPI_KEY")
    if "NEWSAPI_KEY" in os.environ:
        del os.environ["NEWSAPI_KEY"]
    
    try:
        result = get_web_insights("Los Angeles Lakers", "Boston Celtics")
        assert isinstance(result, str)
        assert "NEWSAPI_KEY" in result  # Should mention the missing key
        assert "Los Angeles Lakers" in result
        assert "Boston Celtics" in result
    finally:
        # Restore the API key if it existed
        if original_key:
            os.environ["NEWSAPI_KEY"] = original_key

def test_get_web_insights_with_api_key():
    """Test that web insights works with an API key (if available)"""
    api_key = os.environ.get("NEWSAPI_KEY")
    
    # Skip test if no API key is available
    if not api_key:
        pytest.skip("No NEWSAPI_KEY found in environment")
    
    result = get_web_insights("Los Angeles Lakers", "Boston Celtics")
    assert isinstance(result, str)
    
    # Should provide some result that isn't the error message
    assert "NEWSAPI_KEY" not in result or "Add a NEWSAPI_KEY" not in result
    
    # If it found articles, it should mention "News" or have formatted article content
    # This is a loose check since results depend on external API
    assert "News" in result or "http" in result 