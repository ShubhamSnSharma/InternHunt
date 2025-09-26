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
    """Scrape Internshala internship listings.
    Note: Public pages are paginated; we keep it light with max_pages.
    """
    jobs: List[Dict] = []
    base = "https://internshala.com/internships"
    params_common = []
    if location:
        params_common.append(f"location={requests.utils.quote(location)}")
    query = "&".join(params_common) if params_common else ""

    for page in range(1, max_pages + 1):
        url = f"{base}?page={page}{('&' + query) if query else ''}"
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, "lxml")
            cards = soup.select("div.container-fluid.individual_internship")
            for card in cards:
                title = (card.select_one("a.job-title") or card.select_one("h3\n a")).get_text(strip=True) if card else "Internship"
                company = (card.select_one("a.link_display_like_text") or card.select_one("div.company_name")).get_text(strip=True) if card else ""
                loc_el = card.select_one("a.location_link") or card.select_one("span#location_names")
                location_text = loc_el.get_text(strip=True) if loc_el else ""
                stipend = (card.select_one("span.stipend") or card.select_one("div.stipend")).get_text(strip=True) if card else None
                date_posted = (card.select_one("div.status-container") or card.select_one("div.other_detail_item")).get_text(strip=True) if card else None
                link_el = card.select_one("a.view_detail_button") or card.select_one("a.job-title")
                link = "https://internshala.com" + link_el.get("href") if link_el and link_el.get("href") else url

                text_blob = " ".join([title or "", company or "", location_text or ""]).lower()
                if not _match_any(text_blob, skills):
                    continue

                jobs.append({
                    "title": title,
                    "company": company,
                    "location": location_text,
                    "tags": ["internship"],
                    "salary": stipend,
                    "posted_at": date_posted,
                    "url": link,
                    "source": "internshala",
                })
            time.sleep(1)
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
                if not a or not a.get("href"):
                    continue
                full_name = a.get("href").strip("/")
                repo_url = "https://github.com" + a.get("href")
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
            title = (row.select_one("td.position h2") or row.select_one("a.preventLink")).get_text(strip=True) if row else ""
            company = (row.select_one("td.company h3") or row.select_one("span.companyLink")).get_text(strip=True) if row else ""
            tags = [t.get_text(strip=True) for t in row.select("td.tags a")]
            location_text = (row.select_one("div.location") or row.select_one("div.location.tooltip")).get_text(strip=True) if row else "Remote"
            link_el = row.select_one("a.preventLink") or row.select_one("a")
            link_href = link_el.get("href") if link_el else None
            link = ("https://remoteok.com" + link_href) if link_href and link_href.startswith("/") else (link_href or base)
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
    for fn in (scrape_internshala, scrape_github_repos, scrape_remoteok):
        try:
            collected.extend(fn(skills, location) if fn is not scrape_github_repos else fn(skills))
        except Exception:
            continue
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
