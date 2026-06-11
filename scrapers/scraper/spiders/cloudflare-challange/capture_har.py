"""Capture a HAR for sirup.inaproc.id. Writes under this folder's ``outputs/<engine>/``.

    python -m scraper.spiders.sirup_inaproc_id.capture_har
"""

from pathlib import Path

from scrapy_playwright.page import PageMethod

from scraper.spiders._capture_har.capture_har import run_capture
from .settle_cloudflare_page import wait_for_load_cloudflare_default
URLS = [
    "https://www.scrapingcourse.com/cloudflare-challenge",
]

# Gate capture on the listing's search XHR completing rather than a blind timeout.
PAGE_METHODS_GOTO = [
    PageMethod(
        wait_for_load_cloudflare_default,
    )
]

if __name__ == "__main__":
    run_capture(Path(__file__).resolve().parent, URLS, page_methods_goto=PAGE_METHODS_GOTO)
