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
        # Try direct import first (more reliable)
        import en_core_web_sm
        return en_core_web_sm.load()
    except ImportError:
        # Fall back to spacy.load
        try:
            return spacy.load("en_core_web_sm")
        except OSError as e:
            st.error("""
            Error loading spaCy model 'en_core_web_sm'. 
            Please install it by running: 
            ```
            python -m spacy download en_core_web_sm
            ```
            and add 'en-core-web-sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1.tar.gz' to your requirements.txt
            """)
            st.error(f"Full error: {str(e)}")
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
            
            # Web frameworks / frontend
            'html', 'html5', 'css', 'css3', 'react', 'reactjs', 'next.js', 'nextjs', 'angular', 'vue', 'svelte', 'redux', 'tailwind', 'bootstrap', 'sass', 'less', 'vite', 'webpack', 'babel',
            'tailwindcss', 'nest.js', 'nestjs',
            
            # Backend / runtime
            'node.js', 'nodejs', 'express', 'django', 'flask', 'fastapi', 'laravel', 'rails', 'spring', 'spring boot', 'grpc', 'graphql', 'rest', 'openapi', 'swagger',
            'springboot',
            
            # Data/ML/AI
            'pandas', 'numpy', 'scikit-learn', 'sklearn', 'tensorflow', 'keras', 'pytorch', 'nlp', 'computer vision', 'opencv', 'xgboost', 'lightgbm', 'matplotlib', 'seaborn', 'plotly',
            'transformers', 'hugging face', 'yolo', 'langchain', 'nltk', 'spacy', 'streamlit',
            'machine learning', 'deep learning', 'neural networks', 'llm', 'generative ai', 'genai', 'natural language processing',
            
            # Data platforms / analytics
            'power bi', 'tableau', 'excel', 'pyspark', 'spark', 'hadoop', 'hive', 'airflow', 'looker', 'superset', 'google colab', 'colab',
            
            # Databases/Cloud/DevOps
            'sql', 'mysql', 'postgresql', 'postgres', 'sqlite', 'mongodb', 'redis', 'elasticsearch', 'aws', 'gcp', 'azure', 'docker', 'kubernetes',
            'git', 'github', 'gitlab', 'github actions', 'gitlab ci', 'ci/cd', 'terraform', 'linux', 'bash', 'shell', 'nginx', 'vscode', 'vs code', 'powerpoint', 'ms powerpoint',
            'ansible', 'jenkins', 'prometheus', 'grafana', 'devops', 'cloud computing',
            
            # Mobile
            'android', 'ios', 'react native', 'swiftui', 'flutter', 'firebase', 'supabase',
            
            # Testing/Others
            'pytest', 'jest', 'mocha', 'chai', 'cypress', 'playwright', 'selenium', 'beautifulsoup', 'postman',
            
            # Hardware/Electrical / Embedded
            'verilog', 'vhdl', 'systemverilog', 'fpga', 'pcb design', 'circuit design', 'digital design', 'analog design', 'vlsi', 'asic', 'embedded systems',
            'arm', 'arm cortex-m', 'stm32', 'esp32', 'raspberry pi', 'msp430', 'pic', 'arduino'
        }
        # Map variants/aliases to canonical names
        alias_map = {
            'reactjs': 'react',
            'nextjs': 'next.js',
            'nodejs': 'node.js',
            'postgres': 'postgresql',
            'postgresql': 'postgresql',
            'ci cd': 'ci/cd',
            'ci-cd': 'ci/cd',
            'c/c++': 'c++',
            'c & c++': 'c++',
            'c++11': 'c++', 'c++14': 'c++', 'c++17': 'c++', 'c++20': 'c++',
            'c language': 'c', 'c-lang': 'c',
            'golang': 'go',
            'python3': 'python', 'python 3': 'python', 'python 3.x': 'python',
            'java 8': 'java', 'java 11': 'java',
            'r (programming)': 'r',
            'bs4': 'beautifulsoup',
            'huggingface': 'hugging face',
            'google colaboratory': 'google colab',
            'google-colab': 'google colab',
            'vs-code': 'vs code',
            'visual studio code': 'vs code',
            'k8s': 'kubernetes',
            'k8s/kubernetes': 'kubernetes',
            'tailwind css': 'tailwind',
            'tailwindcss': 'tailwind',
            'nestjs': 'nest.js',
            'springboot': 'spring boot',
            'spring-boot': 'spring boot',
            'ml': 'machine learning',
            'ai': 'artificial intelligence',
            'artificial intelligence': 'artificial intelligence',
            'natural language processing': 'nlp',
            'genai': 'generative ai',
            'gen ai': 'generative ai'
        }
        normalized = {s.lower(): (alias_map.get(s.lower(), s)) for s in skills}
        # Ensure alias keys also exist
        for k, v in alias_map.items():
            normalized[k] = v
        return {k: normalized[k].title() if normalized[k] in ['aws','gcp','sql','nlp','fpga','vhdl','vlsi','asic','ios','grpc','ci/cd','llm'] else normalized[k] for k in normalized}
    
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
            # Reset file pointer to beginning in case it was read before
            uploaded_file.seek(0)
            file_bytes = uploaded_file.read()
            
            if not file_bytes:
                st.error("Uploaded file appears to be empty")
                return ""
            
            reader = PdfReader(io.BytesIO(file_bytes))
            pages = []
            
            for page in reader.pages:
                try:
                    text = page.extract_text()
                    pages.append(text or "")
                except Exception as page_error:
                    st.warning(f"Could not extract text from a page: {page_error}")
                    pages.append("")
            
            text = "\n".join(pages).strip()
            
            if not text:
                st.error("No text could be extracted from the PDF. This may be an image-only PDF or corrupted file.")
                return ""
            
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
    
    def _is_section_heading(self, line: str) -> bool:
        """Heuristic check for section headings (non-skill)."""
        l = line.strip().lower()
        non_skill_heads = [
            'experience', 'work experience', 'projects', 'education', 'certifications', 'achievements',
            'publications', 'summary', 'objective', 'profile', 'interests', 'hobbies', 'activities',
            'awards', 'responsibilities', 'internship', 'research', 'volunteer'
        ]
        if len(l) <= 2:
            return False
        return any(re.match(fr"^\s*{re.escape(h)}\b", l) for h in non_skill_heads)

    def _is_skills_heading(self, line: str) -> bool:
        l = line.strip().lower()
        skill_heads = [
            'skills', 'technical skills', 'skills & tools', 'skills and tools', 'tech stack',
            'technologies', 'technical proficiency', 'tooling', 'tools', 'frameworks',
            'programming', 'programming languages', 'languages'
        ]
        return bool(any(re.match(fr"^\s*{re.escape(h)}\b", l) for h in skill_heads) or re.match(r"^\s*skills\s*:\s*", l))

    def _collect_skills_windows(self, text: str) -> List[str]:
        """Extract text windows that likely represent the Skills section(s)."""
        lines = text.split('\n')
        windows: List[str] = []
        i = 0
        n = len(lines)
        while i < n:
            line = lines[i]
            if self._is_skills_heading(line):
                # Collect subsequent lines until next heading or a large gap
                buf = [line]
                i += 1
                empty_run = 0
                while i < n:
                    cur = lines[i]
                    if self._is_section_heading(cur) or self._is_skills_heading(cur):
                        break
                    if cur.strip() == '':
                        empty_run += 1
                        if empty_run >= 2 and buf:
                            break
                    else:
                        empty_run = 0
                        buf.append(cur)
                    # Hard cap to avoid swallowing the rest of the doc
                    if len(buf) > 60:
                        break
                    i += 1
                windows.append('\n'.join(buf))
            else:
                i += 1
        # Also capture inline blocks anywhere (Skills:, Programming:, Tech Stack:, Languages:)
        for line in lines:
            m = re.search(r"\b(skills|programming|tech\s*stack|languages)\s*:\s*(.+)", line, flags=re.IGNORECASE)
            if m:
                windows.append(m.group(2))
        return [w for w in windows if w and w.strip()]

    def _parse_structured_skills(self, text: str) -> List[str]:
        """Parse explicit labeled lines within Skills sections like 'Languages: ...'.
        Returns a flat list preserving order.
        """
        windows = self._collect_skills_windows(text)
        found: List[str] = []
        labels = [
            'languages', 'libraries/frameworks', 'libraries', 'frameworks', 'tools', 'tools/platforms',
            'databases', 'concepts', 'soft skills', 'soft-skills', 'programming', 'data science', 'machine learning', 'technologies'
        ]
        for win in windows:
            for line in win.split('\n'):
                m = re.match(r"^\s*(?:[-•–]\s*)?([A-Za-z /\-&]+)\s*:\s*(.+)$", line.strip())
                if not m:
                    continue
                label = m.group(1).strip().lower()
                values = m.group(2).strip()
                if any(label.startswith(l) for l in labels):
                    parts = re.split(r"[,;\u2022\u2023\u25E6\u2043\u2219]", values)
                    for p in parts:
                        token = p.strip().strip('.')
                        if not token:
                            continue
                        token = re.sub(r"\s*\(.*?\)$", "", token).strip()
                        found.append(token)
        # Additional pass over full text for Languages:/Tools:/Tech Stack:
        for m in re.finditer(r"(?im)^(?:[-•–]\s*)?(languages|tools|tech\s*stack)\s*:\s*(.+)$", text):
            values = m.group(2).strip()
            parts = re.split(r"[,;\u2022\u2023\u25E6\u2043\u2219]", values)
            for p in parts:
                token = re.sub(r"\s*\(.*?\)$", "", p.strip().strip('.')).strip()
                if token:
                    found.append(token)
        # de-dup preserve order
        ordered: List[str] = []
        seen = set()
        for s in found:
            if s not in seen:
                seen.add(s)
                ordered.append(s)
        return ordered

    def _match_skills(self, text: str, use_fuzzy: bool = False) -> List[str]:
        """Run matchers over given text and return normalized skills."""
        doc = self.nlp(text.lower())
        found = set()
        # Phrase matcher (exact-ish)
        for _, start, end in self.skill_matcher(doc):
            s = doc[start:end].text.strip().lower()
            if s in self.valid_skills:
                found.add(self.valid_skills[s])
        # Tokenize common list separators inside Skills blocks to catch variants
        tokens = re.split(r"[,/|•;\u2022\u2023\u25E6\u2043\u2219]|\s-\s|\n", text)
        for t in tokens:
            tt = t.strip().lower()
            if not tt or len(tt) > 60:
                continue
            # Strip parentheses content and trailing version numbers (e.g., "python 3.11")
            tt = re.sub(r"\(.*?\)", "", tt).strip()
            tt = re.sub(r"\s\d+(?:\.\d+)*$", "", tt).strip()
            # Normalize simple aliases (keys already exist in valid_skills)
            tt_norm = (tt
                .replace('react.js', 'react')
                .replace('next js', 'next.js')
                .replace('node js', 'node.js')
                .replace('postgre', 'postgresql')
                .replace('golang', 'go')
                .replace('c language', 'c')
            )
            if tt_norm in self.valid_skills:
                found.add(self.valid_skills[tt_norm])
        if use_fuzzy:
            text_lower = text.lower()
            tokens_clean = []
            for t in re.split(r"[,/|•;\u2022\u2023\u25E6\u2043\u2219]|\s-\s|\n", text):
                tt = t.strip().lower()
                tt = re.sub(r"\(.*?\)", "", tt).strip()
                tt = re.sub(r"\s\d+(?:\.\d+)*$", "", tt).strip()
                if tt and len(tt) <= 60:
                    tokens_clean.append(tt)
            
            for key, val in self.valid_skills.items():
                # Exact whole-word presence (safe for short tokens)
                key_re = re.compile(rf"\b{re.escape(key)}\b", flags=re.IGNORECASE)
                if key_re.search(text_lower):
                    found.add(val)
                    continue
                # Fuzzy check only on individual tokens to catch typos without false positives
                if len(key) >= 4 and key not in {'html', 'css'} and tokens_clean:
                    best_match = process.extractOne(key, tokens_clean, scorer=fuzz.ratio)
                    if best_match and best_match[1] >= 80:
                        found.add(val)
        return sorted(found)

    def extract_skills(self, text: str) -> List[str]:
        """Extract skills prioritizing explicit Skills sections; add safe language fallback."""
        structured = self._parse_structured_skills(text)
        skills_sections = self._collect_skills_windows(text)
        collected: List[str] = []
        for win in skills_sections:
            collected.extend(self._match_skills(win, use_fuzzy=True))
            
        # Combine both while preserving order
        combined = []
        seen = set()
        for s in structured:
            if s.lower() not in seen:
                seen.add(s.lower())
                combined.append(s)
        for s in collected:
            if s.lower() not in seen:
                seen.add(s.lower())
                combined.append(s)
                
        if combined:
            return combined
        # Safe fallback: detect only programming languages across full text
        languages = {'python','java','javascript','typescript','go','golang','rust','c','c++','c#','kotlin','swift','ruby','php','r','scala','matlab'}
        text_lower = text.lower()
        found_langs = []
        if re.search(r"\b(programming|languages|tech\s*stack|stack)\b", text_lower):
            for lang in languages:
                if lang in {'c++','c#'}:
                    if re.search(r"\bc\+\+\b", text_lower) and lang == 'c++':
                        found_langs.append('C++')
                    if re.search(r"\bc#\b", text_lower) and lang == 'c#':
                        found_langs.append('C#')
                    continue
                if re.search(rf"\b{re.escape(lang)}\b", text_lower):
                    canonical = {'golang':'go'}.get(lang, lang)
                    pretty = self.valid_skills.get(canonical, canonical)
                    found_langs.append(pretty if isinstance(pretty, str) else canonical)
        return sorted(list(dict.fromkeys(found_langs)))
    
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
        """Extract candidate name using improved heuristic approach"""
        # Get first 5 non-empty lines
        top_lines = self._first_nonempty_lines(text, n=5)
        top_text = "\n".join(top_lines)
        
        # Method 1: Look for name patterns in the first few lines
        name_candidates = []
        
        # Check first 3 lines for name patterns
        for i, line in enumerate(top_lines[:3]):
            # Skip lines that look like contact info, headers, or URLs
            if self._is_contact_or_header_line(line):
                continue
                
            # Look for capitalized name patterns
            name = self._extract_name_from_line(line)
            if name and self._is_valid_name(name):
                name_candidates.append((name, i))  # (name, line_index)
        
        # If we found valid names, return the one from the earliest line
        if name_candidates:
            name_candidates.sort(key=lambda x: x[1])  # Sort by line index
            return name_candidates[0][0]
        
        # Method 2: Use spaCy NER as fallback, but with better filtering
        top_doc = self.nlp(top_text)
        persons = []
        for ent in top_doc.ents:
            if ent.label_ == "PERSON":
                person_text = ent.text.strip()
                # Filter out obvious non-names
                if self._is_valid_name(person_text) and not self._contains_url_or_email(person_text):
                    persons.append(person_text)
        
        if persons:
            # Prefer 2-3 word names, then by length
            persons.sort(key=lambda s: (abs(len(s.split())-2), -len(s)))
            return persons[0]
        
        return None
    
    def _is_contact_or_header_line(self, line: str) -> bool:
        """Check if line contains contact info or headers"""
        line_lower = line.lower()
        contact_indicators = [
            'phone', 'email', 'mobile', 'contact', 'address', 'linkedin', 'github',
            'curriculum vitae', 'resume', 'cv', 'projects', 'experience', 'education',
            'skills', 'objective', 'summary', 'profile'
        ]
        return any(indicator in line_lower for indicator in contact_indicators)
    
    def _extract_name_from_line(self, line: str) -> Optional[str]:
        """Extract potential name from a single line"""
        # Remove common prefixes/suffixes
        line = re.sub(r'^(mr\.?|ms\.?|mrs\.?|dr\.?)\s*', '', line, flags=re.IGNORECASE)
        
        # Split into tokens and find capitalized words
        tokens = line.split()
        cap_words = []
        
        for token in tokens:
            # Match capitalized words (allowing for hyphens and apostrophes)
            if re.match(r"^[A-Z][a-zA-Z'\-]+$", token):
                cap_words.append(token)
            else:
                # If we hit a non-capitalized word, stop (names are usually consecutive)
                break
        
        # Return if we have 2-4 capitalized words
        if 2 <= len(cap_words) <= 4:
            return " ".join(cap_words)
        
        return None
    
    def _is_valid_name(self, name: str) -> bool:
        """Validate if extracted text looks like a real person's name"""
        if not name or len(name.strip()) < 2:
            return False
        
        name = name.strip()
        words = name.split()
        
        # Must have 2-4 words
        if not (2 <= len(words) <= 4):
            return False
        
        # Each word should be 2+ characters and start with capital letter
        for word in words:
            if len(word) < 2 or not re.match(r"^[A-Z][a-zA-Z'\-]*$", word):
                return False
        
        # Check for common non-name patterns
        name_lower = name.lower()
        non_name_patterns = [
            'university', 'college', 'institute', 'company', 'corporation', 'inc', 'ltd',
            'department', 'school', 'academy', 'center', 'centre', 'group', 'team',
            'project', 'research', 'development', 'engineering', 'technology', 'science',
            'curriculum', 'vitae', 'resume', 'cv', 'profile', 'summary', 'objective',
            'software', 'engineer', 'developer', 'analyst', 'manager', 'director',
            'specialist', 'consultant', 'coordinator', 'administrator', 'supervisor'
        ]
        
        if any(pattern in name_lower for pattern in non_name_patterns):
            return False
        
        # Additional validation: check if it looks like a job title
        job_title_indicators = ['engineer', 'developer', 'analyst', 'manager', 'specialist', 'consultant']
        if any(indicator in name_lower for indicator in job_title_indicators):
            return False
        
        return True
    
    def _contains_url_or_email(self, text: str) -> bool:
        """Check if text contains URL or email patterns"""
        url_pattern = r'https?://|www\.|\.com|\.org|\.net|\.edu|\.gov'
        email_pattern = r'@'
        return bool(re.search(url_pattern, text, re.IGNORECASE) or re.search(email_pattern, text))
    
    def parse_resume(self, uploaded_file) -> Dict[str, Any]:
        """Main parsing function"""
        try:
            # Check if file is valid
            if not uploaded_file:
                st.error("❌ No file provided for parsing")
                return {}
            
            text = self.read_pdf_text(uploaded_file)
            
            # Check if text is empty or scanned/image-like (very few words)
            word_count = len(re.findall(r"\w+", text)) if text else 0
            
            if word_count < 50:
                try:
                    uploaded_file.seek(0)
                    pdf_bytes = uploaded_file.read()
                    if pdf_bytes:
                        # Inform user we are running AI OCR
                        st.info("🔮 Scanned or low-text PDF detected. Running AI-powered OCR fallback...")
                        from chat_service import parse_resume_via_gemini
                        ocr_text = parse_resume_via_gemini(pdf_bytes)
                        if ocr_text and len(re.findall(r"\w+", ocr_text)) >= 50:
                            text = ocr_text
                            st.success("✅ AI OCR text extraction successful!")
                except Exception as ocr_err:
                    st.warning(f"⚠️ AI OCR extraction fallback failed: {ocr_err}")
            
            if not text:
                st.error("❌ Failed to extract text from PDF")
                return {}
            
            # Extract data
            name = self.extract_name(text)
            contacts = self.extract_contact_info(text)
            skills = self.extract_skills(text)
            
            result = {
                "name": name,
                "email": contacts["emails"][0] if contacts["emails"] else None,
                "mobile_number": contacts["phones"][0] if contacts["phones"] else None,
                "skills": skills,
                "linkedin": contacts["linkedin"],
                "github": contacts["github"],
                "raw_text": text,
                "total_experience": 0  # Add default experience
            }
            
            # Check if result has meaningful data - at minimum we need name OR skills OR email
            if not any([name, skills, contacts.get("emails")]):
                st.warning("⚠️ No meaningful data extracted from resume. Please check if the PDF contains readable text.")
                st.info("**Troubleshooting tips:**\n- Ensure PDF is text-searchable (not just scanned images)\n- Try OCR conversion if document is image-based\n- Check file isn't corrupted")
                return {}
            
            # No success banner (per design) — just return parsed result
            return result
            
        except Exception as e:
            st.error(f"❌ Unexpected error during resume parsing: {str(e)}")
            return {}
