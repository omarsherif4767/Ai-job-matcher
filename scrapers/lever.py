import asyncio
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from scrapers.normalizer import normalize_job_data

class LeverScraper(BaseScraper):
    """Scrapes job listings from Lever ATS career boards."""

    async def scrape_board(self, site_name: str, company_name: str) -> List[Dict[str, Any]]:
        url = f"https://jobs.lever.co/{site_name}"
        jobs = []
        try:
            html = await self.fetch_page_content(url, wait_selector=".posting")
            soup = BeautifulSoup(html, "lxml")
            postings = soup.select(".posting")

            for posting in postings:
                title_elem = posting.select_one("h5")
                location_elem = posting.select_one(".sort-by-location")
                workplace_elem = posting.select_one(".workplaceType")
                link_elem = posting.select_one("a.posting-title")

                if title_elem and link_elem:
                    title = title_elem.text.strip()
                    job_url = link_elem.get("href", "")
                    location = location_elem.text.strip() if location_elem else "Remote"
                    workplace = workplace_elem.text.strip() if workplace_elem else ""

                    job_dict = normalize_job_data(
                        title=title,
                        company=company_name,
                        location=f"{location} {workplace}".strip(),
                        description=f"Position: {title} at {company_name}.",
                        apply_url=job_url,
                        source_platform="Lever"
                    )
                    jobs.append(job_dict)
        except Exception as e:
            print(f"Error scraping Lever board {site_name}: {e}")
        return jobs
