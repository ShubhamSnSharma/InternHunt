"""
Job scraping utilities (no external job APIs).

Sources implemented:
- Internshala (internships)
- GitHub repositories (signals like topics: internship/hiring)
- RemoteOK (jobs/internships)

Each scraper returns a list of normalized job dicts:
{
  'title': str,
  'company': str,
  'location': str,
  'tags': List[str],
  'salary': Optional[str],
  'posted_at': Optional[str],
  'url': str,
  'source': str,
}
"""
from __future__ import annotations

import time
import re
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
}


def _match_any(text: str, keywords: List[str]) -> bool:
    if not keywords:
        return True
    t = (text or "").lower()
    return any(kw.lower() in t for kw in keywords)


# ---------------- Internshala ----------------

def scrape_internshala(skills: List[str], location: str = "", max_pages: int = 1) -> List[Dict]:
    """Scrape Internshala internship listings using correct HTML selectors."""
    jobs: List[Dict] = []
    base = "https://internshala.com/internships"

    for page in range(1, max_pages + 1):
        url = f"{base}?page={page}" if page > 1 else base
        try:
            r = requests.get(url, headers=HEADERS, timeout=12)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "lxml")
            cards = soup.select("div.individual_internship")

            for card in cards:
                # Title
                title_el = card.select_one(".job-internship-name a") or card.select_one("a.job-title-href")
                title = title_el.get_text(strip=True) if title_el else "Internship"

                # URL via data-href attribute
                data_href = card.get("data-href")
                if isinstance(data_href, list):
                    data_href_str = " ".join(data_href).strip()
                else:
                    data_href_str = (data_href or "").strip()
                link = ("https://internshala.com" + data_href_str) if data_href_str else url

                # Company
                comp_el = card.select_one(".company-name") or card.select_one("h4 a")
                company = comp_el.get_text(strip=True) if comp_el else ""

                # Location
                loc_el = card.select_one("#location_names") or card.select_one(".locations a") or card.select_one(".location_link")
                location_text = loc_el.get_text(strip=True) if loc_el else ""

                # Stipend
                stip_el = card.select_one("span.stipend")
                stipend = stip_el.get_text(strip=True) if stip_el else None

                # Duration from .detail-row-1 items
                dur = None
                for item in card.select(".detail-row-1 .row-1-item"):
                    txt = item.get_text(strip=True)
                    if any(x in txt.lower() for x in ["month", "week", "day"]) and "\u20b9" not in txt:
                        dur = txt
                        break

                # Description snippet
                desc_el = card.select_one(".job-snippet, .internship_about, .desc")
                desc = desc_el.get_text(" ", strip=True) if desc_el else None

                text_blob = " ".join([title, company, location_text, desc or ""]).lower()
                if not _match_any(text_blob, skills):
                    continue

                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location_text,
                    "stipend": stipend,
                    "duration": dur,
                    "description": desc,
                    "posted_at": None,
                    "url": link,
                    "source": "internshala",
                })
            time.sleep(0.5)
        except Exception:
            continue
    return jobs

from urllib.parse import quote_plus

def scrape_internshala_by_keywords(query: str, location: str = "India", max_pages: int = 1) -> List[Dict]:
    """Scrape Internshala using keyword URL pattern with correct HTML selectors."""
    # Delegate to api_services implementation which has been verified against live pages
    try:
        from api_services import scrape_internshala_by_keywords as _impl
        return _impl(query, location, max_pages)
    except ImportError:
        pass

    # Fallback inline implementation
    jobs: List[Dict] = []
    q = quote_plus((query or "").strip())
    loc = quote_plus((location or "India").strip())
    base = f"https://internshala.com/internships/keywords-{q}"
    if loc and location.lower() not in ("india", ""):
        base += f"/in-{loc}"

    for page in range(1, max_pages + 1):
        url = base if page == 1 else f"{base}?page={page}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=12)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "lxml")
            cards = soup.select("div.individual_internship")
            for card in cards:
                title_el = card.select_one(".job-internship-name a") or card.select_one("a.job-title-href")
                title = title_el.get_text(strip=True) if title_el else "Internship"
                data_href = card.get("data-href")
                if isinstance(data_href, list):
                    data_href_str = " ".join(data_href).strip()
                else:
                    data_href_str = (data_href or "").strip()
                link = ("https://internshala.com" + data_href_str) if data_href_str else url
                comp_el = card.select_one(".company-name") or card.select_one("h4 a")
                company = comp_el.get_text(strip=True) if comp_el else ""
                loc_el = card.select_one("#location_names") or card.select_one(".locations a")
                location_text = loc_el.get_text(strip=True) if loc_el else location
                stip_el = card.select_one("span.stipend")
                stipend = stip_el.get_text(strip=True) if stip_el else None
                duration = None
                for item in card.select(".detail-row-1 .row-1-item"):
                    txt = item.get_text(strip=True)
                    if any(x in txt.lower() for x in ["month", "week", "day"]) and "\u20b9" not in txt:
                        duration = txt
                        break
                desc_el = card.select_one(".job-snippet, .internship_about, .desc")
                desc = desc_el.get_text(" ", strip=True) if desc_el else None
                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location_text,
                    "stipend": stipend,
                    "duration": duration,
                    "description": desc,
                    "url": link,
                    "source": "internshala",
                })
            time.sleep(0.5)
        except Exception:
            continue
    return jobs


# ---------------- GitHub repositories ----------------

def scrape_github_repos(skills: List[str], max_pages: int = 1) -> List[Dict]:
    """Scrape GitHub search for repos with topics indicating hiring/internships.
    This is heuristic and best effort. We filter by keywords and topics.
    """
    jobs: List[Dict] = []
    for page in range(1, max_pages + 1):
        # Search for repos with topics 'hiring' or 'internship'
        url = f"https://github.com/search?p={page}&q=topic%3Ahiring+OR+topic%3Ainternship&type=repositories"
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "lxml")
            items = soup.select("li.repo-list-item, div.search-title + div.mt-n1")
            for it in items:
                a = it.select_one("a.v-align-middle") or it.select_one("a.Link--primary")
                if not a:
                    continue
                href_val = a.get("href")
                if isinstance(href_val, list):
                    href_str = " ".join(href_val).strip()
                else:
                    href_str = (href_val or "").strip()
                if not href_str:
                    continue
                full_name = href_str.strip("/")
                repo_url = "https://github.com" + href_str
                desc_el = it.select_one("p")
                desc = desc_el.get_text(strip=True) if desc_el else ""
                meta = it.get_text(" ", strip=True).lower()
                text_blob = f"{full_name} {desc} {meta}".lower()
                if not _match_any(text_blob, skills):
                    continue
                jobs.append({
                    "title": f"Repository: {full_name}",
                    "company": "GitHub Repo",
                    "location": "Remote",
                    "tags": ["github", "repo", "hiring"],
                    "salary": None,
                    "posted_at": None,
                    "url": repo_url,
                    "source": "github",
                })
            time.sleep(1)
        except Exception:
            continue
    return jobs


# ---------------- RemoteOK ----------------

def scrape_remoteok(skills: List[str], location: str = "", max_pages: int = 1) -> List[Dict]:
    """Scrape RemoteOK listings (best effort; HTML may change)."""
    jobs: List[Dict] = []
    base = "https://remoteok.com/remote-dev-jobs"
    try:
        r = requests.get(base, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return jobs
        soup = BeautifulSoup(r.text, "lxml")
        rows = soup.select("tr.job")
        for row in rows:
            title_el = row.select_one("td.position h2") or row.select_one("a.preventLink") if row else None
            title = title_el.get_text(strip=True) if title_el else ""
            
            comp_el = row.select_one("td.company h3") or row.select_one("span.companyLink") if row else None
            company = comp_el.get_text(strip=True) if comp_el else ""
            
            tags = [t.get_text(strip=True) for t in row.select("td.tags a")] if row else []
            
            loc_el = row.select_one("div.location") or row.select_one("div.location.tooltip") if row else None
            location_text = loc_el.get_text(strip=True) if loc_el else "Remote"
            
            link_el = row.select_one("a.preventLink") or row.select_one("a") if row else None
            link_href = link_el.get("href") if link_el else None
            if isinstance(link_href, list):
                link_href_str = " ".join(link_href).strip()
            else:
                link_href_str = (link_href or "").strip()
            link = ("https://remoteok.com" + link_href_str) if link_href_str and link_href_str.startswith("/") else (link_href_str or base)
            text_blob = " ".join([title or "", company or "", " ".join(tags)]).lower()
            if not _match_any(text_blob, skills):
                continue
            jobs.append({
                "title": title,
                "company": company,
                "location": location_text or "Remote",
                "tags": tags,
                "salary": None,
                "posted_at": None,
                "url": link,
                "source": "remoteok",
            })
        time.sleep(1)
    except Exception:
        return jobs
    return jobs


def scrape_all(skills: List[str], location: str = "") -> List[Dict]:
    """Run all scrapers and return a combined list (deduplicated by URL)."""
    skills = [s for s in (skills or []) if s]
    collected = []
    
    # Run scrape_internshala
    try:
        collected.extend(scrape_internshala(skills, location))
    except Exception:
        pass

    # Run scrape_github_repos
    try:
        collected.extend(scrape_github_repos(skills))
    except Exception:
        pass

    # Run scrape_remoteok
    try:
        collected.extend(scrape_remoteok(skills, location))
    except Exception:
        pass

    # Dedup by URL
    seen = set()
    unique = []
    for j in collected:
        u = j.get("url")
        if not u or u in seen:
            continue
        seen.add(u)
        unique.append(j)
    return unique
