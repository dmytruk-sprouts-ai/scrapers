# handlers.py
from twisted.internet.defer import DeferredList, maybeDeferred
from scrapy_playwright.handler import ScrapyPlaywrightDownloadHandler, Download, _maybe_await
from scrapy_impersonate import ImpersonateDownloadHandler
from scrapy import Spider
from typing import Optional
from scrapy.http import Request, Response
from playwright.async_api import (
    BrowserContext,
    BrowserType,
    Download as PlaywrightDownload,
    Error as PlaywrightError,
    Page,
    Playwright as AsyncPlaywright,
    PlaywrightContextManager,
    Request as PlaywrightRequest,
    Response as PlaywrightResponse,
    Route,
)
import asyncio
import logging
from functools import partial
from scrapy_playwright.page import PageMethod

logger = logging.getLogger("scrapy-playwright-fixed")

class PlaywrightFixedDownloadHandler(ScrapyPlaywrightDownloadHandler):
    # when cloudflare protected page is loaded we get 403 error, after sucessful bypassing response status code and content is not updated
    # new parameter "playwright_page_goto_methods"
    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    # **added by modifying  _apply_page_methods**
    async def _apply_page_goto_methods(self, page: Page, request: Request, spider: Spider) -> None:
        context_name = request.meta.get("playwright_context")
        # **modified**
        page_methods = request.meta.get("playwright_page_goto_methods") or ()
        # **modified**
        if isinstance(page_methods, dict):
            page_methods = page_methods.values()
        for pm in page_methods:
            if isinstance(pm, PageMethod):
                try:
                    if callable(pm.method):
                        method = partial(pm.method, page)
                    else:
                        method = getattr(page, pm.method)
                except AttributeError as ex:
                    logger.warning(
                        "Ignoring %r: could not find method",
                        pm,
                        extra={
                            "spider": spider,
                            "context_name": context_name,
                            "scrapy_request_url": request.url,
                            "scrapy_request_method": request.method,
                            "exception": ex,
                        },
                        exc_info=True,
                    )
                else:
                    pm.result = await _maybe_await(method(*pm.args, **pm.kwargs))
                    await page.wait_for_load_state(timeout=self.config.navigation_timeout)
            else:
                logger.warning(
                    "Ignoring %r: expected PageMethod, got %r",
                    pm,
                    type(pm),
                    extra={
                        "spider": spider,
                        "context_name": context_name,
                        "scrapy_request_url": request.url,
                        "scrapy_request_method": request.method,
                    },
                )
    # **added by modifying  _apply_page_methods**


    async def _get_response_and_download(
        self, request: Request, page: Page, spider: Spider
    ) -> tuple[Optional[PlaywrightResponse], Optional[Download]]:
        # **modified**
        ctx = {"response": None}
        # **modified**
        download: Download = Download()  # updated in-place in _handle_download
        download_started = asyncio.Event()
        download_ready = asyncio.Event()

        async def _handle_download(dwnld: PlaywrightDownload) -> None:
            download_started.set()
            self.stats.inc_value("playwright/download_count")
            try:
                if failure := await dwnld.failure():
                    raise RuntimeError(f"Failed to download {dwnld.url}: {failure}")
                download.body = (await dwnld.path()).read_bytes()
                download.url = dwnld.url
                download.suggested_filename = dwnld.suggested_filename
            except Exception as ex:
                download.exception = ex
            finally:
                download_ready.set()

        async def _handle_response(response: PlaywrightResponse) -> None:
            download.response_status = response.status
            download.headers = await response.all_headers()
            download_started.set()
            # **added**
            ctx["response"] = response
            # **added**

        page_goto_kwargs = request.meta.get("playwright_page_goto_kwargs") or {}
        page_goto_kwargs.pop("url", None)

        page.on("download", _handle_download)
        page.on("response", _handle_response)
        try:
            _ = await page.goto(url=request.url, **page_goto_kwargs)
            # **added**
            if request.meta.get("playwright_page_goto_methods"):
                await self._apply_page_goto_methods(page, request, spider)
                # response = await page.request.get(page.url)
            # **added**
        except PlaywrightError as err:
            if not (
                "Download is starting" in err.message
                or self.config.browser_type_name == "chromium"
                and "net::ERR_ABORTED" in err.message
            ):
                raise

            logger.debug(
                "Navigating to %s failed",
                request.url,
                extra={
                    "spider": spider,
                    "context_name": request.meta.get("playwright_context"),
                    "scrapy_request_url": request.url,
                    "scrapy_request_method": request.method,
                },
            )
            await download_started.wait()

            if download.response_status == 204:
                raise err

            logger.debug(
                "Waiting on download to finish for %s",
                request.url,
                extra={
                    "spider": spider,
                    "context_name": request.meta.get("playwright_context"),
                    "scrapy_request_url": request.url,
                    "scrapy_request_method": request.method,
                },
            )
            await download_ready.wait()
        finally:
            page.remove_listener("download", _handle_download)
            page.remove_listener("response", _handle_response)

        # **modified**
        return ctx["response"], download if download else None
        # **modified**