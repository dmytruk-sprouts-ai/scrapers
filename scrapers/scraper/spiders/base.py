"""Common base class for every generated spider."""

from datetime import UTC, datetime

import scrapy

SHARED_SETTINGS = {"HTTPERROR_ALLOW_ALL": True, "TELNETCONSOLE_ENABLED": False}


class BaseSpider(scrapy.Spider):
    """Shared base for generated spiders.

    Subclasses set ``name`` (unique within the project), the start URLs/requests, and a parse
    callback that yields :class:`scraper.items.BaseItem` directly — the raw HTML of the right pages,
    NOT parsed fields. Put spider-specific config in ``custom_settings`` rather than editing the
    shared settings module.
    """

    @classmethod
    def update_settings(cls, settings):
        super().update_settings(settings)
        settings.setdict(SHARED_SETTINGS, priority="spider")

    @staticmethod
    def utcnow_iso() -> str:
        """ISO-8601 UTC timestamp for the item's ``scraped_at`` provenance field."""
        return datetime.now(UTC).isoformat()


class ScrapySpider(BaseSpider):
    @classmethod
    def update_settings(cls, settings):
        super().update_settings(settings)

class UndetectedChromedriverSpider(BaseSpider):
    _required_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            "scraper.middlewares.UndetectedChromedriverMiddleware": 1000,
        },
    }
    
    @classmethod
    def update_settings(cls, settings):
        super().update_settings(settings)
        settings.setdict(
            cls._required_settings,
            priority="spider",
        )

