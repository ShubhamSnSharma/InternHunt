# Utility functions for InternHunt application
import base64
import os
import streamlit as st
from typing import Optional, List, Dict, Any
import pandas as pd

class FileUtils:
    """File handling utilities"""
    
    @staticmethod
    def ensure_directory_exists(directory_path: str) -> bool:
        """Ensure directory exists, create if it doesn't"""
        try:
            os.makedirs(directory_path, exist_ok=True)
            return True
        except Exception as e:
            st.error(f"Failed to create directory {directory_path}: {e}")
            return False
    
    @staticmethod
    def get_file_size(file_path: str) -> Optional[int]:
        """Get file size in bytes"""
        try:
            return os.path.getsize(file_path)
        except Exception:
            return None
    
    @staticmethod
    def is_valid_pdf(file) -> bool:
        """Check if uploaded file is a valid PDF"""
        if file is None:
            return False
        
        # Check file extension
        if not file.name.lower().endswith('.pdf'):
            return False
        
        # Check file size (max 10MB)
        if hasattr(file, 'size') and file.size > 10 * 1024 * 1024:
            st.error("File size too large. Please upload a PDF smaller than 10MB.")
            return False
        
        return True

class DataUtils:
    """Data processing utilities"""
    
    @staticmethod
    def get_download_link(df: pd.DataFrame, filename: str, text: str) -> str:
        """Generate download link for dataframe"""
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
        return href
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove special characters but keep basic punctuation
        import re
        text = re.sub(r'[^\w\s\-\.\@\(\)\+]', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def normalize_skill(skill: str) -> str:
        """Normalize skill name for comparison"""
        if not skill:
            return ""
        
        return skill.lower().strip().replace('-', ' ').replace('_', ' ')
    
    @staticmethod
    def calculate_match_score(user_skills: List[str], job_requirements: List[str]) -> float:
        """Calculate match score between user skills and job requirements"""
        if not user_skills or not job_requirements:
            return 0.0
        
        user_skills_normalized = [DataUtils.normalize_skill(skill) for skill in user_skills]
        job_requirements_normalized = [DataUtils.normalize_skill(req) for req in job_requirements]
        
        matches = 0
        for req in job_requirements_normalized:
            if any(req in skill or skill in req for skill in user_skills_normalized):
                matches += 1
        
        return (matches / len(job_requirements_normalized)) * 100

class ValidationUtils:
    """Input validation utilities"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Validate phone number format"""
        import re
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        # Check if it's between 10-15 digits
        return 10 <= len(digits_only) <= 15
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename for safe storage"""
        import re
        # Remove or replace unsafe characters
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Limit length
        if len(filename) > 255:
            name, ext = os.path.splitext(filename)
            filename = name[:255-len(ext)] + ext
        return filename

class UIUtils:
    """UI helper utilities"""
    
    @staticmethod
    def show_success_message(message: str, duration: int = 3):
        """Show success message with auto-dismiss"""
        success_placeholder = st.empty()
        success_placeholder.success(message)
        # Note: Streamlit doesn't support auto-dismiss, but this is a placeholder for future enhancement
    
    @staticmethod
    def show_progress_bar(current: int, total: int, text: str = "Processing..."):
        """Show progress bar"""
        progress = current / total if total > 0 else 0
        st.progress(progress, text=f"{text} ({current}/{total})")
    
    @staticmethod
    def create_metric_card(title: str, value: str, delta: Optional[str] = None):
        """Create a metric display card"""
        st.metric(label=title, value=value, delta=delta)
    
    @staticmethod
    def create_info_box(title: str, content: str, icon: str = "ℹ️"):
        """Create an information box"""
        st.markdown(f"""
        <div style="
            background-color: #f0f2f6;
            border-left: 4px solid #1f77b4;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 0.5rem;
        ">
            <h4 style="margin: 0 0 0.5rem 0; color: #1f77b4;">
                {icon} {title}
            </h4>
            <p style="margin: 0; color: #333;">
                {content}
            </p>
        </div>
        """, unsafe_allow_html=True)

class AnalyticsUtils:
    """Analytics and metrics utilities"""
    
    @staticmethod
    def calculate_resume_score_breakdown(resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Return a detailed breakdown: total, components, and suggestions.
        Improved scoring: adds quantified achievements, recency, diminishing returns for skills,
        and penalties for missing critical items.
        """
        import re
        total = 0.0
        components: Dict[str, float] = {
            "basic_info": 0.0,         # max 15
            "skills": 0.0,             # max 30
            "sections": 0.0,           # max 25
            "achievements": 0.0,       # max 15
            "recency": 0.0,            # max 10
            "links": 0.0,              # max 5
        }

        raw_text_full = (resume_data.get('raw_text') or '')
        raw_text = raw_text_full.lower()
        skills = resume_data.get('skills', []) or []

        # ---------- Basic information (max 15) ----------
        basic = 0.0
        basic += 6 if resume_data.get('name') else 0
        basic += 5 if resume_data.get('email') else 0
        basic += 4 if resume_data.get('mobile_number') else 0
        components["basic_info"] = basic
        total += basic

        # ---------- Skills (max 30) with diminishing returns and diversity bonus ----------
        uniq = list({(s or '').strip().lower() for s in skills if s})
        n = len(uniq)
        # Diminishing returns curve: up to ~10 effective points scaled to 30
        # eff = min(n, 12) mapped via sqrt curve
        import math
        eff = math.sqrt(min(n, 12)) / math.sqrt(12)  # 0..1
        skill_points = eff * 24  # base up to 24
        # Diversity bonus: mix of hard vs soft keywords in raw text
        soft_kw = ["leadership", "communication", "teamwork", "collaboration", "mentoring", "stakeholder"]
        hard_hit = sum(1 for s in uniq if re.search(r"[a-z]", s)) >= 5
        soft_hit = any(k in raw_text for k in soft_kw)
        if hard_hit and soft_hit:
            skill_points += 6  # bonus to reach 30
        components["skills"] = min(30.0, skill_points)
        total += components["skills"]

        # ---------- Sections (max 25) ----------
        def has_any(patterns):
            return any(re.search(p, raw_text, re.I) for p in patterns)
        has_exp = has_any([r"experience", r"work history", r"employment"])
        has_edu = has_any([r"education", r"b\.?tech|bachelor|master|b\.?e\.?|degree"])
        has_proj = has_any([r"projects?", r"publications?", r"case study", r"portfolio"])
        sec_pts = 0.0
        sec_pts += 12 if has_exp else 0
        sec_pts += 8 if has_edu else 0
        sec_pts += 5 if has_proj else 0
        components["sections"] = sec_pts
        total += sec_pts

        # ---------- Achievements (max 15): quantified impact ----------
        # Look for bullets/sentences with numbers, %, $ and action verbs
        sentences = re.split(r"[\.\!\?\n]+", raw_text_full)
        action_verbs = ["led", "managed", "increased", "reduced", "improved", "built", "designed", "shipped", "optimized", "launched", "delivered"]
        quantified = 0
        mentions = 0
        for s in sentences:
            s_l = s.lower()
            if any(v in s_l for v in action_verbs):
                mentions += 1
                if re.search(r"(\d+%|\$\d+|\b\d{1,4}\b)", s_l):
                    quantified += 1
        ach_ratio = quantified / mentions if mentions else 0.0
        ach_pts = min(15.0, 15.0 * ach_ratio)
        components["achievements"] = ach_pts
        total += ach_pts

        # ---------- Recency (max 10): recent years in resume ----------
        years = [int(y) for y in re.findall(r"\b(20\d{2}|19\d{2})\b", raw_text_full)]
        rec_pts = 0.0
        if years:
            latest = max(years)
            # Heuristic current year; avoid importing datetime for deterministic scoring
            current_year = 2025
            diff = current_year - latest
            if diff <= 1:
                rec_pts = 10.0
            elif diff <= 2:
                rec_pts = 8.0
            elif diff <= 4:
                rec_pts = 5.0
            elif diff <= 6:
                rec_pts = 2.0
        components["recency"] = rec_pts
        total += rec_pts

        # ---------- Links (max 5) ----------
        linkedin = resume_data.get('linkedin')
        github = resume_data.get('github')
        has_linkedin = bool(linkedin and (isinstance(linkedin, list) and len(linkedin) > 0 or isinstance(linkedin, str)))
        has_github = bool(github and (isinstance(github, list) and len(github) > 0 or isinstance(github, str)))
        link_pts = (3 if has_linkedin else 0) + (2 if has_github else 0)
        components["links"] = link_pts
        total += link_pts

        # ---------- Penalties (up to -15): missing contacts, too short, missing sections ----------
        penalties = 0.0
        length = len(raw_text)
        if length < 600:
            penalties += 6.0
        if not resume_data.get('email'):
            penalties += 4.0
        if not has_exp:
            penalties += 3.0
        if not has_edu:
            penalties += 2.0
        total = max(0.0, total - min(15.0, penalties))

        # Suggestions
        suggestions = AnalyticsUtils.get_improvement_suggestions(resume_data)
        # Add contextual suggestions based on new components
        if ach_pts < 10:
            suggestions.append("Quantify achievements with numbers or % (e.g., 'Improved latency by 30%').")
        if rec_pts < 5:
            suggestions.append("Add recent work/education (last 2–3 years) to show recency.")
        if components["skills"] < 20:
            suggestions.append("Include a balanced mix of hard and soft skills relevant to your target roles.")
        if components["sections"] < 20:
            suggestions.append("Ensure clear sections: Experience, Education, and Projects with bullet points.")
        if link_pts == 0:
            suggestions.append("Add your LinkedIn and GitHub (if applicable) for credibility.")

        # Compose output
        max_map = {"basic_info": 15, "skills": 30, "sections": 25, "achievements": 15, "recency": 10, "links": 5}
        # Round components for display
        components_rounded = {k: round(min(v, max_map[k]), 2) for k, v in components.items()}

        return {
            "total": int(min(round(total, 0), 100)),
            "components": components_rounded,
            "suggestions": suggestions,
        }

    @staticmethod
    def calculate_resume_score(resume_data: Dict[str, Any]) -> int:
        """Compatibility wrapper returning only the total score."""
        return AnalyticsUtils.calculate_resume_score_breakdown(resume_data)["total"]
    
    @staticmethod
    def categorize_user_level(resume_score: int, skills_count: int) -> str:
        """Categorize user level based on resume score and skills"""
        if resume_score >= 80 and skills_count >= 10:
            return "Advanced"
        elif resume_score >= 60 and skills_count >= 5:
            return "Intermediate"
        else:
            return "Beginner"
    
    @staticmethod
    def get_improvement_suggestions(resume_data: Dict[str, Any]) -> List[str]:
        """Get personalized improvement suggestions"""
        suggestions = []
        
        if not resume_data.get('name'):
            suggestions.append("Add your full name at the top of your resume")
        
        if not resume_data.get('email'):
            suggestions.append("Include a professional email address")
        
        if not resume_data.get('mobile_number'):
            suggestions.append("Add your phone number for easy contact")
        
        if not resume_data.get('linkedin'):
            suggestions.append("Add your LinkedIn profile URL")
        
        if not resume_data.get('github'):
            suggestions.append("Include your GitHub profile if you're in tech")
        
        skills = resume_data.get('skills', [])
        if len(skills) < 5:
            suggestions.append("Add more relevant skills to strengthen your profile")
        
        if len(resume_data.get('raw_text', '')) < 500:
            suggestions.append("Expand your resume with more detailed experience and achievements")
        
        return suggestions
