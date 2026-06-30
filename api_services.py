# API services module for job recommendations
import requests
import json
import streamlit as st
import os
from typing import List, Dict, Optional
from urllib.parse import urlencode, quote
from config import Config


class JobAPIService:
    """Handles job API integrations"""

    @staticmethod
    def fetch_jobs_from_jooble(skills: List[str], location: str = "") -> Optional[List[Dict]]:
        """Fetch jobs from Jooble API"""
        url = f"https://jooble.org/api/{Config.JOOBLE_API_KEY}"
        keywords = ", ".join([s for s in (skills or []) if s])
        headers = {"Content-Type": "application/json"}
        try:
            all_jobs: List[Dict] = []
            for pg in (1, 2):
                payload = {"keywords": keywords, "location": location or "", "page": pg}
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=10)
                if response.status_code != 200:
                    continue
                page_jobs = response.json().get("jobs", [])
                if page_jobs:
                    all_jobs.extend(page_jobs)
            jobs = all_jobs[:10]
            return jobs if jobs else None
        except requests.exceptions.RequestException:
            return None
        except Exception:
            return None

    @staticmethod
    def fetch_jobs_from_remotive(skills: List[str], location: str = "") -> Optional[List[Dict]]:
        """Fetch remote jobs from Remotive API (free, no key required).
        Docs: https://remotive.com/api/remote-jobs
        """
        query = " ".join([s for s in (skills or []) if s][:5])
        if not query:
            query = "software developer"

        url = "https://remotive.com/api/remote-jobs"
        params = {"search": query, "limit": 15}

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code != 200:
                return None

            results = response.json().get("jobs", [])
            jobs = []
            for item in results:
                company = item.get("company_name", "")
                candidate_loc = item.get("candidate_required_location", "Remote")
                tags = item.get("tags", [])
                salary = item.get("salary", "")
                jobs.append({
                    "title": item.get("title", ""),
                    "company": company,
                    "location": candidate_loc or "Remote",
                    "url": item.get("url", ""),
                    "link": item.get("url", ""),
                    "tags": tags[:5] if tags else ["Remote"],
                    "salary": salary if salary else None,
                    "posted_at": item.get("publication_date", ""),
                    "description": "",
                    "source": "remotive",
                })
            return jobs if jobs else None
        except Exception:
            return None


class YouTubeService:
    """Handles YouTube video information fetching"""

    @staticmethod
    def fetch_yt_video(link: str) -> str:
        """Fetch YouTube video title"""
        try:
            try:
                import yt_dlp  # type: ignore[import-not-found]
            except ImportError:
                return "YouTube service unavailable (install yt_dlp)"
            with yt_dlp.YoutubeDL({}) as ydl:
                info = ydl.extract_info(link, download=False)
                return info.get('title', 'Unknown Title')
        except Exception as e:
            return f"Error fetching video: {e}"


# ---------------------------------------------------------------------------
# Internshala scraper — HTML-based (their site is server-rendered for listing pages)
# ---------------------------------------------------------------------------

_INTERNSHALA_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://internshala.com/",
}


def _parse_internshala_cards(html: str, base_url: str) -> List[Dict]:
    """Parse internship cards from an Internshala listing page HTML."""
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        return []

    soup = BeautifulSoup(html, "lxml")
    cards = soup.select("div.individual_internship")
    results = []

    for card in cards:
        try:
            # Title
            title_el = card.select_one(".job-internship-name a") or card.select_one("a.job-title-href")
            title = title_el.get_text(strip=True) if title_el else "Internship"

            # data-href gives a reliable relative URL
            data_href = card.get("data-href")
            if isinstance(data_href, list):
                data_href_str = " ".join(data_href).strip()
            else:
                data_href_str = (data_href or "").strip()
            url = ("https://internshala.com" + data_href_str) if data_href_str else base_url

            # Company
            comp_el = card.select_one(".company-name") or card.select_one("h4 a")
            company = comp_el.get_text(strip=True) if comp_el else ""

            # Location
            loc_el = card.select_one("#location_names") or card.select_one(".locations a") or card.select_one(".location_link")
            location = loc_el.get_text(strip=True) if loc_el else "India"

            # Stipend — inside .stipend span
            stip_el = card.select_one("span.stipend")
            stipend = stip_el.get_text(strip=True) if stip_el else None

            # Duration — second .row-1-item inside .detail-row-1
            row1_items = card.select(".detail-row-1 .row-1-item")
            duration = None
            for item in row1_items:
                txt = item.get_text(strip=True)
                if any(x in txt.lower() for x in ["month", "week", "day"]) and "₹" not in txt:
                    duration = txt
                    break

            # Quick description from card text
            desc_el = card.select_one(".job-snippet, .internship_about, .desc")
            description = desc_el.get_text(" ", strip=True) if desc_el else None

            results.append({
                "title": title,
                "company": company,
                "location": location,
                "stipend": stipend,
                "duration": duration,
                "description": description,
                "url": url,
                "source": "internshala",
            })
        except Exception:
            continue

    return results


def scrape_internshala_by_keywords(query: str, location: str = "India", max_pages: int = 1) -> List[Dict]:
    """Scrape Internshala internship listings by keyword using the keyword URL pattern.
    URL: https://internshala.com/internships/keywords-{query}/in-{location}
    Falls back to generic listing if no results.
    """
    from urllib.parse import quote_plus
    collected: List[Dict] = []
    seen: set = set()

    def _add(items: List[Dict]) -> None:
        for it in items:
            key = it.get("url", "") or it.get("title", "")
            if key in seen:
                continue
            seen.add(key)
            collected.append(it)

    def _fetch(url: str) -> List[Dict]:
        try:
            r = requests.get(url, headers=_INTERNSHALA_HEADERS, timeout=12)
            if r.status_code != 200:
                return []
            return _parse_internshala_cards(r.text, url)
        except Exception:
            return []

    # Attempt 1: keyword URL pattern
    q = quote_plus((query or "").strip())
    loc = quote_plus((location or "India").strip())
    if q:
        kw_url = f"https://internshala.com/internships/keywords-{q}"
        if loc and location.lower() not in ("india", ""):
            kw_url += f"/in-{loc}"
        _add(_fetch(kw_url))

    if len(collected) >= 8:
        return collected[:10]

    # Attempt 2: first keyword only
    if query:
        first_kw = quote_plus(query.split(",")[0].strip())
        if first_kw and first_kw != q:
            _add(_fetch(f"https://internshala.com/internships/keywords-{first_kw}"))

    if len(collected) >= 8:
        return collected[:10]

    # Attempt 3: generic listing (no filters)
    _add(_fetch("https://internshala.com/internships"))

    return collected[:10]


# Keep legacy alias used in older parts of App.py
def fetch_internshala_internships(query: str, location: str = "India") -> Optional[List[Dict]]:
    """Legacy wrapper — delegates to the HTML scraper."""
    result = scrape_internshala_by_keywords(query, location)
    return result if result else None
