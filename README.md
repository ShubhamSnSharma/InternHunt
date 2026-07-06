# InternHunt

> Analyze resumes, evaluate ATS readiness, predict career domains, identify skill gaps, and discover relevant internships — through an end-to-end machine learning pipeline.

InternHunt is an AI-powered resume intelligence platform built with Streamlit, scikit-learn, spaCy, Google Gemini, and PostgreSQL. It was built to solve a problem most students face but rarely think about analytically: why does a well-written resume still get filtered out, and what specifically needs to change?

---

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Neon-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://neon.tech/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Gemini AI](https://img.shields.io/badge/Gemini-1.5%20Flash-4F8EF7?style=for-the-badge&logo=google-gemini&logoColor=white)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)](./LICENSE)
[![Version](https://img.shields.io/badge/Version-v3.0.0-8b5cf6?style=for-the-badge)](#)

**[Live App](https://internhunt.streamlit.app)** · **[Landing Page](https://internhuntt.vercel.app)** · **[GitHub](https://github.com/ShubhamSnSharma/InternHunt)**

---

## Overview

Most students don't know why their resume gets filtered out, which skills they're actually missing, or where to look for opportunities that match their current profile. InternHunt is built around those three problems.

When a candidate uploads a PDF resume, the platform:

- Parses and extracts structured information using NLP
- Predicts the most relevant career domain using a trained MLP classifier
- Evaluates ATS readiness across five weighted scoring factors
- Identifies missing technical skills relative to the predicted domain
- Recommends courses to address those gaps
- Surfaces live internship listings from four aggregated sources
- Provides a context-aware AI assistant loaded with the candidate's parsed data

For admins and recruiters, every submission is logged to a PostgreSQL database and visualized through an analytics dashboard with score distributions, field breakdowns, and a searchable candidate registry.

---

## At a Glance

| | |
|:---|:---|
| **ML Model Accuracy** | 85.3% (3-fold stratified cross-validation) |
| **Career Categories** | 25 distinct job domains |
| **Skills Detected** | 100+ via spaCy NLP matcher |
| **Job Sources** | 4 — Internshala, Remotive, Jooble, GitHub |
| **AI Assistant** | Gemini 1.5 Flash, resume-context aware |
| **Database** | Neon PostgreSQL (serverless) |

---

## Technology Stack

| Layer | Tools |
|:---|:---|
| **Application** | Streamlit, Python 3.9+ |
| **UI / Styling** | Custom HTML, Vanilla CSS, Plotly |
| **ML Pipeline** | scikit-learn (TF-IDF + MLP), spaCy |
| **AI** | Google Gemini API (gemini-1.5-flash) |
| **Database** | Neon PostgreSQL (production), MySQL (local fallback) |
| **Deployment** | Streamlit Cloud, Vercel (landing page) |

---

## Live Demo

> 📹 *A short walkthrough GIF demonstrating the complete flow — from resume upload to internship recommendations — will be added here.*

**[Try the live app →](https://internhunt.streamlit.app)**

---

## Application Walkthrough

The application follows a complete resume intelligence workflow, beginning with resume upload and ending with recruiter-facing analytics.

### 1 · Landing Page
![Landing Page](./screenshots/landing-page.png)

*Public project landing page introducing InternHunt and its AI-powered workflow.*

---

### 2 · Application Home
![Main App](./screenshots/landing-page-main.png)

*Main Streamlit interface where candidates begin their analysis.*

---

### 3 · Resume Upload
![Resume Upload](./screenshots/resume-upload.png)

*A custom SaaS-inspired drag-and-drop uploader built using HTML/CSS instead of Streamlit's default uploader.*

---

### 4 · Resume Analysis
![Resume Analysis](./screenshots/resume-analysis.png)

*Personal details, contact information, resume metadata, and parsed document information extracted immediately after upload.*

---

### 5 · Skills Analysis
![Skills Extracted](./screenshots/skills-extracted.png)

*spaCy identifies technical skills and technologies found throughout the resume.*

---

### 6 · AI Profile Summary
![AI Profile](./screenshots/ai-profile.png)

*An AI-generated overview summarising strengths, experience level, career direction, and improvement opportunities.*

---

### 7 · ATS Performance
![ATS Dashboard](./screenshots/ats-dashboard.png)

*The resume receives an ATS compatibility score with a detailed breakdown across weighted evaluation factors.*

---

### 8 · Career Prediction & Skill Gap
![Suggestions](./screenshots/suggestions.png)

*The ML classifier predicts the most suitable career domain while highlighting missing skills required for that field.*

---

### 9 · Course Recommendations
![Courses](./screenshots/courses.png)

*Learning resources are recommended to help candidates bridge their identified skill gaps.*

---

### 10 · Internship Opportunities
![Job Search 1](./screenshots/job-search1.png)
![Job Search 2](./screenshots/job-search2.png)

*InternHunt aggregates internship listings from multiple providers and ranks opportunities relevant to the candidate profile.*

---

### 11 · AI Career Assistant
![AI Chatbot](./screenshots/chatbot.png)

*A Gemini-powered assistant answers resume-specific career questions using the parsed resume as context.*

---

### 12 · Admin Login
![Admin Login](./screenshots/admin-login.png)

*A password-protected administration portal featuring a custom premium login interface.*

---

### 13 · Analytics Dashboard
![Admin Dashboard 1](./screenshots/admin-dashboard1.png)
![Admin Dashboard 2](./screenshots/admin-dashboard2.png)

*Interactive Plotly dashboards and a PostgreSQL-backed candidate registry provide recruiters with insights into uploaded resumes and platform activity.*

## Core Features

### Resume Analysis
- **PDF Parsing** — Text extracted from PDF via `pypdf`. Non-ASCII characters removed, whitespace normalized, formatting artifacts stripped before any NLP runs.
- **Skill Extraction** — spaCy matcher against a curated 100+ skill vocabulary. Handles common aliases (`k8s` → `Kubernetes`, `tf` → `TensorFlow`).
- **ATS Scoring** — 100-point score calculated across five weighted dimensions. Missing sections are explicitly identified, not just penalized silently.
- **Career Prediction** — TF-IDF + MLP classifier routing to 25 role categories. Returns top-3 predictions with confidence scores.

### Career Guidance
- **Skill Gap Detection** — Compares the candidate's detected skills against the expected stack for their predicted domain. Only genuinely missing skills are surfaced.
- **Course Recommendations** — Matched from a curated catalog (`Courses.py`) based on the identified gaps, not the entire role.
- **Internship Matching** — Multi-source aggregation filtered by the candidate's skill profile rather than a generic search term.

### AI Features
- **Gemini Assistant** — Before the session starts, the chatbot system prompt is constructed from the parsed resume: name, email, skills, predicted field, ATS score, and experience level. This means the assistant can answer specific questions about the candidate's resume rather than giving generic advice.

### Recruiter & Admin
- **Candidate Registry** — Every submission logged to PostgreSQL: name, email, score, timestamp, predicted field, experience level, detected skills, recommended skills, recommended courses.
- **Analytics Dashboard** — Score distribution, career field frequency, skill density charts. Single-scroll candidate table with sticky headers.
- **CSV Export** — Full registry exportable from the admin panel.

---

## System Workflow

The diagram below shows how a resume moves through the application from upload to final output.

![System Workflow Diagram](./screenshots/workflow-diagram.png)

Here is what happens at each stage:

**1. Resume Upload**
The candidate uploads a PDF file through the custom drag-and-drop interface. File size and format are validated before processing begins.

**2. Text Extraction**
`pypdf` reads the PDF and extracts raw text, preserving the content while discarding layout formatting.

**3. Text Cleaning**
The extracted text is cleaned: non-ASCII characters removed, excessive whitespace collapsed, special symbols stripped. This normalization step is important for consistent NLP and TF-IDF performance.

**4. Contact Information Parsing**
Regex patterns extract email addresses, phone numbers, and profile URLs (GitHub, LinkedIn). These are displayed immediately and later passed to the Gemini chatbot context.

**5. Technical Skill Extraction**
The spaCy NLP matcher scans the cleaned text against a vocabulary of 100+ technical skills. The matcher handles variations and aliases — for example, both `k8s` and `Kubernetes` map to the same skill token.

**6. Career Prediction**
The cleaned resume text is vectorized using `TfidfVectorizer` (2500 features, unigrams + bigrams). The resulting vector is passed to the trained `MLPClassifier`, which returns a probability distribution across 25 career categories. The top three predictions are shown to the candidate.

**7. ATS Evaluation**
The resume is evaluated against a five-factor scoring model. Each factor is weighted and scored independently: Content (50%), Keywords (20%), Formatting (15%), Experience (10%), and Readability (5%). Missing sections trigger explicit warnings rather than silent score deductions.

**8. Missing Skill Detection**
The candidate's detected skill set is compared against the expected technical stack for their top predicted domain. Skills present in the domain standard but absent from the resume are flagged as gaps.

**9. Course Recommendation**
Gap skills are matched against a curated course catalog. Only courses addressing the specific missing skills are returned, not a generic list for the domain.

**10. Internship Discovery**
Four external sources are queried in parallel using the candidate's detected skills as search parameters: Internshala (scraper), Remotive (REST API), Jooble (REST API), GitHub (scraper). Results are displayed in a card layout.

**11. Database Logging**
The complete candidate profile — name, email, score, predicted field, experience level, detected skills, recommended skills, and recommended courses — is written to Neon PostgreSQL. This record is immediately available in the admin dashboard.

**12. AI Career Assistant**
The Gemini system prompt is assembled from the parsed candidate data before the chat session initialises. The assistant has full context and can answer resume-specific questions, explain the ATS score, or suggest specific improvements.

---

## Implementation Details

### Resume Parser
The parser (`resume_parser.py`) handles extraction, cleaning, and section detection. Sections are identified through heading pattern matching rather than positional parsing, which makes the parser more tolerant of varied resume layouts.

### Skill Extraction
The spaCy matcher uses a curated pattern list maintained in `utils.py`. Patterns are compiled once at startup and reused across sessions. Alias handling is done through a normalization map before matching, so the vocabulary covers both shorthand and full-form representations of the same skill.

### ATS Engine
Rather than simple keyword counting, the ATS engine evaluates structural completeness. Each factor (Content, Keywords, Formatting, Experience, Readability) has its own scoring logic. The Content score alone accounts for half the total, and it evaluates whether the resume contains a coherent objective, education history, project descriptions, and measurable experience — not just whether those section headers exist.

### Career Prediction Model
The model is a `Pipeline` object serialized to `resume_classifier_v3_skills_mlp.pkl`. At inference time, the same `TfidfVectorizer` used during training transforms the input text, ensuring vocabulary consistency. The MLP returns class probabilities, and the top three are extracted using `predict_proba` — giving candidates visibility into adjacent fields that are close matches.

### Recommendation Engine
Courses are served from a structured dictionary in `Courses.py`, keyed by skill name. Internship queries use the top five detected skills as search terms. This keeps recommendations relevant to what the candidate actually has, not just what domain they were predicted to belong to.

### PostgreSQL Candidate Registry
Database connections are managed in `database.py`. In production (Streamlit Cloud), the application connects to Neon via `DATABASE_URL` using `psycopg2`. In local development, it falls back to MySQL via `pymysql`. The schema is identical across both environments. The admin registry view renders the full table in a single scroll container with sticky headers — no pagination.

### AI Assistant
The chatbot uses the `google-generativeai` SDK. The system prompt is dynamically assembled from the parsed candidate fields (name, email, skills, ATS score, predicted field, experience level) before `chat_service.py` initialises the session. This means every conversation starts with the candidate's actual data as context, not a generic career coaching prompt.

---

## Machine Learning Pipeline

The classifier maps resume text to one of 25 career categories.

### Training Pipeline

```
Resume Text
    ↓
TfidfVectorizer  (2500 features, unigrams + bigrams)
    ↓
MLPClassifier    (128 → 64 hidden units, ReLU, Adam)
    ↓
Class Probabilities  (25 categories)
    ↓
Top-3 Predictions
```

**Training data**: `UpdatedResumeDataSet.csv` — 166 deduplicated samples across 25 classes. The dataset was deduplicated before training to prevent identical samples from inflating held-out accuracy.

> [!NOTE]
> The 25 target classes include: Data Science, Web Development, Android Development, iOS Development, UI/UX Design, Java Developer, Python Developer, DevOps, Database, Network Security, Machine Learning, Artificial Intelligence, DotNet Developer, Blockchain, Hadoop, Ethical Hacking, Data Analyst, Cloud Computing, Full Stack Developer, Big Data, Automation Testing, Embedded Systems, Information Security, PMO, and Mechanical Engineer.

### Model Configuration

```python
Pipeline([
    ('tfidf', TfidfVectorizer(
        max_features=2500,
        ngram_range=(1, 2),       # Unigrams and bigrams
        min_df=1,
        max_df=0.95,
        stop_words='english',
        lowercase=True
    )),
    ('classifier', MLPClassifier(
        hidden_layer_sizes=(128, 64),
        activation='relu',
        solver='adam',
        alpha=0.1,
        learning_rate_init=0.001,
        max_iter=1000,
        early_stopping=False,
        random_state=42
    ))
])
```

### Evaluation

| Metric | Score |
|:---|:---|
| Test Accuracy | **85.29%** |
| Precision (weighted avg) | **88.2%** |
| Recall (weighted avg) | **85.3%** |
| F1-Score (weighted avg) | **81.9%** |
| Cross-Validation (3-fold stratified) | **81.69% ± 0.85%** |

**Artifact**: `resume_classifier_v3_skills_mlp.pkl` — 10.1 MB

To retrain:
```bash
python soft_skill_role_trainer.py
```

---

## Job Sources

| Source | Method | Details |
|:---|:---|:---|
| **Internshala** | HTML scraper | India-focused listings. Parses stipend, duration, and apply links. |
| **Remotive** | REST API | Public endpoint for global remote roles. Filtered by detected skills. |
| **Jooble** | REST API | POST-based search with keyword and location parameters. Requires `JOOBLE_API_KEY`. |
| **GitHub** | HTML scraper | Repositories tagged `topic:hiring` or `topic:internship`. |

---

## Analytics Dashboard

The admin portal is accessible via a password-protected login. Once authenticated, it provides:

- **Score distribution** — Area chart showing the spread of ATS scores across all logged candidates
- **Career field breakdown** — Bar chart of predicted role frequency across the candidate pool
- **Skill frequency** — Most commonly detected and most commonly missing skills
- **Candidate registry** — Full PostgreSQL-backed table with name, email, score, field, level, skills, and timestamp. Exportable to CSV.

All charts are rendered with Plotly and update dynamically as new candidates are processed.

---

## Database Architecture

Two backends are supported depending on the environment:

| Database | Environment | Driver |
|:---|:---|:---|
| **Neon PostgreSQL** | Production (Streamlit Cloud) | `psycopg2` via `DATABASE_URL` |
| **MySQL** | Local development | `pymysql` via `.env` variables |

### Schema

```sql
CREATE TABLE IF NOT EXISTS user_data (
    ID                  SERIAL PRIMARY KEY,
    Name                VARCHAR(500) NOT NULL,
    Email_ID            VARCHAR(500) NOT NULL,
    resume_score        VARCHAR(8)   NOT NULL,
    Timestamp           VARCHAR(50)  NOT NULL,
    Page_no             VARCHAR(5)   NOT NULL,
    Predicted_Field     TEXT         NOT NULL,
    User_level          TEXT         NOT NULL,
    Actual_skills       TEXT         NOT NULL,
    Recommended_skills  TEXT         NOT NULL,
    Recommended_courses TEXT         NOT NULL
);
```

---

## Design

The default Streamlit UI was replaced entirely with a custom dark interface. The design draws from modern SaaS dashboards — particularly Linear and Vercel's documentation aesthetic — without being a copy of either.

The key decisions:

**Dark background with low-contrast card borders.** Extended use of a bright UI adds eye strain and shifts attention away from content. Low-contrast borders maintain structure without competing with the data.

**Glassmorphism cards.** Semi-transparent backgrounds (`rgba(255,255,255,0.02)`) with subtle blur create depth without visual noise. Cards feel distinct from the background without requiring heavy borders or shadows.

**Explicit information hierarchy.** Score summaries, predictions, and flagged warnings are placed in distinct highlighted containers. The goal is that a candidate can scan the results page in under ten seconds and immediately understand their score, their predicted field, and what they're missing.

**Micro-interactions.** Hover states on cards and buttons (lift, glow, scale) make the interface feel responsive without being distracting. The interaction budget is intentionally small.

**Custom typography.** The Nevera typeface is used for headings throughout the application to establish a consistent visual identity separate from Streamlit's defaults.

---

## Engineering Challenges

Several non-obvious technical problems came up during development:

**Designing an ATS scoring algorithm without access to proprietary ATS logic.** Real ATS systems use undisclosed weighting. The solution was to model the scoring on documented best practices across five independently scored dimensions — rather than reverse-engineering any specific system — so the score would be meaningful and explainable to candidates.

**Building consistent skill extraction across diverse resume formats.** Resumes have no standard structure. A skills section in one resume might be a paragraph of prose in another. The spaCy pattern matcher runs on the full document text regardless of layout, with alias normalization applied before matching to handle shorthand, capitalization variations, and version suffixes.

**Aggregating internship listings from heterogeneous sources.** Internshala requires HTML scraping; Remotive and Jooble use different REST API formats; GitHub requires searching repository topics. Each source has its own error surface and rate limit behavior. The integration is handled through a unified interface (`job_scrapers.py`, `api_services.py`) that gracefully degrades if any single source is unavailable.

**Building a usable dark SaaS interface inside Streamlit's component model.** Streamlit renders through a React frontend with limited styling access. The entire visual layer required injecting custom HTML, CSS variables, and component overrides through `st.markdown` with `unsafe_allow_html=True`, alongside carefully targeted CSS selectors — including Streamlit's internal BasewWeb component classes — to achieve consistent theming across widgets.

**Maintaining dual database compatibility.** The application targets Neon PostgreSQL in production but needs to work with a local MySQL instance during development. Rather than maintaining two separate query layers, the abstraction in `database.py` detects the environment and routes to the appropriate driver while keeping the SQL interface identical.

**Dynamic AI context assembly.** Generic AI career chatbots give generic answers. Making the Gemini assistant useful required assembling the system prompt programmatically from the parsed candidate data before each session — so the assistant has the candidate's actual skills, score, and predicted field from the start of the conversation.

---

## Installation

### Prerequisites

- Python 3.9+
- A [Google Gemini API key](https://ai.google.dev/) — optional; core features work without it
- A Neon PostgreSQL connection string, or a local MySQL instance

### Setup

**1. Clone the repository**
```bash
git clone https://github.com/ShubhamSnSharma/InternHunt.git
cd InternHunt
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

**4. Configure environment variables**

Create a `.env` file in the project root:
```env
# Gemini API (optional — core features work without this)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# Database — use Option A for cloud, Option B for local

# Option A: Neon PostgreSQL
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require

# Option B: MySQL (local development)
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_password
DB_NAME=internhunt

# Admin panel
ADMIN_PASSWORD=your_admin_password_here

# Jooble API (optional)
JOOBLE_API_KEY=your_jooble_key_here
```

**5. Run the application**
```bash
streamlit run App.py
```

Open `http://localhost:8501` in your browser.

---

## Project Structure

```
InternHunt/
│
├── Core Application
│   ├── App.py                          # Main entry point — all pages and routing
│   ├── styles.py                       # Custom CSS/HTML theming injected via st.markdown
│   ├── resume_parser.py                # PDF parsing, skill extraction, ATS scoring
│   ├── chat_service.py                 # Gemini API session management
│   └── utils.py                        # Skill vocabulary, alias map, shared helpers
│
├── Machine Learning
│   ├── resume_classifier_v3_skills_mlp.pkl   # Serialized TF-IDF + MLP pipeline (10.1 MB)
│   ├── soft_skill_role_trainer.py             # Training script
│   ├── UpdatedResumeDataSet.csv               # Labeled training data (166 deduplicated samples)
│   └── ResumeClassification_Model.ipynb       # Exploration and evaluation notebook
│
├── Data & Integrations
│   ├── Courses.py                      # Course catalog, keyed by skill name
│   ├── database.py                     # DB connection logic (Neon PostgreSQL / MySQL)
│   ├── api_services.py                 # Remotive and Jooble API clients
│   ├── job_scrapers.py                 # Internshala and GitHub HTML scrapers
│   └── seed_database.py                # Schema creation and initial seeding
│
├── Configuration
│   ├── config.py                       # Paths, model file locations, env config
│   ├── error_handler.py                # Centralized error handling and logging
│   ├── .env.example                    # Environment variable reference
│   ├── .gitignore
│   └── .streamlit/
│       └── config.toml                 # Streamlit server settings
│
└── Assets & Docs
    ├── screenshots/                    # Application screenshots (used in README)
    ├── nevera_font/                    # Custom Nevera typeface files
    ├── Uploaded_Resumes/               # Runtime directory for uploaded PDFs
    ├── README.md
    ├── LICENSE
    └── PRIVACY.md
```

---

## Roadmap

### Near-term
- [ ] Resume version history — allow candidates to compare scores across multiple uploads
- [ ] DOCX support and OCR for image-based or scanned PDFs

### Medium-term
- [ ] LinkedIn and Indeed job source integrations
- [ ] OAuth-based admin authentication to replace the current password gate
- [ ] Docker image for self-hosted deployment

### Long-term
- [ ] Interview question generation based on the predicted role and detected skill gaps
- [ ] Multi-language resume support
- [ ] Resume comparison view between two uploaded versions

---

## Contributing

The project is straightforward to run locally. Follow the installation steps above, then:

```bash
# Fork, then clone your fork
git clone https://github.com/your-username/InternHunt.git

# Create a feature branch
git checkout -b feature/your-change

# Commit and push
git commit -m "Add: brief description"
git push origin feature/your-change

# Open a pull request
```

**Good places to start:**
- Adding a new job source: follow the existing pattern in `job_scrapers.py` or `api_services.py`
- Improving the ML model: start with `ResumeClassification_Model.ipynb` and `soft_skill_role_trainer.py`
- Expanding skill vocabulary: edit the pattern list and alias map in `utils.py`
- UI improvements: custom styles live in `styles.py`

---

## About the Developer

**Shubham Sharma**

InternHunt started as a way to understand what ATS systems actually evaluate and whether a machine learning pipeline could give students useful, specific feedback rather than generic resume tips. It grew into a full-stack AI application covering NLP, classification, a custom scoring engine, multi-source job aggregation, PostgreSQL persistence, and a Gemini-powered assistant.

Interests: machine learning, NLP, data science, AI applications, full-stack development.

- **GitHub** — [@ShubhamSnSharma](https://github.com/ShubhamSnSharma)
- **LinkedIn** — [linkedin.com/in/shubhamsnsharma](https://linkedin.com/in/shubhamsnsharma)
- **Portfolio** — [shubhamsnsharma](https://shubhamsn.vercel.app/)

---

## Acknowledgments

- [Google Gemini](https://ai.google.dev/) for the generative AI API
- [Streamlit](https://streamlit.io/) for the application framework
- [scikit-learn](https://scikit-learn.org/) and [spaCy](https://spacy.io/) for the ML and NLP tooling
- [Neon](https://neon.tech/) for serverless PostgreSQL
- [Remotive](https://remotive.com/) and [Jooble](https://jooble.org/) for the job data APIs

---

<div align="center">

If this project was useful, consider giving it a ⭐

</div>
