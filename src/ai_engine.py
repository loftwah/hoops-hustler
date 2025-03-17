import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_community.llms import OpenAI
from langchain_ollama import OllamaLLM  # Updated import for Ollama
from pydantic import BaseModel
import yaml
from tenacity import retry, stop_after_attempt, wait_fixed, wait_exponential

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

# Enhanced prompt template
prompt_config = yaml.safe_load("""
template: "You're an NBA analyst breaking down {team1} vs {team2}. With stats: {stats1} for {team1} and {stats2} for {team2}, which team has the edge? Give a sharp, witty take highlighting key factors, recent performance, and matchup dynamics. Include specific numerical advantages and discuss one or two key players who could influence the outcome based on these stats."
""")
prompt = PromptTemplate(
    input_variables=["team1", "team2", "stats1", "stats2"],
    template=prompt_config['template']
)

# Initialize LLM based on .env settings with improved models
use_ollama = os.getenv("USE_OLLAMA", "false").lower().strip() == "true"
if use_ollama:
    llm = OllamaLLM(model=os.getenv("OLLAMA_MODEL", "llama3.2"))  # Updated to OllamaLLM
else:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or api_key == "your_openai_api_key":
        raise ValueError(
            "OpenAI API key is missing or invalid. Provide a valid OPENAI_API_KEY in .env or set USE_OLLAMA=true."
        )
    llm = OpenAI(
        openai_api_key=api_key,
        base_url=os.getenv("OPENAI_URL", "https://api.openai.com/v1"),
        model=os.getenv("OPENAI_MODEL", "gpt-4") # Upgraded from gpt-4o-mini
    )

# Create a Runnable sequence instead of LLMChain
runnable = prompt | llm

# Enhanced retry mechanism with exponential backoff
@retry(
    stop=stop_after_attempt(3), 
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=True
)
def generate_comparison(team1, team2, stats1, stats2):
    """Generate an AI comparison between two NBA teams based on their stats."""
    # Validate stats using Pydantic model with optional fields
    try:
        TeamStats(**stats1)
        TeamStats(**stats2)
        # Using invoke instead of run
        result = runnable.invoke({"team1": team1, "team2": team2, "stats1": stats1, "stats2": stats2})
        return result
    except Exception as e:
        print(f"Error generating comparison: {e}")
        return f"Analysis unavailable at this time. Both {team1} and {team2} have valid stats, but our analyst needed a timeout. Please try again."