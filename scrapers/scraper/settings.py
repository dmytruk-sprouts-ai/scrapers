"""Shared base settings for every spider in this project.

These apply to ALL spiders. Per-spider overrides belong in the spider's ``custom_settings``
dict (e.g. enabling the scrapy-playwright download handler), NOT here.
"""

BOT_NAME = "scraper"

SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

# Be a good citizen by default.
ROBOTSTXT_OBEY = True
USER_AGENT = ""

# Gentle, self-tuning request rate.
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 10.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
CONCURRENT_REQUESTS = 8

RETRY_ENABLED = True
RETRY_TIMES = 2

# Shared pipelines applied to every spider. Add reusable pipelines here; keep spider-specific
# ones in the spider's custom_settings.
ITEM_PIPELINES = {
    "scraper.pipelines.ValidationPipeline": 300,
}

FEED_EXPORT_ENCODING = "utf-8"
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"

# asyncio reactor — required by scrapy-playwright and harmless for plain/curl_cffi spiders, so
# playwright spiders only need to add the DOWNLOAD_HANDLERS in their custom_settings.
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# LOG_LEVEL = "INFO"
LOG_LEVEL = "DEBUG"
LOGSTATS_INTERVAL = 3
# Colored logs via Rich (see scraper.logconf). LOG_ENABLED=False makes Scrapy install a no-op
# handler instead of its own plain StreamHandler, so the Rich handler owns the root logger alone.
from scraper.logconf import install_rich_logging  # noqa: E402

install_rich_logging(LOG_LEVEL)
LOG_ENABLED = False
