"""Item pipeline: parse Thai e-GP detail records and write them as JSONL.

Registered on the ``gprocurement_details`` spider (see its ``custom_settings``). Each raw
``BaseItem`` is mapped by :func:`parse.parse_record` into the canonical tender schema and an
``extra`` bag, written to two side-by-side files that join on ``tender_id``:

    outputs/parsed/records.jsonl   # canonical schema, one tender per line
    outputs/parsed/extra.jsonl     # every leftover source field, same tender_id

The output directory is resolved next to this package so it doesn't depend on the crawl's cwd, and
can be overridden with the ``GPROCUREMENT_PARSED_DIR`` setting.
"""

from __future__ import annotations

import json
from pathlib import Path

import structlog
from itemadapter import ItemAdapter

from .parse import CANONICAL_FIELDS, parse_record

logger = structlog.get_logger(__name__)


class GprocurementJsonlPipeline:
    """Parse each detail item into canonical + extra JSONL records."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self._records = None
        self._extra = None
        self._written = 0

    @classmethod
    def from_crawler(cls, crawler):
        configured = crawler.settings.get("GPROCUREMENT_PARSED_DIR")
        output_dir = (
            Path(configured)
            if configured
            else Path(__file__).resolve().parent / "outputs" / "parsed"
        )
        return cls(output_dir)

    def open_spider(self, spider):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Truncate per run: a re-crawl re-emits the same tenders, so appending would duplicate.
        self._records = (self.output_dir / "records.jsonl").open("w", encoding="utf-8")
        self._extra = (self.output_dir / "extra.jsonl").open("w", encoding="utf-8")
        logger.info("jsonl pipeline open", output_dir=str(self.output_dir))

    def close_spider(self, spider):
        for fh in (self._records, self._extra):
            if fh:
                fh.close()
        logger.info(
            "jsonl pipeline closed", written=self._written, output_dir=str(self.output_dir)
        )

    def process_item(self, item, spider):
        canonical, extra = parse_record(ItemAdapter(item))
        if not canonical.get("tender_id"):
            logger.warning("skipping record with no tender_id")
            return item
        # Stable column order for the canonical file; extra stays as-is.
        ordered = {field: canonical.get(field) for field in CANONICAL_FIELDS}
        self._records.write(json.dumps(ordered, ensure_ascii=False) + "\n")
        self._extra.write(json.dumps(extra, ensure_ascii=False) + "\n")
        self._written += 1
        return item
