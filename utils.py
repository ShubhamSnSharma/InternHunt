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
    """Analytics and metrics utilities with ATS-style scoring"""
    
    # ATS keyword database for different industries/roles
    ATS_KEYWORDS = {
        'technical': {
            'programming': ['python', 'java', 'javascript', 'c++', 'c#', 'go', 'rust', 'scala', 'kotlin', 'swift'],
            'web_dev': ['html', 'css', 'react', 'angular', 'vue', 'nodejs', 'django', 'flask', 'express'],
            'data_ml': ['pandas', 'numpy', 'tensorflow', 'pytorch', 'scikit-learn', 'sql', 'machine learning', 'deep learning'],
            'devops': ['docker', 'kubernetes', 'aws', 'azure', 'gcp', 'ci/cd', 'terraform', 'jenkins'],
            'databases': ['mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch', 'oracle'],
        },
        'soft_skills': ['leadership', 'communication', 'teamwork', 'problem solving', 'analytical', 'project management', 'collaboration'],
        'action_verbs': ['developed', 'implemented', 'designed', 'managed', 'led', 'created', 'optimized', 'improved', 'built', 'deployed', 'maintained']
    }

    @staticmethod
    def calculate_resume_score_breakdown(resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """ATS-style scoring with weights:
        - Content Quality: 50%
        - Formatting: 15%
        - Keyword Relevance (incl. role alignment): 20%
        - Experience Recency/Impact: 10%
        - Grammar/Readability: 5%
        Applies refined penalties and caps scanned/image-like PDFs.
        """
        import re
        import math
        
        raw_text = (resume_data.get('raw_text') or '').strip()
        if not raw_text:
            return {"total": 0, "components": {}, "scores": {}, "suggestions": ["Resume text could not be parsed"], "feedback": "Unable to analyze resume"}
        
        # Heuristic for scanned/image-like PDFs: very few words
        word_count = len(re.findall(r"\w+", raw_text))
        scanned_like = word_count < 100
        
        scores = {
            'content_quality': 0.0,   # 50 max
            'formatting': 0.0,        # 15 max
            'keyword_relevance': 0.0, # 20 max
            'experience_impact': 0.0, # 10 max
            'readability': 0.0        # 5 max
        }
        components: Dict[str, float] = {}
        suggestions: List[str] = []
        strong_areas: List[str] = []
        weak_areas: List[str] = []
        
        # Content (scale 60->50)
        content_raw = AnalyticsUtils._analyze_content_quality(resume_data, raw_text)
        scores['content_quality'] = min(50.0, round(content_raw['total'] * (50.0/60.0), 2))
        components.update(content_raw['components'])
        suggestions.extend(content_raw['suggestions'])
        strong_areas.extend(content_raw['strong_areas'])
        weak_areas.extend(content_raw['weak_areas'])
        
        # Formatting (scale 20->15)
        fmt_raw = AnalyticsUtils._analyze_formatting_quality(raw_text)
        scores['formatting'] = min(15.0, round(fmt_raw['total'] * (15.0/20.0), 2))
        components.update({f"fmt_{k}": v for k, v in fmt_raw['components'].items()})
        suggestions.extend(fmt_raw['suggestions'])
        strong_areas.extend(fmt_raw['strong_areas'])
        weak_areas.extend(fmt_raw['weak_areas'])
        
        # Keyword relevance + role alignment
        kw_raw = AnalyticsUtils._analyze_keyword_relevance(resume_data, raw_text)
        scores['keyword_relevance'] = min(20.0, kw_raw['total'])
        components.update({f"kw_{k}": v for k, v in kw_raw['components'].items()})
        suggestions.extend(kw_raw['suggestions'])
        strong_areas.extend(kw_raw['strong_areas'])
        weak_areas.extend(kw_raw['weak_areas'])
        
        # Experience impact/recency
        exp_raw = AnalyticsUtils._analyze_experience_impact(raw_text)
        scores['experience_impact'] = min(10.0, exp_raw['total'])
        components.update({f"exp_{k}": v for k, v in exp_raw['components'].items()})
        suggestions.extend(exp_raw['suggestions'])
        strong_areas.extend(exp_raw['strong_areas'])
        weak_areas.extend(exp_raw['weak_areas'])
        
        # Grammar / readability
        read_raw = AnalyticsUtils._analyze_readability(raw_text)
        scores['readability'] = min(5.0, read_raw['total'])
        components.update({f"read_{k}": v for k, v in read_raw['components'].items()})
        suggestions.extend(read_raw['suggestions'])
        strong_areas.extend(read_raw['strong_areas'])
        weak_areas.extend(read_raw['weak_areas'])
        
        # Refined penalties
        sections = AnalyticsUtils._detect_resume_sections(raw_text)
        penalties = 0
        # Student heuristic: if no experience but has education/projects, lessen penalty
        is_student_like = (not sections.get('experience')) and (sections.get('education') or sections.get('projects')) and bool(re.search(r'\b(student|b\.?tech|bachelor|graduate|undergrad|university)\b', raw_text, re.I))
        if not sections['experience']:
            penalties += 10 if is_student_like else 25
            weak_areas.append('Experience section missing')
            suggestions.append('Add a Work Experience section with achievements and dates')
        if not sections['skills']:
            penalties += 15
            weak_areas.append('Skills section missing')
            suggestions.append('Add a dedicated Skills section with technologies and tools')
        if not sections['summary']:
            penalties += 5
            suggestions.append('Add a short Summary/Objective tailored to the target role')
        
        total_score = max(0.0, sum(scores.values()) - penalties)
        if scanned_like:
            suggestions.append('PDF looks image-based or too short; convert to a text-searchable PDF')
            total_score = min(total_score, 40.0)
        
        feedback = AnalyticsUtils._generate_ats_feedback(total_score, strong_areas, weak_areas, components)
        
        # Round numeric component values; keep strings/others as-is
        def _round_if_num(x):
            return round(x, 1) if isinstance(x, (int, float)) else x
        return {
            "total": int(min(round(total_score), 100)),
            "components": {k: _round_if_num(v) for k, v in components.items()},
            "scores": {k: round(v, 1) for k, v in scores.items()},
            "suggestions": suggestions[:10],
            "feedback": feedback,
            "strong_areas": strong_areas[:5],
            "weak_areas": weak_areas[:5]
        }
    
    @staticmethod
    def _analyze_content_quality(resume_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        """Analyze content quality (60% of total score)"""
        import re
        
        components = {}
        suggestions = []
        strong_areas = []
        weak_areas = []
        total = 0
        
        lines = raw_text.split('\n')
        
        # Contact Information (10 points)
        contact_score = 0
        if resume_data.get('name'):
            contact_score += 3
            strong_areas.append('Complete name provided')
        else:
            weak_areas.append('Missing name')
            suggestions.append('Add your full name prominently at the top')
            
        if resume_data.get('email'):
            contact_score += 3
            strong_areas.append('Professional email included')
        else:
            weak_areas.append('Missing email')
            suggestions.append('Include a professional email address')
            
        if resume_data.get('mobile_number'):
            contact_score += 2
        else:
            suggestions.append('Add your phone number for direct contact')
            
        if resume_data.get('linkedin') or resume_data.get('github'):
            contact_score += 2
            strong_areas.append('Professional profiles linked')
        else:
            suggestions.append('Include LinkedIn and relevant professional profiles')
            
        components['contact_info'] = contact_score
        total += contact_score
        
        # Section Completeness (target 25 points)
        sections = AnalyticsUtils._detect_resume_sections(raw_text)
        # Weights sum to 25
        sec_weights = {
            'experience': 12,
            'education': 6,
            'skills': 4,
            'summary': 2,
            'projects': 1,
        }
        sec_scored = {}
        for k, w in sec_weights.items():
            present = bool(sections.get(k))
            sec_scored[k] = w if present else 0
        section_score = sum(sec_scored.values())
        
        # Strengths/weaknesses
        if sections['experience']:
            strong_areas.append('Work experience section present')
        else:
            weak_areas.append('Missing work experience section')
            suggestions.append('Add detailed work experience with achievements')
        if sections['education']:
            strong_areas.append('Education section present')
        else:
            weak_areas.append('Missing education section')
            suggestions.append('Include your educational background')
        if sections['skills']:
            strong_areas.append('Skills section present')
        else:
            suggestions.append('Add a dedicated skills section')
        if not sections['summary']:
            suggestions.append('Consider adding a professional summary')
        
        components['sections'] = section_score
        components['sections_presence'] = sections
        components['sections_breakdown'] = {'weights': sec_weights, 'scored': sec_scored}
        total += section_score
        
        # Experience Quality (15 points)
        exp_score = AnalyticsUtils._analyze_experience_quality(raw_text)
        components['experience_quality'] = exp_score
        total += exp_score
        
        if exp_score < 8:
            suggestions.append('Use more action verbs and quantify achievements')
            weak_areas.append('Experience lacks quantified achievements')
        else:
            strong_areas.append('Well-documented experience with achievements')
        
        # Skills Assessment (10 points)
        skills = resume_data.get('skills', [])
        skill_score = min(10, len(skills) * 0.8) if skills else 0
        components['skills_count'] = skill_score
        total += skill_score
        
        if len(skills) < 8:
            suggestions.append('Expand your skills section with relevant technical and soft skills')
        
        # Evidence links near experience/projects (max 4)
        idxs = [i for i, l in enumerate(lines) if re.search(r'project|experience|work|internship', l, re.I)]
        evidence = 0
        for i in idxs:
            win = '\n'.join(lines[max(0, i-3):min(len(lines), i+4)])
            if re.search(r'(https?://|github\.com|colab|kaggle|demo|portfolio)', win, re.I):
                evidence += 1
        links_pts = min(4, evidence * 1.5)
        components['evidence_links'] = evidence
        components['links_quality'] = links_pts
        if evidence == 0 and sections.get('projects'):
            suggestions.append('Add GitHub/portfolio links near your projects to boost credibility')
        total += links_pts

        # Content Length and Depth (5 points)
        text_length = len(raw_text.strip())
        if text_length >= 2000:
            length_score = 5
            strong_areas.append('Comprehensive resume content')
        elif text_length >= 1200:
            length_score = 3
        elif text_length >= 600:
            length_score = 2
        else:
            length_score = 0
            weak_areas.append('Resume content too brief')
            suggestions.append('Expand resume with more detailed descriptions')
            
        components['content_depth'] = length_score
        total += length_score
        
        return {
            'total': total,
            'components': components,
            'suggestions': suggestions,
            'strong_areas': strong_areas,
            'weak_areas': weak_areas
        }
    
    @staticmethod
    def _role_alignment_score(resume_data: Dict[str, Any], skills: List[str], text_lower: str) -> (float, str):
        """Compute role alignment (0-8). If a target role is provided, score only against that role; otherwise choose best match."""
        import re, math
        clusters = {
            'Software Engineer': ['python','java','c++','git','data structures','algorithms','oop','docker','kubernetes','microservices','aws'],
            'Data Analyst': ['sql','excel','tableau','power bi','pandas','numpy','data analysis','visualization','statistics','matplotlib','seaborn'],
            'Web Developer': ['html','css','javascript','react','nodejs','express','django','flask','api','rest','frontend','backend'],
            'Machine Learning Engineer': ['python','pytorch','tensorflow','scikit-learn','ml','deep learning','model','training','inference','numpy','pandas'],
        }
        # Prefer an explicit target role if provided
        target_keys = ['target_role','job_type','desired_role','role']
        target_role = next((str(resume_data.get(k)).strip() for k in target_keys if resume_data.get(k)), None)
        
        def score_for(keys: List[str]) -> float:
            pts = 0.0
            for kw in keys:
                freq = len(re.findall(rf"\b{re.escape(kw)}\b", text_lower)) + (1 if kw in skills else 0)
                if freq:
                    pts += min(1.5, math.log2(1+freq))
            return pts
        
        # If user selected a role explicitly, compute alignment against that role only
        if target_role and any(target_role.lower() == r.lower() for r in clusters.keys()):
            keys = next(v for k, v in clusters.items() if k.lower() == target_role.lower())
            pts = score_for(keys)
            return min(8.0, pts), target_role
        
        # Otherwise, choose the best matching role automatically
        best_role, best_pts = 'General', -1.0
        for role, kws in clusters.items():
            cur = score_for(kws)
            if cur > best_pts:
                best_pts, best_role = cur, role
        return min(8.0, best_pts), best_role
    
    @staticmethod
    def _analyze_formatting_quality(raw_text: str) -> Dict[str, Any]:
        """Analyze formatting quality (20% of total score)"""
        import re
        
        components = {}
        suggestions = []
        strong_areas = []
        weak_areas = []
        total = 0
        
        # Section Headers (8 points)
        headers = re.findall(r'^([A-Z][A-Z\s]{2,30})\s*$', raw_text, re.MULTILINE)
        if len(headers) >= 4:
            header_score = 8
            strong_areas.append('Clear section headers used')
        elif len(headers) >= 2:
            header_score = 5
        else:
            header_score = 2
            weak_areas.append('Lacks clear section headers')
            suggestions.append('Use clear, uppercase section headers (EXPERIENCE, EDUCATION, etc.)')
            
        components['section_headers'] = header_score
        total += header_score
        
        # Bullet Points Usage (6 points)
        bullet_patterns = [r'•', r'\*', r'-', r'\d+\.']
        bullet_count = sum(len(re.findall(pattern, raw_text)) for pattern in bullet_patterns)
        
        if bullet_count >= 8:
            bullet_score = 6
            strong_areas.append('Good use of bullet points for readability')
        elif bullet_count >= 4:
            bullet_score = 4
        elif bullet_count >= 1:
            bullet_score = 2
        else:
            bullet_score = 0
            weak_areas.append('No bullet points used')
            suggestions.append('Use bullet points to improve readability and ATS parsing')
            
        components['bullet_points'] = bullet_score
        total += bullet_score
        
        # Consistent Spacing (3 points)
        lines = raw_text.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        if len(non_empty_lines) / len(lines) > 0.6:  # Good content-to-space ratio
            spacing_score = 3
            strong_areas.append('Well-structured layout')
        else:
            spacing_score = 1
            suggestions.append('Improve spacing and layout consistency')
            
        components['spacing'] = spacing_score
        total += spacing_score
        
        # Date Formatting (3 points)
        date_patterns = re.findall(r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|\d{1,2}/\d{1,2}/|\d{4})\b', raw_text)
        if len(date_patterns) >= 3:
            date_score = 3
            strong_areas.append('Consistent date formatting')
        elif len(date_patterns) >= 1:
            date_score = 2
        else:
            date_score = 0
            suggestions.append('Include dates for experience and education entries')
            
        components['date_formatting'] = date_score
        total += date_score
        
        return {
            'total': total,
            'components': components,
            'suggestions': suggestions,
            'strong_areas': strong_areas,
            'weak_areas': weak_areas
        }
    
    @staticmethod
    def _analyze_experience_impact(raw_text: str) -> Dict[str, Any]:
        """Analyze recency and quantified impact (max 10)."""
        import re, math
        components = {}
        suggestions = []
        strong_areas = []
        weak_areas = []
        total = 0.0
        # Recency (max 6)
        years = [int(y) for y in re.findall(r"\b(20\d{2})\b", raw_text)]
        recency = 0.0
        if years:
            latest = max(years)
            current_year = 2025
            diff = current_year - latest
            if diff <= 1:
                recency = 6.0
                strong_areas.append('Recent experience highlighted')
            elif diff <= 3:
                recency = 4.5
            elif diff <= 5:
                recency = 3.0
            else:
                recency = 1.0
                suggestions.append('Add more recent roles (last 3–5 years)')
        else:
            suggestions.append('Provide dates for experience entries')
        components['recency'] = recency
        total += recency
        # Quantified impact (max 4)
        quantifiers = re.findall(r'\b\d+%|\$\d+[\d,]*|\b\d+[\d,]*\+?\b', raw_text)
        impact = min(4.0, math.log2(1 + len(quantifiers)))
        components['quantified_impact'] = impact
        components['quantified_count'] = len(quantifiers)
        components['dates_found'] = bool(years)
        total += impact
        if impact < 2:
            suggestions.append('Quantify results (%, $ or numbers) to show impact')
        else:
            strong_areas.append('Achievements quantified with metrics')
        return {
            'total': total,
            'components': components,
            'suggestions': suggestions,
            'strong_areas': strong_areas,
            'weak_areas': weak_areas
        }
    
    @staticmethod
    def _analyze_keyword_relevance(resume_data: Dict[str, Any], raw_text: str) -> Dict[str, Any]:
        """Analyze keyword relevance (20%) with role alignment and frequency weighting."""
        import re, math
        components = {}
        suggestions = []
        strong_areas = []
        weak_areas = []
        total = 0.0
        
        text_lower = raw_text.lower()
        skills = [s.lower() for s in (resume_data.get('skills', []) or [])]
        
        # Role alignment (max 8)
        role_score, role_name = AnalyticsUtils._role_alignment_score(resume_data, skills, text_lower)
        components['role_alignment'] = round(role_score, 2)
        components['role_alignment_role'] = role_name
        # Build top-3 roles with matching keywords (why)
        clusters = {
            'Software Engineer': ['python','java','c++','git','data structures','algorithms','oop','docker','kubernetes','microservices','aws'],
            'Data Analyst': ['sql','excel','tableau','power bi','pandas','numpy','data analysis','visualization','statistics','matplotlib','seaborn'],
            'Web Developer': ['html','css','javascript','react','nodejs','express','django','flask','api','rest','frontend','backend'],
            'Machine Learning Engineer': ['python','pytorch','tensorflow','scikit-learn','ml','deep learning','model','training','inference','numpy','pandas'],
        }
        def role_pts(role, kws):
            import math, re
            pts = 0.0
            matched = []
            for kw in kws:
                freq = len(re.findall(rf"\b{re.escape(kw)}\b", text_lower)) + (1 if kw in skills else 0)
                if freq:
                    matched.append(kw)
                    pts += min(1.5, math.log2(1+freq))
            return pts, matched
        role_details = []
        for r, kws in clusters.items():
            pts, matched = role_pts(r, kws)
            role_details.append({'role': r, 'score': round(min(8.0, pts), 2), 'keywords': matched[:6]})
        role_details.sort(key=lambda x: x['score'], reverse=True)
        components['role_alignment_top'] = role_details[:3]
        total += role_score
        if role_score >= 6:
            strong_areas.append(f'Good alignment to role: {role_name}')
        else:
            weak_areas.append('Role alignment could be improved')
            suggestions.append('Tailor your resume to the target job (adjust headline/summary and skills)')
        
        # Technical keywords (max 7) - weighted by frequency
        tech_points = 0.0
        for _, keywords in AnalyticsUtils.ATS_KEYWORDS['technical'].items():
            cat_points = 0.0
            for kw in keywords:
                freq = len(re.findall(rf"\b{re.escape(kw)}\b", text_lower)) + (1 if kw in skills else 0)
                if freq > 0:
                    cat_points += min(1.5, math.log2(1 + freq))
            tech_points += min(2.5, cat_points)
        tech_score = min(7.0, tech_points)
        components['technical_keywords'] = round(tech_score, 2)
        total += tech_score
        if tech_score < 3:
            suggestions.append('Add more concrete technical keywords relevant to the target role')
        
        # Action verbs (max 3)
        action_matches = sum(len(re.findall(rf"\b{re.escape(v)}\b", text_lower)) for v in AnalyticsUtils.ATS_KEYWORDS['action_verbs'])
        action_score = min(3.0, math.log2(1 + action_matches))
        components['action_verbs'] = round(action_score, 2)
        components['action_verb_count'] = int(action_matches)
        total += action_score
        
        # Keyword stuffing detection
        stuffing = []
        for _, keywords in AnalyticsUtils.ATS_KEYWORDS['technical'].items():
            for kw in keywords:
                freq = len(re.findall(rf"\b{re.escape(kw)}\b", text_lower))
                if freq >= 8:
                    stuffing.append({'keyword': kw, 'count': int(freq)})
        if stuffing:
            components['keyword_stuffing'] = stuffing
            suggestions.append('Reduce repetitive keyword usage; excessive repeats can hurt ATS scores.')
        
        # Soft skills (max 1)
        soft_matches = sum(1 for s in AnalyticsUtils.ATS_KEYWORDS['soft_skills'] if s in text_lower)
        soft_score = min(1.0, soft_matches * 0.2)
        components['soft_skills'] = round(soft_score, 2)
        total += soft_score
        
        # Industry terms (max 1)
        industry_terms = ['agile', 'scrum', 'api', 'database', 'cloud', 'security', 'testing', 'debugging']
        industry_score = min(1.0, sum(1 for t in industry_terms if t in text_lower) * 0.2)
        components['industry_terms'] = round(industry_score, 2)
        total += industry_score
        
        return {
            'total': total,
            'components': components,
            'suggestions': suggestions,
            'strong_areas': strong_areas,
            'weak_areas': weak_areas
        }
    
    @staticmethod
    def _detect_resume_sections(raw_text: str) -> Dict[str, bool]:
        """Detect presence of key resume sections with broader coverage."""
        import re
        t = raw_text.lower()
        sections = {
            'summary': bool(re.search(r'\b(summary|professional summary|profile|objective|about me)\b', t)),
            'experience': bool(re.search(r'\b(experience|work history|professional experience|employment history|career history|professional background)\b', t)),
            'education': bool(re.search(r'\b(education|academic background|degree|university|college|school)\b', t)),
            'skills': bool(re.search(r'\b(skills|technical skills|core competencies|competencies|proficiencies|tech stack)\b', t)),
            'projects': bool(re.search(r'\b(projects|key projects|portfolio|selected projects|work samples)\b', t)),
            'certifications': bool(re.search(r'\b(certification|certifications|certificates|license|licenses)\b', t))
        }
        return sections
    
    @staticmethod
    def _analyze_experience_quality(raw_text: str) -> float:
        """Analyze quality of experience descriptions (within content quality)."""
        import re
        # Quantified achievements (more weight)
        quantifiers = re.findall(r'\b\d+%|\$\d+[\d,]*|\b\d+[\d,]*\+?\b', raw_text)
        q_score = min(9.0, len(quantifiers) * 0.9)
        # Action verbs
        action_verbs = ['developed', 'implemented', 'managed', 'led', 'created', 'improved', 'optimized', 'designed', 'launched', 'delivered']
        action_count = sum(1 for verb in action_verbs if re.search(rf"\b{re.escape(verb)}\b", raw_text.lower()))
        a_score = min(6.0, action_count * 0.8)
        return min(15.0, q_score + a_score)
    
    @staticmethod
    def _analyze_readability(raw_text: str) -> Dict[str, Any]:
        """Analyze grammar and readability (max 5). Use textstat or fallback heuristic; optionally grammar check."""
        components = {}
        suggestions = []
        strong_areas = []
        weak_areas = []
        score = 0.0
        # Try textstat
        try:
            import textstat  # type: ignore
            fre = textstat.flesch_reading_ease(raw_text)
            components['flesch_reading_ease'] = round(fre, 1)
            if fre >= 60:
                score = 5.0
                strong_areas.append('Clear, readable writing style')
            elif fre >= 45:
                score = 3.5
            elif fre >= 30:
                score = 2.0
            else:
                score = 1.0
                suggestions.append('Shorten sentences and simplify wording for clarity')
        except Exception:
            # Fallback based on average sentence length
            import re, math
            sentences = [s for s in re.split(r'[.!?\n]+', raw_text) if s.strip()]
            words = sum(len(s.split()) for s in sentences) or 1
            asl = words / max(1, len(sentences))
            components['avg_sentence_len'] = round(asl, 1)
            if asl <= 18:
                score = 4.0
                strong_areas.append('Concise, readable sentences')
            elif asl <= 25:
                score = 2.5
            else:
                score = 1.0
                suggestions.append('Use shorter sentences and bullets to improve readability')
        # Optional grammar check
        try:
            import language_tool_python  # type: ignore
            tool = language_tool_python.LanguageTool('en-US')
            matches = tool.check(raw_text[:10000])
            issues = len(matches)
            components['grammar_issues'] = issues
            if issues <= 5:
                score = min(5.0, score + 1.0)
                strong_areas.append('Few grammar issues detected')
            elif issues > 20:
                suggestions.append('Fix grammar issues; run a grammar checker')
        except Exception:
            pass
        return {
            'total': score,
            'components': components,
            'suggestions': suggestions,
            'strong_areas': strong_areas,
            'weak_areas': weak_areas
        }
    
    @staticmethod
    def _generate_ats_feedback(total_score: float, strong_areas: List[str], weak_areas: List[str], comp: Dict[str, Any]) -> str:
        """Return a styled HTML block for ATS feedback with chips and icon lists."""
        # Grade + summary
        if total_score >= 85:
            grade, color = "Excellent", "#10B981"  # green
            summary = "Your resume is well-optimized for ATS systems with strong content, keyword alignment, and formatting."
        elif total_score >= 70:
            grade, color = "Good", "#34D399"
            summary = "Your resume performs well in ATS scoring with a few areas to polish."
        elif total_score >= 55:
            grade, color = "Average", "#F59E0B"  # amber
            summary = "Your resume meets basic ATS requirements but needs optimization in multiple areas."
        else:
            grade, color = "Needs Improvement", "#EF4444"  # red
            summary = "Your resume needs significant improvements to pass ATS screening effectively."

        # Inline badges (hidden)
        badges = []

        # Deduplicate improvement items (normalize and collapse near-duplicates)
        import re
        def _canon(text: str) -> str:
            s = text.lower()
            s = re.sub(r"work\s+experience", "experience", s)
            s = re.sub(r"[^a-z0-9\s]+", " ", s)
            stop = {"the","a","an","your","section","sections","resume","cv"}
            toks = [t for t in s.split() if t and t not in stop]
            return " ".join(sorted(toks))
        uniq_weak: List[str] = []
        seen: List[str] = []
        for w in (weak_areas or []):
            if not w:
                continue
            cw = _canon(w)
            toks = set(cw.split())
            duplicate = False
            for prev in seen:
                ptoks = set(prev.split())
                inter = len(toks & ptoks)
                union = max(1, len(toks | ptoks))
                sim = inter / union
                if sim >= 0.8:
                    duplicate = True
                    break
            if not duplicate:
                uniq_weak.append(w)
                seen.append(cw)

        # Build HTML
        score_text = f"{int(total_score)}/100"
        html = []
        html.append("<div style='display:flex;flex-direction:column;gap:8px;'>")
        # Header
        html.append(
            f"<div style='display:flex;align-items:center;gap:10px;flex-wrap:wrap;'>"
            f"<span style='color:#E0E7FF;font-weight:800;'>ATS Score</span>"
            f"<span style='color:#E0E7FF;font-weight:800;'>{score_text}</span>"
            f"<span style='background:{color}26;color:{color};border:1px solid {color}66;padding:2px 8px;border-radius:999px;font-weight:700;'>"
            f"{grade}</span>"
            f"</div>"
        )
        # Summary
        html.append(f"<div style='color:#CBD5E1;font-size:13px;'>{summary}</div>")
        # Strengths
        if strong_areas:
            html.append("<div style='margin-top:4px;color:#93C5FD;font-weight:800;'>Strengths</div>")
            html.append("<ul style='margin:4px 0 0 18px;padding:0;list-style:none;'>")
            for s in strong_areas[:4]:
                html.append(f"<li style='margin:2px 0;color:#E0E7FF;'>✅ {s}</li>")
            html.append("</ul>")
        # Improvements
        if uniq_weak:
            html.append("<div style='margin-top:8px;color:#FCA5A5;font-weight:800;'>Areas for Improvement</div>")
            html.append("<ul style='margin:4px 0 0 18px;padding:0;list-style:none;'>")
            for w in uniq_weak[:5]:
                html.append(f"<li style='margin:2px 0;color:#E0E7FF;'>⚠️ {w}</li>")
            html.append("</ul>")
        html.append("</div>")
        return "".join(html)

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
