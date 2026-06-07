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
Return multiple leads as a list. Use empty string for missing fields. Never invent data.
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
            wait_for=None,
            page_timeout=60000,
        )
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            result = await crawler.arun(url=url, config=run_config)
            if not result.extracted_content:
                return []
            try:
                data = json.loads(result.extracted_content)
                if isinstance(data, list):
                    return data
                if isinstance(data, dict):
                    return [data]
            except json.JSONDecodeError:
                return []
        return []

    async def extract_many(self, urls: List[str]) -> List[Dict]:
        tasks = [self.extract_one(u) for u in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        out = []
        for r in results:
            if isinstance(r, list):
                out.extend(r)
        return out
