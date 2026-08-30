"""scrapers/company.py — Generic company career page scraper for known company sites.

Supports: OpenAI, Anthropic, Microsoft, NVIDIA, Google, Meta, Databricks,
          Snowflake, Hugging Face, Scale AI.
"""
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from scrapers.normalizer import normalize_job_data

# Known company career page configs
COMPANY_CONFIGS = {
    "openai": {
        "url": "https://openai.com/careers",
        "job_selector": "[class*='job'], [class*='position'], li a",
        "title_selector": "h3, h4, strong",
    },
    "anthropic": {
        "url": "https://www.anthropic.com/careers",
        "job_selector": "[class*='role'], [class*='job'], li",
        "title_selector": "h3, h4, p",
    },
    "microsoft": {
        "url": "https://jobs.careers.microsoft.com/us/en/search",
        "job_selector": ".ms-List-cell",
        "title_selector": "h2, h3",
    },
    "nvidia": {
        "url": "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite",
        "job_selector": "li[class*='css']",
        "title_selector": "a[data-automation-id='jobTitle']",
    },
    "google": {
        "url": "https://careers.google.com/jobs/results/",
        "job_selector": "li[class*='sMn0jc']",
        "title_selector": "h3",
    },
    "meta": {
        "url": "https://www.metacareers.com/jobs",
        "job_selector": "[data-testid='job-listing-item']",
        "title_selector": "a",
    },
    "databricks": {
        "url": "https://www.databricks.com/company/careers/open-positions",
        "job_selector": ".job-item, [class*='posting'], li",
        "title_selector": "h3, h4",
    },
    "snowflake": {
        "url": "https://careers.snowflake.com/us/en/search-results",
        "job_selector": "li[class*='result']",
        "title_selector": "h3",
    },
    "huggingface": {
        "url": "https://apply.workable.com/huggingface/",
        "job_selector": "[data-ui='job']",
        "title_selector": "h3",
    },
    "scaleai": {
        "url": "https://scale.com/careers",
        "job_selector": "[class*='job'], [class*='role'], li",
        "title_selector": "h3, h4",
    },
}


class CompanyScraper(BaseScraper):
    """Scrapes direct company career pages using Playwright for JavaScript rendering."""

    async def scrape_company(self, company_key: str, company_name: str = "") -> List[Dict[str, Any]]:
        config = COMPANY_CONFIGS.get(company_key.lower())
        if not config:
            raise ValueError(f"Unknown company key: {company_key}. Available: {list(COMPANY_CONFIGS.keys())}")

        url = config["url"]
        company_name = company_name or company_key.title()
        jobs = []

        try:
            html = await self.fetch_page_content(url, wait_selector=config["job_selector"])
            soup = BeautifulSoup(html, "lxml")
            listings = soup.select(config["job_selector"])

            for item in listings[:50]:
                title_elem = item.select_one(config["title_selector"]) or item.find(["h2", "h3", "h4", "strong"])
                link_elem = item.find("a") or (item if item.name == "a" else None)

                if title_elem:
                    title = title_elem.text.strip()
                    href = link_elem.get("href", "") if link_elem else ""
                    if not href.startswith("http"):
                        base = url.split("/")[0] + "//" + url.split("/")[2]
                        href = base + href if href.startswith("/") else url
                    jobs.append(normalize_job_data(
                        title=title,
                        company=company_name,
                        location="Check listing",
                        description=f"Position at {company_name}: {title}",
                        apply_url=href or url,
                        source_platform=f"Direct:{company_name}"
                    ))
        except Exception as e:
            print(f"[CompanyScraper] Error scraping {company_key}: {e}")

        return jobs

    async def scrape_all(self) -> List[Dict[str, Any]]:
        """Scrape all configured company career pages."""
        all_jobs = []
        for key, config in COMPANY_CONFIGS.items():
            jobs = await self.scrape_company(key)
            all_jobs.extend(jobs)
            print(f"[CompanyScraper] {key}: {len(jobs)} jobs found")
        return all_jobs
