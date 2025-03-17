import streamlit as st
from src.data_fetch import get_team_stats, get_team_history, get_team_roster
from src.ai_engine import generate_advanced_comparison
from src.web_insights import get_web_insights
from src.social_insights import get_social_sentiment
import altair as alt
import pandas as pd
import plotly.graph_objects as go
import numpy as np
import re

st.set_page_config(page_title="Hoops Hustler: NBA Team Showdown", page_icon="🏀", layout="wide")

# Helper function to convert hex to rgba
def hex_to_rgba(hex_color, opacity=0.5):
    hex_color = hex_color.lstrip('#')
    if len(hex_color) == 6:
        r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        return f'rgba({r},{g},{b},{opacity})'
    return hex_color

# Main header with custom styling
st.markdown("""
<div style="text-align: center; padding: 1rem 0; background: linear-gradient(90deg, #17408B, #C9082A); border-radius: 10px; margin-bottom: 20px;">
    <h1 style="color: white;">🏀 Hoops Hustler: NBA Team Showdown</h1>
    <p style="color: white; font-size: 1.2rem;">Advanced NBA Team Analysis and Comparison</p>
</div>
""", unsafe_allow_html=True)

# Stat definitions
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

# NBA team colors dictionary for better visualizations
team_colors = {
    'Atlanta Hawks': '#E03A3E',
    'Boston Celtics': '#007A33',
    'Brooklyn Nets': '#000000',
    'Charlotte Hornets': '#1D1160',
    'Chicago Bulls': '#CE1141',
    'Cleveland Cavaliers': '#860038',
    'Dallas Mavericks': '#00538C',
    'Denver Nuggets': '#0E2240',
    'Detroit Pistons': '#C8102E',
    'Golden State Warriors': '#1D428A',
    'Houston Rockets': '#CE1141',
    'Indiana Pacers': '#002D62',
    'LA Clippers': '#c8102E',
    'Los Angeles Lakers': '#552583',
    'Memphis Grizzlies': '#5D76A9',
    'Miami Heat': '#98002E',
    'Milwaukee Bucks': '#00471B',
    'Minnesota Timberwolves': '#0C2340',
    'New Orleans Pelicans': '#0C2340',
    'New York Knicks': '#F58426',
    'Oklahoma City Thunder': '#007AC1',
    'Orlando Magic': '#0077C0',
    'Philadelphia 76ers': '#006BB6',
    'Phoenix Suns': '#1D1160',
    'Portland Trail Blazers': '#E03A3E',
    'Sacramento Kings': '#5A2D81',
    'San Antonio Spurs': '#C4CED4',
    'Toronto Raptors': '#CE1141',
    'Utah Jazz': '#002B5C',
    'Washington Wizards': '#002B5C'
}

# Team selection in the main area using columns
from nba_api.stats.static import teams
team_list = [team['full_name'] for team in teams.get_teams()]

# Create a container for team selection
selection_container = st.container()
with selection_container:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Team 1")
        team1 = st.selectbox(
            "Select first team", 
            team_list, 
            index=team_list.index("Denver Nuggets") if "Denver Nuggets" in team_list else 0,
            key="team1_select"
        )
        team1_img = "https://cdn.nba.com/logos/nba/{}/global/L/logo.svg".format(
            next((team['id'] for team in teams.get_teams() if team['full_name'] == team1), "")
        )
        # Display team color as background
        team1_color = team_colors.get(team1, '#C9082A')  # Default to red if not found
        st.markdown(f"""
        <div style="background-color: {team1_color}; padding: 10px; border-radius: 10px; text-align: center;">
            <img src="{team1_img}" width="120" style="background-color: white; border-radius: 5px; padding: 5px;">
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("### Team 2")
        team2 = st.selectbox(
            "Select second team", 
            team_list, 
            index=team_list.index("Miami Heat") if "Miami Heat" in team_list else 1,
            key="team2_select"
        )
        team2_img = "https://cdn.nba.com/logos/nba/{}/global/L/logo.svg".format(
            next((team['id'] for team in teams.get_teams() if team['full_name'] == team2), "")
        )
        # Display team color as background
        team2_color = team_colors.get(team2, '#17408B')  # Default to blue if not found
        st.markdown(f"""
        <div style="background-color: {team2_color}; padding: 10px; border-radius: 10px; text-align: center;">
            <img src="{team2_img}" width="120" style="background-color: white; border-radius: 5px; padding: 5px;">
        </div>
        """, unsafe_allow_html=True)

# Stats selection in a cleaner layout
st.markdown("### Select Stats to Compare")
stats_to_show = st.multiselect(
    "Choose stats", 
    options=all_stats, 
    default=['wins', 'losses', 'ppg', 'rebounds', 'assists', 'fg_pct', 'fg3_pct'],
    format_func=lambda x: stat_labels[x]
)

st.info("💡 Team stats are cached for faster performance.")

if st.button("Compare Teams", type="primary", use_container_width=True):
    if team1 == team2:
        st.warning("⚠️ Please select two different teams for comparison!")
    else:
        with st.spinner(f"Fetching stats for {team1} and {team2}..."):
            stats1 = get_team_stats(team1)
            stats2 = get_team_stats(team2)
            history1 = get_team_history(team1)
            history2 = get_team_history(team2)
            roster1 = get_team_roster(team1)
            roster2 = get_team_roster(team2)
        
        if not stats1 or not stats2:
            st.error("❌ Couldn't fetch stats. Check team validity or try again later.")
        else:
            # Get team colors for visualizations
            team1_color = team_colors.get(team1, '#C9082A')  # Default to red if not found
            team2_color = team_colors.get(team2, '#17408B')  # Default to blue if not found
            
            # Create two columns for team logos and stats
            team_cols = st.columns(2)
            with team_cols[0]:
                st.markdown(f"""
                <div style="background-color: {team1_color}; padding: 10px; border-radius: 10px; text-align: center;">
                    <img src="{team1_img}" width="80" style="background-color: white; border-radius: 5px; padding: 5px;">
                    <h3 style="color: white; margin-top: 5px;">{team1}</h3>
                </div>
                """, unsafe_allow_html=True)
            with team_cols[1]:
                st.markdown(f"""
                <div style="background-color: {team2_color}; padding: 10px; border-radius: 10px; text-align: center;">
                    <img src="{team2_img}" width="80" style="background-color: white; border-radius: 5px; padding: 5px;">
                    <h3 style="color: white; margin-top: 5px;">{team2}</h3>
                </div>
                """, unsafe_allow_html=True)
            
            # Display team stats in a nice table
            st.markdown("## Team Statistics")
            df_stats = pd.DataFrame({
                stat_labels[stat]: [stats1.get(stat, "N/A"), stats2.get(stat, "N/A")]
                for stat in stats_to_show
            }, index=[team1, team2])
            st.dataframe(df_stats.style.format(precision=2), use_container_width=True)
            
            # 🧠 Advanced AI Analysis section - moved to the top for prominence
            st.markdown("## 🧠 Advanced AI Analysis")
            with st.spinner("Generating advanced analysis..."):
                players1_names = ", ".join([player.get("PLAYER", "N/A") for player in roster1])
                players2_names = ", ".join([player.get("PLAYER", "N/A") for player in roster2])
                advanced_comparison = generate_advanced_comparison(team1, team2, stats1, stats2, players1_names, players2_names)
            
            st.markdown(advanced_comparison)
            
            # Interactive Visualizations section
            st.markdown("## Interactive Visualizations")
            
            # Tabs for visualisations
            viz_tabs = st.tabs(["Radar Chart", "Bar Chart", "Head-to-Head", "Historical Trends"])
            
            # Prepare data for visualisations
            viz_data = pd.DataFrame()
            for stat in stats_to_show:
                if stat in stats1 and stat in stats2:
                    new_row = pd.DataFrame({
                        'Statistic': [stat_labels[stat], stat_labels[stat]],
                        'Value': [stats1[stat], stats2[stat]],
                        'Team': [team1, team2]
                    })
                    viz_data = pd.concat([viz_data, new_row], ignore_index=True)
            
            # Radar Chart Tab (now first for better visual impact)
            with viz_tabs[0]:
                radar_stats = [s for s in stats_to_show if s not in ['wins', 'losses']]
                if len(radar_stats) >= 3:
                    radar_data = {}
                    for stat in radar_stats:
                        if stat in stats1 and stat in stats2:
                            max_val = max(stats1[stat], stats2[stat])
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
                    
                    # Convert hex colors to rgba for transparency
                    team1_fill = hex_to_rgba(team1_color, 0.3)
                    team2_fill = hex_to_rgba(team2_color, 0.3)
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatterpolar(
                        r=[radar_data[stat][team1] for stat in radar_stats],
                        theta=[stat_labels[stat] for stat in radar_stats],
                        fill='toself',
                        name=team1,
                        line=dict(color=team1_color),
                        fillcolor=team1_fill
                    ))
                    fig.add_trace(go.Scatterpolar(
                        r=[radar_data[stat][team2] for stat in radar_stats],
                        theta=[stat_labels[stat] for stat in radar_stats],
                        fill='toself',
                        name=team2,
                        line=dict(color=team2_color),
                        fillcolor=team2_fill
                    ))
                    fig.update_layout(
                        polar=dict(
                            radialaxis=dict(
                                visible=True,
                                range=[0, 1]
                            )
                        ),
                        showlegend=True,
                        height=500,
                        margin=dict(l=80, r=80, t=20, b=20),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Select at least 3 non-win/loss stats for a radar chart.")
            
            # Bar Chart Tab
            with viz_tabs[1]:
                # Convert the data to ensure numeric values for percentages
                for i, row in viz_data.iterrows():
                    if isinstance(row['Value'], str) and '%' in row['Value']:
                        viz_data.at[i, 'Value'] = float(row['Value'].strip('%')) / 100
                
                # Create a simpler bar chart that works reliably
                chart = alt.Chart(viz_data).mark_bar().encode(
                    y=alt.Y('Statistic:N', title=None),
                    x=alt.X('Value:Q', title='Value'),
                    color=alt.Color('Team:N', scale=alt.Scale(
                        domain=[team1, team2],
                        range=[team1_color, team2_color]
                    )),
                    tooltip=['Team', 'Statistic', 'Value']
                ).properties(
                    height=len(stats_to_show) * 50  # Dynamic height based on number of stats
                )
                
                st.altair_chart(chart, use_container_width=True)
            
            # Head-to-Head Comparison Tab
            with viz_tabs[2]:
                comparison_data = []
                for stat in stats_to_show:
                    if stat in stats1 and stat in stats2:
                        if stat in ['losses', 'turnovers']:
                            better_team = team1 if stats1[stat] < stats2[stat] else team2 if stats2[stat] < stats1[stat] else "Tie"
                        else:
                            better_team = team1 if stats1[stat] > stats2[stat] else team2 if stats2[stat] > stats1[stat] else "Tie"
                        comparison_data.append({
                            'Statistic': stat_labels[stat],
                            team1: stats1[stat],
                            team2: stats2[stat],
                            'Edge': better_team
                        })
                comparison_df = pd.DataFrame(comparison_data)
                st.dataframe(comparison_df, use_container_width=True, height=400)
            
            # Historical Trends Tab
            with viz_tabs[3]:
                if history1 is not None and history2 is not None:
                    st.subheader("Historical Game Logs")
                    
                    # Filter out Team_ID and GAME_ID columns if they exist
                    if 'Team_ID' in history1.columns:
                        history1 = history1.drop(columns=['Team_ID'])
                    if 'GAME_ID' in history1.columns:
                        history1 = history1.drop(columns=['GAME_ID'])
                    if 'Team_ID' in history2.columns:
                        history2 = history2.drop(columns=['Team_ID'])
                    if 'GAME_ID' in history2.columns:
                        history2 = history2.drop(columns=['GAME_ID'])
                    
                    history_tabs = st.tabs([f"{team1} Recent Games", f"{team2} Recent Games"])
                    with history_tabs[0]:
                        st.dataframe(history1.head(10), use_container_width=True)
                    with history_tabs[1]:
                        st.dataframe(history2.head(10), use_container_width=True)
                else:
                    st.info("Historical data not available for one or both teams.")
            
            # Additional insights sections
            st.markdown("## 📊 Social Insights")
            sentiment = get_social_sentiment(team1, team2)
            st.markdown(sentiment)
            
            st.markdown("## 📰 Web Insights")
            news = get_web_insights(team1, team2)
            st.markdown(news)
            
            # Bottom action buttons - Fix for experimental_rerun
            st.button("Run Another Comparison", type="primary", use_container_width=True, key="rerun_btn", on_click=st.rerun)
else:
    # Welcome screen with better styling
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: rgba(0,0,0,0.05); border-radius: 10px;">
        <h2>Welcome to Hoops Hustler!</h2>
        <p style="font-size: 1.2rem;">Select two NBA teams above and click 'Compare Teams' to see advanced stats, visualizations, and AI-powered analysis.</p>
        <p>Features include:</p>
        <ul style="display: inline-block; text-align: left;">
            <li>Detailed team statistics comparison</li>
            <li>Interactive visualizations (radar charts, bar charts)</li>
            <li>Head-to-head statistical advantages</li>
            <li>Historical game logs and trends</li>
            <li>Advanced AI analysis with player insights</li>
            <li>Social media insights and web news</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
