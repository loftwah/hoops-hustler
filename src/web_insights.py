import os
import requests
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

def get_web_insights(team1, team2):
    """Fetch recent news articles about the teams using NewsAPI."""
    api_key = os.getenv("NEWSAPI_KEY")
    
    # If no API key is provided, return a default message
    if not api_key:
        return f"Want more insights? Add a NEWSAPI_KEY to your .env file to get recent news about {team1} and {team2}."
    
    try:
        # Fetch news about both teams
        url = f"https://newsapi.org/v2/everything?q=NBA {team1} OR {team2}&apiKey={api_key}&sortBy=publishedAt&language=en&pageSize=5"
        response = requests.get(url)
        data = response.json()
        
        # Check if the request was successful
        if response.status_code != 200:
            return f"Couldn't fetch news insights: {data.get('message', 'Unknown error')}"
        
        articles = data.get('articles', [])
        
        # If no articles found, try with just NBA and the team names
        if not articles:
            return f"No recent news found for {team1} or {team2}."
        
        # Format the top 2 articles
        insights = "Recent NBA News:\n"
        for i, article in enumerate(articles[:2]):
            source = article['source']['name']
            title = article['title']
            url = article['url']
            published = article['publishedAt'][:10]  # Just the date part
            insights += f"{i+1}. {title} ({source}, {published}) - {url}\n"
        
        # Add a general insight based on article count
        team1_count = sum(1 for article in articles if team1.lower() in article['title'].lower())
        team2_count = sum(1 for article in articles if team2.lower() in article['title'].lower())
        
        if team1_count > team2_count:
            insights += f"\n{team1} is generating more buzz in recent news."
        elif team2_count > team1_count:
            insights += f"\n{team2} is generating more buzz in recent news."
        
        return insights
        
    except Exception as e:
        return f"Error fetching news insights: {str(e)}"