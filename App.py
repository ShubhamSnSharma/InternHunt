# This will show us the current contents of App.py so we can analyze it
import streamlit as st
import pandas as pd
import base64, random
import time, datetime
import io, os
import json
import requests
from PIL import Image
from streamlit_tags import st_tags
import pymysql
from Courses import ds_course, web_course, android_course, ios_course

# import spacy
import pyresparser.resume_parser as resume_parser
#############
# App.py
# A lightweight, pyresparser-free resume parser for PDF files using spaCy + simple rules.
# Works on Python 3.11+ (including 3.13) as long as spaCy's small English model is available.

import io
import re
from typing import List, Dict, Any

import streamlit as st

# ---- Dependencies kept minimal: spacy + pypdf ----
# pip install spacy pypdf streamlit
# python -m spacy download en_core_web_sm
import spacy
from pypdf import PdfReader
from spacy.matcher import PhraseMatcher

# -----------------------------
# Utilities
# -----------------------------
@st.cache_resource(show_spinner=False)
def load_spacy():
    """Load spaCy model, auto-install if missing."""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        # Try to download model on the fly (works if internet allowed)
        import subprocess, sys
        try:
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            return spacy.load("en_core_web_sm")
        except Exception:
            st.error("spaCy model 'en_core_web_sm' is not installed and could not be downloaded automatically.")
            raise

def read_pdf_text(uploaded_file) -> str:
    """Extract raw text from uploaded PDF (Streamlit UploadedFile)."""
    # pypdf needs a file-like object
    file_bytes = uploaded_file.read()
    reader = PdfReader(io.BytesIO(file_bytes))
    pages = []
    for p in reader.pages:
        try:
            pages.append(p.extract_text() or "")
        except Exception:
            pages.append("")
    text = "\n".join(pages)
    # Normalize whitespace
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def first_nonempty_lines(text: str, n: int = 8) -> List[str]:
    lines = [ln.strip() for ln in text.splitlines()]
    lines = [ln for ln in lines if ln]
    return lines[:n]

# -----------------------------
# Rule-based Extractors
# -----------------------------
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
PHONE_RE = re.compile(
    r"(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}|\d{5}[\s\-]?\d{5})"
)
URL_RE = re.compile(r"\b(?:https?://|www\.)[^\s<>)+]+", re.I)
GITHUB_RE = re.compile(r"github\.com/[A-Za-z0-9_.\-]+", re.I)
LINKEDIN_RE = re.compile(r"(?:linkedin\.com/in/|linkedin\.com/pub/)[A-Za-z0-9\-\_/%]+", re.I)

DEGREE_WORDS = [
    "bachelor", "masters", "master", "b.tech", "btech", "m.tech", "mtech", "b.e", "be", "bsc", "msc",
    "phd", "doctorate", "mba", "bs", "ba", "ms", "mca", "bca", "bcom", "mcom", "bba", "mse", "m.eng",
    "b.eng", "bachelor of", "master of", "associate", "diploma"
]
DEGREE_RE = re.compile(r"|".join([re.escape(d) for d in DEGREE_WORDS]), re.I)
YEAR_RE = re.compile(r"(20|19)\d{2}")

# A not-too-huge general skills set (add/remove as you like)
SKILLS = {
    # Programming languages
    "python","java","javascript","typescript","c","c++","c#","go","rust","kotlin","swift","ruby","php","r","matlab","scala",
    # Web / frameworks
    "html","css","react","next.js","nextjs","angular","vue","svelte","node.js","nodejs","express","django","flask","fastapi","spring","spring boot","laravel","rails",
    # Data / ML / AI
    "pandas","numpy","scikit-learn","sklearn","tensorflow","keras","pytorch","nlp","computer vision","opencv","xgboost","lightgbm","matplotlib","seaborn","plotly",
    # Databases / cloud / devops
    "sql","mysql","postgresql","sqlite","mongodb","redis","elasticsearch","aws","gcp","azure","docker","kubernetes","git","github","gitlab","ci/cd","terraform",
    # Mobile
    "android","ios","react native","swiftui","flutter",
    # Testing / others
    "pytest","jest","cypress","playwright","graphql","rest","grpc","microservices"
}
# Normalize skills variants
SKILL_SYNONYMS = {
    "nextjs": "next.js",
    "nodejs": "node.js",
    "spring boot": "spring boot",
}

def build_skill_matcher(nlp):
    phrases = list(SKILLS)
    patterns = [nlp.make_doc(p) for p in phrases]
    matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
    matcher.add("SKILL", patterns)
    return matcher

def extract_name(doc) -> str | None:
    # Heuristic: Use first PERSON entity in top lines; else guess from top tokens
    top_text = "\n".join(first_nonempty_lines(doc.text, n=5))
    top_doc = doc.from_bytes(top_text.encode("utf-8"))
    persons = [ent.text.strip() for ent in top_doc.ents if ent.label_ == "PERSON"]
    if persons:
        # Prefer a 2- or 3-token name
        persons.sort(key=lambda s: (abs(len(s.split())-2), -len(s)))
        return persons[0]
    # Fallback: first line with 2-4 capitalized words
    for ln in first_nonempty_lines(doc.text, n=5):
        tokens = ln.split()
        cap_words = [w for w in tokens if re.match(r"^[A-Z][a-zA-Z'\-]+$", w)]
        if 1 < len(cap_words) <= 4:
            return " ".join(cap_words)
    return None

def extract_contacts(text: str) -> Dict[str, Any]:
    emails = list(dict.fromkeys(EMAIL_RE.findall(text)))
    phones = list(dict.fromkeys(PHONE_RE.findall(text)))
    urls = list(dict.fromkeys(URL_RE.findall(text)))

    # Pull special links if present
    gh = list(dict.fromkeys(GITHUB_RE.findall(text)))
    li = list(dict.fromkeys(LINKEDIN_RE.findall(text)))

    # Normalize URLs (add scheme if missing)
    def norm(u: str) -> str:
        u = u.strip().strip(").,;")
        if u.startswith("www."):
            return "https://" + u
        if not u.startswith("http"):
            # assume already bare path like github.com/user
            return "https://" + u
        return u

    urls = [norm(u) for u in urls]
    gh = [norm(u) for u in gh]
    li = [norm(u) for u in li]

    return {
        "emails": emails,
        "phones": phones,
        "urls": urls,
        "github": gh,
        "linkedin": li
    }

def extract_skills(doc, matcher) -> List[str]:
    matches = matcher(doc)
    found = []
    for _, start, end in matches:
        span = doc[start:end].text.strip().lower()
        # normalize variants
        span = SKILL_SYNONYMS.get(span, span)
        found.append(span)
    # de-dup, preserve order
    deduped = []
    seen = set()
    for s in found:
        if s not in seen:
            deduped.append(s)
            seen.add(s)
    return deduped

def extract_education(text: str) -> List[str]:
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    edu_lines = []
    # Section-based pull
    section_idxs = []
    for i, ln in enumerate(lines):
        if re.search(r"\beducation|qualifications|academics?\b", ln, re.I):
            section_idxs.append(i)
    grabbed = []
    for idx in section_idxs:
        # take next ~10 lines after a section header
        grabbed.extend(lines[idx: idx+12])
    if not grabbed:
        grabbed = lines
    # Filter for degree keywords or school-like terms
    for ln in grabbed:
        if DEGREE_RE.search(ln) or re.search(r"(university|college|institute|school)", ln, re.I):
            # add year context if present
            yr = YEAR_RE.findall(ln)
            edu_lines.append(ln if ln.endswith(tuple(yr)) else ln)
    # de-dup & keep reasonable length lines
    out, seen = [], set()
    for l in edu_lines:
        if l.lower() not in seen and len(l) < 200:
            out.append(l)
            seen.add(l.lower())
    return out[:12]

def extract_experience(text: str) -> List[str]:
    # Very lightweight: pull lines around "Experience/Work/Employment"
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    indices = []
    for i, ln in enumerate(lines):
        if re.search(r"\b(experience|employment|work history|professional experience)\b", ln, re.I):
            indices.append(i)
    bullets = []
    for idx in indices or [0]:
        chunk = lines[idx: idx+40]  # next ~40 lines
        for ln in chunk:
            if ln.startswith(("-", "•", "*")) or re.search(r"\b(20\d{2}|19\d{2})\b", ln):
                bullets.append(ln)
    # keep unique, readable chunks
    out, seen = [], set()
    for b in bullets:
        b = re.sub(r"^\s*[-•*]\s*", "", b).strip()
        if b.lower() not in seen and 10 <= len(b) <= 220:
            out.append(b)
            seen.add(b.lower())
    return out[:30]

def extract_summary(doc) -> str | None:
    # Grab first 3-5 sentences as a short summary/objective if present near top.
    sents = [s.text.strip() for s in doc.sents if s.text.strip()]
    if not sents:
        return None
    top = sents[:5]
    # Prefer lines that contain keywords like objective/summary/profile
    for s in top:
        if re.search(r"\b(objective|summary|profile|about)\b", s, re.I):
            return s
    # fallback: first sentence
    return sents[0] if sents else None

def parse_resume(text: str, nlp, matcher) -> Dict[str, Any]:
    doc = nlp(text)
    name = extract_name(doc)
    contacts = extract_contacts(text)
    skills = extract_skills(doc, matcher)
    education = extract_education(text)
    experience = extract_experience(text)
    summary = extract_summary(doc)

    return {
        "name": name,
        "summary": summary,
        "emails": contacts["emails"],
        "phones": contacts["phones"],
        "linkedin": contacts["linkedin"],
        "github": contacts["github"],
        "other_urls": [u for u in contacts["urls"] if u not in contacts["github"] + contacts["linkedin"]],
        "skills": skills,
        "education": education,
        "experience_points": experience
    }

# -----------------------------
# UI
# -----------------------------
def main():
    st.set_page_config(page_title="Resume Parser (spaCy)", page_icon="🧾", layout="centered")
    st.title("🧾 Resume Parser (no pyresparser)")

    st.caption("Upload a **PDF resume**. This app extracts name, contact info, skills, education, and experience using spaCy + rule-based patterns.")

    uploaded = st.file_uploader("Upload resume (PDF)", type=["pdf"], accept_multiple_files=False)
    if not uploaded:
        st.info("Tip: PDFs with actual text (not just scanned images) work best. For scanned PDFs, run OCR first.")
        return

    with st.spinner("Reading PDF..."):
        text = read_pdf_text(uploaded)

    if not text:
        st.error("Couldn't extract text from this PDF. If it's scanned, please OCR it and try again.")
        return

    nlp = load_spacy()
    matcher = build_skill_matcher(nlp)

    with st.spinner("Analyzing resume with spaCy..."):
        data = parse_resume(text, nlp, matcher)

    # ---------------- Display ----------------
    st.subheader("Extracted Profile")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Name:**", data.get("name") or "—")
        st.write("**Email(s):**", ", ".join(data["emails"]) if data["emails"] else "—")
        st.write("**Phone(s):**", ", ".join(data["phones"]) if data["phones"] else "—")
    with col2:
        st.write("**LinkedIn:**", ", ".join(data["linkedin"]) if data["linkedin"] else "—")
        st.write("**GitHub:**", ", ".join(data["github"]) if data["github"] else "—")
        st.write("**Other Links:**", ", ".join(data["other_urls"]) if data["other_urls"] else "—")

    if data.get("summary"):
        st.write("**Summary / Objective:**")
        st.info(data["summary"])

    st.write("---")
    st.subheader("Skills")
    if data["skills"]:
        st.write(", ".join(sorted(set([s.title() for s in data["skills"]]))))
    else:
        st.write("—")

    st.write("---")
    st.subheader("Education")
    if data["education"]:
        for line in data["education"]:
            st.write(f"- {line}")
    else:
        st.write("—")

    st.write("---")
    st.subheader("Experience Highlights")
    if data["experience_points"]:
        for pt in data["experience_points"]:
            st.write(f"- {pt}")
    else:
        st.write("—")

    with st.expander("Show raw extracted text"):
        st.text_area("Text", value=text, height=300)

if __name__ == "__main__":
    main()



##############
resume_parser.spacy.load = lambda name: spacy.load("en_core_web_sm")

# NLTK setup
import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

# Ensure spaCy model is installed BEFORE importing pyresparser
import spacy
import subprocess
import sys

try:
    spacy.load("en_core_web_sm")
except OSError:
    print("Downloading spaCy model 'en_core_web_sm'...")
    subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
    spacy.load("en_core_web_sm")  # Load after installing

from pyresparser import ResumeParser  # Import only after model is ready

# Setting Streamlit page config early
st.set_page_config(
    page_title="InternHunt - Your Internship Finder",
    page_icon='Logo/InternHunt_logo.png',
    layout="wide",
)

# Initialize theme if not already set
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "dark"

# Toggle switch
theme = st.toggle("🌙 Dark Mode" if st.session_state.theme_mode == "light" else "☀️ Light Mode")

# Update theme based on toggle
st.session_state.theme_mode = "light" if theme else "dark"

def apply_theme(mode):
    if mode == "dark":
        st.markdown("""
            <style>
            body {
                background-color: #0f172a;
                color: #ffffff;
            }
            .stApp {
                background-color: #0f172a;
                color: #ffffff;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
            body {
                background-color: #f8fafc;
                color: #111827;
            }
            .stApp {
                background-color: #f8fafc;
                color: #111827;
            }
            </style>
        """, unsafe_allow_html=True)

# Apply the theme
apply_theme(st.session_state.theme_mode)


from ui import add_custom_css, add_footer

# Add CSS
add_custom_css()

# Smooth scroll behavior
st.markdown("""
    <style>
        html {
            scroll-behavior: smooth;
        }
    </style>
""", unsafe_allow_html=True)


query_params = st.query_params

# Inject custom CSS
st.markdown("""
    <style>
        .topnav {
            background-color: rgba(0, 0, 0, 0);
            overflow: hidden;
            padding: 10px 20px;
            display: flex;
            justify-content: flex-end;
            align-items: center;
            gap: 20px;
            position: fixed;
            top: 0;
            width: 100%;
            z-index: 1000;
        }
        .topnav a {
            color: #f2f2f2;
            text-decoration: none;
            font-size: 16px;
            padding: 8px 12px;
            border-radius: 5px;
            transition: background-color 0.3s ease;
        }

        .topnav a:hover {
            background-color: #00796b;
        }

        .theme-toggle {
            padding: 5px 10px;
            background-color: #00695c;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 14px;
            cursor: pointer;
        }

        .theme-toggle:hover {
            background-color: #00897b;
        }
    </style>

    <div class="topnav">
        <a href="#contact">Contact</a>
        <a href="#privacy">Privacy</a>
        <form action="#" method="get" style="margin: 0;">
            <button class="theme-toggle" onclick="document.location.reload()">
                Toggle Theme
            </button>
        </form>
    </div>
""", unsafe_allow_html=True)

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True

# Apply theme styling dynamically
if st.session_state.dark_mode:
    st.markdown("""
        <style>
            body { background-color: #0E1117; color: white; }
            .container { background: linear-gradient(135deg, #1a1a1a, #2e2e2e); color: white; }
            .main-title, .subtitle, .upload-instructions {
                color: white !important;
            }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
            body { background-color: white; color: black; }
            .container { background: linear-gradient(135deg, #e0f2f1, #ffffff); color: black; }
            .main-title, .subtitle, .upload-instructions {
                color: black !important;
            }
        </style>
        .header-section {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: linear-gradient(135deg, #e0f2f1, #ffffff);
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
            margin: 5rem auto 2rem auto;  /* Push down because of fixed top nav */
            max-width: 900px;
        }

        .text-content {
            flex: 1;
            text-align: left;
        }

        .logo-image img {
            border-radius: 12px;
            max-width: 150px;
        }
    """, unsafe_allow_html=True)


# Display the header
st.markdown("""
    <div style="text-align: center; margin-bottom: 0;">
        <h1 style="font-size: 3em; margin-bottom: 0.2rem;">InternHunt</h1>
        <h3 style="color: #ccc; margin-top: 0;">Resume Analyzer</h3>
        <p style="color: #aaa; font-size: 1.1em;">
            Upload your resume and get smart internship recommendations based on your skills.
        </p>
    </div>
""", unsafe_allow_html=True)

# Add padding to avoid navbar overlap
st.markdown("<br><br><br><br><br><br><br><br>", unsafe_allow_html=True)

import nltk
from resume_parser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
import yt_dlp as youtube_dl
import plotly.express as px
from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos

nltk.download('stopwords')

# Download necessary NLTK resources if not already present
nltk_data_path = os.path.join(os.path.expanduser("~"), "nltk_data")
if not os.path.exists(os.path.join(nltk_data_path, "corpora/stopwords")):
    nltk.download("stopwords", download_dir=nltk_data_path)

# Set NLTK data path (helps Streamlit Cloud locate it)
nltk.data.path.append(nltk_data_path)

def fetch_yt_video(link):
    try:
        with youtube_dl.YoutubeDL({}) as ydl:
            info = ydl.extract_info(link, download=False)
            return info.get('title', 'Unknown Title')
    except Exception as e:
        return f"Error fetching video: {e}"


def get_table_download_link(df,filename,text):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # some strings <-> bytes conversions necessary here
    # href = f'<a href="data:file/csv;base64,{b64}">Download Report</a>'
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


def pdf_reader(file):
    from pdfminer.high_level import extract_text_to_fp
    from pdfminer.layout import LAParams
    from pdfminer.pdfinterp import PDFResourceManager
    from pdfminer.converter import TextConverter
    from pdfminer.pdfinterp import PDFPageInterpreter
    from pdfminer.pdfpage import PDFPage
    import io

    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    laparams = LAParams()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=laparams)
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    try:
        if isinstance(file, str):  # For file paths
            with open(file, "rb") as fh:
                for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
                    page_interpreter.process_page(page)
        else:  # For Streamlit UploadedFile
            with io.BytesIO(file.getbuffer()) as fh:
                for page in PDFPage.get_pages(fh, caching=True, check_extractable=True):
                    page_interpreter.process_page(page)
    except Exception as e:
        converter.close()
        fake_file_handle.close()
        return f"Error reading PDF: {str(e)}"

    text = fake_file_handle.getvalue()
    converter.close()
    fake_file_handle.close()
    return text


def show_pdf(file_path):
    import base64
    import os

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

st.markdown("""
    <style>
    /* Glowing header box */
    .glow-header {
        background-color: #0f172a;
        padding: 15px 25px;
        border-radius: 12px;
        box-shadow: 0 0 15px #3b82f6;
        color: #e0f2fe;
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        transition: 0.3s ease;
    }

    .glow-header:hover {
        box-shadow: 0 0 25px #60a5fa;
        transform: scale(1.02);
    }

    /* Course card styling */
    .course-card {
        background-color: #1e293b;
        border-radius: 12px;
        padding: 20px;
        margin: 10px 0;
        box-shadow: 0 0 10px rgba(34, 211, 238, 0.2);
        transition: 0.3s ease;
        color: #e2e8f0;
    }

    .course-card:hover {
        box-shadow: 0 0 20px rgba(34, 211, 238, 0.6);
        transform: scale(1.02);
        cursor: pointer;
    }
    </style>
""", unsafe_allow_html=True)


def course_recommender(course_list):
    st.markdown("""
        <div class="glow-header">
        Courses & Certificates Recommendations 🎓
        </div>
        <p style='color:#cbd5e1; text-align:center;'>✨ These handpicked courses will boost your skillset and career potential.</p>
        """, unsafe_allow_html=True)

    if not course_list:
        st.warning("No course recommendations available at the moment.")
        return []

    # Custom styled label above slider
    st.markdown("""
        <div style="margin-top: 10px; margin-bottom: -12px;">
            <span style="font-size: 15px; font-weight: 500; color: #f0f0f0;">
                🎯 <b>Select how many recommendations you want to explore:</b>
            </span>
        </div>
    """, unsafe_allow_html=True)

    no_of_reco = st.selectbox(
        "",
        options=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        index=4
    )
    
    st.markdown("""
    <style>
    .course-box {
        background: linear-gradient(145deg, #1a1a1a, #232323);
        padding: 20px;
        border-radius: 16px;
        margin-bottom: 20px;
        border: 1px solid #2e2e2e;
        box-shadow: 0 0 10px rgba(0, 255, 255, 0.2);
        transition: all 0.3s ease-in-out;
    }

    .course-box:hover {
        transform: scale(1.02);
        box-shadow: 0 0 25px rgba(0, 255, 255, 0.6);
    }

    .course-box a {
        color: #00eaff;
        text-decoration: none;
        display: block;  /* Makes the whole card clickable */
    }

    .course-box a:hover {
        text-decoration: none;
    }

    .course-sub {
        color: #bcbcbc;
        font-size: 13px;
        margin-top: 8px;
    }
    </style>
""", unsafe_allow_html=True)

    recommended_courses = random.sample(course_list, min(no_of_reco, len(course_list)))
    cols = st.columns(2)

    for idx, (c_name, c_link) in enumerate(recommended_courses):
        with cols[idx % 2]:
            st.markdown(f"""
                <div class="course-box">
                    <a href="{c_link}" target="_blank">
                        <h4>✅ {c_name}</h4>
                        <p class="course-sub">🔗 Tap to explore this course</p>
                    </a>
                </div>
            """, unsafe_allow_html=True)

    return [c_name for c_name, _ in recommended_courses]




# Jooble API credentials
import requests
import json

# Jooble API Key
JOOBLE_API_KEY = "4d4c75a1-1761-49c7-a003-71ed93beaf52"

def fetch_jobs_from_jooble(skills, location=""):
   
    url = f"https://jooble.org/api/{JOOBLE_API_KEY}"
    
    # Combine all skills into a single search query (e.g., "Python, Data Science, AI")
    keywords = ", ".join(skills)  # ✅ Using all skills together in one search

    payload = {
        "keywords": keywords,
        "location": location,  # Allows users to specify job location
        "page": 1
    }

    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            jobs = response.json().get("jobs", [])[:5]  # Get top 5 jobs
            return jobs if jobs else None
        else:
            return None  # No jobs found
    
    except Exception as e:
        return None  # Handle API errors



import requests
import streamlit as st

# Adzuna API Credentials
ADZUNA_APP_ID = "1178ed1c"
ADZUNA_API_KEY = "2e96a2f4573fff0502a2a081c21b6810"
ADZUNA_COUNTRY = "in"  # Change this based on the country you want

# Function to fetch job listings
def get_jobs_from_adzuna(skill, location="India", results=10):
    url = f"https://api.adzuna.com/v1/api/jobs/{ADZUNA_COUNTRY}/search/1"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_API_KEY,
        "results_per_page": results,
        "what": skill,  # Search based on skill
        "where": location,  # User-inputted location
    }

    response = requests.get(url, params=params)

    if response.status_code == 200:
        jobs = response.json()
        return jobs.get("results", [])  # Return list of job results
    else:
        st.error("⚠️ Failed to fetch jobs. Please check the location format.")
        return []


#CONNECT TO DATABASE

connection = pymysql.connect(host='localhost',user='root',password='Snamlien321',db='cv')
cursor = connection.cursor()

def insert_data(name, email, res_score, timestamp, no_of_pages, reco_field, cand_level, skills, recommended_skills, courses):
    if not connection.open:
        return

    insert_sql = """
    INSERT INTO user_data (Name, Email_ID, resume_score, Timestamp, Page_no, Predicted_Field, 
                           User_level, Actual_skills, Recommended_skills, Recommended_courses)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """  # ✅ Explicit column names

    rec_values = (
        name,
        email,
        str(res_score),
        timestamp,
        str(no_of_pages),
        reco_field,
        cand_level,
        ', '.join(skills),              # Must be str
        ', '.join(recommended_skills),  # Must be str
        ', '.join(courses)              # Must be str
    )

    try:
        cursor.execute(insert_sql, rec_values)
        connection.commit()
    except pymysql.MySQLError as e:
        st.error(f"Database Insert Error: {e}")

def run():
    st.markdown("""
        <style>
            .main-title {
                font-size: 3.5rem;
                font-weight: 700;
                color: #2c2c2c;
                text-align: center;
                margin-top: 1rem;
            }
            .subtitle {
                font-size: 1.5rem;
                color: #666;
                text-align: center;
                margin-top: -0.5rem;
            }
            .upload-instructions {
                font-size: 1rem;
                color: #28a745;
                text-align: center;
                margin-bottom: 2rem;
            }
            .container {
                background-color: #fff;
                padding: 2rem;
                border-radius: 1rem;
                box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
            }
        </style>
        </div>
    """, unsafe_allow_html=True)

    st.sidebar.markdown("# Choose User")
    activities = ["User", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    st.sidebar.markdown(
    """
    <p style='text-align: center; font-size: 12px;'>
        © Developed by 
        <a href='https://www.linkedin.com/in/shubham-sharma-163a962a9' target='_blank'>Shubham</a>, 
        <a href='https://www.linkedin.com/in/abhinav-ghangas-5a3b8128a' target='_blank'>Abhinav</a>, 
        <a href='https://www.linkedin.com/in/pragya-9974b1298' target='_blank'>Pragya</a>
    </p>
    """,
    unsafe_allow_html=True
)

    # Create the DB
    db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
    cursor.execute(db_sql)

    # Create table
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                     Name varchar(500) NOT NULL,
                     Email_ID VARCHAR(500) NOT NULL,
                     resume_score VARCHAR(8) NOT NULL,
                     Timestamp VARCHAR(50) NOT NULL,
                     Page_no VARCHAR(5) NOT NULL,
                     Predicted_Field BLOB NOT NULL,
                     User_level BLOB NOT NULL,
                     Actual_skills BLOB NOT NULL,
                     Recommended_skills BLOB NOT NULL,
                     Recommended_courses BLOB NOT NULL,
                     PRIMARY KEY (ID));
                    """
    cursor.execute(table_sql)
    import time

    if choice == 'User':
        st.markdown("""
            <style>
                .upload-box {
                    background-color: #1e1e30;
                    padding: 30px;
                    border-radius: 12px;
                    border: 1px solid #3e3e50;
                    margin-bottom: 25px;
                    max-width: 700px;
                    margin-left: auto;
                    margin-right: auto;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4);
                }
                .section-header {
                    font-size: 24px;
                    font-weight: 700;
                    color: #ffffff;
                    padding-bottom: 12px;
                    border-bottom: 1px solid #444;
                    margin-bottom: 20px;
                    font-family: 'Segoe UI', sans-serif;
                }
                .info-label {
                    font-weight: 600;
                    color: #bbbbbb;
                    margin-bottom: 3px;
                    font-size: 15px;
                }
                .info-value {
                    color: #f1f1f1;
                    font-size: 17px;
                    margin-bottom: 18px;
                    padding: 6px 12px;
                    background-color: #2c2c3e;
                    border-radius: 6px;
                    display: inline-block;
                    font-family: 'Segoe UI', sans-serif;
                }
                .sub-note {
                    color: #888;
                    font-size: 14px;
                    margin-top: -10px;
                    padding-left: 2px;
                }
            </style>

            <div class="upload-box">
                <div class="section-header">Upload Your Resume</div>
                <p class="sub-note">Supported format: PDF</p>
            </div>
        """, unsafe_allow_html=True)

        pdf_file = st.file_uploader(
            "Upload Resume", 
            type=["pdf"], 
            label_visibility="collapsed"  # Hides the label visually, but keeps it for accessibility
        )

        if pdf_file is not None:
            with st.spinner("Uploading and analyzing your resume..."):
                time.sleep(2)

            save_image_path = './Uploaded_Resumes/' + pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())

            show_pdf(save_image_path)

            resume_data = ResumeParser(save_image_path).get_extracted_data()


            if resume_data:
                resume_text = pdf_reader(save_image_path)

            st.markdown(f"""
            <style>
                .candidate-info-container {{
                    background-color: #1e1e2d;
                    border-radius: 10px;
                    padding: 24px;
                    margin-bottom: 30px;
                    border: 1px solid rgba(255, 255, 255, 0.08);
                    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
                    max-width: 500px;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;
                }}

                .candidate-info-container:hover {{
                    box-shadow: 0 6px 25px rgba(0, 0, 0, 0.4);
                    transform: scale(1.01);
                }}

                .greeting {{
                    font-size: 24px;
                    font-weight: 700;
                    color: #ffffff;
                    margin-bottom: 18px;
                }}

                .candidate-info-grid {{
                    display: grid;
                    grid-template-columns: 1fr;
                    gap: 15px;
                }}

                .info-item {{
                    display: flex;
                    flex-direction: column;
                    transition: transform 0.3s ease;
                }}

                .info-item:hover {{
                    transform: translateX(4px);
                }}

                .info-label {{
                    color: rgba(255, 255, 255, 0.6);
                    font-size: 13px;
                    margin-bottom: 4px;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                    font-weight: 500;
                }}

                .info-value {{
                    color: #ffffff;
                    font-size: 15px;
                    padding: 6px 12px;
                    background-color: rgba(255, 255, 255, 0.05);
                    border-radius: 6px;
                    border-left: 3px solid #6e8efb;
                    transition: background-color 0.3s ease;
                }}

                .info-item:hover .info-value {{
                    background-color: rgba(255, 255, 255, 0.08);
                }}
            </style>

            <div class="candidate-info-container">
                <div class="greeting">
                    Hello {resume_data.get('name', resume_data.get('candidate_name', 'there'))}
                </div>
                <div class="candidate-info-grid">
                    <div class="info-item">
                        <span class="info-label">Email Address</span>
                        <span class="info-value">{resume_data.get('email', resume_data.get('email_address', 'N/A'))}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Phone Number</span>
                        <span class="info-value">{resume_data.get('mobile_number', resume_data.get('phone', resume_data.get('contact', 'N/A')))}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


            
            from fuzzywuzzy import process, fuzz

            # Step 1: Raw text from resume
            resume_text = resume_text.lower()  # already loaded using pdf_reader()
            parser_skills = resume_data.get('skills', [])

            # Step 2: Clean and prepare valid skills
            VALID_SKILLS = {
                # Technical Skills
                'python', 'java', 'c++', 'c', 'c#', 'javascript', 'typescript', 'php', 'ruby', 'go', 'rust', 'swift', 
                'kotlin', 'html', 'css', 'sql', 'nosql', 'mongodb', 'mysql', 'postgresql', 'oracle', 'docker', 
                'kubernetes', 'aws', 'azure', 'google cloud', 'git', 'github', 'gitlab', 'bitbucket', 'react', 
                'angular', 'vue.js', 'node.js', 'express.js', 'django', 'flask', 'spring boot', 'tensorflow', 
                'pytorch', 'keras', 'scikit-learn', 'pandas', 'numpy', 'r', 'matlab', 'tableau', 'power bi', 
                'excel', 'linux', 'unix', 'windows', 'macos', 'shell scripting', 'bash', 'powershell', 'rest api', 
                'graphql', 'microservices', 'serverless', 'ci/cd', 'devops', 'agile', 'scrum',
                
                # Hardware/Electrical Engineering
                'verilog', 'vhdl', 'systemverilog', 'fpga', 'pcb design', 'circuit design', 'digital design', 
                'analog design', 'vlsi', 'asic', 'embedded systems', 'arm', 'msp430', 'pic', 'arduino', 
                'raspberry pi', 'cad', 'autocad', 'solidworks', 'spice', 'ltspice', 'xilinx', 'intel quartus', 
                'vivado', 'modelsim', 'planahead', 'magic', 'cadence', 'synopsys', 'signal processing', 
                'control systems', 'microcontrollers', 'microprocessors', 'computer architecture', 'rtos', 
                'bluetooth', 'wifi', 'rf design', 'power electronics', 'motor control', 'iot', 'xilinx ise',
                'bluespec', 'keil', 'eclipse', 'vlsi design', 'analog ic design', 'digital ic design',

                # Soft Skills
                'communication', 'leadership', 'teamwork', 'problem solving', 'critical thinking', 
                'time management', 'project management', 'decision making', 'negotiation', 'conflict resolution', 
                'adaptability', 'creativity', 'emotional intelligence', 'strategic planning', 'public speaking', 
                'technical writing', 'customer service', 'mentorship', 'coaching', 'analytical thinking', 
                'research', 'attention to detail', 'organization', 'self-motivation', 'interpersonal skills',

                # Data Science/Analytics
                'machine learning', 'deep learning', 'neural networks', 'data mining', 'data visualization', 
                'statistical analysis', 'predictive modeling', 'natural language processing', 'computer vision', 
                'reinforcement learning', 'a/b testing', 'regression analysis', 'classification', 'clustering', 
                'time series analysis', 'bayesian methods', 'feature engineering', 'dimensionality reduction', 
                'big data', 'hadoop', 'spark', 'etl', 'data warehousing', 'data cleaning', 'business intelligence',
                'data analysis', 'data structures', 'algorithms',

                # Design/Creative
                'adobe photoshop', 'adobe illustrator', 'adobe indesign', 'figma', 'sketch', 'ui design', 
                'ux design', 'graphic design', 'web design', 'typography', 'color theory', '3d modeling', 
                'animation', 'video editing', 'audio editing', 'content creation', 'wireframing', 
                'prototyping', 'user research', 'usability testing',

                # Business/Management
                'strategic planning', 'financial analysis', 'budgeting', 'risk management', 'market research', 
                'sales', 'marketing', 'digital marketing', 'seo', 'sem', 'social media marketing', 
                'content marketing', 'email marketing', 'crm', 'supply chain management', 'operations management', 
                'quality management', 'business development', 'contract negotiation', 'hr management', 
                'recruitment', 'performance management', 'training and development',
                
                # Additional specialized terms
                'rtl', 'circuit simulator', 'latex', 'test automation', 'cybersecurity', 'network security',
                'blockchain', 'cryptography', 'cloud computing', 'virtualization', 'shell', 'compiler design',
                'operating systems', 'parallel computing', 'distributed systems', 'web development',
                'mobile development', 'database administration', 'systems administration', 'network administration'
                }

            BANNED_SKILLS = {
                'email', 'presentation', 'matrix', 'international', 'hospitality', 'health', 'magic'
            }

            valid_skills_lower = {skill.lower(): skill for skill in VALID_SKILLS}
            valid_skill_list = list(valid_skills_lower.keys())

            fuzzy_threshold = 50
            found_skills = set()

            # Step 3: Search text using fuzzy matching
            for skill in valid_skill_list:
                # Exact phrase search (relaxed with basic formatting)
                if skill.replace("-", " ") in resume_text and skill not in BANNED_SKILLS:
                    found_skills.add(valid_skills_lower[skill])
                else:
                    # Fuzzy match from text chunks (helpful for near matches)
                    result = process.extractOne(skill, [resume_text], scorer=fuzz.token_set_ratio)
                    if result:
                        match, score = result
                        if score >= fuzzy_threshold:
                            found_skills.add(valid_skills_lower[skill])

            # Step 4: Add parser-based skills with fuzzy matching
            for skill in parser_skills:
                norm_skill = skill.lower().strip()
                if norm_skill in BANNED_SKILLS:
                    continue
                match, score = process.extractOne(norm_skill, valid_skill_list)
                if score >= fuzzy_threshold:
                    found_skills.add(valid_skills_lower[match])

            # Final result
            extracted_skills = list(found_skills)
      
           # ADD THIS NEW FUNCTION HERE
            def categorize_skills(extracted_skills):
                categories = {
                    "Technical Skills": [],
                    "Hardware/Electrical Engineering": [],
                    "Soft Skills": [],
                    "Data Science/Analytics": [],
                    "Design/Creative": [],
                    "Business/Management": []
                }
                
                # Define which skills belong to which category
                skill_categories = {
                    # Technical Skills
                    'python': "Technical Skills",
                    'java': "Technical Skills",
                    'c++': "Technical Skills",
                    'c': "Technical Skills",
                    'html': "Technical Skills",
                    'css': "Technical Skills",
                    'git': "Technical Skills",
                    'algorithms': "Technical Skills",
                    'data structures': "Technical Skills",
                    'shell scripting': "Technical Skills",
                    'eclipse': "Technical Skills",
                    
                    # Hardware/Electrical Engineering
                    'verilog': "Hardware/Electrical Engineering",
                    'systemverilog': "Hardware/Electrical Engineering",
                    'fpga': "Hardware/Electrical Engineering",
                    'circuit design': "Hardware/Electrical Engineering",
                    'digital design': "Hardware/Electrical Engineering",
                    'analog design': "Hardware/Electrical Engineering",
                    'vlsi': "Hardware/Electrical Engineering",
                    'cad': "Hardware/Electrical Engineering",
                    'xilinx': "Hardware/Electrical Engineering",
                    'vivado': "Hardware/Electrical Engineering",
                    'matlab': "Hardware/Electrical Engineering",
                    'spice': "Hardware/Electrical Engineering",
                    'control systems': "Hardware/Electrical Engineering",
                    'microprocessors': "Hardware/Electrical Engineering",
                    'computer architecture': "Hardware/Electrical Engineering",
                    'signal processing': "Hardware/Electrical Engineering",
                    'pcb design': "Hardware/Electrical Engineering",
                    'arm': "Hardware/Electrical Engineering",
                    'msp430': "Hardware/Electrical Engineering",
                    'keil': "Hardware/Electrical Engineering",
                    'latex': "Hardware/Electrical Engineering",
                    'bluespec': "Hardware/Electrical Engineering",
                    'modelsim': "Hardware/Electrical Engineering",
                    
                    # Soft Skills
                    'problem solving': "Soft Skills",
                    
                    # Data Science/Analytics
                    'data analysis': "Data Science/Analytics"
                }
                
                # Sort skills into categories
                for skill in extracted_skills:
                    category = skill_categories.get(skill.lower(), "Other")
                    if category in categories:
                        categories[category].append(skill)
                    else:
                        # Create an "Other" category for uncategorized skills
                        if "Other" not in categories:
                            categories["Other"] = []
                        categories["Other"].append(skill)
                
                # Remove empty categories
                return {k: v for k, v in categories.items() if v}

            # APPLY THE CATEGORIZATION
            categorized_skills = categorize_skills(extracted_skills)

            # REPLACE YOUR DISPLAY CODE
            st.markdown("""
            <style>
                .skills-header {
                    display: flex;
                    align-items: center;
                    margin-top: 30px;
                    margin-bottom: 25px;
                    padding-bottom: 12px;
                    border-bottom: 2px solid rgba(110, 142, 251, 0.4);
                }
                
                .skills-header-icon {
                    font-size: 24px;
                    margin-right: 12px;
                    background: linear-gradient(135deg, #6e8efb 0%, #5a70e7 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    background-clip: text;
                }
                
                .skills-header-text {
                    font-size: 22px;
                    font-weight: 600;
                    color: white;
                    letter-spacing: 0.5px;
                    margin: 0;
                }
            </style>

            <div class="skills-header">
                <div class="skills-header-icon">🛠️</div>
                <h2 class="skills-header-text">SKILLS EXTRACTED</h2>
            </div>
            """, unsafe_allow_html=True)

            # Enhanced CSS for styling
            st.markdown("""
            <style>
                /* Overall container */
                .skills-container {
                    margin-top: 15px;
                    padding: 10px 0;
                }
                
                /* Category styling */
                .skill-category {
                    margin-top: 25px;
                    margin-bottom: 15px;
                    padding-bottom: 8px;
                    font-weight: 600;
                    color: #ffffff;
                    font-size: 20px;
                    display: flex;
                    align-items: center;
                    border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                }
                
                .category-icon {
                    margin-right: 10px;
                    opacity: 0.9;
                }
                
                /* Skills grid */
                .skills-grid {
                    display: flex;
                    flex-wrap: wrap;
                    gap: 10px;
                    margin-bottom: 20px;
                }
                
                /* Skill tag base styling */
                .skill-tag {
                    display: inline-flex;
                    align-items: center;
                    padding: 8px 14px;
                    border-radius: 30px;
                    font-size: 14px;
                    transition: all 0.2s ease;
                    cursor: default;
                }
                
                /* Technical skills */
                .tech-skill {
                    background-color: rgba(84, 119, 153, 0.75);
                    color: white;
                    border: 1px solid rgba(84, 119, 153, 0.3);
                }
                .tech-skill:hover {
                    background-color: rgba(84, 119, 153, 0.9);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                }
                
                /* Hardware skills */
                .hardware-skill {
                    background-color: rgba(92, 131, 116, 0.75);
                    color: white;
                    border: 1px solid rgba(92, 131, 116, 0.3);
                }
                .hardware-skill:hover {
                    background-color: rgba(92, 131, 116, 0.9);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                }
                
                /* Soft skills */
                .soft-skill {
                    background-color: rgba(147, 101, 184, 0.75);
                    color: white;
                    border: 1px solid rgba(147, 101, 184, 0.3);
                }
                .soft-skill:hover {
                    background-color: rgba(147, 101, 184, 0.9);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                }
                
                /* Data science skills */
                .data-skill {
                    background-color: rgba(191, 85, 105, 0.75);
                    color: white;
                    border: 1px solid rgba(191, 85, 105, 0.3);
                }
                .data-skill:hover {
                    background-color: rgba(191, 85, 105, 0.9); 
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                }
                
                /* Other skills */
                .other-skill {
                    background-color: rgba(107, 114, 142, 0.75);
                    color: white;
                    border: 1px solid rgba(107, 114, 142, 0.3);
                }
                .other-skill:hover {
                    background-color: rgba(107, 114, 142, 0.9);
                    transform: translateY(-2px);
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                }
                
                /* Skill section spacing */
                .skill-section {
                    margin-bottom: 35px;
                }
            </style>
            """, unsafe_allow_html=True)

            # Category icons mapping
            category_icons = {
                "Technical Skills": "💻",
                "Hardware/Electrical Engineering": "🔌",
                "Soft Skills": "🤝",
                "Data Science/Analytics": "📊",
                "Other": "🔧"
            }

            # CSS class mapping
            css_class_map = {
                "Technical Skills": "tech-skill",
                "Hardware/Electrical Engineering": "hardware-skill",
                "Soft Skills": "soft-skill", 
                "Data Science/Analytics": "data-skill",
                "Other": "other-skill"
            }

            # Display skills by category with improved layout
            html_output = '<div class="skills-container">'

            for category, skills in categorized_skills.items():
                if skills:
                    icon = category_icons.get(category, "🔹")
                    css_class = css_class_map.get(category, "tech-skill")
                    
                    html_output += f'''
                    <div class="skill-section">
                        <h3 class="skill-category">
                            <span class="category-icon">{icon}</span> {category}
                        </h3>
                        <div class="skills-grid">
                    '''
                    
                    for skill in skills:
                        html_output += f'<span class="skill-tag {css_class}">{skill}</span>'
                        
                    html_output += '</div></div>'

            html_output += '</div>'
            st.markdown(html_output, unsafe_allow_html=True)

            
            # Get user input
            st.markdown("""
            <style>
                .stTextInput div[data-baseweb="input"] {
                    border-radius: 25px;
                    border: 2px solid #5C5C5C;
                    background-color: #333333;
                    padding: 2px 15px;
                }
                .stTextInput div[data-baseweb="input"]:focus-within {
                    border-color: #8E44AD;
                    box-shadow: 0 0 5px rgba(142, 68, 173, 0.5);
                }
                .stTextInput input {
                    color: white;
                }
                .job-card {
                    border-left: 4px solid #8E44AD;
                    background-color: #1E1E1E;
                    padding: 15px;
                    margin-bottom: 15px;
                    border-radius: 5px;
                }
                .job-title {
                    color: white;
                    font-size: 20px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }
                .job-info {
                    color: #CCCCCC;
                    margin-bottom: 5px;
                }
                .apply-button {
                    background-color: #4CAF50;
                    color: white;
                    padding: 8px 15px;
                    border: none;
                    border-radius: 20px;
                    cursor: pointer;
                    text-align: center;
                    font-weight: bold;
                    transition: background-color 0.3s;
                }
                .apply-button:hover {
                    background-color: #45a049;
                }
                .separator {
                    height: 1px;
                    background: linear-gradient(to right, rgba(142, 68, 173, 0), rgba(142, 68, 173, 0.7), rgba(142, 68, 173, 0));
                    margin: 10px 0 20px 0;
                }
            </style>
            """, unsafe_allow_html=True)

            # Improved search bar with icon and placeholder
            col1, col2 = st.columns([6, 1])
            with col1:
                location_input = st.text_input("", placeholder=" Enter your Preferred Location (Leave blank for remote jobs)", key="search_location")
            with col2:
                st.markdown("<br>", unsafe_allow_html=True)
                search_button = st.button("🔍 Search")

            # Get the most relevant skill
            top_skill = resume_data.get('skills', ["Developer"])[0]

            # Fetch jobs using the specified location
            jobs = get_jobs_from_adzuna(top_skill, location=location_input, results=5)

            # Add custom CSS for improved styling
            st.markdown("""
            <style>
                /* Overall page improvements */
                .main .block-container {
                    padding-top: 2rem;
                    padding-bottom: 3rem;
                    max-width: 1200px;
                }
                
                /* Section header styling */
                .section-header {
                    color: white;
                    margin-top: 30px;
                    margin-bottom: 25px;
                    font-size: 24px;
                    font-weight: 600;
                    border-bottom: 2px solid #8E44AD;
                    padding-bottom: 10px;
                    display: inline-block;
                }
                
                /* Job listing styling - with NO card effect */
                .job-listing {
                    padding: 15px 0;
                    margin-bottom: 10px;
                    border-left: 4px solid #8E44AD;
                    padding-left: 15px;
                }
                
                /* Job title with improved contrast */
                .job-title {
                    color: #FFFFFF;
                    font-size: 20px;
                    font-weight: bold;
                    margin-bottom: 15px;
                    letter-spacing: 0.3px;
                    display: flex;
                    align-items: center;
                }
                
                /* Job metadata with better spacing */
                .job-info-container {
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin-bottom: 15px;
                }
                
                .job-info {
                    display: flex;
                    flex-direction: column;
                    gap: 10px;
                }
                
                .info-item {
                    display: flex;
                    align-items: center;
                    gap: 8px;
                    color: #CCCCCC;
                }
                
                .info-label {
                    font-weight: 600;
                    color: #9A9A9A;
                }
                
                /* Description section - matching other info items */
                .job-description {
                    color: #CCCCCC;
                    margin-top: 15px;
                    margin-bottom: 20px;
                    line-height: 1.5;
                    background-color: rgba(33, 33, 33, 0.4);
                    padding: 15px;
                    border-radius: 4px;
                }
                
                /* Apply button with improved design */
                .apply-button {
                    background-color: #4CAF50;
                    color: white;
                    padding: 8px 16px;
                    border: none;
                    border-radius: 20px;
                    cursor: pointer;
                    display: inline-block;
                    font-weight: bold;
                    transition: all 0.3s;
                    text-decoration: none;
                    text-align: center;
                    min-width: 100px;
                }
                
                .apply-button:hover {
                    background-color: #45a049;
                    box-shadow: 0 2px 5px rgba(76, 175, 80, 0.3);
                }
                
                /* Separator improvement */
                .separator {
                    height: 1px;
                    background: linear-gradient(to right, rgba(142, 68, 173, 0), rgba(142, 68, 173, 0.5), rgba(142, 68, 173, 0));
                    margin: 20px 0;
                }
                
                /* Status indicators */
                .status-tag {
                    display: inline-block;
                    padding: 4px 10px;
                    border-radius: 20px;
                    font-size: 12px;
                    font-weight: 600;
                    margin-left: 12px;
                    background-color: #8E44AD;
                    color: white;
                }
            </style>
            """, unsafe_allow_html=True)
            
            st.markdown("""
                    <style>
                    @keyframes fadeSlideIn {
                        from {
                            opacity: 0;
                            transform: translateY(20px);
                        }
                        to {
                            opacity: 1;
                            transform: translateY(0);
                        }
                    }

                    @keyframes shine {
                        0% {
                            background-position: -100%;
                        }
                        100% {
                            background-position: 200%;
                        }
                    }

                    .animated-header {
                        animation: fadeSlideIn 0.8s ease-out;
                        position: relative;
                        overflow: hidden;
                        transition: box-shadow 0.3s ease;
                    }

                    .animated-header:hover {
                        box-shadow: 0 0 12px #00ffe1;
                    }

                    .animated-header:hover::after {
                        content: '';
                        position: absolute;
                        top: 0;
                        left: -75%;
                        width: 50%;
                        height: 100%;
                        background: linear-gradient(120deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.2) 50%, rgba(255,255,255,0.05) 100%);
                        animation: shine 1s ease forwards;
                    }
                    </style>
                """, unsafe_allow_html=True)

            st.markdown("""
                        <div class="animated-header" style="
                        background-color: #111827;
                        padding: 1.2rem;
                        border-radius: 8px;
                        margin-top: 2rem;
                        margin-bottom: 2rem;
                    ">
                        <h1 style='color: #ffffff; margin: 0;'> Job Recommendations</h1>
                    </div>
                """, unsafe_allow_html=True)
            
            st.markdown("""
                <div class="animated-header" style="
                    background-color: #1e1e1e;
                    padding: 0.8rem;
                    border-left: 6px solid #4ade80;
                    border-radius: 6px;
                    margin-top: 1.5rem;
                    margin-bottom: 1rem;
                ">
                    <h2 style='color: #ffffff; margin: 0;'>1. From Adzuna</h2>
                </div>
            """, unsafe_allow_html=True)

            if jobs:
                for i, job in enumerate(jobs):
                    job_title = job.get("title", "No Title")
                    company_name = job.get("company", {}).get("display_name", "Unknown Company")
                    job_location = job.get("location", {}).get("display_name", "Location Not Available")
                    job_link = job.get("redirect_url", "#")
                    
                    # Job title with tag
                    st.markdown('<div class="job-listing">', unsafe_allow_html=True)
                    st.markdown(f'<div class="job-title">🔹 {job_title}<span class="status-tag"></span></div>', unsafe_allow_html=True)
                    
                    # Job info and apply button in same row
                    st.markdown('<div class="job-info-container">', unsafe_allow_html=True)
                    
                    # Left side - Company and Location
                    st.markdown('<div class="job-info">', unsafe_allow_html=True)
                    
                    # Company info
                    st.markdown(f'''
                    <div class="info-item">
                        <span>🏢</span>
                        <span class="info-label">Company:</span>
                        <span>{company_name}</span>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Location info
                    st.markdown(f'''
                    <div class="info-item">
                        <span>📍</span>
                        <span class="info-label">Location:</span>
                        <span>{job_location}</span>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    # Salary info (if available)
                    if job.get("salary"):
                        st.markdown(f'''
                        <div class="info-item">
                            <span>💰</span>
                            <span class="info-label">Salary:</span>
                            <span>{job['salary']}</span>
                        </div>
                        ''', unsafe_allow_html=True)
                        
                    st.markdown('</div>', unsafe_allow_html=True)  # Close job-info
                    
                    # Right side - Apply button
                    st.markdown(f'''
                    <div>
                        <a href="{job_link}" target="_blank" style="text-decoration: none;">
                            <div class="apply-button">Apply Now</div>
                        </a>
                    </div>
                    ''', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)  # Close job-info-container
                    
                    # Job description styled consistently with other info items
                    if job.get("description"):
                        description = job["description"][:300] + "..." if len(job["description"]) > 300 else job["description"]
                        st.markdown(f'''
                        <div class="info-item" style="align-items: flex-start;">
                            <span></span>
                            <span class="info-label">About this role:</span>
                        </div>
                        <div class="job-description">{description}</div>
                        ''', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)  # Close job-listing
                    
                    # Add separator between jobs (if not the last job)
                    if i < len(jobs) - 1:
                        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
            else:
                st.info("No jobs found for the specified location. Try a different city or country!")
                
                
            # Display job recommendations from Jooble with improved layout
            st.markdown("""
                <div class="animated-header" style="
                    background-color: #1e1e1e;
                    padding: 0.8rem;
                    border-left: 6px solid #60a5fa;
                    border-radius: 6px;
                    margin-top: 2rem;
                    margin-bottom: 1rem;
                ">
                    <h2 style='color: #ffffff; margin: 0;'>2. From Jooble</h2>
                </div>
            """, unsafe_allow_html=True)



            jooble_jobs = fetch_jobs_from_jooble(extracted_skills, location_input)

            if jooble_jobs:
                for i, job in enumerate(jooble_jobs):
                    job_title = job.get("title", "No Title")
                    company_name = job.get("company", "Unknown Company")
                    job_location = job.get("location", "Location Not Available")
                    job_link = job.get("link", "#")

                    # Job title with tag
                    st.markdown('<div class="job-listing">', unsafe_allow_html=True)
                    st.markdown(f'<div class="job-title">🔹 {job_title}<span class="status-tag"></span></div>', unsafe_allow_html=True)

                    # Job info and apply button in same row
                    st.markdown('<div class="job-info-container">', unsafe_allow_html=True)

                    # Left side - Company and Location
                    st.markdown('<div class="job-info">', unsafe_allow_html=True)

                    # Company info
                    st.markdown(f'''
                    <div class="info-item">
                        <span>🏢</span>
                        <span class="info-label">Company:</span>
                        <span>{company_name}</span>
                    </div>
                    ''', unsafe_allow_html=True)

                    # Location info
                    st.markdown(f'''
                    <div class="info-item">
                        <span>📍</span>
                        <span class="info-label">Location:</span>
                        <span>{job_location}</span>
                    </div>
                    ''', unsafe_allow_html=True)

                    # Salary info (if available)
                    if job.get("salary"):
                        st.markdown(f'''
                        <div class="info-item">
                            <span>💰</span>
                            <span class="info-label">Salary:</span>
                            <span>{job["salary"]}</span>
                        </div>
                        ''', unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)  # Close job-info

                    # Right side - Apply button
                    st.markdown(f'''
                    <div>
                        <a href="{job_link}" target="_blank" style="text-decoration: none;">
                            <div class="apply-button">Apply Now</div>
                        </a>
                    </div>
                    ''', unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)  # Close job-info-container

                    # Optional description (if Jooble provides one)
                    if job.get("snippet"):
                        description = job["snippet"][:300] + "..." if len(job["snippet"]) > 300 else job["snippet"]
                        st.markdown(f'''
                        <div class="info-item" style="align-items: flex-start;">
                            <span></span>
                            <span class="info-label">About this role:</span>
                        </div>
                        <div class="job-description">{description}</div>
                        ''', unsafe_allow_html=True)

                    st.markdown('</div>', unsafe_allow_html=True)  # Close job-listing

                    # Add separator between jobs (if not the last job)
                    if i < len(jooble_jobs) - 1:
                        st.markdown('<div class="separator"></div>', unsafe_allow_html=True)
            else:
                st.warning(f"⚠ No jobs found in `{location_input or 'Remote'}`.")


            from difflib import get_close_matches

            # Skill categories and their keywords
            skill_categories = {
                "Data Science": ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask', 'streamlit'],
                "Web Development": ['react', 'django', 'node js', 'react js', 'php', 'laravel', 'magento', 'wordpress',
                                    'javascript', 'angular js', 'c#', 'flask'],
                "Android Development": ['android', 'android development', 'flutter', 'kotlin', 'xml', 'kivy'],
                "iOS Development": ['ios', 'ios development', 'swift', 'cocoa', 'cocoa touch', 'xcode'],
                "UI/UX Design": ['ux', 'adobe xd', 'figma', 'zeplin', 'balsamiq', 'ui', 'prototyping', 'wireframes',
                                'storyframes', 'adobe photoshop', 'photoshop', 'editing', 'adobe illustrator',
                                'illustrator', 'adobe after effects', 'after effects', 'adobe premiere pro',
                                'premiere pro', 'adobe indesign', 'indesign', 'solid', 'grasp', 'user research',
                                'user experience']
            }

            # Recommended skills per category
            recommended_map = {
                "Data Science": ['Flask', 'Numpy', 'Pandas', 'Deep Learning', 'AWS', 'Azure', 'Streamlit'],
                "Web Development": ['React', 'Django', 'HTML', 'CSS', 'Javascript', 'Node.js'],
                "Android Development": ['Kotlin', 'Java', 'Flutter', 'XML'],
                "iOS Development": ['Swift', 'Xcode', 'Cocoa'],
                "UI/UX Design": ['Figma', 'Adobe XD', 'User Research', 'Prototyping']
            }

            from difflib import get_close_matches

            # Lowercase extracted skills
            import re
            def normalize_skill(skill):
                return re.sub(r'[^a-z0-9\s]', '', skill.lower().strip())

            extracted_skills = [normalize_skill(skill) for skill in resume_data.get('skills', [])]

            
            # Initialize
            recommended_fields = set()
            recommended_skills = set()
            rec_course = None

            skill_categories = {
                "Data Science/Analytics": {
                    "keywords": ['tensorflow', 'keras', 'pytorch', 'machine learning', 'deep learning', 'flask', 
                                'streamlit', 'pandas', 'numpy', 'scikit-learn', 'data analysis', 'data visualization', 
                                'statistical analysis', 'big data', 'power bi', 'tableau', 'r', 'sql', 'nosql', 
                                'data mining', 'data modeling', 'data engineering', 'spark', 'hadoop', 'time series',
                                'regression analysis', 'nlp', 'natural language processing', 'computer vision', 
                                'data warehouse', 'etl', 'snowflake', 'databricks', 'airflow', 'dbt'],
                    "recommend": ['Data Visualization', 'Predictive Analytics', 'Statistical Modeling', 'Data Mining',
                                'Clustering & Classification', 'Data Analytics', 'Quantitative Analysis', 'Web Scraping',
                                'ML Algorithms', 'Keras', 'PyTorch', 'Probability', 'SQL', 'Power BI', 'Tableau', 
                                'Scikit-learn', 'TensorFlow', 'Flask', 'Streamlit', 'Cloud Computing', 'AWS', 'Azure',
                                'Data Pipelines', 'A/B Testing', 'Docker', 'Kubernetes']
                },
                "Web Development": {
                    "keywords": ['react', 'django', 'node.js', 'node js', 'react.js', 'react js', 'php', 'laravel', 
                                'magento', 'wordpress', 'javascript', 'angular', 'vue.js', 'vue js', 'typescript',
                                'html', 'css', 'sass', 'less', 'tailwind', 'bootstrap', 'jquery', 'rest api',
                                'graphql', 'mongodb', 'express.js', 'express js', 'firebase', 'next.js', 'next js',
                                'gatsby', 'svelte', 'pwa', 'web components', 'redux', 'webpack', 'vite', 'remix',
                                'webassembly', 'wasm', 'jamstack', 'seo', 'web accessibility', 'web security'],
                    "recommend": ['React', 'Next.js', 'TypeScript', 'Tailwind CSS', 'GraphQL', 'Node.js', 'MongoDB', 
                                'AWS Amplify', 'Docker', 'CI/CD', 'GitHub Actions', 'Vercel', 'Netlify', 'Redux',
                                'Jest', 'Testing Library', 'Responsive Design', 'Web Accessibility', 'Web Security',
                                'Performance Optimization', 'API Development', 'OAuth', 'JWT Authentication']
                },
                "Mobile Development": {
                    "keywords": ['android', 'ios', 'flutter', 'react native', 'kotlin', 'swift', 'objective-c',
                                'java', 'xml', 'kivy', 'xamarin', 'ionic', 'cordova', 'capacitor', 'mobile ui',
                                'mobile ux', 'app store optimization', 'aso', 'push notifications',
                                'offline storage', 'jetpack compose', 'swiftui', 'dart', 'kotlin multiplatform',
                                'mobile analytics', 'app performance', 'mobile testing', 'mobile security'],
                    "recommend": ['Flutter', 'React Native', 'Kotlin', 'Swift', 'SwiftUI', 'Jetpack Compose',
                                'Firebase', 'App Architecture', 'State Management', 'Navigation', 'Animation',
                                'Mobile UI/UX', 'Responsive Layouts', 'Offline Storage', 'API Integration',
                                'Push Notifications', 'App Store/Play Store', 'Mobile Testing', 'CI/CD']
                },
                "UI/UX Design": {
                    "keywords": ['ux', 'user experience', 'adobe xd', 'figma', 'sketch', 'zeplin', 'balsamiq', 'ui',
                                'prototyping', 'wireframes', 'storyframes', 'adobe photoshop', 'photoshop',
                                'editing', 'adobe illustrator', 'illustrator', 'adobe after effects',
                                'after effects', 'adobe premiere pro', 'premiere pro', 'adobe indesign',
                                'indesign', 'solid', 'grasp', 'user research', 'information architecture',
                                'interaction design', 'visual design', 'usability testing', 'accessibility',
                                'design thinking', 'user interviews', 'journey mapping', 'framer', 'design systems'],
                    "recommend": ['UI', 'User Experience', 'Figma', 'Design Systems', 'Prototyping', 'Wireframing',
                                'User Research', 'Information Architecture', 'Interaction Design', 'Visual Design',
                                'Adobe Creative Suite', 'Accessibility', 'Design Thinking', 'Usability Testing',
                                'User Interviews', 'Journey Mapping', 'Color Theory', 'Typography', 'Motion Design']
                },
                "DevOps/Cloud Engineering": {
                    "keywords": ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'gitlab ci', 'github actions',
                                'terraform', 'ansible', 'chef', 'puppet', 'prometheus', 'grafana', 'elk stack',
                                'logging', 'monitoring', 'ci/cd', 'continuous integration', 'continuous deployment',
                                'infrastructure as code', 'iac', 'devops', 'sre', 'site reliability', 'cloud architecture',
                                'serverless', 'lambda', 'cloudformation', 'networking', 'linux', 'unix', 'shell scripting',
                                'bash', 'cybersecurity', 'security', 'devsecops', 'cloud security'],
                    "recommend": ['AWS', 'Azure', 'Docker', 'Kubernetes', 'Terraform', 'CI/CD', 'Infrastructure as Code',
                                'Monitoring & Observability', 'Cloud Architecture', 'Serverless', 'Linux', 'Shell Scripting',
                                'Security Best Practices', 'Networking', 'Cost Optimization', 'High Availability', 
                                'Disaster Recovery', 'Performance Tuning', 'Compliance', 'Documentation']
                },
                "Hardware/Electrical Engineering": {
                    "keywords": ['fpga', 'verilog', 'vhdl', 'pcb design', 'systemverilog', 'vlsi', 'bluespec', 'modelsim',
                                'circuit design', 'analog design', 'digital design', 'microprocessors', 'embedded systems',
                                'msp430', 'arm', 'xilinx', 'signal processing', 'control systems', 'verilog', 'cadence',
                                'altium', 'eagle', 'kicad', 'multisim', 'spice', 'ltspice', 'embedded c', 'arduino',
                                'raspberry pi', 'stm32', 'microcontrollers', 'sensors', 'actuators', 'robotics',
                                'power electronics', 'battery management', 'rf design', 'antenna design', 'iot', 
                                'internet of things', 'embedded linux', 'rtos', 'freertos', 'zephyr'],
                    "recommend": ['PCB Design', 'Circuit Simulation', 'FPGA Programming', 'Verilog/VHDL', 'Altium Designer',
                                'Embedded C/C++', 'ARM Architecture', 'RTOS', 'Digital Signal Processing', 'IoT Protocols',
                                'Wireless Communication', 'Battery Management', 'Sensor Integration', 'Power Management',
                                'Hardware Testing', 'Schematic Design', 'Embedded Linux', 'Hardware Security']
                },
                "Cybersecurity": {
                    "keywords": ['penetration testing', 'ethical hacking', 'vulnerability assessment', 'security audit',
                                'network security', 'application security', 'cloud security', 'security operations',
                                'soc', 'incident response', 'forensics', 'malware analysis', 'threat intelligence',
                                'security architecture', 'identity management', 'access control', 'cryptography',
                                'encryption', 'security compliance', 'gdpr', 'hipaa', 'pci dss', 'iso 27001',
                                'security tools', 'wireshark', 'metasploit', 'burp suite', 'nmap', 'kali linux',
                                'siem', 'splunk', 'security+', 'cissp', 'cism', 'oscp'],
                    "recommend": ['Penetration Testing', 'Vulnerability Assessment', 'Security Monitoring', 'Incident Response',
                                'Threat Intelligence', 'Security Tools', 'Cloud Security', 'DevSecOps', 'Security Architecture',
                                'Encryption', 'Identity & Access Management', 'Security Compliance', 'Risk Assessment',
                                'SIEM', 'Network Security', 'Application Security', 'Security Automation']
                },
                "Project Management": {
                    "keywords": ['project management', 'program management', 'product management', 'agile', 'scrum',
                                'kanban', 'lean', 'pmp', 'prince2', 'safe', 'jira', 'confluence', 'asana', 'trello',
                                'monday', 'ms project', 'risk management', 'stakeholder management', 'roadmapping',
                                'sprint planning', 'retrospectives', 'user stories', 'estimation', 'resource planning',
                                'budgeting', 'cost management', 'change management', 'release management',
                                'project documentation', 'project lifecycle', 'critical path', 'gantt chart',
                                'business analysis', 'requirements gathering'],
                    "recommend": ['Agile Methodologies', 'Scrum', 'JIRA', 'Stakeholder Management', 'Risk Management',
                                'Resource Planning', 'Roadmapping', 'Sprint Planning', 'Estimation', 'Communication',
                                'Team Leadership', 'Reporting', 'Product Lifecycle', 'Conflict Resolution',
                                'Continuous Improvement', 'Project Documentation', 'Performance Metrics']
                },
                "Blockchain/Web3": {
                    "keywords": ['blockchain', 'web3', 'smart contracts', 'ethereum', 'solidity', 'rust', 'bitcoin',
                                'cryptocurrency', 'nft', 'defi', 'dao', 'consensus mechanisms', 'distributed ledger',
                                'cryptography', 'tokenomics', 'dapps', 'decentralized applications', 'web3.js',
                                'ethers.js', 'truffle', 'hardhat', 'metamask', 'wallet integration', 'layer 2',
                                'zero knowledge', 'zk rollups', 'polkadot', 'substrate', 'solana', 'avalanche',
                                'chainlink', 'oracles', 'ipfs', 'filecoin'],
                    "recommend": ['Smart Contract Development', 'Solidity', 'Web3.js/Ethers.js', 'Hardhat/Truffle',
                                'DApp Architecture', 'Token Standards', 'Wallet Integration', 'NFT Development',
                                'Security Best Practices', 'Gas Optimization', 'Layer 2 Solutions', 'Cross-chain',
                                'DeFi Protocols', 'Testing & Auditing', 'Blockchain Architecture']
                },
                "AI Engineering": {
                    "keywords": ['artificial intelligence', 'machine learning engineer', 'llm', 'large language models',
                                'generative ai', 'ai engineering', 'prompt engineering', 'neural networks', 'transformer models',
                                'bert', 'gpt', 'stable diffusion', 'openai', 'hugging face', 'langchain', 'llama index',
                                'model tuning', 'fine-tuning', 'vector databases', 'embeddings', 'rag', 'retrieval augmented generation',
                                'ai agents', 'autonomous agents', 'ai ethics', 'responsible ai', 'ai governance',
                                'multi-modal ai', 'ai integration', 'ai inference', 'onnx', 'model optimization',
                                'model quantization', 'model deployment', 'ai ops'],
                    "recommend": ['LLM Integration', 'Prompt Engineering', 'Vector Databases', 'RAG Systems', 
                                'Fine-tuning', 'AI Application Development', 'Hugging Face', 'LangChain', 
                                'Embeddings', 'Model Optimization', 'Multi-modal AI', 'AI Evaluation', 
                                'AI Ethics', 'Model Deployment', 'AI Agents', 'Inference Optimization']
                }
            }

            # Initialize as a set from the beginning
            recommended_fields = set()
            recommended_skills = set()  # Make sure this is defined

            # Match skills to categories
            from collections import defaultdict

            # Define weights for direct matches and similarity matches
            DIRECT_MATCH_WEIGHT = 1.0
            SIMILARITY_MATCH_WEIGHT = 0.5

            # Normalize keywords for better matching
            for field in skill_categories:
                skill_categories[field]["keywords"] = [normalize_skill(k) for k in skill_categories[field]["keywords"]]

            field_scores = defaultdict(int)
            field_recommend_skills = defaultdict(set)

            for skill in extracted_skills:
                for field, content in skill_categories.items():
                    keywords = content["keywords"]
                    
                    # Check for direct matches (exact matches)
                    if skill in keywords:
                        field_scores[field] += DIRECT_MATCH_WEIGHT
                        field_recommend_skills[field].update(content["recommend"])
                        continue
                        
                    # Check for similarity matches
                    matches = get_close_matches(skill, keywords, n=1, cutoff=0.7)  # Increased cutoff
                    if matches:
                        # Add a lower score for similarity matches
                        field_scores[field] += SIMILARITY_MATCH_WEIGHT
                        field_recommend_skills[field].update(content["recommend"])


            # Pick top matched fields - Modified to show ALL fields with scores above a threshold
            if field_scores:
                # Define a minimum threshold score (adjust as needed)
                threshold_score = 0.5
                
                # Get all fields that meet the threshold
                recommended_fields = {field for field, score in field_scores.items() if score >= threshold_score}
                
                # If no fields meet the threshold, take the top 3
                if not recommended_fields:
                    sorted_fields = sorted(field_scores.items(), key=lambda x: x[1], reverse=True)
                    recommended_fields = {field for field, score in sorted_fields[:3]}
                
                for field in recommended_fields:
                    recommended_skills.update(field_recommend_skills[field])
            else:
                # Fallback
                st.info("We couldn't determine your specific field based on your skills. Here are some general recommendations.")
                recommended_fields.add('General')
                has_programming = any('programming' in s or 'html' in s or 'c++' in s for s in extracted_skills)
                if has_programming:
                    recommended_fields.add('Web Development')
                    recommended_skills.update(['JavaScript', 'React', 'Node.js', 'Python', 'Django', 'Database Management',
                                        'API Development', 'Git', 'DevOps', 'Testing'])
                else:
                    recommended_skills.update(['Communication', 'Problem Solving', 'Critical Thinking', 'Time Management',
                                        'Project Management', 'Microsoft Office', 'Data Analysis', 'Leadership',
                                        'Teamwork', 'Attention to Detail'])

            # Convert to list for display if needed
            recommended_fields_list = list(recommended_fields)

            # Display Career Fields in a more attractive way
            if recommended_fields:
                st.subheader("🎯 Recommended Career Fields Based on Your Skills")
                
                # Field icons dictionary (add more as needed)
                field_icons = {
                    "UI/UX Design": "🎨",
                    "Web Development": "🌐",
                    "Data Science/Analytics": "📊",
                    "Hardware/Electrical Engineering": "⚡",
                    "AI Engineering": "🤖",
                    "Mobile Development": "📱",
                    "Blockchain/Web3": "🔗",
                    "DevOps/Cloud Engineering": "☁️",
                    "Cybersecurity": "🔒",
                    "Project Management": "📋",
                    "General": "🔍"
                }
                
                # Create a list from the set and sort by score
                fields_list = list(recommended_fields)
                fields_list.sort(key=lambda x: field_scores[x], reverse=True)
                
                # Create two columns
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    # Top field gets special treatment
                    if fields_list:
                        top_field = fields_list[0]
                        score = field_scores[top_field]
                        percentage = min(100, (score/10) * 100)
                        
                        icon = field_icons.get(top_field, "✨")
                        
                        st.markdown(f"""
                        <div style='background-color:#f8f9fa;border-radius:15px;padding:20px;margin-bottom:20px;border:1px solid #eaeaea;'>
                            <h2 style='margin:0;color:#333;'>{icon} {top_field}</h2>
                            <p style='color:#666;margin:5px 0 15px 0;'>Top recommendation based on your skills</p>
                            <div style='background-color:#e9ecef;height:12px;border-radius:6px;margin:10px 0;'>
                                <div style='background-color:#1ed760;width:{percentage}%;height:12px;border-radius:6px;'></div>
                            </div>
                            <div style='display:flex;justify-content:space-between;'>
                                <span style='font-size:14px;color:#666;'>Match score</span>
                                <span style='font-weight:bold;'>{score}/10</span>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                
                # Create rows for remaining fields
                if len(fields_list) > 1:
                    st.markdown("### Other Suitable Fields")
                    
                    # Create grid
                    remaining_cols = st.columns(min(2, len(fields_list)-1))
                    for i, field in enumerate(fields_list[1:]):
                        with remaining_cols[i % len(remaining_cols)]:
                            score = field_scores[field]
                            percentage = min(100, (score/10) * 100)
                            icon = field_icons.get(field, "✨")
                            
                            st.markdown(f"""
                            <div style='background-color:#f8f9fa;border-radius:10px;padding:15px;margin-bottom:15px;border:1px solid #eaeaea;'>
                                <h3 style='margin:0;color:#333;font-size:18px;'>{icon} {field}</h3>
                                <div style='background-color:#e9ecef;height:8px;border-radius:4px;margin:10px 0;'>
                                    <div style='background-color:#1ed760;width:{percentage}%;height:8px;border-radius:4px;'></div>
                                </div>
                                <div style='text-align:right;font-size:14px;'>
                                    <span style='font-weight:bold;'>{score}/10</span>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                
            # 🚀 Skills to Develop Section (Grouped by Field)
            st.markdown("""
                <h2 style='color: #66ff66;'>🚀 Skills to Develop</h2>
                <p style='color: #888;'>Boost your profile in the matched career fields by adding these skills</p>
                <style>
                    .field-section {
                        margin-bottom: 30px;
                        padding: 12px 20px;
                        border-left: 4px solid #66ff66;
                        background-color: #2d2d2d;  /* Dark background for field section */
                        border-radius: 8px;
                    }
                    .skill-card {
                        background-color: #3c3c3c;  /* Dark card background */
                        border: 1px solid #444444;  /* Darker border */
                        border-radius: 10px;
                        padding: 10px 16px;
                        text-align: center;
                        font-weight: 500;
                        color: #dcdcdc;  /* Light text color for readability */
                        margin-bottom: 12px;
                        box-shadow: 0px 1px 4px rgba(0,0,0,0.1);
                        transition: all 0.2s ease-in-out;
                    }
                    .skill-card:hover {
                        transform: scale(1.03);
                        background-color: #4a4a4a;  /* Darker shade on hover */
                        cursor: pointer;
                    }
                </style>
            """, unsafe_allow_html=True)

            # Normalize user's extracted skills
            extracted_skills_normalized = {skill.strip().lower() for skill in extracted_skills}

            skills_grouped_by_field = {}

            # Sort top fields by score and limit to top 5
            top_fields = sorted(field_scores.items(), key=lambda x: x[1], reverse=True)[:5]

            for field, _ in top_fields:
                if field in field_recommend_skills:
                    field_skills_raw = field_recommend_skills[field]
                    normalized_skill_map = {
                        skill.strip().lower(): skill.strip() for skill in field_skills_raw
                    }

                    # Extract missing skills only
                    missing_normalized_skills = [
                        normalized_skill_map[skill]
                        for skill in normalized_skill_map
                        if skill not in extracted_skills_normalized
                    ]

                    if missing_normalized_skills:
                        skills_grouped_by_field[field] = sorted(missing_normalized_skills)[:6]  # limit to 6

            # Display grouped skills
            if skills_grouped_by_field:
                for field, skills in skills_grouped_by_field.items():
                    st.markdown(f"""
                        <div class='field-section'>
                            <h4 style='color:#66ff66;margin-bottom:10px;'>📌 {field} <span style='color:#aaa;font-size:90%;'>({len(skills)} skills)</span></h4>
                    """, unsafe_allow_html=True)
                    skill_cols = st.columns(min(3, len(skills)))
                    for i, skill in enumerate(skills):
                        with skill_cols[i % len(skill_cols)]:
                            st.markdown(f"<div class='skill-card'>{skill}</div>", unsafe_allow_html=True)
                    st.markdown("</div>", unsafe_allow_html=True)

                st.markdown(
                    '''<p style='text-align: left; color: #66ff66; margin-top: 25px; font-weight:500;'>
                    ✨ Adding these skills to your resume will significantly improve your career potential!</p>''',
                    unsafe_allow_html=True
                )
            else:
                st.info("No additional skills to recommend — you're already rocking a strong skill set! 💪")
                
            from Courses import ds_course, web_course, android_course, ios_course, uiux_course

            # Create course list based on skill keywords
            course_list = []

            if any(skill in recommended_skills for skill in ["Python", "Pandas", "NumPy", "Machine Learning", "Data Analysis"]):
                course_list.extend(ds_course)
            if any(skill in recommended_skills for skill in ["HTML", "CSS", "JavaScript", "React", "Frontend"]):
                course_list.extend(web_course)
            if any(skill in recommended_skills for skill in ["Kotlin", "Java", "Android"]):
                course_list.extend(android_course)
            if any(skill in recommended_skills for skill in ["Swift", "iOS"]):
                course_list.extend(ios_course)
            if any(skill in recommended_skills for skill in ["Figma", "UI/UX", "Prototyping"]):
                course_list.extend(uiux_course)

            # Now show recommended courses if available
            if course_list:
                course_recommender(course_list)
            else:
                st.info("No matching course recommendations based on your skills.")



                    

            # Insert into table
            ts = time.time()
            cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
            cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
            timestamp = str(cur_date + '_' + cur_time)

            # Updated weights based on your screenshot
            section_weights = {
                'projects': 25,
                'skills': 25,
                'objective': 15,
                'achievements': 15,
                'certifications': 10,
                'declaration': 5,
                'hobbies': 5
            }

            # Alternative names to capture variations
            alternate_keywords = {
                'hobbies': ['hobbies', 'interests'],
                'certifications': ['certifications', 'courses', 'licenses']
            }

            # Suggestions for missing sections
            section_suggestions = {
                'projects': 'Please add Projects. They show practical experience related to the role.',
                'skills': 'Please list your Skills clearly. They are vital for matching your profile to a job.',
                'objective': 'Please add a career Objective. It helps recruiters understand your direction.',
                'achievements': 'Please mention Achievements to highlight what sets you apart.',
                'certifications': 'Include Certifications to show proven expertise in your field.',
                'declaration': 'Please add a Declaration for credibility and ownership of resume content.',
                'hobbies': 'Mentioning Hobbies or Interests shows a glimpse of your personality and culture fit.'
            }
            
            st.markdown("""
                <style>
                .tip-box {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    padding: 6px 12px;
                    border-radius: 6px;
                    margin-bottom: 5px;
                    font-weight: 500;
                    transition: all 0.3s ease;
                }

                .dot {
                    height: 12px;
                    width: 12px;
                    border-radius: 50%;
                    box-shadow: 0 0 6px rgba(0,0,0,0.2);
                    transition: all 0.3s ease;
                }

                .dot-green {
                    background-color: #00FF00;
                    box-shadow: 0 0 8px rgba(0, 255, 0, 0.6);
                }

                .dot-green:hover {
                    box-shadow: 0 0 12px rgba(0, 255, 0, 1);
                }

                .dot-red {
                    background-color: #FF4B4B;
                    box-shadow: 0 0 8px rgba(255, 75, 75, 0.6);
                }

                .dot-red:hover {
                    box-shadow: 0 0 12px rgba(255, 75, 75, 1);
                }
                </style>
            """, unsafe_allow_html=True)

            def calculate_resume_score_and_tips(resume_text):
                resume_text = resume_text.lower()
                score = 0

                st.markdown("""
                    <h2 style='color:#FFD700; font-size: 28px; font-weight: 700; margin-bottom: 10px;'>
                        📄 Resume Tips & Ideas
                    </h2>
                """, unsafe_allow_html=True)

                
                st.markdown("<br>", unsafe_allow_html=True)

                for section, weight in section_weights.items():
                    found = False
                    keywords = alternate_keywords.get(section, [section])

                    for keyword in keywords:
                        if keyword in resume_text:
                            found = True
                            break

                    if found:
                        score += weight
                        st.markdown(
                            f"""
                            <div class='tip-box'>
                                <div class='dot dot-green'></div>
                                <span style='color: #00FF00;'>Awesome! You have added <b>{section.capitalize()}</b></span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"""
                            <div class='tip-box'>
                                <div class='dot dot-red'></div>
                                <span style='color: #FF4B4B;'>{section_suggestions[section]}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )


                st.markdown("<br>", unsafe_allow_html=True)
                st.subheader("📊 Resume Score")

                st.markdown(
                    f"""
                    <div style='padding: 20px; background-color: #1c1c1e; border-radius: 10px; color: #00FF00; font-size: 24px;'>
                        <b>Your Resume Score is</b><br> {score}/100
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("""
                    <div style='margin-top: 20px; background-color: #2c2c2e; padding: 10px; border-radius: 8px; font-size: 14px; color: #AAAAAA;'>
                    <b>Note:</b> Your resume score is calculated by analyzing key sections like Projects, Skills, and Achievements. 
                    Each section contributes different weights based on its importance (e.g., Projects and Skills contribute 25% each).
                    </div>
                """, unsafe_allow_html=True)

                return score


            # Calculate the score
            resume_score = calculate_resume_score_and_tips(resume_text)

            # Show Candidate Level Below Score with Dynamic Color, Icons, and Enhanced Layout
            if resume_score < 40:
                cand_level = "Fresher"
                level_color = "#d73b5c"
            elif resume_score <= 70:
                cand_level = "Intermediate"
                level_color = "#66ff66"
            else:
                cand_level = "Experienced"
                level_color = "#fba171"

            # Display the Candidate Level with dynamic color and icons with a modern layout
            st.markdown(f'''
                <div style="background-color: #1d1f1f; color: {level_color}; padding: 20px; border-radius: 12px; 
                            display: flex; justify-content: center; align-items: center; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);">
                    <div style="font-size: 20px; font-weight: bold; text-align: center;">
                        You are at <u>{cand_level}</u> level!
                    </div>
                </div>
            ''', unsafe_allow_html=True)

            def insert_data(name, email, score, timestamp, num_pages, fields, level, skills, recommended_skills, courses):
                query = """
                INSERT INTO resume_table (name, email, score, timestamp, num_pages, fields, level, skills, recommended_skills, courses)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (name, email, score, timestamp, num_pages, fields, level, skills, recommended_skills, courses)
                cursor.execute(query, values)
                connection.commit()


            # ---- CSS Styling ----
            st.markdown("""
                <style>
                    .video-row {
                        display: flex;
                        justify-content: center;
                        gap: 1.5rem;
                        flex-wrap: wrap;
                        margin-top: 20px;
                    }
                    .video-card {
                        width: 240px;
                        background-color: #fefefe;
                        padding: 12px;
                        border-radius: 16px;
                        border: 1px solid #e0e0e0;
                        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.04);
                        text-align: center;
                    }
                    .video-card h4 {
                        font-size: 15px;
                        margin-bottom: 10px;
                        color: #0072b1;
                    }
                    .video-frame iframe {
                        border-radius: 12px;
                    }
                </style>
            """, unsafe_allow_html=True)

            # Header
            st.header("🎥 Bonus Learning Videos (Compact View)")

            # Randomly pick videos
            resume_vid = random.choice(resume_videos)
            interview_vid = random.choice(interview_videos)

            # Fetch titles (placeholder)
            res_vid_title = fetch_yt_video(resume_vid)
            int_vid_title = fetch_yt_video(interview_vid)

            # Layout container
            st.markdown('<div class="video-row">', unsafe_allow_html=True)

            # Resume Video
            st.markdown(f"""
                <div class="video-card">
                    <h4>✅ {res_vid_title}</h4>
                    <div class="video-frame">
            """, unsafe_allow_html=True)
            st.video(resume_vid)
            st.markdown("</div></div>", unsafe_allow_html=True)

            # Interview Video
            st.markdown(f"""
                <div class="video-card">
                    <h4>✅ {int_vid_title}</h4>
                    <div class="video-frame">
            """, unsafe_allow_html=True)
            st.video(interview_vid)
            st.markdown("</div></div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)


            connection.commit()
        else:
            st.markdown(
                """
                <div style="text-align:center; background-color:#d4edda; padding:10px; border-radius:10px; color:#155724; font-weight:bold;">
                    Welcome!!!
                </div>
                """,
                unsafe_allow_html=True
            )

    else:
        import pandas as pd
        import plotly.express as px

        # Utility function to generate a download link
        def get_table_download_link(df, filename, link_text):
            import base64
            csv = df.to_csv(index=False)
            b64 = base64.b64encode(csv.encode()).decode()
            return f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'

        # --- Admin Side ---
        st.success('Welcome to Admin Side')

        # Multiple admin credentials stored in a dictionary
        admins = {
            'Shubham': 'Snamlien321',
            'Abhinav': 'Abhi@321',
            'Pragya': 'Pragya@321'
        }

        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button('Login'):
            if ad_user in admins and ad_password == admins[ad_user]:
                st.success(f"Welcome Mr./Ms. {ad_user}")

                # ✅ Display Data from DB
                cursor.execute('''SELECT * FROM user_data''')
                data = cursor.fetchall()

                df = pd.DataFrame(data, columns=[
                    'ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Page',
                    'Predicted_Field', 'User_level', 'Actual Skills', 'Recommended Skills',
                    'Recommended Course'
                ])
                st.header("**User's Data**")
                st.dataframe(df)

                # ✅ Download CSV Report
                st.markdown(get_table_download_link(df, 'User_Data.csv', '📥 Download Report'), unsafe_allow_html=True)

                # ✅ Read data again for charts
                query = 'SELECT * FROM user_data;'
                plot_data = pd.read_sql(query, connection)

                # Decode bytes to string if needed
                for col in ['Predicted_Field', 'User_level']:
                    if plot_data[col].dtype == object:
                        plot_data[col] = plot_data[col].apply(lambda x: x.decode('utf-8') if isinstance(x, bytes) else x)

                # ✅ Pie Chart: Predicted Field
                st.subheader("📊 Pie-Chart for Predicted Field Recommendation")
                field_counts = plot_data['Predicted_Field'].value_counts().reset_index()
                field_counts.columns = ['Predicted_Field', 'Count']
                fig1 = px.pie(
                    field_counts,
                    values='Count',
                    names='Predicted_Field',
                    title='Predicted Field according to the Skills'
                )
                st.plotly_chart(fig1)

                # ✅ Pie Chart: User Experience Level
                st.subheader("📊 Pie-Chart for User's Experienced Level")
                level_counts = plot_data['User_level'].value_counts().reset_index()
                level_counts.columns = ['User_level', 'Count']
                fig2 = px.pie(
                    level_counts,
                    values='Count',
                    names='User_level',
                    title="User's👨‍💻 Experienced Level"
                )
                st.plotly_chart(fig2)

            else:
                st.error("❌ Wrong ID & Password Provided")
    add_footer()
run()