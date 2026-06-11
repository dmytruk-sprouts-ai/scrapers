import json
import re
import subprocess
import threading

import scrapy.signals
import undetected_chromedriver as uc
import urllib3
from scrapy.http import HtmlResponse
from scrapy.utils.defer import deferred_to_future
from structlog import get_logger
from twisted.internet import threads
from .wait import (
    log_challenge_response,
    settle_page,
    settle_page_methods,
    wait_until_settled,
)
logger = get_logger(__name__)


def _detect_chrome_major_version():
    """Return the installed Chrome major version (e.g. ``148``), or ``None`` if undetectable.

    Chrome freezes the minor/build/patch parts of its UA string to ``.0.0.0`` for privacy, so
    only the major version is meaningful for building a realistic UA. Returning ``None`` lets
    undetected-chromedriver fall back to its own auto-detection.
    """
    try:
        binary = uc.find_chrome_executable()
        if not binary:
            logger.warning("could not locate Chrome executable")
            return None
        # e.g. "Google Chrome 148.0.7778.178"
        output = subprocess.check_output([binary, "--version"], text=True)
        match = re.search(r"(\d+)\.\d+\.\d+\.\d+", output)
        if match:
            return int(match.group(1))
        logger.warning(f"could not parse Chrome version from {output!r}")
    except Exception:
        logger.warning("could not detect Chrome version; using undetected-chromedriver default")
    return None

def _capture_settle(driver, ready_js, meta) -> None:
    """Run the Selenium waiter and stash its outcome on the request meta (response.meta is the same
    dict), since the undetected-chromedriver middleware discards webdriver_actions return values."""
    meta["settle_status"] = wait_until_settled(driver, ready_js=ready_js)


class UndetectedChromedriverMiddleware:
    # https://github.com/ultrafunkamsterdam/undetected-chromedriver
    """
    Most spiders need nothing here. To use a heavier download path, a spider opts in via its own
    ``custom_settings`` rather than editing this module:

    example settings:
        custom_settings = {
            "DOWNLOADER_MIDDLEWARES": {
                "scraper.middlewares.UndetectedChromedriverMiddleware": 1000,
            },
        }

    """

    def __init__(self):
        urllib3.PoolManager(maxsize=50)

        # One driver is shared across all requests, but Scrapy runs each request's render on its
        # own thread (deferToThread) and Selenium WebDriver is not thread-safe — concurrent
        # get()/CDP/get_log() calls on one session interleave and throw. Serialize them.
        self._driver_lock = threading.Lock()

        # Match the UA and the chromedriver to whatever Chrome is actually installed, so a Chrome
        # auto-update never desyncs them. ``None`` falls back to undetected-chromedriver's own
        # auto-detection.
        chrome_major = _detect_chrome_major_version()
        ua_version = f"{chrome_major}.0.0.0" if chrome_major else "148.0.0.0"

        # Configure headless options correctly for modern Chrome versions
        self.options = uc.ChromeOptions()
        self.options.add_argument("--disable-dev-shm-usage")
        # Old headless Chrome advertises "HeadlessChrome/<ver>" in the UA (and in
        # navigator.userAgent), which sannysoft flags (User Agent (Old) / HEADCHR_UA). Force a
        # normal Chrome UA matching the installed major version.
        self.options.add_argument(
            f"--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            f"(KHTML, like Gecko) Chrome/{ua_version} Safari/537.36"
        )
        self.options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        # Initialize the driver once to reuse it across requests
        # Run headful on the available X display (DISPLAY): headless Chrome falls back to the
        # SwiftShader software renderer, whose WebGL renderer string ("SwiftShader") sannysoft
        # flags. Headful uses the real GPU and reports a genuine renderer.
        self.driver = uc.Chrome(
            options=self.options, headless=False, version_main=chrome_major, keep_alive=False
        )

        browser_version = self.driver.capabilities.get("browserVersion")  # e.g., '120.0.6099.109'
        driver_version = (
            self.driver.capabilities.get("chrome", {}).get("chromedriverVersion", "").split(" ")[0]
        )

        logger.info(f"Google Chrome Version: {browser_version}")
        logger.info(f"ChromeDriver Version: {driver_version}")

    @classmethod
    def from_crawler(cls, crawler):
        middleware = cls()
        crawler.signals.connect(middleware.spider_closed, signal=scrapy.signals.spider_closed)
        return middleware

    async def process_request(self, request):
        if not request.meta.get("use_uc", True):
            return None
        
        ready_js = request.meta.get('ready_js', None)
        meta = request.meta
        request.meta["webdriver_actions"] = [lambda d, rj=ready_js, m=meta: _capture_settle(d, rj, m)]

        # Offload the blocking Selenium code to a separate thread AND cast to a native future
        response_data = await deferred_to_future(
            threads.deferToThread(self._render_with_uc, request)
        )
        return response_data

    def _render_with_uc(self, request):
        """Runs inside a background thread to prevent blocking Scrapy.

        The whole body holds ``_driver_lock`` because the single driver is shared across the
        thread pool and Selenium is not thread-safe; concurrent requests render one at a time.
        """

        with self._driver_lock:
            self.driver.execute_cdp_cmd("Network.enable", {})
            self.driver.get(request.url)

            for action in request.meta.get("webdriver_actions", []):
                action(self.driver)

            body = self.driver.page_source
            current_url = self.driver.current_url

            status = 200
            headers = {}

            # Fetch precise network data using Chrome DevTools Protocol (CDP)
            # Alternatively, if using selenium-wire: self.driver.requests
            try:
                # Fetch performance logs to extract real status and headers
                logs = self.driver.get_log("performance")
                for entry in reversed(logs):
                    message = json.loads(entry["message"])["message"]

                    if message["method"] == "Network.responseReceived":
                        response_data = message["params"]["response"]
                        # Verify this log matches our final destination URL
                        if response_data["url"] == current_url:
                            status = response_data["status"]
                            headers = response_data["headers"]
                            break
            except Exception:
                logger.error("could not parse status_code and headers")

        headers.pop("Content-Encoding", None)
        headers.pop("content-encoding", None)
        headers.pop("Content-Length", None)
        headers.pop("content-length", None)

        return HtmlResponse(
            url=current_url,
            status=status,
            headers=headers,
            body=body,
            encoding="utf-8",
            request=request,
        )

    def spider_closed(self):
        # Clean up driver process when spider finishes
        if self.driver:
            self.driver.quit()
