import asyncio
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
                    job_dict = normalize_job_data(
                        title=title_elem.text.strip(),
                        company=company_name,
                        location=location_elem.text.strip() if location_elem else "Remote",
                        description=f"Position: {title_elem.text.strip()} at {company_name}.",
                        apply_url=job_url,
                        source_platform="Workable"
                    )
                    jobs.append(job_dict)
        except Exception as e:
            print(f"Error scraping Workable board {company_subdomain}: {e}")
        return jobs


class AshbyScraper(BaseScraper):
    """Scrapes job listings from Ashby-hosted career boards."""

    async def scrape_board(self, company_slug: str, company_name: str) -> List[Dict[str, Any]]:
        url = f"https://jobs.ashbyhq.com/{company_slug}"
        jobs = []
        try:
            html = await self.fetch_page_content(url, wait_selector=".ashby-job-posting-brief-title")
            soup = BeautifulSoup(html, "lxml")
            titles = soup.select(".ashby-job-posting-brief-title")
            locations = soup.select(".ashby-job-posting-brief-department")
            links = soup.select("a.ashby-job-posting-brief")
            for i, title_elem in enumerate(titles):
                href = links[i].get("href", "") if i < len(links) else ""
                job_url = f"https://jobs.ashbyhq.com{href}" if href.startswith("/") else href
                location = locations[i].text.strip() if i < len(locations) else "Remote"
                job_dict = normalize_job_data(
                    title=title_elem.text.strip(),
                    company=company_name,
                    location=location,
                    description=f"Position: {title_elem.text.strip()} at {company_name}.",
                    apply_url=job_url,
                    source_platform="Ashby"
                )
                jobs.append(job_dict)
        except Exception as e:
            print(f"Error scraping Ashby board {company_slug}: {e}")
        return jobs


class RemoteOKScraper(BaseScraper):
    """Scrapes job listings from RemoteOK using their public JSON API."""

    async def scrape_jobs(self, tags: List[str] = None) -> List[Dict[str, Any]]:
        import httpx
        jobs = []
        try:
            url = "https://remoteok.com/api"
            async with httpx.AsyncClient(headers={"User-Agent": "AntigravityAI/1.0"}) as client:
                response = await client.get(url, timeout=15)
                data = response.json()
                # First element is a notice, skip it
                for job in data[1:31]:
                    if not isinstance(job, dict):
                        continue
                    if tags:
                        job_tags = [t.lower() for t in job.get("tags", [])]
                        if not any(tag.lower() in job_tags for tag in tags):
                            continue
                    job_dict = normalize_job_data(
                        title=job.get("position", "Software Engineer"),
                        company=job.get("company", "Remote Company"),
                        location="Remote",
                        salary=job.get("salary", "Not Specified"),
                        description=job.get("description", job.get("position", "")),
                        apply_url=job.get("url", f"https://remoteok.com/remote-jobs/{job.get('id', '')}"),
                        source_platform="RemoteOK",
                        skills=job.get("tags", [])
                    )
                    jobs.append(job_dict)
        except Exception as e:
            print(f"Error scraping RemoteOK: {e}")
        return jobs
