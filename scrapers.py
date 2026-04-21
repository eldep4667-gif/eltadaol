"""
Job scrapers for multiple job boards
Uses requests + BeautifulSoup for scraping
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import random
import logging
from typing import List
from urllib.parse import urlencode, quote_plus
from core.models import Job

logger = logging.getLogger(__name__)

# Rotating user agents to avoid blocks
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


def get_headers():
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0",
    }


def safe_get(url, timeout=15, retries=2):
    """Safe HTTP GET with retries"""
    for attempt in range(retries):
        try:
            session = requests.Session()
            response = session.get(url, headers=get_headers(), timeout=timeout)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt+1} failed for {url}: {e}")
            if attempt < retries - 1:
                time.sleep(random.uniform(1, 3))
    return None


def clean_text(text: str) -> str:
    """Clean and normalize text"""
    if not text:
        return "N/A"
    return re.sub(r'\s+', ' ', text.strip())


def query_matches(text: str, query: str) -> bool:
    """Relaxed matcher so APIs return broader relevant results"""
    if not query:
        return True
    text_l = (text or "").lower()
    q_tokens = [t for t in re.split(r"\W+", query.lower()) if len(t) > 2]
    if not q_tokens:
        return True
    # Any meaningful token match is enough (less strict than full phrase)
    return any(token in text_l for token in q_tokens)


# ─────────────────────────────────────────────────────────────────────────────
# INDEED SCRAPER
# ─────────────────────────────────────────────────────────────────────────────

def scrape_indeed(query: str, location: str = "", work_type: str = "", max_pages: int = 3) -> List[Job]:
    """Scrape Indeed job listings"""
    jobs = []
    
    params = {
        "q": query,
        "l": location,
        "sort": "date",
        "fromage": "14",  # Last 14 days
    }
    
    if work_type:
        type_map = {
            "Full Time": "fulltime",
            "Part Time": "parttime",
            "Remote": "remote",
            "Internship": "internship",
            "Contract": "contract",
        }
        if work_type in type_map:
            params["jt"] = type_map[work_type]
    
    base_url = "https://www.indeed.com/jobs"
    
    for page in range(max_pages):
        params["start"] = page * 10
        url = f"{base_url}?{urlencode(params)}"
        
        try:
            resp = safe_get(url)
            if not resp:
                continue
                
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Indeed job cards
            job_cards = soup.find_all("div", class_=re.compile(r"job_seen_beacon|cardOutline"))
            
            if not job_cards:
                # Try alternative selectors
                job_cards = soup.find_all("td", class_="resultContent")
            
            for card in job_cards:
                try:
                    # Title
                    title_el = card.find("h2", class_=re.compile(r"jobTitle")) or card.find("a", {"data-jk": True})
                    title = clean_text(title_el.get_text()) if title_el else "N/A"
                    
                    # Company
                    company_el = card.find("span", class_=re.compile(r"companyName")) or card.find("a", {"data-tn-element": "companyName"})
                    company = clean_text(company_el.get_text()) if company_el else "N/A"
                    
                    # Location
                    loc_el = card.find("div", class_=re.compile(r"companyLocation"))
                    location_text = clean_text(loc_el.get_text()) if loc_el else location or "N/A"
                    
                    # Work type detection
                    wt_el = card.find("div", class_=re.compile(r"jobMetaDataGroup|attribute_snippet"))
                    detected_type = clean_text(wt_el.get_text()) if wt_el else work_type or "Full Time"
                    
                    # Salary
                    salary_el = card.find("div", class_=re.compile(r"salary-snippet|estimated-salary"))
                    salary = clean_text(salary_el.get_text()) if salary_el else "Not specified"
                    
                    # Date
                    date_el = card.find("span", class_=re.compile(r"date"))
                    date_text = clean_text(date_el.get_text()) if date_el else "Recent"
                    
                    # Apply URL
                    link_el = card.find("a", {"id": re.compile(r"job_")}) or card.find("a", href=re.compile(r"/rc/clk"))
                    if link_el:
                        href = link_el.get("href", "")
                        apply_url = f"https://www.indeed.com{href}" if href.startswith("/") else href
                    else:
                        apply_url = url
                    
                    if title != "N/A" and company != "N/A":
                        jobs.append(Job(
                            title=title,
                            company=company,
                            location=location_text,
                            work_type=detected_type,
                            salary=salary,
                            source="Indeed",
                            date_posted=date_text,
                            apply_url=apply_url,
                        ))
                except Exception as e:
                    logger.debug(f"Error parsing Indeed card: {e}")
                    continue
            
            time.sleep(random.uniform(1.5, 3))
            
        except Exception as e:
            logger.error(f"Indeed scraping error: {e}")
            continue
    
    logger.info(f"Indeed: Found {len(jobs)} jobs for '{query}'")
    return jobs


# ─────────────────────────────────────────────────────────────────────────────
# WUZZUF SCRAPER
# ─────────────────────────────────────────────────────────────────────────────

def scrape_wuzzuf(query: str, location: str = "", max_pages: int = 3) -> List[Job]:
    """Scrape Wuzzuf job listings (Egypt-focused)"""
    jobs = []
    
    for page in range(max_pages):
        query_slug = quote_plus(query)
        url = f"https://wuzzuf.net/search/jobs/?q={query_slug}&a=hpb&start={page}"
        
        try:
            resp = safe_get(url)
            if not resp:
                continue
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            job_cards = soup.find_all("div", class_=re.compile(r"css-1gatmva|job-card"))
            
            if not job_cards:
                # Alternative: article tags
                job_cards = soup.find_all("article", class_=re.compile(r"css"))
            
            for card in job_cards:
                try:
                    # Title
                    title_el = card.find("h2") or card.find("a", {"data-id": True})
                    if not title_el:
                        continue
                    title = clean_text(title_el.get_text())
                    
                    # Company
                    company_el = card.find("a", class_=re.compile(r"css.*company")) or card.find("span", class_=re.compile(r"company"))
                    company = clean_text(company_el.get_text()) if company_el else "N/A"
                    
                    # Location
                    loc_el = card.find("span", class_=re.compile(r"location|css.*location"))
                    location_text = clean_text(loc_el.get_text()) if loc_el else location or "Egypt"
                    
                    # Work type
                    type_el = card.find("span", class_=re.compile(r"type|job-type"))
                    work_type_text = clean_text(type_el.get_text()) if type_el else "Full Time"
                    
                    # Date
                    date_el = card.find("time") or card.find("span", class_=re.compile(r"date|time"))
                    date_text = date_el.get("datetime", clean_text(date_el.get_text())) if date_el else "Recent"
                    
                    # Apply URL
                    link_el = title_el.find("a") if title_el.name != "a" else title_el
                    if not link_el:
                        link_el = card.find("a", href=re.compile(r"/jobs/"))
                    href = link_el.get("href", "") if link_el else ""
                    apply_url = f"https://wuzzuf.net{href}" if href.startswith("/") else href or url
                    
                    if title and company != "N/A":
                        jobs.append(Job(
                            title=title,
                            company=company,
                            location=location_text,
                            work_type=work_type_text,
                            salary="Not specified",
                            source="Wuzzuf",
                            date_posted=str(date_text),
                            apply_url=apply_url,
                        ))
                except Exception as e:
                    logger.debug(f"Error parsing Wuzzuf card: {e}")
                    continue
            
            time.sleep(random.uniform(1, 2.5))
        
        except Exception as e:
            logger.error(f"Wuzzuf scraping error: {e}")
            continue
    
    logger.info(f"Wuzzuf: Found {len(jobs)} jobs for '{query}'")
    return jobs


# ─────────────────────────────────────────────────────────────────────────────
# REMOTEOK SCRAPER
# ─────────────────────────────────────────────────────────────────────────────

def scrape_remoteok(query: str) -> List[Job]:
    """Scrape RemoteOK for remote data analyst jobs"""
    jobs = []
    
    slug = query.lower().replace(" ", "-")
    url = f"https://remoteok.com/remote-{slug}-jobs"
    
    try:
        resp = safe_get(url, timeout=20)
        if not resp:
            return jobs
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # RemoteOK uses tr tags for job rows
        rows = soup.find_all("tr", class_=re.compile(r"job"))
        
        for row in rows:
            try:
                if "expand" in row.get("class", []):
                    continue
                
                # Title
                title_el = row.find("h2", itemprop="title") or row.find("a", class_=re.compile(r"position"))
                if not title_el:
                    continue
                title = clean_text(title_el.get_text())
                
                # Company
                company_el = row.find("h3", itemprop="name") or row.find("span", class_=re.compile(r"company"))
                company = clean_text(company_el.get_text()) if company_el else "N/A"
                
                # Salary
                salary_el = row.find("div", class_=re.compile(r"salary"))
                salary = clean_text(salary_el.get_text()) if salary_el else "Not specified"
                
                # Date
                date_el = row.find("time")
                date_text = date_el.get("datetime", "Recent") if date_el else "Recent"
                
                # Tags / location
                tags = [clean_text(t.get_text()) for t in row.find_all("div", class_=re.compile(r"tag"))]
                
                # Apply URL
                job_id = row.get("data-id", "")
                apply_url = f"https://remoteok.com/l/{job_id}" if job_id else url
                
                if title and company != "N/A":
                    jobs.append(Job(
                        title=title,
                        company=company,
                        location="Remote",
                        work_type="Remote",
                        salary=salary,
                        source="RemoteOK",
                        date_posted=str(date_text)[:10],
                        apply_url=apply_url,
                        description=", ".join(tags),
                    ))
            except Exception as e:
                logger.debug(f"Error parsing RemoteOK row: {e}")
                continue
        
        time.sleep(2)
        
    except Exception as e:
        logger.error(f"RemoteOK scraping error: {e}")
    
    logger.info(f"RemoteOK: Found {len(jobs)} jobs for '{query}'")
    return jobs


# ─────────────────────────────────────────────────────────────────────────────
# LINKEDIN (via search page — no auth required for public listings)
# ─────────────────────────────────────────────────────────────────────────────

def scrape_linkedin(query: str, location: str = "", work_type: str = "") -> List[Job]:
    """Scrape LinkedIn public job search"""
    jobs = []
    
    params = {
        "keywords": query,
        "location": location,
        "sortBy": "DD",  # Date posted
        "f_TPR": "r604800",  # Last 7 days
    }
    
    # Work type filters
    type_map = {
        "Full Time": "F",
        "Part Time": "P",
        "Remote": "2",
        "Internship": "I",
        "Contract": "C",
    }
    if work_type in type_map:
        params["f_WT"] = type_map[work_type]
    
    url = f"https://www.linkedin.com/jobs/search/?{urlencode(params)}"
    
    try:
        resp = safe_get(url)
        if not resp:
            return jobs
        
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Public job cards
        cards = soup.find_all("div", class_=re.compile(r"base-card|job-search-card"))
        
        for card in cards:
            try:
                title_el = card.find("h3", class_=re.compile(r"base-search-card__title"))
                if not title_el:
                    continue
                title = clean_text(title_el.get_text())
                
                company_el = card.find("h4", class_=re.compile(r"base-search-card__subtitle"))
                company = clean_text(company_el.get_text()) if company_el else "N/A"
                
                loc_el = card.find("span", class_=re.compile(r"job-search-card__location"))
                location_text = clean_text(loc_el.get_text()) if loc_el else location or "N/A"
                
                date_el = card.find("time")
                date_text = date_el.get("datetime", "Recent") if date_el else "Recent"
                
                link_el = card.find("a", class_=re.compile(r"base-card__full-link"))
                apply_url = link_el.get("href", url) if link_el else url
                
                if title and company != "N/A":
                    jobs.append(Job(
                        title=title,
                        company=company,
                        location=location_text,
                        work_type=work_type or "Full Time",
                        salary="Not specified",
                        source="LinkedIn",
                        date_posted=str(date_text)[:10],
                        apply_url=apply_url,
                    ))
            except Exception as e:
                logger.debug(f"Error parsing LinkedIn card: {e}")
                continue
        
        time.sleep(random.uniform(2, 4))
        
    except Exception as e:
        logger.error(f"LinkedIn scraping error: {e}")
    
    logger.info(f"LinkedIn: Found {len(jobs)} jobs for '{query}'")
    return jobs


# ─────────────────────────────────────────────────────────────────────────────
# GLASSDOOR SCRAPER
# ─────────────────────────────────────────────────────────────────────────────

def scrape_glassdoor(query: str, location: str = "") -> List[Job]:
    """Scrape Glassdoor job listings"""
    jobs = []
    
    params = {
        "sc.keyword": query,
        "locT": "C",
        "locId": "1",
        "jobType": "",
        "fromAge": "14",
        "minSalary": "0",
        "includeNoSalaryJobs": "true",
        "radius": "25",
        "cityId": "-1",
        "minRating": "0.0",
        "industryId": "-1",
        "sgocId": "-1",
        "seniorityType": "all",
        "isNewGrad": "0",
        "filterType": "POSTS_BY_DATE",
    }
    
    url = f"https://www.glassdoor.com/Job/jobs.htm?{urlencode(params)}"
    
    try:
        resp = safe_get(url)
        if not resp:
            return jobs
        
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("li", class_=re.compile(r"react-job-listing|jobListing"))
        
        for card in cards:
            try:
                title_el = card.find("a", class_=re.compile(r"job-title|jobTitle"))
                if not title_el:
                    continue
                title = clean_text(title_el.get_text())
                
                company_el = card.find("div", class_=re.compile(r"employer-name|companyName"))
                company = clean_text(company_el.get_text()) if company_el else "N/A"
                
                loc_el = card.find("span", class_=re.compile(r"location|companyLocation"))
                location_text = clean_text(loc_el.get_text()) if loc_el else location or "N/A"
                
                salary_el = card.find("span", class_=re.compile(r"salary-estimate|salaryEstimate"))
                salary = clean_text(salary_el.get_text()) if salary_el else "Not specified"
                
                href = title_el.get("href", "")
                apply_url = f"https://www.glassdoor.com{href}" if href.startswith("/") else href or url
                
                if title and company != "N/A":
                    jobs.append(Job(
                        title=title,
                        company=company,
                        location=location_text,
                        work_type="Full Time",
                        salary=salary,
                        source="Glassdoor",
                        date_posted="Recent",
                        apply_url=apply_url,
                    ))
            except Exception as e:
                logger.debug(f"Error parsing Glassdoor card: {e}")
                continue
        
        time.sleep(random.uniform(2, 4))
        
    except Exception as e:
        logger.error(f"Glassdoor scraping error: {e}")
    
    logger.info(f"Glassdoor: Found {len(jobs)} jobs for '{query}'")
    return jobs


# ─────────────────────────────────────────────────────────────────────────────
# BAYT SCRAPER
# ─────────────────────────────────────────────────────────────────────────────

def scrape_bayt(query: str, location: str = "") -> List[Job]:
    """Scrape Bayt.com job listings"""
    jobs = []
    
    slug = quote_plus(query)
    url = f"https://www.bayt.com/en/jobs/?q={slug}"
    
    if location:
        url += f"&l={quote_plus(location)}"
    
    try:
        resp = safe_get(url)
        if not resp:
            return jobs
        
        soup = BeautifulSoup(resp.text, "html.parser")
        cards = soup.find_all("li", class_=re.compile(r"has-pointer-d"))
        
        if not cards:
            cards = soup.find_all("div", class_=re.compile(r"media-item"))
        
        for card in cards:
            try:
                title_el = card.find("h2") or card.find("a", class_=re.compile(r"is-black"))
                if not title_el:
                    continue
                title = clean_text(title_el.get_text())
                
                company_el = card.find("b", class_=re.compile(r"t-default")) or card.find("span", class_=re.compile(r"company"))
                company = clean_text(company_el.get_text()) if company_el else "N/A"
                
                loc_el = card.find("span", class_=re.compile(r"t-icon-location"))
                if loc_el and loc_el.parent:
                    location_text = clean_text(loc_el.parent.get_text())
                else:
                    location_text = location or "Middle East"
                
                link = card.find("a", href=re.compile(r"/en/job"))
                href = link.get("href", "") if link else ""
                apply_url = f"https://www.bayt.com{href}" if href.startswith("/") else href or url
                
                if title and company != "N/A":
                    jobs.append(Job(
                        title=title,
                        company=company,
                        location=location_text,
                        work_type="Full Time",
                        salary="Not specified",
                        source="Bayt",
                        date_posted="Recent",
                        apply_url=apply_url,
                    ))
            except Exception as e:
                logger.debug(f"Error parsing Bayt card: {e}")
                continue
        
        time.sleep(random.uniform(1.5, 3))
        
    except Exception as e:
        logger.error(f"Bayt scraping error: {e}")
    
    logger.info(f"Bayt: Found {len(jobs)} jobs for '{query}'")
    return jobs


# ─────────────────────────────────────────────────────────────────────────────
# REMOTIVE API (public remote jobs feed)
# ─────────────────────────────────────────────────────────────────────────────

def scrape_remotive(query: str, location: str = "") -> List[Job]:
    """Fetch jobs from Remotive public API"""
    jobs = []
    url = "https://remotive.com/api/remote-jobs"

    try:
        resp = safe_get(url, timeout=20)
        if not resp:
            return jobs

        data = resp.json()
        listings = data.get("jobs", [])
        q = query.lower()
        loc = location.lower().strip()

        for item in listings:
            try:
                title = clean_text(item.get("title", ""))
                company = clean_text(item.get("company_name", ""))
                candidate_loc = clean_text(item.get("candidate_required_location", "Remote"))
                description = clean_text(item.get("job_type", ""))

                if not query_matches(title, q):
                    continue
                if loc and loc not in candidate_loc.lower():
                    continue

                jobs.append(Job(
                    title=title or "N/A",
                    company=company or "N/A",
                    location=candidate_loc or "Remote",
                    work_type=description or "Remote",
                    salary="Not specified",
                    source="Remotive",
                    date_posted=str(item.get("publication_date", "Recent"))[:10],
                    apply_url=item.get("url", "https://remotive.com"),
                ))
            except Exception as e:
                logger.debug(f"Error parsing Remotive item: {e}")
                continue

    except Exception as e:
        logger.error(f"Remotive scraping error: {e}")

    logger.info(f"Remotive: Found {len(jobs)} jobs for '{query}'")
    return jobs


# ─────────────────────────────────────────────────────────────────────────────
# ARBEITNOW API (global remote jobs)
# ─────────────────────────────────────────────────────────────────────────────

def scrape_arbeitnow(query: str, location: str = "", max_pages: int = 2) -> List[Job]:
    """Fetch jobs from Arbeitnow public jobs API"""
    jobs = []
    q = query.lower().strip()
    loc = location.lower().strip()

    for page in range(1, max_pages + 1):
        url = f"https://www.arbeitnow.com/api/job-board-api?page={page}"
        try:
            resp = safe_get(url, timeout=20)
            if not resp:
                continue

            data = resp.json()
            listings = data.get("data", [])
            if not listings:
                continue

            for item in listings:
                try:
                    title = clean_text(item.get("title", ""))
                    company = clean_text(item.get("company_name", ""))
                    tags = item.get("tags", []) or []
                    remote_flag = item.get("remote", False)
                    location_list = item.get("location", []) or []
                    location_text = ", ".join(location_list) if location_list else ("Remote" if remote_flag else "N/A")

                    title_blob = f"{title} {' '.join(tags)}".lower()
                    if not query_matches(title_blob, q):
                        continue
                    if loc and loc not in location_text.lower():
                        continue

                    jobs.append(Job(
                        title=title or "N/A",
                        company=company or "N/A",
                        location=location_text,
                        work_type="Remote" if remote_flag else "Full Time",
                        salary="Not specified",
                        source="Arbeitnow",
                        date_posted=str(item.get("created_at", "Recent"))[:10],
                        apply_url=item.get("url", "https://www.arbeitnow.com/jobs"),
                        description=", ".join(tags),
                    ))
                except Exception as e:
                    logger.debug(f"Error parsing Arbeitnow item: {e}")
                    continue
        except Exception as e:
            logger.error(f"Arbeitnow scraping error: {e}")
            continue

    logger.info(f"Arbeitnow: Found {len(jobs)} jobs for '{query}'")
    return jobs


# ─────────────────────────────────────────────────────────────────────────────
# THE MUSE API (public jobs API)
# ─────────────────────────────────────────────────────────────────────────────

def scrape_themuse(query: str, location: str = "", max_pages: int = 2) -> List[Job]:
    """Fetch jobs from The Muse public API"""
    jobs = []
    q = query.lower().strip()
    loc = location.lower().strip()

    for page in range(max_pages):
        url = f"https://www.themuse.com/api/public/jobs?page={page}"
        try:
            resp = safe_get(url, timeout=20)
            if not resp:
                continue

            data = resp.json()
            listings = data.get("results", [])
            if not listings:
                continue

            for item in listings:
                try:
                    title = clean_text(item.get("name", ""))
                    company_obj = item.get("company", {}) or {}
                    company = clean_text(company_obj.get("name", "N/A"))

                    locations = item.get("locations", []) or []
                    location_text = ", ".join(
                        clean_text(x.get("name", "")) for x in locations if x.get("name")
                    ) or "N/A"

                    if not query_matches(title, q):
                        continue
                    if loc and loc not in location_text.lower():
                        continue

                    jobs.append(Job(
                        title=title or "N/A",
                        company=company or "N/A",
                        location=location_text,
                        work_type="Full Time",
                        salary="Not specified",
                        source="TheMuse",
                        date_posted=str(item.get("publication_date", "Recent"))[:10],
                        apply_url=item.get("refs", {}).get("landing_page", "https://www.themuse.com/jobs"),
                    ))
                except Exception as e:
                    logger.debug(f"Error parsing TheMuse item: {e}")
                    continue
        except Exception as e:
            logger.error(f"TheMuse scraping error: {e}")
            continue

    logger.info(f"TheMuse: Found {len(jobs)} jobs for '{query}'")
    return jobs


# ─────────────────────────────────────────────────────────────────────────────
# JOOBLE-LIKE FEED ALTERNATIVE: JOBICY API (public)
# ─────────────────────────────────────────────────────────────────────────────

def scrape_jobicy(query: str, location: str = "") -> List[Job]:
    """Fetch jobs from Jobicy public feed API"""
    jobs = []
    q = query.lower().strip()
    loc = location.lower().strip()
    url = "https://jobicy.com/api/v2/remote-jobs"

    try:
        resp = safe_get(url, timeout=20)
        if not resp:
            return jobs

        data = resp.json()
        listings = data.get("jobs", []) if isinstance(data, dict) else []

        for item in listings:
            try:
                title = clean_text(item.get("jobTitle", ""))
                company = clean_text(item.get("companyName", "N/A"))
                location_text = clean_text(item.get("jobGeo", "Remote"))
                tags = item.get("jobTags", []) or []
                title_blob = f"{title} {' '.join(tags)}"

                if not query_matches(title_blob, q):
                    continue
                if loc and loc not in location_text.lower():
                    continue

                jobs.append(Job(
                    title=title or "N/A",
                    company=company or "N/A",
                    location=location_text or "Remote",
                    work_type="Remote",
                    salary="Not specified",
                    source="Jobicy",
                    date_posted=str(item.get("pubDate", "Recent"))[:10],
                    apply_url=item.get("url", "https://jobicy.com/jobs"),
                    description=", ".join(tags),
                ))
            except Exception as e:
                logger.debug(f"Error parsing Jobicy item: {e}")
                continue
    except Exception as e:
        logger.error(f"Jobicy scraping error: {e}")

    logger.info(f"Jobicy: Found {len(jobs)} jobs for '{query}'")
    return jobs
