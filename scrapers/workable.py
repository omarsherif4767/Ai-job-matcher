"""scrapers/workable.py — Workable ATS career board scraper."""
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from scrapers.normalizer import normalize_job_data


class WorkableScraper(BaseScraper):
    """Scrapes job listings from Workable-hosted career boards."""

    async def scrape_board(self, company_subdomain: str, company_name: str) -> List[Dict[str, Any]]:
        url = f"https://apply.workable.com/{company_subdomain}/"
        jobs = []
        try:
            html = await self.fetch_page_content(url, wait_selector="[data-ui='job']")
            soup = BeautifulSoup(html, "lxml")
            listings = soup.select("[data-ui='job']")
            for item in listings:
                title_elem = item.find("h3") or item.find("h2")
                location_elem = item.find("span", attrs={"data-ui": "job-location"})
                link_elem = item.find("a")
                if title_elem and link_elem:
                    href = link_elem.get("href", "")
                    job_url = f"https://apply.workable.com{href}" if href.startswith("/") else href
                    jobs.append(normalize_job_data(
                        title=title_elem.text.strip(),
                        company=company_name,
                        location=location_elem.text.strip() if location_elem else "Remote",
                        description=f"Position: {title_elem.text.strip()} at {company_name}.",
                        apply_url=job_url,
                        source_platform="Workable"
                    ))
        except Exception as e:
            print(f"[WorkableScraper] Error scraping {company_subdomain}: {e}")
        return jobs
