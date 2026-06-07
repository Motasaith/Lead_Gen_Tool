"""
goodfirms.py — GoodFirms.co agency directory
GoodFirms lists 50,000+ dev agencies. Each has: company name, location, hourly rate,
team size, services, portfolio, and contact info. This is direct lead data — not jobs,
just agencies you could partner with OR their clients' details if exposed.
"""
import asyncio
import random
import re
from typing import List, Dict
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from config import CRAWL_DELAY_MIN, CRAWL_DELAY_MAX


GOODFIRMS_CATEGORIES = [
    "https://www.goodfirms.co/directory/category/top-web-development-companies",
    "https://www.goodfirms.co/directory/category/top-software-development-companies",
    "https://www.goodfirms.co/directory/category/top-ecommerce-development-companies",
    "https://www.goodfirms.co/directory/category/top-wordpress-development-companies",
    "https://www.goodfirms.co/directory/category/top-app-development-companies",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]


class GoodFirmsCrawler:
    """Discover and extract agency profiles from GoodFirms directory."""

    def __init__(self):
        self.browser = BrowserConfig(
            headless=True,
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True,
            extra_args=["--disable-blink-features=AutomationControlled"],
        )

    async def _discover_profiles(self, listing_url: str) -> List[str]:
        async with AsyncWebCrawler(config=self.browser) as crawler:
            cfg = CrawlerRunConfig(wait_for=None, page_timeout=30000, magic=True)
            try:
                res = await crawler.arun(url=listing_url, config=cfg)
                md = res.markdown or ""
                if "blocked" in md.lower() or "access denied" in md.lower():
                    return []
                # GoodFirms profile URLs look like: /company/profile-name
                profile_urls = re.findall(
                    r'https://www\.goodfirms\.co/company/([a-z0-9-]+)',
                    md,
                    re.IGNORECASE
                )
                unique = list(set(profile_urls))[:25]
                return [f"https://www.goodfirms.co/company/{slug}" for slug in unique]
            except Exception as e:
                print(f"[GoodFirms] Discovery error: {e}")
                return []

    async def _extract_profile(self, profile_url: str) -> Dict:
        async with AsyncWebCrawler(config=self.browser) as crawler:
            cfg = CrawlerRunConfig(wait_for=None, page_timeout=30000, magic=True)
            try:
                res = await crawler.arun(url=profile_url, config=cfg)
                md = res.markdown or ""
                lead = {
                    "source": "goodfirms",
                    "source_url": profile_url,
                    "website": profile_url,
                    "lead_type": "agency",
                }

                # Try to extract company name (first H1 or first strong heading)
                h1_match = re.search(r'^#\s+(.+?)$', md, re.MULTILINE)
                if h1_match:
                    lead["company_name"] = h1_match.group(1).strip()[:200]

                # Extract email
                email_match = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', md)
                emails = [e for e in email_match if not e.endswith(("example.com", "goodfirms.co"))]
                if emails:
                    lead["email"] = emails[0]

                # Extract website
                website_match = re.search(
                    r'(?:Website|Visit Website|Visit Site)[:\s]*(https?://[^\s\)\]]+)',
                    md,
                    re.IGNORECASE
                )
                if website_match:
                    lead["website"] = website_match.group(1)

                # Extract location (look for "Location:" or country names)
                loc_match = re.search(
                    r'(?:Location|Headquarters|Address)[:\s]*([^\n]{5,150})',
                    md,
                    re.IGNORECASE
                )
                if loc_match:
                    lead["country"] = loc_match.group(1).strip().split(",")[-1].strip()

                # Extract hourly rate
                rate_match = re.search(
                    r'\$\s*([\d-]+)\s*/\s*hr',
                    md
                )
                if rate_match:
                    lead["hourly_rate"] = f"${rate_match.group(1)}/hr"

                # Extract team size
                size_match = re.search(
                    r'(\d+\s*-\s*\d+|\d+\+?)\s*(?:employees|people|developers|team)',
                    md,
                    re.IGNORECASE
                )
                if size_match:
                    lead["company_size"] = size_match.group(0)

                # Save first 500 chars of raw text for LLM re-scoring later
                lead["raw_text"] = md[:500]
                return lead
            except Exception as e:
                print(f"[GoodFirms] Profile error {profile_url}: {e}")
                return {}

    async def crawl(self) -> List[Dict]:
        all_profiles = []
        for listing_url in GOODFIRMS_CATEGORIES[:3]:  # first 3 categories
            profiles = await self._discover_profiles(listing_url)
            print(f"[GoodFirms] {listing_url[:60]} -> {len(profiles)} profiles")
            all_profiles.extend(profiles)
            await asyncio.sleep(random.uniform(CRAWL_DELAY_MAX, CRAWL_DELAY_MAX * 2))

        all_profiles = list(set(all_profiles))[:30]
        leads = []
        for url in all_profiles:
            lead = await self._extract_profile(url)
            if lead.get("company_name") or lead.get("email"):
                leads.append(lead)
            await asyncio.sleep(CRAWL_DELAY_MAX)
        return leads
