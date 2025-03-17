import streamlit as st
from src.data_fetch import get_team_stats
from src.ai_engine import generate_comparison
from src.web_insights import get_web_insights
import altair as alt
import pandas as pd

st.title("Hoops Hustler: NBA Team Showdown")

# Get all NBA teams for dropdowns
from nba_api.stats.static import teams
team_list = [team['full_name'] for team in teams.get_teams()]
team1 = st.selectbox("Select Team 1", team_list)
team2 = st.selectbox("Select Team 2", team_list)

if st.button("Compare"):
    stats1 = get_team_stats(team1)
    stats2 = get_team_stats(team2)
    
    if stats1 and stats2:
        insights = get_web_insights(team1, team2)
        comparison = generate_comparison(team1, team2, stats1, stats2)
        
        # Display raw stats
        st.write(f"**{team1} Stats:** {stats1}")
        st.write(f"**{team2} Stats:** {stats2}")
        
        # Simple bar chart with Altair
        data = pd.DataFrame({
            'Team': [team1, team2],
            'PPG': [stats1['ppg'], stats2['ppg']]
        })
        chart = alt.Chart(data).mark_bar().encode(
            x='Team', y='PPG', color='Team'
        ).properties(width=300, height=200)
        st.altair_chart(chart)
        
        # Insights and comparison
        st.write(f"**Insights:** {insights}")
        st.write(f"**Hustler’s Take:** {comparison}")
    else:
        st.error("Couldn’t fetch stats. Check team names!")