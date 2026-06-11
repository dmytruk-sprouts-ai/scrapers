from __future__ import annotations

from email.utils import formatdate
from typing import TYPE_CHECKING

from twisted.internet.error import ConnectError, ConnectionDone, ConnectionLost

from scrapy import signals
from scrapy.exceptions import (
    DownloadConnectionRefusedError,
    DownloadFailedError,
    DownloadTimeoutError,
    IgnoreRequest,
    NotConfigured,
)
import copy
from scrapy.utils.project import data_path
from scrapy.utils.decorators import _warn_spider_arg
from scrapy.utils.misc import load_object
from scrapy.downloadermiddlewares.httpcache import HttpCacheMiddleware
if TYPE_CHECKING:
    # typing.Self requires Python 3.11
    from typing_extensions import Self

    from scrapy.crawler import Crawler
    from scrapy.http.request import Request
    from scrapy.http.response import Response
    from scrapy.settings import Settings
    from scrapy.spiders import Spider
    from scrapy.statscollectors import StatsCollector




class MigrateCacheMiddleware(HttpCacheMiddleware):

    def __init__(self, settings: Settings, stats: StatsCollector) -> None:
        super().__init__(settings, stats)
        dest_settings = copy.copy(settings)
        dest_settings.frozen = False # Unfreeze the copy to allow edits
        dest_settings["HTTPCACHE_DIR"] = settings["HTTPCACHE_DIR"] + '/migrated'
        
        self.destination_storage = load_object(settings["HTTPCACHE_MIGRATE_DESTINATION_STORAGE"])(settings)

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        assert crawler.stats
        o = cls(crawler.settings, crawler.stats)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        o.crawler = crawler
        return o

    def spider_opened(self, spider: Spider) -> None:
        super().spider_opened(spider)
        self.destination_storage.open_spider(spider)

    def spider_closed(self, spider: Spider) -> None:
        super().spider_closed(spider)
        self.destination_storage.open_spider(spider)

    def process_response(
        self, request: Request, response: Response
    ) -> Request | Response:
        response.flags = [f for f in response.flags if f != 'cached']
        request.meta.pop("cached_response", None)
        return super().process_response(request, response)

    def _cache_response(self, response: Response, request: Request) -> None:
        if self.policy.should_cache_response(response, request):
            self.stats.inc_value("httpcache/store")
            self.destination_storage.store_response(self.crawler.spider, request, response)
        else:
            self.stats.inc_value("httpcache/uncacheable")