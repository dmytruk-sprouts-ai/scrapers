"""Spider for books.toscrape.com.

Scrapes all 1 000 books across 50 listing pages. For each book it fetches the
detail page (stored as ``content``) and preserves the raw ``<article
class="product_pod">`` block from the listing page in ``extra`` — this block
carries the thumbnail URL and compact availability label that are absent from
the detail page.
"""

from scraper.items import BaseItem
from scraper.spiders.base import BaseSpider


class BooksToScrapeSpider(BaseSpider):
    """Crawls https://books.toscrape.com and yields one BaseItem per book."""

    name = "books_toscrape_com"
    start_urls = ["https://books.toscrape.com/"]

    custom_settings = {
        # Plain HTTP is sufficient — no anti-bot measures on this site.
        "ROBOTSTXT_OBEY": False,
        "AUTOTHROTTLE_TARGET_CONCURRENCY": 2.0,
        # cache
        "HTTPCACHE_ENABLED": True,
        "HTTPCACHE_IGNORE_HTTP_CODES": [403, 500, 502, 503],
        "HTTPCACHE_EXPIRATION_SECS": 0,
        "HTTPCACHE_ZSTD_DICT_SAMPLE_COUNT": 100,
        "HTTPCACHE_STORAGE": "scraper.cache_storages.zstd.ZstdSqliteCacheStorage",
        
        # cache migrate to another storage settings
        "DOWNLOADER_MIDDLEWARES": {
            "scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware": None, # disable default
            "scraper.middlewares.migrate_cache.MigrateCacheMiddleware": 900
        },
        "HTTPCACHE_MIGRATE_DESTINATION_STORAGE": "scraper.cache_storages.zstd.ZstdSqliteCacheStorage",
    
    }

    # ------------------------------------------------------------------
    # Listing page
    # ------------------------------------------------------------------

    def parse(self, response):
        """Parse a catalogue listing page.

        Yields one Request per book (→ ``parse_detail``) and follows the
        ``li.next > a`` pagination link when present.
        """
        for article in response.css("article.product_pod"):
            # Relative href inside the article, e.g. "catalogue/book-slug/index.html"
            relative_href = article.css("h3 > a::attr(href)").get("")
            detail_url = response.urljoin(relative_href)

            yield response.follow(
                detail_url,
                callback=self.parse_detail,
                meta={"listing_article": article.get()},
            )

        # Pagination: follow li.next > a if present.
        next_href = response.css("li.next > a::attr(href)").get()
        if next_href:
            yield response.follow(next_href, callback=self.parse)

    # ------------------------------------------------------------------
    # Detail page
    # ------------------------------------------------------------------

    def parse_detail(self, response):
        """Build one BaseItem from the detail page + listing article block."""
        item = BaseItem()
        item["content"] = response.text
        item["extra"] = {"listing_article": response.meta.get("listing_article", "")}
        item["request_url"] = response.request.url
        item["response_url"] = response.url
        item["domain"] = response.url.split("/")[2]
        item["status"] = response.status
        item["scraped_at"] = self.utcnow_iso()
        yield item
