"""
Configuration settings for the InternHunt application
"""
import os
from typing import Dict, Any

class Config:
    """Application configuration"""
    
    # Database settings
    DATABASE = {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'database': os.getenv('DB_NAME', 'cv'),
        'charset': 'utf8mb4'
    }
    
    # API Keys
    JOOBLE_API_KEY = os.getenv('JOOBLE_API_KEY', '')
    ADZUNA_APP_ID = os.getenv('ADZUNA_APP_ID', '')
    ADZUNA_API_KEY = os.getenv('ADZUNA_API_KEY', '')
    
    # File upload settings
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = ['pdf']
    
    # Application settings
    DEFAULT_THEME = os.getenv('DEFAULT_THEME', 'dark')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    
    # Admin credentials (in production, use proper authentication)
    ADMIN_USERS = {
        'admin': os.getenv('ADMIN_PASSWORD', 'change_me'),
        'Shubham': os.getenv('SHUBHAM_PASSWORD', 'Snamlien321'),
        'Abhinav': os.getenv('ABHINAV_PASSWORD', 'Abhi@321'),
        'Pragya': os.getenv('PRAGYA_PASSWORD', 'Pragya@321')
    }
    
    @classmethod
    def validate(cls) -> bool:
        """Validate configuration"""
        required_vars = [
            'JOOBLE_API_KEY',
            'ADZUNA_APP_ID', 
            'ADZUNA_API_KEY'
        ]
        
        missing = [var for var in required_vars if not getattr(cls, var)]
        
        if missing:
            print(f"Warning: Missing required environment variables: {missing}")
            return False
        
        return True