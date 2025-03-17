import streamlit as st
from src.data_fetch import get_team_stats
from src.ai_engine import generate_comparison
from src.web_insights import get_web_insights
import altair as alt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

st.set_page_config(page_title="Hoops Hustler: NBA Team Showdown", page_icon="🏀", layout="wide")

st.title("🏀 Hoops Hustler: NBA Team Showdown")
st.markdown("### Compare NBA teams with stats and AI-powered analysis")

# Cache stats to avoid redundant API calls
@st.cache_data(ttl=3600)  # Cache for 1 hour
def cached_team_stats(team_name):
    return get_team_stats(team_name)

# Get all NBA teams for dropdowns
from nba_api.stats.static import teams
team_list = [team['full_name'] for team in teams.get_teams()]

# Sidebar for options
st.sidebar.title("Options")
team1 = st.sidebar.selectbox("Select Team 1", team_list, index=team_list.index("Denver Nuggets") if "Denver Nuggets" in team_list else 0)
team2 = st.sidebar.selectbox("Select Team 2", team_list, index=team_list.index("Miami Heat") if "Miami Heat" in team_list else 1)

# Let users select which stats to display
all_stats = ['wins', 'losses', 'ppg', 'fg_pct', 'fg3_pct', 'ft_pct', 'rebounds', 'assists', 'steals', 'blocks', 'turnovers']
stat_labels = {
    'wins': 'Wins', 
    'losses': 'Losses', 
    'ppg': 'Points Per Game', 
    'fg_pct': 'FG%', 
    'fg3_pct': '3PT%', 
    'ft_pct': 'FT%', 
    'rebounds': 'Rebounds', 
    'assists': 'Assists', 
    'steals': 'Steals', 
    'blocks': 'Blocks', 
    'turnovers': 'Turnovers'
}

stats_to_show = st.sidebar.multiselect(
    "Stats to Compare", 
    options=all_stats, 
    default=['wins', 'losses', 'ppg', 'rebounds', 'assists'],
    format_func=lambda x: stat_labels[x]
)

# Add a note about caching
st.sidebar.info("💡 Team stats are cached for faster performance. The app makes fresh API calls only when needed.")

if st.button("Compare Teams", type="primary"):
    # Check if teams are the same
    if team1 == team2:
        st.warning("⚠️ Please select two different teams for comparison!")
    else:
        with st.spinner(f"Getting stats for {team1} and {team2}..."):
            stats1 = cached_team_stats(team1)
            stats2 = cached_team_stats(team2)
        
        if not stats1 or not stats2:
            st.error(f"❌ Couldn't fetch stats. Check if the teams are valid or try again later.")
        else:
            # Create columns for team stats
            col1, col2 = st.columns(2)
            
            # Function to format stat values
            def format_stat(stat, value):
                if stat in ['fg_pct', 'fg3_pct', 'ft_pct']:
                    return f"{value:.1%}"
                return value
            
            # Display team stats in cards
            with col1:
                st.subheader(f"{team1}")
                for stat in stats_to_show:
                    if stat in stats1:
                        st.metric(stat_labels[stat], format_stat(stat, stats1[stat]))
            
            with col2:
                st.subheader(f"{team2}")
                for stat in stats_to_show:
                    if stat in stats2:
                        st.metric(stat_labels[stat], format_stat(stat, stats2[stat]))
            
            st.markdown("---")
            
            # Create visualizations
            st.subheader("📊 Visual Comparison")
            viz_tabs = st.tabs(["Bar Chart", "Radar Chart", "Head-to-Head"])
            
            # Prepare data for visualizations
            viz_data = pd.DataFrame()
            for stat in stats_to_show:
                if stat in stats1 and stat in stats2:
                    new_row = pd.DataFrame({
                        'Statistic': [stat_labels[stat], stat_labels[stat]],
                        'Value': [stats1[stat], stats2[stat]],
                        'Team': [team1, team2]
                    })
                    viz_data = pd.concat([viz_data, new_row], ignore_index=True)
            
            # Bar chart
            with viz_tabs[0]:
                chart = alt.Chart(viz_data).mark_bar().encode(
                    x='Statistic',
                    y='Value',
                    color='Team',
                    column=alt.Column('Statistic', header=alt.Header(labelOrient='bottom'))
                ).properties(width=100)
                st.altair_chart(chart)
            
            # Radar chart - only show numeric stats that make sense in a radar
            with viz_tabs[1]:
                radar_stats = [s for s in stats_to_show if s not in ['wins', 'losses']]
                if len(radar_stats) >= 3:  # Need at least 3 stats for a meaningful radar
                    # Normalize the data for radar chart
                    radar_data = {}
                    for stat in radar_stats:
                        if stat in stats1 and stat in stats2:
                            max_val = max(stats1[stat], stats2[stat])
                            # For turnovers, lower is better, so invert the normalization
                            if stat == 'turnovers':
                                radar_data[stat] = {
                                    team1: 1 - (stats1[stat] / max_val) if max_val > 0 else 0,
                                    team2: 1 - (stats2[stat] / max_val) if max_val > 0 else 0
                                }
                            else:
                                radar_data[stat] = {
                                    team1: stats1[stat] / max_val if max_val > 0 else 0,
                                    team2: stats2[stat] / max_val if max_val > 0 else 0
                                }
                    
                    # Create the radar chart
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatterpolar(
                        r=[radar_data[stat][team1] for stat in radar_stats],
                        theta=[stat_labels[stat] for stat in radar_stats],
                        fill='toself',
                        name=team1
                    ))
                    
                    fig.add_trace(go.Scatterpolar(
                        r=[radar_data[stat][team2] for stat in radar_stats],
                        theta=[stat_labels[stat] for stat in radar_stats],
                        fill='toself',
                        name=team2
                    ))
                    
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 1]
                            )
                        ),
                        showlegend=True
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Select at least 3 non-win/loss stats to display a radar chart.")
            
            # Head-to-head comparison
            with viz_tabs[2]:
                # Create a head-to-head table
                comparison_data = []
                for stat in stats_to_show:
                    if stat in stats1 and stat in stats2:
                        if stat == 'losses' or stat == 'turnovers':
                            # For these stats, lower is better
                            better_team = team1 if stats1[stat] < stats2[stat] else team2 if stats2[stat] < stats1[stat] else "Tie"
                        else:
                            # For all other stats, higher is better
                            better_team = team1 if stats1[stat] > stats2[stat] else team2 if stats2[stat] > stats1[stat] else "Tie"
                        
                        comparison_data.append({
                            'Statistic': stat_labels[stat],
                            team1: format_stat(stat, stats1[stat]),
                            team2: format_stat(stat, stats2[stat]),
                            'Edge': better_team
                        })
                
                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(comparison_df, use_container_width=True)
            
            st.markdown("---")
            
            # Get web insights
            st.subheader("📰 Recent News")
            with st.spinner("Fetching news insights..."):
                insights = get_web_insights(team1, team2)
            st.markdown(insights)
            
            st.markdown("---")
            
            # Get AI analysis
            st.subheader("🧠 Hustler's Analysis")
            with st.spinner("Our AI analyst is breaking down the matchup..."):
                comparison = generate_comparison(team1, team2, stats1, stats2)
            st.markdown(comparison)
            
            # Add a rerun button at the bottom
            if st.button("Run Another Comparison"):
                st.experimental_rerun()
else:
    # Display app instructions when first loaded
    st.info("👈 Select two NBA teams from the sidebar and click 'Compare Teams' to see stats and analysis!")