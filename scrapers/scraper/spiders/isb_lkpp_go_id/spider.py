"""LKPP "satudata" open-data spider — pure curl_cffi, no browser.

inaproc.id / isb.lkpp.go.id publishes four public procurement datasets as plain JSON/CSV
endpoints (documented in this package's README.md). Unlike the sibling ``sirup_inaproc_id``
spider, there is no Cloudflare / DataTables / Turnstile gate here, so no Playwright is needed:
every endpoint is reachable with an impersonated curl_cffi request alone.

  MasterKLPD            JSON, no params   — list of institutions (KLPD codes)
  MasterLPSE            JSON, no params   — list of procurement units (LPSE codes)
  SanksiDaftarHitam/{tahun}/{kd_klpd}     — public blacklist, per year + KLPD code
  TenderUmumPublik/{tahun}/{kd_lpse}      — public tenders, per year + LPSE code

The two master lists drive the per-code blacklist and tender requests: MasterKLPD supplies the
``kd_klpd`` codes for the blacklist, MasterLPSE supplies the ``kd_lpse`` codes for the tenders.
The cross-product (years × every code) is large, so both code dimensions are parameterizable
and the year span defaults to "current year down to a floor".

Usage::

    # Smoke test — one code, one year, each service:
    scrapy crawl isb_lkpp_go_id -a years=2024 -a kd_klpd=K1 -a kd_lpse=119 -O isb.jsonl

    # Master lists only:
    scrapy crawl isb_lkpp_go_id -a services=klpd,lpse -O master.jsonl

    # Default crawl: tenders only (years 2026..2021 × every LPSE code):
    scrapy crawl isb_lkpp_go_id -O isb.jsonl

    # Opt into the other datasets explicitly:
    scrapy crawl isb_lkpp_go_id -a services=klpd,lpse,blacklist,tender -O isb.jsonl

Args (all optional):
    years      "2024" | "2022,2023,2024" | "2021-2026"  (default: CURRENT_YEAR..min_year, desc)
    min_year   floor for the default descending year range (default 2021)
    kd_klpd    comma list to restrict blacklist codes (default: every code from MasterKLPD)
    kd_lpse    comma list to restrict tender codes   (default: every code from MasterLPSE)
    services   comma subset of {klpd,lpse,blacklist,tender} (default: lpse,tender)

Output is raw: each response becomes one BaseItem with the verbatim body in ``content`` and the
request context (service / year / code) in ``extra``. Parsing happens downstream. Persist with
``-o``/``-O``; the shared ValidationPipeline drops any empty-content responses.
"""

from datetime import UTC, datetime

import scrapy
import structlog

from scraper.browser_profile import IMPERSONATE, navigation_headers
from scraper.items import BaseItem
from scraper.proxies import pick_proxy

logger = structlog.get_logger(__name__)

BASE = "https://isb.lkpp.go.id/isb-2/api/satudata"
MASTER_KLPD = f"{BASE}/MasterKLPD"
MASTER_LPSE = f"{BASE}/MasterLPSE"
SANKSI = BASE + "/SanksiDaftarHitam/{tahun}/{kd_klpd}"
TENDER = BASE + "/TenderUmumPublik/{tahun}/{kd_lpse}"

CURRENT_YEAR = 2026
DEFAULT_MIN_YEAR = 2021

ALL_SERVICES = ("klpd", "lpse", "blacklist", "tender")
# Default to just the tender pipeline: MasterLPSE supplies the kd_lpse codes that drive
# TenderUmumPublik. klpd/blacklist are opt-in (pass services= to include them).
DEFAULT_SERVICES = ("lpse", "tender")


def _parse_years(years: str | None, min_year: int) -> list[int]:
    """Turn the ``years`` arg into a concrete list of years.

    Accepts ``"2024"``, a comma list ``"2022,2023,2024"``, or a range ``"2021-2026"``. With no
    arg, defaults to the current year down to ``min_year`` (descending — newest first).
    """
    if not years:
        return list(range(CURRENT_YEAR, min_year - 1, -1))
    if "-" in years and "," not in years:
        lo, hi = (int(p) for p in years.split("-", 1))
        return list(range(hi, lo - 1, -1))
    return [int(p) for p in years.split(",") if p.strip()]


def _parse_codes(codes: str | None) -> list[str] | None:
    """Comma list of codes, or None to mean 'use every code from the master list'."""
    if not codes:
        return None
    return [c.strip() for c in codes.split(",") if c.strip()]


class IsbLkppGoIdSpider(scrapy.Spider):
    """Fetch the four LKPP satudata datasets via curl_cffi, with sticky-session proxy support."""

    name = "isb_lkpp_go_id"

    # Master lists gate the per-code fan-out, so fetch them ahead of the bulk requests.
    MASTER_PRIORITY = 100

    @classmethod
    def update_settings(cls, settings):
        super().update_settings(settings)  # type: ignore
        settings.setdict(
            {
                "DOWNLOAD_HANDLERS": {
                    "https": "scraper.handlers.HybridDownloadHandler",
                    "http": "scraper.handlers.HybridDownloadHandler",
                },
                # Open data, but the cross-product is large — stay polite and let AutoThrottle
                # back off if the server slows.
                "CONCURRENT_REQUESTS": 5,
                "DOWNLOAD_DELAY": 0.5,
                "RANDOMIZE_DOWNLOAD_DELAY": True,
                "URLLENGTH_LIMIT": 0,
                "HTTPERROR_ALLOW_ALL": True,
                "ROBOTSTXT_OBEY": False,
                "RETRY_ENABLED": True,
                "RETRY_TIMES": 2,
                # Cache so the large cross-product crawl is resumable across runs.
                "HTTPCACHE_ENABLED": True,
                "HTTPCACHE_IGNORE_HTTP_CODES": [403, 500, 502, 503],
                "HTTPCACHE_ZSTD_DICT_SAMPLE_COUNT": 20,
                "HTTPCACHE_STORAGE": "scraper.cache_storages.zstd.ZstdSqliteCacheStorage",
            },
            priority="spider",
        )

    def __init__(
        self,
        years: str | None = None,
        min_year: int | str = DEFAULT_MIN_YEAR,
        kd_klpd: str | None = None,
        kd_lpse: str | None = None,
        services: str | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.years = _parse_years(years, int(min_year))
        self.klpd_codes = _parse_codes(kd_klpd)
        self.lpse_codes = _parse_codes(kd_lpse)
        self.services = (
            tuple(s.strip() for s in services.split(",") if s.strip())
            if services
            else DEFAULT_SERVICES
        )
        # One sticky-session proxy for the whole crawl (same egress IP everywhere). The API may
        # rate-limit per IP, so thread it through every request via meta['proxy'].
        self.proxy = pick_proxy()
        logger.info(
            "isb spider configured",
            years=self.years,
            services=self.services,
            kd_klpd=self.klpd_codes or "all",
            kd_lpse=self.lpse_codes or "all",
            proxy=self.proxy.username if self.proxy else None,
        )

    # ------------------------------------------------------------------ request helpers
    def _proxy_meta(self) -> dict:
        # HttpProxyMiddleware splits meta['proxy'] into a Proxy-Authorization header, which
        # scrapy_impersonate re-applies to curl_cffi — so every leg exits from the one IP.
        return {"proxy": self.proxy.url} if self.proxy else {}

    def _api_request(
        self, url: str, callback, *, partition: str, meta_extra: dict, priority: int = 0
    ) -> scrapy.Request:
        headers = navigation_headers()
        # JSON for the master/blacklist endpoints; the tender endpoint serves CSV/JSON — this
        # accept covers both. Server ignores it for the CSV route.
        headers["accept"] = "application/json, text/plain, */*"
        return scrapy.Request(
            url,
            callback=callback,
            headers=headers,
            priority=priority,
            dont_filter=True,
            meta={
                "impersonate": IMPERSONATE,
                "impersonate_args": {"default_headers": False},
                "referrer_policy": "no-referrer",
                "cookiejar": "cf",
                "cache_partition_key": partition,
                **self._proxy_meta(),
                **meta_extra,
            },
        )

    # ------------------------------------------------------------------ entry point
    async def start(self):
        # MasterKLPD: needed when the blacklist runs without an explicit code list (to discover
        # codes), and emitted as an item whenever the klpd service is enabled.
        want_klpd_item = "klpd" in self.services
        need_klpd_codes = "blacklist" in self.services and self.klpd_codes is None
        if want_klpd_item or need_klpd_codes:
            yield self._api_request(
                MASTER_KLPD,
                self.parse_klpd,
                partition=f"{self.name}-master-klpd",
                meta_extra={"service": "MasterKLPD", "emit": want_klpd_item},
                priority=self.MASTER_PRIORITY,
            )
        elif "blacklist" in self.services:
            # Codes supplied explicitly — fan out directly, no master fetch.
            for request in self._blacklist_requests(self.klpd_codes or []):
                yield request

        want_lpse_item = "lpse" in self.services
        need_lpse_codes = "tender" in self.services and self.lpse_codes is None
        if want_lpse_item or need_lpse_codes:
            yield self._api_request(
                MASTER_LPSE,
                self.parse_lpse,
                partition=f"{self.name}-master-lpse",
                meta_extra={"service": "MasterLPSE", "emit": want_lpse_item},
                priority=self.MASTER_PRIORITY,
            )
        elif "tender" in self.services:
            for request in self._tender_requests(self.lpse_codes or []):
                yield request

    # ------------------------------------------------------------------ master lists
    def parse_klpd(self, response):
        if response.meta.get("emit"):
            yield self._item(response, {"service": "MasterKLPD"})
        if "blacklist" not in self.services:
            return
        codes = self.klpd_codes or self._extract_codes(response, "kd_klpd")
        logger.info("klpd codes resolved", n=len(codes), years=self.years)
        yield from self._blacklist_requests(codes)

    def parse_lpse(self, response):
        if response.meta.get("emit"):
            yield self._item(response, {"service": "MasterLPSE"})
        if "tender" not in self.services:
            return
        codes = self.lpse_codes or self._extract_codes(response, "kd_lpse")
        logger.info("lpse codes resolved", n=len(codes), years=self.years)
        yield from self._tender_requests(codes)

    def _extract_codes(self, response, field: str) -> list[str]:
        # Master lists are a flat JSON array of objects; pull the code field off each row.
        try:
            rows = response.json()
        except Exception:
            logger.error(
                "failed to parse master list JSON",
                url=response.url,
                status=response.status,
                body=response.text[:200],
            )
            return []
        codes: list[str] = []
        for row in rows:
            value = row.get(field)
            if value is not None and str(value).strip():
                codes.append(str(value).strip())
        return codes

    # ------------------------------------------------------------------ per-code fan-out
    def _blacklist_requests(self, codes: list[str]):
        for year in self.years:
            for code in codes:
                yield self._api_request(
                    SANKSI.format(tahun=year, kd_klpd=code),
                    self.parse_blacklist,
                    partition=f"{self.name}-blacklist-{year}",
                    meta_extra={
                        "service": "SanksiDaftarHitam",
                        "year": year,
                        "kd_klpd": code,
                    },
                )

    def _tender_requests(self, codes: list[str]):
        for year in self.years:
            for code in codes:
                yield self._api_request(
                    TENDER.format(tahun=year, kd_lpse=code),
                    self.parse_tender,
                    partition=f"{self.name}-tender-{year}",
                    meta_extra={
                        "service": "TenderUmumPublik",
                        "year": year,
                        "kd_lpse": code,
                    },
                )

    def parse_blacklist(self, response):
        yield self._item(
            response,
            {
                "service": "SanksiDaftarHitam",
                "year": response.meta["year"],
                "kd_klpd": response.meta["kd_klpd"],
            },
        )

    def parse_tender(self, response):
        yield self._item(
            response,
            {
                "service": "TenderUmumPublik",
                "year": response.meta["year"],
                "kd_lpse": response.meta["kd_lpse"],
            },
        )

    # ------------------------------------------------------------------ item
    def _item(self, response, extra: dict) -> BaseItem:
        # Raw capture: the verbatim body goes in content, the request context in extra. No
        # field parsing here (project convention) — downstream jobs parse the JSON/CSV.
        return BaseItem(
            request_url=response.request.url,
            response_url=response.url,
            domain="isb.lkpp.go.id",
            status=response.status,
            scraped_at=datetime.now(UTC).isoformat(),
            content=response.text,
            extra=extra,
        )
