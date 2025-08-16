# Database operations module for InternHunt
import pymysql
import streamlit as st
import logging
from typing import Optional, Dict, Any
from config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self._connect()
    
    def _connect(self):
        """Establish database connection"""
        try:
            # Only attempt connection if database credentials are provided
            if Config.DB_CONFIG.get('password') or Config.DB_CONFIG.get('user') != 'root':
                self.connection = pymysql.connect(**Config.DB_CONFIG)
                self.cursor = self.connection.cursor()
                self._initialize_database()
                logger.info("Database connected successfully")
            else:
                logger.info("Database credentials not configured - running without database features")
                self.connection = None
                self.cursor = None
        except Exception as e:
            logger.warning(f"Database connection failed: {e} - continuing without database features")
            self.connection = None
            self.cursor = None
    
    def _initialize_database(self):
        """Create database and tables if they don't exist"""
        try:
            # Create database
            self.cursor.execute("CREATE DATABASE IF NOT EXISTS cv;")
            self.cursor.execute("USE cv;")
            
            # Create user_data table
            create_table_sql = """
            CREATE TABLE IF NOT EXISTS user_data (
                ID INT NOT NULL AUTO_INCREMENT,
                Name VARCHAR(500) NOT NULL,
                Email_ID VARCHAR(500) NOT NULL,
                resume_score VARCHAR(8) NOT NULL,
                Timestamp VARCHAR(50) NOT NULL,
                Page_no VARCHAR(5) NOT NULL,
                Predicted_Field TEXT NOT NULL,
                User_level TEXT NOT NULL,
                Actual_skills TEXT NOT NULL,
                Recommended_skills TEXT NOT NULL,
                Recommended_courses TEXT NOT NULL,
                PRIMARY KEY (ID)
            );
            """
            self.cursor.execute(create_table_sql)
            self.connection.commit()
        except pymysql.MySQLError as e:
            logger.error(f"Database initialization failed: {e}")
    
    def insert_user_data(self, name: str, email: str, res_score: int, 
                        timestamp: str, no_of_pages: int, reco_field: str,
                        cand_level: str, skills: list, recommended_skills: list,
                        courses: list) -> bool:
        """Insert user data into database"""
        if not self.connection:
            logger.info("Database not available - skipping data insertion")
            return False
            
        try:
            insert_sql = """
            INSERT INTO user_data (Name, Email_ID, resume_score, Timestamp, Page_no, 
                                  Predicted_Field, User_level, Actual_skills, 
                                  Recommended_skills, Recommended_courses)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            values = (
                name,
                email,
                str(res_score),
                timestamp,
                str(no_of_pages),
                reco_field,
                cand_level,
                ', '.join(skills),
                ', '.join(recommended_skills),
                ', '.join(courses)
            )
            
            self.cursor.execute(insert_sql, values)
            self.connection.commit()
            logger.info("User data inserted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to insert user data: {e}")
            return False
    
    def get_user_data(self, limit: int = 100) -> Optional[list]:
        """Retrieve user data from database"""
        if not self.connection:
            return None
        
        try:
            self.cursor.execute(f"SELECT * FROM user_data ORDER BY ID DESC LIMIT {limit}")
            return self.cursor.fetchall()
        except pymysql.MySQLError as e:
            logger.error(f"Database query failed: {e}")
            return None
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.close()

# Global database instance
db_manager = DatabaseManager()
