"""Capture a HAR for sirup.inaproc.id. Writes under this folder's ``outputs/<engine>/``.

python -m scraper.spiders.sirup_inaproc_id.capture_har
"""

from pathlib import Path

from scrapy_playwright.page import PageMethod

from scraper.spiders._capture_har.capture_har import run_capture

URLS = [
    "https://spse.inaproc.id/jakarta/lelang",
]

# Gate capture on the listing's search XHR completing rather than a blind timeout.
PAGE_METHODS_GOTO = [
    PageMethod(
        "wait_for_event",
        "response",
        lambda r: "dt/lelang" in r.url,
        timeout=15000,
    ),
]

if __name__ == "__main__":
    run_capture(
        Path(__file__).resolve().parent, URLS, page_methods_goto=PAGE_METHODS_GOTO
    )
