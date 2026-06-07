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
            cfg = CrawlerRunConfig(css_selector=".user-list-item", page_timeout=20000, wait_for=None)
            try:
                res = await crawler.arun(url=url, config=cfg)
                profiles = []
                if res.links and "internal" in res.links:
                    for link in res.links["internal"]:
                        href = link.get("href", "")
                        if re.match(r"https://github\.com/[A-Za-z0-9-]+$", href):
                            profiles.append(href)
                return list(set(profiles))[:15]
            except Exception as e:
                print(f"[GitHub] Search error: {e}")
                return []

    async def _extract_profile(self, profile_url: str) -> Dict:
        async with AsyncWebCrawler(config=self.browser) as crawler:
            cfg = CrawlerRunConfig(
                css_selector=".p-name, .p-nickname, .p-label, .u-email, .p-note",
                page_timeout=15000,
                wait_for=None,
            )
            try:
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
            except Exception as e:
                print(f"[GitHub] Profile error {profile_url}: {e}")
                return {}

    async def crawl(self) -> List[Dict]:
        all_profiles = []
        for q in QUERIES[:2]:
            profiles = await self._search_profiles(q)
            all_profiles.extend(profiles)
            await asyncio.sleep(5)
        all_profiles = list(set(all_profiles))[:20]

        leads = []
        for url in all_profiles:
            lead = await self._extract_profile(url)
            if lead.get("email") or lead.get("raw_text"):
                leads.append(lead)
            await asyncio.sleep(CRAWL_DELAY_MIN)
        return leads
