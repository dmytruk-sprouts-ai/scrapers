import collections
from dataclasses import dataclass, replace
from pathlib import Path
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qsl, urlencode, urlsplit

import scrapy
import structlog
from scrapy.exceptions import CloseSpider
from scrapy.extensions.httpcache import DummyPolicy
from scrapy.http import Response
from scrapy.http.request import Request
from scrapy.utils.httpobj import urlparse_cached
from scrapy.utils.project import data_path
from scrapy_playwright.page import PageMethod

from scraper.browser_profile import IMPERSONATE, navigation_headers

from .cache_router import cache_route
from .facets import STEP_ID_MAPPING
from .facets_translation import get_step_grp

if TYPE_CHECKING:
    from scrapy.http.request import Request

logger = structlog.get_logger(__name__)

# JSON listing API. Pagination is a single `page` param; counts live on a sibling
# endpoint (announcement/sumProjectMoneyAndCount -> totalPages / recordsTotal). The
# listing response's own `totalPages` is 0, so we stop on an empty `data.data`.
LIST_URL = "https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/announcement"
# Summary endpoint (sibling of the listing): totals/count for the same filter, no page.
COUNT_URL = f"{LIST_URL}/sumProjectMoneyAndCount"
# The browser's Angular app sends this as Referer on every announcement XHR.
ANNOUNCEMENT_REFERER = (
    "https://process5.gprocurement.go.th/egp-agpc01-web/announcement?keywordSearch="
)


class GPRocurementCachePolicy(DummyPolicy):
    @classmethod
    def is_blocked_pagination(cls, response: Response):
        if (
            "process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/announcement"
            in response.url
        ):
            try:
                if "validateCfTurnTile" in response.json():
                    return True
            except Exception:
                return True

    @classmethod
    def non_complete_page(cls, response: Response):
        if (
            "process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/announcement"
            in response.url
        ):
            try:
                if len(response.json()["data"].get("data", [])) != 10:
                    return True
            except Exception as e:
                logger.error(e, response=response)
                raise e

    def should_cache_request(self, request: Request) -> bool:
        return urlparse_cached(request).scheme not in self.ignore_schemes

    def should_cache_response(self, response: Response, request: Request) -> bool:
        if self.is_blocked_pagination(response):
            return False
        return response.status not in self.ignore_http_codes

    def is_cached_response_fresh(
        self, cachedresponse: Response, request: Request
    ) -> bool:
        if self.is_blocked_pagination(cachedresponse):
            return False
        if self.non_complete_page(cachedresponse):
            return False
        return True

    def is_cached_response_valid(
        self, cachedresponse: Response, response: Response, request: Request
    ) -> bool: ...


@dataclass(frozen=True)
class ListingQuery:
    """Immutable description of one announcement listing request.

    Render with ``to_url()``, walk pages with ``next_page()``, and parse an
    existing URL back into state with ``from_url()`` — so a 401/403 can rebuild
    the exact page that failed and resume there. Being frozen, advancing returns
    a *new* query rather than mutating this one.

    page:           1-based page index (the API is 1-based).
    budget_year:    Thai Buddhist-calendar year (2569 == 2026 CE).
    today_flag:     the API's announcementTodayFlag.
    project_status: the API's projectStatus (the stepGrp id, e.g. "1" for the
                    draft-TOR stage). None leaves the listing unfiltered.
    """

    page: int = 1
    budget_year: int = 2569
    today_flag: bool = False
    project_status: str | None = None

    def next_page(self) -> "ListingQuery":
        return replace(self, page=self.page + 1)

    def _filter_params(self) -> list[tuple[str, Any]]:
        # Param order mirrors the SPA's XHR: budgetYear, projectStatus (when filtering),
        # announcementTodayFlag. Shared by the listing and the summary endpoints.
        params: list[tuple[str, Any]] = [("budgetYear", self.budget_year)]
        if self.project_status:
            params.append(("projectStatus", self.project_status))
        params.append(("announcementTodayFlag", "true" if self.today_flag else "false"))
        return params

    def to_url(self) -> str:
        return f"{LIST_URL}?{urlencode([*self._filter_params(), ('page', self.page)])}"

    def to_count_url(self) -> str:
        # Same filter as the listing, but no page — returns totals/count for the filter.
        return f"{COUNT_URL}?{urlencode(self._filter_params())}"

    @classmethod
    def from_url(cls, url: str) -> "ListingQuery":
        q = dict(parse_qsl(urlsplit(url).query, keep_blank_values=True))
        return cls(
            page=int(q.get("page", 1)),
            budget_year=int(q.get("budgetYear", cls.budget_year)),
            today_flag=q.get("announcementTodayFlag", "false") == "true",
            project_status=q.get("projectStatus") or None,
        )


async def init_page(page, request):
    # cache static assets; Cloudflare + data API pass straight through
    await page.route("**/*", cache_route)


async def handler_response(
    event: str, r, hc: dict[str, Any]
):  # 3xx redirects / failed responses have no body
    if (
        "process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/announcement?budgetYear="
        not in r.url
    ):
        return
    t = r.request.timing
    hc[event].append(
        {
            "r": r,
            "status": r.status,
            "url": r.url,
            "res_headers": r.headers,
            "req_headers": r.request.headers,
            "timing": t,
        }
    )


async def populate_body(response):  # 3xx redirects / failed responses have no body
    # playwright page musdt be present
    for entry in response.meta["handlers_context"].get("response", []):
        try:
            entry["body"] = await entry["r"].body()
        except Exception:
            entry["body"] = None


STAGES = {
    "draft": "Draft TOR Preparation",
    "draft-approval": "Head of Government Agency Approval",
    "invitation": "Invitation Announcement",
    "purchase-approval": "Head of Government Agency Purchase Approval",
    "contract-value": "Contract Value",
}
OPPORTUNITY_STAGES = {"draft", "draft-approval", "invitation"}


def map_stage_to_original(stage_eng: str) -> str:
    revers = {v: k for k, v in get_step_grp.items()}
    return revers[stage_eng]


def map_stage_to_english(stage: str) -> str:
    return get_step_grp[stage]


def get_stage_id(stage: str) -> str:
    if stage not in STEP_ID_MAPPING:
        stage = map_stage_to_original(stage)
    return STEP_ID_MAPPING[stage]


# The API's budgetYear is a Thai Buddhist-calendar year, 543 ahead of the Gregorian
# (CE) year the spider is configured with: 2026 CE == 2569 BE.
BUDDHIST_YEAR_OFFSET = 543


def to_budget_year(year_ce: int) -> int:
    """Gregorian (CE) year -> the API's Thai Buddhist budgetYear."""
    return year_ce + BUDDHIST_YEAR_OFFSET


def from_budget_year(budget_year: int) -> int:
    """Thai Buddhist budgetYear -> Gregorian (CE) year."""
    return budget_year - BUDDHIST_YEAR_OFFSET


class GprocurementGoTh(scrapy.Spider):
    name = "gprocurement_go_th"

    # will be configured later
    stage = "draft"
    # Gregorian (CE) year to crawl; converted to the API's Thai Buddhist budgetYear.
    year = 2026

    # Pagination outranks any future detail fetching: drain every listing page first.
    PAGINATION_PRIORITY = 100

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
            "PLAYWRIGHT_CONTEXTS": {
                "default": {"no_viewport": True, "locale": "en-US"}
            },
            "PLAYWRIGHT_PROCESS_REQUEST_HEADERS": None,
            "HTTPCACHE_POLICY": GPRocurementCachePolicy,
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
                "HTTPCACHE_ENABLED": True,
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
                "AUTOTHROTTLE_START_DELAY": 5.0,
                "AUTOTHROTTLE_MAX_DELAY": 30.0,
                "AUTOTHROTTLE_TARGET_CONCURRENCY": 1.0,
                # DataTables search URL is ~2.4k chars; disable the 2083 cap (0 = no limit).
                "URLLENGTH_LIMIT": 0,
                # Ignore the `_` cache-bust param in the cache key, so pages hit the cache
                # across runs instead of missing on every fresh timestamp.
                "HTTPERROR_ALLOW_ALL": True,
                "ROBOTSTXT_OBEY": False,
                "RETRY_ENABLED": False,
                **playwright,
                **handlers,
            },
            priority="spider",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Per-partition set of project ids already written this run, so cache replays /
        # overlapping pages don't append duplicates to the on-disk file.
        self._seen_ids: dict[str, set[str]] = {}
        # Partitions whose summary counts have already been fetched, so a mid-crawl
        # re-bootstrap doesn't re-request them.
        self._counts_fetched: set[str] = set()

    @property
    def project_status(self) -> str:
        # Resolve the configured stage ("draft", ...) to the API's projectStatus id (the
        # stepGrp id, "1".."5") used to filter the listing.
        return get_stage_id(STAGES[self.stage])

    @property
    def budget_year(self) -> int:
        # Resolve the configured Gregorian year to the API's Thai Buddhist budgetYear.
        return to_budget_year(self.year)

    async def start(self):
        # Bootstrap the session in a real browser, then resume curl_cffi pagination at page 1.
        # yield self._playwright_request(resume_query=ListingQuery())
        yield self._listing_request(
            query=ListingQuery(
                budget_year=self.budget_year, project_status=self.project_status
            ),
            tokens={},
        )

    def _playwright_request(
        self,
        resume_query: "ListingQuery | None" = None,
    ) -> scrapy.Request:
        hc = collections.defaultdict(list)
        return scrapy.Request(
            "https://process5.gprocurement.go.th/egp-agpc01-web/announcement?keywordSearch=",
            callback=self.parse_playwright,
            dont_filter=True,
            # A re-bootstrap is on the critical path; keep it ahead of queued detail work.
            meta={
                "dont_cache": True,
                "playwright": True,
                "playwright_include_page": True,  # needed to harvest the context jar
                "playwright_page_init_callback": init_page,
                "playwright_page_goto_kwargs": {
                    "timeout": 600000,  # Individual 60-second limit for this specific URL
                },
                "playwright_page_methods": [
                    PageMethod(
                        "wait_for_event",
                        "response",
                        lambda r: (
                            "process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/announcement?budgetYear="
                            in r.url
                        ),
                        timeout=60000,
                    ),
                ],
                "playwright_page_event_handlers": {
                    "response": lambda response: handler_response(
                        "response", response, hc
                    ),
                },
                "handlers_context": hc,
                # The page to resume on once the session is earned (defaults to page 1).
                "resume_query": resume_query,
            },
        )

    async def parse_playwright(self, response):
        # The browser earned the session. Harvest two things and hand them to curl_cffi, which
        # then drives the paginated JSON API with an impersonated TLS/HTTP2 fingerprint:
        #   1. the cookie jar (Xsrf-Token + the TS* anti-bot cookies), and
        #   2. the per-session API tokens the Angular app injects into every announcement XHR
        #      (X-Announcement-Token, X-Xsrf-Token). Unlike cookies, Scrapy will NOT replay
        #      these, so they must be carried in meta and re-attached to every page.
        page = response.meta["playwright_page"]

        # If even the real browser is blocked (403), the session can't be re-earned — there is
        # nothing left to fall back to, so stop the whole crawl rather than loop.
        if response.status == 403:
            await page.close()
            raise CloseSpider(
                f"Playwright bootstrap blocked with 403 at {response.url}"
            )

        try:
            await populate_body(response=response)
            list_items_responses = response.meta["handlers_context"].get("response", [])
            assert len(list_items_responses) == 1
            req_headers = list_items_responses[0]["req_headers"]
            # req_headers_access example
            # {
            #     'x-announcement-token': 'RUdQLUFOTk9VTkNFTUVOVC1LRVk6MTc4MTIwMjU1NDU2NjpheDRaVkdtem1LcEFGTHBVZmtVMzFXWE5odGlqSEo0amI1bEhqMEtzTFBRPQ==',
            #     'x-xsrf-token': '+JDBxwZsPXXECdkSKzbFZ9MfScktVZzsgYN1Cngmen2JX1i9DsSFoVScCvsPS34z3ihvnb3iMjarVswFcgBeJw==',
            #     'cookie': 'Xsrf-Token=69b8cfd1c3c28d712a56a782dd46c59cf9d0d3ad; TS0174b17a=010cf4a45346ec5e1bc07a4f0af15ce67ef30ce496551758aebf4c07bc52fdc60e2472e0556e84841ee882b46638df47b80125ed031a9d23181471366bed915490e6671b20; TS4c538cb7027=0851e63e8dab20005320710dcc62c43e46663bc269d7deffe3bccb156fe3b933721c41433fcdeb31086b8f4e13113000b54befa53198f3a7bcf33a9c7cfbb3646ccdd5a1d043fb6f7550b24d76309c14a733ae91b2e0144e8898c3d193badca6'
            # }

            # The token carries an embedded expiry (~2h out), so it's reusable across the
            # whole pagination chain until it lapses — at which point parse() re-bootstraps.
            api_tokens = {
                "x-announcement-token": req_headers["x-announcement-token"],
                "x-xsrf-token": req_headers["x-xsrf-token"],
            }
            cookies = await page.context.cookies()
        finally:
            await page.close()

        # Pass just name->value: Playwright's full cookie dicts carry a float `expires` that
        # curl_cffi rejects. These seed the shared "cf" jar on the resumed request.
        cookie_dict = {c["name"]: c["value"] for c in cookies}
        # Detail requests re-sign X-Xsrf-Token per call from the (session-stable) Xsrf-Token
        # cookie, so carry its value alongside the harvested tokens.
        api_tokens["xsrf-cookie"] = cookie_dict.get("Xsrf-Token")
        resume_query = response.meta["resume_query"]
        # Cloudflare is cleared and the session earned — fetch the summary counts once per
        # partition before resuming pagination on the same session.
        if self._partition_key(resume_query) not in self._counts_fetched:
            self._counts_fetched.add(self._partition_key(resume_query))
            yield self._count_request(
                resume_query, tokens=api_tokens, cookies=cookie_dict
            )
        yield self._listing_request(
            resume_query, tokens=api_tokens, cookies=cookie_dict
        )

    def _api_headers(self, tokens: dict) -> dict:
        # Start from the canonical Chrome profile, then override the navigation-specific bits
        # to the fetch/CORS shape the announcement XHR actually uses, and inject the session
        # tokens. (curl_cffi sends exactly these — default_headers is off.)
        headers = navigation_headers()
        headers.pop("upgrade-insecure-requests", None)
        headers.pop("sec-fetch-user", None)
        headers.update(
            {
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
                "referer": ANNOUNCEMENT_REFERER,
            }
        )
        if tokens:
            headers.update(
                {
                    "x-announcement-token": tokens["x-announcement-token"],
                    "x-xsrf-token": tokens["x-xsrf-token"],
                }
            )
        return headers

    def _listing_request(
        self, query: "ListingQuery", tokens: dict, cookies: dict | None = None
    ) -> scrapy.Request:
        # curl_cffi (impersonate) request on the shared "cf" cookiejar. `cookies` seeds the jar
        # on the first hop; later hops pass None and let CookiesMiddleware replay the jar — which
        # by then holds whatever the server rotated in via Set-Cookie. The API tokens ride in
        # meta so every page re-attaches them via _api_headers().
        return scrapy.Request(
            query.to_url(),
            callback=self.parse,
            headers=self._api_headers(tokens),
            cookies=cookies,
            # Listing pages outrank any detail pages so the full index is walked first.
            priority=self.PAGINATION_PRIORITY,
            meta={
                "impersonate": IMPERSONATE,
                "impersonate_args": {"default_headers": False},
                # Stop RefererMiddleware adding a Referer; we set the exact one ourselves.
                "referrer_policy": "no-referrer",
                # One jar for the whole curl_cffi chain; the middleware owns send + Set-Cookie.
                "cookiejar": "cf",
                # Carry the session tokens forward to the next page (Scrapy won't replay them).
                "api_tokens": tokens,
                # caching
                "cache_partition_key": self._partition_key(query),
            },
            dont_filter=True,
        )

    def _count_request(
        self, query: "ListingQuery", tokens: dict, cookies: dict | None = None
    ) -> scrapy.Request:
        # One-off summary fetch on the same impersonated "cf" session as the listing. Not
        # cached — we persist the JSON to the partition's counts file ourselves.
        return scrapy.Request(
            query.to_count_url(),
            callback=self.parse_count,
            headers=self._api_headers(tokens),
            cookies=cookies,
            priority=self.PAGINATION_PRIORITY,
            meta={
                "impersonate": IMPERSONATE,
                "impersonate_args": {"default_headers": False},
                "referrer_policy": "no-referrer",
                "cookiejar": "cf",
                "api_tokens": tokens,
                "dont_cache": True,
                # Carry the query so parse_count can resolve the output path.
                "count_query": query,
            },
            dont_filter=True,
        )

    def parse_count(self, response):
        query = response.meta["count_query"]
        if response.status != 200:
            logger.warning(
                "sumProjectMoneyAndCount failed",
                status=response.status,
                url=response.url,
            )
            return
        self._store_counts(query, response.text)
        logger.info(
            "stored summary counts",
            path=str(self._counts_path(query)),
            url=response.url,
        )

    def _partition_key(self, query: "ListingQuery") -> str:
        # One partition per (spider, budgetYear, stage). The pagination cache and the
        # project-ids file are both keyed by this so they stay aligned.
        return f"{self.name}-pagination-{query.budget_year}-{query.project_status or 'all'}"

    def _partition_dir(self) -> Path:
        # Same folder the cache storage writes its partitions into:
        # data_path(HTTPCACHE_DIR) / <safe_spider_name> (see ZstdSqliteCacheStorage).
        cachedir = data_path(self.settings["HTTPCACHE_DIR"], createdir=True)
        safe_name = "".join(c if c.isalnum() else "_" for c in self.name).rstrip("_")
        out_dir = Path(cachedir) / safe_name
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir

    def _project_ids_path(self, query: "ListingQuery") -> Path:
        # Project ids: one id per line, keyed by the same partition as the cache.
        return self._partition_dir() / f"{self._partition_key(query)}.project_ids.txt"

    def _counts_path(self, query: "ListingQuery") -> Path:
        # Summary counts JSON, partitioned alongside the project-ids file.
        return self._partition_dir() / f"{self._partition_key(query)}.counts.json"

    def _store_counts(self, query: "ListingQuery", body: str) -> None:
        self._counts_path(query).write_text(body, encoding="utf-8")

    def _store_project_ids(self, query: "ListingQuery", rows: list[dict]) -> None:
        # Append this page's project ids to the partition's file, skipping any already
        # written this run so the file holds each id once.
        seen = self._seen_ids.setdefault(self._partition_key(query), set())
        new_ids = []
        for row in rows:
            pid = row.get("projectId")
            if pid is None:
                continue
            pid = str(pid)
            if pid not in seen:
                seen.add(pid)
                new_ids.append(pid)
        if not new_ids:
            return
        with self._project_ids_path(query).open("a", encoding="utf-8") as f:
            f.write("".join(f"{pid}\n" for pid in new_ids))

    def parse(self, response):
        # if response.status == 429:
        #     # timelimited, neew context needed
        #     raise CloseSpider(reason="429 too many requests")
        # 401/403 => the session/token is no longer accepted (token expired or jar lapsed).
        # Re-run Playwright to earn a fresh jar + tokens, then resume *this* page (not page 1).
        if response.status in (
            401,
            403,
            429,
        ) or GPRocurementCachePolicy.is_blocked_pagination(response):
            self.logger.warning(
                "%s on %s — re-bootstrapping session via Playwright",
                response.status,
                response.url,
            )
            yield self._playwright_request(
                resume_query=ListingQuery.from_url(response.url)
            )
        else:
            assert response.status == 200
            # TODO: MUST NOT STORE BAD RESPONSES
            query = ListingQuery.from_url(response.url)
            try:
                payload = response.json()["data"]  # fails here
                rows = payload.get("data", [])
                logger.info(
                    "scraped page",
                    status=response.status,
                    n=len(rows),
                    page=query.page,
                    url=response.url,
                )
            except Exception:
                logger.error(
                    "malformed pagination page",
                    status=response.status,
                    url=response.url,
                    payload=response.json(),
                    meta=response.meta,
                    flags=response.flags,
                )
                rows = []

            tokens = response.meta["api_tokens"]

            # Persist this page's project ids; detail collection is a separate pass that reads
            # these files. Stored alongside the pagination cache, keyed by the same partition.
            self._store_project_ids(query, rows)

            # The listing response's own totalPages is 0, so terminate when a page comes back empty.
            if rows:
                yield self._listing_request(query.next_page(), tokens=tokens)
            else:
                logger.warning(
                    "no more pages to follow (empty page encountered)", url=response.url
                )
