import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI
from langchain_ollama import OllamaLLM  # Updated import for Ollama
from pydantic import BaseModel
import yaml
from tenacity import retry, stop_after_attempt, wait_exponential

# Load environment variables
load_dotenv()

# Pydantic model for validation with expanded stats
class TeamStats(BaseModel):
    wins: int
    losses: int
    ppg: float
    fg_pct: float = None
    fg3_pct: float = None
    ft_pct: float = None
    rebounds: float = None
    assists: float = None
    steals: float = None
    blocks: float = None
    turnovers: float = None

# Enhanced prompt template for basic comparison
prompt_config = yaml.safe_load("""
template: "You're an NBA analyst breaking down {team1} vs {team2}. With stats: {stats1} for {team1} and {stats2} for {team2}, which team has the edge? Give a sharp, witty take highlighting key factors, recent performance, and matchup dynamics. Include specific numerical advantages."
""")
prompt = PromptTemplate(
    input_variables=["team1", "team2", "stats1", "stats2"],
    template=prompt_config['template']
)

# Advanced prompt template for deeper analysis (team and player-level)
advanced_prompt_config = yaml.safe_load("""
template: "You are an advanced NBA analyst. Compare teams {team1} and {team2} using team stats {stats1} vs {stats2} and player performances {players1} vs {players2}. Provide historical context, key player insights, and predictive analysis."
""")
advanced_prompt = PromptTemplate(
    input_variables=["team1", "team2", "stats1", "stats2", "players1", "players2"],
    template=advanced_prompt_config['template']
)

# Initialize LLM based on .env settings with improved models
use_ollama = os.getenv("USE_OLLAMA", "false").lower().strip() == "true"
if use_ollama:
    llm = OllamaLLM(model=os.getenv("OLLAMA_MODEL", "llama3.2"))
else:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or api_key == "your_openai_api_key":
        raise ValueError(
            "OpenAI API key is missing or invalid. Provide a valid OPENAI_API_KEY in .env or set USE_OLLAMA=true."
        )
    llm = OpenAI(
        openai_api_key=api_key,
        base_url=os.getenv("OPENAI_URL", "https://api.openai.com/v1"),
        model=os.getenv("OPENAI_MODEL", "gpt-4")
    )

# Create a Runnable sequence for basic analysis
basic_runnable = prompt | llm
# Create a Runnable sequence for advanced analysis
advanced_runnable = advanced_prompt | llm

# Enhanced retry mechanism with exponential backoff for basic analysis
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def generate_comparison(team1, team2, stats1, stats2):
    """Generate a basic AI comparison between two NBA teams based on their stats."""
    try:
        TeamStats(**stats1)
        TeamStats(**stats2)
        result = basic_runnable.invoke({"team1": team1, "team2": team2, "stats1": stats1, "stats2": stats2})
        return result
    except Exception as e:
        print(f"Error generating comparison: {e}")
        return f"Analysis unavailable at this time. Please try again."

# Enhanced retry mechanism with exponential backoff for advanced analysis
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def generate_advanced_comparison(team1, team2, stats1, stats2, players1, players2):
    """Generate an advanced AI analysis including player-level insights."""
    try:
        TeamStats(**stats1)
        TeamStats(**stats2)
        result = advanced_runnable.invoke({
            "team1": team1,
            "team2": team2,
            "stats1": stats1,
            "stats2": stats2,
            "players1": players1,
            "players2": players2
        })
        return result
    except Exception as e:
        print(f"Error generating advanced comparison: {e}")
        return f"Advanced analysis unavailable at this time. Please try again."
