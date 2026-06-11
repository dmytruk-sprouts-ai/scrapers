"""Capture a HAR for sirup.inaproc.id. Writes under this folder's ``outputs/<engine>/``.

    python -m scraper.spiders.sirup_inaproc_id.capture_har
"""

from pathlib import Path

from scraper.spiders._capture_har.capture_har import run_capture

URLS = [
    "https://www.crunchbase.com/organization/nvidia",
]

if __name__ == "__main__":
    run_capture(Path(__file__).resolve().parent, URLS)
