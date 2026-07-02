<div align="center">

# InternHunt

### AI-Powered Internship Matching Platform

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Google Gemini](https://img.shields.io/badge/Google%20Gemini-8E75B2?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

[![Vercel](https://img.shields.io/badge/Landing-Live_on_Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white)](https://internhuntt.vercel.app)
[![Streamlit Cloud](https://img.shields.io/badge/App-Live_on_Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://internhunt.streamlit.app)

**Intelligent Internship Matching Using ML, APIs & Web Data**

---

**👉 Start at the [Landing Page](https://internhuntt.vercel.app) → Click "Upload Resume" → Experience the [Full App](https://internhunt.streamlit.app)!**

</div>

---

## 📸 Screenshots

> **💡 Want to see it in action? Check out the [Live Demo](https://internhuntt.vercel.app)!**

### 🏠 Landing Page (Vercel)
![Landing Page](./screenshots/landing-page.png)
*Beautiful Figma-designed landing page hosted on Vercel*

### 🚀 Main Application Portal (Streamlit)
![Main App Landing Page](./screenshots/landing-page-main.png)
*Core interactive app landing page on Streamlit Cloud*

### 💼 Resume Analysis
![Resume Upload](./screenshots/resume-upload.png)
*Smart resume parsing and classification*

### 🤖 AI Career Assistant
![AI Chatbot](./screenshots/chatbot.png)
*Powered by Google Gemini for personalized career guidance*

### 🎓 Course Recommendations
![Course Recommendations](./screenshots/courses.png)
*Tailored learning paths based on your profile*

### 🔍 Job Search
![Job Search 1](./screenshots/job-search1.png)
![Job Search 2](./screenshots/job-search2.png)
*Real-time internship opportunities matching your skills (scraped from multiple platforms like Internshala, Remotive, and Jooble)*

### 🔐 Admin Dashboard
![Admin Dashboard](./screenshots/admin-dashboard.png)
*User management and analytics with premium Plotly interactive visualizations*

---

## 🎯 Key Features

### 📋 Complete Resume Analysis Pipeline

| Stage | What Happens |
|-------|--------------|
| **1. Upload & Parse** | PDF/DOCX support (50MB limit), text extraction via `pypdf` + `python-docx` |
| **2. Skill Detection** | 100+ technical skills via spaCy NLP + fuzzy matching (e.g., `k8s` → `Kubernetes`) |
| **3. Role Prediction** | MLP Neural Network (TF-IDF → 128/64 hidden layers) → Top 3 roles with confidence |
| **4. ATS Scoring** | 5-factor breakdown: Content (50%), Formatting (15%), Keywords (20%), Experience (10%), Readability (5%) |
| **5. Recommendations** | Live internships (Jooble, Internshala, Remotive, GitHub) + curated courses |
| **6. AI Assistant** | Gemini 1.5 Flash with full resume context for personalized career coaching |

---

## ⚙️ System Architecture & Workflow

InternHunt processes resume uploads, evaluates scoring, logs user details to the database, queries external scrapers, and initializes the chatbot context in a highly structured pipeline:

![System Workflow Diagram](./screenshots/workflow-diagram.png)

### **Workflow Breakdown:**
1. **Extraction & Preprocessing:** The uploaded document is parsed, stripped of raw formatting, and cleaned of non-ASCII symbols and excessive spacing.
2. **Parallel Feature Extraction:** 
   - **Regex filters** extract email, phone, and profile URLs.
   - **spaCy matcher** extracts normalized skill sets.
   - **TF-IDF Vectorizer** maps the cleaned text to 2500 terms, which are classified by the **MLPClassifier** to predict the candidate's career role.
3. **ATS Assessment:** Core sections are checked, and missing skills are highlighted by matching actual skills against predicted career role profiles.
4. **Data Persistence:** Candidate profiles and computed stats are logged to **Neon serverless PostgreSQL** for admin audit and analytics.
5. **Recommendation & Assistant Routing:** Matched courses (from `Courses.py`) and job listings are displayed, and a detailed profile is built and loaded into the **Google Gemini system instructions** so the sidebar assistant chatbot can answer resume-specific questions.

---

## 🤖 Machine Learning Model

InternHunt utilizes a **custom-trained Multi-Layer Perceptron (MLP) Neural Network** classifier to automatically route resumes to 25 distinct job roles.

#### **Model Architecture:**
- **Algorithm:** Multi-Layer Perceptron Classifier (scikit-learn)
- **Vectorization:** TF-IDF (Term Frequency-Inverse Document Frequency)
- **Pipeline:** `TfidfVectorizer` (ngram_range=(1, 2), max_features=2500) → `MLPClassifier` (128, 64 hidden nodes)
- **File:** `resume_classifier_v3_skills_mlp.pkl` (10.1 MB)
- **Training Data:** `UpdatedResumeDataSet.csv` (166 unique deduplicated samples to prevent training bias)

#### **Model Performance:**
| Metric | Score |
|--------|-------|
| **Test Accuracy** | **85.29%** |
| **Precision** | **88.2%** (weighted avg) |
| **Recall** | **85.3%** (weighted avg) |
| **F1-Score** | **81.9%** (weighted avg) |
| **Cross-Validation** | **81.69% ± 0.85%** (3-fold Stratified) |

#### **Training Configuration:**
```python
Pipeline([
    ('tfidf', TfidfVectorizer(
        max_features=2500,        # Vocabulary size limit
        ngram_range=(1, 2),       # Unigrams & bigrams
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

---

## 🌐 Job Sources & Recommendations

InternHunt combines **APIs + custom scrapers** for comprehensive coverage:

| Source | Type | Coverage | Key Details |
|--------|------|----------|-------------|
| **Internshala** | HTML Scraper | India-focused internships | Keyword-based URLs, parses stipend, duration, apply links |
| **Remotive** | REST API | Global remote dev jobs | Free public endpoint, filtered by top 5 skills |
| **Jooble** | REST API | Global job search | Requires `JOOBLE_API_KEY`, POST with keywords + location |
| **GitHub** | HTML Scraper | Hiring/Internship repos | Searches repos with `topic:hiring` or `topic:internship` |

---

## 💾 Database & Persistence

InternHunt supports dual persistence schemes for local development and cloud production:

Dual persistence for local dev + cloud production:

| Database | Use Case | Driver |
|----------|----------|--------|
| **Neon PostgreSQL** | Production (Streamlit Cloud) | `psycopg2` via `DATABASE_URL` |
| **MySQL** | Local development fallback | `pymysql` via env vars |

### **Logged User Registry Schema:**
```sql
CREATE TABLE IF NOT EXISTS user_data (
    ID SERIAL PRIMARY KEY,
    Name VARCHAR(500) NOT NULL,
    Email_ID VARCHAR(500) NOT NULL,
    resume_score VARCHAR(8) NOT NULL,
    Timestamp VARCHAR(50) NOT NULL,
    Page_no VARCHAR(5) NOT NULL,
    Predicted_Field TEXT NOT NULL,
    User_level TEXT NOT NULL,
    Actual_skills TEXT NOT NULL,
    Recommended_skills TEXT NOT NULL,
    Recommended_courses TEXT NOT NULL
);
```

---

## 🚀 Installation

### Prerequisites
- Python 3.9 or higher
- pip package manager
- Google Gemini API key ([Get one here](https://ai.google.dev/))

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/ShubhamSnSharma/internhunt2.git
cd internhunt2
```

2. **Create virtual environment**
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download NLTK data** (Required for NLP)
```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

5. **Set up environment variables**
Create a `.env` file in the root directory:
```env
# Google Gemini API
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# Neon Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@host.neon.tech/dbname?sslmode=require
```

6. **Run the application**
```bash
streamlit run App.py
```

The app will open in your browser at `http://localhost:8501` 🎉

---

## 📁 Project Structure

```
internhunt2/
├── 📄 App.py                           # Main Streamlit application entry point
├── 🎨 styles.py                        # Centralized UI styling and themes
├── 🤖 chat_service.py                  # Gemini AI chatbot service
├── 📝 resume_parser.py                 # Resume parsing & NLP analysis
├── ⚙️ config.py                        # Configuration management
├── 🛠️ utils.py                         # Utility functions
├── 💾 database.py                      # Neon PostgreSQL database operations
├── 🌐 api_services.py                  # External API integrations (Jooble)
├── 🔍 job_scrapers.py                  # Job scraping (Internshala)
├── ⚠️ error_handler.py                 # Error handling & logging
├── 📚 Courses.py                       # Course recommendation engine
│
├── 🤖 resume_classifier_v3_skills_mlp.pkl # Upgraded ML model (TF-IDF + MLP, 10.1 MB)
├── ⚙️ soft_skill_role_trainer.py         # Local model training script
├── 📊 UpdatedResumeDataSet.csv            # Training dataset (166 deduplicated unique samples)
├── 📓 ResumeClassification_Model.ipynb    # Exploration model notebook
│
├── 📋 requirements.txt                 # Python dependencies
├── 📖 README.md                        # Project documentation
├── 📜 LICENSE                          # MIT License
├── 🔒 PRIVACY.md                       # Privacy policy
├── 🔐 .env.example                     # Environment variables template
├── 🚫 .gitignore                       # Git ignore rules
│
├── 📁 .streamlit/                      # Streamlit configuration
│   ├── config.toml                     # App configuration
│   └── secrets.toml.example            # Secrets template
│
├── 🔤 nevera_font/                     # Custom Nevera font files
│   ├── Nevera-Bold.ttf
│   ├── Nevera-Regular.ttf
│   └── Nevera-Light.ttf
│
├── 📂 Uploaded_Resumes/                # User uploaded resume storage
│   └── .gitkeep                        # Preserve directory in Git
│
└── 📁 screenshots/                     # Application screenshots for README
```

---

## 🧪 Development & Testing

### Run Model Training (Optional)
```bash
# Retrain the classifier with new data
python soft_skill_role_trainer.py
```

### Check Gemini Connection
```bash
python -c "from chat_service import check_gemini_health; print(check_gemini_health())"
```

### Linting & Formatting
```bash
# If you have ruff/black configured
ruff check .
black .
```

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create a feature branch** — `git checkout -b feature/amazing-feature`
3. **Commit changes** — `git commit -m 'Add amazing feature'`
4. **Push to branch** — `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Ideas for Contribution Ideas:
- Add new job sources (LinkedIn, Indeed, Wellfound)
- Improve resume parsing for DOCX/images
- Add more ML roles or fine-tune the classifier
- Enhance UI/UX with new visualizations
- Write tests for core modules

---

## 👨‍💻 Author

**Shubham Sharma**
- GitHub: [@ShubhamSnSharma](https://github.com/ShubhamSnSharma)
- Project: [internhunt2](https://github.com/ShubhamSnSharma/internhunt2)

---

## 🙏 Acknowledgments

- [Google Gemini](https://ai.google.dev/) — Conversational AI capabilities
- [Streamlit](https://streamlit.io/) — Beautiful web framework for data apps
- [Internshala](https://internshala.com/) — Internship listings for Indian students
- [Remotive](https://remotive.com/) — Free remote job API
- [Jooble](https://jooble.org/) — Global job search API
- [scikit-learn](https://scikit-learn.org/) — Machine learning toolkit
- [spaCy](https://spacy.io/) — Industrial-strength NLP
- All open-source contributors ❤️

---

<div align="center">

**⭐ Star this repo if you found it helpful!**

Made with ❤️ by students, for students

</div>
