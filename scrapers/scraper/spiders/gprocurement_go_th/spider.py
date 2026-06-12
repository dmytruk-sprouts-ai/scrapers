from typing import Any, TYPE_CHECKING
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
from scrapy.extensions.httpcache import DummyPolicy
from scrapy.utils.httpobj import urlparse_cached
from .cache_router import cache_route
from . import crypto
import collections
import json
from scrapy.http.request import Request
from scrapy.http import Headers, Response
if TYPE_CHECKING:
    import os
    from collections.abc import Callable
    from types import ModuleType

    from scrapy.http.request import Request
    from scrapy.settings import BaseSettings
    from scrapy.spiders import Spider
    from scrapy.utils.request import RequestFingerprinterProtocol

logger = structlog.get_logger(__name__)

# JSON listing API. Pagination is a single `page` param; counts live on a sibling
# endpoint (announcement/sumProjectMoneyAndCount -> totalPages / recordsTotal). The
# listing response's own `totalPages` is 0, so we stop on an empty `data.data`.
LIST_URL = "https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/announcement"
# The browser's Angular app sends this as Referer on every announcement XHR.
ANNOUNCEMENT_REFERER = "https://process5.gprocurement.go.th/egp-agpc01-web/announcement?keywordSearch="


class GPRocurementCachePolicy(DummyPolicy):

    @classmethod
    def is_blocked_pagination(cls, response: Response):
        if 'process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/announcement' in response.url:
            try:
                if 'validateCfTurnTile' in response.json():
                    return True
            except Exception:
                return True
    @classmethod    
    def non_complete_page(cls, response: Response):
        if 'process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/announcement' in response.url:
            try:
                if len(response.json()['data'].get('data', [])) != 10:
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
    ) -> bool:
        ...


@dataclass(frozen=True)
class ListingQuery:
    """Immutable description of one announcement listing request.

    Render with ``to_url()``, walk pages with ``next_page()``, and parse an
    existing URL back into state with ``from_url()`` — so a 401/403 can rebuild
    the exact page that failed and resume there. Being frozen, advancing returns
    a *new* query rather than mutating this one.

    page:        1-based page index (the API is 1-based).
    budget_year: Thai Buddhist-calendar year (2569 == 2026 CE).
    today_flag:  the API's announcementTodayFlag.
    """

    page: int = 1
    budget_year: int = 2569
    today_flag: bool = False

    def next_page(self) -> "ListingQuery":
        return replace(self, page=self.page + 1)

    def to_url(self) -> str:
        params = [
            ("budgetYear", self.budget_year),
            ("announcementTodayFlag", "true" if self.today_flag else "false"),
            ("page", self.page),
        ]
        return f"{LIST_URL}?{urlencode(params)}"

    @classmethod
    def from_url(cls, url: str) -> "ListingQuery":
        q = dict(parse_qsl(urlsplit(url).query, keep_blank_values=True))
        return cls(
            page=int(q.get("page", 1)),
            budget_year=int(q.get("budgetYear", cls.budget_year)),
            today_flag=q.get("announcementTodayFlag", "false") == "true",
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


class GprocurementGoTh(scrapy.Spider):
    name = "gprocurement_go_th"

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
            "HTTPCACHE_POLICY": GPRocurementCachePolicy
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
                "AUTOTHROTTLE_START_DELAY": 3.0,
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
    
    yielded = 0

    async def start(self):
        # Bootstrap the session in a real browser, then resume curl_cffi pagination at page 1.
        # yield self._playwright_request(resume_query=ListingQuery())
        yield self._listing_request(query=ListingQuery(), tokens={})

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
        yield self._listing_request(
            response.meta["resume_query"], tokens=api_tokens, cookies=cookie_dict
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
            headers.update({
                "x-announcement-token": tokens["x-announcement-token"],
                "x-xsrf-token": tokens["x-xsrf-token"],
            })
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
                "cache_partition_key": f"{self.name}-pagination-{query.budget_year}",
            },
            dont_filter=True,
        )

    def parse(self, response):
        # 401/403 => the session/token is no longer accepted (token expired or jar lapsed).
        # Re-run Playwright to earn a fresh jar + tokens, then resume *this* page (not page 1).
        if response.status in (401, 403) or GPRocurementCachePolicy.is_blocked_pagination(response):
            self.logger.warning(
                "%s on %s — re-bootstrapping session via Playwright",
                response.status,
                response.url,
            )
            yield self._playwright_request(resume_query=ListingQuery.from_url(response.url))
            return

        assert response.status == 200
        # TODO: MUST NOT STORE BAD RESPONSES
        query = ListingQuery.from_url(response.url)
        try:
            payload = response.json()["data"] # fails here
            rows = payload.get("data", [])
            logger.warning(
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
                flags=response.flags
            )
            rows = []

        tokens = response.meta["api_tokens"]

        # TODO: this does not look good, we will skip many pages
        # TODO: add errorbacks
        # Fan out one detail chain per project. Detail requests run at default priority, so the
        # whole listing (priority=PAGINATION_PRIORITY) is drained first. They need a live session
        # (cookies + a per-session Xsrf-Token to re-sign): when pagination is served straight from
        # cache we have no tokens yet, so skip details until a bootstrap has populated them.
        if tokens.get("xsrf-cookie"):

            for row in rows:
                if row.get("projectId"):
                    logger.warning(
                        "issueing details request", project_id=row.get("projectId")
                    )
                    yield self._generate_token_request(row, tokens)

        # The listing response's own totalPages is 0, so terminate when a page comes back empty.
        if rows and self.yielded < 15:
            self.yielded +=1
            yield self._listing_request(query.next_page(), tokens=tokens)

    # ------------------------------------------------------------------ details
    # Per-project detail chain. The SPA fetches these after the user opens a row:
    #   generateToken -> getProjectDetail -> getProcurementDetail -> greenBook -> infoDeptSub
    # generateToken mints an X-Announcement-Token bound to the (double-encrypted) project id;
    # every later call carries that token plus a freshly re-signed X-Xsrf-Token. We chain them
    # sequentially, accumulating each raw body, and emit a single record at the end.

    DETAIL_ENDPOINT = LIST_URL  # ".../a-egp-allt-project/announcement"
    RDB_DEPT_URL = "https://process5.gprocurement.go.th/egp-rdb-service/infoDeptSub"
    ORIGIN = "https://process5.gprocurement.go.th"

    # Within a project's chain each step outranks the previous, so an in-progress project finishes
    # (token -> projectDetail -> procurement -> greenBook -> deptSub) before the next project's
    # generateToken is dequeued. All stay below PAGINATION_PRIORITY so the listing still drains
    # first. With CONCURRENT_REQUESTS=1 only one chain is ever above the token tier at a time.
    DETAIL_TOKEN_PRIORITY = 1
    DETAIL_PROJECT_PRIORITY = 2
    DETAIL_PROCUREMENT_PRIORITY = 3
    DETAIL_GREENBOOK_PRIORITY = 4
    DETAIL_DEPTSUB_PRIORITY = 5

    def _detail_headers(
        self, tokens: dict, announcement_token: str | None = None, post: bool = False
    ) -> dict:
        # Same fetch/CORS shape as the listing XHR, but X-Xsrf-Token is re-minted per request from
        # the Xsrf-Token cookie (the SPA signs "{cookie}:{now_ms}" on every call) and the
        # announcement token, when present, authorizes the detail endpoints.
        headers = self._api_headers({})
        headers["x-xsrf-token"] = crypto.xsrf_token(tokens["xsrf-cookie"])
        if announcement_token:
            headers["x-announcement-token"] = announcement_token
        if post:
            # generateToken is a CORS POST; the browser sends an explicit Origin.
            headers["origin"] = self.ORIGIN
        return headers

    def _detail_request(
        self,
        url: str,
        callback,
        tokens: dict,
        meta_extra: dict,
        announcement_token: str | None = None,
        method: str = "GET",
        body: str | None = None,
        priority: int = 0,
    ) -> scrapy.Request:
        # curl_cffi (impersonate) request on the shared "cf" jar, mirroring _listing_request.
        # dont_cache: generateToken is single-use POST; the detail GETs ride the same flag so a
        # stale cached body can never stand in for a live, token-bound fetch.
        return scrapy.Request(
            url,
            method=method,
            body=body,
            callback=callback,
            headers=self._detail_headers(
                tokens, announcement_token=announcement_token, post=method == "POST"
            ),
            priority=priority,
            dont_filter=True,
            meta={
                "impersonate": IMPERSONATE,
                "impersonate_args": {"default_headers": False},
                "referrer_policy": "no-referrer",
                "cookiejar": "cf",
                "dont_cache": True,
                "api_tokens": tokens,
                **meta_extra,
            },
        )

    def _generate_token_request(self, row: dict, tokens: dict) -> scrapy.Request:
        project_id = str(row["projectId"])
        body = json.dumps({"key": crypto.generate_token_key(project_id)})
        logger.info("detail 1/5 generateToken queued", project_id=project_id)
        return self._detail_request(
            f"{self.DETAIL_ENDPOINT}/generateToken",
            self.parse_token,
            tokens,
            method="POST",
            body=body,
            priority=self.DETAIL_TOKEN_PRIORITY,
            meta_extra={"project_id": project_id, "detail": {"listing": row}},
        )

    def _detail_json(self, response):
        # Detail endpoints answer {"response": {"responseCode": "0", ...}, "data": ...}.
        # Treat anything but a 200 with responseCode "0" as a failed hop.
        if response.status != 200:
            return None
        try:
            payload = response.json()
        except Exception:
            return None
        if (payload.get("response") or {}).get("responseCode") != "0":
            return None
        return payload.get("data")

    def parse_token(self, response):
        project_id = response.meta["project_id"]
        token = self._detail_json(response)
        if not token:
            logger.warning(
                "generateToken failed; skipping detail",
                status=response.status,
                project_id=project_id,
            )
            return
        logger.info(
            "detail 1/5 generateToken done", project_id=project_id, status=response.status
        )
        meta = response.meta["detail"]
        logger.info("detail 2/5 getProjectDetail queued", project_id=project_id)
        yield self._detail_request(
            f"{self.DETAIL_ENDPOINT}/getProjectDetail?projectId={project_id}",
            self.parse_project_detail,
            response.meta["api_tokens"],
            announcement_token=token,
            priority=self.DETAIL_PROJECT_PRIORITY,
            meta_extra={
                "project_id": project_id,
                "announcement_token": token,
                "detail": meta,
            },
        )

    def parse_project_detail(self, response):
        project_id = response.meta["project_id"]
        token = response.meta["announcement_token"]
        detail = response.meta["detail"]
        detail["getProjectDetail"] = response.text
        logger.info(
            "detail 2/5 getProjectDetail done",
            project_id=project_id,
            status=response.status,
            bytes=len(response.body),
        )
        logger.info("detail 3/5 getProcurementDetail queued", project_id=project_id)
        yield self._detail_request(
            f"{self.DETAIL_ENDPOINT}/getProcurementDetail?projectId={project_id}",
            self.parse_procurement_detail,
            response.meta["api_tokens"],
            announcement_token=token,
            priority=self.DETAIL_PROCUREMENT_PRIORITY,
            meta_extra={
                "project_id": project_id,
                "announcement_token": token,
                # methodId/announceType drive the greenBook call; pull them off this body.
                "project_data": self._detail_json(response) or {},
                "detail": detail,
            },
        )

    def parse_procurement_detail(self, response):
        project_id = response.meta["project_id"]
        token = response.meta["announcement_token"]
        detail = response.meta["detail"]
        detail["getProcurementDetail"] = response.text
        project_data = response.meta["project_data"]
        procurement_data = self._detail_json(response) or {}

        method_id = project_data.get("methodId") or procurement_data.get("methodId")
        announce_type = project_data.get("announceType", "")
        logger.info(
            "detail 3/5 getProcurementDetail done",
            project_id=project_id,
            status=response.status,
            method_id=method_id,
            dept_id=procurement_data.get("deptId"),
        )
        params = urlencode(
            {
                "mode": "LINK",
                "methodId": method_id or "",
                "tempProjectId": project_id,
                "pageAnnounceType": announce_type,
            }
        )
        logger.info("detail 4/5 greenBook queued", project_id=project_id)
        yield self._detail_request(
            f"{self.DETAIL_ENDPOINT}/greenBook?{params}",
            self.parse_green_book,
            response.meta["api_tokens"],
            announcement_token=token,
            priority=self.DETAIL_GREENBOOK_PRIORITY,
            meta_extra={
                "project_id": project_id,
                "announcement_token": token,
                # deptId/deptSubId drive infoDeptSub.
                "dept_id": procurement_data.get("deptId"),
                "dept_sub_id": procurement_data.get("deptSubId"),
                "detail": detail,
            },
        )

    def parse_green_book(self, response):
        project_id = response.meta["project_id"]
        detail = response.meta["detail"]
        detail["greenBook"] = response.text
        dept_id = response.meta["dept_id"]
        dept_sub_id = response.meta["dept_sub_id"]
        logger.info(
            "detail 4/5 greenBook done",
            project_id=project_id,
            status=response.status,
            bytes=len(response.body),
        )

        # infoDeptSub lives on a different service and needs no announcement token — just the
        # session cookies + a signed X-Xsrf-Token. Skip it if the procurement body had no dept ids.
        if dept_id and dept_sub_id:
            params = urlencode({"deptId": dept_id, "deptSubId": dept_sub_id})
            logger.info("detail 5/5 infoDeptSub queued", project_id=project_id)
            yield self._detail_request(
                f"{self.RDB_DEPT_URL}?{params}",
                self.parse_dept_sub,
                response.meta["api_tokens"],
                priority=self.DETAIL_DEPTSUB_PRIORITY,
                meta_extra={"project_id": project_id, "detail": detail},
            )
        else:
            logger.info(
                "detail done (no dept ids; skipping infoDeptSub), emitting item",
                project_id=project_id,
            )
            yield self._build_detail_item(project_id, detail, response)

    def parse_dept_sub(self, response):
        project_id = response.meta["project_id"]
        detail = response.meta["detail"]
        detail["infoDeptSub"] = response.text
        logger.info(
            "detail 5/5 infoDeptSub done, emitting item",
            project_id=project_id,
            status=response.status,
        )
        yield self._build_detail_item(project_id, detail, response)

    def _build_detail_item(self, project_id: str, detail: dict, response) -> BaseItem:
        # One record per project. getProjectDetail is the "main" body (-> content); the listing
        # row and the other endpoints ride along in extra so the record stays whole.
        item = BaseItem()
        item["request_url"] = (
            f"{self.ORIGIN}/egp-agpc01-web/announcement/procurement/"
            f"{crypto.route_param(project_id)}"
        )
        item["response_url"] = response.url
        item["domain"] = "gprocurement.go.th"
        item["status"] = response.status
        item["scraped_at"] = datetime.now(UTC).isoformat()
        item["content"] = detail.get("getProjectDetail", "")
        item["extra"] = {
            "project_id": project_id,
            "listing": detail.get("listing"),
            "getProcurementDetail": detail.get("getProcurementDetail"),
            "greenBook": detail.get("greenBook"),
            "infoDeptSub": detail.get("infoDeptSub"),
        }
        return item
