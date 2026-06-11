"""Proxy egress-IP consistency check.

Resolves the public IP twice over the *same* sticky proxy session — once through the Playwright
browser context, once through curl_cffi — and verifies they agree. This is the precondition the
cloudflare-challange spider relies on: cf_clearance is bound to the egress IP, so the browser leg
and the curl_cffi replay must share one IP. If this spider reports match=True, the handoff is
sound; if not, the proxy session isn't pinning a single exit and clearance reuse will fail.

Modeled on ``scraper.spiders.cloudflare-challange.spider``: same Hybrid handler, same per-crawl
proxied Playwright context, same single :class:`Proxy` threaded into the curl_cffi leg.
"""

from datetime import UTC, datetime
import json

import scrapy

from scraper.items import BaseItem
from scraper.browser_profile import navigation_headers, IMPERSONATE
from scraper.proxies import pick_proxy

URL = "https://ipinfo.io/json"


class IpinfoConsistencySpider(scrapy.Spider):
    name = "ipinfo_io"

    @classmethod
    def update_settings(cls, settings):
        playwright = {
            "PLAYWRIGHT_BROWSER_TYPE": "chromium",
            "PLAYWRIGHT_LAUNCH_OPTIONS": {
                "headless": False,
                "channel": "chrome",
                "args": ["--disable-blink-features=AutomationControlled"],
            },
            # Per-crawl context is built dynamically from playwright_context_kwargs (with the
            # proxy) in start(); no proxy-less startup context to fall back to.
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
                "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
                "HTTPERROR_ALLOW_ALL": True,
                "ROBOTSTXT_OBEY": False,
                "RETRY_ENABLED": False,
                **playwright,
                **handlers,
            },
            priority="spider",
        )

    async def start(self):
        # One sticky-session proxy for both legs — the whole point is to confirm the egress IP
        # is identical across them, so they must use the same credential (same sid => same exit).
        proxy = pick_proxy()
        self.logger.info("using proxy session %s", proxy.username)
        yield scrapy.Request(
            URL,
            callback=self.parse_playwright,
            meta={
                "playwright": True,
                "playwright_include_page": True,  # needed to evaluate JS in the page
                "playwright_context": f"ipinfo-{proxy.username}",
                "playwright_context_kwargs": {
                    "no_viewport": True,
                    "locale": "en-US",
                    "proxy": proxy.playwright,
                },
                # Threaded forward so the curl_cffi leg reuses the exact same egress IP.
                "proxy_choice": proxy,
            },
            dont_filter=True,
        )

    async def parse_playwright(self, response):
        # The page already navigated to ipinfo.io/json, but Chromium wraps JSON in its viewer,
        # so read the raw body via an in-page fetch (same context => same proxy => same IP)
        # rather than scraping the rendered HTML.
        page = response.meta["playwright_page"]
        proxy = response.meta["proxy_choice"]
        try:
            raw = await page.evaluate(
                "async () => await (await fetch('https://ipinfo.io/json')).text()"
            )
        finally:
            await page.close()

        playwright_ip = json.loads(raw).get("ip")
        self.logger.info("playwright resolved ip=%s", playwright_ip)

        # Now resolve the IP again over curl_cffi on the SAME proxy and compare in verify().
        yield self._curl_cffi_request(playwright_ip, proxy)

    def _curl_cffi_request(self, playwright_ip, proxy):
        return scrapy.Request(
            URL,
            callback=self.verify,
            headers=navigation_headers(),
            meta={
                "impersonate": IMPERSONATE,
                "impersonate_args": {"default_headers": False},
                # Same egress IP the browser used. HttpProxyMiddleware splits the credentials
                # into Proxy-Authorization, which scrapy_impersonate re-applies to curl_cffi.
                "proxy": proxy.url,
                "referrer_policy": "no-referrer",
                "playwright_ip": playwright_ip,
            },
            dont_filter=True,
        )

    def verify(self, response):
        playwright_ip = response.meta["playwright_ip"]
        # curl_cffi returns the JSON endpoint verbatim — no browser viewer to strip.
        curl_ip = json.loads(response.text).get("ip")
        match = playwright_ip == curl_ip

        self.logger.info(
            "ip check: playwright=%s curl_cffi=%s match=%s",
            playwright_ip,
            curl_ip,
            match,
        )
        if not match:
            self.logger.error(
                "egress IP mismatch — proxy session is not pinning a single exit IP; "
                "cf_clearance reuse would fail"
            )

        yield BaseItem(
            request_url=URL,
            response_url=response.url,
            domain="ipinfo.io",
            status=response.status,
            scraped_at=datetime.now(UTC).isoformat(),
            content=response.text,
            extra={
                "playwright_ip": playwright_ip,
                "curl_cffi_ip": curl_ip,
                "match": match,
            },
        )
