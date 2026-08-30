"""Wuzzuf job search scraper."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus, urljoin

import httpx
from bs4 import BeautifulSoup

from scrapers.normalizer import normalize_job_data


class WuzzufScraper:
    BASE_URL = "https://wuzzuf.net"

    async def _fetch_html(self, client: httpx.AsyncClient, url: str) -> str:
        response = await client.get(url)
        response.raise_for_status()
        return response.text

    def _build_urls(self, query: str, country: Optional[str]) -> List[str]:
        search_query = quote_plus(query or "software engineer")
        urls = [f"{self.BASE_URL}/search/jobs/?q={search_query}"]

        normalized_country = (country or "").strip().lower()
        if normalized_country and normalized_country != "all":
            country_value = quote_plus(country)
            urls.insert(0, f"{self.BASE_URL}/search/jobs/?q={search_query}&filters%5Bcountry%5D%5B0%5D={country_value}")
            urls.append(f"{self.BASE_URL}/search/jobs/?q={search_query}&a=navbl")

        return urls

    def _extract_jobs_from_html(self, html: str, default_country: str = "Egypt") -> List[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        jobs: List[Dict[str, Any]] = []
        seen = set()

        card_selectors = [
            "div.css-1gatmva",
            "div[class*='css-1gatmva']",
            "div[class*='job-card']",
            "article",
            "li",
        ]
        title_selectors = [
            "h2 a[href]",
            "h3 a[href]",
            "a.css-o171kl[href]",
            "a[href*='/jobs/p/']",
            "a[href*='/job/']",
        ]
        company_selectors = [
            "a.css-17s97q8",
            "a[href*='/jobs/careers/']",
            "a[href*='/companies/']",
            "span[class*='company']",
            "h3 + div",
        ]
        location_selectors = [
            "span.css-5wys0k",
            "span[class*='css-5wys0k']",
            "span[class*='location']",
            "div[class*='location']",
        ]
        skills_selectors = [
            "a.css-5x9pm1",
            "a[class*='css-5x9pm1']",
            "a[href*='skills']",
            "span[class*='skill']",
            "div[class*='skill'] span",
        ]

        cards = []
        for selector in card_selectors:
            cards.extend(soup.select(selector))

        if not cards:
            cards = [anchor.parent for anchor in soup.select("a[href*='/jobs/p/'], a[href*='/job/']") if anchor.parent]

        for card in cards:
            title_link = None
            for selector in title_selectors:
                title_link = card.select_one(selector)
                if title_link:
                    break
            if not title_link:
                continue

            href = title_link.get("href", "").strip()
            if not href:
                continue

            title = title_link.get_text(" ", strip=True)
            if not title:
                title = re.sub(r"\s+", " ", title_link.get("aria-label", "")).strip()
            if not title:
                continue

            apply_url = urljoin(self.BASE_URL, href).split("?")[0]
            if apply_url in seen:
                continue
            seen.add(apply_url)

            company = "Wuzzuf Company"
            for selector in company_selectors:
                company_node = card.select_one(selector)
                if company_node:
                    text = company_node.get_text(" ", strip=True).strip("-").strip()
                    if text:
                        company = text
                        break

            location = default_country
            for selector in location_selectors:
                location_node = card.select_one(selector)
                if location_node:
                    text = location_node.get_text(" ", strip=True)
                    if text:
                        location = text
                        break

            skill_candidates = []
            for selector in skills_selectors:
                skill_candidates.extend([tag.get_text(" ", strip=True) for tag in card.select(selector)])
            skills = [skill for skill in dict.fromkeys([s for s in skill_candidates if s])]

            text_blob = card.get_text(" ", strip=True)
            jobs.append(
                normalize_job_data(
                    title=title,
                    company=company,
                    location=location,
                    description=text_blob,
                    apply_url=apply_url,
                    source_platform="Wuzzuf",
                    skills=skills[:8],
                )
            )

        return jobs

    async def search_jobs(
        self,
        query: str,
        country: Optional[str] = None,
        limit: int = 12,
    ) -> List[Dict[str, Any]]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9,ar;q=0.8",
        }

        jobs: List[Dict[str, Any]] = []
        default_country = country if country and country.lower() != "all" else "Egypt"

        async with httpx.AsyncClient(headers=headers, follow_redirects=True, timeout=25) as client:
            for url in self._build_urls(query, country):
                try:
                    html = await self._fetch_html(client, url)
                    parsed_jobs = self._extract_jobs_from_html(html, default_country=default_country)
                    if parsed_jobs:
                        jobs.extend(parsed_jobs)
                except Exception:
                    continue

        unique_jobs: List[Dict[str, Any]] = []
        seen = set()
        for job in jobs:
            key = job.get("apply_url")
            if not key or key in seen:
                continue
            seen.add(key)
            unique_jobs.append(job)
            if len(unique_jobs) >= limit:
                break

        return unique_jobs
