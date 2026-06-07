"""
yc.py — Y Combinator's Work at a Startup crawler
YC's workatastartup.com lists jobs at funded YC startups (S19, W20, etc.).
The /companies page has the format:
  [Company (Batch) <bullet> Description](https://workatastartup.com/companies/slug)
  [Job Title](https://workatastartup.com/jobs/NUMBER)
  Fulltime Location Info $Salary
"""
import asyncio
import random
import re
from typing import List, Dict
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, BrowserConfig
from config import CRAWL_DELAY_MIN, CRAWL_DELAY_MAX


# Start with the /companies page (rich data) and individual role pages
YC_URLS = [
    "https://www.workatastartup.com/companies",
    "https://www.workatastartup.com/jobs?role=Software+Engineer",
    "https://www.workatastartup.com/jobs?role=Full+Stack",
    "https://www.workatastartup.com/jobs?role=Front+End",
    "https://www.workatastartup.com/jobs?role=Design",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]

# Bullet chars that appear in YC's HTML
BULLET_CHARS = r"[ΓÇó\u2022\u00b7•·\-]"  # includes the mangled ΓÇó


class YCCrawler:
    """Scrape YC's Work at a Startup for funded startups hiring devs."""

    def __init__(self):
        self.browser = BrowserConfig(
            headless=True,
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1920, "height": 1080},
            java_script_enabled=True,
            extra_args=["--disable-blink-features=AutomationControlled"],
        )

    def _parse_jobs(self, md: str) -> List[Dict]:
        """
        Find all job links and the company line before each.
        The YC markdown format (from /companies page):
          [Company (Batch) • Description](company_url)
          [Job Title](job_url)
          Fulltime Location Info $Salary
        """
        leads = []
        seen_urls = set()

        # Find all company links: [Name (S19) • Desc](https://workatastartup.com/companies/slug)
        # Build a map from job_id -> company info using line-by-line scan
        lines = md.split('\n')

        # First pass: find all company profile links (line index -> company info)
        company_info = {}  # line_idx -> (name, batch, description, slug)
        company_re = re.compile(
            r'\[([A-Z][A-Za-z0-9\s&\.\-]+?)\s*\(([SW]\d{2})\)\s*' + BULLET_CHARS + r'\s*([^\]]*?)\]\((https://www\.workatastartup\.com/companies/([a-z0-9\-]+))\)',
            re.IGNORECASE
        )
        for i, line in enumerate(lines):
            m = company_re.search(line)
            if m:
                company_info[i] = {
                    "name": m.group(1).strip(),
                    "batch": m.group(2).strip(),
                    "description": m.group(3).strip()[:200],
                    "slug": m.group(5).strip(),
                }

        # Second pass: find all job links and look BACKWARDS for nearest company
        job_re = re.compile(
            r'\[([^\]]+)\]\((https://www\.workatastartup\.com/jobs/(\d+))\)',
            re.IGNORECASE
        )
        for i, line in enumerate(lines):
            m = job_re.search(line)
            if not m:
                continue
            title = m.group(1).strip()
            url = m.group(2).strip()
            job_id = m.group(3).strip()

            if url in seen_urls:
                continue
            seen_urls.add(url)

            # Find nearest company line above (within 5 lines)
            nearest_company = None
            for j in range(i - 1, max(-1, i - 6), -1):
                if j in company_info:
                    nearest_company = company_info[j]
                    break

            # Look for meta info on the next line (Fulltime / $Salary / location)
            location = None
            salary = None
            role = None
            for offset in [1, 2, 3]:
                if i + offset >= len(lines):
                    break
                next_line = lines[i + offset].strip()
                if not next_line or next_line.startswith('[') or next_line.startswith('!'):
                    continue
                # Skip if not a meta line
                if not any(t in next_line for t in ['Fulltime', 'Intern', 'Contract', 'Parttime']):
                    continue
                # Extract location
                loc_match = re.search(r'(Remote[^,]*|[A-Z][a-z]+(?:,\s*[A-Z]{2})?(?:\s*/\s*[A-Z][a-z]+)*)', next_line)
                if loc_match:
                    location = loc_match.group(0)[:80]
                # Extract salary
                sal_match = re.search(r'(\$[\dKkMm]+(?:\s*-\s*\$?[\dKkMm]+)?)', next_line)
                if sal_match:
                    salary = sal_match.group(0)
                # Role
                for r in ['Full stack', 'Front end', 'Frontend', 'Backend', 'Mobile', 'Design', 'Data', 'Machine learning']:
                    if r.lower() in next_line.lower():
                        role = r
                        break
                break

            company_name = nearest_company["name"] if nearest_company else "Unknown YC Startup"
            batch = nearest_company["batch"] if nearest_company else None
            description = nearest_company["description"] if nearest_company else None
            slug = nearest_company["slug"] if nearest_company else "unknown"

            leads.append({
                "company_name": company_name[:120],
                "title": title[:150],
                "source": "yc",
                "source_url": url,
                "website": f"https://www.workatastartup.com/companies/{slug}",
                "niche": f"YC {batch} (funded startup)" if batch else "YC startup",
                "lead_type": "hiring_signal",
                "country": location,
                "yc_batch": batch,
                "yc_job_id": job_id,
                "salary_range": salary,
                "role_category": role,
                "raw_text": description,
            })
        return leads

    async def crawl(self) -> List[Dict]:
        all_leads = []
        seen = set()
        async with AsyncWebCrawler(config=self.browser) as crawler:
            for url in YC_URLS:
                try:
                    cfg = CrawlerRunConfig(wait_for=None, page_timeout=45000, magic=True)
                    res = await crawler.arun(url=url, config=cfg)
                    md = res.markdown or ""
                    if "blocked" in md.lower() or "captcha" in md.lower():
                        print(f"[YC] {url[:60]} -> BLOCKED")
                        continue
                    if not md:
                        print(f"[YC] {url[:60]} -> empty")
                        continue
                    new_leads = self._parse_jobs(md)
                    added = 0
                    for lead in new_leads:
                        if lead["source_url"] not in seen:
                            seen.add(lead["source_url"])
                            all_leads.append(lead)
                            added += 1
                    print(f"[YC] {url[:60]} -> {added} new jobs")
                except Exception as e:
                    print(f"[YC] Error {url[:60]}: {str(e)[:100]}")
                await asyncio.sleep(random.uniform(CRAWL_DELAY_MAX, CRAWL_DELAY_MAX * 2))
        return all_leads
