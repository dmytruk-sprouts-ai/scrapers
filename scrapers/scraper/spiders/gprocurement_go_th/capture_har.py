"""Capture a HAR for sirup.inaproc.id. Writes under this folder's ``outputs/<engine>/``.

    python -m scraper.spiders.sirup_inaproc_id.capture_har
"""
import asyncio

from pathlib import Path
from scraper.spiders._capture_har.capture_har import CaptureHarSpider
from scrapy_playwright.page import PageMethod

from scraper.spiders._capture_har.capture_har import run_capture
import structlog
from .cache_router import cache_route


logger = structlog.get_logger(__name__)

URLS = [
    "https://www.gprocurement.go.th/new_index.html",
]

async def init_page(page, request):
    # cache static assets; Cloudflare + data API pass straight through
    await page.route("**/*", cache_route)


class PatchedCaptureHarSpider(CaptureHarSpider):

    async def start(self):
        yield self._playwright_request(
            url=self.url,
            overwrite_meta={
                "playwright_page_init_callback": init_page,
                "playwright_page_goto_kwargs": {
                    "timeout": 600000,  # Individual 60-second limit for this specific URL
                },
            }
        )



async def navigate(
    page,
):
    logger.warning("navigating", current_url=page.url)
    await asyncio.sleep(0.7)

    await page.goto("https://process5.gprocurement.go.th/egp-agpc01-web/announcement?keywordSearch=", timeout=300000)
    logger.warning("navigating", current_url=page.url)
    
    
    await asyncio.sleep(60)

    


if __name__ == "__main__":
    run_capture(Path(__file__).resolve().parent, URLS, 
            page_methods_goto=[],
            page_methods=[PageMethod(
        navigate
    )], spider=PatchedCaptureHarSpider)

