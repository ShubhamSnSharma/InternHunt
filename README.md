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

### 🌐 **Live Demo**

<div align="center">

[![Landing Page](https://img.shields.io/badge/🌟_Landing_Page-Visit_Now-6366F1?style=for-the-badge&labelColor=1e293b)](https://internhuntt.vercel.app)
[![Web App](https://img.shields.io/badge/🚀_Web_App-Try_Live-FF4B4B?style=for-the-badge&labelColor=1e293b)](https://internhunt.streamlit.app)

**👉 Start at the [Landing Page](https://internhuntt.vercel.app) → Click "Upload Resume" → Experience the [Full App](https://internhunt.streamlit.app)!**

</div>

---

[Features](#-features) • [Workflow](#-system-architecture--workflow) • [Screenshots](#-screenshots) • [Installation](#-installation) • [Machine Learning](#-machine-learning-model) • [Scrapers](#-job-scrapers--recommendations) • [Database](#-database--persistence)

</div>

---

## 📸 Screenshots

> **💡 Want to see it in action? Check out the [Live Demo](https://internhuntt.vercel.app)!**

### 🏠 Landing Page (Vercel)
![Landing Page](./screenshots/landing-page.png)
*Beautiful Figma-designed landing page hosted on Vercel*

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

## ✨ Features

### 📋 **Complete Resume Analysis Pipeline**

#### **1. Resume Upload & Parsing**
- 📄 **Multi-format Support** - Upload PDF or DOCX resumes (50MB limit)
- 🎯 **Advanced Text Extraction** - Utilizes `pypdf` and `python-docx` for reliable raw text decoding
- 📊 **Contact Detection** - Regex filters identify Name, Email, Phone, GitHub, and LinkedIn URLs

#### **2. Skill Detection & Normalization**
- 🔍 **NLP-Powered Detection** - Identifies 100+ technical skills via a dictionary-based `spaCy` matcher
- 🏷️ **Fuzzy Matching** - Employs `fuzzywuzzy` to recognize variations and typos (e.g. `k8s` mapped to `Kubernetes`)
- 🎨 **Domain-based Skill Badges** - Groups parsed skills visually by category (Languages, Databases, DevOps, mobile, etc.)

#### **3. AI-Detected Career Profile**
- 🧠 **ML Classification** - Neural network (MLPClassifier) role prediction trained on a deduplicated unique dataset
- 🎯 **Top 3 Role Recommendations** - Displays alternative career matches with corresponding probability scores
- 📊 **Probability Calibration** - Sharp softmax outputs map directly to confidence ratings (High, Medium, Low)

#### **4. ATS Performance Analytics**
- 📈 **ATS Score Dial** - Tracks resume compatibility with modern Applicant Tracking Systems
- 🎯 **Completeness Checks** - Evaluates the presence of 5 core sections (Contact, Skills, Experience, Education, Projects)
- 💡 **Actionable Optimization Tips** - Tailored suggestions to improve formatting and add missing information

#### **5. Double-Source Recommendations**
- 🎓 **Tailored Courses** - Pulls matched learning path suggestions from a mapped course repository (`Courses.py`)
- 🌐 **Live Internships** - Combines multiple APIs and web scrapers to gather matched real-time listings

#### **6. Context-Aware AI Chatbot Assistant**
- 💬 **Gemini AI Coaching** - Conversational career chat powered by Google Gemini (`gemini-1.5-flash`)
- 📚 **Resume-Aware System Instructions** - Chatbot reads the parsed resume details, scoring metrics, and missing keywords to suggest customized advice

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

## 🌐 Job Scrapers & Recommendations

The application does not rely on a single source but combines APIs and custom HTML scrapers:

* **Internshala Scraper:** A Python scraper using `requests` and `BeautifulSoup4` (`lxml` parser) to scrape India-focused listings. It queries Internshala’s keyword URL structures (e.g. `https://internshala.com/internships/keywords-{query}`) and parses details like stipends, durations, and application links directly from individual internship cards.
* **Remotive API:** Pulls remote developer opportunities from Remotive's free public endpoint based on the top 5 parsed skills.
* **Jooble API:** Queries the global Jooble job search engine using HTTP POST requests containing skill keywords and locations. (Requires `JOOBLE_API_KEY`).
* **GitHub Repositories Search:** Scrapes GitHub search listings looking for repositories tagged with `hiring` or `internship` matching the candidate's core skills.

---

## 💾 Database & Persistence

InternHunt supports dual persistence schemes for local development and cloud production:

* **Neon serverless PostgreSQL:** (Preferred in production). Connects using `psycopg2` via a connection string environment variable (`DATABASE_URL`).
* **Local MySQL:** (Fallback for local development). Connects using `pymysql` based on local configuration credentials.

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

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:
1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

---

## 👨‍💻 Author

**Shubham Sharma**
- GitHub: [@ShubhamSnSharma](https://github.com/ShubhamSnSharma)

---

## 🙏 Acknowledgments
- [Google Gemini](https://ai.google.dev/) for conversational AI capabilities.
- [Streamlit](https://streamlit.io/) for the clean web framework.
- [Internshala](https://internshala.com/) for internship listings.
- All open-source contributors.
