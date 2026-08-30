"""scrapers/wellfound.py — Wellfound (formerly AngelList) startup jobs scraper."""
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from scrapers.normalizer import normalize_job_data


class WellfoundScraper(BaseScraper):
    """Scrapes startup job listings from Wellfound using Playwright for JS rendering."""

    async def scrape_jobs(self, role: str = "software-engineer", limit: int = 30) -> List[Dict[str, Any]]:
        url = f"https://wellfound.com/role/{role}"
        jobs = []
        try:
            html = await self.fetch_page_content(url, wait_selector="[data-test='JobListing']")
            soup = BeautifulSoup(html, "lxml")
            listings = soup.select("[data-test='JobListing']")
            for item in listings[:limit]:
                title_elem = item.select_one("[data-test='jobTitle']") or item.find("h2") or item.find("h3")
                company_elem = item.select_one("[data-test='companyName']") or item.find("span", class_=lambda c: c and "company" in c.lower())
                location_elem = item.select_one("[data-test='location']") or item.find("span", class_=lambda c: c and "location" in c.lower())
                salary_elem = item.select_one("[data-test='salary']") or item.find("span", class_=lambda c: c and "salary" in c.lower())
                link_elem = item.find("a")
                if title_elem:
                    href = link_elem.get("href", "") if link_elem else ""
                    job_url = f"https://wellfound.com{href}" if href.startswith("/") else href
                    jobs.append(normalize_job_data(
                        title=title_elem.text.strip(),
                        company=company_elem.text.strip() if company_elem else "Startup",
                        location=location_elem.text.strip() if location_elem else "Remote",
                        salary=salary_elem.text.strip() if salary_elem else "",
                        description=f"Startup role: {title_elem.text.strip()}",
                        apply_url=job_url,
                        source_platform="Wellfound"
                    ))
        except Exception as e:
            print(f"[WellfoundScraper] Error scraping role={role}: {e}")
        return jobs
