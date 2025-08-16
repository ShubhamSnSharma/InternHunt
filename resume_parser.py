# Resume parsing module for InternHunt
import io
import re
import spacy
import streamlit as st
from pypdf import PdfReader
from spacy.matcher import PhraseMatcher
from fuzzywuzzy import process, fuzz
from typing import List, Dict, Any, Optional
from config import Config

@st.cache_resource(show_spinner=False)
def load_spacy_model():
    """Load spaCy model with caching"""
    try:
        return spacy.load("en_core_web_sm")
    except OSError:
        try:
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            return spacy.load("en_core_web_sm")
        except Exception:
            st.error("spaCy model 'en_core_web_sm' is not installed and could not be downloaded automatically.")
            raise

class ResumeParser:
    """Enhanced resume parser using spaCy and rule-based extraction"""
    
    def __init__(self):
        self.nlp = self._load_spacy()
        self.valid_skills = self._get_valid_skills()
        self.skill_matcher = self._build_skill_matcher()
        
    def _load_spacy(self):
        """Load spaCy model, auto-install if missing"""
        return load_spacy_model()
    
    def _get_valid_skills(self) -> Dict[str, str]:
        """Get comprehensive list of valid skills"""
        skills = {
            # Programming languages
            'python', 'java', 'javascript', 'typescript', 'c', 'c++', 'c#', 'go', 'rust', 'kotlin', 'swift', 'ruby', 'php', 'r', 'matlab', 'scala',
            
            # Web frameworks
            'html', 'css', 'react', 'next.js', 'nextjs', 'angular', 'vue', 'svelte', 'node.js', 'nodejs', 'express', 'django', 'flask', 'fastapi', 'spring', 'spring boot', 'laravel', 'rails',
            
            # Data/ML/AI
            'pandas', 'numpy', 'scikit-learn', 'sklearn', 'tensorflow', 'keras', 'pytorch', 'nlp', 'computer vision', 'opencv', 'xgboost', 'lightgbm', 'matplotlib', 'seaborn', 'plotly',
            
            # Databases/Cloud/DevOps
            'sql', 'mysql', 'postgresql', 'sqlite', 'mongodb', 'redis', 'elasticsearch', 'aws', 'gcp', 'azure', 'docker', 'kubernetes', 'git', 'github', 'gitlab', 'ci/cd', 'terraform',
            
            # Hardware/Electrical
            'verilog', 'vhdl', 'systemverilog', 'fpga', 'pcb design', 'circuit design', 'digital design', 'analog design', 'vlsi', 'asic', 'embedded systems', 'arm', 'msp430', 'pic', 'arduino',
            
            # Mobile
            'android', 'ios', 'react native', 'swiftui', 'flutter',
            
            # Testing/Others
            'pytest', 'jest', 'cypress', 'playwright', 'graphql', 'rest', 'grpc', 'microservices'
        }
        
        return {skill.lower(): skill for skill in skills}
    
    def _build_skill_matcher(self):
        """Build spaCy phrase matcher for skills"""
        phrases = list(self.valid_skills.keys())
        patterns = [self.nlp.make_doc(p) for p in phrases]
        matcher = PhraseMatcher(self.nlp.vocab, attr="LOWER")
        matcher.add("SKILL", patterns)
        return matcher
    
    def read_pdf_text(self, uploaded_file) -> str:
        """Extract raw text from uploaded PDF"""
        try:
            file_bytes = uploaded_file.read()
            reader = PdfReader(io.BytesIO(file_bytes))
            pages = []
            
            for page in reader.pages:
                try:
                    pages.append(page.extract_text() or "")
                except Exception:
                    pages.append("")
            
            text = "\n".join(pages)
            # Normalize whitespace
            text = re.sub(r"[ \t]+", " ", text)
            text = re.sub(r"\n{3,}", "\n\n", text)
            return text.strip()
        except Exception as e:
            st.error(f"Error reading PDF: {e}")
            return ""
    
    def extract_contact_info(self, text: str) -> Dict[str, Any]:
        """Extract contact information from resume text"""
        email_pattern = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
        phone_pattern = re.compile(r"(?:\+?\d{1,3}[\s\-]?)?(?:\(?\d{3}\)?[\s\-]?\d{3}[\s\-]?\d{4}|\d{5}[\s\-]?\d{5})")
        url_pattern = re.compile(r"\b(?:https?://|www\.)[^\s<>)+]+", re.I)
        github_pattern = re.compile(r"github\.com/[A-Za-z0-9_.\-]+", re.I)
        linkedin_pattern = re.compile(r"(?:linkedin\.com/in/|linkedin\.com/pub/)[A-Za-z0-9\-\_/%]+", re.I)
        
        emails = list(dict.fromkeys(email_pattern.findall(text)))
        phones = list(dict.fromkeys(phone_pattern.findall(text)))
        urls = list(dict.fromkeys(url_pattern.findall(text)))
        github = list(dict.fromkeys(github_pattern.findall(text)))
        linkedin = list(dict.fromkeys(linkedin_pattern.findall(text)))
        
        return {
            "emails": emails,
            "phones": phones,
            "urls": urls,
            "github": github,
            "linkedin": linkedin
        }
    
    def extract_skills(self, text: str) -> List[str]:
        """Extract skills using fuzzy matching and NLP"""
        doc = self.nlp(text.lower())
        found_skills = set()
        
        # Use spaCy matcher
        matches = self.skill_matcher(doc)
        for _, start, end in matches:
            skill = doc[start:end].text.strip().lower()
            if skill in self.valid_skills:
                found_skills.add(self.valid_skills[skill])
        
        # Fuzzy matching for additional skills
        text_lower = text.lower()
        for skill_key, skill_value in self.valid_skills.items():
            if skill_key.replace("-", " ") in text_lower:
                found_skills.add(skill_value)
            else:
                # Fuzzy match
                result = process.extractOne(skill_key, [text_lower], scorer=fuzz.token_set_ratio)
                if result and result[1] >= Config.FUZZY_THRESHOLD:
                    found_skills.add(skill_value)
        
        return list(found_skills)
    
    def _first_nonempty_lines(self, text: str, n: int = 5) -> List[str]:
        """Get first n non-empty lines from text"""
        lines = []
        for line in text.split('\n'):
            if line.strip():
                lines.append(line.strip())
                if len(lines) >= n:
                    break
        return lines
    
    def extract_name(self, text: str) -> Optional[str]:
        """Extract candidate name using simplified heuristic approach"""
        # Get first 5 non-empty lines
        top_lines = self._first_nonempty_lines(text, n=5)
        top_text = "\n".join(top_lines)
        
        # Use spaCy NER on top lines
        top_doc = self.nlp(top_text)
        persons = [ent.text.strip() for ent in top_doc.ents if ent.label_ == "PERSON"]
        
        if persons:
            # Prefer a 2- or 3-token name
            persons.sort(key=lambda s: (abs(len(s.split())-2), -len(s)))
            return persons[0]
        
        # Fallback: first line with 2-4 capitalized words
        for line in top_lines:
            tokens = line.split()
            cap_words = [w for w in tokens if re.match(r"^[A-Z][a-zA-Z'\-]+$", w)]
            if 1 < len(cap_words) <= 4:
                return " ".join(cap_words)
        
        return None
    
    def parse_resume(self, uploaded_file) -> Dict[str, Any]:
        """Main parsing function"""
        text = self.read_pdf_text(uploaded_file)
        if not text:
            return {}
        
        name = self.extract_name(text)
        contacts = self.extract_contact_info(text)
        skills = self.extract_skills(text)
        
        return {
            "name": name,
            "email": contacts["emails"][0] if contacts["emails"] else None,
            "mobile_number": contacts["phones"][0] if contacts["phones"] else None,
            "skills": skills,
            "linkedin": contacts["linkedin"],
            "github": contacts["github"],
            "raw_text": text
        }
