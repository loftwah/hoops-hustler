import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI, Ollama
from langchain.chains import LLMChain
from pydantic import BaseModel
import yaml
from tenacity import retry, stop_after_attempt, wait_fixed

# Load environment variables
load_dotenv()

# Pydantic model for validation
class TeamStats(BaseModel):
    wins: int
    losses: int
    ppg: float

# Load prompt from YAML (example config)
prompt_config = yaml.safe_load("""
template: "Compare {team1} and {team2} based on stats: {stats1} vs {stats2}. Which team has the edge and why?"
""")
prompt = PromptTemplate(
    input_variables=["team1", "team2", "stats1", "stats2"],
    template=prompt_config['template']
)

# Initialize LLM based on .env settings
use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
if use_ollama:
    llm = Ollama(model=os.getenv("OLLAMA_MODEL", "llama3.2"))
else:
    llm = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_URL"),
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    )

# Create LLM chain
chain = LLMChain(llm=llm, prompt=prompt)

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def generate_comparison(team1, team2, stats1, stats2):
    # Validate stats with Pydantic
    TeamStats(**stats1)
    TeamStats(**stats2)
    
    # Run the chain
    return chain.run(team1=team1, team2=team2, stats1=stats1, stats2=stats2)