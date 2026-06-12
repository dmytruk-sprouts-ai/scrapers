"""Shared item definition.

Every spider yields :class:`BaseItem` directly: RAW HTML, with NO field parsing. Spiders do not
subclass this or add fields — they only reach the right pages and store their HTML.

Each item is one logical RECORD. When an item's information is split across pages (e.g. the listing
page carries data the detail page lacks, or extra requests are needed to complete it), keep ALL of
it in the same record: the main page's HTML in ``content`` and everything else in ``extra``.
"""

import json

import scrapy


class BaseItem(scrapy.Item):
    """One logical record, stored as raw HTML (no field parsing)."""

    # URL we requested.
    request_url = scrapy.Field()
    # Final URL after redirects.
    response_url = scrapy.Field()
    # Site domain.
    domain = scrapy.Field()
    # HTTP status code of the fetched main page.
    status = scrapy.Field()
    # ISO-8601 UTC timestamp.
    scraped_at = scrapy.Field()
    # Raw HTML of the record's main page.
    content = scrapy.Field()
    # Additional content not present on the main page (e.g. from the listing page or extra
    # requests), as a dict or HTML. Keeps a record whole when its data is split across pages.
    extra = scrapy.Field()

    def __repr__(self):
        # Customize exactly which fields show up in the logs. Only the gprocurement spider's
        # `content` is JSON shaped like {"data": {"projectId": ...}}; every other spider stores
        # raw text/HTML/CSV, so guard the lookup and fall back to the default repr rather than
        # raising inside Scrapy's item logger.
        try:
            return json.dumps(
                {"projectID": json.loads(self["content"])["data"]["projectId"]}
            )
        except (KeyError, TypeError, ValueError):
            return super().__repr__()
