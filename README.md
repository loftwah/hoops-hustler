# Hoops Hustler

A fun NBA team comparison tool built with real stats from the NBA API and AI-generated insights, powered by Streamlit.

## Features

- Compare two NBA teams based on wins, losses, and points per game (PPG).
- Visualize PPG with an Altair bar chart.
- Get AI-driven analysis using Ollama (local) or OpenAI (API).

## Prerequisites

- Python 3.10+
- [UV](https://github.com/astral-sh/uv) for dependency management
- [Ollama](https://ollama.ai/) (if using local LLM) or an OpenAI API key

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
     OPENAI_API_KEY=your_actual_openai_api_key_here  # Required if USE_OLLAMA=false
     OPENAI_URL=https://api.openai.com/v1
     OPENAI_MODEL=gpt-4o-mini
     USE_OLLAMA=true                          # Set to false for OpenAI
     OLLAMA_MODEL=llama3.2                    # Default Ollama model
     ```
   - For Ollama: Run `ollama serve` and ensure `llama3.2` is pulled (`ollama pull llama3.2`).

6. **Run the App**:
   ```
   uv run streamlit run app.py
   ```
   - Open `http://localhost:8501` in your browser.

## Usage

- Select two NBA teams from the dropdowns.
- Click "Compare" to see stats, a PPG chart, and an AI-generated comparison.

## Testing

- Run unit tests:
  ```
  uv run pytest tests/
  ```

## Project Structure

```
hoops-hustler/
├── app.py              # Streamlit app entry point
├── requirements.txt    # Pinned dependencies
├── README.md           # This file
├── .gitignore          # Ignore venv, caches, etc.
├── .env                # Environment variables
├── src/                # Core logic
│   ├── data_fetch.py   # NBA API data fetching
│   ├── ai_engine.py    # AI (Ollama/OpenAI) logic
│   └── web_insights.py # Web context (placeholder)
└── tests/              # Unit tests
    └── test_data_fetch.py
```

## Notes

- **Ollama**: Default mode (`USE_OLLAMA=true`) requires a running Ollama instance.
- **OpenAI**: Set `USE_OLLAMA=false` and provide a valid `OPENAI_API_KEY`.
- **Caching**: SQLite support is available but commented out in `data_fetch.py`.
- **Expansion**: Add more stats or real web insights in `web_insights.py`.

## Dependencies

See `requirements.txt` for the full list, including `nba_api==1.8.0`, `streamlit==1.43.2`, `langchain==0.3.20`, `ollama==0.4.7`, and `openai==1.66.3`.

````

---

### Setup Instructions
To apply this:
1. Replace your existing `~/g/hoops-hustler/README.md` with the above content:
   ```bash
   nano README.md  # Or use your editor of choice
````

- Paste the markdown, save, and exit.

2. (Optional) Create an `.env.example` for reference:
   ```bash
   touch .env.example
   ```
   - Add:
     ```
     OPENAI_API_KEY=
     OPENAI_URL=https://api.openai.com/v1
     OPENAI_MODEL=gpt-4o-mini
     USE_OLLAMA=true
     OLLAMA_MODEL=llama3.2
     ```

---

### Why This Version?

- **UV Focus**: Emphasizes `uv run` for consistency with your workflow.
- **Dual LLM Support**: Clarifies how to toggle between Ollama and OpenAI.
- **Current State**: Reflects the working app with stats, charts, and AI comparisons.
- **Expandability**: Hints at next steps (e.g., more stats, web insights).
