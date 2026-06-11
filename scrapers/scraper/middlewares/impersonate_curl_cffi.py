# from curl_cffi import BrowserType
# from curl_cffi.requests.impersonate import REAL_TARGET_MAP

# https://github.com/jxlil/scrapy-impersonate


class ImpersonateBrowserMiddleware:
    """
    Most spiders need nothing here. To use a heavier download path, a spider opts in via its own
    ``custom_settings`` rather than editing this module:

    curl_cffi (TLS/JA3 impersonation) — scrapy-impersonate::

    valid browser options are:
        - "chrome"
        - "firefox"
        - "safari"
        - "edge"
        - "tor"

        - "edge99"
        - "edge101"
        - "chrome99"
        - "chrome100"
        - "chrome101"
        - "chrome104"
        - "chrome107"
        - "chrome110"
        - "chrome116"
        - "chrome119"
        - "chrome120"
        - "chrome123"
        - "chrome124"
        - "chrome131"
        - "chrome133a"
        - "chrome136"
        - "chrome142"
        - "chrome145"
        - "chrome146"
        - "chrome99_android"
        - "chrome131_android"
        - "safari153"
        - "safari155"
        - "safari170"
        - "safari172_ios"
        - "safari180"
        - "safari180_ios"
        - "safari184"
        - "safari184_ios"
        - "safari260"
        - "safari260_ios"
        - "safari2601"
        - "firefox133"
        - "firefox135"
        - "firefox144"
        - "firefox147"
        - "tor145"

    example settings:
        custom_settings = {
            "DOWNLOAD_HANDLERS": {
                "http": "scrapy_impersonate.ImpersonateDownloadHandler",
                "https": "scrapy_impersonate.ImpersonateDownloadHandler",
            },
        }
        # then set request.meta["impersonate"] = "chrome" in the spider.
    """
