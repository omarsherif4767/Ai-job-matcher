"""scrapers/ashby.py — Ashby ATS career board scraper."""
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from scrapers.base_scraper import BaseScraper
from scrapers.normalizer import normalize_job_data


class AshbyScraper(BaseScraper):
    """Scrapes job listings from Ashby-hosted career boards."""

    async def scrape_board(self, company_slug: str, company_name: str) -> List[Dict[str, Any]]:
        url = f"https://jobs.ashbyhq.com/{company_slug}"
        jobs = []
        try:
            html = await self.fetch_page_content(url, wait_selector=".ashby-job-posting-brief-title")
            soup = BeautifulSoup(html, "lxml")
            titles = soup.select(".ashby-job-posting-brief-title")
            departments = soup.select(".ashby-job-posting-brief-department")
            links = soup.select("a.ashby-job-posting-brief")
            for i, title_elem in enumerate(titles):
                href = links[i].get("href", "") if i < len(links) else ""
                job_url = f"https://jobs.ashbyhq.com{href}" if href.startswith("/") else href
                dept = departments[i].text.strip() if i < len(departments) else "Engineering"
                jobs.append(normalize_job_data(
                    title=title_elem.text.strip(),
                    company=company_name,
                    location=dept,
                    description=f"Position: {title_elem.text.strip()} at {company_name}.",
                    apply_url=job_url,
                    source_platform="Ashby"
                ))
        except Exception as e:
            print(f"[AshbyScraper] Error scraping {company_slug}: {e}")
        return jobs
