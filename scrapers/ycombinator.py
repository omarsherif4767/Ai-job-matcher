"""scrapers/ycombinator.py — Y Combinator Jobs (work at a startup) scraper."""
import httpx
from typing import List, Dict, Any
from scrapers.base_scraper import BaseScraper
from scrapers.normalizer import normalize_job_data


class YCombinatorScraper(BaseScraper):
    """Scrapes job listings from YC's Work at a Startup board via API."""

    async def scrape_jobs(self, limit: int = 40) -> List[Dict[str, Any]]:
        jobs = []
        try:
            # YC exposes a public JSON API for job listings
            url = "https://www.workatastartup.com/jobs.json"
            async with httpx.AsyncClient(
                headers={"User-Agent": "AntigravityAI/1.0"},
                follow_redirects=True
            ) as client:
                response = await client.get(url, timeout=15)
                if response.status_code == 200:
                    data = response.json()
                    for job in data[:limit]:
                        if not isinstance(job, dict):
                            continue
                        company_info = job.get("company", {})
                        jobs.append(normalize_job_data(
                            title=job.get("title", "Software Engineer"),
                            company=company_info.get("name", "YC Company"),
                            location=job.get("locations", ["Remote"])[0] if job.get("locations") else "Remote",
                            salary=f"${job.get('min_experience', '')} yrs exp" if job.get("min_experience") else "",
                            description=job.get("description", ""),
                            apply_url=f"https://www.workatastartup.com/jobs/{job.get('id', '')}",
                            source_platform="YCombinator",
                            skills=job.get("skills", [])
                        ))
                else:
                    # Fallback: Playwright scrape
                    html = await self.fetch_page_content(
                        "https://www.workatastartup.com/jobs",
                        wait_selector=".job-name"
                    )
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(html, "lxml")
                    for item in soup.select(".job")[:limit]:
                        title = item.select_one(".job-name")
                        company = item.select_one(".company-name")
                        link = item.find("a")
                        if title and link:
                            href = link.get("href", "")
                            job_url = f"https://www.workatastartup.com{href}" if href.startswith("/") else href
                            jobs.append(normalize_job_data(
                                title=title.text.strip(),
                                company=company.text.strip() if company else "YC Startup",
                                location="Remote",
                                description=title.text.strip(),
                                apply_url=job_url,
                                source_platform="YCombinator"
                            ))
        except Exception as e:
            print(f"[YCombinatorScraper] Error: {e}")
        return jobs
