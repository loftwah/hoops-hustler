# 🏀 Hoops Hustler

A comprehensive NBA team comparison tool built with real-time stats from the NBA API and AI-generated insights, powered by Streamlit.

## Features

- Compare any two NBA teams with detailed statistics including:
  - Win/loss records
  - Scoring (Points Per Game)
  - Shooting percentages (FG%, 3PT%, FT%)
  - Advanced metrics (rebounds, assists, steals, blocks, turnovers)
- Interactive visualizations:
  - Bar charts for direct stat comparisons
  - Radar/spider charts to see team strengths
  - Head-to-head advantage tables
- AI-driven analysis using Ollama (local) or OpenAI (API)
- Real-time web insights with news articles about compared teams
- SQLite caching for faster performance with frequently compared teams
- User customization of displayed stats
- Feedback collection system

## Prerequisites

- Python 3.10+
- [UV](https://github.com/astral-sh/uv) for dependency management
- [Ollama](https://ollama.ai/) (if using local LLM) or an OpenAI API key
- (Optional) [NewsAPI](https://newsapi.org/) key for news insights

## Setup

1. **Install UV**:

   ```
   pip install uv
   ```

2. **Create Virtual Environment**:

   ```
   uv venv
   ```

3. **Install Dependencies**:

   ```
   uv pip install -r requirements.txt
   ```

4. **(Optional) Lock Dependencies**:

   ```
   uv lock
   ```

5. **Configure Environment**:

   - Copy `.env.example` to `.env` and edit it:
     ```
     OPENAI_API_KEY=your_openai_api_key  # Required if USE_OLLAMA=false
     OPENAI_URL=https://api.openai.com/v1
     OPENAI_MODEL=gpt-4                  # Upgraded from gpt-4o-mini
     USE_OLLAMA=true                     # Set to false for OpenAI
     OLLAMA_MODEL=llama3.2               # Default Ollama model
     NEWSAPI_KEY=your_newsapi_key        # For fetching news (optional)
     ```
   - For Ollama: Run `ollama serve` and ensure `llama3.2` is pulled (`ollama pull llama3.2`).
   - For NewsAPI: Register at [newsapi.org](https://newsapi.org/) to get a free API key.

6. **Run the App**:
   ```
   uv run streamlit run app.py
   ```
   - Open `http://localhost:8501` in your browser.

## Usage

- Select two NBA teams from the sidebar dropdowns.
- Choose which stats you want to compare.
- Click "Compare Teams" to see:
  - Side-by-side team stats
  - Multiple visualization options
  - Latest news articles about the teams
  - AI-generated analysis of the matchup

## Data Caching

The app uses two levels of caching:
- SQLite database (automatic) - Stores team stats to reduce API calls
- Streamlit caching - Further optimizes performance during a session

## Testing

- Run unit tests:
  ```
  uv run pytest tests/
  ```

## Project Structure

```
hoops-hustler/
├── app.py              # Streamlit app entry point (enhanced UI)
├── requirements.txt    # Dependencies with versions
├── README.md           # Documentation
├── .gitignore          # Ignore venv, caches, etc.
├── .env                # Environment variables
├── data/               # Auto-created for SQLite caching
│   └── teams.db        # Team stats cache
├── src/                # Core logic
│   ├── data_fetch.py   # NBA API data fetching with caching
│   ├── ai_engine.py    # Enhanced AI analysis
│   └── web_insights.py # News API integration
└── tests/              # Unit tests
    └── test_data_fetch.py
```

## Notes

- **Ollama**: Default mode (`USE_OLLAMA=true`) requires a running Ollama instance.
- **OpenAI**: Set `USE_OLLAMA=false` and provide a valid `OPENAI_API_KEY`.
- **News Insights**: Add a `NEWSAPI_KEY` for real-time news about teams.

## Future Enhancements

- Player-level comparisons
- Historical performance trends
- Social media sentiment analysis
- Predictive matchup outcomes
- Mobile app version

## Dependencies

See `requirements.txt` for the full list, including:
- Core: `streamlit`, `pandas`, `numpy`, `altair`, `plotly`
- Data: `nba_api`, `sqlalchemy`
- AI: `langchain`, `openai`, `ollama`
- Web: `requests`, `python-dotenv`

## Contributing

We welcome contributions! Feel free to submit pull requests or suggest features through the in-app feedback form.
