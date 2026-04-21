"""
Job search manager - orchestrates parallel scraping with threading
"""

import logging
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Callable, Optional
from datetime import datetime

from PySide6.QtCore import QThread, Signal

from core.models import Job, JOB_TITLES
from core.scrapers import (
    scrape_indeed,
    scrape_wuzzuf,
    scrape_remoteok,
    scrape_linkedin,
    scrape_glassdoor,
    scrape_bayt,
    scrape_remotive,
    scrape_arbeitnow,
    scrape_themuse,
    scrape_jobicy,
)

logger = logging.getLogger(__name__)


class SearchWorker(QThread):
    """Background worker thread for job searching"""
    
    # Signals
    jobs_found = Signal(list)          # Emits list of new Job objects
    progress_update = Signal(str)      # Status message
    search_complete = Signal(int)      # Total count when done
    error_occurred = Signal(str)       # Error message
    
    def __init__(self, params: dict):
        super().__init__()
        self.params = params
        self._stop_flag = threading.Event()
    
    def stop(self):
        self._stop_flag.set()
    
    def run(self):
        """Main search execution"""
        try:
            location = self.params.get("location", "")
            work_type = self.params.get("work_type", "")
            experience = self.params.get("experience", "")
            sources = self.params.get("sources", [])
            keywords = self.params.get("keywords", [])
            
            # Select job titles to search
            titles_to_search = keywords if keywords else JOB_TITLES[:8]  # Limit for speed
            
            all_jobs = []
            seen = set()
            
            # Build search tasks
            tasks = []
            
            for title in titles_to_search:
                if self._stop_flag.is_set():
                    break
                
                # Add experience modifier to query
                query = title
                if experience and experience != "All Levels":
                    level_map = {
                        "Entry Level": f"entry level {title}",
                        "Junior": f"junior {title}",
                        "Mid Level": f"mid level {title}",
                    }
                    query = level_map.get(experience, title)
                
                if not sources or "Indeed" in sources:
                    tasks.append(("Indeed", scrape_indeed, query, location, work_type))
                if not sources or "Wuzzuf" in sources:
                    tasks.append(("Wuzzuf", scrape_wuzzuf, query, location))
                if not sources or "LinkedIn" in sources:
                    tasks.append(("LinkedIn", scrape_linkedin, query, location, work_type))
                if not sources or "Glassdoor" in sources:
                    tasks.append(("Glassdoor", scrape_glassdoor, query, location))
                if not sources or "Bayt" in sources:
                    tasks.append(("Bayt", scrape_bayt, query, location))
                if not sources or "RemoteOK" in sources:
                    if work_type in ["", "Remote", "All Types"]:
                        tasks.append(("RemoteOK", scrape_remoteok, query))
                if not sources or "Remotive" in sources:
                    tasks.append(("Remotive", scrape_remotive, query, location))
                if not sources or "Arbeitnow" in sources:
                    tasks.append(("Arbeitnow", scrape_arbeitnow, query, location))
                if not sources or "TheMuse" in sources:
                    tasks.append(("TheMuse", scrape_themuse, query, location))
                if not sources or "Jobicy" in sources:
                    tasks.append(("Jobicy", scrape_jobicy, query, location))
            
            total_tasks = len(tasks)
            completed = 0
            
            # Execute searches in parallel (limited concurrency)
            with ThreadPoolExecutor(max_workers=4) as executor:
                future_map = {}
                
                for task in tasks:
                    if self._stop_flag.is_set():
                        break
                    
                    source_name = task[0]
                    func = task[1]
                    args = task[2:]
                    
                    future = executor.submit(func, *args)
                    future_map[future] = source_name
                
                for future in as_completed(future_map):
                    if self._stop_flag.is_set():
                        executor.shutdown(wait=False)
                        break
                    
                    source_name = future_map[future]
                    completed += 1
                    
                    try:
                        new_jobs = future.result(timeout=30)
                        
                        # Deduplicate
                        unique_new = []
                        for job in new_jobs:
                            key = f"{job.title.lower()}|{job.company.lower()}"
                            if key not in seen:
                                seen.add(key)
                                unique_new.append(job)
                        
                        if unique_new:
                            all_jobs.extend(unique_new)
                            self.jobs_found.emit(unique_new)
                        
                        progress_pct = int((completed / total_tasks) * 100)
                        self.progress_update.emit(
                            f"[{progress_pct}%] {source_name} ✓ — {len(all_jobs)} وظيفة حتى الآن"
                        )
                        
                    except Exception as e:
                        logger.error(f"Task error for {source_name}: {e}")
                        self.progress_update.emit(f"⚠ خطأ في {source_name}")
            
            if not self._stop_flag.is_set():
                self.search_complete.emit(len(all_jobs))
                self.progress_update.emit(
                    f"✅ اكتمل البحث — تم العثور على {len(all_jobs)} وظيفة"
                )
                
        except Exception as e:
            logger.error(f"Search worker error: {e}")
            self.error_occurred.emit(str(e))
