<p align="center">
  <img src="logo.png" alt="InternHunt Logo" width="100" />
</p>

<h1 align="center">InternHunt – AI‑Powered Resume & Job Assistant</h1>

<p align="center">
  Parse resumes, extract skills, discover jobs and courses, classify domain, and chat locally with an AI coach — all in a modern Streamlit app.
</p>

<p align="center">
  <a href="https://python.org"><img src="https://img.shields.io/badge/Python-3.9+-blue" alt="Python"></a>
  <a href="https://streamlit.io"><img src="https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B" alt="Streamlit"></a>
  <a href="https://www.mysql.com/"><img src="https://img.shields.io/badge/MySQL-8.0+-4479A1" alt="MySQL"></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-green" alt="License"></a>
</p>

---

## Overview

InternHunt helps candidates quickly understand and improve their resumes, discover relevant roles and courses, and converse with a local AI about improvements. The app is modular and production-ready, with graceful fallbacks when optional services (DB, APIs, Ollama) aren’t configured.

- Live UI with Streamlit
- Resume parsing and skill extraction
- Job and course recommendations
- Resume domain classification
- Local chatbot via Ollama (optional)
- MySQL persistence and admin features (optional)
- Job scraping across multiple sources

---

## Features

- Resume Parsing
  - Extracts contact info, skills, education, and experience from PDFs using spaCy and custom rules in `resume_parser.py`.
- Smart Recommendations
  - Jobs: role and keyword suggestions based on extracted skills.
  - Courses: recommended courses to fill skill gaps (`Courses.py`, `api_services.py`).
- Resume Classification
  - Classifies resume domain/type (e.g., Data Science, Development) via `resume_classifier.py`.
- Job Scraping
  - Aggregates opportunities from multiple sources in `job_scrapers.py` with deduplication.
  - Scrapers include Internshala, GitHub repos (hiring/internship topics), and RemoteOK.
- Local Chatbot (Optional)
  - `chat_service.py` integrates with [Ollama](https://ollama.com/) for fast, local, resume‑aware Q&A.
  - Streaming responses, model health checks, and conversation context.
- Database (Optional)
  - `database.py` provides MySQL connectivity for admin and tracking features.
  - `setup_database.sql` bootstraps schema; app runs fine without DB configured.
- Robust UI/UX
  - Clean components in `ui.py`, theme and styles from `styles.py`.
  - Centralized error handling via `error_handler.py`.
  - Config in `config.py` and helpers in `utils.py`.

---

## Project Structure

```
.
├─ App_refined.py           # Main Streamlit entrypoint (recommended)
├─ App.py                   # Legacy/alternate entry
├─ api_services.py          # External helpers (yt_dlp, course helpers, Jooble, etc.)
├─ chat_service.py          # Local chatbot via Ollama
├─ job_scrapers.py          # Internshala / GitHub / RemoteOK scrapers + aggregator
├─ resume_parser.py         # Resume parsing & extraction logic
├─ resume_classifier.py     # Resume domain/type classifier
├─ Courses.py               # Course recommendations
├─ config.py                # Env loading & app config (dotenv)
├─ database.py              # MySQL connectivity (optional)
├─ error_handler.py         # Centralized error handling/log helpers
├─ styles.py                # Theming and styled components
├─ ui.py                    # UI building blocks
├─ utils.py                 # Utilities and helpers
├─ setup_database.sql       # DB schema bootstrap
├─ requirements.txt         # Pip dependencies
├─ environment.yml          # Conda environment (alternative to pip)
├─ .env.example             # Template for environment variables (no secrets)
├─ .gitignore
├─ README.md
└─ logo.png
```

---

## Getting Started

### Prerequisites

- Python 3.9+
- pip or Conda
- spaCy model `en_core_web_sm`
- Optional:
  - MySQL Server (for DB features)
  - [Ollama](https://ollama.com/) (for the local chatbot)

### Setup

Option A: pip + venv
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

Option B: Conda
```bash
conda env create -f environment.yml
conda activate internhunt
python -m spacy download en_core_web_sm
```

### Environment Variables

Copy and edit the example:
```bash
cp .env.example .env
```

Minimum variables (aligned with `config.py`):
```env
# Database (optional)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=cv

# Chatbot (optional)
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi:latest

# Job APIs (optional)
JOOBLE_API_KEY=
ADZUNA_APP_ID=
ADZUNA_API_KEY=
ADZUNA_COUNTRY=in
```

If DB or Ollama are not configured, the app still runs with those features disabled.

### Run

Use the Streamlit runner:
```bash
streamlit run App_refined.py --server.port 8502
```

Open the URL printed in the terminal (e.g., http://localhost:8502).

---

## Optional Integrations

### Database (MySQL)

1) Start MySQL and apply schema:
```bash
mysql -u root -p < setup_database.sql
```

2) Ensure `.env` contains the correct credentials.

3) Run the app; database‑backed features (admin/tracking) will be enabled.

### Local Chatbot (Ollama)

1) Install and run Ollama:
- macOS: `brew install ollama`
- Start server: `ollama serve`

2) Pull a model:
```bash
ollama pull phi
# or: ollama pull llama3
```

3) Configure `.env`:
```env
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=phi:latest
```

4) Launch the app and open the chat panel.

### Job Scrapers

- `job_scrapers.py` aggregates results from multiple sources and deduplicates by URL.
- Some sources are rate‑limited; the code throttles requests (`time.sleep`) and handles errors gracefully.
- Provide skills (and optional location) to `scrape_all(skills, location)`.

---

## Usage Guide

- Upload a resume (PDF) on the main screen.
- Review extracted contact details, skills, education, and experience.
- Explore recommended job roles and keywords.
- See course recommendations to fill skill gaps.
- Check resume classification (e.g., DS, Dev).
- Use the chatbot for tailored suggestions (if Ollama enabled).
- If DB is enabled, use admin/tracking features as configured.

---

## VS Code Debugging

Use a Streamlit launch configuration so Streamlit provides a proper ScriptRunContext:

```json
{
  "name": "Python: Streamlit",
  "type": "python",
  "request": "launch",
  "module": "streamlit",
  "args": ["run", "App_refined.py", "--server.port", "8502"],
  "cwd": "${workspaceFolder}",
  "justMyCode": true,
  "console": "integratedTerminal",
  "env": { "PYTHONPATH": "${workspaceFolder}" }
}
```

---

## Troubleshooting

- Streamlit “missing ScriptRunContext” warnings
  - Run with `streamlit run App_refined.py`, not `python App_refined.py`.
- spaCy model not found
  - `python -m spacy download en_core_web_sm`
- MySQL connection errors
  - Verify server is running; credentials in `.env` match; database exists via `setup_database.sql`.
- Ollama connection errors
  - Confirm `ollama serve` is running; model is pulled; `OLLAMA_HOST` is correct (no trailing `/api`, no trailing slash).
- yt‑dlp or API errors
  - Ensure URLs are valid; some endpoints may require API keys configured in `.env`.

---

## FAQ

- Can I run without MySQL?
  - Yes. The app detects missing DB credentials and runs with DB features disabled.
- Which Ollama model should I use?
  - Defaults to `phi:latest`. You can try `llama3` or other models depending on your hardware.
- Do I need API keys?
  - Only for the optional job APIs. Scrapers and the core app work without them.

---

## Contributing

Issues and PRs are welcome. For major changes, please open an issue first to discuss your approach.

---

## License

MIT. See `LICENSE`.

---

<p align="center">
  <strong>⭐ If you found this project helpful, please give it a star! ⭐</strong><br/>
  <em>Built with ❤️ for students and job seekers</em>
</p>
