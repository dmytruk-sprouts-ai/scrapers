import re
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from urllib.parse import urlencode, urlsplit

import scrapy
import structlog
from scrapy.exceptions import CloseSpider
from scrapy_playwright.page import PageMethod

from scraper.browser_profile import (
    IMPERSONATE,
    PLATFORM,
    SEC_CH_UA,
    USER_AGENT,
    navigation_headers,
)
from scraper.items import BaseItem

logger = structlog.get_logger(__name__)

# SPSE is multi-tenant: one LPSE instance per sub-path (here DKI Jakarta -> /jakarta/).
BASE_URL = "https://spse.inaproc.id"

# DataTables column layout for the `dt/lelang` grid. Unlike sirup the `data` name is just the
# column index; index 3 (the "tahap" link column) is neither searchable nor orderable.
# (index, searchable/orderable)
SEARCH_COLUMNS = [
    (0, True),
    (1, True),
    (2, True),
    (3, False),
    (4, True),
    (5, True),
]

# The landing page embeds the per-session CSRF token inline in the DataTables ajax config:
#   d.authenticityToken = 'dcb41c34746cc7c64e01b1688be6bddb0aac3241';
_TOKEN_RE = re.compile(r"authenticityToken\s*=\s*['\"]([0-9a-fA-F]+)['\"]")
# ...and the budget year as a query param on that same ajax url: url : "/jakarta/dt/lelang?tahun=2027"
_TAHUN_RE = re.compile(r"dt/lelang\?tahun=(\d+)")


@dataclass(frozen=True)
class SearchQuery:
    """Immutable description of one DataTables `dt/lelang` POST request.

    Render the body with ``to_body()`` and walk pages with ``next_page()``. Being frozen,
    advancing a page returns a *new* query, so a query is safe to reuse / log / compare.

    The session-scoped ``authenticity_token`` (CSRF) and ``tahun`` (budget year) are scraped
    from the landing page during the Playwright bootstrap and threaded through every page.

    page:        0-based page index (page 0 -> start=0).
    length:      rows per request (page size).
    sort_column: column index to sort on, see SEARCH_COLUMNS.
    sort_dir:    "asc" or "desc".
    """

    lpse: str = "jakarta"
    tahun: int = 2027
    authenticity_token: str = ""
    page: int = 0
    length: int = 100
    sort_column: int = 5
    sort_dir: str = "desc"

    @property
    def start(self) -> int:
        """Row offset DataTables expects (derived, never stored)."""
        return self.page * self.length

    @property
    def draw(self) -> int:
        """DataTables draw counter, derived so it can't drift from the page."""
        return self.page + 1

    @property
    def url(self) -> str:
        return f"{BASE_URL}/{self.lpse}/dt/lelang?tahun={self.tahun}"

    @property
    def referer(self) -> str:
        return f"{BASE_URL}/{self.lpse}/lelang"

    def next_page(self) -> "SearchQuery":
        """Return the same query advanced one page."""
        return replace(self, page=self.page + 1)

    def to_body(self) -> str:
        """Render the application/x-www-form-urlencoded POST body."""
        params: list[tuple[str, object]] = [("draw", self.draw)]
        for i, on in SEARCH_COLUMNS:
            flag = "true" if on else "false"
            params += [
                (f"columns[{i}][data]", i),
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
            ("authenticityToken", self.authenticity_token),
        ]
        return urlencode(params)


@dataclass
class Paginator:
    """Stateful cursor over the search result pages.

    The server reports ``recordsFiltered`` as Integer.MAX_VALUE (a sentinel, not a real count),
    so there is no total to compare against — the spider instead stops when a page comes back
    short (fewer rows than ``length``). This cursor only tracks the current page.
    """

    query: SearchQuery = field(default_factory=SearchQuery)

    def advance(self) -> SearchQuery:
        """Return the current page's query, then move the cursor forward."""
        current = self.query
        self.query = self.query.next_page()
        return current


def ajax_headers(referer: str) -> dict[str, str]:
    """Headers for the DataTables XHR, matching what Chrome sends for the `dt/lelang` POST."""
    return {
        "sec-ch-ua": SEC_CH_UA,
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": f'"{PLATFORM}"',
        "user-agent": USER_AGENT,
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "x-requested-with": "XMLHttpRequest",
        "origin": BASE_URL,
        "referer": referer,
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US",
    }


class SpceInaprocIDSpider(scrapy.Spider):
    name = "spce_inaproc_id"
    # Which LPSE instance (sub-path) to crawl. Override via -a lpse=... if needed.
    lpse = "jakarta"

    def __init__(self, lpse: str | None = None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if lpse:
            self.lpse = lpse
        self.paginator = Paginator(query=SearchQuery(lpse=self.lpse))

    @classmethod
    def update_settings(cls, settings):
        playwright = {
            "PLAYWRIGHT_BROWSER_TYPE": "chromium",
            "PLAYWRIGHT_LAUNCH_OPTIONS": {
                "headless": False,
                "channel": "chrome",
                "args": ["--disable-blink-features=AutomationControlled"],
            },
            "PLAYWRIGHT_CONTEXTS": {
                "default": {"no_viewport": True, "locale": "en-US"}
            },
            "PLAYWRIGHT_PROCESS_REQUEST_HEADERS": None,
        }
        handlers = {
            "DOWNLOAD_HANDLERS": {
                "https": "scraper.handlers.HybridDownloadHandler",
                "http": "scraper.handlers.HybridDownloadHandler",
            },
        }

        super().update_settings(settings)  # type: ignore
        settings.setdict(
            {
                # caching
                "HTTPCACHE_ENABLED": False,
                "HTTPCACHE_IGNORE_HTTP_CODES": [403, 500, 502, 503],
                "HTTPCACHE_ZSTD_DICT_SAMPLE_COUNT": 20,
                "HTTPCACHE_STORAGE": "scraper.cache_storages.zstd.ZstdSqliteCacheStorage",
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
                "URLLENGTH_LIMIT": 0,
                "HTTPERROR_ALLOW_ALL": True,
                "ROBOTSTXT_OBEY": False,
                "RETRY_ENABLED": False,
                **playwright,
                **handlers,
            },
            priority="spider",
        )

    # Pagination outranks detail fetching: the scheduler drains every listing page (high
    # priority) before iterating the queued detail requests (default priority 0).
    PAGINATION_PRIORITY = 100

    async def start(self):
        # First hop is always a Playwright bootstrap: it solves the Cloudflare challenge and
        # harvests both the session cookies and the per-session CSRF token from the page.
        yield self._playwright_request(resume_query=self.paginator.advance())

    def _playwright_request(
        self,
        resume_query: "SearchQuery | None" = None,
        detail_id: str | None = None,
        detail_row: dict | list | None = None,
    ) -> scrapy.Request:
        # Bootstrap (or re-bootstrap) the session in a real browser: load the listing page and
        # wait for its DataTables XHR — the signal that the server has issued the session cookies
        # (cf_clearance, __cf_bm, SPSE_SESSION, …) and rendered the inline authenticityToken. Once
        # cookies + token are harvested, resume the work that triggered this: a listing page
        # (`resume_query`) or a detail page (`detail_id`).
        return scrapy.Request(
            f"{BASE_URL}/{self.lpse}/lelang",
            callback=self.parse_playwright,
            dont_filter=True,
            priority=self.PAGINATION_PRIORITY,
            meta={
                "dont_cache": True,
                "playwright": True,
                "playwright_include_page": True,  # needed to harvest the context jar
                "playwright_page_methods": [
                    PageMethod(
                        "wait_for_event",
                        "response",
                        lambda r: "dt/lelang" in r.url,
                        timeout=15000,
                    ),
                ],
                "resume_query": resume_query,
                "detail_id": detail_id,
                "detail_row": detail_row,
            },
        )

    async def parse_playwright(self, response):
        # The browser earned the session. Harvest the context jar + the inline CSRF token, then
        # hand off to curl_cffi which drives the paginated JSON API with an impersonated
        # TLS/HTTP2 fingerprint.
        page = response.meta["playwright_page"]

        # If even the real browser is blocked (403), the session can't be re-earned — stop the
        # whole crawl rather than loop.
        if response.status == 403:
            await page.close()
            raise CloseSpider(
                f"Playwright bootstrap blocked with 403 at {response.url}"
            )

        try:
            html = await page.content()
            cookies = await page.context.cookies()
        finally:
            await page.close()

        token = self._extract_token(html)
        if token is None:
            raise CloseSpider(
                f"Could not find authenticityToken on bootstrap page {response.url}"
            )
        tahun = self._extract_tahun(html)

        # Pass just name->value: Playwright's full cookie dicts carry a float `expires` that
        # curl_cffi rejects. These seed the shared "cf" jar on the resumed request.
        cookie_dict = {c["name"]: c["value"] for c in cookies}

        if response.meta.get("resume_query") is not None:
            resume_query: SearchQuery = response.meta["resume_query"]
            # Refresh the resumed query with the freshly harvested token/year.
            query = replace(
                resume_query,
                authenticity_token=token,
                tahun=tahun if tahun is not None else resume_query.tahun,
            )
            # Keep the paginator's cursor in step with the (possibly updated) year/token so
            # subsequent pages carry them too.
            self.paginator.query = replace(
                self.paginator.query,
                authenticity_token=token,
                tahun=query.tahun,
            )
            yield self._search_request(query, cookies=cookie_dict)
        else:
            yield self._detail_request(
                response.meta["detail_id"],
                response.meta["detail_row"],
                cookies=cookie_dict,
            )

    def _extract_token(self, html: str) -> str | None:
        m = _TOKEN_RE.search(html)
        return m.group(1) if m else None

    def _extract_tahun(self, html: str) -> int | None:
        m = _TAHUN_RE.search(html)
        return int(m.group(1)) if m else None

    def _search_request(
        self, query: "SearchQuery", cookies: dict | None = None
    ) -> scrapy.Request:
        # curl_cffi (impersonate) POST on the shared "cf" cookiejar. `cookies` seeds the jar on
        # the first hop; later hops pass None and let CookiesMiddleware replay the jar — which by
        # then holds whatever the server rotated in via Set-Cookie.
        return scrapy.Request(
            query.url,
            method="POST",
            body=query.to_body(),
            callback=self.parse,
            headers=ajax_headers(query.referer),
            cookies=cookies,
            priority=self.PAGINATION_PRIORITY,
            meta={
                "impersonate": IMPERSONATE,
                "impersonate_args": {"default_headers": False},
                "referrer_policy": "no-referrer",
                "cookiejar": "cf",
                "search_query": query,
                "cache_partition_key": f"{self.name}-pagination",
            },
            # Pages share host+path+body-shape; only `start` differs. Never let the dupefilter
            # collapse a page.
            dont_filter=True,
        )

    def parse(self, response):
        query: SearchQuery = response.meta["search_query"]
        # 403 => the curl_cffi session/clearance is no longer accepted. Re-run Playwright to earn
        # a fresh jar + token, then resume *this* page (cursor untouched, so pagination continues).
        if response.status == 403:
            self.logger.warning(
                "403 on %s — re-bootstrapping session via Playwright", response.url
            )
            yield self._playwright_request(resume_query=query)
            return

        assert response.status == 200
        data = response.json()
        rows = data.get("data", [])
        logger.warning(
            "scraped page",
            status=response.status,
            n=len(rows),
            page=query.page,
            url=response.url,
        )

        # Each listing row points at a package announcement page; fetch it for the full record.
        # row[0] is the package id; the row itself rides into the detail item's `extra`.
        for row in rows:
            yield self._detail_request(row[0], row)

        # The server's recordsFiltered is a sentinel (Integer.MAX_VALUE), so we can't compare
        # against a total. Stop when a page comes back short — that's the last page.
        if len(rows) >= query.length:
            yield self._search_request(self.paginator.advance())

    def _detail_url(self, detail_id: str) -> str:
        return f"{BASE_URL}/{self.lpse}/lelang/{detail_id}/pengumumanlelang"

    def _detail_request(
        self, detail_id: str, row: dict | list, cookies: dict | None = None
    ) -> scrapy.Request:
        # Detail pages sit behind the same Cloudflare edge, so reuse the shared "cf" jar and the
        # impersonated fingerprint. Default priority (0) keeps these below pagination, so the whole
        # index is walked before details are fetched.
        return scrapy.Request(
            self._detail_url(detail_id),
            callback=self.parse_detail,
            headers=navigation_headers(),
            cookies=cookies,
            meta={
                "impersonate": IMPERSONATE,
                "impersonate_args": {"default_headers": False},
                "referrer_policy": "no-referrer",
                "cookiejar": "cf",
                # The listing row travels with the request so the item stays whole even though
                # the detail page lacks these fields.
                "listing_row": row,
                "detail_id": detail_id,
                "cache_partition_key": f"{self.name}-details",
            },
        )

    def parse_detail(self, response):
        # 403 on a detail page => session lapsed. Re-bootstrap via Playwright, then re-issue this
        # exact detail request (its id + listing row ride along in meta).
        if response.status == 403:
            self.logger.warning(
                "403 on detail %s — re-bootstrapping session", response.url
            )
            yield self._playwright_request(
                detail_id=response.meta["detail_id"],
                detail_row=response.meta["listing_row"],
            )
            return
        assert response.status == 200
        row = response.meta["listing_row"]
        yield BaseItem(
            request_url=response.request.url,
            response_url=response.url,
            domain=urlsplit(response.url).netloc,
            status=response.status,
            scraped_at=datetime.now(UTC).isoformat(),
            content=response.text,  # raw announcement-page HTML
            extra=row,  # listing fields the detail page doesn't carry
        )
