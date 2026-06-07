"""
bark.py — Bark.com service marketplace
Bark is where customers POST jobs (e.g. "I need a website") and pros respond.
This is gold for service providers — these are people with budget looking for help.
"""
import asyncio
import random
import json
import re
from typing import List, Dict
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from config import CRAWL_DELAY_MIN, CRAWL_DELAY_MAX, TARGET_LOCATIONS


# Bark.com category slugs (URL paths)
BARK_CATEGORIES = [
    "web-design",
    "web-development",
    "ecommerce-development",
    "wordpress",
    "app-development",
    "logo-design",
    "seo",
    "digital-marketing",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


class BarkCrawler:
    """Scrape Bark.com for businesses requesting web design/dev services."""

    BASE = "https://www.bark.com/en/{location}/{category}/"

    def __init__(self):
        self.browser = BrowserConfig(
            headless=True,
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True,
            extra_args=["--disable-blink-features=AutomationControlled"],
        )

    def build_urls(self) -> List[str]:
        """Build URLs across categories and 3-4 major locations."""
        locs = ["us", "gb", "au", "ca"]  # Bark.com uses country codes
        urls = []
        for cat in BARK_CATEGORIES:
            for loc in locs:
                urls.append(self.BASE.format(location=loc, category=cat))
        return urls

    async def crawl(self) -> List[Dict]:
        out = []
        async with AsyncWebCrawler(config=self.browser) as crawler:
            for url in self.build_urls():
                try:
                    cfg = CrawlerRunConfig(
                        wait_for=None,
                        page_timeout=45000,
                        magic=True,
                    )
                    res = await crawler.arun(url=url, config=cfg)
                    md = res.markdown or ""

                    if "blocked" in md.lower() or "access denied" in md.lower():
                        print(f"[Bark] {url} -> BLOCKED, skipping")
                        continue

                    # Bark's job listings are in cards with a typical structure
                    # Extract: title, location, description snippet, posted time
                    job_pattern = re.compile(
                        r'\[([^\]]{10,200})\]\((https://www\.bark\.com[^\)]+job[^\)]*)\)',
                        re.IGNORECASE
                    )
                    for m in job_pattern.finditer(md):
                        title, link = m.group(1).strip(), m.group(2)
                        # Heuristic: skip nav links, just keep job posts
                        if any(x in title.lower() for x in ["sign in", "log in", "register", "home", "about"]):
                            continue
                        out.append({
                            "company_name": title[:120],
                            "title": title,
                            "source": "bark",
                            "source_url": link,
                            "website": link,
                            "niche": "Service Request",
                            "lead_type": "service_request",
                        })

                    # Also catch plain URLs (Bark often uses non-markdown links)
                    url_pattern = re.compile(
                        r'https://www\.bark\.com/en/[^/]+/[^/]+/[^/]+/(\d+)/?',
                        re.IGNORECASE
                    )
                    for m in url_pattern.finditer(md):
                        link = m.group(0)
                        if not any(d.get("source_url") == link for d in out):
                            out.append({
                                "company_name": f"Bark Request #{m.group(1)}",
                                "source": "bark",
                                "source_url": link,
                                "website": link,
                                "niche": "Service Request",
                                "lead_type": "service_request",
                            })

                    print(f"[Bark] {url[:80]} -> {len(out)} total so far")
                except Exception as e:
                    print(f"[Bark] Error {url[:60]}: {str(e)[:100]}")
                await asyncio.sleep(random.uniform(CRAWL_DELAY_MAX, CRAWL_DELAY_MAX * 2))
        return out
