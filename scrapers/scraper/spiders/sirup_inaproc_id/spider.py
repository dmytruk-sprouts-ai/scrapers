from typing import Any
from datetime import UTC, datetime
from dataclasses import dataclass, replace, field
from urllib.parse import urlencode, urlsplit, parse_qsl
import scrapy
from scrapy.exceptions import CloseSpider
from scrapy.utils.request import RequestFingerprinter
from w3lib.url import url_query_cleaner
from scraper.items import BaseItem
from scraper.spiders.base import BaseSpider
from scraper.browser_profile import navigation_headers, IMPERSONATE
from scrapy_playwright.page import PageMethod
import structlog

logger = structlog.get_logger(__name__)
# DataTables column order as sent by the page. Index = order[0][column] sort target.
# (data name, searchable/orderable)
SEARCH_COLUMNS = [
    ("", False),            # 0  control column
    ("paket", True),        # 1
    ("pagu", True),         # 2
    ("jenisPengadaan", True),  # 3
    ("isPDN", True),        # 4
    ("isUMK", True),        # 5
    ("metode", True),       # 6
    ("pemilihan", True),    # 7
    ("kldi", True),         # 8
    ("satuanKerja", True),  # 9
    ("lokasi", True),       # 10
    ("id", True),           # 11
]

SEARCH_URL = "https://sirup.inaproc.id/sirup/caripaketctr/search"
# Per-package detail page; `idPaket` is the listing row's `id`.
DETAIL_URL = "https://sirup.inaproc.id/sirup/rup/detailPaketPenyedia2020"

@dataclass(frozen=True)
class SearchQuery:
    """Immutable description of one DataTables search request.

    Render with ``to_url()``, walk pages with ``next_page()``, and parse an
    existing URL back into state with ``from_url()``. Being frozen, advancing a
    page returns a *new* query rather than mutating this one, so a query is safe
    to reuse / log / compare.

    page:        0-based page index (page 0 -> start=0).
    length:      rows per request (page size).
    sort_column: column index to sort on, see SEARCH_COLUMNS.
    sort_dir:    "asc" or "desc".
    """

    page: int = 0
    length: int = 10000
    sort_column: int = 7
    sort_dir: str = "asc"
    tahun_anggaran: int = 2026

    @property
    def start(self) -> int:
        """Row offset DataTables expects (derived, never stored)."""
        return self.page * self.length

    @property
    def draw(self) -> int:
        """DataTables draw counter, derived so it can't drift from the page."""
        return self.page + 1

    def next_page(self) -> "SearchQuery":
        """Return the same query advanced one page."""
        return replace(self, page=self.page + 1)

    def to_url(self) -> str:
        params: list[tuple[str, Any]] = [
            ("tahunAnggaran", self.tahun_anggaran),
            ("jenisPengadaan", ""),
            ("metodePengadaan", ""),
            ("minPagu", ""),
            ("maxPagu", ""),
            ("bulan", ""),
            ("lokasi", ""),
            ("kldi", ""),
            ("pdn", ""),
            ("ukm", ""),
            ("draw", self.draw),
        ]

        for i, (data, on) in enumerate(SEARCH_COLUMNS):
            flag = "true" if on else "false"
            params += [
                (f"columns[{i}][data]", data),
                (f"columns[{i}][name]", ""),
                (f"columns[{i}][searchable]", flag),
                (f"columns[{i}][orderable]", flag),
                (f"columns[{i}][search][value]", ""),
                (f"columns[{i}][search][regex]", "false"),
            ]

        params += [
            ("order[0][column]", self.sort_column),
            ("order[0][dir]", self.sort_dir),
            ("start", self.start),
            ("length", self.length),
            ("search[value]", ""),
            ("search[regex]", "false"),
            # NB: the DataTables `_=<ms>` cache-bust param is deliberately omitted. The server
            # ignores it, and keeping the URL stable lets Scrapy's HTTP cache actually hit on
            # re-runs instead of writing a fresh entry every time.
        ]

        return f"{SEARCH_URL}?{urlencode(params)}"

    @classmethod
    def from_url(cls, url: str) -> "SearchQuery":
        """Reconstruct the query state from a previously-built search URL."""
        q = dict(parse_qsl(urlsplit(url).query, keep_blank_values=True))
        length = int(q.get("length", cls.length))
        start = int(q.get("start", 0))
        return cls(
            page=start // length,
            length=length,
            sort_column=int(q.get("order[0][column]", cls.sort_column)),
            sort_dir=q.get("order[0][dir]", cls.sort_dir),
            tahun_anggaran=int(q.get("tahunAnggaran", cls.tahun_anggaran)),
        )

    @classmethod
    def next_url(cls, url: str) -> str:
        """Convenience: given a search URL, return the URL for the next page."""
        return cls.from_url(url).next_page().to_url()

@dataclass
class Paginator:
    """Stateful cursor over the search result pages.

    Holds the current query plus the total matching row count (``recordsFiltered``
    from the DataTables response), so it knows when there is nothing left to fetch.
    """
    query: SearchQuery = field(default_factory=SearchQuery)

    def advance(self) -> SearchQuery:
        """Return the current page's query, then move the cursor forward.

        The first call yields the first page (start=0); each later call yields
        the next page.
        """
        current = self.query
        self.query = self.query.next_page()
        return current

    def next_page_url(self) -> str:
        return self.advance().to_url()



class CacheBustStrippingFingerprinter(RequestFingerprinter):
    """Fingerprint requests with the DataTables `_` cache-bust param removed.

    The request still *sends* `_` (the server's JS adds it), but the HTTP cache key
    and the dupefilter ignore it — so the same page fingerprints identically across
    runs and can actually hit the cache, instead of being a fresh miss every time.
    Pages stay distinct because they differ in `start`/`length`/`order`, not in `_`.
    """

    def fingerprint(self, request: scrapy.Request) -> bytes:
        cleaned = url_query_cleaner(request.url, ["_"], remove=True)
        if cleaned != request.url:
            request = request.replace(url=cleaned)
        return super().fingerprint(request)



class SirupInaprocIDSpider(scrapy.Spider):
    name = "sirup_inaproc_id"
    paginator = Paginator()
    

    @classmethod
    def update_settings(cls, settings):
        playwright = {
            "PLAYWRIGHT_BROWSER_TYPE": "chromium",
            "PLAYWRIGHT_LAUNCH_OPTIONS": {
                "headless": False,
                "channel": "chrome",
                # Kept for parity with the default variant so the A/B isolates the engine. patchright
                # also manages navigator.webdriver itself; this arg can be dropped to test which scores
                # cleaner.
                "args": ["--disable-blink-features=AutomationControlled"],
            },
            "PLAYWRIGHT_CONTEXTS": {"default": {"no_viewport": True, "locale": "en-US"}},
            "PLAYWRIGHT_PROCESS_REQUEST_HEADERS": None,
        }
        handlers = {
            "DOWNLOAD_HANDLERS": {
                "https": "scraper.handlers.HybridDownloadHandler",
                "http": "scraper.handlers.HybridDownloadHandler",
            },
        }
        
        super().update_settings(settings) # type: ignore
        settings.setdict(
            {
                # caching
                "HTTPCACHE_ENABLED": True,
                "HTTPCACHE_IGNORE_HTTP_CODES": [403, 500, 502, 503],
                "HTTPCACHE_ZSTD_DICT_SAMPLE_COUNT": 20,
                "HTTPCACHE_STORAGE": "scraper.cache_storages.zstd.ZstdSqliteCacheStorage",
                # cache migrate to another storage settings
                # "DOWNLOADER_MIDDLEWARES": {
                #     "scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware": None, # disable default
                #     "scraper.middlewares.migrate_cache.MigrateCacheMiddleware": 900
                # },
                # "HTTPCACHE_MIGRATE_DESTINATION_STORAGE": "scraper.cache_storages.zstd.ZstdSqliteCacheStorage",
    
                # Anti-block posture for Cloudflare: one request in flight at a time, a
                # randomized base delay so the cadence isn't robotic, and AutoThrottle to
                # back off further whenever the server's latency rises.
                "CONCURRENT_REQUESTS": 1,
                "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
                "DOWNLOAD_DELAY": 3.0,
                "RANDOMIZE_DOWNLOAD_DELAY": True,  # actual delay = 0.5x–1.5x DOWNLOAD_DELAY
                "AUTOTHROTTLE_ENABLED": True,
                "AUTOTHROTTLE_START_DELAY": 3.0,
                "AUTOTHROTTLE_MAX_DELAY": 30.0,
                "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
                # DataTables search URL is ~2.4k chars; disable the 2083 cap (0 = no limit).
                "URLLENGTH_LIMIT": 0,
                # Ignore the `_` cache-bust param in the cache key, so pages hit the cache
                # across runs instead of missing on every fresh timestamp.
                "REQUEST_FINGERPRINTER_CLASS": CacheBustStrippingFingerprinter,
                'HTTPERROR_ALLOW_ALL': True,
                "ROBOTSTXT_OBEY": False,
                "RETRY_ENABLED": False,
                **playwright,
                **handlers
                
            },
            priority="spider",
        )

    # Pagination outranks detail fetching: the scheduler drains every listing page (high
    # priority) before iterating the queued detail requests (default priority 0).
    PAGINATION_PRIORITY = 100

    async def start(self):
        # Resume page = the first page; advance() returns it and moves the cursor to page 1.
        yield self._playwright_request(resume_query=self.paginator.advance())

    def _playwright_request(
        self,
        resume_query: "SearchQuery | None" = None,
        detail_row: dict | None = None,
    ) -> scrapy.Request:
        # Bootstrap (or re-bootstrap) the session in a real browser: load the search page and
        # wait for its DataTables XHR, the signal the server has issued whatever session cookies
        # (JSESSIONID, anti-bot, …) the JSON API requires. Once cookies are harvested, resume the
        # work that triggered this: a listing page (`resume_query`) or a detail page (`detail_row`).
        return scrapy.Request(
            "https://sirup.inaproc.id/sirup/caripaketctr/index",
            callback=self.parse_playwright,
            dont_filter=True,
            # A re-bootstrap is on the critical path; keep it ahead of queued detail work.
            priority=self.PAGINATION_PRIORITY,
            meta={
                "dont_cache": True,
                "playwright": True,
                "playwright_include_page": True,  # needed to harvest the context jar
                "playwright_page_methods": [
                    PageMethod(
                        "wait_for_event",
                        "response",
                        lambda r: "caripaketctr/search" in r.url,
                        timeout=15000,
                    ),
                ],
                "resume_query": resume_query,
                "detail_row": detail_row,
            },
        )

    async def parse_playwright(self, response):
        # The browser earned the session. Harvest the context jar and hand it to curl_cffi,
        # which then drives the paginated JSON API with an impersonated TLS/HTTP2 fingerprint.
        page = response.meta["playwright_page"]

        # If even the real browser is blocked (403), the session can't be re-earned — there is
        # nothing left to fall back to, so stop the whole crawl rather than loop.
        if response.status == 403:
            await page.close()
            raise CloseSpider(f"Playwright bootstrap blocked with 403 at {response.url}")

        try:
            cookies = await page.context.cookies()
        finally:
            await page.close()

        # Pass just name->value: Playwright's full cookie dicts carry a float `expires` that
        # curl_cffi rejects. These seed the shared "cf" jar on the resumed request.
        cookie_dict = {c["name"]: c["value"] for c in cookies}
        if response.meta.get("resume_query") is not None:
            yield self._search_request(response.meta["resume_query"], cookies=cookie_dict)
        else:
            yield self._detail_request(response.meta["detail_row"], cookies=cookie_dict)

    def _search_request(self, query: "SearchQuery", cookies: dict | None = None) -> scrapy.Request:
        # curl_cffi (impersonate) request on the shared "cf" cookiejar. `cookies` seeds the jar
        # on the first hop; later hops pass None and let CookiesMiddleware replay the jar — which
        # by then holds whatever the server rotated in via Set-Cookie.
        return scrapy.Request(
            query.to_url(),
            callback=self.parse,
            headers=navigation_headers(),
            cookies=cookies,
            # Listing pages outrank detail pages so the full index is walked first.
            priority=self.PAGINATION_PRIORITY,
            meta={
                "impersonate": IMPERSONATE,
                "impersonate_args": {"default_headers": False},
                # Stop RefererMiddleware adding a Referer the real navigation lacked.
                "referrer_policy": "no-referrer",
                # One jar for the whole curl_cffi chain; the middleware owns send + Set-Cookie.
                "cookiejar": "cf",
                # caching 
                "cache_partition_key": f"{self.name}-pagination"
            },
            # Distinct pages share a host+path; the cache-bust `_` makes urls unique, but be
            # explicit so the dupefilter never collapses a page.
            dont_filter=True,
        )

    def parse(self, response):
        # 403 => the curl_cffi session/clearance is no longer accepted. Re-run Playwright to
        # earn a fresh jar, then resume *this* page (not page 0). The cursor is untouched, so
        # normal pagination continues once the page succeeds.
        if response.status == 403:
            self.logger.warning("403 on %s — re-bootstrapping session via Playwright", response.url)
            yield self._playwright_request(SearchQuery.from_url(response.url))
        else:
            assert response.status == 200
            data = response.json()
            _query = SearchQuery.from_url(response.url)
            # The active fingerprinter is CacheBustStrippingFingerprinter; its hex digest is the
            # HTTP-cache key (and on-disk dir name) for this request.
            _fp = self.crawler.request_fingerprinter.fingerprint(response.request).hex()
            logger.warning(
                "scraped page",
                status=response.status,
                n=len(data.get("data", [])),
                page=_query.page,
                url=response.url,
                cache_fingerprint=_fp,
            )
            # Each listing row points at a package detail page; fetch it for the full record.
            # The row itself is carried into the detail item's `extra` so nothing is lost.
            # for row in data.get("data", []):
            #     yield self._detail_request(row)

            # Stop when the next page would start past the total matching rows.
            filtered = int(data.get("recordsFiltered", 0))
            next_query = self.paginator.advance()
            if next_query.start < filtered:
                yield self._search_request(next_query)

    # def _detail_request(self, row: dict, cookies: dict | None = None) -> scrapy.Request:
    #     # Detail pages sit behind the same Cloudflare edge, so reuse the shared "cf" jar and
    #     # the impersonated fingerprint — same transport as the search hops. Default priority (0)
    #     # keeps these below pagination, so the whole index is walked before details are fetched.
    #     return scrapy.Request(
    #         f"{DETAIL_URL}?idPaket={row['id']}",
    #         callback=self.parse_detail,
    #         headers=navigation_headers(),
    #         cookies=cookies,
    #         meta={
    #             "impersonate": IMPERSONATE,
    #             "impersonate_args": {"default_headers": False},
    #             "referrer_policy": "no-referrer",
    #             "cookiejar": "cf",
    #             # The listing row travels with the request so the item stays whole even though
    #             # the detail page lacks these fields.
    #             "listing_row": row,
    #             "cache_partition_key": f"{self.name}-details"
    #         },
    #     )

    # def parse_detail(self, response):
    #     # 403 on a detail page => session lapsed. Re-bootstrap via Playwright, then re-issue
    #     # this exact detail request (its listing row rides along in meta).
    #     if response.status == 403:
    #         self.logger.warning("403 on detail %s — re-bootstrapping session", response.url)
    #         yield self._playwright_request(detail_row=response.meta["listing_row"])
    #         return
    #     assert response.status == 200
    #     row = response.meta["listing_row"]
    #     yield BaseItem(
    #         request_url=response.request.url,
    #         response_url=response.url,
    #         domain=urlsplit(response.url).netloc,
    #         status=response.status,
    #         scraped_at=datetime.now(UTC).isoformat(),
    #         content=response.text,   # raw detail-page HTML
    #         extra=row,               # listing fields the detail page doesn't carry
    #     )


