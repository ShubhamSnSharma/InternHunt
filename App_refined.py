import streamlit as st
import pandas as pd
import base64
import random
import time
import datetime
import io
import os
import json
import requests
from PIL import Image
import pymysql
from typing import List, Dict, Any, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import custom modules
try:
    from Courses import ds_course, web_course, android_course, ios_course, uiux_course, resume_videos, interview_videos
    from ui import add_custom_css, add_footer
except ImportError as e:
    logger.error(f"Failed to import custom modules: {e}")
    st.error("Some modules are missing. Please check your installation.")

# Set page config early
st.set_page_config(
    page_title="InternHunt - Your Internship Finder",
    page_icon='🎯',
    layout="wide",
)

# Environment variables for sensitive data
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'your_password'),
    'database': os.getenv('DB_NAME', 'cv')
}

# API Keys from environment
JOOBLE_API_KEY = os.getenv("JOOBLE_API_KEY", "4d4c75a1-1761-49c7-a003-71ed93beaf52")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID", "1178ed1c")
ADZUNA_API_KEY = os.getenv("ADZUNA_API_KEY", "2e96a2f4573fff0502a2a081c21b6810")

class DatabaseManager:
    """Handle all database operations"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self.connect()
    
    def connect(self):
        """Establish database connection"""
        try:
            self.connection = pymysql.connect(**DB_CONFIG)
            self.cursor = self.connection.cursor()
            self.setup_database()
        except Exception as e:
            logger.error(f"Database connection failed: {e}")
            st.error("Database connection failed. Please check your configuration.")
    
    def setup_database(self):
        """Create database and tables if they don't exist"""
        try:
            # Create database
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS cv;")
            self.cursor.execute("USE cv;")
            
            # Create table with proper schema
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS user_data (
                ID INT NOT NULL AUTO_INCREMENT,
                Name VARCHAR(500) NOT NULL,
                Email_ID VARCHAR(500) NOT NULL,
                resume_score VARCHAR(8) NOT NULL,
                Timestamp VARCHAR(50) NOT NULL,
                Page_no VARCHAR(5) NOT NULL,
                Predicted_Field TEXT NOT NULL,
                User_level TEXT NOT NULL,
                Actual_skills TEXT NOT NULL,
                Recommended_skills TEXT NOT NULL,
                Recommended_courses TEXT NOT NULL,
                PRIMARY KEY (ID)
            );
            """
            self.cursor.execute(create_table_sql)
            self.connection.commit()
        except Exception as e:
            logger.error(f"Database setup failed: {e}")
    
    def insert_user_data(self, data: Dict):
        """Insert user data into database"""
        try:
            insert_sql = """
            INSERT INTO user_data (Name, Email_ID, resume_score, Timestamp, Page_no, 
                                 Predicted_Field, User_level, Actual_skills, 
                                 Recommended_skills, Recommended_courses)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                data.get('name', ''),
                data.get('email', ''),
                str(data.get('score', 0)),
                data.get('timestamp', ''),
                str(data.get('pages', 0)),
                ', '.join(data.get('fields', [])),
                data.get('level', ''),
                ', '.join(data.get('skills', [])),
                ', '.join(data.get('recommended_skills', [])),
                ', '.join(data.get('courses', []))
            )
            self.cursor.execute(insert_sql, values)
            self.connection.commit()
            return True
        except Exception as e:
            logger.error(f"Data insertion failed: {e}")
            return False
    
    def get_all_data(self):
        """Retrieve all user data"""
        try:
            self.cursor.execute("SELECT * FROM user_data")
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Data retrieval failed: {e}")
            return []

class ResumeParser:
    """Enhanced resume parsing with multiple methods"""
    
    def __init__(self):
        self.nlp = self._load_spacy()
        self.skill_matcher = self._build_skill_matcher()
    
    @st.cache_resource
    def _load_spacy(self):
        """Load spaCy model with caching"""
        try:
            import spacy
            return spacy.load("en_core_web_sm")
        except OSError:
            try:
                import subprocess
                import sys
                subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
                import spacy
                return spacy.load("en_core_web_sm")
            except Exception as e:
                logger.error(f"spaCy model loading failed: {e}")
                st.error("spaCy model could not be loaded. Please install it manually.")
                return None
    
    def _build_skill_matcher(self):
        """Build skill matcher for NLP processing"""
        if not self.nlp:
            return None
        
        from spacy.matcher import PhraseMatcher
        
        skills = {
            'python', 'java', 'javascript', 'html', 'css', 'react', 'angular', 'vue',
            'node.js', 'django', 'flask', 'sql', 'mongodb', 'aws', 'azure', 'docker',
            'kubernetes', 'git', 'machine learning', 'data science', 'ai', 'tensorflow',
            'pytorch', 'pandas', 'numpy', 'scikit-learn', 'tableau', 'power bi'
        }
        
        patterns = [self.nlp.make_doc(skill) for skill in skills]
        matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        matcher.add("SKILL", patterns)
        return matcher
    
    def extract_text_from_pdf(self, uploaded_file) -> str:
        """Extract text from PDF file"""
        try:
            from pypdf import PdfReader
            file_bytes = uploaded_file.read()
            reader = PdfReader(io.BytesIO(file_bytes))
            
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            
            return text.strip()
        except Exception as e:
            logger.error(f"PDF text extraction failed: {e}")
            return ""
    
    def parse_resume(self, text: str) -> Dict[str, Any]:
        """Parse resume text and extract information"""
        if not self.nlp or not text:
            return {}
        
        doc = self.nlp(text)
        
        # Extract basic information
        emails = self._extract_emails(text)
        phones = self._extract_phones(text)
        skills = self._extract_skills(doc)
        
        return {
            'name': self._extract_name(doc),
            'emails': emails,
            'phones': phones,
            'skills': skills,
            'education': self._extract_education(text),
            'experience': self._extract_experience(text)
        }
    
    def _extract_emails(self, text: str) -> List[str]:
        """Extract email addresses"""
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return list(set(re.findall(email_pattern, text)))
    
    def _extract_phones(self, text: str) -> List[str]:
        """Extract phone numbers"""
        import re
        phone_pattern = r'(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}|\d{5}[\s\-]?\d{5})'
        return list(set(re.findall(phone_pattern, text)))
    
    def _extract_name(self, doc) -> Optional[str]:
        """Extract name from document"""
        # Simple heuristic: first PERSON entity
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text.strip()
        return None
    
    def _extract_skills(self, doc) -> List[str]:
        """Extract skills using matcher"""
        if not self.skill_matcher:
            return []
        
        matches = self.skill_matcher(doc)
        skills = []
        for _, start, end in matches:
            skill = doc[start:end].text.strip().lower()
            if skill not in skills:
                skills.append(skill)
        return skills
    
    def _extract_education(self, text: str) -> List[str]:
        """Extract education information"""
        import re
        education_keywords = ['bachelor', 'master', 'phd', 'degree', 'university', 'college']
        lines = text.split('\n')
        education = []
        
        for line in lines:
            if any(keyword in line.lower() for keyword in education_keywords):
                education.append(line.strip())
        
        return education[:5]  # Limit to 5 entries
    
    def _extract_experience(self, text: str) -> List[str]:
        """Extract experience information"""
        import re
        lines = text.split('\n')
        experience = []
        
        for line in lines:
            if re.search(r'\b(20\d{2}|19\d{2})\b', line) and len(line.strip()) > 20:
                experience.append(line.strip())
        
        return experience[:10]  # Limit to 10 entries

class JobRecommender:
    """Handle job recommendations from multiple APIs"""
    
    @staticmethod
    def fetch_from_adzuna(skill: str, location: str = "India", results: int = 5) -> List[Dict]:
        """Fetch jobs from Adzuna API"""
        try:
            url = f"https://api.adzuna.com/v1/api/jobs/in/search/1"
            params = {
                "app_id": ADZUNA_APP_ID,
                "app_key": ADZUNA_API_KEY,
                "results_per_page": results,
                "what": skill,
                "where": location,
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                return response.json().get("results", [])
        except Exception as e:
            logger.error(f"Adzuna API error: {e}")
        return []
    
    @staticmethod
    def fetch_from_jooble(skills: List[str], location: str = "") -> List[Dict]:
        """Fetch jobs from Jooble API"""
        try:
            url = f"https://jooble.org/api/{JOOBLE_API_KEY}"
            keywords = ", ".join(skills[:3])  # Limit to first 3 skills
            
            payload = {
                "keywords": keywords,
                "location": location,
                "page": 1
            }
            
            response = requests.post(url, json=payload, timeout=10)
            if response.status_code == 200:
                return response.json().get("jobs", [])[:5]
        except Exception as e:
            logger.error(f"Jooble API error: {e}")
        return []

class SkillAnalyzer:
    """Analyze skills and provide recommendations"""
    
    SKILL_CATEGORIES = {
        "Data Science/Analytics": {
            "keywords": ['python', 'pandas', 'numpy', 'machine learning', 'tensorflow', 'pytorch'],
            "recommend": ['Data Visualization', 'Statistical Analysis', 'SQL', 'Power BI', 'Tableau']
        },
        "Web Development": {
            "keywords": ['html', 'css', 'javascript', 'react', 'angular', 'node.js'],
            "recommend": ['TypeScript', 'Next.js', 'GraphQL', 'MongoDB', 'AWS']
        },
        "Mobile Development": {
            "keywords": ['android', 'ios', 'flutter', 'react native', 'kotlin', 'swift'],
            "recommend": ['Firebase', 'App Architecture', 'UI/UX Design', 'API Integration']
        }
    }
    
    @classmethod
    def categorize_skills(cls, skills: List[str]) -> Dict[str, List[str]]:
        """Categorize skills into different domains"""
        categorized = {}
        skills_lower = [skill.lower() for skill in skills]
        
        for category, data in cls.SKILL_CATEGORIES.items():
            category_skills = []
            for skill in skills:
                if skill.lower() in data["keywords"]:
                    category_skills.append(skill)
            
            if category_skills:
                categorized[category] = category_skills
        
        return categorized
    
    @classmethod
    def recommend_skills(cls, current_skills: List[str]) -> Dict[str, List[str]]:
        """Recommend skills based on current skills"""
        recommendations = {}
        skills_lower = [skill.lower() for skill in current_skills]
        
        for category, data in cls.SKILL_CATEGORIES.items():
            if any(skill in skills_lower for skill in data["keywords"]):
                missing_skills = [skill for skill in data["recommend"] 
                               if skill.lower() not in skills_lower]
                if missing_skills:
                    recommendations[category] = missing_skills[:5]
        
        return recommendations

def calculate_resume_score(text: str) -> tuple[int, List[str]]:
    """Calculate resume score and provide tips"""
    text_lower = text.lower()
    score = 0
    tips = []
    
    sections = {
        'projects': 25,
        'skills': 25,
        'objective': 15,
        'achievements': 15,
        'certifications': 10,
        'declaration': 5,
        'hobbies': 5
    }
    
    for section, weight in sections.items():
        if section in text_lower:
            score += weight
        else:
            tips.append(f"Add {section.capitalize()} section to improve your resume")
    
    return score, tips

def display_job_recommendations(jobs: List[Dict], source: str):
    """Display job recommendations in a formatted way"""
    if not jobs:
        st.warning(f"No jobs found from {source}")
        return
    
    st.subheader(f"🔍 Jobs from {source}")
    
    for i, job in enumerate(jobs):
        with st.expander(f"Job {i+1}: {job.get('title', 'No Title')}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Company:** {job.get('company', {}).get('display_name', 'Unknown')}")
                st.write(f"**Location:** {job.get('location', {}).get('display_name', 'Not specified')}")
            
            with col2:
                if job.get('salary'):
                    st.write(f"**Salary:** {job['salary']}")
                
                apply_url = job.get('redirect_url') or job.get('link', '#')
                st.markdown(f"[Apply Now]({apply_url})")
            
            if job.get('description'):
                description = job['description'][:200] + "..." if len(job['description']) > 200 else job['description']
                st.write(f"**Description:** {description}")

def main():
    """Main application function"""
    # Initialize theme
    if "theme_mode" not in st.session_state:
        st.session_state.theme_mode = "dark"
    
    # Add custom CSS
    try:
        add_custom_css()
    except:
        pass
    
    # Header
    st.markdown("""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="font-size: 3em; margin-bottom: 0.2rem;">InternHunt</h1>
            <h3 style="color: #ccc; margin-top: 0;">Resume Analyzer & Job Finder</h3>
            <p style="color: #aaa; font-size: 1.1em;">
                Upload your resume and get smart internship recommendations based on your skills.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize components
    db_manager = DatabaseManager()
    resume_parser = ResumeParser()
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    choice = st.sidebar.selectbox("Choose an option:", ["User", "Admin"])
    
    if choice == "User":
        handle_user_interface(db_manager, resume_parser)
    else:
        handle_admin_interface(db_manager)
    
    # Footer
    try:
        add_footer()
    except:
        pass

def handle_user_interface(db_manager: DatabaseManager, resume_parser: ResumeParser):
    """Handle user interface and resume processing"""
    st.header("📄 Upload Your Resume")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file", 
        type=["pdf"],
        help="Upload your resume in PDF format for analysis"
    )
    
    if uploaded_file is not None:
        # Validate file size (max 5MB)
        if uploaded_file.size > 5 * 1024 * 1024:
            st.error("File size too large. Please upload a file smaller than 5MB.")
            return
        
        with st.spinner("Analyzing your resume..."):
            # Extract text
            resume_text = resume_parser.extract_text_from_pdf(uploaded_file)
            
            if not resume_text:
                st.error("Could not extract text from the PDF. Please ensure it's not a scanned image.")
                return
            
            # Parse resume
            resume_data = resume_parser.parse_resume(resume_text)
            
            if not resume_data:
                st.error("Could not parse resume data. Please try again.")
                return
        
        # Display extracted information
        display_resume_analysis(resume_data, resume_text, db_manager)

def display_resume_analysis(resume_data: Dict, resume_text: str, db_manager: DatabaseManager):
    """Display comprehensive resume analysis"""
    
    # Basic Information
    st.subheader("👤 Extracted Information")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Name:** {resume_data.get('name', 'Not found')}")
        st.write(f"**Email:** {', '.join(resume_data.get('emails', ['Not found']))}")
    
    with col2:
        st.write(f"**Phone:** {', '.join(resume_data.get('phones', ['Not found']))}")
    
    # Skills Analysis
    skills = resume_data.get('skills', [])
    if skills:
        st.subheader("🛠️ Skills Found")
        categorized_skills = SkillAnalyzer.categorize_skills(skills)
        
        if categorized_skills:
            for category, category_skills in categorized_skills.items():
                st.write(f"**{category}:** {', '.join(category_skills)}")
        else:
            st.write(', '.join(skills))
        
        # Skill Recommendations
        st.subheader("🚀 Recommended Skills to Learn")
        skill_recommendations = SkillAnalyzer.recommend_skills(skills)
        
        for category, recommended in skill_recommendations.items():
            st.write(f"**{category}:** {', '.join(recommended)}")
    
    # Resume Score
    score, tips = calculate_resume_score(resume_text)
    st.subheader("📊 Resume Score")
    
    # Score display with color coding
    if score >= 80:
        score_color = "green"
    elif score >= 60:
        score_color = "orange"
    else:
        score_color = "red"
    
    st.markdown(f"<h2 style='color: {score_color};'>Score: {score}/100</h2>", unsafe_allow_html=True)
    
    # Tips for improvement
    if tips:
        st.subheader("💡 Improvement Tips")
        for tip in tips:
            st.write(f"• {tip}")
    
    # Job Recommendations
    if skills:
        st.subheader("💼 Job Recommendations")
        
        location = st.text_input("Enter preferred location (optional):", placeholder="e.g., Mumbai, Delhi")
        
        if st.button("Get Job Recommendations"):
            with st.spinner("Fetching job recommendations..."):
                # Fetch from multiple sources
                adzuna_jobs = JobRecommender.fetch_from_adzuna(skills[0], location)
                jooble_jobs = JobRecommender.fetch_from_jooble(skills, location)
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    display_job_recommendations(adzuna_jobs, "Adzuna")
                
                with col2:
                    display_job_recommendations(jooble_jobs, "Jooble")
    
    # Save to database
    user_data = {
        'name': resume_data.get('name', 'Unknown'),
        'email': resume_data.get('emails', [''])[0] if resume_data.get('emails') else '',
        'score': score,
        'timestamp': datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S'),
        'pages': 1,  # Could be calculated from PDF
        'fields': list(SkillAnalyzer.categorize_skills(skills).keys()),
        'level': 'Fresher' if score < 40 else 'Intermediate' if score <= 70 else 'Experienced',
        'skills': skills,
        'recommended_skills': [skill for skills_list in SkillAnalyzer.recommend_skills(skills).values() for skill in skills_list],
        'courses': []  # Could be populated based on recommendations
    }
    
    if db_manager.insert_user_data(user_data):
        st.success("✅ Your data has been saved successfully!")

def handle_admin_interface(db_manager: DatabaseManager):
    """Handle admin interface for data viewing"""
    st.subheader("🔐 Admin Login")
    
    # Admin credentials (in production, use proper authentication)
    admins = {
        'admin': 'password123',
        'Shubham': 'Snamlien321',
        'Abhinav': 'Abhi@321',
        'Pragya': 'Pragya@321'
    }
    
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    
    if st.button("Login"):
        if username in admins and password == admins[username]:
            st.success(f"Welcome, {username}!")
            
            # Display user data
            data = db_manager.get_all_data()
            
            if data:
                df = pd.DataFrame(data, columns=[
                    'ID', 'Name', 'Email', 'Resume Score', 'Timestamp', 'Total Pages',
                    'Predicted Field', 'User Level', 'Actual Skills', 'Recommended Skills',
                    'Recommended Courses'
                ])
                
                st.subheader("📊 User Analytics")
                st.dataframe(df)
                
                # Download link
                csv = df.to_csv(index=False)
                b64 = base64.b64encode(csv.encode()).decode()
                href = f'<a href="data:file/csv;base64,{b64}" download="user_data.csv">📥 Download CSV Report</a>'
                st.markdown(href, unsafe_allow_html=True)
                
                # Basic analytics
                if len(df) > 0:
                    st.subheader("📈 Quick Stats")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric("Total Users", len(df))
                    
                    with col2:
                        avg_score = df['Resume Score'].astype(float).mean()
                        st.metric("Average Score", f"{avg_score:.1f}")
                    
                    with col3:
                        top_level = df['User Level'].mode().iloc[0] if len(df) > 0 else "N/A"
                        st.metric("Most Common Level", top_level)
            else:
                st.info("No user data found in the database.")
        else:
            st.error("❌ Invalid credentials")

if __name__ == "__main__":
    main()