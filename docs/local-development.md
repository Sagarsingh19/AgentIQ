# Local development

## Prerequisites

- Python 3.11–3.13
- Tavily and Groq API keys for an end-to-end hosted-provider run

## Set up

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Set `AGENTIQ_TAVILY_API_KEY` and `AGENTIQ_GROQ_API_KEY` in `.env`. Do not place real keys in
source, tests, issues, logs or chat messages.

## Verify and run

```powershell
python -m pytest
python -m ruff check .
python main.py
```

The interactive API documentation is then available at `http://127.0.0.1:8000/docs`. The
development server binds only to loopback. A production deployment must use the Phase 5
deployment controls from the production-readiness audit, not this command.
