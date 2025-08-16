# API services module for job recommendations
import requests
import json
import streamlit as st
from typing import List, Dict, Optional
from config import Config

class JobAPIService:
    """Handles job API integrations"""
    
    @staticmethod
    def fetch_jobs_from_jooble(skills: List[str], location: str = "") -> Optional[List[Dict]]:
        """Fetch jobs from Jooble API"""
        url = f"https://jooble.org/api/{Config.JOOBLE_API_KEY}"
        
        # Combine all skills into a single search query
        keywords = ", ".join(skills)
        
        payload = {
            "keywords": keywords,
            "location": location,
            "page": 1
        }
        
        headers = {"Content-Type": "application/json"}
        
        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
            
            if response.status_code == 200:
                jobs = response.json().get("jobs", [])[:5]
                return jobs if jobs else None
            else:
                st.warning(f"Jooble API returned status code: {response.status_code}")
                return None
        
        except requests.exceptions.RequestException as e:
            st.error(f"Jooble API request failed: {e}")
            return None
        except Exception as e:
            st.error(f"Unexpected error with Jooble API: {e}")
            return None
    
    @staticmethod
    def get_jobs_from_adzuna(skill: str, location: str = "India", results: int = 10) -> List[Dict]:
        """Fetch jobs from Adzuna API"""
        url = f"https://api.adzuna.com/v1/api/jobs/{Config.ADZUNA_COUNTRY}/search/1"
        
        params = {
            "app_id": Config.ADZUNA_APP_ID,
            "app_key": Config.ADZUNA_API_KEY,
            "results_per_page": results,
            "what": skill,
            "where": location,
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                jobs = response.json()
                return jobs.get("results", [])
            else:
                st.warning(f"Adzuna API returned status code: {response.status_code}")
                return []
        
        except requests.exceptions.RequestException as e:
            st.error(f"Adzuna API request failed: {e}")
            return []
        except Exception as e:
            st.error(f"Unexpected error with Adzuna API: {e}")
            return []

class YouTubeService:
    """Handles YouTube video information fetching"""
    
    @staticmethod
    def fetch_yt_video(link: str) -> str:
        """Fetch YouTube video title"""
        try:
            with yt_dlp.YoutubeDL({}) as ydl:
                info = ydl.extract_info(link, download=False)
                return info.get('title', 'Unknown Title')
        except Exception as e:
            return f"Error fetching video: {e}"
