"""LinkedIn public jobs search scraper.

LinkedIn frequently blocks automated access. This scraper only uses public
search result markup and returns direct `/jobs/view/...` links when available.
"""
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urljoin

import httpx
from bs4 import BeautifulSoup

from scrapers.normalizer import normalize_job_data


class LinkedInScraper:
    async def search_jobs(
        self,
        query: str,
        country: Optional[str] = None,
        limit: int = 12,
    ) -> List[Dict[str, Any]]:
        keywords = quote_plus(query or "software engineer")
        location = quote_plus(country if country and country.lower() != "all" else "Worldwide")
        url = f"https://www.linkedin.com/jobs/search?keywords={keywords}&location={location}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
        }

        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=20) as client:
            response = await client.get(url)
            response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        jobs: List[Dict[str, Any]] = []

        for card in soup.select("li, div.base-card"):
            title_node = card.select_one("h3, a.base-card__full-link")
            link_node = card.select_one("a.base-card__full-link[href], a[href*='/jobs/view/']")
            if not title_node or not link_node:
                continue

            title = title_node.get_text(" ", strip=True)
            apply_url = urljoin("https://www.linkedin.com", link_node.get("href", "")).split("?")[0]
            if "/jobs/view/" not in apply_url:
                continue

            company_node = card.select_one("h4, a.hidden-nested-link, .base-search-card__subtitle")
            location_node = card.select_one(".job-search-card__location, .base-search-card__metadata")

            jobs.append(
                normalize_job_data(
                    title=title,
                    company=company_node.get_text(" ", strip=True) if company_node else "LinkedIn Company",
                    location=location_node.get_text(" ", strip=True) if location_node else country or "Worldwide",
                    description=card.get_text(" ", strip=True),
                    apply_url=apply_url,
                    source_platform="LinkedIn",
                    skills=[],
                )
            )

            if len(jobs) >= limit:
                break

        return jobs
