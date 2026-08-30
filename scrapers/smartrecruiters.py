"""scrapers/smartrecruiters.py — SmartRecruiters ATS career board scraper."""
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from scrapers.normalizer import normalize_job_data


class SmartRecruitersScraper(BaseScraper):
    """Scrapes job listings from SmartRecruiters-hosted career boards."""

    async def scrape_board(self, company_slug: str, company_name: str) -> List[Dict[str, Any]]:
        url = f"https://jobs.smartrecruiters.com/{company_slug}"
        jobs = []
        try:
            html = await self.fetch_page_content(url, wait_selector=".job-item")
            soup = BeautifulSoup(html, "lxml")
            listings = soup.select(".job-item")
            for item in listings:
                title_elem = item.select_one(".job-title") or item.find("h4") or item.find("h3")
                location_elem = item.select_one(".job-location") or item.select_one("[class*='location']")
                link_elem = item.find("a")
                if title_elem and link_elem:
                    href = link_elem.get("href", "")
                    job_url = f"https://jobs.smartrecruiters.com{href}" if href.startswith("/") else href
                    jobs.append(normalize_job_data(
                        title=title_elem.text.strip(),
                        company=company_name,
                        location=location_elem.text.strip() if location_elem else "Remote",
                        description=f"Position: {title_elem.text.strip()} at {company_name}.",
                        apply_url=job_url,
                        source_platform="SmartRecruiters"
                    ))
        except Exception as e:
            print(f"[SmartRecruitersScraper] Error scraping {company_slug}: {e}")
        return jobs
