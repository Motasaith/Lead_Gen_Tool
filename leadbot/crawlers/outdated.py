"""
outdated.py — Outdated website detector
Finds businesses with old/ugly/non-mobile websites = perfect leads for redesign services.
Detects: no HTTPS, old jQuery, old WordPress themes, no viewport meta, table layouts.
"""
import asyncio
import random
import re
from typing import List, Dict
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from config import CRAWL_DELAY_MIN, CRAWL_DELAY_MAX


# Discovery sources — places where small businesses list their websites
DISCOVERY_SOURCES = [
    # Bing search (less protected than Google)
    "https://www.bing.com/search?q=%22powered+by+wordpress%22+%22we+are+a+small+business%22",
    "https://www.bing.com/search?q=%22family+owned%22+%22established+1985%22+restaurant+website",
    "https://www.bing.com/search?q=intitle%3A%22welcome+to%22+inurl%3A%22about%22+%22our+services%22",
    "https://duckduckgo.com/?q=%22best+in+town%22+restaurant+old+website&t=h_&ia=web",
    "https://duckduckgo.com/?q=%22call+us+today%22+law+firm+website&t=h_&ia=web",
    "https://duckduckgo.com/?q=%22we+offer%22+real+estate+website&t=h_&ia=web",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]


class OutdatedDetector:
    """
    Find businesses whose websites look outdated, then extract their contact info.
    These are HOT leads for redesign services.
    """

    def __init__(self):
        self.browser = BrowserConfig(
            headless=True,
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True,
            extra_args=["--disable-blink-features=AutomationControlled"],
        )

    async def _discover_urls(self, search_url: str) -> List[str]:
        """Use search engines to find candidate websites."""
        async with AsyncWebCrawler(config=self.browser) as crawler:
            cfg = CrawlerRunConfig(wait_for=None, page_timeout=30000, magic=True)
            try:
                res = await crawler.arun(url=search_url, config=cfg)
                md = res.markdown or ""
                if "blocked" in md.lower() or "captcha" in md.lower():
                    return []
                # Find URLs in search results (skip search engine's own URLs)
                urls = re.findall(
                    r'https?://[a-z0-9.-]+\.(?:com|co\.uk|net|org|io|biz)/[^\s\)\]\"\']*',
                    md,
                    re.IGNORECASE
                )
                # Filter out known big sites and search engine domains
                skip_domains = {
                    "google.com", "bing.com", "duckduckgo.com", "youtube.com",
                    "facebook.com", "twitter.com", "linkedin.com", "wikipedia.org",
                    "reddit.com", "microsoft.com", "apple.com", "amazon.com",
                }
                filtered = []
                for u in urls:
                    domain = re.sub(r'https?://([^/]+)/.*', r'\1', u).lower()
                    if not any(skip in domain for skip in skip_domains):
                        filtered.append(u)
                return list(set(filtered))[:15]
            except Exception as e:
                print(f"[Outdated] Search error: {e}")
                return []

    async def _check_site(self, url: str) -> Dict | None:
        """Visit a site, detect outdated signals, extract contact info."""
        async with AsyncWebCrawler(config=self.browser) as crawler:
            cfg = CrawlerRunConfig(wait_for=None, page_timeout=20000, magic=True)
            try:
                res = await crawler.arun(url=url, config=cfg)
                html = res.html or ""
                md = res.markdown or ""
                if not md or "blocked" in md.lower():
                    return None

                signals = []
                score = 0

                # No HTTPS
                if url.startswith("http://"):
                    signals.append("no_https")
                    score += 20

                # Old jQuery version
                if re.search(r'jquery[-/]?(1\.|2\.|3\.[01])', html, re.IGNORECASE):
                    signals.append("old_jquery")
                    score += 25

                # Old WordPress theme (twentytwelve, twentyeleven, etc.)
                if re.search(r'/wp-content/themes/twenty(?:ten|eleven|twelve|thirteen|fourteen)', html, re.IGNORECASE):
                    signals.append("old_wp_theme")
                    score += 30

                # Missing viewport meta (not mobile responsive)
                if "viewport" not in html.lower() and "responsive" not in html.lower():
                    signals.append("not_responsive")
                    score += 25

                # Table-based layout (look for many <table> tags with no role)
                table_count = len(re.findall(r'<table(?![^>]*role)', html, re.IGNORECASE))
                if table_count > 3:
                    signals.append("table_layout")
                    score += 20

                # No <main> or <nav> semantic HTML
                if "<main" not in html.lower() and "<nav" not in html.lower():
                    signals.append("no_semantic_html")
                    score += 10

                # Old copyright year
                if re.search(r'©\s*201[0-5]|copyright\s*201[0-5]', md, re.IGNORECASE):
                    signals.append("old_copyright")
                    score += 15

                # No schema.org / Open Graph
                if 'itemtype=' not in html and 'property="og:' not in html:
                    signals.append("no_seo_meta")
                    score += 10

                if not signals or score < 30:
                    return None  # Not outdated enough

                # Extract contact info
                emails = re.findall(r'[\w.+-]+@[\w-]+\.[\w.-]+', md)
                emails = [e for e in emails if not e.endswith(("example.com", "wixpress.com", "sentry.io"))]

                phones = re.findall(r'(\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}', md)

                # Extract business name from <title> or first H1
                title_match = re.search(r'<title>([^<]+)</title>', html, re.IGNORECASE)
                company = "Unknown"
                if title_match:
                    company = title_match.group(1).split("|")[0].split("-")[0].strip()[:100]
                if not company or company == "Unknown":
                    h1_match = re.search(r'^#\s+(.+?)$', md, re.MULTILINE)
                    if h1_match:
                        company = h1_match.group(1).strip()[:100]

                return {
                    "company_name": company,
                    "source": "outdated_detector",
                    "source_url": url,
                    "website": url,
                    "email": emails[0] if emails else None,
                    "phone": phones[0] if phones else None,
                    "outdated_signals": signals,
                    "outdated_score": score,
                    "lead_type": "outdated_site",
                    "niche": "Website redesign opportunity",
                }
            except Exception as e:
                return None

    async def crawl(self) -> List[Dict]:
        all_urls = []
        for src in DISCOVERY_SOURCES[:3]:  # limit to 3 search sources
            urls = await self._discover_urls(src)
            print(f"[Outdated] {src[:50]} -> {len(urls)} candidate URLs")
            all_urls.extend(urls)
            await asyncio.sleep(random.uniform(CRAWL_DELAY_MAX, CRAWL_DELAY_MAX * 2))

        all_urls = list(set(all_urls))[:25]
        leads = []
        for url in all_urls:
            lead = await self._check_site(url)
            if lead:
                leads.append(lead)
                print(f"[Outdated] FOUND: {lead['company_name']} (score={lead['outdated_score']})")
            await asyncio.sleep(CRAWL_DELAY_MAX)
        return leads
