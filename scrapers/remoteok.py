"""scrapers/remoteok.py — RemoteOK public JSON API scraper."""
import httpx
from typing import List, Dict, Any, Optional
from scrapers.base_scraper import BaseScraper
from scrapers.normalizer import normalize_job_data


class RemoteOKScraper(BaseScraper):
    """Scrapes job listings from RemoteOK using their public JSON API (no Playwright needed)."""

    async def scrape_jobs(self, tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        jobs = []
        try:
            url = "https://remoteok.com/api"
            async with httpx.AsyncClient(headers={"User-Agent": "AntigravityAI/1.0"}) as client:
                response = await client.get(url, timeout=15)
                data = response.json()
                for job in data[1:51]:  # skip first notice element
                    if not isinstance(job, dict):
                        continue
                    if tags:
                        job_tags = [t.lower() for t in job.get("tags", [])]
                        if not any(tag.lower() in job_tags for tag in tags):
                            continue
                    jobs.append(normalize_job_data(
                        title=job.get("position", "Software Engineer"),
                        company=job.get("company", "Remote Company"),
                        location="Remote",
                        salary=job.get("salary", ""),
                        description=job.get("description", job.get("position", "")),
                        apply_url=job.get("url", f"https://remoteok.com/remote-jobs/{job.get('id', '')}"),
                        source_platform="RemoteOK",
                        skills=job.get("tags", [])
                    ))
        except Exception as e:
            print(f"[RemoteOKScraper] Error: {e}")
        return jobs
