"""Bounded sample crawl + stats dump — shared infra, run once per spider at finalize.

This is NOT a test (Lever 4 keeps pytest offline and fast). It is a real, bounded network crawl
used to (a) capture a handful of sample records next to the spider and (b) surface Scrapy's run
stats so the result can be eyeballed for trouble (zero items, 403/429, exceptions).

Usage (from the project root, where scrapy.cfg lives)::

    python -m scraper.sample_runner <spider_slug> [limit]

Writes ``scraper/spiders/<slug>/samples/items.jsonl`` (the captured records) and
``scraper/spiders/<slug>/samples/stats.json`` (the full Scrapy stats), and echoes the stats JSON
to stdout on one line prefixed with ``SAMPLE_STATS_JSON:``.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

DEFAULT_LIMIT = 20
STDOUT_MARKER = "SAMPLE_STATS_JSON:"


def collect(slug: str, limit: int = DEFAULT_LIMIT) -> dict:
    """Crawl ``slug`` until ~``limit`` items, write samples + stats, return the stats dict."""
    out = Path("scraper/spiders") / slug / "samples"
    out.mkdir(parents=True, exist_ok=True)

    settings = get_project_settings()
    # Stop after ~limit items (may overshoot slightly with in-flight requests — that's fine), and
    # cap wall-clock so a blocked/slow site can't hang the whole run.
    settings.set("CLOSESPIDER_ITEMCOUNT", limit)
    settings.set("CLOSESPIDER_TIMEOUT", 120)
    settings.set(
        "FEEDS",
        {str(out / "items.jsonl"): {"format": "jsonlines", "overwrite": True}},
    )

    process = CrawlerProcess(settings)
    crawler = process.create_crawler(slug)  # applies the spider's own custom_settings
    stats: dict = {}
    try:
        process.crawl(crawler)
        process.start()  # blocks until the (bounded) crawl finishes
    finally:
        # Capture whatever the stats collector holds, even on a mid-crawl error.
        stats = dict(crawler.stats.get_stats()) if crawler.stats else {}
        (out / "stats.json").write_text(json.dumps(stats, default=str, indent=2), encoding="utf-8")

    return stats


if __name__ == "__main__":
    spider_slug = sys.argv[1]
    item_limit = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_LIMIT
    collect(spider_slug, item_limit)
