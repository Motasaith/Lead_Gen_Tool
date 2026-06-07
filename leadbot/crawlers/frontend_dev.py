"""
frontend_dev.py — Design community scrapers
Dribbble, Behance, Awwwards host designers + their contact info.
Find designers/agencies to partner with, or to learn from.
"""
import asyncio
import random
import re
from typing import List, Dict
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from config import CRAWL_DELAY_MIN, CRAWL_DELAY_MAX


SOURCES = [
    # Dribbble designer listings
    "https://dribbble.com/designers",
    "https://dribbble.com/designers?q=freelance+web+designer",
    # Awwwards nominees
    "https://www.awwwards.com/websites/",
    "https://www.awwwards.com/awwwards/nominees/",
    # Behance search (free + no auth)
    "https://www.behance.net/search/projects?search=web+design+agency",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]


class FrontendDevCrawler:
    """Scrape design communities for potential leads (partners, agencies, clients)."""

    def __init__(self):
        self.browser = BrowserConfig(
            headless=True,
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True,
            extra_args=["--disable-blink-features=AutomationControlled"],
        )

    async def crawl(self) -> List[Dict]:
        out = []
        async with AsyncWebCrawler(config=self.browser) as crawler:
            for url in SOURCES:
                try:
                    cfg = CrawlerRunConfig(wait_for=None, page_timeout=45000, magic=True)
                    res = await crawler.arun(url=url, config=cfg)
                    md = res.markdown or ""
                    html = res.html or ""

                    if "blocked" in md.lower() or "captcha" in md.lower():
                        print(f"[Design] {url[:60]} -> BLOCKED")
                        continue

                    # Dribbble: profile URLs are /<username>
                    if "dribbble.com" in url:
                        # Look for "by <name>" patterns or profile links
                        profile_links = re.findall(
                            r'https://dribbble\.com/([a-z0-9_-]{2,30})(?![\w])',
                            md + " " + html,
                            re.IGNORECASE
                        )
                        seen = set()
                        for username in profile_links:
                            if username in seen or username in {"designers", "shots", "stories", "search", "tags", "about", "jobs", "pro", "freelance"}:
                                continue
                            seen.add(username)
                            if len(seen) > 20:
                                break
                            out.append({
                                "company_name": username,
                                "contact_name": username,
                                "source": "dribbble",
                                "source_url": f"https://dribbble.com/{username}",
                                "website": f"https://dribbble.com/{username}",
                                "niche": "Web designer",
                                "lead_type": "designer",
                            })

                    # Awwwards: agency/designer names
                    elif "awwwards" in url:
                        # Look for agency credits
                        agency_matches = re.findall(
                            r'(?:Agency|Studio|by)[:\s]*([A-Z][A-Za-z0-9\s&.-]{2,50})',
                            md
                        )
                        for agency in agency_matches[:15]:
                            agency = agency.strip()
                            if agency and len(agency) < 50:
                                out.append({
                                    "company_name": agency,
                                    "source": "awwwards",
                                    "source_url": url,
                                    "website": url,
                                    "niche": "Web design agency",
                                    "lead_type": "agency",
                                })

                    # Behance: project links
                    elif "behance" in url:
                        # Look for owner/agency mentions
                        owner_matches = re.findall(
                            r'(?:by|Owner)[:\s]*([A-Z][A-Za-z0-9\s&.-]{2,50})',
                            md
                        )
                        for owner in owner_matches[:15]:
                            owner = owner.strip()
                            if owner and len(owner) < 50:
                                out.append({
                                    "company_name": owner,
                                    "source": "behance",
                                    "source_url": url,
                                    "website": url,
                                    "niche": "Designer/Studio",
                                    "lead_type": "designer",
                                })

                    print(f"[Design] {url[:60]} -> {len(out)} total")
                except Exception as e:
                    print(f"[Design] Error {url[:60]}: {str(e)[:100]}")
                await asyncio.sleep(random.uniform(CRAWL_DELAY_MAX, CRAWL_DELAY_MAX * 2))
        return out
