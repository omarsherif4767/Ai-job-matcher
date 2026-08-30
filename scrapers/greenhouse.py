import asyncio
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from scrapers.normalizer import normalize_job_data

class GreenhouseScraper(BaseScraper):
    """Scrapes job listings from Greenhouse ATS career boards."""
    
    async def scrape_board(self, board_token: str, company_name: str) -> List[Dict[str, Any]]:
        url = f"https://boards.greenhouse.io/{board_token}"
        jobs = []
        try:
            html = await self.fetch_page_content(url, wait_selector=".opening")
            soup = BeautifulSoup(html, "lxml")
            openings = soup.select(".opening")

            for opening in openings:
                title_elem = opening.find("a")
                location_elem = opening.find("span", class_="location")

                if title_elem:
                    title = title_elem.text.strip()
                    job_path = title_elem.get("href", "")
                    job_url = f"https://boards.greenhouse.io{job_path}" if job_path.startswith("/") else job_path
                    location = location_elem.text.strip() if location_elem else "Remote"

                    job_dict = normalize_job_data(
                        title=title,
                        company=company_name,
                        location=location,
                        description=f"Position: {title} at {company_name}. Location: {location}.",
                        apply_url=job_url,
                        source_platform="Greenhouse"
                    )
                    jobs.append(job_dict)
        except Exception as e:
            print(f"Error scraping Greenhouse board {board_token}: {e}")
        return jobs
