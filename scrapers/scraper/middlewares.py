"""Shared downloader/spider middlewares.

Most spiders need nothing here. To use a heavier download path, a spider opts in via its own
``custom_settings`` rather than editing this module:

  * curl_cffi (TLS/JA3 impersonation) — scrapy-impersonate::

        custom_settings = {
            "DOWNLOAD_HANDLERS": {
                "http": "scrapy_impersonate.ImpersonateDownloadHandler",
                "https": "scrapy_impersonate.ImpersonateDownloadHandler",
            },
        }
        # then set request.meta["impersonate"] = "chrome" in the spider.

  * playwright (JS rendering) — scrapy-playwright::

        custom_settings = {
            "DOWNLOAD_HANDLERS": {
                "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            },
        }
        # then set request.meta["playwright"] = True in the spider.

Add genuinely shared, reusable middlewares below.
"""
