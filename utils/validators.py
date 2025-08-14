"""
Input validation utilities
"""
import re
from typing import List, Optional
import streamlit as st

class FileValidator:
    """Validate uploaded files"""
    
    @staticmethod
    def validate_pdf(uploaded_file) -> tuple[bool, Optional[str]]:
        """Validate PDF file upload"""
        if not uploaded_file:
            return False, "No file uploaded"
        
        # Check file extension
        if not uploaded_file.name.lower().endswith('.pdf'):
            return False, "Only PDF files are allowed"
        
        # Check file size (5MB limit)
        if uploaded_file.size > 5 * 1024 * 1024:
            return False, "File size must be less than 5MB"
        
        # Check if file is empty
        if uploaded_file.size == 0:
            return False, "File is empty"
        
        return True, None

class DataValidator:
    """Validate data inputs"""
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number format"""
        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)
        # Check if it has 10-15 digits
        return 10 <= len(digits) <= 15
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        """Sanitize text input"""
        if not text:
            return ""
        
        # Remove potentially harmful characters
        sanitized = re.sub(r'[<>"\']', '', text)
        return sanitized.strip()
    
    @staticmethod
    def validate_location(location: str) -> bool:
        """Validate location input"""
        if not location:
            return True  # Optional field
        
        # Basic validation - only letters, spaces, commas
        pattern = r'^[a-zA-Z\s,.-]+$'
        return bool(re.match(pattern, location)) and len(location) <= 100

def display_validation_error(message: str):
    """Display validation error message"""
    st.error(f"❌ {message}")

def display_validation_success(message: str):
    """Display validation success message"""
    st.success(f"✅ {message}")