# handlers.py
from twisted.internet.defer import DeferredList, maybeDeferred
from scrapy_playwright.handler import ScrapyPlaywrightDownloadHandler
from scrapy_impersonate import ImpersonateDownloadHandler
from .playwright_fixed import PlaywrightFixedDownloadHandler

class HybridDownloadHandler:
    lazy = False

    def __init__(self, crawler):
        self._playwright = PlaywrightFixedDownloadHandler.from_crawler(crawler)
        self._impersonate = ImpersonateDownloadHandler.from_crawler(crawler)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    async def download_request(self, request):          # no spider
        if request.meta.get("playwright"):
            return await self._playwright.download_request(request)
        if request.meta.get("impersonate"):
            return await self._impersonate.download_request(request)
        raise NotImplementedError(
            f"No download handler meta set for {request.url!r}"
        )

    async def close(self):                              # no spider
        await self._playwright.close()
        await self._impersonate.close()