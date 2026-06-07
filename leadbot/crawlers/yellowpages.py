import asyncio
import random
import json
from typing import List, Dict
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy
from config import CRAWL_DELAY_MIN, CRAWL_DELAY_MAX


# Multiple selector variants — YP.com changes class names over time
YP_SCHEMA = {
    "name": "YP Listings",
    "baseSelector": ".result, .organic .result, [class*='result'], article, .search-results .v-card, .v-card",
    "fields": [
        {"name": "company_name", "selector": ".business-name span, h2 a, .n, a.business-name, [class*='business-name']", "type": "text"},
        {"name": "phone", "selector": ".phones, .phone, [class*='phone']", "type": "text"},
        {"name": "website", "selector": "a.track-visit-website, a[href*='http']:not([href*='yellowpages'])", "type": "attribute", "attribute": "href"},
        {"name": "address", "selector": ".street-address, .street, [class*='street']", "type": "text"},
        {"name": "locality", "selector": ".locality, [class*='locality']", "type": "text"},
        {"name": "categories", "selector": ".categories a, [class*='categor'] a", "type": "text"},
    ]
}

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


class YellowPagesCrawler:
    BASE = "https://www.yellowpages.com/search"

    def __init__(self):
        self.browser = BrowserConfig(
            headless=True,
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True,
            extra_args=["--disable-blink-features=AutomationControlled"],
        )

    def build_urls(self, niches, locations, pages_per_combo=2) -> List[str]:
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
                        wait_for=None,
                        page_timeout=45000,
                        magic=True,
                    )
                    res = await crawler.arun(url=url, config=cfg)

                    md = res.markdown or ""
                    if "blocked" in md.lower() or "cloudflare" in md.lower() or "access denied" in md.lower():
                        print(f"[YP] {url} -> BLOCKED by anti-bot. Skipping.")
                        continue

                    if res.extracted_content:
                        items = json.loads(res.extracted_content)
                        if not isinstance(items, list):
                            items = [items]
                        for item in items:
                            if not isinstance(item, dict):
                                continue
                            item["source"] = "yellowpages"
                            item["source_url"] = url
                            locality = item.get("locality", "") or ""
                            if "," in locality:
                                item["country"] = locality.split(",")[-1].strip()
                            out.append(item)
                    print(f"[YP] {i+1}/{len(urls)}: extracted {len(out)} total so far")
                except Exception as e:
                    print(f"[YP] Error on {url}: {str(e)[:120]}")
                await asyncio.sleep(random.uniform(CRAWL_DELAY_MAX, CRAWL_DELAY_MAX * 2.5))
        return out
