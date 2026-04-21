"""
Job data model and constants
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Job:
    """Represents a single job listing"""
    title: str
    company: str
    location: str
    work_type: str
    salary: str
    source: str
    date_posted: str
    apply_url: str
    description: str = ""
    job_id: str = ""
    is_favorite: bool = False
    scraped_at: datetime = field(default_factory=datetime.now)

    def __hash__(self):
        return hash((self.title.lower(), self.company.lower(), self.location.lower()))

    def __eq__(self, other):
        if not isinstance(other, Job):
            return False
        return (self.title.lower() == other.title.lower() and
                self.company.lower() == other.company.lower())


# All job titles to search for
JOB_TITLES = [
    "Data Analyst",
    "Junior Data Analyst",
    "Senior Data Analyst",
    "BI Analyst",
    "Business Intelligence Analyst",
    "Business Analyst",
    "Reporting Analyst",
    "Power BI Developer",
    "Data Visualization Analyst",
    "SQL Analyst",
    "Financial Analyst",
    "Operations Analyst",
    "Excel Analyst",
    "Dashboard Analyst",
    "Analytics Specialist",
    "Data Specialist",
    "MIS Analyst",
    "Data Engineer",
    "Analytics Engineer",
    "Insights Analyst",
]

# Work type options
WORK_TYPES = ["All Types", "Full Time", "Part Time", "Remote", "Hybrid", "Internship", "Contract", "Freelance"]

# Experience levels
EXPERIENCE_LEVELS = ["All Levels", "Entry Level", "Junior", "Mid Level"]

# Source websites
SOURCES = {
    "LinkedIn": "https://www.linkedin.com/jobs",
    "Indeed": "https://www.indeed.com",
    "Wuzzuf": "https://wuzzuf.net",
    "Glassdoor": "https://www.glassdoor.com",
    "Bayt": "https://www.bayt.com",
    "RemoteOK": "https://remoteok.com",
    "Remotive": "https://remotive.com",
    "Arbeitnow": "https://www.arbeitnow.com/jobs",
    "TheMuse": "https://www.themuse.com/jobs",
    "Jobicy": "https://jobicy.com/jobs",
    "Wellfound": "https://wellfound.com",
}
