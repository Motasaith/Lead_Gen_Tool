"""
dedup.py — File-backed deduplication
Loads into memory, saves on commit(). Uses multiple keys to identify uniqueness:
  - email (strong)
  - website domain (medium - same company website)
  - company_name (for job leads where website is the job board)
  - source_url (for unique pages)
"""
import json
import os
import hashlib
from typing import Set, Dict
from config import SEEN_FILE


class DedupStore:
    def __init__(self):
        self._emails: Set[str] = set()
        self._domains: Set[str] = set()
        self._companies: Set[str] = set()
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
            self._companies = set(data.get("companies", []))
            self._urls = set(data.get("urls", []))
        except (json.JSONDecodeError, OSError):
            pass

    def _save(self):
        data = {
            "emails": sorted(self._emails),
            "domains": sorted(self._domains),
            "companies": sorted(self._companies),
            "urls": sorted(self._urls),
        }
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @staticmethod
    def _hash(value: str) -> str:
        return hashlib.md5(value.lower().encode()).hexdigest()

    @staticmethod
    def _domain(url: str) -> str:
        """Extract root domain from URL."""
        url = url.replace("https://", "").replace("http://", "").split("/")[0]
        # Remove www.
        if url.startswith("www."):
            url = url[4:]
        return url

    def is_duplicate(self, lead: Dict) -> bool:
        # 1. Email match (strongest)
        email = (lead.get("email") or "").strip().lower()
        if email and self._hash(email) in self._emails:
            return True

        # 2. Company name match (for job leads where everyone has same job board URL)
        company = (lead.get("company_name") or "").strip().lower()
        lead_type = lead.get("lead_type", "")
        if company and lead_type in ("hiring_signal", "service_request", "designer"):
            # For these lead types, company_name is the unique key
            if self._hash(company) in self._companies:
                return True

        # 3. Website domain match (skip job board domains for hiring leads)
        website = (lead.get("website") or "").strip().lower()
        if website and lead_type not in ("hiring_signal",):
            # Don't dedupe hiring leads on website (which is the job board URL)
            domain = self._domain(website)
            if domain and self._hash(domain) in self._domains:
                return True

        # 4. Source URL match
        source_url = (lead.get("source_url") or "").strip()
        if source_url and self._hash(source_url) in self._urls:
            return True

        return False

    def mark_seen(self, lead: Dict):
        email = (lead.get("email") or "").strip().lower()
        if email:
            self._emails.add(self._hash(email))

        company = (lead.get("company_name") or "").strip().lower()
        if company:
            self._companies.add(self._hash(company))

        website = (lead.get("website") or "").strip().lower()
        if website:
            domain = self._domain(website)
            if domain:
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
            "companies_seen": len(self._companies),
            "urls_seen": len(self._urls),
        }
