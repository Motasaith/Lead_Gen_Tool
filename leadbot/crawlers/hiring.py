"""
hiring.py — Job-board scanner using FREE public APIs
Companies posting jobs = they have budget for dev work = potential clients.

Sources (all FREE public APIs, no key needed):
  - Remotive.io
  - Arbeitnow (EU)
  - Jobicy
  - 4dayweek.io
"""
import json
import urllib.request
from typing import List, Dict


REMOTIVE_API = "https://remotive.com/api/remote-jobs"
ARBEITNOW_API = "https://www.arbeitnow.com/api/job-board-api"
JOBICY_API = "https://jobicy.com/api/v2/remote-jobs"
FOUR_DAY_API = "https://4dayweek.io/api/jobs"


def _fetch_json(url: str, timeout: int = 25) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "LeadBot/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="ignore"))


DEV_KEYWORDS = [
    "frontend", "front-end", "front end",
    "backend", "back-end",
    "react", "vue", "angular", "svelte", "next.js", "nextjs",
    "javascript", "typescript", "node.js",
    "wordpress", "wp developer",
    "web developer", "webdev", "web engineer",
    "full stack", "fullstack", "full-stack",
    "ui developer", "ui engineer",
    "html", "css", "web designer",
    "shopify", "magento", "drupal", "php developer",
    "developer", "engineer", "programmer",
]


def is_dev_role(*texts) -> bool:
    combined = " ".join(t or "" for t in texts).lower()
    return any(kw in combined for kw in DEV_KEYWORDS)


class HiringCrawler:
    """Find companies actively hiring for dev skills."""

    def _from_remotive(self) -> List[Dict]:
        leads = []
        seen = set()
        try:
            data = _fetch_json(f"{REMOTIVE_API}?category=software-dev&limit=100")
            for job in data.get("jobs", []):
                url = job.get("url", "")
                if url in seen:
                    continue
                if not is_dev_role(job.get("title"), job.get("category")):
                    continue
                seen.add(url)
                leads.append({
                    "company_name": (job.get("company_name") or "Unknown")[:120],
                    "title": (job.get("title") or "")[:150],
                    "source": "remotive",
                    "source_url": url,
                    "website": url,
                    "niche": f"Hiring: {job.get('category', 'dev')}",
                    "lead_type": "hiring_signal",
                    "country": (job.get("candidate_required_location") or "")[:60] or None,
                    "raw_text": (job.get("description") or "")[:500],
                })
        except Exception as e:
            print(f"[Hiring] Remotive error: {e}")
        return leads

    def _from_arbeitnow(self) -> List[Dict]:
        leads = []
        try:
            data = _fetch_json(ARBEITNOW_API)
            for job in data.get("data", []):
                title = job.get("title", "")
                tags = job.get("tags", [])
                if not is_dev_role(title, " ".join(tags)):
                    continue
                leads.append({
                    "company_name": (job.get("company_name") or "Unknown")[:120],
                    "title": title[:150],
                    "source": "arbeitnow",
                    "source_url": job.get("url", ""),
                    "website": job.get("url", ""),
                    "niche": "EU dev hiring",
                    "lead_type": "hiring_signal",
                    "country": (job.get("location") or "")[:60] or None,
                })
        except Exception as e:
            print(f"[Hiring] Arbeitnow error: {e}")
        return leads

    def _from_jobicy(self) -> List[Dict]:
        leads = []
        try:
            data = _fetch_json(f"{JOBICY_API}?count=50")
            for job in data.get("jobList", []):
                title = job.get("jobTitle", "")
                if not is_dev_role(title):
                    continue
                leads.append({
                    "company_name": (job.get("companyName") or "Unknown")[:120],
                    "title": title[:150],
                    "source": "jobicy",
                    "source_url": job.get("url", ""),
                    "website": job.get("url", ""),
                    "niche": "Remote dev job",
                    "lead_type": "hiring_signal",
                    "country": (job.get("jobGeo") or "")[:60] or None,
                })
        except Exception as e:
            print(f"[Hiring] Jobicy error: {e}")
        return leads

    def _from_4dayweek(self) -> List[Dict]:
        leads = []
        try:
            data = _fetch_json(FOUR_DAY_API)
            jobs = data.get("jobs") or data.get("data") or []
            for job in jobs:
                title = job.get("title", "")
                if not is_dev_role(title):
                    continue
                leads.append({
                    "company_name": (job.get("company") or job.get("companyName") or "Unknown")[:120],
                    "title": title[:150],
                    "source": "4dayweek",
                    "source_url": job.get("url", ""),
                    "website": job.get("url", ""),
                    "niche": "4-day week company",
                    "lead_type": "hiring_signal",
                    "country": (job.get("location") or "")[:60] or None,
                })
        except Exception as e:
            print(f"[Hiring] 4dayweek error: {e}")
        return leads

    def crawl(self) -> List[Dict]:
        all_leads = []
        for name, leads in [
            ("Remotive", self._from_remotive()),
            ("Arbeitnow", self._from_arbeitnow()),
            ("Jobicy", self._from_jobicy()),
            ("4dayweek", self._from_4dayweek()),
        ]:
            print(f"[Hiring] {name:10s} -> {len(leads):3d} matching jobs")
            all_leads.extend(leads)
        return all_leads
