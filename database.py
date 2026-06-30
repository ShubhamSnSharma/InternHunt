# Database operations module for InternHunt
import os
import logging
import streamlit as st
from typing import Optional, Dict, Any
import pymysql
import psycopg2
from urllib.parse import urlparse
from config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self):
        self.connection = None
        self.cursor = None
        self._connect()
    
    def _connect(self):
        """Establish database connection (Postgres via DATABASE_URL preferred)."""
        try:
            db_url = getattr(Config, 'DATABASE_URL', None)
            if db_url:
                # Postgres (Neon) path
                self.engine_type = 'postgres'
                # Ensure SSL for Neon if not provided
                needs_ssl = ('sslmode=' not in db_url)
                conn_kwargs: dict[str, str] = {}
                if needs_ssl:
                    conn_kwargs['sslmode'] = 'require'
                self.connection = psycopg2.connect(db_url, **conn_kwargs)  # type: ignore[call-overload]
                self.cursor = self.connection.cursor()
                self._initialize_database()
                logger.info("Connected to Postgres (DATABASE_URL)")
                return
            # Fallback to MySQL if configured
            if Config.DB_CONFIG.get('host') and Config.DB_CONFIG.get('user') and Config.DB_CONFIG.get('database'):
                self.engine_type = 'mysql'
                self.connection = pymysql.connect(**Config.DB_CONFIG)  # type: ignore[call-overload]
                self.cursor = self.connection.cursor()
                self._initialize_database()
                logger.info("Connected to MySQL")
            else:
                logger.info("Database not configured - running without persistence")
                self.connection = None
                self.cursor = None
        except Exception as e:
            logger.warning(f"Database connection failed: {e} - continuing without database features")
            self.connection = None
            self.cursor = None
    
    def _initialize_database(self):
        """Create required tables in the connected database if they don't exist.
        Note: Managed cloud providers may restrict CREATE DATABASE; we only create tables.
        """
        try:
            if getattr(self, 'engine_type', 'mysql') == 'postgres':
                create_table_sql = """
                CREATE TABLE IF NOT EXISTS user_data (
                    ID SERIAL PRIMARY KEY,
                    Name VARCHAR(500) NOT NULL,
                    Email_ID VARCHAR(500) NOT NULL,
                    resume_score VARCHAR(8) NOT NULL,
                    Timestamp VARCHAR(50) NOT NULL,
                    Page_no VARCHAR(5) NOT NULL,
                    Predicted_Field TEXT NOT NULL,
                    User_level TEXT NOT NULL,
                    Actual_skills TEXT NOT NULL,
                    Recommended_skills TEXT NOT NULL,
                    Recommended_courses TEXT NOT NULL
                );
                """
            else:
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
            if self.cursor is None or self.connection is None:
                return
            self.cursor.execute(create_table_sql)
            self.connection.commit()
        except Exception as e:
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
            
            if self.cursor is None or self.connection is None:
                return False
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
            if self.cursor is None:
                return None
            self.cursor.execute(f"SELECT * FROM user_data ORDER BY ID DESC LIMIT {limit}")
            return self.cursor.fetchall()
        except Exception as e:
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
