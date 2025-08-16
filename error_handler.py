# Error handling module for InternHunt application
import streamlit as st
import logging
import traceback
from typing import Optional, Callable, Any
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('internhunt.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class ErrorHandler:
    """Centralized error handling for the application"""
    
    @staticmethod
    def handle_api_error(error: Exception, api_name: str) -> None:
        """Handle API-related errors"""
        logger.error(f"{api_name} API Error: {str(error)}")
        st.error(f"⚠️ {api_name} service is currently unavailable. Please try again later.")
    
    @staticmethod
    def handle_database_error(error: Exception) -> None:
        """Handle database-related errors"""
        logger.error(f"Database Error: {str(error)}")
        st.error("⚠️ Database connection issue. Some features may be limited.")
    
    @staticmethod
    def handle_file_error(error: Exception, filename: str = "") -> None:
        """Handle file processing errors"""
        logger.error(f"File Error ({filename}): {str(error)}")
        st.error(f"⚠️ Error processing file {filename}. Please ensure it's a valid PDF.")
    
    @staticmethod
    def handle_parsing_error(error: Exception) -> None:
        """Handle resume parsing errors"""
        logger.error(f"Parsing Error: {str(error)}")
        st.error("⚠️ Unable to parse resume. Please ensure the PDF contains readable text.")
    
    @staticmethod
    def handle_generic_error(error: Exception, context: str = "") -> None:
        """Handle generic errors"""
        logger.error(f"Generic Error ({context}): {str(error)}")
        st.error(f"⚠️ An unexpected error occurred. {context}")

def error_handler(error_type: str = "generic", context: str = ""):
    """Decorator for handling errors in functions"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if error_type == "api":
                    ErrorHandler.handle_api_error(e, context)
                elif error_type == "database":
                    ErrorHandler.handle_database_error(e)
                elif error_type == "file":
                    ErrorHandler.handle_file_error(e, context)
                elif error_type == "parsing":
                    ErrorHandler.handle_parsing_error(e)
                else:
                    ErrorHandler.handle_generic_error(e, context)
                return None
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, **kwargs) -> Optional[Any]:
    """Safely execute a function with error handling"""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        logger.error(f"Safe execution failed: {str(e)}")
        logger.error(traceback.format_exc())
        return None
