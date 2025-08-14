"""
Security utilities for the application
"""
import hashlib
import secrets
from typing import Optional
import streamlit as st

class SecurityManager:
    """Handle security-related operations"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate secure session token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def sanitize_sql_input(input_str: str) -> str:
        """Basic SQL injection prevention"""
        if not input_str:
            return ""
        
        # Remove potentially dangerous SQL keywords
        dangerous_keywords = [
            'DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE',
            'EXEC', 'EXECUTE', 'UNION', 'SELECT', '--', ';'
        ]
        
        sanitized = input_str
        for keyword in dangerous_keywords:
            sanitized = sanitized.replace(keyword.upper(), '')
            sanitized = sanitized.replace(keyword.lower(), '')
        
        return sanitized.strip()
    
    @staticmethod
    def check_file_safety(file_content: bytes) -> bool:
        """Basic file safety check"""
        # Check for PDF magic number
        if not file_content.startswith(b'%PDF'):
            return False
        
        # Check for suspicious content (basic)
        suspicious_patterns = [b'<script', b'javascript:', b'<iframe']
        
        for pattern in suspicious_patterns:
            if pattern in file_content:
                return False
        
        return True

class SessionManager:
    """Manage user sessions"""
    
    @staticmethod
    def initialize_session():
        """Initialize session state variables"""
        if 'authenticated' not in st.session_state:
            st.session_state.authenticated = False
        
        if 'user_role' not in st.session_state:
            st.session_state.user_role = None
        
        if 'session_token' not in st.session_state:
            st.session_state.session_token = None
    
    @staticmethod
    def login_user(username: str, role: str = 'user'):
        """Login user and create session"""
        st.session_state.authenticated = True
        st.session_state.user_role = role
        st.session_state.session_token = SecurityManager.generate_session_token()
        st.session_state.username = username
    
    @staticmethod
    def logout_user():
        """Logout user and clear session"""
        st.session_state.authenticated = False
        st.session_state.user_role = None
        st.session_state.session_token = None
        if 'username' in st.session_state:
            del st.session_state.username
    
    @staticmethod
    def is_authenticated() -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    @staticmethod
    def get_user_role() -> Optional[str]:
        """Get current user role"""
        return st.session_state.get('user_role')