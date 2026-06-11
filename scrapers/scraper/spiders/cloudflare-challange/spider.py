from typing import Any
from datetime import UTC, datetime
import json
import scrapy
from scraper.items import BaseItem
from scraper.spiders.base import BaseSpider
from scraper.browser_profile import navigation_headers, IMPERSONATE
import collections
from scrapy_playwright.page import PageMethod
import structlog
from .settle_cloudflare_page import wait_for_load_cloudflare_default
from scraper.proxies import pick_proxy

logger = structlog.get_logger(__name__)


async def handler_request(event: str, r, hc: dict[str, Any]):
    hc[event].append(
        {
            "r": r,
            "method": r.method,
            "url": r.url,
            "headers": r.headers
        }
    )


async def handler_response(event: str, r, hc: dict[str, Any]):               # 3xx redirects / failed responses have no body
    t = r.request.timing
    hc[event].append(
        {
            "r": r,
            "status": r.status,
            "url": r.url,
            "headers": r.headers,
            "timing": t,
        }
    )


async def populate_body(response):               # 3xx redirects / failed responses have no body
    # playwright page musdt be present
    page = response.meta["playwright_page"]

    for entry in response.meta['handlers_context'].get("response", []):
        try:
            entry["body"] = await entry["r"].body()
            entry["cookies"] = entry["r"].get('cookiejar')
        except Exception:
            entry["body"] = None
            entry["cookies"] = None

    await page.close()

 

class CloudflareChallangeTestSpider(scrapy.Spider):
    name = "cloudflare-challange"

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
                "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
                'HTTPERROR_ALLOW_ALL': True,
                "ROBOTSTXT_OBEY": False,
                "RETRY_ENABLED": False,
                **playwright,
                **handlers
                
            },
            priority="spider",
        )
    
    async def start(self):
        # must be initialized here, to be able to mutate in handlers
        hc = collections.defaultdict(list)
        # One sticky-session proxy for the entire chain. Cloudflare binds cf_clearance to the
        # egress IP that solved the challenge, so the curl_cffi replay must exit from the same
        # IP as this Playwright run — we thread this single Proxy through every leg.
        proxy = pick_proxy()
        self.logger.info("using proxy session %s", proxy.username)
        meta = {
                "playwright": True,
                "playwright_include_page": True, # needed to await page events
                # Per-crawl context bound to the chosen proxy. A dedicated (non-"default")
                # context name forces scrapy-playwright to build a fresh context with these
                # kwargs instead of reusing the proxy-less startup context.
                "playwright_context": f"cf-{proxy.username}",
                "playwright_context_kwargs": {
                    "no_viewport": True,
                    "locale": "en-US",
                    "proxy": proxy.playwright,
                },
                "playwright_page_methods": [
                    PageMethod(
                        wait_for_load_cloudflare_default
                    ),
                ],
                "playwright_page_event_handlers":{
                    "requestfinished": lambda request: handler_request("requestfinished", request, hc),
                    "requestfailed": lambda request: handler_request("requestfailed", request, hc),
                    "request": lambda request: handler_request("request", request, hc),
                    "response": lambda response: handler_response("response", response, hc),
                },
                "handlers_context": hc,
                # Carried forward so the curl_cffi legs reuse the exact same egress IP.
                "cf_proxy": proxy,
            }
        yield scrapy.Request(
            "https://www.scrapingcourse.com/cloudflare-challenge",
            callback=self.parse_playwright,
            meta=meta
        )


    async def parse_playwright(self, response):
        # Playwright drove the real browser through Cloudflare's JS challenge. Wait for the
        # success marker so cf_clearance has actually been issued, then harvest the context
        # jar (cf_clearance, __cf_bm, …) to hand off to curl_cffi.
        assert response.status == 200
        page = response.meta["playwright_page"]
        try:
            cookies = await page.context.cookies()
        finally:
            await page.close()


        # The whole point: replay the SAME page with curl_cffi using these cookies.
        yield self.retry_with_curl_cffi(response, cookies)

    def retry_with_curl_cffi(self, response, cookies):
        # Replay the same URL through curl_cffi, carrying the cf_clearance cookie Playwright
        # earned. If the impersonated TLS/HTTP2 + headers match the identity Cloudflare bound
        # the clearance to, the challenge does not re-trigger and we get the page directly.
        # Playwright's cookies seed a shared "cf" jar; CookiesMiddleware sends them. Pass just
        # name->value (the full Playwright dicts carry a float `expires` curl_cffi rejects).
        cookie_dict = {c["name"]: c["value"] for c in cookies}
        proxy = response.meta["cf_proxy"]
        return self._curl_cffi_request(response.url, curl_pass=1, proxy=proxy, cookies=cookie_dict)

    def _curl_cffi_request(self, url, curl_pass, proxy, cookies=None):
        # curl_cffi (impersonate) request on the shared "cf" cookiejar. `cookies` seeds the jar
        # on the first hop; later hops pass None and let CookiesMiddleware replay the jar — which
        # by then holds whatever the server rotated in via Set-Cookie.
        return scrapy.Request(
            url,
            callback=self.verify_access,
            headers=navigation_headers(),
            cookies=cookies,
            meta={
                "impersonate": IMPERSONATE,
                "impersonate_args": {"default_headers": False},
                # Same egress IP Playwright used to earn cf_clearance — Cloudflare bound the
                # clearance to it, so curl_cffi must exit there too or the challenge re-triggers.
                # HttpProxyMiddleware splits the credentials out into Proxy-Authorization, which
                # scrapy_impersonate then re-applies to curl_cffi.
                "proxy": proxy.url,
                "cf_proxy": proxy,
                # Stop RefererMiddleware adding a Referer the real navigation lacked.
                "referrer_policy": "no-referrer",
                # One jar for the whole curl_cffi chain; the middleware owns send + Set-Cookie.
                "cookiejar": "cf",
                "curl_pass": curl_pass,
            },
            # Same URL already fetched — bypass the dupefilter.
            dont_filter=True,
        )

    def verify_access(self, response):
        curl_pass = response.meta.get("curl_pass", 1)
        title = (response.css("h2#challenge-title::text").get() or "").strip()
        bypassed = "bypassed the Cloudflare challenge" in title

        self.logger.info(
            "curl_cffi replay (pass %d): status=%s access_granted=%s title=%r",
            curl_pass,
            response.status,
            bypassed,
            title,
        )

        # One more curl_cffi load reusing the same jar — no Playwright in the loop. Its cookies
        # now include the server's Set-Cookie rotations, confirming access is self-sustaining.
        # Same proxy again so the egress IP stays pinned across the whole curl_cffi chain.
        if curl_pass == 1:
            yield self._curl_cffi_request(response.url, curl_pass=2, proxy=response.meta["cf_proxy"])
