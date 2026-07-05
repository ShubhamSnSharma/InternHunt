#!/usr/bin/env python3
"""
InternHunt - Resume Analyzer Application
A comprehensive resume analysis tool with job recommendations and skill assessment.
"""
# fmt: off
# Linting disabled for embedded HTML/CSS strings.
# fmt: on

# Core libraries
import streamlit as st
from streamlit_lottie import st_lottie
import pandas as pd
import base64
import plotly.express as px
import random
import time
import datetime
import os
import re
import requests
import nltk
import joblib
from pathlib import Path


# Import custom modules
from config import Config
from database import DatabaseManager
db_manager = DatabaseManager()
from api_services import JobAPIService, fetch_internshala_internships
from resume_parser import ResumeParser
from styles import StyleManager
from utils import AnalyticsUtils
from chat_service import chat_gemini, build_resume_context, check_gemini_health, get_suggested_questions
from markdown_it import MarkdownIt

# Initialize Markdown parser
md_parser = MarkdownIt()
# st.iframe replaces the deprecated st.components.v1.html for raw HTML iframe embedding
from job_scrapers import scrape_all, scrape_internshala, scrape_internshala_by_keywords
from Courses import (
    ds_course, web_course, android_course, ios_course, uiux_course,
    ai_course, cyber_course, cloud_course, data_eng_course, blockchain_course
)

import warnings
warnings.filterwarnings("ignore", message="coroutine 'expire_cache' was never awaited")

def clean_html(html_str):
    """Strip all leading and trailing whitespace from each line to prevent Markdown code-block interpretation."""
    if not html_str:
        return ""
    return "\n".join(line.strip() for line in html_str.split("\n"))

# -----------------------------
# ML Model Loading
# -----------------------------

MODEL_CANDIDATES = [
    "resume_classifier_v3_skills_mlp.pkl",
    "resume_classifier_v2.pkl",
]

SKILL_HEADINGS = [
    "skills",
    "skill details",
    "technical skills",
    "technical proficiency",
    "technical expertise",
    "core competencies",
   # Core dependencies
   # streamlit-lottie==0.0.5",
    "technologies",
    "tools & technologies",
    "software proficiency",
    "skill set",
]

STOP_HEADINGS = [
    "education",
    "education details",
    "experience",
    "work experience",
    "employment history",
    "professional experience",
    "company details",
    "projects",
    "project details",
    "certification",
    "certifications",
    "achievements",
    "responsibilities",
    "declaration",
    "personal details",
    "objective",
    "summary",
]

@st.cache_data
def load_lottie(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def clean_resume_text(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"http\S+|www\.\S+", " ", text)
    text = re.sub(r"[^\x00-\x7F]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _compile_heading_regex(headings):
    escaped = [re.escape(h) for h in headings]
    return re.compile(r"(?i)\b(?:%s)\b\s*:?" % "|".join(escaped))


SKILL_RE = _compile_heading_regex(SKILL_HEADINGS)
STOP_RE = _compile_heading_regex(STOP_HEADINGS)


def prepare_text_for_role_model(resume_text: str, model=None) -> str:
    """
    Match inference-time preprocessing to the model's training mode.

    - Legacy models use the full cleaned resume text.
    - The new v3 soft-computing model is trained on skill-focused text,
      so we extract the most relevant skill sections before prediction.
    """
    cleaned_text = clean_resume_text(resume_text)
    training_mode = getattr(model, "_internhunt_training_mode", "legacy_full_resume")

    if training_mode != "deduplicated_skill_focused":
        return cleaned_text

    lower_text = cleaned_text.lower()
    snippets = []

    for match in SKILL_RE.finditer(lower_text):
        start = match.start()
        next_stop = STOP_RE.search(lower_text, match.end())
        end = next_stop.start() if next_stop else min(len(cleaned_text), match.end() + 1200)
        chunk = cleaned_text[start:end].strip(" :-")
        if chunk:
            snippets.append(chunk)

    if not snippets:
        boundary = STOP_RE.search(lower_text)
        fallback = cleaned_text[: boundary.start()] if boundary else cleaned_text[:1200]
        snippets.append(fallback)

    merged = " ".join(snippets)
    merged = re.sub(r"\bexprience\b", "experience", merged, flags=re.IGNORECASE)
    merged = re.sub(r"\bmonths?\b", " ", merged, flags=re.IGNORECASE)
    merged = re.sub(r"\bcompany details\b.*", " ", merged, flags=re.IGNORECASE)
    merged = re.sub(r"\s+", " ", merged).strip()
    return merged

@st.cache_resource
def load_resume_classifier():
    """
    Load the trained resume classification model.

    Supports both:
      - Old format: plain Pipeline (LogisticRegression)
      - New format: dict with 'model' key (MLPClassifier — upgraded)

    Logs the model type so the UI can display it correctly.
    """
    import sklearn

    try:
        model_path = next((path for path in MODEL_CANDIDATES if Path(path).exists()), None)
        if model_path is None:
            raise FileNotFoundError

        data = joblib.load(model_path)

        if isinstance(data, dict) and "model" in data:
            model = data["model"]
            trained_version = data.get("sklearn_version", "unknown")
            model_type = data.get("model_type", "Unknown")

            # Attach metadata to model object so UI can read it
            model._internhunt_model_type = model_type
            model._internhunt_architecture = data.get(
                "architecture", "TF-IDF → Classifier"
            )
            model._internhunt_training_mode = data.get(
                "training_mode", "legacy_full_resume"
            )
            model._internhunt_model_filename = model_path

            if trained_version != sklearn.__version__:
                st.warning(
                    f"⚠️ Model trained on scikit-learn {trained_version}, "
                    f"running on {sklearn.__version__}. "
                    f"Retraining recommended if unexpected issues occur."
                )
        else:
            # Backward-compatible fallback for older .pkl without metadata
            model = data
            model._internhunt_model_type = "LogisticRegression"
            model._internhunt_architecture = "TF-IDF(5000) → LogisticRegression"
            model._internhunt_training_mode = "legacy_full_resume"
            model._internhunt_model_filename = model_path

        return model

    except FileNotFoundError:
        st.error(
            "❌ Model file not found. "
            "Please ensure one of these files exists in the project directory: "
            f"{', '.join(MODEL_CANDIDATES)}"
        )
        return None

    except Exception as e:
        st.warning(f"⚠️ Could not load ML model: {e}")
        return None


def fuzzy_label(probability: float) -> str:
    """
    Assign a fuzzy linguistic confidence label to a classifier probability.

    Soft Computing concept: instead of binary (yes/no), the model output is
    interpreted through fuzzy membership regions:

      High   : p > 0.70  — dominant, highly confident prediction
      Medium : 0.40 ≤ p ≤ 0.70  — uncertain overlap zone (alternative role)
      Low    : p < 0.40  — weak secondary signal

    This converts the neural network's crisp probability into a
    human-readable, linguistically meaningful confidence grade.
    """
    if probability > 0.70:
        return "High"
    elif probability >= 0.40:
        return "Medium"
    else:
        return "Low"


@st.cache_resource
def get_embedding_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def predict_resume_category(resume_text, model=None):
    """
    Predict resume job category using the trained pipeline.

    Returns:
        predicted_category (str): The top predicted role.
        top_3_predictions (list[dict]): Top-3 predictions, each containing:
            - 'category'    : str   — role name
            - 'probability' : float — raw probability from predict_proba()
            - 'fuzzy_label' : str   — 'High' | 'Medium' | 'Low'

    Example output:
        (
            "Data Science",
            [
                {"category": "Data Science",     "probability": 0.82, "fuzzy_label": "High"},
                {"category": "Business Analyst", "probability": 0.12, "fuzzy_label": "Medium"},
                {"category": "Database",         "probability": 0.06, "fuzzy_label": "Low"}
            ]
        )
    """
    if model is None:
        model = load_resume_classifier()

    if model is None:
        return None, []

    try:
        model_input = prepare_text_for_role_model(resume_text, model)
        model_type = getattr(model, "_internhunt_model_type", "Unknown")

        if model_type == "MLPClassifier_Embeddings":
            embedder = get_embedding_model()
            features = embedder.encode([model_input], show_progress_bar=False)
            predicted_category = str(model.predict(features)[0])
            probabilities = model.predict_proba(features)[0]
        else:
            predicted_category = str(model.predict([model_input])[0])
            probabilities = model.predict_proba([model_input])[0]

        classes = model.classes_

        # Top-3 indices sorted by descending probability
        top_3_idx = probabilities.argsort()[-3:][::-1]

        top_3_predictions = [
            {
                "category"   : str(classes[idx]),
                "probability": float(probabilities[idx]),
                "fuzzy_label": fuzzy_label(probabilities[idx]),   # ← NEW
            }
            for idx in top_3_idx
        ]

        return predicted_category, top_3_predictions

    except Exception as e:
        st.error(f"Error predicting category: {e}")
        return None, []

def get_courses_by_category(predicted_category):
    """Get relevant courses based on predicted category"""
    category_course_map = {
        # --- Programming & Software ---
        'Java Developer': web_course + android_course,
        'Python Developer': ds_course + web_course + ai_course,
        'DotNet Developer': web_course,
        'Automation Testing': web_course,
        'Testing': web_course,

        # --- Data & AI ---
        'Data Science': ds_course + ai_course + data_eng_course,
        'Machine Learning Engineer': ai_course + ds_course,
        'AI Engineer': ai_course + ds_course,
        'Artificial Intelligence': ai_course + ds_course,
        'Business Analyst': ds_course + data_eng_course,

        # --- Web & Design ---
        'Web Designing': web_course + uiux_course,
        'Frontend Developer': web_course + uiux_course,
        'Full Stack Developer': web_course + cloud_course,
        'UI/UX Designer': uiux_course,

        # --- Cloud & DevOps ---
        'DevOps Engineer': cloud_course,
        'Cloud Engineer': cloud_course,
        'Site Reliability Engineer': cloud_course,

        # --- Cybersecurity ---
        'Network Security Engineer': cyber_course,
        'Cybersecurity Analyst': cyber_course,
        'Ethical Hacker': cyber_course,

        # --- Database & Big Data ---
        'Database': data_eng_course,
        'Hadoop': data_eng_course,
        'ETL Developer': data_eng_course,
        'Data Engineer': data_eng_course,

        # --- Blockchain & Web3 ---
        'Blockchain': blockchain_course,
        'Web3 Developer': blockchain_course,
        'Smart Contract Developer': blockchain_course,

        # --- Others / General Fields ---
        'HR': [],
        'Operations Manager': [],
        'SAP Developer': cloud_course,
        'Mechanical Engineer': [],
        'Civil Engineer': [],
        'Electrical Engineering': [],
        'Sales': [],
        'Arts': uiux_course,
        'Health and fitness': [],
        'Advocate': [],
        'PMO': [],
    }

    # Fallback recommendation (in case category not found)
    fallback_courses = ds_course + web_course + ai_course
    return category_course_map.get(predicted_category, fallback_courses)


import re

def filter_jobs_by_category(jobs, predicted_category):
    """
    Filter and rank jobs based on how relevant they are to the predicted career category.
    Uses weighted keyword matching (core vs related), fuzzy matching, and adaptive fallback.
    """

    if not predicted_category or not jobs:
        return jobs

    # ========== SMART FUZZY MATCHER ==========
    def keyword_in_text(keyword, text):
        """Smart matching for plural, hyphen, spacing variations"""
        pattern = r'\b' + re.escape(keyword).replace(r'\-', r'[-\s]?') + r's?\b'
        return re.search(pattern, text, re.IGNORECASE)

    # ========== CATEGORY KEYWORDS ==========
    category_keywords = {
        # --- Core Developer Roles ---
        'Java Developer': {
            'core': ['java', 'spring', 'jvm', 'kotlin'],
            'related': ['backend', 'software', 'developer', 'engineer']
        },
        'Python Developer': {
            'core': ['python', 'django', 'flask'],
            'related': ['backend', 'software', 'developer', 'ai', 'ml']
        },
        'Web Designing': {
            'core': ['web', 'frontend', 'ui', 'ux', 'html', 'css'],
            'related': ['react', 'angular', 'vue', 'javascript', 'designer']
        },
        'Full Stack Developer': {
            'core': ['full stack', 'mern', 'mean', 'frontend', 'backend'],
            'related': ['react', 'node', 'express', 'django', 'api']
        },
        'Android Developer': {
            'core': ['android', 'kotlin', 'java', 'mobile'],
            'related': ['flutter', 'compose']
        },
        'iOS Developer': {
            'core': ['ios', 'swift', 'swiftui', 'xcode'],
            'related': ['mobile', 'app', 'developer']
        },

        # --- Data & AI ---
        'Data Science': {
            'core': ['data', 'scientist', 'analytics', 'analysis'],
            'related': ['machine learning', 'ml', 'ai', 'insight', 'python', 'sql']
        },
        'Machine Learning Engineer': {
            'core': ['machine learning', 'ml', 'ai', 'neural'],
            'related': ['pytorch', 'tensorflow', 'deep learning']
        },
        'AI Engineer': {
            'core': ['ai', 'artificial intelligence', 'ml', 'deep learning'],
            'related': ['llm', 'nlp', 'vision', 'transformer']
        },
        'Data Engineer': {
            'core': ['data engineer', 'pipeline', 'etl', 'big data'],
            'related': ['airflow', 'spark', 'hadoop', 'aws glue', 'kafka']
        },
        'Business Analyst': {
            'core': ['business analyst', 'data', 'requirements', 'insights'],
            'related': ['excel', 'tableau', 'power bi']
        },

        # --- Cloud & DevOps ---
        'DevOps Engineer': {
            'core': ['devops', 'ci/cd', 'docker', 'kubernetes'],
            'related': ['aws', 'azure', 'gcp', 'infrastructure', 'terraform']
        },
        'Cloud Engineer': {
            'core': ['cloud', 'aws', 'azure', 'gcp', 'infrastructure'],
            'related': ['devops', 'serverless', 'kubernetes', 'docker']
        },
        'Site Reliability Engineer': {
            'core': ['sre', 'reliability', 'monitoring'],
            'related': ['devops', 'cloud', 'automation']
        },

        # --- Cybersecurity ---
        'Network Security Engineer': {
            'core': ['network', 'security', 'cyber'],
            'related': ['infosec', 'pentesting', 'firewall', 'ethical hacking']
        },
        'Cybersecurity Analyst': {
            'core': ['cybersecurity', 'security analyst', 'threat', 'incident'],
            'related': ['vulnerability', 'forensics', 'malware', 'siem']
        },
        'Ethical Hacker': {
            'core': ['ethical hacker', 'pentest', 'penetration testing'],
            'related': ['bug bounty', 'offensive security', 'owasp']
        },

        # --- Blockchain & Web3 ---
        'Blockchain Developer': {
            'core': ['blockchain', 'web3', 'solidity', 'crypto'],
            'related': ['ethereum', 'smart contract', 'defi']
        },
        'Web3 Developer': {
            'core': ['web3', 'blockchain', 'solidity'],
            'related': ['dapp', 'nft', 'crypto']
        },

        # --- UI/UX & Creative ---
        'UI/UX Designer': {
            'core': ['ui', 'ux', 'figma', 'design'],
            'related': ['prototype', 'wireframe', 'adobe', 'user research']
        },

        # --- Other Tech Roles ---
        'Database': {
            'core': ['database', 'dba', 'sql'],
            'related': ['oracle', 'mongodb', 'mysql', 'postgresql']
        },
        'Testing': {
            'core': ['testing', 'qa', 'quality', 'automation'],
            'related': ['selenium', 'software', 'engineer']
        },
        'SAP Developer': {
            'core': ['sap', 'erp'],
            'related': ['developer', 'abap']
        },
        'Operations Manager': {
            'core': ['operations', 'manager'],
            'related': ['project', 'business', 'process']
        },
    }

    # ========== GET CATEGORY KEYWORDS ==========
    keyword_set = category_keywords.get(predicted_category, {})
    core_keywords = keyword_set.get('core', [])
    related_keywords = keyword_set.get('related', [])

    if not core_keywords and not related_keywords:
        return jobs  # no filtering if unknown category

    # ========== FILTER & SCORE JOBS ==========
    scored_jobs = []

    for job in jobs:
        title = (job.get('title', '') or '').lower().replace('-', ' ')
        description = (job.get('description', '') or '').lower().replace('-', ' ')
        company = (job.get('company', '') or '').lower()
        tags = ' '.join(job.get('tags', [])).lower()
        job_text = f"{title} {description} {company} {tags}"

        title_score, body_score = 0, 0

        # --- Score titles ---
        for keyword in core_keywords:
            if keyword_in_text(keyword, title):
                title_score += 5
        for keyword in related_keywords:
            if keyword_in_text(keyword, title):
                title_score += 2

        # --- Score description, company, tags ---
        for keyword in core_keywords:
            if keyword_in_text(keyword, job_text):
                body_score += 3
        for keyword in related_keywords:
            if keyword_in_text(keyword, job_text):
                body_score += 1

        total_score = title_score + body_score

        has_core = any(keyword_in_text(kw, job_text) for kw in core_keywords)
        has_strong_title = title_score >= 3

        if has_core or has_strong_title or total_score >= 4:
            scored_jobs.append((job, total_score))

    # ========== SORT & FALLBACK ==========
    scored_jobs.sort(key=lambda x: x[1], reverse=True)
    filtered_jobs = [job for job, score in scored_jobs]

    # If filtering removes too many jobs, fallback to original list
    if len(filtered_jobs) < max(3, len(jobs) * 0.2):
        return jobs

    return filtered_jobs if filtered_jobs else jobs


# -----------------------------
# Application Setup
# -----------------------------

def initialize_app():
    """Initialize the Streamlit application"""
    # Initialize page state if it doesn't exist
    if 'page' not in st.session_state:
        st.session_state.page = "analyzer"  # Skip landing page, go directly to analyzer
    # Set page config with theme first
    st.set_page_config(
        page_title=Config.APP_TITLE,
        page_icon=Config.APP_ICON,
        layout="wide",
        initial_sidebar_state="expanded",
    )
    
    # Apply Streamlit component overrides for dark theme
    st.markdown(StyleManager.get_streamlit_component_overrides(), unsafe_allow_html=True)
    
    # Validate configuration
    config_status = Config.validate_config()
    if not config_status['valid']:
        st.error("Configuration issues found:")
        for issue in config_status['issues']:
            st.error(f"- {issue}")
        st.stop()
    
    # Show warnings if any
    if config_status.get('warnings'):
        for warning in config_status['warnings']:
            st.warning(f"⚠️ {warning}")
    
    # Initialize session state
    if "page" not in st.session_state:
        st.session_state.page = "landing"
    
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "light"
    
    if "admin_authenticated" not in st.session_state:
        st.session_state.admin_authenticated = False

    # Ensure NLTK data only once per session
    if not st.session_state.get("nltk_ready"):
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
        st.session_state["nltk_ready"] = True
    
    # Apply styles
    StyleManager.apply_global_styles()
    StyleManager.apply_theme_styles(st.session_state.theme_mode)
    
    # Apply sidebar chat styles
    st.markdown(StyleManager.get_sidebar_chat_styles(), unsafe_allow_html=True)

@st.cache_resource(show_spinner=False)
def get_resume_parser():
    """Get cached resume parser instance"""
    return ResumeParser()

@st.cache_data
def _load_nevera_font():
    """Load and encode Nevera font as base64"""
    try:
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'nevera_font', 'Nevera-Regular.otf')
        if not os.path.exists(font_path):
            return ""
        with open(font_path, 'rb') as f:
            font_bytes = f.read()
        encoded = base64.b64encode(font_bytes).decode('utf-8')
        return encoded
    except Exception as e:
        return ""

def display_header():
    """Display professional application header with ultra-modern design"""
    # Apply animations
    st.markdown(StyleManager.get_animation_styles(), unsafe_allow_html=True)
    
    # Apply default light theme
    if 'theme_mode' not in st.session_state:
        st.session_state.theme_mode = 'light'
        StyleManager.apply_theme_styles('light')
    
    # Load font inline
    font_b64 = _load_nevera_font()
    
    # Display hero section with custom font
    st.markdown(StyleManager.get_hero_section(font_b64), unsafe_allow_html=True)
    
    # Apply scroll indicator animation styles
    st.markdown(StyleManager.get_scroll_indicator_styles(), unsafe_allow_html=True)


def show_ai_loading_dashboard():
    """Display a premium multi-stage AI analysis loading dashboard"""
    stages = [
        ("Uploading Resume", "📤"),
        ("Extracting Resume Information", "📄"),
        ("Analyzing Skills & Expertise", "🧠"),
        ("Searching Internship Databases", "🔍"),
        ("Ranking Matched Opportunities", "🎯"),
        ("Generating Recommendations", "✨")
    ]
    
    placeholder = st.empty()
    
    # Custom CSS for the loader
    loader_css = """
    <style>
    .loading-dashboard {
        background: rgba(20, 26, 53, 0.45);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 30px;
        max-width: 650px;
        margin: 2rem auto;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
    }
    .loading-title {
        font-family: 'Poppins', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: #F8FAFC;
        margin-bottom: 20px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .loader-pulse {
        width: 12px;
        height: 12px;
        background: #2dd4bf;
        border-radius: 50%;
        animation: pulse-ring 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        box-shadow: 0 0 10px #2dd4bf;
    }
    @keyframes pulse-ring {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(45, 212, 191, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(45, 212, 191, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(45, 212, 191, 0); }
    }
    .stage-item {
        display: flex;
        align-items: center;
        gap: 15px;
        padding: 12px 16px;
        margin-bottom: 10px;
        border-radius: 10px;
        transition: all 0.3s ease;
    }
    .stage-active {
        background: rgba(99, 102, 241, 0.12);
        border: 1px solid rgba(99, 102, 241, 0.3);
        color: #F8FAFC;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.1);
    }
    .stage-pending {
        opacity: 0.4;
        color: #94A3B8;
    }
    .stage-complete {
        color: #10B981;
        font-weight: 500;
    }
    .stage-icon {
        font-size: 1.25rem;
    }
    .status-check {
        font-size: 1rem;
        margin-left: auto;
    }
    .progress-bar-container {
        width: 100%;
        height: 6px;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 999px;
        overflow: hidden;
        margin-bottom: 25px;
    }
    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #6366F1, #2dd4bf);
        transition: width 0.4s ease;
    }
    </style>
    """
    
    for i in range(len(stages)):
        active_idx = i
        progress_pct = int(((active_idx + 1) / len(stages)) * 100)
        
        stages_html = ""
        for idx, (name, icon) in enumerate(stages):
            if idx < active_idx:
                stages_html += f"""
                <div class="stage-item stage-complete">
                    <span class="stage-icon">{icon}</span>
                    <span>{name}</span>
                    <span class="status-check">✓</span>
                </div>
                """
            elif idx == active_idx:
                stages_html += f"""
                <div class="stage-item stage-active">
                    <span class="stage-icon">{icon}</span>
                    <span>{name}</span>
                    <span class="status-check"><div class="loader-pulse"></div></span>
                </div>
                """
            else:
                stages_html += f"""
                <div class="stage-item stage-pending">
                    <span class="stage-icon">{icon}</span>
                    <span>{name}</span>
                    <span class="status-check">○</span>
                </div>
                """
                
        html_content = f"""
        {loader_css}
        <div class="loading-dashboard fade-in">
            <div class="loading-title">
                <div class="loader-pulse"></div>
                <span>InternHunt AI Engine Processing</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar-fill" style="width: {progress_pct}%;"></div>
            </div>
            <div class="stages-list">
                {stages_html}
            </div>
        </div>
        """
        placeholder.markdown(clean_html(html_content), unsafe_allow_html=True)
        time.sleep(0.6)
        
    placeholder.empty()


def get_table_download_link(df, filename, text):
    """Generate download link for dataframe"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href

def show_pdf(file_path):
    """Display PDF in Streamlit"""
    if not os.path.exists(file_path):
        st.error("PDF file not found.")
        return
    
    try:
        with open(file_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Error displaying PDF: {e}")

def categorize_skills(skills):
    """Categorize skills into specific sections (languages, frontend, backend, libraries, etc.)."""
    categories = {
        "Languages": [],
        "Frontend": [],
        "Backend": [],
        "Libraries / Data-ML": [],
        "Databases": [],
        "Cloud / DevOps": [],
        "Mobile": [],
        "Tools / Platforms": [],
        "Embedded / Hardware": [],
        "Concepts": [],
        "Soft Skills": [],
        "Other": []
    }

    # Normalization aliases
    aliases = {
        'reactjs': 'react', 'nextjs': 'next.js', 'nodejs': 'node.js', 'postgres': 'postgresql',
        'ci cd': 'ci/cd', 'ci-cd': 'ci/cd', 'bs4': 'beautifulsoup', 'huggingface': 'hugging face',
        'redux toolkit': 'redux', 'tailwindcss': 'tailwind', 'postgre': 'postgresql',
        'google colaboratory': 'google colab', 'google-colab': 'google colab', 'visual studio code': 'vs code'
    }

    langs = {
        'python','java','javascript','typescript','go','rust','c','c++','c#','kotlin','swift','ruby','php','r','scala','matlab'
    }
    frontend = {
        'html','html5','css','css3','react','next.js','angular','vue','svelte','redux','tailwind','bootstrap','sass','less','vite','webpack','babel'
    }
    backend = {
        'node.js','express','django','flask','fastapi','spring','spring boot','laravel','rails','graphql','grpc','rest','openapi','swagger'
    }
    libs = {
        'numpy','pandas','scikit-learn','sklearn','matplotlib','seaborn','plotly','tensorflow','keras','pytorch','opencv','xgboost','lightgbm','transformers','hugging face','langchain','yolo','pyspark','spark','nltk','spacy','streamlit'
    }
    dbs = {'sql','mysql','postgresql','sqlite','mongodb','redis','elasticsearch'}
    devops = {'aws','gcp','azure','docker','kubernetes','terraform','git','github','gitlab','github actions','gitlab ci','ci/cd','linux','bash','shell','nginx'}
    mobile = {'android','ios','react native','swiftui','flutter','firebase','supabase'}
    tools = {'postman','selenium','beautifulsoup','power bi','tableau','excel','airflow','hive','hadoop','looker','superset','colab','google colab','vscode','vs code','powerpoint','ms powerpoint','api integration','jupyter'}
    embedded = {'verilog','vhdl','systemverilog','fpga','pcb design','circuit design','embedded systems','arm','arm cortex-m','stm32','esp32','raspberry pi','msp430','pic','arduino'}
    soft = {'communication','leadership','teamwork','collaboration','problem solving','time management','adaptability','critical thinking'}
    concepts = {'data analysis','operating systems','os','networking fundamentals'}

    def norm(s):
        s0 = (s or '').strip()
        if not s0:
            return None
        low = s0.lower()
        low = aliases.get(low, low)
        # unify minor variants
        low = low.replace('react.js','react').replace('next js','next.js').replace('node js','node.js')
        return low, s0  # return original-cased too

    for s in skills:
        res = norm(s)
        if not res:
            continue
        low, orig = res
        if low in langs:
            categories['Languages'].append(orig)
        elif low in frontend:
            categories['Frontend'].append(orig)
        elif low in backend:
            categories['Backend'].append(orig)
        elif low in libs:
            categories['Libraries / Data-ML'].append(orig)
        elif low in dbs:
            categories['Databases'].append(orig)
        elif low in devops:
            categories['Cloud / DevOps'].append(orig)
        elif low in mobile:
            categories['Mobile'].append(orig)
        elif low in tools:
            categories['Tools / Platforms'].append(orig)
        elif low in embedded:
            categories['Embedded / Hardware'].append(orig)
        elif low in soft:
            categories['Soft Skills'].append(orig)
        elif low in concepts:
            categories['Concepts'].append(orig)
        else:
            categories['Other'].append(orig)

    # Drop empty categories and de-duplicate while preserving order
    out = {}
    for k, v in categories.items():
        if not v:
            continue
        seen = set()
        ordered = []
        for item in v:
            if item not in seen:
                seen.add(item)
                ordered.append(item)
        out[k] = ordered
    return out

def display_skills(categorized_skills):
    """Display categorized skills with professional styling"""
    st.markdown(StyleManager.get_skills_styles(), unsafe_allow_html=True)
    
    st.markdown("""
        <div id="skills-section" class="skills-header animate-fade-in">
            <div class="skills-header-icon">🛠️</div>
            <h2 class="skills-header-text">SKILLS EXTRACTED</h2>
        </div>
    """, unsafe_allow_html=True)
    
    category_icons = {
        "Languages": "🧠",
        "Frontend": "🎨",
        "Backend": "🧩",
        "Libraries / Data-ML": "📚",
        "Databases": "🗄️",
        "Cloud / DevOps": "☁️",
        "Mobile": "📱",
        "Tools / Platforms": "🧰",
        "Embedded / Hardware": "🔌",
        "Concepts": "🧩",
        "Soft Skills": "🤝",
        "Other": "🔧"
    }
    
    css_class_map = {
        "Languages": "tech-skill",
        "Frontend": "design-skill",
        "Backend": "tech-skill",
        "Libraries / Data-ML": "data-skill",
        "Databases": "data-skill",
        "Cloud / DevOps": "tech-skill",
        "Mobile": "tech-skill",
        "Tools / Platforms": "business-skill",
        "Embedded / Hardware": "hardware-skill",
        "Concepts": "business-skill",
        "Soft Skills": "soft-skill",
        "Other": "other-skill"
    }
    
    html_output = '<div class="skills-container">'
    
    delay_counter = 0
    for category, skills in categorized_skills.items():
        if skills:
            icon = category_icons.get(category, "✨")
            css_class = css_class_map.get(category, "tech-skill")
            
            html_output += f'''
            <div class="skill-section animate-fade-in animate-delay-{min(delay_counter * 100, 400)}">
                <h3 class="skill-category">
                    <span class="category-icon">{icon}</span> {category}
                </h3>
                <div class="skills-grid">
            '''
            
            for skill in skills:
                html_output += f'<span class="skill-tag {css_class}">{skill}</span>'
            
            html_output += '</div></div>'
            delay_counter += 1
    
    html_output += '</div>'
    st.markdown(html_output, unsafe_allow_html=True)

def _fetch_all_jobs(skills, user_location):
    """Fetch and merge Jooble + scraper jobs into a common schema and deduplicate by URL."""
    jooble_jobs = JobAPIService.fetch_jobs_from_jooble(skills, user_location) or []
    scraped_jobs = scrape_all(skills, user_location) or []

    def map_jooble(j):
        return {
            "title": j.get("title", ""),
            "company": j.get("company", ""),
            "location": j.get("location", "") or "Remote",
            "tags": [],
            "description": j.get("snippet", ""),
            "url": j.get("link", "#"),
            "source": "jooble",
        }

    def map_scraper(j):
        return {
            "title": j.get("title", ""),
            "company": j.get("company", ""),
            "location": j.get("location", "") or "Remote",
            "tags": j.get("tags", []),
            "description": j.get("description", ""),
            "url": j.get("url", "#"),
            "source": j.get("source", "scraper"),
        }

    merged = [map_jooble(j) for j in jooble_jobs] + [map_scraper(j) for j in scraped_jobs]

    # Deduplicate by URL
    seen = set()
    unique = []
    for j in merged:
        u = j.get("url")
        if not u or u in seen:
            continue
        seen.add(u)
        unique.append(j)
    return unique

def _filter_jobs(jobs, query, source):
    """Client-side filter by source and free-text query over multiple fields."""
    q = (query or "").strip().lower()
    s = (source or "All").lower()
    def keep(j):
        js = j.get("source", "").lower()
        if s == "jooble":
            if js != "jooble":
                return False
        elif s == "scrapers":
            # Treat any non-jooble as a scraper
            if js == "jooble":
                return False
        # else: s == all -> no source filter
        if not q:
            return True
        # Prefer matching location first; many scrapers use 'Remote'
        loc = (j.get("location", "") or "").lower()
        if q in loc:
            return True
        # Consider 'remote' a match if user typed something like 'remote'
        if q in ("remote", "wfh", "work from home") and ("remote" in loc or loc == ""):
            return True
        # Otherwise, perform a soft match against title/company/tags/description
        blob = " ".join([
            j.get("title", ""),
            j.get("company", ""),
            " ".join(j.get("tags", [])),
            j.get("description", ""),
        ]).lower()
        return q in blob
    return [j for j in (jobs or []) if keep(j)]

def display_job_recommendations_dual(skills_list, keywords_text: str, location_text: str, predicted_category=None):
    """Display job recommendations: Jooble + Remotive globally, and Internshala for India."""
    from concurrent.futures import ThreadPoolExecutor
    st.markdown(StyleManager.get_job_listing_styles(), unsafe_allow_html=True)
    st.markdown(StyleManager.get_animation_styles(), unsafe_allow_html=True)

    # Build query skills from manual input or resume skills
    manual = (keywords_text or "").strip()
    if manual:
        query_skills = [s.strip() for s in manual.split(",") if s.strip()]
    else:
        query_skills = [s for s in (skills_list or []) if s]

    # Build Internshala query string using category mapping if available
    category_search_terms = {
        "Java Developer": "java developer",
        "Python Developer": "python developer",
        "Data Science": "data analyst",
        "Web Designing": "web design",
        "DevOps Engineer": "devops",
        "HR": "hr",
        "Testing": "software testing",
        "Database": "database",
        "Blockchain": "blockchain",
        "Operations Manager": "operations",
        "SAP Developer": "sap",
        "Mechanical Engineer": "mechanical",
        "Civil Engineer": "civil",
        "Electrical Engineering": "electrical",
        "Network Security Engineer": "cyber security",
    }
    if predicted_category:
        query_str = category_search_terms.get(predicted_category, ", ".join(query_skills[:3]))
    else:
        query_str = ", ".join(query_skills[:4])

    global_loc = location_text or "India"

    # Unique cache key for the query
    cache_key_jobs = f"cached_jobs_{hash(str(query_skills) + '||' + global_loc + '||' + query_str)}"

    if cache_key_jobs not in st.session_state:
        # Fetch all sources concurrently
        with st.spinner("Fetching opportunities..."):
            with ThreadPoolExecutor(max_workers=3) as ex:
                f1 = ex.submit(JobAPIService.fetch_jobs_from_jooble, query_skills[:5], global_loc)
                f2 = ex.submit(scrape_internshala_by_keywords, query_str or "", (location_text or "India"))
                f3 = ex.submit(JobAPIService.fetch_jobs_from_remotive, query_skills[:5], global_loc)
                jooble_jobs = f1.result() or []
                internshala_jobs = f2.result() or []
                remotive_jobs = f3.result() or []

        # Apply ML-based category filtering
        if predicted_category:
            jooble_jobs = filter_jobs_by_category(jooble_jobs, predicted_category)
            remotive_jobs = filter_jobs_by_category(remotive_jobs, predicted_category)
            internshala_jobs = filter_jobs_by_category(internshala_jobs, predicted_category)

        # Internshala fallback
        if not internshala_jobs:
            try:
                internshala_jobs = scrape_internshala(query_skills, location_text) or []
            except Exception:
                internshala_jobs = []
        if not internshala_jobs:
            try:
                internshala_jobs = scrape_internshala([], "India") or []
            except Exception:
                internshala_jobs = []

        # Store in session state cache
        st.session_state[cache_key_jobs] = (jooble_jobs, internshala_jobs, remotive_jobs)
    else:
        # Load from session state cache
        jooble_jobs, internshala_jobs, remotive_jobs = st.session_state[cache_key_jobs]

    # ── Global Section Header ──────────────────────────────────────────────
    st.markdown("""
    <div style="
        display: flex; align-items: center; gap: 14px;
        margin: 2rem 0 1.2rem 0;
        padding-bottom: 14px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    ">
        <div style="
            width: 4px; height: 36px; border-radius: 4px;
            background: linear-gradient(180deg, #6366f1, #8b5cf6);
        "></div>
        <div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #f1f5f9; letter-spacing: -0.3px;">
                Global Opportunities
            </div>
            <div style="font-size: 0.82rem; color: #64748b; margin-top: 2px;">
                Sourced from Jooble &amp; Remotive
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Interleave Jooble + Remotive results
    global_jobs = []
    max_len = max(len(jooble_jobs), len(remotive_jobs))
    for idx in range(max_len):
        if idx < len(jooble_jobs):
            global_jobs.append((jooble_jobs[idx], "jooble"))
        if idx < len(remotive_jobs):
            global_jobs.append((remotive_jobs[idx], "remotive"))
    global_jobs = global_jobs[:12]

    if global_jobs:
        for job, source in global_jobs:
            display_job_card(job, source)
    else:
        st.markdown("""
        <div style="text-align:center; padding: 40px; color: #64748b; font-size: 0.95rem;">
            No global opportunities found. Try adjusting your keywords above.
        </div>
        """, unsafe_allow_html=True)

    # ── Internshala Section Header ─────────────────────────────────────────
    st.markdown("""
    <div style="
        display: flex; align-items: center; gap: 14px;
        margin: 2.5rem 0 1.2rem 0;
        padding-bottom: 14px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    ">
        <div style="
            width: 4px; height: 36px; border-radius: 4px;
            background: linear-gradient(180deg, #10b981, #34d399);
        "></div>
        <div>
            <div style="font-size: 1.25rem; font-weight: 700; color: #f1f5f9; letter-spacing: -0.3px;">
                India Internships
            </div>
            <div style="font-size: 0.82rem; color: #64748b; margin-top: 2px;">
                Live listings from Internshala
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Internshala re-search row
    c_ik, c_il, c_ib = st.columns([3, 2, 1])
    with c_ik:
        intern_kw = st.text_input("Keywords", value=(query_str or ""), placeholder="e.g., Python, React", key="intern_kw_input")
    with c_il:
        intern_loc = st.text_input("Location", value=(location_text or "India"), placeholder="City or India", key="intern_loc_input")
    with c_ib:
        st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
        intern_btn = st.button("Search", key="intern_search_btn", width='stretch')

    if intern_btn:
        with st.spinner("Searching Internshala..."):
            internshala_jobs = scrape_internshala_by_keywords(intern_kw or "", intern_loc or "India") or internshala_jobs
            # Update cache with new results
            st.session_state[cache_key_jobs] = (jooble_jobs, internshala_jobs, remotive_jobs)

    if internshala_jobs:
        for job in internshala_jobs[:10]:
            display_job_card(job, "internshala")
    else:
        st.markdown("""
        <div style="text-align:center; padding: 40px; color: #64748b; font-size: 0.95rem;">
            No internships found. Try different keywords or location.
        </div>
        """, unsafe_allow_html=True)

def display_job_recommendations(skills, location):
    """Legacy API-only recommendations (kept for compatibility)."""
    st.markdown(StyleManager.get_job_listing_styles(), unsafe_allow_html=True)
    st.markdown(StyleManager.get_animation_styles(), unsafe_allow_html=True)
    
    st.markdown("""
        <div class="animated-header" style="
            background-color: #111827;
            padding: 1.2rem;
            border-radius: 8px;
            margin-top: 2rem;
            margin-bottom: 2rem;
        ">
            <h1 style='color: #ffffff; margin: 0;'>💼 Job Recommendations</h1>
        </div>
    """, unsafe_allow_html=True)
    
    # Jooble jobs
    st.markdown("""
        <div class="animated-header" style="
            background-color: #1e1e1e;
            padding: 0.8rem;
            border-left: 6px solid #60a5fa;
            border-radius: 6px;
            margin-top: 2rem;
            margin-bottom: 1rem;
        ">
            <h2 style='color: #ffffff; margin: 0;'>Job Recommendations from Jooble (Global)</h2>
        </div>
    """, unsafe_allow_html=True)
    
    jooble_jobs = JobAPIService.fetch_jobs_from_jooble(skills, location)
    
    if jooble_jobs:
        for i, job in enumerate(jooble_jobs[:10]):
            display_job_card(job, "jooble")
            if i < min(10, len(jooble_jobs)) - 1:
                st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    else:
        st.info("No opportunities found based on your skills.")

    # Internshala API (if configured)
    st.markdown("""
        <div class="animated-header" style="
            background-color: #1e1e1e;
            padding: 0.8rem;
            border-left: 6px solid #34d399;
            border-radius: 6px;
            margin-top: 1.6rem;
            margin-bottom: 0.6rem;
        ">
            <h2 style='color: #ffffff; margin: 0;'>🇮🇳 Internships from Internshala (India)</h2>
        </div>
    """, unsafe_allow_html=True)

    insh_raw = fetch_internshala_internships(", ".join([s for s in (skills or []) if s]), location or "India") or []
    if insh_raw:
        norm = []
        for it in insh_raw[:10]:
            link_path = it.get('link') or ''
            norm.append({
                "title": it.get('title') or it.get('profile') or 'Internship',
                "company": it.get('company') or it.get('company_name') or '',
                "location": it.get('location') or it.get('location_names') or 'India',
                "url": f"https://internshala.com{link_path}" if link_path.startswith('/') else (link_path or '#'),
                "description": it.get('description') or '',
                "source": "internshala",
                "_raw_link_path": link_path,
            })
        for i, job in enumerate(norm):
            display_job_card(job, "internshala")
            if job.get('_raw_link_path'):
                st.markdown(f"[Apply Here](https://internshala.com{job['_raw_link_path']})", unsafe_allow_html=True)
            if i < min(10, len(norm)) - 1:
                st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
    else:
        st.info("No internships found matching your skills.")

def display_job_card(job, source):
    """Display a single job/internship card with a premium glass-morphism design."""
    import random

    # ── Normalise fields by source ─────────────────────────────────────────
    pay = None
    duration = None
    if source == "remotive":
        job_title = job.get("title", "No Title")
        company_name = job.get("company", "Unknown")
        job_location = job.get("location", "Remote")
        job_link = job.get("url") or job.get("link", "#")
        pay = job.get("salary")
        tags_raw = job.get("tags", [])
    elif source == "jooble":
        job_title = job.get("title", "No Title")
        company_name = job.get("company", "Unknown")
        job_location = job.get("location", "Not specified")
        job_link = job.get("link", "#")
        pay = job.get("salary") or job.get("compensation")
        tags_raw = []
    elif source == "internshala":
        job_title = job.get("title", "Internship")
        company_name = job.get("company", "")
        job_location = job.get("location", "India")
        job_link = job.get("url", "#")
        pay = job.get("stipend") or job.get("salary")
        duration = job.get("duration")
        tags_raw = []
    else:
        job_title = job.get("title", "No Title")
        company_name = job.get("company", "Unknown")
        job_location = job.get("location", "Remote")
        job_link = job.get("url", "#")
        pay = job.get("salary")
        tags_raw = []

    # ── Source badge colour ────────────────────────────────────────────────
    source_colours = {
        "jooble": ("#3b82f6", "#1d4ed8", "Jooble"),
        "remotive": ("#8b5cf6", "#6d28d9", "Remotive"),
        "internshala": ("#10b981", "#059669", "Internshala"),
    }
    badge_bg, badge_border, source_label = source_colours.get(
        source, ("#64748b", "#475569", source.capitalize())
    )

    # ── Match score ────────────────────────────────────────────────────────
    skills_list = []
    predicted_cat = None
    if "resume_data" in st.session_state and st.session_state["resume_data"]:
        skills_list = st.session_state["resume_data"].get("skills", [])
        predicted_cat = st.session_state["resume_data"].get("predicted_category")

    desc_val = job.get("description") or ""
    title_lower = job_title.lower()
    desc_lower = desc_val.lower()
    import re as _re_badge
    # Build resume skill matches using word-boundary (min 3 chars, no single-letter noise)
    matched_skills = [
        s.strip() for s in skills_list
        if isinstance(s, str) and len(s.strip()) >= 3 and _re_badge.search(
            r'\b' + _re_badge.escape(s.strip().lower()) + r'\b',
            title_lower + " " + desc_lower
        )
    ][:6]

    if matched_skills:
        match_score = min(65 + len(matched_skills) * 9, 98)
    else:
        random.seed(hash(job_title))
        match_score = random.randint(68, 88)

    # ── Build detail chips ─────────────────────────────────────────────────
    detail_chips = []
    if job_location:
        detail_chips.append(f'<span class="jd-chip jd-chip-loc">&#128205; {job_location}</span>')
    if pay:
        label = "Stipend" if source == "internshala" else "Pay"
        detail_chips.append(f'<span class="jd-chip jd-chip-pay">&#128176; {label}: {pay}</span>')
    if duration:
        detail_chips.append(f'<span class="jd-chip jd-chip-dur">&#128336; {duration}</span>')

    detail_chips_html = " ".join(detail_chips)

    # ── Extract skill/keyword tags from the job itself ────────────────────
    # Curated list of skills/tools commonly found in job postings
    _SKILL_KEYWORDS = [
        # Languages
        "python", "java", "javascript", "typescript", "c++", "c#", "kotlin", "swift",
        "php", "ruby", "golang", "rust", "scala", "r", "matlab",
        # Web
        "react", "angular", "vue", "node.js", "nodejs", "django", "flask", "fastapi",
        "html", "css", "tailwind", "bootstrap", "next.js", "express",
        # Data / AI
        "machine learning", "deep learning", "data science", "data analysis",
        "nlp", "computer vision", "tensorflow", "pytorch", "scikit-learn",
        "pandas", "numpy", "sql", "mysql", "postgresql", "mongodb",
        "tableau", "power bi", "excel",
        # Cloud / DevOps
        "aws", "gcp", "azure", "docker", "kubernetes", "devops", "ci/cd",
        "terraform", "linux", "git", "github",
        # Mobile
        "android", "ios", "flutter", "react native",
        # Design / Other
        "figma", "ui/ux", "photoshop", "illustrator", "canva",
        "seo", "social media", "content writing", "graphic design",
        "video editing", "autocad", "solidworks",
        # Business
        "sales", "marketing", "business development", "hr", "finance",
        "accounting", "operations", "supply chain",
    ]

    job_text = (job_title + " " + (desc_val or "")).lower()
    # Extract keywords present in this specific job
    extracted_job_skills = []
    seen_lower = set()
    for kw in _SKILL_KEYWORDS:
        if _re_badge.search(r'\b' + _re_badge.escape(kw) + r'\b', job_text):
            key = kw.lower()
            if key not in seen_lower:
                seen_lower.add(key)
                extracted_job_skills.append(kw.title() if " " not in kw else kw.title())

    # Also add tags_raw from Remotive (already structured)
    for t in (tags_raw or []):
        key = t.lower()
        if key not in seen_lower and len(t) > 2:
            seen_lower.add(key)
            extracted_job_skills.append(t)

    # Fallback: use predicted category
    if not extracted_job_skills and predicted_cat and predicted_cat != "Not Detected":
        extracted_job_skills = [predicted_cat]

    # ── Build skill badge HTML ─────────────────────────────────────────────
    # Show up to 5 job-extracted skills; highlight those matching resume
    matched_lower = {s.lower() for s in matched_skills}
    skill_badges_html_parts = []
    for skill in extracted_job_skills[:5]:
        is_matched = skill.lower() in matched_lower or any(
            skill.lower() in m.lower() or m.lower() in skill.lower()
            for m in matched_skills
        )
        if is_matched:
            # Highlighted: resume match
            skill_badges_html_parts.append(
                f'<span class="jd-skill-badge jd-skill-match">{skill}</span>'
            )
        else:
            skill_badges_html_parts.append(
                f'<span class="jd-skill-badge">{skill}</span>'
            )
    skill_badges_html = "".join(skill_badges_html_parts)


    # ── Description snippet ────────────────────────────────────────────────
    desc_html = ""
    if desc_val:
        import re as _re
        desc_clean = _re.sub(r'<[^>]*>', '', desc_val)
        desc_clean = _re.sub(r'\s+', ' ', desc_clean).strip()
        if len(desc_clean) > 160:
            desc_clean = desc_clean[:160] + "..."
        if desc_clean:
            desc_html = f'<p class="jd-desc">{desc_clean}</p>'

    card_html = f"""
<style>
.jd-card {{
    background: linear-gradient(135deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 22px 24px;
    margin-bottom: 14px;
    position: relative;
    transition: border-color 0.2s, box-shadow 0.2s;
}}
.jd-card:hover {{
    border-color: rgba(255,255,255,0.13);
    box-shadow: 0 6px 30px rgba(0,0,0,0.35);
}}
.jd-top {{ display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }}
.jd-title {{ font-size: 1.05rem; font-weight: 700; color: #f1f5f9; line-height: 1.35; margin-bottom: 4px; }}
.jd-company {{ font-size: 0.82rem; color: #94a3b8; font-weight: 500; }}
.jd-badges {{ display: flex; gap: 6px; align-items: center; flex-shrink: 0; }}
.jd-score {{
    font-size: 0.72rem; font-weight: 700; padding: 3px 9px; border-radius: 999px;
    background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.25); color: #34d399;
}}
.jd-source {{
    font-size: 0.72rem; font-weight: 600; padding: 3px 9px; border-radius: 999px;
    background: rgba({badge_bg[1:]}, 0.12);
    border: 1px solid {badge_border};
    color: {badge_bg};
}}
.jd-details {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 14px; }}
.jd-chip {{
    font-size: 0.78rem; padding: 4px 10px; border-radius: 6px;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.07); color: #cbd5e1;
}}
.jd-chip-pay {{ color: #fbbf24; border-color: rgba(251,191,36,0.2); background: rgba(251,191,36,0.06); }}
.jd-chip-dur {{ color: #a78bfa; border-color: rgba(167,139,250,0.2); background: rgba(167,139,250,0.06); }}
.jd-desc {{ font-size: 0.82rem; color: #64748b; margin-top: 12px; line-height: 1.55; font-style: italic; }}
.jd-footer {{ display: flex; justify-content: space-between; align-items: center; margin-top: 16px; flex-wrap: wrap; gap: 10px; }}
.jd-skill-badge {{
    font-size: 0.72rem; padding: 3px 8px; border-radius: 5px;
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); color: #94a3b8;
    font-weight: 600;
}}
.jd-skill-match {{
    background: rgba(99,102,241,0.12); border: 1px solid rgba(99,102,241,0.3); color: #818cf8;
}}

.jd-apply {{
    display: inline-flex; align-items: center; gap: 6px;
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: #fff; padding: 8px 20px; border-radius: 8px;
    font-size: 0.82rem; font-weight: 700; text-decoration: none;
    transition: opacity 0.2s;
}}
.jd-apply:hover {{ opacity: 0.85; color: #fff; }}
</style>
<div class="jd-card">
    <div class="jd-top">
        <div>
            <div class="jd-title">{job_title}</div>
            <div class="jd-company">{company_name}</div>
        </div>
        <div class="jd-badges">
            <span class="jd-score">{match_score}% Match</span>
            <span class="jd-source">{source_label}</span>
        </div>
    </div>
    <div class="jd-details">{detail_chips_html}</div>
    {desc_html}
    <div class="jd-footer">
        <div style="display:flex;gap:6px;flex-wrap:wrap;">{skill_badges_html}</div>
        <a class="jd-apply" href="{job_link}" target="_blank">Apply Now &#8599;</a>
    </div>
</div>
"""
    st.markdown(clean_html(card_html), unsafe_allow_html=True)

def course_recommender(course_list):
    """Display course recommendations - Catalog-style cards with a premium glass-morphism design."""
    # Apply modern global/card styles
    st.markdown(StyleManager.get_course_card_styles(), unsafe_allow_html=True)

    # Header (left-aligned, premium accent bar, no emojis)
    st.markdown("""
    <div id="courses-section" style="
        display: flex; align-items: center; gap: 14px;
        margin: 1.5rem 0 1.5rem 0;
        padding-bottom: 14px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    ">
        <div style="
            width: 4px; height: 40px; border-radius: 4px;
            background: linear-gradient(180deg, #6366f1, #a78bfa);
        "></div>
        <div>
            <div style="font-size: 1.35rem; font-weight: 700; color: #f1f5f9; letter-spacing: -0.4px;">
                Recommended Courses
            </div>
            <div style="font-size: 0.82rem; color: #64748b; margin-top: 2px;">
                Tailored learning paths to strengthen your profile and career growth
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not course_list:
        st.markdown("""
        <div style="text-align:center; padding: 40px; color: #64748b; font-size: 0.95rem;">
            No course recommendations available at the moment.
        </div>
        """, unsafe_allow_html=True)
        return []

    # Place the selectbox in a neat half-width column instead of stretching full screen
    col_sel, _ = st.columns([2, 3])
    with col_sel:
        no_of_reco = st.selectbox(
            "Recommendations limit:",
            options=[2, 4, 6, 8, 10],
            index=2,
            key="courses_selectbox"
        )

    recommended_courses = random.sample(course_list, min(no_of_reco, len(course_list)))

    # Helper to render a single card
    def _render_course_card(title: str, link: str, idx: int):
        l = (link or '').lower()
        provider_class = "provider-generic"
        if 'udemy' in l:
            provider = 'Udemy'
            provider_class = "provider-udemy"
        elif 'coursera' in l:
            provider = 'Coursera'
            provider_class = "provider-coursera"
        elif 'linkedin' in l:
            provider = 'LinkedIn Learning'
            provider_class = "provider-linkedin"
        elif 'edx' in l:
            provider = 'edX'
            provider_class = "provider-edx"
        else:
            provider = 'Online'

        badges = []
        if idx == 0:
            badges.append('Top Match')
        if any(k in title.lower() for k in ['beginner', 'introduction', 'fundamentals']):
            badges.append('Beginner Friendly')
        if any(k in title.lower() for k in ['advanced', 'deep dive']):
            badges.append('Trending')

        # Simple summary fallback
        summary = ''
        if any(k in title.lower() for k in ['python','react','data','ml','ai','sql','django','flask','devops','cloud']):
            summary = f"Build practical skills in {title.split()[0]} with hands-on exercises."
        else:
            summary = "Enhance your skills with this curated learning pathway and interactive labs."

        badge_spans = ''.join([f"<span class='course-tag'>{b}</span>" for b in badges])
        summary_html = f"<div class='course-desc-text'>{summary}</div>"

        card_html = f"""
<style>
/* Equal heights setup */
[data-testid="column"] > div {{
    height: 100%;
}}
.course-card-premium {{
    background: linear-gradient(135deg, rgba(255,255,255,0.03) 0%, rgba(255,255,255,0.01) 100%);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    height: 100%;
    min-height: 240px;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}}
.course-card-premium:hover {{
    border-color: rgba(99, 102, 241, 0.25);
    box-shadow: 0 12px 30px rgba(0, 0, 0, 0.4);
    transform: translateY(-2px);
    background: linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.01) 100%);
}}
.course-card-meta {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 14px;
    gap: 8px;
}}
.course-provider-badge {{
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 3px 8px;
    border-radius: 4px;
    background: rgba(255, 255, 255, 0.05);
    color: #94a3b8;
    border: 1px solid rgba(255, 255, 255, 0.07);
}}
.provider-udemy {{
    background: rgba(168, 85, 247, 0.1);
    color: #c084fc;
    border-color: rgba(168, 85, 247, 0.2);
}}
.provider-coursera {{
    background: rgba(59, 130, 246, 0.1);
    color: #60a5fa;
    border-color: rgba(59, 130, 246, 0.2);
}}
.provider-linkedin {{
    background: rgba(14, 165, 233, 0.1);
    color: #38bdf8;
    border-color: rgba(14, 165, 233, 0.2);
}}
.provider-edx {{
    background: rgba(34, 197, 94, 0.1);
    color: #4ade80;
    border-color: rgba(34, 197, 94, 0.2);
}}
.course-tag {{
    font-size: 0.68rem;
    font-weight: 600;
    padding: 3px 8px;
    border-radius: 999px;
    background: rgba(99, 102, 241, 0.12);
    border: 1px solid rgba(99, 102, 241, 0.25);
    color: #818cf8;
}}
.course-title-text {{
    font-size: 1.05rem;
    font-weight: 700;
    color: #f8fafc;
    line-height: 1.4;
    margin-bottom: 8px;
}}
.course-desc-text {{
    font-size: 0.82rem;
    color: #94a3b8;
    line-height: 1.55;
    margin-bottom: 16px;
    flex-grow: 1;
}}
.course-btn-premium {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white !important;
    padding: 8px 18px;
    border-radius: 6px;
    font-size: 0.82rem;
    font-weight: 700;
    text-decoration: none;
    transition: opacity 0.2s, transform 0.2s;
    width: fit-content;
}}
.course-btn-premium:hover {{
    opacity: 0.9;
    transform: translateX(2px);
}}
</style>
<div class="course-card-premium">
    <div>
        <div class="course-card-meta">
            <span class="course-provider-badge {provider_class}">{provider}</span>
            <div style="display: flex; gap: 4px; flex-wrap: wrap;">{badge_spans}</div>
        </div>
        <div class="course-title-text">{title}</div>
        {summary_html}
    </div>
    <div style="display: flex; margin-top: auto;">
        <a class="course-btn-premium" href="{link}" target="_blank">Explore Course &rarr;</a>
    </div>
</div>
"""
        st.markdown(clean_html(card_html), unsafe_allow_html=True)

    # Layout: two columns if more than 4
    if len(recommended_courses) > 4:
        cols = st.columns(2)
        for i, (c_name, c_link) in enumerate(recommended_courses):
            with cols[i % 2]:
                _render_course_card(c_name, c_link, i)
    else:
        for i, (c_name, c_link) in enumerate(recommended_courses):
            _render_course_card(c_name, c_link, i)

    return [c_name for c_name, _ in recommended_courses]

def main():
    """Main application function"""
    # Initialize the application
    initialize_app()
    
    # Apply global styles from StyleManager
    StyleManager.apply_global_styles()
    StyleManager.apply_theme_styles("dark")
    

    # Modern Professional Dark Theme with Inter/Poppins
    st.markdown(f"""
    <style>
        /* ============ GLOBAL FONTS ============ */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Poppins:wght@300;400;500;600;700;800&display=swap');
        
        /* ============ CSS COLOR VARIABLES ============ */
        :root {{
            /* Primary Colors */
            --primary: #7c3aed;
            --secondary: #2dd4bf;
            --primary-light: #8b5cf6;
            --primary-dark: #6d28d9;
            
            /* Text Colors */
            --text-main: #e2e8f0;
            --text-bright: #f8fafc;
            --text-muted: #94a3b8;
            --text-dim: #64748b;
            
            /* Background Colors */
            --bg-dark: #0d1228;
            --bg-darker: #0a0f1f;
            --bg-card: rgba(15, 23, 42, 0.6);
            --bg-glass: rgba(15, 23, 42, 0.4);
            
            /* Accent & State Colors */
            --accent-purple: #7f5af0;
            --accent-teal: #2cb67d;
            --accent-blue: #38bdf8;
            --success: #46E1A1;
            
            /* Borders & Shadows */
            --border-color: rgba(255, 255, 255, 0.08);
            --border-light: rgba(255, 255, 255, 0.1);
            --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);
        }}
        
        /* ============ GLOBAL BODY & APP BACKGROUND ============ */
        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
            background: radial-gradient(circle at top, var(--bg-dark), var(--bg-darker) 80%) !important;
            color: var(--text-main) !important;
            margin: 0;
            padding: 0;
        }}
        
        .stApp {{
            background: transparent !important;
        }}
        
        /* ============ TYPOGRAPHY ============ */
        h1, h2, h3, h4, h5, h6 {{
            font-family: 'Poppins', sans-serif !important;
            font-weight: 700 !important;
            color: var(--text-main) !important;
            letter-spacing: -0.02em;
        }}
        
        h1 {{ font-size: 2.5rem !important; }}
        h2 {{ font-size: 2rem !important; }}
        h3 {{ font-size: 1.5rem !important; }}
        
        p, label {{
            font-family: 'Inter', sans-serif !important;
            color: var(--text-main) !important;
        }}
        
        /* ============ STREAMLIT COMPONENTS ============ */
        
        /* Buttons */
        .stButton>button {{
            background: linear-gradient(135deg, var(--primary), var(--secondary)) !important;
            border-radius: 8px !important;
            padding: 0.6rem 1.4rem !important;
            font-weight: 600 !important;
            font-family: 'Inter', sans-serif !important;
            color: white !important;
            border: none !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 12px rgba(124, 58, 237, 0.3) !important;
        }}
        
        .stButton>button:hover {{
            transform: scale(1.05) !important;
            box-shadow: 0 0 20px rgba(124, 58, 237, 0.5) !important;
        }}
        
        /* Input Fields */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea,
        .stSelectbox>div>div>div {{
            background: var(--bg-glass) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid var(--border-light) !important;
            border-radius: 8px !important;
            color: var(--text-main) !important;
            padding: 0.6rem 1rem !important;
            font-family: 'Inter', sans-serif !important;
        }}
        
        .stTextInput>div>div>input:focus,
        .stTextArea>div>div>textarea:focus {{
            border-color: var(--primary) !important;
            box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.2) !important;
        }}
        
        /* Cards & Containers */
        .element-container, .stMarkdown {{
            margin: 0.5rem 0 !important;
        }}
        
        /* Glass effect panels */
        [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlock"] {{
            background: var(--glass-bg);
            backdrop-filter: blur(12px);
            border: 1px solid var(--glass-border);
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
        }}
        
        /* ============ SIDEBAR DASHBOARD PANEL ============ */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #0e132a 0%, #0a0d1b 100%) !important;
            border-right: 1px solid rgba(255,255,255,0.05) !important;
            padding: 1.5rem 1rem !important;
        }}
        
        [data-testid="stSidebar"] * {{
            color: var(--text-main) !important;
        }}
        
        /* Sidebar headers with icons */
        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3 {{
            font-family: 'Poppins', sans-serif !important;
            font-weight: 600 !important;
            font-size: 1.1rem !important;
            color: var(--text-main) !important;
            margin-bottom: 1rem !important;
            padding-bottom: 0.5rem !important;
            border-bottom: 1px solid var(--border-color);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        /* Sidebar selectbox - glassy effect */
        [data-testid="stSidebar"] .stSelectbox {{
            margin-bottom: 1.5rem;
        }}
        
        [data-testid="stSidebar"] .stSelectbox label {{
            font-weight: 500 !important;
            font-size: 0.9rem !important;
            margin-bottom: 0.5rem !important;
            color: var(--text-muted) !important;
        }}
        
        [data-testid="stSidebar"] .stSelectbox > div > div {{
            background: rgba(255, 255, 255, 0.04) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid rgba(255, 255, 255, 0.08) !important;
            border-radius: 8px !important;
            padding: 8px 12px !important;
            font-size: 0.95rem !important;
            transition: all 0.3s ease !important;
        }}
        
        [data-testid="stSidebar"] .stSelectbox > div > div:hover {{
            background: rgba(255, 255, 255, 0.08) !important;
            border-color: rgba(45, 212, 191, 0.4) !important;
            transform: translateY(-1px);
        }}
        
        [data-testid="stSidebar"] .stSelectbox > div > div > div {{
            color: var(--text-main) !important;
        }}
        
        /* Sidebar dividers */
        [data-testid="stSidebar"] hr {{
            border: none;
            height: 1px;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
            margin: 1.5rem 0;
        }}
        
        /* Sidebar links and text */
        [data-testid="stSidebar"] p {{
            font-size: 0.85rem;
            line-height: 1.6;
            color: var(--text-muted) !important;
        }}
        
        [data-testid="stSidebar"] a {{
            color: #94a3b8 !important;
            font-size: 0.95rem;
            text-decoration: none;
            transition: color 0.3s ease, transform 0.2s ease;
            display: inline-block;
        }}
        
        [data-testid="stSidebar"] a:hover {{
            color: #2dd4bf !important;
            transform: translateX(2px);
        }}
        
        /* Active menu item styling */
        [data-testid="stSidebar"] .active-item,
        [data-testid="stSidebar"] [data-selected="true"] {{
            background: rgba(99,102,241,0.15) !important;
            border-left: 3px solid #7c3aed !important;
            border-radius: 8px;
            padding-left: 0.75rem !important;
        }}
        
        /* Sidebar buttons */
        [data-testid="stSidebar"] .stButton > button {{
            width: 100%;
            background: linear-gradient(135deg, rgba(124, 58, 237, 0.15), rgba(45, 212, 191, 0.15)) !important;
            border: 1px solid rgba(124, 58, 237, 0.3) !important;
            color: var(--text-main) !important;
            font-weight: 600 !important;
            padding: 0.75rem 1rem !important;
            border-radius: 8px !important;
            margin-bottom: 0.75rem;
        }}
        
        [data-testid="stSidebar"] .stButton > button:hover {{
            background: linear-gradient(135deg, rgba(124, 58, 237, 0.25), rgba(45, 212, 191, 0.25)) !important;
            border-color: rgba(124, 58, 237, 0.5) !important;
            transform: translateY(-1px);
        }}
        
        /* Sidebar scrollbar */
        [data-testid="stSidebar"] ::-webkit-scrollbar {{
            width: 6px;
        }}
        
        [data-testid="stSidebar"] ::-webkit-scrollbar-track {{
            background: rgba(255, 255, 255, 0.03);
        }}
        
        [data-testid="stSidebar"] ::-webkit-scrollbar-thumb {{
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            border-radius: 3px;
        }}
        
        /* Selectbox */
        .stSelectbox>div>div>div>div>div>div {{
            color: var(--text-primary) !important;
            background-color: var(--bg-secondary) !important;
        }}
        
        /* File Uploader */
        [data-testid="stFileUploader"] {{
            background: var(--glass-bg) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 12px !important;
            padding: 1rem !important;
        }}
        
        [data-testid="stFileUploader"]>div>div>div>div>div>div {{
            color: var(--text-primary) !important;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
            background: transparent;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 8px;
            padding: 0.5rem 1rem;
            color: var(--text-secondary) !important;
            font-weight: 600;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(45, 212, 191, 0.2));
            color: var(--text-primary) !important;
            border-color: var(--accent-primary);
        }}
        
        /* Expander */
        .streamlit-expanderHeader {{
            background: var(--glass-bg) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 8px !important;
            color: var(--text-primary) !important;
            font-weight: 600 !important;
        }}
        
        /* Alerts */
        .stAlert {{
            background: var(--glass-bg) !important;
            backdrop-filter: blur(10px) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 8px !important;
            color: var(--text-primary) !important;
        }}
        
        /* Spinner */
        .stSpinner>div {{
            border-top-color: var(--accent-primary) !important;
        }}
        
        /* DataFrames & Tables */
        .dataframe {{
            background: var(--glass-bg) !important;
            border: 1px solid var(--glass-border) !important;
            border-radius: 8px !important;
            color: var(--text-primary) !important;
        }}
        
        /* Links */
        a {{
            color: #60a5fa !important;
            text-decoration: none;
        }}
        
        a:hover {{
            color: #93c5fd !important;
            text-decoration: underline;
        }}
        
        /* Scrollbar */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}
        
        ::-webkit-scrollbar-track {{
            background: var(--bg-primary);
        }}
        
        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(135deg, #7c3aed, #2dd4bf);
            border-radius: 4px;
        }}
        
        ::-webkit-scrollbar-thumb:hover {{
            background: linear-gradient(135deg, #6d28d9, #14b8a6);
        }}
        
        /* Reduce excessive padding */
        .block-container {{
            padding-top: 6rem !important;
            padding-bottom: 2rem !important;
            max-width: 1100px;
            padding-left: 1.25rem !important;
            padding-right: 1.25rem !important;
        }}
        
        /* Consistent margins */
        .element-container {{
            margin-bottom: 0.75rem !important;
        }}
        
        /* ============ SECTION DIVIDERS ============ */
        /* Section title spacing */
        h2, h3 {{ margin-top: 36px !important; }}
        .courses-title, .search-title, .section-title, .dashboard-title, .sugg-title, .role-title, .skills-header-text {{ margin-top: 36px !important; }}
        .section-divider {{
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, rgba(255,255,255,0.1), transparent);
            margin: 60px 0;
        }}
        
        .section-divider-sm {{
            border: none;
            height: 1px;
            background: linear-gradient(to right, transparent, rgba(255,255,255,0.08), transparent);
            margin: 40px 0;
        }}
        
        .section-divider-lg {{
            border: none;
            height: 2px;
            background: linear-gradient(to right, transparent, rgba(124, 58, 237, 0.2), rgba(45, 212, 191, 0.2), transparent);
            margin: 80px 0;
        }}
    </style>
    """, unsafe_allow_html=True)
    
    # Legacy dark theme overrides
    st.markdown("""
    <style>
        /* Ensure dark theme is applied to all elements */
        body {
            color: #F8FAFC !important;
            background-color: #0D1429 !important;
        }
        
        /* Ensure text color is consistent */
        .stApp, .stText, .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, 
        .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6, 
        .stMarkdown li, .stMarkdown ol, .stMarkdown ul, .stMarkdown table,
        .stAlert, .stAlert p, .stAlert h1, .stAlert h2, .stAlert h3, .stAlert h4,
        .stAlert h5, .stAlert h6, .stAlert li, .stAlert ol, .stAlert ul, .stAlert table {
            color: #F8FAFC !important;
        }
        
        /* Style file uploader specifically */
        .stFileUploader > div > div > div > div > div > div {
            color: #F8FAFC !important;
        }
        
        /* Style select boxes */
        .stSelectbox > div > div > div > div > div > div {
            color: #F8FAFC !important;
        }
        
        /* Style input fields */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            color: #F8FAFC !important;
            background-color: #1E293B !important;
        }
    </style>
    """, unsafe_allow_html=True)

    # Main application
    if st.session_state.page == "analyzer":
        # Navigation Bar
        st.markdown("""
            <style>
            .nav-bar {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 15px 30px;
                border-radius: 12px;
                margin-bottom: 30px;
                display: flex;
                justify-content: space-between;
                align-items: center;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }
            .nav-logo {
                font-size: 1.5rem;
                font-weight: 800;
                color: white;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .nav-links {
                display: flex;
            }
            </style>
        """, unsafe_allow_html=True)
        
        display_header()
        # Minimal space after Hero Section (Reduces empty whitespace to bring upload section closer)
        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
        
        # Sidebar with icons
        st.markdown("""
        <style>
        .sidebar-header {
            font-family: 'Inter', sans-serif;
            font-size: 1rem;
            font-weight: 600;
            color: #8b5cf6;
            margin: 20px 0 10px;
            text-align: center;
            text-transform: uppercase;
            letter-spacing: 1px;
            text-shadow: 0 0 8px rgba(139,92,246,0.5);
        }
        
        [data-baseweb="select"] {
            background-color: rgba(255,255,255,0.05) !important;
            border-radius: 10px !important;
            border: 1px solid rgba(255,255,255,0.15) !important;
            color: #fff !important;
            transition: all 0.3s ease !important;
            margin: 10px 0 !important;
            width: 100% !important;
        }
        
        [data-baseweb="select"] * {
            color: #fff !important;
        }
        
        [data-baseweb="select"]:hover {
            border-color: #8b5cf6 !important;
            box-shadow: 0 0 12px rgba(139,92,246,0.3) !important;
        }
        
        [data-baseweb="select"] [aria-selected="true"] {
            background-color: rgba(139,92,246,0.2) !important;
        }
        
        [data-baseweb="select"] [role="option"]:hover {
            background-color: rgba(139,92,246,0.3) !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.sidebar.markdown("<div class='sidebar-header'>InternHunt Panel</div>", unsafe_allow_html=True)
        activities = ["User", "Admin"]
        choice = st.sidebar.selectbox("Select Mode", activities)
        
        # Navigation panel for User mode
        if choice == 'User':
            if st.session_state.get('resume_data') is not None:
                nav_html_content = """
                <!DOCTYPE html>
                <html>
                <head>
                <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
                body {
                    background-color: transparent;
                    margin: 0;
                    padding: 0;
                    overflow: hidden;
                    font-family: 'Inter', sans-serif;
                }
                .sidebar-nav {
                    display: flex;
                    flex-direction: column;
                    gap: 6px;
                    width: 100%;
                }
                .sidebar-nav .nav-title {
                    font-size: 11px;
                    font-weight: 700;
                    color: #64748b;
                    text-transform: uppercase;
                    letter-spacing: 0.08em;
                    margin-bottom: 8px;
                    padding-left: 8px;
                }
                .sidebar-nav .nav-item {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    padding: 10px 14px;
                    border-radius: 10px;
                    color: #94a3b8;
                    text-decoration: none;
                    font-size: 13px;
                    font-weight: 600;
                    transition: all 0.25s ease;
                    border: 1px solid transparent;
                    cursor: pointer;
                    user-select: none;
                }
                .sidebar-nav .nav-item:hover {
                    color: #f8fafc;
                    background: rgba(255, 255, 255, 0.04);
                    border-color: rgba(255, 255, 255, 0.06);
                }
                .sidebar-nav .nav-item.active {
                    color: #fff;
                    background: linear-gradient(135deg, rgba(99, 102, 241, 0.2), rgba(139, 92, 246, 0.2));
                    border-color: rgba(99, 102, 241, 0.4);
                    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
                    text-shadow: 0 0 8px rgba(255, 255, 255, 0.2);
                }
                </style>
                </head>
                <body>
                <div class="sidebar-nav">
                    <div class="nav-title">Dashboard Navigation</div>
                    <div class="nav-item active" id="nav-profile" onclick="navTo('profile-section','nav-profile')">Profile Overview</div>
                    <div class="nav-item" id="nav-skills" onclick="navTo('skills-section','nav-skills')">Skills Analysis</div>
                    <div class="nav-item" id="nav-ai-profile" onclick="navTo('ai-profile-section','nav-ai-profile')">AI-Detected Profile</div>
                    <div class="nav-item" id="nav-ats" onclick="navTo('ats-dashboard-section','nav-ats')">ATS Performance</div>
                    <div class="nav-item" id="nav-suggestions" onclick="navTo('suggestions-section','nav-suggestions')">Top Suggestions</div>
                    <div class="nav-item" id="nav-opportunities" onclick="navTo('opportunities-section','nav-opportunities')">Opportunities</div>
                    <div class="nav-item" id="nav-courses" onclick="navTo('courses-section','nav-courses')">Recommended Courses</div>
                    <div class="nav-item" id="nav-chat" onclick="navTo('chat-section','nav-chat')">AI Assistant</div>
                </div>

                <script>
                var _navSections=[{id:'profile-section',navId:'nav-profile'},{id:'skills-section',navId:'nav-skills'},{id:'ai-profile-section',navId:'nav-ai-profile'},{id:'ats-dashboard-section',navId:'nav-ats'},{id:'suggestions-section',navId:'nav-suggestions'},{id:'opportunities-section',navId:'nav-opportunities'},{id:'courses-section',navId:'nav-courses'},{id:'chat-section',navId:'nav-chat'}];

                function _sact(sid){
                    _navSections.forEach(function(s){
                        var e=document.getElementById(s.navId);
                        if(e) e.classList.toggle('active',s.id===sid);
                    });
                }

                window.navTo=function(sectionId,navId){
                    _sact(sectionId);
                    var md = window.parent.document;
                    var mc = md.querySelector('.stMain') || md.querySelector('.main') || md.querySelector('[data-testid=\\'stAppViewContainer\\']') || md.documentElement;
                    var t = md.getElementById(sectionId);
                    console.log("navTo: sectionId =", sectionId, "target =", t, "container =", mc);
                    if (!t) {
                        console.warn("navTo: Target element NOT found!");
                        return;
                    }
                    
                    var cr = mc.getBoundingClientRect();
                    var tr = t.getBoundingClientRect();
                    var currentScroll = window.parent.pageYOffset || window.parent.scrollY || mc.scrollTop || 0;
                    var targetScrollTop = tr.top - cr.top + currentScroll;
                    var finalScroll = targetScrollTop - 100;
                    
                    console.log("navTo: tr.top =", tr.top, "cr.top =", cr.top, "currentScroll =", currentScroll, "finalScroll =", finalScroll);
                    
                    mc.scrollTo({top: finalScroll, behavior: 'smooth'});
                    if (window.parent && window.parent.scrollTo) {
                        window.parent.scrollTo({top: finalScroll, behavior: 'smooth'});
                    }
                };

                function _initScrollSpy() {
                    var md = window.parent.document;
                    var mc = md.querySelector('.stMain') || md.querySelector('.main') || md.querySelector('[data-testid=\\'stAppViewContainer\\']');
                    if (mc && !mc._sspy) {
                        mc._sspy = true;
                        mc.addEventListener('scroll', function() {
                            var th = (window.parent.innerHeight || 800) * 0.35;
                            var activeId = '';
                            for (var i = 0; i < _navSections.length; i++) {
                                var e = md.getElementById(_navSections[i].id);
                                if (e && e.getBoundingClientRect().top <= th) {
                                    activeId = _navSections[i].id;
                                }
                            }
                            if (activeId) {
                                _sact(activeId);
                            }
                        }, {passive: true});
                    }
                }

                setTimeout(_initScrollSpy, 500);
                setInterval(_initScrollSpy, 1500);
                </script>
                </body>
                </html>
                """
                with st.sidebar:
                    st.iframe(nav_html_content, height=420)

            else:
                st.sidebar.markdown(clean_html("""
                <div class="sidebar-nav" style="opacity: 0.5;">
                    <div class="nav-title">Dashboard Navigation</div>
                    <div class="nav-item" style="cursor: not-allowed; opacity: 0.6;">Profile Overview</div>
                    <div class="nav-item" style="cursor: not-allowed; opacity: 0.6;">Skills Analysis</div>
                    <div class="nav-item" style="cursor: not-allowed; opacity: 0.6;">AI-Detected Profile</div>
                    <div class="nav-item" style="cursor: not-allowed; opacity: 0.6;">ATS Performance</div>
                    <div class="nav-item" style="cursor: not-allowed; opacity: 0.6;">Top Suggestions</div>
                    <div class="nav-item" style="cursor: not-allowed; opacity: 0.6;">Opportunities</div>
                    <div class="nav-item" style="cursor: not-allowed; opacity: 0.6;">Recommended Courses</div>
                    <div class="nav-item" style="cursor: not-allowed; opacity: 0.6;">AI Assistant</div>
                </div>
                <div style="font-size: 11px; color: #64748b; padding: 10px 8px; text-align: center; font-style: italic;">
                    Upload a resume to unlock navigation
                </div>
                """), unsafe_allow_html=True)

        st.sidebar.markdown("""
        <style>
        .sidebar-footer {
            text-align: center;
            color: rgba(255,255,255,0.4);
            font-size: 0.8rem;
            margin-top: 30px;
            border-top: 1px solid rgba(255,255,255,0.1);
            padding-top: 12px;
            font-family: 'Inter', sans-serif;
        }
        .sidebar-footer a {
            color: #2dd4bf;
            text-decoration: none;
            font-weight: 500;
            transition: color 0.2s ease;
        }
        .sidebar-footer a:hover {
            color: #8b5cf6;
            text-decoration: none;
        }
        </style>
        <div class='sidebar-footer'>
            © 2025 InternHunt <br>
            Crafted with ❤️ by Students
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.get('admin_authenticated'):
            if st.sidebar.button("🔒 Lock Admin Portal", width="stretch"):
                st.session_state.admin_authenticated = False
                st.rerun()
        
        if choice == 'User':
            # Modern upload section styling
            st.markdown("""
                <style>
                /* ============ UPLOAD SECTION STYLING ============ */
                :root { 
                    --radius: 16px; 
                    --card-bg: rgba(255, 255, 255, 0.02); 
                    --muted: #94a3b8; 
                    --text: #e2e8f0; 
                    --text-bright: #f8fafc;
                }
                
                /* ============ UNIFIED ANIMATIONS ============ */
                /* Fade-in animation with cubic-bezier easing */
                .fade-in { 
                    animation: fadeIn 1s cubic-bezier(0.4, 0, 0.2, 1) both; 
                }
                
                @keyframes fadeIn { 
                    from {{ opacity: 0; transform: translateY(30px); }} 
                    to {{ opacity: 1; transform: translateY(0); }} 
                }}
                
                /* Modern upload card container with elevation */
                .upload-section,
                .card {{ 
                    background: rgba(255, 255, 255, 0.03);
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    backdrop-filter: blur(12px);
                    border-radius: 20px;
                    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
                    padding: 24px;
                    transition: all 0.3s ease-in-out;
                    position: relative;
                }}
                
                .upload-card {{ 
                    padding: 1.75rem; 
                    margin: 1rem 0 1.5rem; 
                    position: relative;
                }}
                
                .upload-card::before {{
                    content: "";
                    position: absolute;
                    inset: -2px;
                    border-radius: 20px;
                    background: linear-gradient(135deg, rgba(124, 58, 237, 0.15), rgba(45, 212, 191, 0.15));
                    opacity: 0;
                    z-index: -1;
                    transition: opacity 0.3s ease;
                }}
                
                .upload-card:hover {{
                    border-color: rgba(124, 58, 237, 0.3);
                    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.35), 0 0 30px rgba(124, 58, 237, 0.15);
                    transform: translateY(-4px);
                }}
                
                .upload-card:hover::before {{
                    opacity: 1;
                }}
                
                /* Upload card title with better contrast */
                .upload-card .title { 
                    font-size: 1.5rem; 
                    font-weight: 800; 
                    color: var(--text-bright); 
                    margin: 0 0 0.5rem; 
                    letter-spacing: -0.02em;
                    font-family: 'Poppins', sans-serif;
                }
                
                /* Subtitle with better readability */
                .upload-card .subtitle { 
                    color: var(--muted); 
                    font-size: 0.95rem; 
                    margin: 0 0 1rem; 
                    line-height: 1.6;
                }
                
                /* Soft divider */
                .soft-divider { 
                    height: 1px; 
                    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent); 
                    margin: 1.25rem 0; 
                    border: none; 
                }
                
                /* File uploader styling */
                [data-testid="stFileUploader"] { 
                    background: transparent; 
                    text-align: center;
                }
                
                [data-testid="stFileUploader"] div[data-testid="stFileUploaderDropzone"] {{
                    background: rgba(255, 255, 255, 0.03);
                    border: 2px dashed rgba(124, 58, 237, 0.3);
                    border-radius: 12px;
                    padding: 2rem 1rem;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                    min-height: 140px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                }}
                
                [data-testid="stFileUploader"] div[data-testid="stFileUploaderDropzone"]:hover {{
                    background: rgba(124, 58, 237, 0.05);
                    border-color: rgba(124, 58, 237, 0.5);
                    box-shadow: 0 0 20px rgba(124, 58, 237, 0.1);
                }}
                
                /* Upload button */
                [data-testid="stFileUploader"] button {{ 
                    background: linear-gradient(135deg, #7c3aed, #2dd4bf) !important;
                    border: 0 !important;
                    color: white !important;
                    font-weight: 700 !important;
                    font-size: 0.95rem !important;
                    border-radius: 10px !important;
                    padding: 10px 20px !important;
                    box-shadow: 0 6px 20px rgba(124, 58, 237, 0.3) !important;
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
                }}
                
                [data-testid="stFileUploader"] button:hover {{ 
                    filter: brightness(1.1) !important;
                    transform: translateY(-2px) !important;
                    box-shadow: 0 8px 25px rgba(124, 58, 237, 0.4) !important;
                }}
                
                /* File pill badge */
                .file-pill { 
                    display: flex; 
                    align-items: center; 
                    gap: 0.75rem; 
                    padding: 0.75rem 1rem; 
                    border-radius: 12px; 
                }
                </style>
            """, unsafe_allow_html=True)

            st.markdown("""
            <style>
            /* ── Entrance animation ── */
            @keyframes fadeUpUpload {
                from { opacity:0; transform:translateY(14px); }
                to   { opacity:1; transform:translateY(0); }
            }

            .upload-section-wrap {
                animation: fadeUpUpload 0.45s ease both;
                display: flex;
                flex-direction: column;
                gap: 16px;
            }

            /* ── Layer 1: Resume Analysis Card ── */
            .upload-intro-card {
                background: linear-gradient(135deg, rgba(99,102,241,0.05) 0%, rgba(139,92,246,0.03) 100%);
                border: 1px solid rgba(99,102,241,0.15);
                border-radius: 16px;
                padding: 24px 28px;
                backdrop-filter: blur(8px);
                -webkit-backdrop-filter: blur(8px);
                transition: transform 0.2s, box-shadow 0.2s;
            }
            .upload-intro-card:hover {
                transform: translateY(-1px);
                box-shadow: 0 8px 24px rgba(99,102,241,0.06);
            }



            /* ── Format Row ── */
            .upload-format-row {
                display: flex; align-items: center; justify-content: center;
                gap: 8px; margin-top: 20px;
            }
            .upload-format-badge {
                background: rgba(99,102,241,0.08);
                border: 1px solid rgba(99,102,241,0.18);
                border-radius: 6px;
                padding: 3px 10px;
                font-size: 10px;
                font-weight: 800;
                color: #A78BFA;
                letter-spacing: 0.8px;
            }
            .upload-meta-pill {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.07);
                border-radius: 6px;
                padding: 3px 10px;
                font-size: 10px;
                color: #475569;
                font-weight: 500;
            }

            /* ── Layer 3: Trust Grid ── */
            .trust-grid {
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 12px;
            }
            .trust-badge {
                background: rgba(17,24,39,0.5);
                border: 1px solid rgba(255,255,255,0.05);
                border-radius: 14px;
                padding: 16px 14px;
                text-align: center;
                transition: transform 0.2s, box-shadow 0.2s;
                backdrop-filter: blur(8px);
                -webkit-backdrop-filter: blur(8px);
            }
            .trust-badge:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(99,102,241,0.08);
            }
            .trust-badge svg { margin-bottom: 8px; }
            .trust-badge-title {
                font-size: 12px; font-weight: 700; color: #E2E8F0;
                margin-bottom: 2px;
            }
            """, unsafe_allow_html=True)

            # ── Layer 1: Resume Analysis Card ──
            st.markdown("""
            <div class="upload-section-wrap">
              <div class="upload-intro-card">
                <div style="display:flex; align-items:flex-start; gap:16px;">
                  <div style="
                      width:44px; height:44px; flex-shrink:0;
                      background:linear-gradient(135deg,#6366F1,#8B5CF6);
                      border-radius:12px;
                      display:flex; align-items:center; justify-content:center;
                      box-shadow:0 4px 14px rgba(99,102,241,0.4);
                  ">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                      <line x1="16" y1="13" x2="8" y2="13"/>
                      <line x1="16" y1="17" x2="8" y2="17"/>
                    </svg>
                  </div>
                  <div style="flex:1;">
                    <div style="font-size:15px; font-weight:700; color:#F8FAFC; margin-bottom:4px; letter-spacing:-0.1px;">Resume Analysis</div>
                    <div style="font-size:13px; color:#64748B; line-height:1.65; margin-bottom:12px;">Upload your resume to unlock AI-powered analysis and personalized internship recommendations.</div>
                    <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px 12px;">
                      <div style="display:flex; align-items:center; gap:8px;">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2.5" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                        <span style="font-size:12px; color:#94A3B8; font-weight:500;">ATS Compatibility Score</span>
                      </div>
                      <div style="display:flex; align-items:center; gap:8px;">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2.5" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                        <span style="font-size:12px; color:#94A3B8; font-weight:500;">Skill Gap Detection</span>
                      </div>
                      <div style="display:flex; align-items:center; gap:8px;">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2.5" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                        <span style="font-size:12px; color:#94A3B8; font-weight:500;">Resume Parsing &amp; Extraction</span>
                      </div>
                      <div style="display:flex; align-items:center; gap:8px;">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2.5" stroke-linecap="round"><polyline points="20 6 9 17 4 12"/></svg>
                        <span style="font-size:12px; color:#94A3B8; font-weight:500;">Internship Matching</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            pdf_file = st.file_uploader("Upload Resume", type=["pdf"], label_visibility="collapsed", key="resume_pdf")

            st.markdown("""
            <div class="upload-section-wrap" style="margin-top: 14px;">
              <div class="upload-format-row">
                <span class="upload-format-badge">PDF</span>
                <span class="upload-meta-pill">Max 50 MB</span>
              </div>

              <!-- Layer 3: Trust Indicators -->
              <div class="trust-grid" style="margin-top: 16px;">
                <div class="trust-badge">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round">
                    <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                  </svg>
                  <div class="trust-badge-title">Secure Upload</div>
                  <div class="trust-badge-sub">Files are 100% private</div>
                </div>
                <div class="trust-badge">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#8B5CF6" stroke-width="2" stroke-linecap="round">
                    <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
                    <line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/>
                  </svg>
                  <div class="trust-badge-title">AI Parsing</div>
                  <div class="trust-badge-sub">Instant skill extraction</div>
                </div>
                <div class="trust-badge">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#A78BFA" stroke-width="2" stroke-linecap="round">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                  </svg>
                  <div class="trust-badge-title">Smart Matching</div>
                  <div class="trust-badge-sub">Personalized matches</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # Initialize resume_data
            resume_data = None
            
            if pdf_file is not None:
                st.session_state['resume_upload_attempted'] = True
                
                # Save uploaded file
                save_path = os.path.join(Config.UPLOAD_DIR, pdf_file.name)
                os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
                
                with open(save_path, "wb") as f:
                    f.write(pdf_file.getbuffer())
                
                # Track current resume to reset chat state if needed
                try:
                    current_resume_id = f"{save_path}:{os.path.getsize(save_path)}"
                except Exception:
                    current_resume_id = save_path
                    
                if st.session_state.get('resume_id') != current_resume_id:
                    # New file uploaded: show AI loading dashboard, then parse and cache
                    show_ai_loading_dashboard()
                    
                    parser = get_resume_parser()
                    resume_data = parser.parse_resume(pdf_file)
                        
                    # Predict category using ML model
                    resume_text = resume_data.get('raw_text', '')  # Use raw_text from parser
                    if resume_text:
                        try:
                            predicted_cat, top_3 = predict_resume_category(resume_text)
                            if predicted_cat:
                                resume_data['predicted_category'] = predicted_cat
                                resume_data['top_3_categories'] = top_3
                                # Success - no need to show message, it's displayed in the card below
                            # else:
                            #     st.warning("⚠️ ML Model could not predict category")
                        except Exception as e:
                            pass  # Silent fail - prediction is optional
                            # st.error(f"❌ ML prediction failed: {e}")
                    
                    st.session_state['resume_id'] = current_resume_id
                    st.session_state['resume_path'] = save_path
                    st.session_state['resume_data'] = resume_data
                    st.session_state['chat_messages'] = []
                    st.rerun()
                else:
                    # Same file selected; reuse cached parsed data
                    resume_data = st.session_state.get('resume_data')
            else:
                if st.session_state.get('resume_id') is not None:
                    # File was cleared by the user
                    st.session_state['resume_id'] = None
                    st.session_state['resume_path'] = None
                    st.session_state['resume_data'] = None
                    st.session_state['chat_messages'] = []
                    st.rerun()
                
                # Use cached parsed resume
                resume_data = st.session_state.get('resume_data')
                # If missing, try to re-parse from saved path to survive reruns/errors
                resume_path = st.session_state.get('resume_path')
                if not resume_data and resume_path and os.path.exists(resume_path):
                    try:
                        parser = get_resume_parser()
                        with open(resume_path, "rb") as f:
                            resume_data = parser.parse_resume(f)
                        st.session_state['resume_data'] = resume_data
                        st.rerun()
                    except Exception:
                        pass
            
            if resume_data:
                # Spacer before results section
                st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
                
                # Display candidate info - Modern Card Design
                st.markdown(f"""
                <style>
                @keyframes shimmer {{
                    0% {{ left: -100%; }}
                    100% {{ left: 100%; }}
                }}
                
                @keyframes cardSlideIn {{
                    0% {{ 
                        opacity: 0;
                        transform: translateY(10px);
                    }}
                    100% {{ 
                        opacity: 1;
                        transform: translateY(0px);
                    }}
                }}
                </style>
                """, unsafe_allow_html=True)
                
                # Default role is auto-detect
                _resume_for_score = dict(resume_data)
                breakdown = AnalyticsUtils.calculate_resume_score_breakdown(_resume_for_score)
                score = breakdown.get("total", 0)
                components = breakdown.get("components", {})
                sections_presence = components.get('sections_presence') or {}
                suggestions = breakdown.get("suggestions", [])
                scores_summary = breakdown.get("scores", {})

                # Profile Overview Card (sleek, minimal)
                subtitle = "Candidate Profile"
                email = resume_data.get('email') or 'N/A'
                phone = resume_data.get('mobile_number') or 'N/A'
                linkedin = resume_data.get('linkedin')
                github = resume_data.get('github')
                
                # Build contact cards dynamically
                contact_cards = []
                contact_cards.append(f'<div class="ov-card-mini">📧 {email}</div>')
                contact_cards.append(f'<div class="ov-card-mini">📞 {phone}</div>')
                if linkedin or github:
                    raw_link = linkedin if linkedin else github
                    def _pick_link(v):
                        if isinstance(v, (list, tuple, set)):
                            for x in v:
                                if isinstance(x, str) and x.strip():
                                    return x.strip()
                            return None
                        if isinstance(v, dict):
                            for k in ("url", "href", "link", "profile", "username"):
                                val = v.get(k)
                                if isinstance(val, str) and val.strip():
                                    return val.strip()
                            return None
                        if isinstance(v, str):
                            s = v.strip()
                            return s or None
                        return None
                    link_text = _pick_link(raw_link)
                    if link_text:
                        lt = link_text
                        lower = lt.lower()
                        link_href = lt if lower.startswith(("http://", "https://")) else ("https://" + lt.lstrip("/"))
                        link_disp = lt.replace("https://", "").replace("http://", "")
                        contact_cards.append(f'<div class="ov-card-mini">🔗 <a class="inline" href="{link_href}" target="_blank">{link_disp}</a></div>')

                # Calculate dashboard variables
                skills_count = len(resume_data.get('skills') or [])
                present_count = sum(1 for k in ['experience','education','skills','summary','projects'] if sections_presence.get(k))
                percent = int((present_count/5)*100)
                pages = max(1, len(resume_data.get('raw_text', '')) // 2000)
                
                exp_years = resume_data.get('total_experience') or 0
                if exp_years >= 5:
                    candidate_level = "Senior Specialist"
                elif exp_years >= 2:
                    candidate_level = "Mid-Level Professional"
                else:
                    candidate_level = "Entry / Student"
                    
                if score >= 85:
                    grade = "Excellent"
                    score_color = "#10B981"
                    grade_icon = "🎯"
                elif score >= 70:
                    grade = "Good"
                    score_color = "#34D399"
                    grade_icon = "✓"
                elif score >= 55:
                    grade = "Fair"
                    score_color = "#F59E0B"
                    grade_icon = "⚡"
                else:
                    grade = "Needs Work"
                    score_color = "#EF4444"
                    grade_icon = "🔧"

                predicted_cat = resume_data.get('predicted_category') or "Not Detected"

                st.markdown(clean_html(f"""
                <style>
                .ov-avatar {{ 
                    width: 50px; 
                    height: 50px; 
                    border-radius: 50%; 
                    background: linear-gradient(135deg, #6366F1, #8B5CF6); 
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    color: white; 
                    font-weight: 900; 
                    font-size: 20px;
                    box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3);
                }}
                .ov-name {{ color: #F8FAFC; font-weight: 800; font-size: 22px; letter-spacing: -0.3px; }}
                .ov-sub {{ color: #94A3B8; font-size: 13px; margin-top: 2px; }}
                .ov-card-mini {{ 
                    display: inline-flex; 
                    align-items: center; 
                    gap: 8px; 
                    border: 1px solid rgba(255, 255, 255, 0.06); 
                    background: rgba(255, 255, 255, 0.03); 
                    padding: 8px 12px; 
                    border-radius: 8px; 
                    color: #E2E8F0; 
                    font-size: 13px;
                    transition: all 0.2s ease;
                }}
                .ov-card-mini:hover {{
                    background: rgba(255, 255, 255, 0.06);
                    border-color: rgba(99, 102, 241, 0.2);
                }}
                .kpi-title {{
                    font-size: 11px; 
                    font-weight: 700; 
                    color: #94A3B8; 
                    text-transform: uppercase; 
                    letter-spacing: 0.06em; 
                    margin-bottom: 6px;
                }}
                .kpi-value {{
                    font-size: 24px; 
                    font-weight: 800; 
                    color: #F8FAFC;
                }}
                </style>
                
                <div id="profile-section" class="glass-card fade-in">
                    <!-- Contact and Title Header -->
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.08); padding-bottom: 16px; margin-bottom: 20px; flex-wrap: wrap; gap: 16px;">
                        <div style="display: flex; align-items: center; gap: 14px;">
                            <div class="ov-avatar">{(resume_data.get('name','?') or '?')[:1].upper()}</div>
                            <div>
                                <div class="ov-name">{resume_data.get('name') or 'Candidate'}</div>
                                <div class="ov-sub">{subtitle}</div>
                            </div>
                        </div>
                        <div style="display: flex; gap: 8px; flex-wrap: wrap;">
                            {''.join(contact_cards)}
                        </div>
                    </div>
                    
                    <!-- KPI Metric Grid -->
                    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 16px;">
                        <!-- KPI 1: Resume Score -->
                        <div style="background: rgba(16, 185, 129, 0.04); border: 1px solid rgba(16, 185, 129, 0.2); border-radius: 12px; padding: 16px; text-align: center;">
                            <div class="kpi-title">Resume Score</div>
                            <div class="kpi-value" style="color: {score_color};">{score}<span style="font-size: 13px; color: #64748B; font-weight:500;">/100</span></div>
                            <div style="font-size: 11px; color: {score_color}; margin-top: 4px; font-weight: 600;">{grade_icon} {grade}</div>
                        </div>
                        <!-- KPI 2: Candidate Level -->
                        <div style="background: rgba(99, 102, 241, 0.04); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 12px; padding: 16px; text-align: center;">
                            <div class="kpi-title">Candidate Level</div>
                            <div style="font-size: 15px; font-weight: 800; color: #F8FAFC; margin-top: 8px; min-height: 38px; display: flex; align-items: center; justify-content: center;">{candidate_level}</div>
                        </div>
                        <!-- KPI 3: Skills Found -->
                        <div style="background: rgba(139, 92, 246, 0.04); border: 1px solid rgba(139, 92, 246, 0.2); border-radius: 12px; padding: 16px; text-align: center;">
                            <div class="kpi-title">Skills Found</div>
                            <div class="kpi-value" style="color: #A78BFA; margin-top: 2px;">{skills_count}</div>
                            <div style="font-size: 11px; color: #94A3B8; margin-top: 4px;">Detected Tech Skills</div>
                        </div>
                        <!-- KPI 4: Recommended Domain -->
                        <div style="background: rgba(45, 212, 191, 0.04); border: 1px solid rgba(45, 212, 191, 0.2); border-radius: 12px; padding: 16px; text-align: center;">
                            <div class="kpi-title">Recommended Domain</div>
                            <div style="font-size: 14px; font-weight: 800; color: #2DD4BF; margin-top: 8px; min-height: 38px; display: flex; align-items: center; justify-content: center; line-height: 1.3;">{predicted_cat}</div>
                        </div>
                        <!-- KPI 5: Document Pages -->
                        <div style="background: rgba(255, 255, 255, 0.02); border: 1px solid rgba(255, 255, 255, 0.06); border-radius: 12px; padding: 16px; text-align: center;">
                            <div class="kpi-title">Pages</div>
                            <div class="kpi-value" style="margin-top: 2px;">{pages}</div>
                            <div style="font-size: 11px; color: #94A3B8; margin-top: 4px;">PDF Length</div>
                        </div>
                        <!-- KPI 6: Completeness -->
                        <div style="background: rgba(56, 189, 248, 0.04); border: 1px solid rgba(56, 189, 248, 0.15); border-radius: 12px; padding: 16px; text-align: center;">
                            <div class="kpi-title">Completeness</div>
                            <div class="kpi-value" style="color: #38BDF8; margin-top: 2px;">{percent}%</div>
                            <div style="font-size: 11px; color: #94A3B8; margin-top: 4px;">{present_count}/5 Sections</div>
                        </div>
                    </div>
                </div>
                """), unsafe_allow_html=True)
                
                # Skills Extracted (moved up before AI-Detected Profile)
                st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
                skills = resume_data.get('skills', [])
                if skills:
                    categorized_skills = categorize_skills(skills)
                    display_skills(categorized_skills)
                    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
                
                # ML Category Prediction Badge
                predicted_cat = resume_data.get('predicted_category')
                top_3 = resume_data.get('top_3_categories', [])

                if predicted_cat and top_3:
                    confidence = top_3[0]['probability'] * 100 if top_3 else 0

                    # Resolve model type label for display
                    _model_obj = load_resume_classifier()
                    _model_type_label = getattr(_model_obj, '_internhunt_model_type', 'Neural Network')

                    # Build top-3 predictions HTML with fuzzy confidence labels
                    top_3_html = ""
                    for i, pred in enumerate(top_3[:3]):
                        prob    = pred['probability'] * 100
                        category = pred['category']
                        fl      = pred.get('fuzzy_label', 'Low')   # High / Medium / Low
                        icon    = "🎯" if i == 0 else "🔹" if i == 1 else "🔸"
                        fl_cls  = f"fuzzy-{fl.lower()}"
                        top_3_html += (
                            f'<div class="pred-item">'
                            f'{icon} <span class="pred-cat">{category}</span>'
                            f'<span class="pred-prob">{prob:.1f}%</span>'
                            f'<span class="{fl_cls}">{fl}</span>'
                            f'</div>'
                        )

                    st.markdown(f"""
                    <style>
                    .ml-prediction-card {{
                        background: linear-gradient(145deg, #0b1221, #151c30);
                        border: 2px solid rgba(99, 102, 241, 0.3);
                        border-radius: 20px;
                        padding: 20px 24px;
                        margin: 12px 0 20px;
                        box-shadow: 0 12px 32px rgba(99, 102, 241, 0.15), 0 0 40px rgba(99, 102, 241, 0.08);
                        position: relative;
                        overflow: hidden;
                    }}
                    .ml-prediction-card::before {{
                        content: '';
                        position: absolute;
                        top: 0; left: 0; right: 0;
                        height: 3px;
                        background: linear-gradient(90deg, #6366F1, #8B5CF6, #06B6D4);
                    }}
                    .ml-header {{
                        display: flex;
                        align-items: center;
                        gap: 12px;
                        margin-bottom: 16px;
                    }}
                    .ml-icon {{
                        width: 42px; height: 42px;
                        background: linear-gradient(135deg, #6366F1, #8B5CF6);
                        border-radius: 12px;
                        display: flex; align-items: center; justify-content: center;
                        font-size: 20px;
                        box-shadow: 0 6px 18px rgba(99, 102, 241, 0.3);
                    }}
                    .ml-title {{
                        font-size: 18px; font-weight: 800;
                        color: #E6EAF3; margin: 0; flex: 1;
                    }}
                    .ml-model-chip {{
                        font-size: 11px; font-weight: 700;
                        padding: 3px 10px; border-radius: 999px;
                        background: rgba(139, 92, 246, 0.15);
                        border: 1px solid rgba(139, 92, 246, 0.4);
                        color: #a78bfa; letter-spacing: 0.04em;
                    }}
                    .ml-badge {{
                        display: inline-flex; align-items: center; gap: 8px;
                        padding: 10px 16px; border-radius: 12px;
                        background: linear-gradient(135deg, rgba(99,102,241,0.2), rgba(139,92,246,0.15));
                        border: 1px solid rgba(99, 102, 241, 0.4);
                        margin-bottom: 14px;
                    }}
                    .ml-badge-label {{ font-size:14px; color:#A6ADBB; font-weight:600; }}
                    .ml-badge-value {{ font-size:18px; color:#E6EAF3; font-weight:800; }}
                    .ml-badge-conf  {{
                        font-size:13px; color:#22C55E; font-weight:700;
                        background:rgba(34,197,94,0.15); padding:4px 10px;
                        border-radius:8px; border:1px solid rgba(34,197,94,0.3);
                    }}
                    .top-predictions {{
                        display: flex; flex-direction: column; gap: 8px;
                        padding: 14px;
                        background: rgba(255,255,255,0.02);
                        border-radius: 12px;
                        border: 1px solid rgba(255,255,255,0.06);
                    }}
                    .top-pred-header {{
                        font-size:11px; font-weight:700; color:#6b7280;
                        letter-spacing:0.08em; text-transform:uppercase; margin-bottom:4px;
                    }}
                    .pred-item {{
                        display:flex; align-items:center; gap:10px;
                        font-size:14px; color:#D9E2F1;
                    }}
                    .pred-cat  {{ flex:1; font-weight:600; }}
                    .pred-prob {{ font-weight:700; color:#8B5CF6; min-width:52px; text-align:right; }}
                    /* Fuzzy label badges */
                    .fuzzy-high   {{ font-size:11px; font-weight:700; padding:2px 8px; border-radius:999px;
                                     background:rgba(34,197,94,0.15); border:1px solid rgba(34,197,94,0.4); color:#22c55e; }}
                    .fuzzy-medium {{ font-size:11px; font-weight:700; padding:2px 8px; border-radius:999px;
                                     background:rgba(234,179,8,0.15);  border:1px solid rgba(234,179,8,0.4);  color:#eab308; }}
                    .fuzzy-low    {{ font-size:11px; font-weight:700; padding:2px 8px; border-radius:999px;
                                     background:rgba(239,68,68,0.12);  border:1px solid rgba(239,68,68,0.35); color:#f87171; }}
                    .fuzzy-legend {{
                        font-size:11px; color:#4b5563; margin-top:10px;
                        padding-top:8px; border-top:1px solid rgba(255,255,255,0.05);
                    }}
                    </style>
                    
                    <div id="ai-profile-section" class="ml-prediction-card fade-in">
                        <div class="ml-header">
                            <div class="ml-icon">🤖</div>
                            <div class="ml-title">AI-Detected Profile</div>
                            <span class="ml-model-chip">⚡ {_model_type_label}</span>
                        </div>
                        <div class="ml-badge">
                            <span class="ml-badge-label">Category:</span>
                            <span class="ml-badge-value">{predicted_cat}</span>
                            <span class="ml-badge-conf">{confidence:.1f}% match</span>
                        </div>
                        <div class="top-predictions">
                            <div class="top-pred-header">Top 3 Predictions · Fuzzy Confidence</div>
                            {top_3_html}
                            <div class="fuzzy-legend">🟢 High &gt;70% &nbsp;|&nbsp; 🟡 Medium 40–70% &nbsp;|&nbsp; 🔴 Low &lt;40%</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Spacer after AI-Detected Profile
                st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

                # Premium ATS Score Dashboard
                st.markdown("""
                <style>
                .ats-dashboard {
                    background: linear-gradient(135deg, #1A1F3A 0%, #242F5C 50%, #1A1F3A 100%);
                    border: 1.5px solid rgba(99, 102, 241, 0.3);
                    border-radius: 20px;
                    padding: 40px;
                    margin: 40px 0;
                    box-shadow: 0 15px 50px rgba(99, 102, 241, 0.12), 0 0 30px rgba(99, 102, 241, 0.05);
                    position: relative;
                    overflow: hidden;
                }
                
                .ats-dashboard::before {
                    content: '';
                    position: absolute;
                    top: -50%;
                    left: -50%;
                    width: 200%;
                    height: 200%;
                    background: conic-gradient(from 0deg, transparent, rgba(99, 102, 241, 0.03), transparent);
                    animation: rotate 20s linear infinite;
                }
                
                @keyframes rotate {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
                
                .dashboard-header {
                    display: flex;
                    align-items: center;
                    gap: 16px;
                    margin-bottom: 32px;
                    position: relative;
                    z-index: 2;
                }
                
                .dashboard-title {
                    font-size: 24px;
                    font-weight: 800;
                    color: #E0E7FF;
                    margin: 0;
                }
                
                .dashboard-icon {
                    width: 40px;
                    height: 40px;
                    background: linear-gradient(135deg, #6366F1, #8B5CF6);
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 20px;
                    box-shadow: 0 8px 20px rgba(99, 102, 241, 0.3);
                }
                
                .score-overview {
                    display: grid;
                    grid-template-columns: 1fr 2fr;
                    gap: 40px;
                    margin-bottom: 40px;
                    position: relative;
                    z-index: 2;
                }
                
                .score-gauge-container {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                }
                
                .score-gauge {
                    width: 160px;
                    height: 160px;
                    position: relative;
                    margin-bottom: 20px;
                }
                
                .score-gauge svg {
                    transform: rotate(-90deg);
                    width: 100%;
                    height: 100%;
                }
                
                .score-gauge-bg {
                    fill: none;
                    stroke: rgba(75, 85, 99, 0.2);
                    stroke-width: 10;
                }
                
                .score-gauge-progress {
                    fill: none;
                    stroke-width: 10;
                    stroke-linecap: round;
                    filter: drop-shadow(0 0 8px rgba(16, 185, 129, 0.5));
                    transition: stroke-dashoffset 1.5s ease-out;
                }
                
                .score-gauge-inner {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    width: 130px;
                    height: 130px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, #0F1629, #1A1F3A);
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    border: 2px solid rgba(99, 102, 241, 0.2);
                    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
                }
                
                .score-number {
                    font-size: 32px;
                    font-weight: 900;
                    color: #10B981;
                    line-height: 1;
                }
                
                .score-label {
                    font-size: 12px;
                    color: #9CA3AF;
                    margin-top: 4px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }
                
                .score-grade {
                    display: inline-flex;
                    align-items: center;
                    gap: 8px;
                    padding: 8px 16px;
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(16, 185, 129, 0.05));
                    border: 1px solid rgba(16, 185, 129, 0.3);
                    border-radius: 20px;
                    color: #34D399;
                    font-size: 14px;
                    font-weight: 700;
                }
                
                .sections-overview {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                    gap: 20px;
                    margin-bottom: 40px;
                    position: relative;
                    z-index: 2;
                }
                
                .section-card-premium {
                    background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(139, 92, 246, 0.03));
                    border: 1px solid rgba(99, 102, 241, 0.2);
                    border-radius: 16px;
                    padding: 24px;
                    text-align: center;
                    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
                    position: relative;
                    overflow: hidden;
                    backdrop-filter: blur(10px);
                }
                
                .section-card-premium::before {
                    content: '';
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    height: 3px;
                    background: linear-gradient(90deg, transparent, var(--status-color), transparent);
                    transition: all 0.3s ease;
                }
                
                .section-card-premium:hover {
                    transform: translateY(-8px);
                    box-shadow: 0 20px 40px rgba(99, 102, 241, 0.15);
                    border-color: rgba(167, 139, 250, 0.4);
                    background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(139, 92, 246, 0.06));
                }
                
                .section-card-premium:hover::before {
                    height: 4px;
                    box-shadow: 0 0 20px var(--status-color);
                }
                
                .section-icon-modern {
                    width: 48px;
                    height: 48px;
                    margin: 0 auto 16px;
                    border-radius: 12px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 24px;
                    position: relative;
                    transition: all 0.3s ease;
                }
                
                .section-name-modern {
                    color: #E0E7FF;
                    font-size: 14px;
                    font-weight: 700;
                    margin-bottom: 12px;
                }
                
                .status-indicator {
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    gap: 6px;
                    padding: 6px 12px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                    position: relative;
                }
                
                .status-present-premium {
                    background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(16, 185, 129, 0.05));
                    border: 1px solid rgba(16, 185, 129, 0.4);
                    color: #34D399;
                }
                
                .status-missing-premium {
                    background: linear-gradient(135deg, rgba(245, 158, 11, 0.2), rgba(245, 158, 11, 0.05));
                    border: 1px solid rgba(245, 158, 11, 0.4);
                    color: #FBBF24;
                }
                
                .insights-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                    gap: 24px;
                    position: relative;
                    z-index: 2;
                }
                
                .insights-panel {
                    background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(139, 92, 246, 0.02));
                    border: 1px solid rgba(99, 102, 241, 0.15);
                    border-radius: 16px;
                    padding: 24px;
                    backdrop-filter: blur(10px);
                    transition: all 0.3s ease;
                }
                
                .insights-panel:hover {
                    border-color: rgba(167, 139, 250, 0.3);
                    box-shadow: 0 8px 25px rgba(99, 102, 241, 0.1);
                }
                
                .panel-header {
                    display: flex;
                    align-items: center;
                    gap: 12px;
                    margin-bottom: 16px;
                }
                
                .panel-icon {
                    width: 32px;
                    height: 32px;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 16px;
                }
                
                .panel-title {
                    color: #E0E7FF;
                    font-size: 16px;
                    font-weight: 700;
                    margin: 0;
                }
                
                .insight-item {
                    display: flex;
                    align-items: flex-start;
                    gap: 12px;
                    padding: 12px 0;
                    border-bottom: 1px solid rgba(99, 102, 241, 0.1);
                }
                
                .insight-item:last-child {
                    border-bottom: none;
                    padding-bottom: 0;
                }
                
                .insight-item:first-child {
                    padding-top: 0;
                }
                
                .insight-icon {
                    width: 20px;
                    height: 20px;
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 10px;
                    flex-shrink: 0;
                    margin-top: 2px;
                }
                
                .insight-text {
                    color: #CBD5E1;
                    font-size: 14px;
                    line-height: 1.5;
                    font-weight: 500;
                }
                
                .strength-icon {
                    background: linear-gradient(135deg, #10B981, #059669);
                    color: white;
                }
                
                .improvement-icon {
                    background: linear-gradient(135deg, #F59E0B, #D97706);
                    color: white;
                }
                
                @media (max-width: 768px) {
                    .score-overview {
                        grid-template-columns: 1fr;
                        text-align: center;
                    }
                    
                    .sections-overview {
                        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
                    }
                    
                    .insights-grid {
                        grid-template-columns: 1fr;
                    }
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Get the feedback data
                feedback = breakdown.get('feedback')
                strong_areas = breakdown.get('strong_areas', [])
                weak_areas = breakdown.get('weak_areas', [])
                
                # Determine score color and grade
                if score >= 85:
                    grade = "Excellent"
                    score_color = "#10B981"
                    grade_icon = "🎯"
                elif score >= 70:
                    grade = "Good"
                    score_color = "#34D399"
                    grade_icon = "✅"
                elif score >= 55:
                    grade = "Fair"
                    score_color = "#F59E0B"
                    grade_icon = "⚡"
                else:
                    grade = "Needs Work"
                    score_color = "#EF4444"
                    grade_icon = "🔧"
                
                # Calculate SVG circle parameters
                radius = 70  # SVG circle radius
                circumference = 2 * 3.14159 * radius  # ~439.8
                # For stroke-dashoffset: 
                # - Full circumference = 0% filled (circle hidden)
                # - 0 = 100% filled (full circle)
                # So for 75%, we want 25% remaining = circumference * 0.25
                progress_offset = circumference * (100 - score) / 100
                
                # Top spacer before ATS dashboard
                st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
                
                # Build dashboard using component approach
                dashboard_parts = [
                    '<div id="ats-dashboard-section" class="ats-dashboard">',
                    '<div class="dashboard-header">',
                    '<div class="dashboard-icon">🎯</div>',
                    '<h2 class="dashboard-title">ATS Performance Dashboard</h2>',
                    '</div>',
                    '<div class="score-overview">',
                    '<div class="score-gauge-container">',
                    f'<div class="score-gauge">',
                    '<svg width="160" height="160" viewBox="0 0 160 160">',
                    # Background circle
                    '<circle class="score-gauge-bg" cx="80" cy="80" r="70" />',
                    # Progress circle with inline styles for dasharray and dashoffset
                    f'<circle class="score-gauge-progress" cx="80" cy="80" r="70" style="stroke: {score_color}; stroke-dasharray: {circumference}; stroke-dashoffset: {progress_offset};" />',
                    '</svg>',
                    '<div class="score-gauge-inner">',
                    f'<div class="score-number" style="color: {score_color};">{score}</div>',
                    '<div class="score-label">/ 100</div>',
                    '</div>',
                    '</div>',
                    '<div class="score-grade">',
                    f'<span>{grade_icon}</span>',
                    f'<span>{grade}</span>',
                    '</div>',
                    '</div>',
                    '<div style="display: flex; flex-direction: column; justify-content: center; gap: 16px;">',
                ]
                
                # Add score breakdown metrics instead of feedback text
                if scores_summary:
                    dashboard_parts.extend([
                        '<div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">'
                    ])
                    
                    max_map = {
                        'content_quality': 50,
                        'formatting': 15,
                        'keyword_relevance': 20,
                        'experience_impact': 10,
                        'readability': 5,
                    }
                    
                    for k, v in scores_summary.items():
                        label = k.replace('_', ' ').title()
                        denom = max_map.get(k, 100)
                        val = round(float(v), 1) if isinstance(v, (int, float)) else v
                        percentage = int((val / denom) * 100) if denom > 0 else 0
                        
                        dashboard_parts.extend([
                            '<div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(139, 92, 246, 0.05)); border: 1px solid rgba(99, 102, 241, 0.2); border-radius: 12px; padding: 16px;">',
                            f'<div style="color: #E0E7FF; font-size: 14px; font-weight: 700; margin-bottom: 8px;">{label}</div>',
                            f'<div style="color: #818CF8; font-size: 18px; font-weight: 800;">{val}/{denom}</div>',
                            f'<div style="background: rgba(99, 102, 241, 0.1); height: 4px; border-radius: 2px; margin-top: 8px; overflow: hidden;">',
                            f'<div style="background: linear-gradient(90deg, #6366F1, #8B5CF6); height: 100%; width: {percentage}%; border-radius: 2px; transition: width 0.3s ease;"></div>',
                            '</div>',
                            '</div>'
                        ])
                    
                    dashboard_parts.append('</div>')
                
                dashboard_parts.extend([
                    '</div>',
                    '</div>',
                    '<div class="sections-overview">'
                ])
                
                # Add the enhanced section cards
                items = [
                    ('Experience', 'experience', '💼'),
                    ('Education', 'education', '🎓'),
                    ('Skills', 'skills', '🛠️'),
                    ('Summary', 'summary', '📝'),
                    ('Projects', 'projects', '🚀'),
                ]
                
                for label, key_, icon in items:
                    ok = bool(sections_presence.get(key_))
                    status_class = 'status-present-premium' if ok else 'status-missing-premium'
                    status_color = '#10B981' if ok else '#F59E0B'
                    status_text = 'Present' if ok else 'Missing'
                    status_icon = '✓' if ok else '⚠'
                    
                    dashboard_parts.extend([
                        f'<div class="section-card-premium" style="--status-color: {status_color};">',
                        f'<div class="section-icon-modern" style="background: linear-gradient(135deg, {status_color}20, {status_color}10);">{icon}</div>',
                        f'<div class="section-name-modern">{label}</div>',
                        f'<div class="status-indicator {status_class}">',
                        f'<span>{status_icon}</span>',
                        f'<span>{status_text}</span>',
                        '</div>',
                        '</div>'
                    ])
                
                dashboard_parts.extend([
                    '</div>',
                    '<div class="insights-grid">'
                ])
                
                # Strengths panel
                if strong_areas:
                    dashboard_parts.extend([
                        '<div class="insights-panel">',
                        '<div class="panel-header">',
                        '<div class="panel-icon" style="background: linear-gradient(135deg, #10B981, #059669); color: white;">✓</div>',
                        '<h3 class="panel-title">Strengths</h3>',
                        '</div>'
                    ])
                    
                    for strength in strong_areas[:4]:  # Limit to top 4
                        dashboard_parts.extend([
                            '<div class="insight-item">',
                            '<div class="insight-icon strength-icon">✓</div>',
                            f'<div class="insight-text">{strength}</div>',
                            '</div>'
                        ])
                    
                    dashboard_parts.append('</div>')
                
                # Areas for improvement panel
                if weak_areas:
                    dashboard_parts.extend([
                        '<div class="insights-panel">',
                        '<div class="panel-header">',
                        '<div class="panel-icon" style="background: linear-gradient(135deg, #F59E0B, #D97706); color: white;">⚡</div>',
                        '<h3 class="panel-title">Areas for Improvement</h3>',
                        '</div>'
                    ])
                    
                    for area in weak_areas[:4]:  # Limit to top 4
                        dashboard_parts.extend([
                            '<div class="insight-item">',
                            '<div class="insight-icon improvement-icon">!</div>',
                            f'<div class="insight-text">{area}</div>',
                            '</div>'
                        ])
                    
                    dashboard_parts.append('</div>')
                
                dashboard_parts.extend(['</div>', '</div>'])
                
                st.markdown(''.join(dashboard_parts), unsafe_allow_html=True)

                # Minimal spacing before suggestions
                st.markdown("<div style='margin-top:15px'></div>", unsafe_allow_html=True)

                # Initialize role before conditional blocks so it's always defined
                role: str = components.get('kw_role_alignment_role') or 'Software Engineer'

                if suggestions:
                    # Styles for nicer suggestions list and expanders
                    st.markdown("""
                    <style>
                    .sugg-wrap { margin-top: 16px; }
                    .sugg-title { color:#FFFFFF; margin-bottom:12px; font-weight:800; }
                    .sugg-list { display:flex; flex-direction:column; gap:8px; }
                    .sugg-item { display:flex; align-items:flex-start; gap:10px; padding:10px 12px; border-radius:12px; border:1px solid rgba(99,102,241,.25); background:linear-gradient(135deg, rgba(99,102,241,.10), rgba(37,99,235,.08)); }
                    .sugg-num { width:26px; height:26px; border-radius:999px; display:inline-flex; align-items:center; justify-content:center; font-weight:800; color:#E0E7FF; background:rgba(99,102,241,.35); border:1px solid rgba(99,102,241,.45); }
                    .sugg-text { color:#E0E7FF; font-size:14px; font-weight:600; }
                    [data-testid=\"stExpander\"] { border:1px solid rgba(99,102,241,.25); border-radius:12px; background:linear-gradient(135deg,#0F1534,#121A3F); }
                    [data-testid=\"stExpander\"] > summary { color:#E0E7FF; font-weight:700; }
                    [data-testid=\"stCodeBlock\"] pre { background:#0B1220 !important; border:1px solid rgba(99,102,241,.25); border-radius:10px; }
                    /* Template cards */
                    .tpl-card { border:1px solid rgba(99,102,241,.35); border-radius:12px; background:linear-gradient(135deg,#0B1220,#11183A); padding:14px; }
                    .tpl-head { display:flex; align-items:center; gap:8px; color:#E0E7FF; font-weight:800; margin-bottom:6px; }
                    .tpl-tags { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:8px; }
                    .tpl-tag { background:rgba(99,102,241,.15); border:1px solid rgba(99,102,241,.35); color:#E0E7FF; padding:2px 8px; border-radius:999px; font-size:12px; font-weight:600; }
                    .tpl-pre { margin:0; white-space:pre-wrap; color:#E5E7EB; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, \'Liberation Mono\', \'Courier New\', monospace; font-size:13px; line-height:1.55; }
                    .tpl-tips { margin-top:8px; color:#A5B4FC; font-size:12px; }
                    </style>
                    """, unsafe_allow_html=True)

                    # Header
                    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)
                    st.markdown('<div id="suggestions-section" class="sugg-wrap"><h3 class="sugg-title">💡 Top Suggestions</h3></div>', unsafe_allow_html=True)

                    # Suggestions list
                    resume_hash = hash(str(resume_data.get('skills', [])) + str(resume_data.get('email', ''))) if resume_data else 0
                    if resume_data:
                        # Load personalized suggestions using st.session_state cache
                        cache_key = f"pers_suggs_{resume_hash}"
                        if cache_key not in st.session_state:
                            with st.spinner("Analyzing resume to generate custom suggestions..."):
                                try:
                                    from chat_service import generate_personalized_suggestions
                                    custom_suggs = generate_personalized_suggestions(resume_data)
                                    if custom_suggs:
                                        st.session_state[cache_key] = custom_suggs
                                    else:
                                        st.session_state[cache_key] = suggestions
                                except Exception:
                                    st.session_state[cache_key] = suggestions
                        suggestions = st.session_state[cache_key]

                    rows = [
                        f"<div class='sugg-item'><span class='sugg-num'>{idx}</span><span class='sugg-text'>{s}</span></div>"
                        for idx, s in enumerate(suggestions, start=1)
                    ]
                    st.markdown(f"<div class='sugg-list'>{''.join(rows)}</div>", unsafe_allow_html=True)

                    # Templates for missing sections
                    st.markdown("""
                    <style>
                    .tpl-card {
                        background-color: #0f1720;
                        border-radius: 12px;
                        padding: 16px;
                        margin-bottom: 16px;
                        border: 1px solid rgba(255,255,255,0.04);
                    }
                    .tpl-head {
                        font-size: 18px;
                        font-weight: 600;
                        color: #e6eef8;
                        margin-bottom: 8px;
                    }
                    .tpl-tags { margin-bottom: 10px; }
                    .tpl-tag {
                        display: inline-block;
                        background: linear-gradient(90deg,#5b8cff,#8b5cf6);
                        color: #fff;
                        padding: 5px 10px;
                        border-radius: 999px;
                        font-size: 12px;
                        margin-right: 6px;
                    }
                    .tpl-pre {
                        background-color: #0b0d11;
                        color: #dbeafe;
                        padding: 12px;
                        border-radius: 8px;
                        line-height: 1.6;
                        white-space: pre-line; /* preserves newlines while allowing wrapping */
                        font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, "Roboto Mono", "Courier New", monospace;
                        font-size: 13px;
                        border-left: 3px solid rgba(99,102,241,0.85);
                        margin-top: 8px;
                    }
                    .tpl-tips {
                        margin-top: 10px;
                        color: #9aa4b2;
                        font-size: 13px;
                    }
                    </style>
                    """, unsafe_allow_html=True)

                    # Load personalized templates
                    custom_templates = []
                    if resume_data:
                        tpls_cache_key = f"pers_tpls_{resume_hash}"
                        if tpls_cache_key not in st.session_state:
                            with st.spinner("Generating tailored resume templates..."):
                                try:
                                    from chat_service import generate_personalized_templates
                                    custom_tpls = generate_personalized_templates(resume_data)
                                    if custom_tpls:
                                        st.session_state[tpls_cache_key] = custom_tpls
                                    else:
                                        st.session_state[tpls_cache_key] = []
                                except Exception:
                                    st.session_state[tpls_cache_key] = []
                        custom_templates = st.session_state[tpls_cache_key]

                    if custom_templates:
                        st.markdown("<div style='margin-top:24px; margin-bottom:12px; font-weight:600; color:#cbd5e1; font-size:1rem;'>📋 Tailored ATS Resume Templates</div>", unsafe_allow_html=True)
                        for tpl_idx, tpl in enumerate(custom_templates):
                            title = tpl.get("title", "Tailored Resume Template")
                            tags = tpl.get("tags", [])
                            content = tpl.get("content", "")
                            tip = tpl.get("tip", "")
                            
                            tag_spans = "".join([f"<span class='tpl-tag'>{t}</span>" for t in tags])
                            
                            with st.expander(f"✨ Add {title}", expanded=(tpl_idx == 0)):
                                tpl_html = f"""
                                <div class='tpl-card'>
                                    <div class='tpl-head'>{title}</div>
                                    <div class='tpl-tags'>{tag_spans}</div>
                                    <div class='tpl-pre'>{content}</div>
                                    <div class='tpl-tips'>💡 Tip: {tip}</div>
                                </div>
                                """
                                st.markdown(tpl_html, unsafe_allow_html=True)
                    else:
                        # --- Fallback: Prepare variables ---
                        sp = components.get('sections_presence') or {}
                        top_skills = (resume_data.get('skills') or [])[:3]
                        # Use auto-detected role by default
                        role = components.get('kw_role_alignment_role') or 'Software Engineer'
                        role_for_tpl = role  # Define role_for_tpl for template usage
                        role_skills = ', '.join(top_skills) if top_skills else 'relevant tools/skills'

                        # --- Work Experience Template ---
                        if not sp.get('experience'):
                            with st.expander("💼 Add Work Experience Template", expanded=False):
                                tpl_html = (
                                    "<div class='tpl-card'>"
                                    "<div class='tpl-head'>Work Experience (STAR)</div>"
                                    "<div class='tpl-tags'>"
                                    "<span class='tpl-tag'>{role}</span>"
                                    "<span class='tpl-tag'>{skills}</span>"
                                    "</div>"
                                    "<div class='tpl-pre'>"
                                    "[Job Title] &mdash; [Company], [City] | [MMM YYYY] &ndash; [MMM YYYY or Present]\n"
                                    "Scope: Owned [area/scope]; tools: [{skills}]\n"
                                    "Impact: Achieved &lt;metric/value&gt; by &lt;action&gt;.\n\n"
                                    "&bull; Led &lt;project/feature&gt; using {skills}; increased &lt;KPI&gt; by &lt;X%&gt;.\n"
                                    "&bull; Implemented &lt;solution&gt; that reduced &lt;time/cost&gt; by &lt;X%&gt;.\n"
                                    "&bull; Collaborated with &lt;team/stakeholders&gt; to deliver &lt;outcome&gt;; validated via &lt;metric&gt;.\n"
                                    "&bull; Documented results and created &lt;artifact/report&gt; for visibility."
                                    "</div>"
                                    "<div class='tpl-tips'>&#128161; Tip: Start bullets with action verbs and end with measurable outcomes.</div>"
                                    "</div>"
                                ).format(role=role_for_tpl, skills=role_skills)
                                st.markdown(tpl_html, unsafe_allow_html=True)

                        # --- Summary Template ---
                        if not sp.get('summary'):
                            with st.expander("\U0001F9FE Add Summary / Objective Template", expanded=False):
                                tpl2_html = (
                                    "<div class='tpl-card'>"
                                    "<div class='tpl-head'>Professional Summary</div>"
                                    "<div class='tpl-tags'>"
                                    "<span class='tpl-tag'>{role}</span>"
                                    "<span class='tpl-tag'>{skills}</span>"
                                    "</div>"
                                    "<div class='tpl-pre'>"
                                    "Aspiring {role} with hands-on experience in {skills}. "
                                    "Strong foundation in data-driven problem solving and delivering measurable results.\n"
                                    "Looking to contribute to &lt;team/company&gt; by &lt;how you will add value&gt;, "
                                    "backed by &lt;projects/certifications&gt;."
                                    "</div>"
                                    "<div class='tpl-tips'>&#128161; Tip: Keep it concise (2&ndash;3 sentences); include strengths and target role.</div>"
                                    "</div>"
                                ).format(role=role_for_tpl, skills=role_skills)
                                st.markdown(tpl2_html, unsafe_allow_html=True)


                # Role Alignment Analysis (moved below Top Suggestions)
                if 'kw_role_alignment' in components:
                    st.markdown("""
                    <style>
                    .role-wrap { background: linear-gradient(145deg, #0b1221, #151c30); border:1px solid rgba(255,255,255,0.06); border-radius:20px; padding:16px 18px; margin: 10px 0 20px; box-shadow:0 10px 30px rgba(0,0,0,.35); }
                    .role-head { display:flex; flex-direction:column; gap:4px; }
                    .role-title { color:#E6EAF3; font-size:20px; font-weight:800; margin:0; }
                    .role-sub { color:#9AA4B2; font-size:13px; }
                    .chipset { display:flex; gap:8px; flex-wrap:wrap; margin-top:10px; }
                    .chip { display:inline-flex; align-items:center; gap:.45rem; padding:.5rem .75rem; border-radius:14px; font-size:12px; font-weight:800; border:1px solid rgba(255,255,255,.08); color:#E6EAF3; background: linear-gradient(145deg, rgba(255,255,255,.06), rgba(255,255,255,.03)); transition: transform .15s ease, box-shadow .15s ease; }
                    .chip:hover { transform: translateY(-1px); box-shadow: 0 8px 18px rgba(99,102,241,.18); }
                    .high { background: linear-gradient(145deg, rgba(16,185,129,.25), rgba(16,185,129,.10)); border-color: rgba(16,185,129,.35); color:#CFFAE3; }
                    .med { background: linear-gradient(145deg, rgba(45,212,191,.22), rgba(34,197,94,.10)); border-color: rgba(45,212,191,.35); color:#D1FAF0; }
                    .low { background: linear-gradient(145deg, rgba(148,163,184,.16), rgba(148,163,184,.06)); border-color: rgba(148,163,184,.35); color:#E5E7EB; }
                    .tag { display:inline-flex; align-items:center; gap:.35rem; padding:.35rem .6rem; border-radius:999px; font-size:12px; font-weight:800; color:#9EC5FF; border:1px solid rgba(59,130,246,.35); background: rgba(59,130,246,.10); }
                    </style>
                    """, unsafe_allow_html=True)

                    role_label = ''
                    if role == 'Auto-detect':
                        auto_role = components.get('kw_role_alignment_role')
                        if auto_role:
                            role_label = f"<span class='tag'>Auto-detected: {auto_role}</span>"
                    else:
                        role_label = f"<span class='tag'>Target: {role}</span>"

                    top_roles = components.get('kw_role_alignment_top') or []
                    icon_map = { 'Software Engineer':'💻', 'Data Analyst':'📊', 'Machine Learning Engineer':'🤖', 'Web Developer':'🌐' }

                    chips = []
                    for r in top_roles:
                        role_name = r.get('role') or 'Role'
                        score8 = r.get('score') or 0
                        level = 'high' if score8 >= 6 else ('med' if score8 >= 4 else 'low')
                        icon = icon_map.get(role_name, '🧩')
                        title = ', '.join(r.get('keywords', []))
                        chips.append(f"<span class='chip {level}' title='{title}'>{icon} {role_name} • {score8}/8</span>")

                    st.markdown(
                        f"""
                        <div class='role-wrap fade-in'>
                            <div class='role-head'>
                                <div class='role-title'>Role Alignment Analysis</div>
                                <div class='role-sub'>Based on extracted skills and keyword matches. {role_label}</div>
                            </div>
                            <div class='chipset'>{''.join(chips)}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Cache resume context for chat so first turn has context
                try:
                    st.session_state['resume_context'] = build_resume_context(resume_data)
                except Exception:
                    st.session_state['resume_context'] = None

                # Defer chat rendering to bottom of page
                st.session_state['render_chat_at_bottom'] = True
                
                # Spacer before job search section
                st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
                st.markdown("""
                <style>
                @keyframes slideInLeft {
                    0% { 
                        opacity: 0;
                        transform: translateX(-20px);
                    }
                    100% { 
                        opacity: 1;
                        transform: translateX(0px);
                    }
                }
                
                .job-search-section {
                    background: linear-gradient(135deg, #1A1F3A 0%, #242F5C 50%, #1A1F3A 100%);
                    border: 1.5px solid rgba(99, 102, 241, 0.3);
                    border-radius: 20px;
                    padding: 24px 30px;
                    margin: 20px 0 15px 0;
                    box-shadow: 0 10px 40px rgba(99, 102, 241, 0.12), 0 0 20px rgba(99, 102, 241, 0.05);
                    position: relative;
                }
                </style>
                """, unsafe_allow_html=True)

                # ── Opportunities section header ──────────────────────────────────
                st.markdown("""
                <div id="opportunities-section" style="
                    display: flex; align-items: center; gap: 14px;
                    margin: 0.5rem 0 1.5rem 0;
                    padding-bottom: 14px;
                    border-bottom: 1px solid rgba(255,255,255,0.06);
                ">
                    <div style="
                        width: 4px; height: 40px; border-radius: 4px;
                        background: linear-gradient(180deg, #6366f1, #a78bfa);
                    "></div>
                    <div>
                        <div style="font-size: 1.35rem; font-weight: 700; color: #f1f5f9; letter-spacing: -0.4px;">
                            Opportunities
                        </div>
                        <div style="font-size: 0.82rem; color: #64748b; margin-top: 2px;">
                            Matching jobs and internships based on your resume
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                # ── Search bar ────────────────────────────────────────────────────
                def _default_keywords(skills_list, comps):
                    role_name = None
                    try:
                        role_name = (comps.get('kw_role_alignment_role') or None) if comps else None
                        if not role_name and comps and comps.get('kw_role_alignment_top'):
                            role_name = comps['kw_role_alignment_top'][0].get('role')
                    except Exception:
                        role_name = None
                    tech_stop = {"sales","marketing","operations","hr","human resources","business development"}
                    sk = [s for s in (skills_list or []) if isinstance(s, str) and s.strip() and s.strip().lower() not in tech_stop]
                    def _is_tech(x: str):
                        t = x.lower()
                        return any(k in t for k in ["python","java","react","node","sql","ml","data","django","flask","frontend","backend","devops","cloud","android","ios","c++","c#","go","rust","pandas","numpy","streamlit"])
                    tech_sk = [s for s in sk if _is_tech(s)] or sk
                    parts = ([role_name] if role_name else []) + tech_sk
                    return ", ".join([p for p in parts if p][:3])

                default_kw = _default_keywords(skills, components)
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    keywords_input = st.text_input("Skills / Keywords", value=default_kw, placeholder="e.g., Python, React, SQL", key="search_keywords")
                with col2:
                    location_input = st.text_input("Location", placeholder="City, country, or leave blank", key="search_location")
                with col3:
                    st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
                    search_button = st.button("Search", width='stretch', key="opp_search_btn")

                # Display recommendations
                if skills:
                    predicted_cat = resume_data.get('predicted_category')
                    display_job_recommendations_dual(skills, keywords_input, location_input or "India", predicted_cat)
                # Category-based course recommendations
                predicted_cat = resume_data.get('predicted_category')
                course_list = []
                
                if predicted_cat:
                    # Get courses based on ML predicted category
                    category_courses = get_courses_by_category(predicted_cat)
                    course_list.extend(category_courses)
                
                # Fallback: skill-based recommendations if no category or no courses
                if not course_list:
                    if any(skill.lower() in ['python', 'pandas', 'numpy', 'machine learning', 'data analysis'] for skill in skills):
                        course_list.extend(ds_course)
                    if any(skill.lower() in ['html', 'css', 'javascript', 'react'] for skill in skills):
                        course_list.extend(web_course)
                    if any(skill.lower() in ['kotlin', 'java', 'android'] for skill in skills):
                        course_list.extend(android_course)
                    if any(skill.lower() in ['swift', 'ios'] for skill in skills):
                        course_list.extend(ios_course)
                    if any(skill.lower() in ['figma', 'ui/ux', 'prototyping'] for skill in skills):
                        course_list.extend(uiux_course)
                
                recommended_courses: list = []
                if course_list:
                    # Spacer before courses section
                    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
                    recommended_courses = course_recommender(course_list)
                
                # Save to database (only once per resume upload)
                # Use a combination of resume file identity + email to prevent duplicates
                if resume_data.get('name') and resume_data.get('email'):
                    # Create a unique key based on resume identity and user email
                    resume_id = st.session_state.get('resume_id', '')
                    user_email = resume_data.get('email', '')
                    resume_db_key = f"db_saved_{hash(resume_id + user_email)}"
                    
                    # Only insert if we haven't saved this specific resume for this user
                    if resume_id and not st.session_state.get(resume_db_key, False):
                        timestamp = datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')
                        success = db_manager.insert_user_data(
                            name=resume_data['name'],
                            email=resume_data['email'],
                            res_score=score,
                            timestamp=timestamp,
                            no_of_pages=1,  # Default
                            reco_field="General",
                            cand_level="Intermediate",
                            skills=skills,
                            recommended_skills=[],
                            courses=recommended_courses
                        )
                        if success:
                            # Mark this resume as saved to prevent duplicates on subsequent reruns
                            st.session_state[resume_db_key] = True

        # Spacer before AI chat section
        st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)
        
        # Render chat at the very bottom
        if st.session_state.get('render_chat_at_bottom'):
            # === STYLE BLOCK ===
            st.markdown("""
            <style>
            /* === CONTAINER === */
            .assistant-container {
                background: linear-gradient(145deg, rgba(255,255,255,0.03), rgba(0,0,0,0.25));
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 18px;
                padding: 28px 36px;
                margin-top: 50px;
                margin-bottom: 40px;
                box-shadow: 0 8px 25px rgba(0,0,0,0.35);
                transition: all 0.3s ease;
            }
            .assistant-container:hover {
                box-shadow: 0 10px 32px rgba(0,0,0,0.45);
            }

            /* === HEADER === */
            .assistant-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                background: rgba(255,255,255,0.05);
                border: 1px solid rgba(255,255,255,0.08);
                border-radius: 14px;
                padding: 14px 18px;
                margin-bottom: 15px;
                box-shadow: inset 0 0 0 1px rgba(255,255,255,0.02), 0 6px 20px rgba(0,0,0,0.25);
            }
            .assistant-title {
                display: flex;
                align-items: center;
                gap: 10px;
                font-weight: 700;
                font-size: 1.25rem;
                color: #e5e7eb;
                letter-spacing: 0.3px;
            }
            .assistant-status {
                color: #22c55e;
                font-size: 0.9rem;
                animation: pulse 1.8s infinite;
            }
            @keyframes pulse { 0%{opacity:1;} 50%{opacity:0.6;} 100%{opacity:1;} }

            /* === CHAT AREA === */
            .chat-scroll {
                max-height: 500px;
                overflow-y: auto;
                padding: 15px;
                background: rgba(255,255,255,0.02);
                border-radius: 14px;
                margin-bottom: 16px;
            }
            .chat-scroll::-webkit-scrollbar {
                width: 6px;
            }
            .chat-scroll::-webkit-scrollbar-thumb {
                background: rgba(255,255,255,0.08);
                border-radius: 10px;
            }

            /* === MESSAGE BUBBLES === */
            .message-container {
                display: flex;
                flex-direction: column;
                margin-bottom: 12px;
            }
            .message-user { align-items: flex-end; }
            .message-assistant { align-items: flex-start; }
            .message-bubble {
                padding: 12px 16px;
                border-radius: 16px;
                max-width: 80%;
                word-wrap: break-word;
                font-size: 0.95rem;
                line-height: 1.6;
                animation: fadeIn 0.3s ease-in-out;
            }
            .message-bubble p { margin: 0 0 8px 0; }
            .message-bubble p:last-child { margin-bottom: 0; }
            .message-bubble ul, .message-bubble ol { margin: 0 0 8px 0; padding-left: 20px; }
            .message-bubble li { margin-bottom: 4px; }
            .message-bubble strong { font-weight: 600; color: #fff; }
            .message-bubble em { font-style: italic; opacity: 0.9; }
            .user {
                background: linear-gradient(135deg, #6366f1, #0ea5e9);
                color: #fff;
                border-bottom-right-radius: 4px;
                text-align: right;
                margin-left: auto;
            }
            .assistant {
                background: rgba(255,255,255,0.08);
                color: #e2e8f0;
                border-bottom-left-radius: 4px;
                text-align: left;
            }
            @keyframes fadeIn { from {opacity: 0; transform: translateY(6px);} to {opacity: 1; transform: translateY(0);} }

            .message-time {
                font-size: 0.75rem;
                color: rgba(255,255,255,0.4);
                margin-top: 2px;
            }

            /* === INPUT AREA === */
            .chat-input {
                background: rgba(255,255,255,0.04);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 16px;
                padding: 10px 14px;
                display: flex;
                align-items: center;
                justify-content: space-between;
                gap: 8px;
            }
            .chat-input input {
                background: transparent;
                color: white;
                border: none;
                width: 100%;
                outline: none;
            }
            .stButton>button {
                border-radius: 12px !important;
                background: linear-gradient(90deg, #7c3aed, #2dd4bf);
                border: none;
                color: white;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            .stButton>button:hover {
                transform: scale(1.05);
                box-shadow: 0 0 12px rgba(124,58,237,0.4);
            }

            /* === TYPING ANIMATION === */
            .typing-indicator {
                display: flex;
                align-items: center;
                gap: 8px;
                color: rgba(255,255,255,0.7);
                font-size: 0.9rem;
            }
            .typing-dots {
                display: flex;
                gap: 4px;
            }
            .typing-dot {
                width: 6px;
                height: 6px;
                background: #9ca3af;
                border-radius: 50%;
                animation: blink 1.4s infinite both;
            }
            .typing-dot:nth-child(2){animation-delay:0.2s;}
            .typing-dot:nth-child(3){animation-delay:0.4s;}
            @keyframes blink { 0%{opacity:0.2;} 20%{opacity:1;} 100%{opacity:0.2;} }
            </style>
            """, unsafe_allow_html=True)

            # === MAIN ASSISTANT CONTAINER START ===
            st.markdown('<div id="chat-section" class="assistant-container">', unsafe_allow_html=True)

            # HEADER
            st.markdown("""
            <div class="assistant-header" style="
                display: flex; justify-content: space-between; align-items: center;
                background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
                border-radius: 12px; padding: 16px 20px; margin-bottom: 20px;
            ">
                <div class="assistant-title" style="display: flex; align-items: center; gap: 12px;">
                    <div style="
                        width: 38px; height: 38px; border-radius: 50%;
                        background: linear-gradient(135deg, #6366f1, #8b5cf6);
                        display: flex; align-items: center; justify-content: center;
                        box-shadow: 0 0 12px rgba(99, 102, 241, 0.3);
                    ">
                        <span style="font-size: 1.25rem;">🤖</span>
                    </div>
                    <div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: #f1f5f9; letter-spacing: -0.3px; line-height: 1.2;">
                            InternHunt Assistant
                        </div>
                        <div style="font-size: 0.75rem; color: #94a3b8; font-weight: 500; margin-top: 2px;">
                            AI Career Coach
                        </div>
                    </div>
                </div>
                <div style="
                    display: flex; align-items: center; gap: 6px;
                    padding: 4px 10px; border-radius: 999px;
                    background: rgba(16, 185, 129, 0.08);
                    border: 1px solid rgba(16, 185, 129, 0.25);
                    color: #34d399; font-size: 0.75rem; font-weight: 700;
                ">
                    <span style="width: 6px; height: 6px; border-radius: 50%; background: #10b981;"></span>
                    Online
                </div>
            </div>
            """, unsafe_allow_html=True)

            # CHAT STYLE / OPTIONS
            col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
            with col1:
                chat_style = st.selectbox("Style", ["Concise", "Detailed", "Short"], index=0, key="chat_style")
            with col2:
                st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
                st.session_state['chat_use_context'] = st.checkbox("Use resume context", value=True, key="chat_use_ctx")
            with col3:
                st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
                clear_btn = st.button("🗑️ Clear", key="chat_clear", width='stretch')
            with col4:
                st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
                test_btn = st.button("🔥 Test", key="chat_test", width='stretch')

            if clear_btn:
                st.session_state['chat_messages'] = []
                st.toast("Chat cleared!")
                st.rerun()

            if test_btn:
                with st.spinner("Testing AI connection..."):
                    try:
                        health = check_gemini_health()
                        if health['status'] == 'healthy' and health['api_key_configured']:
                            _ = chat_gemini([{ "role": "user", "content": "Hello"}], None, "Respond with 'Ready to help!'")
                            st.success("AI connection working! 🚀")
                        else:
                            st.error(f"AI not ready: {health.get('error', 'Unknown error')}")
                    except Exception as e:
                        st.error(f"Failed to connect: {e}")

            # CHAT HISTORY CONTAINER
            chat_container = st.container(height=450)
            
            if 'chat_messages' not in st.session_state:
                st.session_state['chat_messages'] = []
            
            with chat_container:
                for m in st.session_state['chat_messages'][-50:]:
                    role = m.get('role', 'user')
                    content = m.get('content', '')
                    with st.chat_message(role):
                        st.markdown(content)
            st.markdown('</div>', unsafe_allow_html=True)

            # CHAT INPUT & PROCESSING
            user_text = st.chat_input("Ask me anything about your resume, career, or job search...")
            if user_text:
                # 1. Append user message
                timestamp = datetime.datetime.now().strftime("%H:%M")
                st.session_state['chat_messages'].append({
                    "role": "user",
                    "content": user_text,
                    "timestamp": timestamp
                })
                # Set reply request flag
                st.session_state['assistant_should_reply'] = True
                # Rerun immediately to paint user message on screen
                st.rerun()

            # 2. Check if assistant needs to reply
            if st.session_state.get('assistant_should_reply'):
                context = st.session_state.get('resume_context') if st.session_state.get('chat_use_context', True) else None
                if chat_style == "Concise":
                    sys = "Be brief and friendly. Give 2-3 quick tips in plain language."
                elif chat_style == "Detailed":
                    sys = "Give helpful advice in a conversational tone. Include 3-4 specific recommendations."
                else:
                    sys = "Answer in 2-3 natural sentences like you're helping a friend."

                with chat_container:
                    with st.chat_message("assistant"):
                        with st.spinner("Thinking..."):
                            try:
                                reply = chat_gemini(
                                    st.session_state['chat_messages'], 
                                    resume_context=context, 
                                    system_prompt=sys
                                )
                                if reply:
                                    st.session_state['chat_messages'].append({
                                        "role": "assistant",
                                        "content": reply,
                                        "timestamp": datetime.datetime.now().strftime("%H:%M")
                                    })
                            except Exception as e:
                                st.session_state['chat_messages'].append({
                                    "role": "assistant",
                                    "content": f"⚠️ Failed to get reply: {e}",
                                    "timestamp": datetime.datetime.now().strftime("%H:%M")
                                })
                # Clear reply flag and rerun to complete rendering
                st.session_state['assistant_should_reply'] = False
                st.rerun()

        elif choice == 'Admin':
            # Admin auth gate
            if not Config.ADMIN_PASSWORD:
                st.markdown("""
                <div style="background:rgba(239,68,68,0.08); border:1px solid rgba(239,68,68,0.3); border-radius:12px; padding:20px 24px; margin-top:24px;">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <span style="font-size:22px;">⚠️</span>
                        <div>
                            <div style="font-weight:700; color:#FCA5A5; font-size:15px;">Admin Portal Not Configured</div>
                            <div style="color:#94A3B8; font-size:13px; margin-top:4px;">Set <code style='background:rgba(255,255,255,0.08);padding:2px 6px;border-radius:4px;'>ADMIN_PASSWORD</code> in your <code style='background:rgba(255,255,255,0.08);padding:2px 6px;border-radius:4px;'>.env</code> file and restart the app.</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            elif not st.session_state.get('admin_authenticated'):

                # ══════════════════════════════════════════════════════════
                # CSS — Page background, animations, form overrides
                # ══════════════════════════════════════════════════════════
                st.markdown("""
                <style>
                /* ── Page-level background ── */
                [data-testid="stAppViewContainer"] > .main {
                    background: radial-gradient(ellipse 80% 60% at 20% 0%, rgba(99,102,241,0.12) 0%, transparent 60%),
                                radial-gradient(ellipse 60% 50% at 80% 100%, rgba(139,92,246,0.10) 0%, transparent 55%),
                                #0B1120 !important;
                }

                /* ── Entrance animation ── */
                @keyframes fadeUp {
                    from { opacity: 0; transform: translateY(18px); }
                    to   { opacity: 1; transform: translateY(0); }
                }
                @keyframes glowPulse {
                    0%, 100% { box-shadow: 0 0 40px rgba(99,102,241,0.12); }
                    50%      { box-shadow: 0 0 70px rgba(99,102,241,0.22); }
                }
                .admin-login-left  { animation: fadeUp 0.5s ease both; }
                .admin-login-right { animation: fadeUp 0.5s ease 0.12s both; }

                /* ── Form: glass card (bottom half) ── */
                [data-testid="stForm"]:has(input[data-testid="stTextInputRootElement"]) {
                    background: rgba(17,24,39,0.7) !important;
                    backdrop-filter: blur(20px) !important;
                    -webkit-backdrop-filter: blur(20px) !important;
                    border: 1px solid rgba(99,102,241,0.18) !important;
                    border-top: none !important;
                    border-radius: 0 0 24px 24px !important;
                    padding: 24px 36px 36px !important;
                    margin-top: -1px !important;
                    box-shadow: none !important;
                }

                /* ── Text input ── */
                [data-testid="stTextInputRootElement"] input {
                    background: rgba(255,255,255,0.04) !important;
                    border: 1.5px solid rgba(99,102,241,0.2) !important;
                    border-radius: 12px !important;
                    color: #F8FAFC !important;
                    font-size: 14px !important;
                    height: 48px !important;
                    padding: 0 16px !important;
                    transition: border-color 0.2s, box-shadow 0.2s !important;
                }
                [data-testid="stTextInputRootElement"] input:focus {
                    border-color: #6366F1 !important;
                    box-shadow: 0 0 0 3px rgba(99,102,241,0.15) !important;
                    outline: none !important;
                }
                [data-testid="stTextInputRootElement"] input::placeholder {
                    color: #475569 !important;
                }

                /* ── Submit button ── */
                [data-testid="stFormSubmitButton"] > button {
                    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%) !important;
                    border: none !important;
                    border-radius: 12px !important;
                    font-weight: 700 !important;
                    font-size: 15px !important;
                    height: 50px !important;
                    letter-spacing: 0.3px !important;
                    color: #fff !important;
                    transition: transform 0.18s, box-shadow 0.18s !important;
                    box-shadow: 0 4px 20px rgba(99,102,241,0.35) !important;
                }
                [data-testid="stFormSubmitButton"] > button:hover {
                    transform: translateY(-2px) !important;
                    box-shadow: 0 8px 32px rgba(99,102,241,0.5) !important;
                }
                [data-testid="InputInstructions"] { display: none !important; }
                </style>
                """, unsafe_allow_html=True)

                # ══════════════════════════════════════════════════════════
                # Two-column layout  45% | 55%
                # ══════════════════════════════════════════════════════════
                left_col, right_col = st.columns([9, 11])

                # ─────────────────── LEFT HERO ────────────────────────────
                with left_col:
                    st.markdown("""
                    <div class="admin-login-left" style="padding: 8px 0 0; min-height: 540px;">

                      <div style="display:flex; align-items:center; gap:10px; margin-bottom:28px;">
                        <div style="
                            width:36px; height:36px;
                            background: linear-gradient(135deg,#6366F1,#8B5CF6);
                            border-radius:10px;
                            display:flex; align-items:center; justify-content:center;
                            font-size:18px;
                            box-shadow: 0 4px 14px rgba(99,102,241,0.4);
                        ">🎯</div>
                        <span style="font-size:15px; font-weight:800; color:#F8FAFC; letter-spacing:0.2px;">InternHunt</span>
                        <span style="
                            font-size:10px; font-weight:700; color:#A78BFA;
                            background: rgba(99,102,241,0.12);
                            border: 1px solid rgba(99,102,241,0.25);
                            border-radius:20px; padding:3px 10px;
                            letter-spacing:1px; text-transform:uppercase;
                        ">Admin</span>
                      </div>

                      <h1 style="
                          font-size:32px; font-weight:800; color:#F8FAFC;
                          line-height:1.2; margin:0 0 14px;
                          letter-spacing:-0.5px;
                      ">Admin Intelligence<br><span style="color:#818CF8;">Portal</span></h1>

                      <p style="
                          font-size:14px; color:#64748B; line-height:1.75;
                          margin:0 0 36px; max-width:340px;
                      ">Secure access to candidate analytics, recruiter insights, resume database, AI recommendations and platform monitoring.</p>

                      <div style="
                          display:grid; grid-template-columns:1fr 1fr;
                          gap:12px; margin-bottom:20px;
                          filter: blur(4px); opacity:0.45;
                          pointer-events:none; user-select:none;
                      ">
                        <div style="background:rgba(30,42,69,0.6); border:1px solid rgba(99,102,241,0.15); border-radius:14px; padding:16px 18px;">
                          <div style="font-size:11px; font-weight:700; color:#6366F1; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">Applications Today</div>
                          <div style="font-size:28px; font-weight:800; color:#F8FAFC; line-height:1;">152</div>
                          <div style="font-size:11px; color:#10B981; margin-top:4px;">↑ +12 from yesterday</div>
                        </div>
                        <div style="background:rgba(30,42,69,0.6); border:1px solid rgba(99,102,241,0.15); border-radius:14px; padding:16px 18px;">
                          <div style="font-size:11px; font-weight:700; color:#6366F1; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">Registered Candidates</div>
                          <div style="font-size:28px; font-weight:800; color:#F8FAFC; line-height:1;">23,482</div>
                          <div style="font-size:11px; color:#A78BFA; margin-top:4px;">Platform total</div>
                        </div>
                        <div style="background:rgba(30,42,69,0.6); border:1px solid rgba(99,102,241,0.15); border-radius:14px; padding:16px 18px;">
                          <div style="font-size:11px; font-weight:700; color:#6366F1; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">Resume Match Accuracy</div>
                          <div style="font-size:28px; font-weight:800; color:#F8FAFC; line-height:1;">94<span style="font-size:16px; color:#64748B;">%</span></div>
                          <div style="font-size:11px; color:#10B981; margin-top:4px;">↑ +2% this week</div>
                        </div>
                        <div style="background:rgba(30,42,69,0.6); border:1px solid rgba(99,102,241,0.15); border-radius:14px; padding:16px 18px;">
                          <div style="font-size:11px; font-weight:700; color:#6366F1; text-transform:uppercase; letter-spacing:1px; margin-bottom:6px;">AI Recommendations</div>
                          <div style="font-size:28px; font-weight:800; color:#F8FAFC; line-height:1;">1,284</div>
                          <div style="font-size:11px; color:#A78BFA; margin-top:4px;">Generated this month</div>
                        </div>
                      </div>

                      <div style="
                          background:rgba(17,24,39,0.5); border:1px solid rgba(255,255,255,0.05);
                          border-radius:14px; padding:16px 20px;
                          filter: blur(4px); opacity:0.4;
                          pointer-events:none; user-select:none;
                      ">
                        <div style="font-size:11px; font-weight:700; color:#475569; text-transform:uppercase; letter-spacing:1px; margin-bottom:12px;">Recent Activity</div>
                        <div style="display:flex; flex-direction:column; gap:9px;">
                          <div style="display:flex; align-items:center; gap:10px;">
                            <div style="width:6px; height:6px; border-radius:50%; background:#6366F1; flex-shrink:0;"></div>
                            <span style="font-size:12px; color:#94A3B8;">Resume uploaded by candidate</span>
                          </div>
                          <div style="display:flex; align-items:center; gap:10px;">
                            <div style="width:6px; height:6px; border-radius:50%; background:#10B981; flex-shrink:0;"></div>
                            <span style="font-size:12px; color:#94A3B8;">New internship posted</span>
                          </div>
                          <div style="display:flex; align-items:center; gap:10px;">
                            <div style="width:6px; height:6px; border-radius:50%; background:#A78BFA; flex-shrink:0;"></div>
                            <span style="font-size:12px; color:#94A3B8;">Candidate shortlisted</span>
                          </div>
                          <div style="display:flex; align-items:center; gap:10px;">
                            <div style="width:6px; height:6px; border-radius:50%; background:#F59E0B; flex-shrink:0;"></div>
                            <span style="font-size:12px; color:#94A3B8;">Analytics report updated</span>
                          </div>
                        </div>
                      </div>


                      <div style="display:flex; align-items:center; gap:8px; margin-top:20px;">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#475569" stroke-width="2" stroke-linecap="round"><rect x="3" y="11" width="18" height="11" rx="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
                        <span style="font-size:12px; color:#475569;">Stats locked until authenticated</span>
                      </div>

                    </div>
                    """, unsafe_allow_html=True)

                # ─────────────────── RIGHT AUTH PANEL ─────────────────────
                with right_col:
                    st.markdown("""
                    <div class="admin-login-right" style="padding: 8px 0 0;">
                      <div style="
                          background: rgba(17,24,39,0.75);
                          backdrop-filter: blur(24px);
                          -webkit-backdrop-filter: blur(24px);
                          border: 1px solid rgba(99,102,241,0.2);
                          border-bottom: none;
                          border-radius: 24px 24px 0 0;
                          padding: 44px 36px 32px;
                          box-shadow: 0 -8px 60px rgba(99,102,241,0.08);
                      ">
                        <div style="
                            width:64px; height:64px;
                            background: linear-gradient(135deg,#6366F1 0%,#8B5CF6 100%);
                            border-radius:18px;
                            display:flex; align-items:center; justify-content:center;
                            margin-bottom:24px;
                            box-shadow: 0 8px 24px rgba(99,102,241,0.45), 0 0 0 8px rgba(99,102,241,0.07);
                        ">
                          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                        </div>
                        <h2 style="font-size:24px; font-weight:800; color:#F8FAFC; margin:0 0 8px; letter-spacing:-0.4px;">Administrator Login</h2>
                        <p style="font-size:13px; color:#64748B; margin:0; line-height:1.7;">Authentication required to access InternHunt<br>analytics and candidate data.</p>
                        <div style="height:1px; background:linear-gradient(90deg,transparent,rgba(99,102,241,0.2),transparent); margin:28px 0 0;"></div>
                      </div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Streamlit form renders as the seamless card bottom
                    with st.form("admin_login_form", enter_to_submit=True):
                        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
                        pw = st.text_input(
                            "Password",
                            type="password",
                            key="admin_pw_input",
                            label_visibility="collapsed",
                            placeholder="Enter admin password..."
                        )
                        st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
                        submitted = st.form_submit_button("Access Dashboard →", type="primary", width="stretch")
                        if submitted:
                            if pw == Config.ADMIN_PASSWORD:
                                st.session_state.admin_authenticated = True
                                st.rerun()
                            else:
                                st.markdown("""
                                <div style="
                                    display:flex; align-items:center; gap:10px;
                                    background:rgba(239,68,68,0.08);
                                    border:1px solid rgba(239,68,68,0.22);
                                    border-radius:10px; padding:12px 16px; margin-top:14px;
                                ">
                                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#FCA5A5" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                                    <span style="font-size:13px; color:#FCA5A5; font-weight:500;">Incorrect password — access denied</span>
                                </div>
                                """, unsafe_allow_html=True)

                    st.markdown("""
                    <div style="text-align:center; margin-top:20px;">
                        <span style="font-size:11px; color:#334155;">
                            🔐 &nbsp;256-bit encrypted session &nbsp;·&nbsp; InternHunt v2.0
                        </span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # ── Page header ───────────────────────────────────────────
                st.markdown("""
                <div style="display:flex; align-items:center; justify-content:space-between; margin-bottom:32px;">
                    <div style="display:flex; align-items:center; gap:14px;">
                        <div style="width:4px; height:40px; border-radius:4px; background:linear-gradient(180deg,#6366F1,#8B5CF6);"></div>
                        <div>
                            <h2 style="font-size:22px; font-weight:800; color:#F1F5F9; margin:0; letter-spacing:-0.3px;">Admin Analytics Portal</h2>
                            <p style="font-size:13px; color:#64748B; margin:3px 0 0;">System reporting, candidate insights and data export</p>
                        </div>
                    </div>
                    <div style="background:rgba(16,185,129,0.1); border:1px solid rgba(16,185,129,0.25); border-radius:8px; padding:6px 14px; font-size:12px; font-weight:600; color:#10B981; letter-spacing:0.5px;">● LIVE</div>
                </div>
                """, unsafe_allow_html=True)

                # Fetch user logs
                try:
                    user_data = db_manager.get_user_data(limit=1000)
                except Exception as e:
                    st.error(f"Database connection failed: {e}")
                    user_data = None

                if user_data:
                    df = pd.DataFrame(user_data, columns=[
                        'ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Pages',
                        'Predicted Field', 'User Level', 'Skills', 'Recommended Skills', 'Courses'
                    ])

                    # Safe casting/parsing of score/pages
                    df['Score_num'] = pd.to_numeric(df['Resume Score'], errors='coerce')
                    df['Score_num'] = df['Score_num'].fillna(0.0)
                    df['Pages_num'] = pd.to_numeric(df['Pages'], errors='coerce')
                    df['Pages_num'] = df['Pages_num'].fillna(1.0)

                    # Tabs
                    tab_analytics, tab_database = st.tabs(["📈 System Analytics", "👥 Candidate Registry"])

                    with tab_analytics:
                        total_users = len(df)
                        avg_score   = df['Score_num'].mean()
                        top_role    = df['Predicted Field'].mode()
                        top_role_str = top_role[0] if not top_role.empty else "N/A"
                        avg_pages   = df['Pages_num'].mean()

                        # ── KPI Cards ────────────────────────────────────────
                        st.markdown(f"""
                        <div style="
                            display: grid;
                            grid-template-columns: repeat(4, 1fr);
                            gap: 16px;
                            margin-bottom: 36px;
                        ">
                            <div class="saas-kpi-card">
                                <div style="font-size:10px; font-weight:700; color:#A78BFA; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:10px;">Total Resumes</div>
                                <div style="font-size:32px; font-weight:800; color:#F8FAFC; line-height:1;">{total_users}</div>
                                <div style="font-size:11px; color:#64748B; margin-top:8px; font-weight:500;">All uploaded candidates</div>
                            </div>
                            <div class="saas-kpi-card">
                                <div style="font-size:10px; font-weight:700; color:#A78BFA; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:10px;">Avg ATS Score</div>
                                <div style="font-size:32px; font-weight:800; color:#F8FAFC; line-height:1;">{avg_score:.1f}<span style='font-size:18px; color:#64748B;'>%</span></div>
                                <div style="font-size:11px; color:#64748B; margin-top:8px; font-weight:500;">Platform average</div>
                            </div>
                            <div class="saas-kpi-card">
                                <div style="font-size:10px; font-weight:700; color:#A78BFA; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:10px;">Top Field</div>
                                <div style="font-size:18px; font-weight:800; color:#F8FAFC; line-height:1.2; margin-top:4px; overflow:hidden; white-space:nowrap; text-overflow:ellipsis;">{top_role_str}</div>
                                <div style="font-size:11px; color:#64748B; margin-top:8px; font-weight:500;">Across database</div>
                            </div>
                            <div class="saas-kpi-card">
                                <div style="font-size:10px; font-weight:700; color:#A78BFA; text-transform:uppercase; letter-spacing:1.2px; margin-bottom:10px;">Avg Pages</div>
                                <div style="font-size:32px; font-weight:800; color:#F8FAFC; line-height:1;">{avg_pages:.1f}</div>
                                <div style="font-size:11px; color:#64748B; margin-top:8px; font-weight:500;">Per resume</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # ── Section divider ───────────────────────────────────
                        st.markdown("""
                        <div style="display:flex; align-items:center; gap:12px; margin-bottom:24px;">
                            <div style="font-size:15px; font-weight:700; color:#F1F5F9; letter-spacing:-0.2px;">Distribution Analytics</div>
                            <div style="flex:1; height:1px; background:rgba(255,255,255,0.06);"></div>
                        </div>
                        """, unsafe_allow_html=True)

                        chart_col1, chart_col2 = st.columns(2)

                        with chart_col1:
                            st.markdown("""
                            <div style="background:#090D16; border:1px solid rgba(255,255,255,0.06);
                                        border-radius:14px; padding:16px 18px; margin-bottom:4px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
                                <div style="font-size:13px; font-weight:700; color:#CBD5E1;">Career Field Distribution</div>
                                <div style="font-size:11px; color:#475569; margin-top:2px;">Predicted field across all resumes</div>
                            </div>
                            """, unsafe_allow_html=True)
                            field_counts = df['Predicted Field'].value_counts().reset_index()
                            field_counts.columns = ['Field', 'Count']
                            
                            fig_fields = px.pie(
                                field_counts,
                                names="Field",
                                values="Count",
                                hole=0.7,
                                color_discrete_sequence=['#818CF8', '#A78BFA', '#C084FC', '#E9D5FF', '#F3E8FF']
                            )
                            fig_fields.add_annotation(
                                text=f"<span style='font-size:26px; font-weight:800; color:#F8FAFC;'>{total_users}</span><br><span style='font-size:9px; font-weight:600; color:#64748B; text-transform:uppercase; letter-spacing:0.5px;'>Resumes</span>",
                                x=0.5, y=0.5,
                                showarrow=False,
                                font=dict(family="Inter, sans-serif")
                            )
                            fig_fields.update_layout(
                                paper_bgcolor="rgba(0,0,0,0)",
                                plot_bgcolor="rgba(0,0,0,0)",
                                font=dict(family="Inter, sans-serif", color="#CBD5E1"),
                                showlegend=True,
                                legend=dict(
                                    orientation="v",
                                    yanchor="middle",
                                    y=0.5,
                                    xanchor="left",
                                    x=0.95,
                                    font=dict(size=10)
                                ),
                                margin=dict(t=10, b=10, l=10, r=10),
                                height=320,
                            )
                            fig_fields.update_traces(
                                textposition='inside',
                                textinfo='none',
                                hoverinfo='label+value',
                                hoverlabel=dict(bgcolor="#0F172A", font_size=11, font_family="Inter, sans-serif")
                            )
                            st.plotly_chart(fig_fields, use_container_width=True, config={'displayModeBar': False})

                        with chart_col2:
                            st.markdown("""
                            <div style="background:#090D16; border:1px solid rgba(255,255,255,0.06);
                                        border-radius:14px; padding:16px 18px; margin-bottom:4px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
                                <div style="font-size:13px; font-weight:700; color:#CBD5E1;">Top Technical Skills</div>
                                <div style="font-size:11px; color:#475569; margin-top:2px;">Most common skills detected across uploaded resumes</div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Parse skills dynamically from the dataframe
                            all_skills = []
                            for skills_str in df['Skills'].dropna():
                                if skills_str:
                                    all_skills.extend([s.strip() for s in str(skills_str).split(',') if s.strip()])
                            
                            if all_skills:
                                skills_series = pd.Series(all_skills).value_counts().head(10).reset_index()
                                skills_series.columns = ['Skill', 'Frequency']
                                
                                fig_skills = px.bar(
                                    skills_series,
                                    x="Frequency",
                                    y="Skill",
                                    orientation="h",
                                    color="Skill",
                                    color_discrete_sequence=px.colors.sequential.Purples_r,
                                )
                                fig_skills.update_traces(
                                    texttemplate='%{x}',
                                    textposition='outside',
                                    marker=dict(line=dict(width=1, color="rgba(255,255,255,0.05)")),
                                    hoverlabel=dict(bgcolor="#0F172A", font_size=11, font_family="Inter, sans-serif")
                                )
                                fig_skills.update_layout(
                                    paper_bgcolor="rgba(0,0,0,0)",
                                    plot_bgcolor="rgba(0,0,0,0)",
                                    font=dict(family="Inter, sans-serif", color="#CBD5E1"),
                                    showlegend=False,
                                    xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.05)", tickformat=",d"),
                                    yaxis=dict(showgrid=False, categoryorder="total ascending"),
                                    margin=dict(t=10, b=10, l=10, r=20),
                                    height=320,
                                )
                                st.plotly_chart(fig_skills, use_container_width=True, config={'displayModeBar': False})
                            else:
                                st.markdown("""
                                <div style="background:rgba(99,102,241,0.02); border:1px dashed rgba(99,102,241,0.15);
                                            border-radius:12px; height:320px; display:flex; flex-direction:column;
                                            align-items:center; justify-content:center; padding:20px;">
                                    <div style="font-size:2rem; margin-bottom:8px;">📊</div>
                                    <div style="font-size:13px; font-weight:600; color:#64748B;">No skills detected yet</div>
                                </div>
                                """, unsafe_allow_html=True)

                        # ── ATS Score Distribution ────────────────────────────
                        st.markdown("""
                        <div style="background:#090D16; border:1px solid rgba(255,255,255,0.06);
                                    border-radius:14px; padding:16px 18px; margin:24px 0 4px; box-shadow: 0 4px 20px rgba(0,0,0,0.15);">
                            <div style="font-size:13px; font-weight:700; color:#CBD5E1;">Score Insights</div>
                            <div style="font-size:11px; color:#475569; margin-top:2px;">Candidate quality bracket breakdown</div>
                        </div>
                        """, unsafe_allow_html=True)

                        def get_bucket(val):
                            if val <= 40: return "0-40% (Poor)"
                            if val <= 60: return "41-60% (Average)"
                            if val <= 80: return "61-80% (Good)"
                            return "81-100% (Excellent)"

                        df['Score_Range'] = df['Score_num'].apply(get_bucket)
                        bucket_order = ["0-40% (Poor)", "41-60% (Average)", "61-80% (Good)", "81-100% (Excellent)"]
                        score_counts = df['Score_Range'].value_counts().reindex(bucket_order).fillna(0).reset_index()
                        score_counts.columns = ['Score Bracket', 'Candidates Count']

                        fig_scores = px.bar(
                            score_counts,
                            x="Score Bracket",
                            y="Candidates Count",
                            color="Score Bracket",
                            color_discrete_sequence=["#EF4444", "#F59E0B", "#10B981", "#8B5CF6"]
                        )
                        fig_scores.update_traces(
                            marker=dict(line=dict(width=1, color="rgba(255,255,255,0.05)")),
                            hoverlabel=dict(bgcolor="#0F172A", font_size=11, font_family="Inter, sans-serif")
                        )
                        fig_scores.update_layout(
                            paper_bgcolor="rgba(0,0,0,0)",
                            plot_bgcolor="rgba(0,0,0,0)",
                            font=dict(family="Inter, sans-serif", color="#CBD5E1"),
                            showlegend=False,
                            xaxis=dict(showgrid=False),
                            yaxis=dict(
                                showgrid=True,
                                gridcolor="rgba(255,255,255,0.05)",
                                tickformat=",d"
                            ),
                            margin=dict(t=15, b=15, l=15, r=15),
                            height=260,
                        )
                        st.plotly_chart(fig_scores, use_container_width=True, config={'displayModeBar': False})

                    with tab_database:
                        # ── Filter bar ───────────────────────────────────────
                        st.markdown("""
                        <div style="display:flex; align-items:center; gap:12px; margin-bottom:20px;">
                            <div style="font-size:15px; font-weight:700; color:#F1F5F9; letter-spacing:-0.2px;">Candidate Registry</div>
                            <div style="flex:1; height:1px; background:rgba(255,255,255,0.06);"></div>
                        </div>
                        """, unsafe_allow_html=True)

                        f_col1, f_col2, f_col3 = st.columns([2, 1, 1])
                        with f_col1:
                            search_q = st.text_input("Search", value="", placeholder="Search by name or email...", key="admin_search", label_visibility="collapsed")
                        with f_col2:
                            fields_list = ["All Fields"] + sorted(list(df['Predicted Field'].dropna().unique()))
                            selected_field = st.selectbox("Field", fields_list, index=0, key="admin_field_filter", label_visibility="collapsed")
                        with f_col3:
                            levels_list = ["All Levels"] + sorted(list(df['User Level'].dropna().unique()))
                            selected_level = st.selectbox("Level", levels_list, index=0, key="admin_level_filter", label_visibility="collapsed")

                        min_score_filter = st.slider(
                            "Minimum ATS Score", min_value=0, max_value=100, value=0, step=5,
                            key="admin_score_filter"
                        )

                        # Apply Filters
                        filtered_df = df.copy()
                        if search_q.strip():
                            q = search_q.strip().lower()
                            filtered_df = filtered_df[
                                filtered_df['Name'].str.lower().str.contains(q, na=False) |
                                filtered_df['Email'].str.lower().str.contains(q, na=False)
                            ]
                        if selected_field != "All Fields":
                            filtered_df = filtered_df[filtered_df['Predicted Field'] == selected_field]
                        if selected_level != "All Levels":
                            filtered_df = filtered_df[filtered_df['User Level'] == selected_level]
                        filtered_df = filtered_df[filtered_df['Score_num'] >= min_score_filter]

                        display_df = filtered_df.drop(columns=['Score_num', 'Pages_num', 'Score_Range'], errors='ignore')

                        st.markdown(f"""
                        <div style="font-size:12px; color:#64748B; font-weight:600; margin:12px 0 12px;">
                            {len(display_df)} candidate{'s' if len(display_df) != 1 else ''} match your filters
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # --- Custom HTML Table Registry & Pagination ---
                        if not display_df.empty:
                            RECORDS_PER_PAGE = 10
                            if 'admin_page_num' not in st.session_state:
                                st.session_state.admin_page_num = 1
                                
                            total_pages = max(1, (len(display_df) + RECORDS_PER_PAGE - 1) // RECORDS_PER_PAGE)
                            if st.session_state.admin_page_num > total_pages:
                                st.session_state.admin_page_num = total_pages
                            if st.session_state.admin_page_num < 1:
                                st.session_state.admin_page_num = 1
                                
                            start_idx = (st.session_state.admin_page_num - 1) * RECORDS_PER_PAGE
                            end_idx = start_idx + RECORDS_PER_PAGE
                            paginated_df = display_df.iloc[start_idx:end_idx]
                            
                            def get_field_badge(field):
                                if not field or pd.isna(field) or str(field).lower() == 'nan':
                                    return '<span class="category-badge">General</span>'
                                return f'<span class="category-badge">{field}</span>'

                            def get_level_badge(level):
                                if not level or pd.isna(level) or str(level).lower() == 'nan':
                                    return '<span class="status-badge status-entry">Entry / Student</span>'
                                lvl_str = str(level).strip()
                                if "Senior" in lvl_str:
                                    return f'<span class="status-badge status-senior">{lvl_str}</span>'
                                elif "Mid" in lvl_str:
                                    return f'<span class="status-badge status-mid">{lvl_str}</span>'
                                else:
                                    return f'<span class="status-badge status-entry">{lvl_str}</span>'

                            def get_skills_pills(skills_str):
                                if not skills_str or pd.isna(skills_str) or str(skills_str).lower() == 'nan':
                                    return '<div class="skills-wrap"></div>'
                                skills = [s.strip() for s in str(skills_str).split(",") if s.strip()]
                                pills = [f'<span class="skill-pill">{s}</span>' for s in skills[:8]]
                                if len(skills) > 8:
                                    pills.append(f'<span class="skill-pill" style="opacity: 0.75; border-style: dashed;">+{len(skills) - 8} more</span>')
                                return f'<div class="skills-wrap">{" ".join(pills)}</div>'

                            def get_score_progress(score_str):
                                try:
                                    score_val = int(float(score_str))
                                except Exception:
                                    score_val = 0
                                return f"""
                                <div class="progress-container">
                                    <div class="progress-bar-wrap">
                                        <div class="progress-bar-fill" style="width: {score_val}%;"></div>
                                    </div>
                                    <span class="progress-text">{score_val}%</span>
                                </div>
                                """

                            table_rows = []
                            for _, row in paginated_df.iterrows():
                                name = str(row['Name']) if pd.notna(row['Name']) else "Unknown"
                                email = str(row['Email']) if pd.notna(row['Email']) else ""
                                field_badge = get_field_badge(row['Predicted Field'])
                                level_badge = get_level_badge(row['User Level'])
                                skills_pills = get_skills_pills(row['Skills'])
                                score_progress = get_score_progress(row['Resume Score'])
                                timestamp = str(row['Timestamp']) if pd.notna(row['Timestamp']) else ""
                                
                                table_rows.append(f"""
                                <tr>
                                    <td>
                                        <div class="candidate-name">{name}</div>
                                        <div class="candidate-email">{email}</div>
                                    </td>
                                    <td>{score_progress}</td>
                                    <td>{level_badge}</td>
                                    <td>{field_badge}</td>
                                    <td>{skills_pills}</td>
                                    <td><span class="timestamp-text">{timestamp}</span></td>
                                </tr>
                                """)

                            table_html = f"""
                            <div class="table-container">
                                <table class="saas-table">
                                    <thead>
                                        <tr>
                                            <th>Candidate</th>
                                            <th>ATS Score</th>
                                            <th>User Level</th>
                                            <th>Predicted Field</th>
                                            <th>Extracted Skills</th>
                                            <th>Timestamp</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {"".join(table_rows)}
                                    </tbody>
                                </table>
                            </div>
                            """
                            st.markdown(table_html, unsafe_allow_html=True)
                            
                            # Render custom pagination wrapper
                            st.markdown("<div class='pagination-wrapper'>", unsafe_allow_html=True)
                            pg_col1, pg_col2, pg_col3, pg_col4, pg_col5 = st.columns([3, 1, 1, 1, 3])
                            with pg_col2:
                                if st.button("Previous", disabled=(st.session_state.admin_page_num == 1), key="btn_prev_page"):
                                    st.session_state.admin_page_num -= 1
                                    st.rerun()
                            with pg_col3:
                                st.markdown(f"<div style='text-align:center; padding-top:6px; font-size:13px; font-weight:600; color:#94A3B8;'>Page {st.session_state.admin_page_num} / {total_pages}</div>", unsafe_allow_html=True)
                            with pg_col4:
                                if st.button("Next", disabled=(st.session_state.admin_page_num == total_pages), key="btn_next_page"):
                                    st.session_state.admin_page_num += 1
                                    st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)
                        else:
                            st.markdown("""
                            <div style="background:rgba(239,68,68,0.03); border:1px dashed rgba(239,68,68,0.15);
                                        border-radius:12px; padding:32px; text-align:center; margin-top:16px;">
                                <div style="font-size:2rem; margin-bottom:8px;">🔍</div>
                                <div style="font-size:14px; font-weight:600; color:#94A3B8;">No candidates match filters</div>
                                <div style="font-size:12px; color:#475569; margin-top:4px;">Adjust your sliders or fields to view registry logs.</div>
                            </div>
                            """, unsafe_allow_html=True)

                        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
                        download_csv_data = display_df.to_csv(index=False)
                        st.download_button(
                            label="📥 Export as CSV",
                            data=download_csv_data,
                            file_name="candidate_registry.csv",
                            mime="text/csv",
                            key="admin_download_btn"
                        )
                else:
                    st.markdown("""
                    <div style="background:rgba(99,102,241,0.06); border:1px solid rgba(99,102,241,0.15);
                                border-radius:12px; padding:32px; text-align:center; margin-top:24px;">
                        <div style="font-size:2rem; margin-bottom:12px;">📭</div>
                        <div style="font-size:15px; font-weight:600; color:#94A3B8;">No candidate records yet</div>
                        <div style="font-size:13px; color:#475569; margin-top:6px;">Upload and analyze a resume to start populating the registry.</div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # ============ FOOTER ============ 
    st.markdown(""" 
        <footer style="text-align: center; margin-top: 80px; font-size: 
    0.9rem; opacity: 0.7; font-family: 'Inter', sans-serif;
    color: #94a3b8; padding: 20px 0;">
                        © 2025 InternHunt • Crafted with ❤️ by Shubham, Abhinav, Pragya & Parmesh
                </footer> 
                """,unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
