"""Item pipeline: store LKPP satudata responses as JSONL.

Registered on the ``isb_lkpp_go_id`` spider (see its ``update_settings``). It writes two
side-by-side files:

    outputs/parsed/raw.jsonl       # every BaseItem, verbatim (always written, source of truth)
    outputs/parsed/tenders.jsonl   # canonical IsbTender records, one tender per line

``raw.jsonl`` is written first, unconditionally, so a crawl is never lost to a parsing bug. Only
``TenderUmumPublik`` items are projected into ``tenders.jsonl`` — the master lists and the
blacklist have no tender schema. Each tender row is validated independently so a single malformed
row is logged and skipped rather than dropping the whole response's worth of tenders.

The output directory is resolved next to this package (independent of the crawl cwd) and can be
overridden with the ``ISB_PARSED_DIR`` setting.
"""

from __future__ import annotations

import json
from pathlib import Path

import structlog
from itemadapter import ItemAdapter
from pydantic import ValidationError

from .models import IsbTender

logger = structlog.get_logger(__name__)

# extra["service"] value emitted by the spider for tender responses.
TENDER_SERVICE = "TenderUmumPublik"


class IsbJsonlPipeline:
    """Persist raw items and the canonical tender projection as JSONL."""

    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self._raw = None
        self._tenders = None
        self._raw_count = 0
        self._tender_count = 0
        self._tender_failures = 0

    @classmethod
    def from_crawler(cls, crawler):
        configured = crawler.settings.get("ISB_PARSED_DIR")
        output_dir = (
            Path(configured)
            if configured
            else Path(__file__).resolve().parent / "outputs" / "parsed"
        )
        return cls(output_dir)

    def open_spider(self, spider):
        self.output_dir.mkdir(parents=True, exist_ok=True)
        # Truncate per run: a re-crawl re-emits the same records, so appending would duplicate.
        self._raw = (self.output_dir / "raw.jsonl").open("w", encoding="utf-8")
        self._tenders = (self.output_dir / "tenders.jsonl").open("w", encoding="utf-8")
        logger.info("isb jsonl pipeline open", output_dir=str(self.output_dir))

    def close_spider(self, spider):
        for fh in (self._raw, self._tenders):
            if fh:
                fh.close()
        logger.info(
            "isb jsonl pipeline closed",
            raw=self._raw_count,
            tenders=self._tender_count,
            tender_failures=self._tender_failures,
            output_dir=str(self.output_dir),
        )

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        # Raw first, unconditionally: the original item is the source of truth and must survive
        # even if the tender projection below is skipped or throws.
        self._raw.write(json.dumps(adapter.asdict(), ensure_ascii=False) + "\n")
        self._raw_count += 1

        extra = adapter.get("extra") or {}
        if extra.get("service") == TENDER_SERVICE:
            self._write_tenders(adapter.get("content"), extra)
        return item

    def _write_tenders(self, content, extra) -> None:
        # One TenderUmumPublik response is a JSON array of packages. Validate each row on its own
        # so a single bad package is logged and skipped, not fatal to the rest of the response.
        try:
            rows = json.loads(content)
        except (TypeError, ValueError) as exc:
            logger.warning(
                "tender content is not valid JSON; skipping projection",
                year=extra.get("year"),
                kd_lpse=extra.get("kd_lpse"),
                error=str(exc),
            )
            return
        for row in rows:
            try:
                tender = IsbTender.model_validate(row)
            except ValidationError as exc:
                self._tender_failures += 1
                logger.warning(
                    "tender row failed validation; skipping",
                    kode_tender=row.get("Kode Tender") if isinstance(row, dict) else None,
                    kd_lpse=extra.get("kd_lpse"),
                    year=extra.get("year"),
                    errors=exc.errors(include_url=False),
                )
                continue
            self._tenders.write(
                tender.model_dump_json(by_alias=False) + "\n"
            )
            self._tender_count += 1
