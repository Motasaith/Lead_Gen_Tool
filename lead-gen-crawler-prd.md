# 🕷️ AI Lead Generation Crawler — File-Based Edition

**Project:** LeadBot — 24/7 Autonomous Lead Extraction (Simplified Stack)
**Owner:** Bina Codes / Abdul Rauf
**Version:** 2.0
**Date:** June 2026
**Stack:** Crawl4AI + Ollama/Groq + APScheduler + JSON/CSV files

---

## What Changed from v1.0

| Removed | Replaced With | Reason |
|---|---|---|
| PostgreSQL | JSON + CSV files in `data/` | Leads visible in Excel, easy backup |
| Redis | `seen.json` + in-memory set | Single bot, no need for Redis speed |
| FastAPI dashboard | `viewer.py` → opens local HTML | No server to host/maintain |
| Docker Compose | `python scheduler.py` | 1 process, 1 machine |
| SQLAlchemy models | Plain Python dicts | Less code, less to break |

**Result:** ~70% less code, ~2-min setup, zero infrastructure to manage.

---

## Table of Contents

1. [Overview](#1-overview)
2. [Quick Start](#2-quick-start)
3. [System Architecture](#3-system-architecture)
4. [Project Structure](#4-project-structure)
5. [File Storage Format](#5-file-storage-format)
6. [Full Code Implementation](#6-full-code-implementation)
7. [Local HTML Viewer](#7-local-html-viewer)
8. [24/7 Scheduler](#8-247-scheduler)
9. [Deployment](#9-deployment)
10. [Costs](#10-costs)

---

## 1. Overview

**What it does:** Crawls business directories, freelancer platforms, and tech sites around the clock using Crawl4AI, extracts lead data (name, email, company, phone, website, niche, country) with an LLM, and writes each batch to a timestamped JSON + CSV file in `data/`.

**What you need:**

- 1x Python install
- 1x Crawl4AI install (free, no key)
- 1x LLM choice: Ollama (free local) OR Groq free tier (cloud, no key)
- That's it.

**Output:**

```
data/
├── leads_2026-06-07_1430.json    # All leads from this run
├── leads_2026-06-07_1430.csv     # Same data, Excel-ready
├── seen.json                     # Deduplication history
└── jobs.log                      # Per-run summary
```

Open the CSV in Excel, sort by `score`, done.

---

## 2. Quick Start

```bash
# 1. Install
pip install -U crawl4ai
crawl4ai-setup

# 2. (Optional) Install local LLM
ollama pull llama3.3

# 3. Configure
cp .env.example .env
# Edit .env if using Groq — leave empty for Ollama

# 4. Run once to test
python main.py

# 5. Start 24/7 scheduler
python scheduler.py

# 6. View leads
python viewer.py --open
```

---

## 3. System Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                       LEADBOT SYSTEM                         │
├────────────┬──────────────┬──────────────┬──────────────────┤
│ SCHEDULER  │   CRAWLER    │  AI EXTRACT  │   FILE STORAGE   │
│            │              │              │                  │
│ APScheduler│ Crawl4AI     │ Ollama local │ data/leads_*.json│
│ (cron-like)│ (Playwright) │ OR           │ data/leads_*.csv │
│            │ + async      │ Groq API     │ data/seen.json   │
│            │              │ (1 key)      │ data/jobs.log    │
└────────────┴──────────────┴──────────────┴──────────────────┘
                         │
                         ▼
                ┌─────────────────┐
                │  Local Viewer   │
                │  (HTML page)    │
                └─────────────────┘
```

---

## 4. Project Structure

```
leadbot/
├── main.py              # Single-run pipeline
├── scheduler.py         # 24/7 cron-like loop
├── viewer.py            # Opens a local HTML lead browser
├── config.py            # Settings from .env
├── crawlers/
│   ├── base.py          # Shared crawler helpers
│   ├── yellowpages.py
│   ├── clutch.py
│   └── github.py
├── extractors/
│   └── llm_extractor.py
├── pipeline/
│   ├── dedup.py         # JSON-file based dedup
│   ├── scorer.py
│   └── writer.py        # JSON + CSV writer
├── data/                # Output (auto-created)
│   ├── leads_*.json
│   ├── leads_*.csv
│   ├── seen.json
│   └── jobs.log
├── templates/
│   └── viewer.html      # Static HTML viewer
├── requirements.txt
└── .env
```

---

## 5. File Storage Format

### Lead JSON schema (one per lead)

```json
{
  "id": "lead_2026-06-07_143022_a3f9",
  "company_name": "Acme Digital Ltd",
  "contact_name": "Sarah Khan",
  "title": "CEO",
  "email": "sarah@acmedigital.co.uk",
  "phone": "+44 20 7946 0958",
  "website": "https://acmedigital.co.uk",
  "linkedin": "https://linkedin.com/in/sarahkhan",
  "country": "United Kingdom",
  "city": "London",
  "industry": "Marketing",
  "niche": "Digital Marketing Agency",
  "company_size": "10-50",
  "source": "clutch",
  "source_url": "https://clutch.co/profile/acme-digital",
  "score": 85,
  "fetched_at": "2026-06-07T14:30:22Z"
}
```

### Run output (per run timestamp)

**`data/leads_2026-06-07_1430.json`** — array of all leads from this run
**`data/leads_2026-06-07_1430.csv`** — same data, flattened for Excel
**`data/seen.json`** — `{ "emails": [...], "domains": [...], "urls": [...] }`
**`data/jobs.log`** — append-only run log

---

## 6. Full Code Implementation

### requirements.txt

```
crawl4ai>=0.8.9
apscheduler>=3.10.0
pydantic>=2.0.0
python-dotenv>=1.0.0
jinja2>=3.1.0
```

### .env

```env
# LLM — leave empty for Ollama (free local)
LLM_PROVIDER=ollama/llama3.3
LLM_API_KEY=

# OR Groq (free 6000 req/day, set both lines):
# LLM_PROVIDER=groq/llama3-70b-8192
# LLM_API_KEY=gsk_your_key_here

# Crawl politeness
CRAWL_DELAY_MIN=3
CRAWL_DELAY_MAX=8

# Niches to search
TARGET_NICHES=web design agency,digital marketing agency,SaaS startup,IT consulting
TARGET_LOCATIONS=United Kingdom,United States,Australia,UAE

# Max leads per source per run
MAX_LEADS_PER_SOURCE=200
```

### config.py

```python
import os
from dotenv import load_dotenv

load_dotenv()

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama/llama3.3")
LLM_API_KEY = os.getenv("LLM_API_KEY") or None

CRAWL_DELAY_MIN = float(os.getenv("CRAWL_DELAY_MIN", 3))
CRAWL_DELAY_MAX = float(os.getenv("CRAWL_DELAY_MAX", 8))

TARGET_NICHES = [n.strip() for n in os.getenv("TARGET_NICHES", "web design agency").split(",")]
TARGET_LOCATIONS = [l.strip() for l in os.getenv("TARGET_LOCATIONS", "United Kingdom").split(",")]

MAX_LEADS_PER_SOURCE = int(os.getenv("MAX_LEADS_PER_SOURCE", 200))

# Project paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
SEEN_FILE = os.path.join(DATA_DIR, "seen.json")
JOBS_LOG = os.path.join(DATA_DIR, "jobs.log")

os.makedirs(DATA_DIR, exist_ok=True)
```

### pipeline/writer.py

```python
import csv
import json
import os
from datetime import datetime
from typing import List, Dict
from config import DATA_DIR


def timestamp_slug() -> str:
    return datetime.utcnow().strftime("%Y-%m-%d_%H%M")


def write_leads(leads: List[Dict], source: str) -> str:
    """
    Write leads to timestamped JSON + CSV.
    Returns the JSON file path.
    """
    slug = timestamp_slug()
    json_path = os.path.join(DATA_DIR, f"leads_{source}_{slug}.json")
    csv_path = os.path.join(DATA_DIR, f"leads_{source}_{slug}.csv")

    # JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(leads, f, indent=2, ensure_ascii=False)

    # CSV (flat for Excel)
    if leads:
        fieldnames = list(leads[0].keys())
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(leads)

    return json_path


def append_job_log(source: str, status: str, leads_found: int, error: str = ""):
    line = f"{datetime.utcnow().isoformat()} | {source} | {status} | leads={leads_found}"
    if error:
        line += f" | error={error[:200]}"
    with open(os.path.join(DATA_DIR, "jobs.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")
```

### pipeline/dedup.py

```python
import json
import os
import hashlib
from typing import Set, Dict
from config import SEEN_FILE


class DedupStore:
    """File-backed deduplication. Loads into memory, saves on every write."""

    def __init__(self):
        self._emails: Set[str] = set()
        self._domains: Set[str] = set()
        self._urls: Set[str] = set()
        self._load()

    def _load(self):
        if not os.path.exists(SEEN_FILE):
            return
        try:
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._emails = set(data.get("emails", []))
            self._domains = set(data.get("domains", []))
            self._urls = set(data.get("urls", []))
        except (json.JSONDecodeError, OSError):
            pass

    def _save(self):
        data = {
            "emails": sorted(self._emails),
            "domains": sorted(self._domains),
            "urls": sorted(self._urls),
        }
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def _hash(value: str) -> str:
        return hashlib.md5(value.lower().encode()).hexdigest()

    def is_duplicate(self, lead: Dict) -> bool:
        email = (lead.get("email") or "").strip().lower()
        if email and self._hash(email) in self._emails:
            return True

        website = (lead.get("website") or "").strip().lower()
        if website:
            domain = website.replace("https://", "").replace("http://", "").split("/")[0]
            if self._hash(domain) in self._domains:
                return True

        return False

    def mark_seen(self, lead: Dict):
        email = (lead.get("email") or "").strip().lower()
        if email:
            self._emails.add(self._hash(email))

        website = (lead.get("website") or "").strip().lower()
        if website:
            domain = website.replace("https://", "").replace("http://", "").split("/")[0]
            self._domains.add(self._hash(domain))

        source_url = (lead.get("source_url") or "").strip()
        if source_url:
            self._urls.add(self._hash(source_url))

    def commit(self):
        self._save()

    @property
    def stats(self) -> Dict:
        return {
            "emails_seen": len(self._emails),
            "domains_seen": len(self._domains),
            "urls_seen": len(self._urls),
        }
```

### pipeline/scorer.py

```python
from typing import Dict


def score_lead(lead: Dict) -> float:
    s = 0.0
    if lead.get("email"):
        s += 30
    if lead.get("website"):
        s += 20
    if lead.get("phone"):
        s += 20
    if lead.get("company_name"):
        s += 10
    if lead.get("contact_name"):
        s += 10
    if lead.get("linkedin"):
        s += 5
    if lead.get("country") and lead.get("city"):
        s += 3
    if lead.get("industry"):
        s += 2
    return min(s, 100.0)


JUNK_EMAIL_MARKERS = ("example.com", "test@", "noreply@", "no-reply@", "yourcompany.com")


def enrich_lead(lead: Dict) -> Dict:
    # Clean email
    email = (lead.get("email") or "").strip().lower()
    if any(j in email for j in JUNK_EMAIL_MARKERS):
        lead["email"] = None
    else:
        lead["email"] = email or None

    # Clean phone (digits, +, -, spaces, parens)
    phone = lead.get("phone") or ""
    if phone:
        lead["phone"] = "".join(c for c in phone if c.isdigit() or c in "+-() ").strip() or None

    # Normalize website
    website = (lead.get("website") or "").strip()
    if website and not website.startswith(("http://", "https://")):
        lead["website"] = "https://" + website

    lead["score"] = score_lead(lead)

    # Generate id
    import uuid
    from datetime import datetime
    lead["id"] = f"lead_{datetime.utcnow().strftime('%Y%m%d')}_{uuid.uuid4().hex[:6]}"
    lead["fetched_at"] = datetime.utcnow().isoformat() + "Z"

    return lead
```

### extractors/llm_extractor.py

```python
import asyncio
import json
from typing import List, Dict
from pydantic import BaseModel
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from crawl4ai import LLMConfig, LLMExtractionStrategy
from config import LLM_PROVIDER, LLM_API_KEY


class LeadData(BaseModel):
    company_name: str = ""
    contact_name: str = ""
    title: str = ""
    email: str = ""
    phone: str = ""
    website: str = ""
    linkedin: str = ""
    country: str = ""
    city: str = ""
    industry: str = ""
    niche: str = ""
    company_size: str = ""


INSTRUCTION = """
Extract all business leads visible on this page. For each business or person, return:
- company_name, contact_name, title, email, phone, website, linkedin, country, city, industry, niche, company_size.
Return multiple leads as a list. Use null for missing fields. Never invent data.
"""


class LLMLeadExtractor:
    def __init__(self):
        self.llm_config = LLMConfig(provider=LLM_PROVIDER, api_token=LLM_API_KEY)
        self.browser_config = BrowserConfig(headless=True, verbose=False)

    async def extract_one(self, url: str) -> List[Dict]:
        run_config = CrawlerRunConfig(
            extraction_strategy=LLMExtractionStrategy(
                llm_config=self.llm_config,
                schema=LeadData.model_json_schema(),
                instruction=INSTRUCTION,
                extraction_type="schema",
            ),
            wait_for="networkidle",
            page_timeout=30000,
        )
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            if not result.extracted_content:
                return []
            try:
                data = json.loads(result.extracted_content)
                return data if isinstance(data, list) else [data]
            except json.JSONDecodeError:
                return []

    async def extract_many(self, urls: List[str]) -> List[Dict]:
        tasks = [self.extract_one(u) for u in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        out = []
        for r in results:
            if isinstance(r, list):
                out.extend(r)
        return out
```

### crawlers/yellowpages.py

```python
import asyncio
import random
import json
from typing import List, Dict
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from config import CRAWL_DELAY_MIN, CRAWL_DELAY_MAX, TARGET_NICHES, TARGET_LOCATIONS


YP_SCHEMA = {
    "name": "YP Listings",
    "baseSelector": ".srp-listing",
    "fields": [
        {"name": "company_name", "selector": ".business-name span", "type": "text"},
        {"name": "phone", "selector": ".phones", "type": "text"},
        {"name": "website", "selector": ".track-visit-website", "type": "attribute", "attribute": "href"},
        {"name": "address", "selector": ".street-address", "type": "text"},
        {"name": "locality", "selector": ".locality", "type": "text"},
        {"name": "categories", "selector": ".categories a", "type": "text"},
    ]
}


class YellowPagesCrawler:
    BASE = "https://www.yellowpages.com/search"

    def __init__(self):
        self.browser = BrowserConfig(headless=True)

    def build_urls(self, niches, locations, pages_per_combo=3) -> List[str]:
        urls = []
        for niche in niches:
            for loc in locations:
                for p in range(1, pages_per_combo + 1):
                    qs = f"search_terms={niche.replace(' ', '+')}&geo_location_terms={loc.replace(' ', '+')}&page={p}"
                    urls.append(f"{self.BASE}?{qs}")
        return urls

    async def crawl(self, urls: List[str]) -> List[Dict]:
        out = []
        async with AsyncWebCrawler(config=self.browser) as crawler:
            for i, url in enumerate(urls):
                try:
                    cfg = CrawlerRunConfig(
                        extraction_strategy=JsonCssExtractionStrategy(YP_SCHEMA),
                        wait_for=".srp-listing",
                        page_timeout=20000,
                    )
                    res = await crawler.arun(url=url, config=cfg)
                    if res.extracted_content:
                        for item in json.loads(res.extracted_content):
                            item["source"] = "yellowpages"
                            item["source_url"] = url
                            item["country"] = item.get("locality", "").split(",")[-1].strip() or None
                            out.append(item)
                except Exception as e:
                    print(f"[YP] Error on {url}: {e}")
                await asyncio.sleep(random.uniform(CRAWL_DELAY_MIN, CRAWL_DELAY_MAX))
        return out
```

### crawlers/clutch.py

```python
import asyncio
import random
import re
from typing import List, Dict
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from extractors.llm_extractor import LLMLeadExtractor
from config import CRAWL_DELAY_MIN, CRAWL_DELAY_MAX


CATEGORIES = [
    "https://clutch.co/agencies/digital-marketing",
    "https://clutch.co/web-developers",
    "https://clutch.co/agencies/seo",
    "https://clutch.co/app-developers",
]


class ClutchCrawler:
    def __init__(self):
        self.browser = BrowserConfig(headless=True)

    async def _discover_profiles(self, listing_url: str) -> List[str]:
        async with AsyncWebCrawler(config=self.browser) as crawler:
            cfg = CrawlerRunConfig(wait_for=".provider-row", page_timeout=20000)
            res = await crawler.arun(url=listing_url, config=cfg)
            urls = []
            if res.links and "internal" in res.links:
                for link in res.links["internal"]:
                    href = link.get("href", "")
                    if "/profile/" in href:
                        if not href.startswith("http"):
                            href = "https://clutch.co" + href
                        urls.append(href)
            return list(set(urls))[:40]

    async def crawl(self) -> List[Dict]:
        extractor = LLMLeadExtractor()
        all_leads = []
        for cat in CATEGORIES[:2]:
            profiles = await self._discover_profiles(cat)
            print(f"[Clutch] {cat} → {len(profiles)} profiles")
            for i in range(0, len(profiles), 5):
                batch = profiles[i:i + 5]
                leads = await extractor.extract_many(batch)
                for lead in leads:
                    lead["source"] = "clutch"
                all_leads.extend(leads)
                await asyncio.sleep(random.uniform(CRAWL_DELAY_MIN, CRAWL_DELAY_MAX))
        return all_leads
```

### crawlers/github.py

```python
import asyncio
import re
from typing import List, Dict
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from config import CRAWL_DELAY_MIN, CRAWL_DELAY_MAX


QUERIES = [
    "location:UK+freelance+developer",
    "location:USA+founder+SaaS",
    "location:UAE+web+developer",
    "location:Australia+agency",
    "bio:freelancer+hireable:true",
]


class GitHubCrawler:
    def __init__(self):
        self.browser = BrowserConfig(headless=True)

    async def _search_profiles(self, query: str) -> List[str]:
        url = f"https://github.com/search?q={query}&type=users"
        async with AsyncWebCrawler(config=self.browser) as crawler:
            cfg = CrawlerRunConfig(css_selector=".user-list-item", page_timeout=20000)
            res = await crawler.arun(url=url, config=cfg)
            profiles = []
            if res.links and "internal" in res.links:
                for link in res.links["internal"]:
                    href = link.get("href", "")
                    if re.match(r"https://github\.com/[A-Za-z0-9-]+$", href):
                        profiles.append(href)
            return list(set(profiles))[:20]

    async def _extract_profile(self, profile_url: str) -> Dict:
        async with AsyncWebCrawler(config=self.browser) as crawler:
            cfg = CrawlerRunConfig(css_selector=".p-name, .p-nickname, .p-label, .u-email, .p-note", page_timeout=15000)
            res = await crawler.arun(url=profile_url, config=cfg)
            text = res.markdown or ""
            emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', text)
            emails = [e for e in emails if not e.endswith(("example.com", "users.noreply.github.com"))]
            return {
                "source": "github",
                "source_url": profile_url,
                "website": profile_url,
                "email": emails[0] if emails else None,
                "raw_text": text[:300],
            }

    async def crawl(self) -> List[Dict]:
        all_profiles = []
        for q in QUERIES[:3]:
            profiles = await self._search_profiles(q)
            all_profiles.extend(profiles)
            await asyncio.sleep(5)
        all_profiles = list(set(all_profiles))[:40]

        leads = []
        for url in all_profiles:
            try:
                lead = await self._extract_profile(url)
                if lead.get("email") or lead.get("raw_text"):
                    leads.append(lead)
            except Exception as e:
                print(f"[GitHub] {url}: {e}")
            await asyncio.sleep(CRAWL_DELAY_MIN)
        return leads
```

### main.py — single run pipeline

```python
import asyncio
import logging
from datetime import datetime
from config import DATA_DIR
from crawlers.yellowpages import YellowPagesCrawler
from crawlers.clutch import ClutchCrawler
from crawlers.github import GitHubCrawler
from extractors.llm_extractor import LLMLeadExtractor
from pipeline.dedup import DedupStore
from pipeline.scorer import enrich_lead
from pipeline.writer import write_leads, append_job_log
from config import MAX_LEADS_PER_SOURCE

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("leadbot")


async def run_source(name: str, coro):
    log.info(f"=== Starting {name} ===")
    dedup = DedupStore()
    try:
        raw = await coro
        cleaned = [enrich_lead(l) for l in raw if l.get("company_name") or l.get("email")]

        unique = []
        for lead in cleaned:
            if dedup.is_duplicate(lead):
                continue
            dedup.mark_seen(lead)
            unique.append(lead)
            if len(unique) >= MAX_LEADS_PER_SOURCE:
                break

        if unique:
            path = write_leads(unique, source=name)
            log.info(f"[{name}] Saved {len(unique)} leads → {path}")
        else:
            log.info(f"[{name}] No new leads")

        append_job_log(name, "ok", len(unique))
        dedup.commit()
    except Exception as e:
        log.exception(f"[{name}] Failed: {e}")
        append_job_log(name, "failed", 0, str(e))


async def run_all():
    log.info("=== LeadBot Run Started ===")
    await run_source("yellowpages", YellowPagesCrawler().crawl(
        YellowPagesCrawler().build_urls(
            __import__("config").TARGET_NICHES[:3],
            __import__("config").TARGET_LOCATIONS[:2],
        )[:30]
    ))
    await asyncio.sleep(60)

    await run_source("clutch", ClutchCrawler().crawl())
    await asyncio.sleep(60)

    await run_source("github", GitHubCrawler().crawl())
    log.info("=== LeadBot Run Complete ===")


if __name__ == "__main__":
    asyncio.run(run_all())
```

---

## 7. Local HTML Viewer

`viewer.py` — opens a generated HTML page listing all leads. No web server.

```python
#!/usr/bin/env python3
"""
viewer.py — Generate a local HTML page listing all leads from data/*.json
Usage: python viewer.py            # writes templates/leads_view.html
       python viewer.py --open     # writes then opens in default browser
"""
import os
import json
import glob
import argparse
import webbrowser
from jinja2 import Template
from datetime import datetime
from config import DATA_DIR


TEMPLATE = """<!doctype html>
<html><head><meta charset="utf-8"><title>LeadBot Leads</title>
<style>
body{font-family:system-ui,sans-serif;max-width:1200px;margin:24px auto;padding:0 16px;background:#0f1115;color:#e6e6e6}
h1{margin-bottom:4px}.sub{color:#888;margin-bottom:24px}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{padding:8px 10px;text-align:left;border-bottom:1px solid #2a2d35;vertical-align:top}
th{background:#1a1d24;position:sticky;top:0}
tr:hover{background:#161922}
a{color:#7cc4ff;text-decoration:none}
.badge{display:inline-block;padding:2px 6px;border-radius:4px;font-size:12px;font-weight:600}
.b-y{background:#1e3a5f;color:#9ecbff}.b-c{background:#3d1e5f;color:#d09ecb}.b-g{background:#1e5f3d;color:#9ecba8}
.score{font-weight:600}.score-hi{color:#7fff9f}.score-md{color:#ffd97f}.score-lo{color:#ff8e8e}
input,select{padding:6px;background:#1a1d24;border:1px solid #2a2d35;color:#e6e6e6;border-radius:4px;margin-right:8px}
</style></head>
<body>
<h1>🕷️ LeadBot Leads</h1>
<div class="sub">Generated {{ generated }} · {{ leads|length }} total leads · sorted by score</div>
<div style="margin-bottom:16px">
<input id="q" placeholder="Filter (company, email, country)..." style="width:300px">
<select id="src"><option value="">All sources</option>{% for s in sources %}<option>{{s}}</option>{% endfor %}</select>
<select id="min"><option value="0">Any score</option><option value="40">≥40</option><option value="60">≥60</option><option value="80">≥80</option></select>
</div>
<table>
<thead><tr><th>Score</th><th>Company</th><th>Contact</th><th>Email</th><th>Phone</th><th>Website</th><th>Country</th><th>Source</th></tr></thead>
<tbody id="rows">
{% for l in leads %}
<tr data-src="{{l.source}}" data-score="{{l.score|int}}" data-text="{{ (l.company_name or '')|lower ~ ' ' ~ (l.email or '')|lower ~ ' ' ~ (l.country or '')|lower }}">
<td><span class="score {% if l.score >= 60 %}score-hi{% elif l.score >= 30 %}score-md{% else %}score-lo{% endif %}">{{ "%.0f"|format(l.score) }}</span></td>
<td><b>{{ l.company_name or '—' }}</b><br><small style="color:#888">{{ l.niche or '' }}</small></td>
<td>{{ l.contact_name or '—' }}<br><small style="color:#888">{{ l.title or '' }}</small></td>
<td>{% if l.email %}<a href="mailto:{{l.email}}">{{l.email}}</a>{% else %}—{% endif %}</td>
<td>{{ l.phone or '—' }}</td>
<td>{% if l.website %}<a href="{{l.website}}" target="_blank">↗</a>{% else %}—{% endif %}</td>
<td>{{ l.country or '—' }}</td>
<td><span class="badge b-{{l.source[0]}}">{{ l.source }}</span></td>
</tr>
{% endfor %}
</tbody></table>
<script>
const q=document.getElementById('q'),src=document.getElementById('src'),mn=document.getElementById('min');
function filter(){
  const t=q.value.toLowerCase(),s=src.value,m=parseInt(mn.value);
  document.querySelectorAll('#rows tr').forEach(r=>{
    r.style.display=(!s||r.dataset.src===s)&&parseInt(r.dataset.score)>=m&&(!t||r.dataset.text.includes(t))?'':'none';
  });
}
[q,src,mn].forEach(e=>e.addEventListener('input',filter));
</script></body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--open", action="store_true")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(DATA_DIR, "leads_*.json")))
    leads = []
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fh:
                data = json.load(fh)
                if isinstance(data, list):
                    leads.extend(data)
        except Exception:
            pass

    leads.sort(key=lambda l: l.get("score", 0), reverse=True)
    sources = sorted({l.get("source", "?") for l in leads})

    out = os.path.join(os.path.dirname(__file__), "templates", "leads_view.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(Template(TEMPLATE).render(
            leads=leads, sources=sources,
            generated=datetime.now().strftime("%Y-%m-%d %H:%M")
        ))

    print(f"Wrote {len(leads)} leads → {out}")
    if args.open:
        webbrowser.open("file://" + os.path.abspath(out))


if __name__ == "__main__":
    main()
```

---

## 8. 24/7 Scheduler

`scheduler.py` — uses APScheduler to trigger `main.run_all` on intervals.

```python
import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from main import run_all

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("scheduler")

scheduler = AsyncIOScheduler(timezone="UTC")


def job():
    log.info("Cron tick — starting run_all()")
    asyncio.create_task(run_all())


def main():
    scheduler.add_job(job, IntervalTrigger(hours=6), id="leadbot_run", replace_existing=True)
    scheduler.start()
    log.info("LeadBot scheduler started — running every 6 hours. Ctrl+C to stop.")
    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()


if __name__ == "__main__":
    main()
```

---

## 9. Deployment

### Option A: Your own laptop (development)

```bash
python scheduler.py
# That's it. Logs to console + data/jobs.log
```

### Option B: VPS (production, $4/month)

```bash
ssh user@your-vps
git clone <your-repo> leadbot && cd leadbot
python3 -m venv venv && source venv/bin/activate
pip install -U crawl4ai && crawl4ai-setup
pip install -r requirements.txt
cp .env.example .env && nano .env

# Install Ollama for free local LLM
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.3 &

# Run as a service (auto-restart on crash/reboot)
sudo tee /etc/systemd/system/leadbot.service > /dev/null <<EOF
[Unit]
Description=LeadBot Crawler
After=network.target

[Service]
User=$USER
WorkingDirectory=/home/$USER/leadbot
ExecStart=/home/$USER/leadbot/venv/bin/python scheduler.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl enable --now leadbot
sudo systemctl status leadbot
```

### Option C: Windows Task Scheduler (no Linux needed)

1. Open Task Scheduler → Create Task
2. Trigger: Daily, repeat every 6 hours
3. Action: `python C:\path\to\main.py`
4. Settings: "Run task as soon as possible after a scheduled start is missed"

### Backup

```bash
# Daily backup of all leads + dedup state
tar -czf leadbot-backup-$(date +%F).tar.gz data/
# Restore
tar -xzf leadbot-backup-2026-06-07.tar.gz
```

---

## 10. Costs

| Item | Cost | Notes |
|---|---|---|
| Crawl4AI | **$0** | Open source, no key |
| Ollama + llama3.3 | **$0** | Runs on your CPU, 8GB RAM enough |
| Groq API (alternative) | **$0** | 6,000 requests/day free |
| APScheduler | **$0** | Python lib |
| File storage | **$0** | Local disk |
| **Total** | **$0** | Zero recurring cost |

### When you'd pay:

- **Proxy service** ($5–50/month) — only if you get blocked. Not needed for moderate volume.
- **VPS** ($4/month) — only if you want 24/7 without your laptop on.
- **Email verifier** (optional) — if you want to verify MX records of captured emails.

---

## Summary: Why This Version Wins

| Aspect | v1.0 (DB stack) | v2.0 (File-based) |
|---|---|---|
| Setup time | 30–60 min | 2–5 min |
| Lines of code | ~700 | ~450 |
| Dependencies | 9 packages | 5 packages |
| To view leads | Open Postico, run SQL | Open CSV in Excel |
| To back up | `pg_dump` command | `cp -r data/` |
| To migrate | Export/import SQL | Copy JSON files |
| Crash recovery | Postgres WAL | Re-run scheduler |
| Hosting | Needs VPS + Docker | Runs on any laptop |
| Skill required | SQL + Docker | Just Python |

**Bottom line:** A lead-gen bot for one person does not need a database. Files are simpler, faster to ship, and you can grep them.

---

*Built for Bina Codes — 2026*
*Stack: Crawl4AI + Ollama/Groq + APScheduler + JSON/CSV files*
