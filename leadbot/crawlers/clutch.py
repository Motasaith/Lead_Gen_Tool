import asyncio
import random
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
            cfg = CrawlerRunConfig(wait_for=None, page_timeout=20000)
            try:
                res = await crawler.arun(url=listing_url, config=cfg)
                urls = []
                if res.links and "internal" in res.links:
                    for link in res.links["internal"]:
                        href = link.get("href", "")
                        if "/profile/" in href:
                            if not href.startswith("http"):
                                href = "https://clutch.co" + href
                            urls.append(href)
                return list(set(urls))[:30]
            except Exception as e:
                print(f"[Clutch] Discovery error: {e}")
                return []

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
