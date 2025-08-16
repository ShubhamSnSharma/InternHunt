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
    def calculate_resume_score(resume_data: Dict[str, Any]) -> int:
        """Calculate resume score based on various factors"""
        score = 0
        
        # Basic information (30 points)
        if resume_data.get('name'):
            score += 10
        if resume_data.get('email'):
            score += 10
        if resume_data.get('mobile_number'):
            score += 10
        
        # Skills (40 points)
        skills = resume_data.get('skills', [])
        if skills:
            skill_score = min(len(skills) * 2, 40)  # Max 40 points for skills
            score += skill_score
        
        # Professional links (20 points)
        if resume_data.get('linkedin'):
            score += 10
        if resume_data.get('github'):
            score += 10
        
        # Content quality (10 points)
        raw_text = resume_data.get('raw_text', '')
        if len(raw_text) > 500:  # Reasonable amount of content
            score += 10
        
        return min(score, 100)  # Cap at 100
    
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
