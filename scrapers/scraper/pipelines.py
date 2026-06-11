"""Shared item pipelines applied to every spider (see settings.ITEM_PIPELINES)."""

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem


class ValidationPipeline:
    """Drop records we failed to capture.

    Since spiders only store raw HTML (no field parsing), the single requirement is that a record
    carries a non-empty ``content`` body. ``extra`` is optional.
    """

    def process_item(self, item):
        adapter = ItemAdapter(item)
        if not adapter.get("content"):
            raise DropItem("missing raw content html")
        return item
