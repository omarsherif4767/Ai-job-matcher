import asyncio
from typing import Dict, Any, List, Optional
from playwright.async_api import async_playwright, Browser, Page

class BaseScraper:
    """
    Base Playwright scraper class providing dynamic browser rendering,
    page navigation, auto-waiting, and structured data extraction.
    """
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.browser: Optional[Browser] = None

    async def get_browser(self) -> Browser:
        if not self.browser:
            p = await async_playwright().start()
            self.browser = await p.chromium.launch(
                headless=self.headless,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
        return self.browser

    async def fetch_page_content(self, url: str, wait_selector: Optional[str] = None) -> str:
        browser = await self.get_browser()
        page: Page = await browser.new_page()
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)
            if wait_selector:
                await page.wait_for_selector(wait_selector, timeout=10000)
            content = await page.content()
            return content
        finally:
            await page.close()

    async def close(self):
        if self.browser:
            await self.browser.close()
            self.browser = None
