"""Summary-counts gprocurement spider — Playwright bootstrap, no pagination.

A sibling of the listing spider (``gprocurement_go_th``) that fetches *only* the
``sumProjectMoneyAndCount`` totals, for every (year, stage) combination. The count endpoint
sits behind the same Turnstile-gated ``X-Announcement-Token`` as the listing, so this spider
reuses the listing spider's real-browser bootstrap (subclassing it) to earn a session, then —
instead of walking listing pages — fans out one summary request per partition.

  bootstrap:  real browser earns cf cookies + X-Announcement-Token (inherited machinery)
  per (year, stage):  GET announcement/sumProjectMoneyAndCount?budgetYear=..&projectStatus=..

Each response's JSON is written to the same per-partition ``.counts.json`` file the listing
spider's cache dir holds, so the two stay aligned. A partition whose counts file already exists
is skipped, making re-runs cheap and resumable.

Usage::

    scrapy crawl gprocurement_counts
"""

from datetime import date

import scrapy
import structlog

from scraper.browser_profile import IMPERSONATE

from .spider import (
    STAGES,
    GPRocurementCachePolicy,
    GprocurementGoTh,
    ListingQuery,
    get_stage_id,
    to_budget_year,
)

logger = structlog.get_logger(__name__)

# First Gregorian (CE) year we fetch summary counts for. Counts span this year through the
# current one, across every stage — so the crawl plan (records per year/stage partition) is
# known without paginating anything.
COUNT_YEAR_START = 2011


class GprocurementCountsSpider(GprocurementGoTh):
    """Fetch the sumProjectMoneyAndCount totals for every (year, stage), browser-bootstrapped."""

    name = "gprocurement_counts"

    @property
    def partition_spider_name(self) -> str:
        # Share the listing spider's partition dir/keys so the .counts.json files sit alongside
        # its .project_ids.txt, instead of in a separate gprocurement_counts/ folder.
        return super().name

    # Counts are the only work this spider does; one priority class is enough. Kept above the
    # inherited PAGINATION_PRIORITY in case any listing request ever sneaks in.
    COUNT_PRIORITY = 200

    async def start(self):
        # No listing to lazily trigger the bootstrap (as the parent does) — kick the real
        # browser off directly. Once it earns a session, parse_session fans out the counts.
        self.logger.info(
            "counts spider start",
            years=f"{COUNT_YEAR_START}-{date.today().year}",
            stages=list(STAGES),
            via_proxy=self.proxy.username if self.proxy else None,
        )
        yield self._playwright_request(callback=self.parse_session)

    async def parse_session(self, response):
        # Post-bootstrap callback: harvest the session (shared with the parent), then start the
        # count chain. Counts run one at a time — each parse_count fires the next — mirroring the
        # listing spider's page walk, so a mid-run block re-bootstraps exactly once. We skip any
        # partition we already have a counts file for (cached from a prior run, or fetched before
        # this re-bootstrap), so the chain resumes where it left off.
        tokens, cookies = await self._harvest_session(response)
        pending = [
            q for q in self._count_queries() if not self._counts_path(q).exists()
        ]
        logger.info("summary counts queued", n=len(pending))
        if pending:
            head, *rest = pending
            yield self._count_request(
                head, tokens=tokens, cookies=cookies, pending=rest
            )

    def _count_queries(self):
        # Every (year, stage) combination: CE years COUNT_YEAR_START..current, each crossed
        # with all STAGES. Yielded as bare ListingQuery values (no page), keyed the same way
        # the listing partitions are so the counts file lands beside the listing's cache.
        for year_ce in range(COUNT_YEAR_START, date.today().year + 1):
            for stage in STAGES.values():
                yield ListingQuery(
                    budget_year=to_budget_year(year_ce),
                    project_status=get_stage_id(stage),
                )

    def _count_request(
        self,
        query: "ListingQuery",
        tokens: dict,
        cookies: dict | None = None,
        pending: list | None = None,
    ) -> scrapy.Request:
        # Summary fetch on the same impersonated "cf" session the browser earned. Not
        # HTTP-cached — we persist the JSON to the partition's counts file ourselves and skip
        # the request entirely when that file already exists (see parse_session). `pending` is
        # the rest of the chain, fired one at a time from parse_count.
        return scrapy.Request(
            query.to_count_url(),
            callback=self.parse_count,
            headers=self._api_headers(tokens),
            cookies=cookies,
            priority=self.COUNT_PRIORITY,
            meta={
                "impersonate": IMPERSONATE,
                "impersonate_args": {"default_headers": False},
                # Same egress IP as the Playwright bootstrap — Cloudflare bound the clearance
                # to it, so curl_cffi must exit there too (see GprocurementGoTh._listing_request).
                **({"proxy": self.proxy.url} if self.proxy else {}),
                "referrer_policy": "no-referrer",
                "cookiejar": "cf",
                "api_tokens": tokens,
                "dont_cache": True,
                # Carry the query (output path) and the remaining chain forward.
                "count_query": query,
                "count_pending": pending or [],
            },
            dont_filter=True,
        )

    def parse_count(self, response):
        query = response.meta["count_query"]
        # A dead/blocked session can't be recovered by retrying the same request. Re-bootstrap;
        # parse_session rebuilds the chain from whatever is still uncached (this query included,
        # since it wasn't stored), so nothing is lost. Only one count is ever in flight, so this
        # fires at most once per block.
        if response.status in (
            401,
            403,
            429,
        ) or GPRocurementCachePolicy.is_blocked_pagination(response):
            self.logger.warning(
                "count blocked (%s) on %s — re-bootstrapping session via Playwright",
                response.status,
                response.url,
            )
            yield self._playwright_request(callback=self.parse_session)
            return

        if response.status == 200:
            self._store_counts(query, response.text)
            logger.info(
                "stored summary counts",
                path=str(self._counts_path(query)),
                url=response.url,
                via_proxy=self.proxy.username if self.proxy else None,
            )
        else:
            # A non-block error: log and skip this partition (don't retry — that would loop).
            logger.warning(
                "sumProjectMoneyAndCount failed",
                status=response.status,
                url=response.url,
            )

        # Advance the chain: fire the next pending partition on the same session (the jar is
        # already seeded, so cookies=None). tokens ride in meta across the whole chain.
        pending = response.meta["count_pending"]
        if pending:
            head, *rest = pending
            yield self._count_request(
                head, tokens=response.meta["api_tokens"], pending=rest
            )
        else:
            logger.info("summary counts done")

    def _counts_path(self, query: "ListingQuery"):
        # Summary counts JSON, partitioned alongside the listing spider's project-ids file.
        return (
            self._partition_dir()
            / "counts"
            / f"{self._partition_key(query)}.counts.json"
        )

    def _store_counts(self, query: "ListingQuery", body: str) -> None:
        self._counts_path(query).write_text(body, encoding="utf-8")
