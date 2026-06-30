# Configuration file for InternHunt application
import os
from typing import Dict, Any
from dotenv import load_dotenv

# Attempt to import Streamlit to access secrets when available
try:
    import streamlit as st
except Exception:
    st = None

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration class"""
    
    # Database Configuration
    DB_CONFIG = {
        'host': os.getenv('DB_HOST'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'user': os.getenv('DB_USER'),
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME'),
        'charset': 'utf8mb4',
        'ssl': {
            'ca': os.getenv('CA_CERT_PATH'),
        } if os.getenv('CA_CERT_PATH') else None,   # Only include SSL if CA path is set
    }

    # API Keys
    JOOBLE_API_KEY = os.getenv('JOOBLE_API_KEY', '4d4c75a1-1761-49c7-a003-71ed93beaf52')
    ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID', '1178ed1c')
    ADZUNA_API_KEY = os.getenv('ADZUNA_API_KEY', '2e96a2f4573fff0502a2a081c21b6810')
    ADZUNA_COUNTRY = os.getenv('ADZUNA_COUNTRY', 'in')
    
    # AI Configuration (prefer env, then Streamlit secrets)
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY') or (st.secrets.get('GEMINI_API_KEY') if st else None)
    GEMINI_MODEL = os.getenv('GEMINI_MODEL') or (st.secrets.get('GEMINI_MODEL') if st else 'gemini-1.5-pro')

    # Third-party APIs (optional)
    INTERNSHALA_API_BASE = os.getenv('INTERNSHALA_API_BASE', '')  # e.g., https://your-internshala-api.example.com/api

    # Application Settings
    APP_TITLE = "InternHunt - Your Internship Finder"
    APP_ICON = 'Logo/InternHunt_logo.png'
    UPLOAD_DIR = './Uploaded_Resumes/'

    # Unified DB URL (preferred for Postgres/Neon)
    DATABASE_URL = os.getenv('DATABASE_URL') or (st.secrets.get('DATABASE_URL') if st else None)

    # Skill matching settings
    FUZZY_THRESHOLD = 50
    DIRECT_MATCH_WEIGHT = 1.0
    SIMILARITY_MATCH_WEIGHT = 0.5
    FIELD_SCORE_THRESHOLD = 0.5

    @classmethod
    def get_db_connection_string(cls) -> str:
        """Get database connection string"""
        return f"mysql://{cls.DB_CONFIG['user']}:{cls.DB_CONFIG['password']}@{cls.DB_CONFIG['host']}:{cls.DB_CONFIG['port']}/{cls.DB_CONFIG['database']}"

    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        # Reload environment variables to get latest values
        load_dotenv(override=True)
        
        issues = []
        warnings = []
        
        # Database is optional; prefer DATABASE_URL (Postgres/Neon). Warn if neither it nor full MySQL config is present.
        db_url = cls.DATABASE_URL or os.getenv('DATABASE_URL')
        db_fields = [cls.DB_CONFIG.get('host'), cls.DB_CONFIG.get('user'), cls.DB_CONFIG.get('password'), cls.DB_CONFIG.get('database')]
        if not db_url and not all(db_fields):
            warnings.append("Database not configured - running without persistence")
        
        # Check current API key from env or secrets
        current_api_key = os.getenv('GEMINI_API_KEY') or (st.secrets.get('GEMINI_API_KEY') if st else None)
        if not current_api_key or current_api_key == "your_gemini_api_key_here":
            warnings.append("Gemini API key not configured - chatbot features will be limited")
        
        if not os.path.exists(cls.UPLOAD_DIR):
            try:
                os.makedirs(cls.UPLOAD_DIR, exist_ok=True)
            except Exception as e:
                issues.append(f"Cannot create upload directory: {e}")
        
        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
