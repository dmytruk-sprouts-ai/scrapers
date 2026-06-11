from scraper.playwright_engine import ENGINE, install_engine

# Swap in the patchright backend (when SCRAPER_PW_ENGINE=patchright) before scrapy-playwright's
# handler is imported at crawl time. Must precede any scrapy_playwright.handler import.
install_engine()
from typing import Any
import collections
import dataclasses
import json
import shutil  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402
from urllib.parse import ParseResult, urlparse  # noqa: E402
from urllib.parse import ParseResult, unquote, urlparse  # noqa: E402
import scrapy  # noqa: E402
import structlog  # noqa: E402
from scrapy.crawler import CrawlerProcess  # noqa: E402
from scrapy.utils.project import get_project_settings  # noqa: E402
from scrapy_playwright.page import PageMethod  # noqa: E402
from twisted.internet import defer  # noqa: E402
from scrapy_playwright.page import PageMethod
from scraper.spiders._capture_har.analyze_har import analyze_all_outputs  # noqa: E402


logger = structlog.get_logger(__name__)


def normalized_domain(url: str | ParseResult):
    match url:
        case str():
            parsed_url = urlparse(url)
        case ParseResult():
            parsed_url = url
    assert parsed_url.hostname is not None
    hostname = parsed_url.hostname
    hostname = hostname if not hostname.startswith("www.") else hostname[4:]
    return hostname


def engine_outputs_dir(base_dir: Path) -> Path:
    """``<base_dir>/outputs/<engine>/`` — the subtree owned by the current run's backend, so a
    patchright run and a playwright run keep their captures side by side instead of overwriting
    each other. ``base_dir`` is the calling spider's folder, so each spider owns its own captures."""
    return base_dir / "outputs" / ENGINE


def output_dir(base_dir: Path, url: str) -> Path:
    target_dir = engine_outputs_dir(base_dir) / normalized_domain(url)
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir


@dataclasses.dataclass
class DerivedPathInfo:
    hostname: str
    normalized_path: str
    status: int
    file_name: str
    extension: str
    extensions: list[str]
    start_time: float | None

    def default_str(self):
        return f"{self.hostname}{self.normalized_path[:100]}-{self.status}"

def derive_path_info(response, timings: dict[str, float] | None = None) -> DerivedPathInfo:
    parsed_url = urlparse(response.url)
    decoded_path = unquote(parsed_url.path).replace("/", "_").strip("_")
    hostname = normalized_domain(parsed_url)
    decoded_path = f"-{decoded_path}" if decoded_path else ''

    start_time = timings['startTime'] if timings else None
    return DerivedPathInfo(
        hostname=hostname,
        normalized_path=decoded_path,
        start_time=start_time,
        file_name=Path(parsed_url.path).name,
        extension=Path(parsed_url.path).suffix,
        extensions=Path(parsed_url.path).suffixes,
        status=response.status
    )




async def handler_request(event: str, r, hc: dict[str, Any]):
    hc[event].append(
        {
            "r": r,
            "method": r.method,
            "url": r.url,
            "headers": r.headers
        }
    )


async def handler_response(event: str, r, hc: dict[str, Any]):               # 3xx redirects / failed responses have no body
    t = r.request.timing
    hc[event].append(
        {
            "r": r,
            "status": r.status,
            "url": r.url,
            "headers": r.headers,
            "timing": t,
        }
    )


async def populate_body(response):               # 3xx redirects / failed responses have no body
    # playwright page musdt be present
    
    for entry in response.meta['handlers_context'].get("response", []):
        try:
            entry["body"] = await entry["r"].body()
        except Exception:
            entry["body"] = None

    

class CaptureHarSpider(scrapy.Spider):
    name:              str  = "capture-har"
    url:               str
    output_base:       str
    # Playwright PageMethods to run on the page before the body is captured. When None, falls back
    # to a plain 60s settle so the page has time to finish its own XHRs. Pass e.g. a
    # ``wait_for_response`` PageMethod to gate capture on a specific request completing.
    page_methods:      list[PageMethod] | None = None
    page_methods_goto: list[PageMethod] | None = None

    @classmethod
    def update_settings(cls, settings):
        playwright = {
            "PLAYWRIGHT_BROWSER_TYPE": "chromium",
            "PLAYWRIGHT_LAUNCH_OPTIONS": {
                "headless": False,
                "channel": "chrome",
                # Kept for parity with the default variant so the A/B isolates the engine. patchright
                # also manages navigator.webdriver itself; this arg can be dropped to test which scores
                # cleaner.
                "args": ["--disable-blink-features=AutomationControlled"],
            },
            "PLAYWRIGHT_CONTEXTS": {"default": {"no_viewport": True,
                                                 "locale": "en-US"
                                                 }},
            "PLAYWRIGHT_PROCESS_REQUEST_HEADERS": None,
        }
        handlers = {
            "DOWNLOAD_HANDLERS": {
                "https": "scraper.handlers.HybridDownloadHandler",
                "http": "scraper.handlers.HybridDownloadHandler",
            },
        }
        
        super().update_settings(settings) # type: ignore
        settings.setdict(
            {
                'HTTPERROR_ALLOW_ALL': True,
                "ROBOTSTXT_OBEY": False,
                **playwright,
                **handlers
                
            },
            priority="spider",
        )

    def _playwright_request(
        self,
        url: str,
        overwrite_meta: dict[str, Any] | None = None
    ) -> scrapy.Request:
        har_path = output_dir(Path(self.output_base), self.url) / "har_file.har"
        # must be initialized here, to be able to mutate in handlers
        hc = collections.defaultdict(list)
        page_methods_goto = (
            self.page_methods_goto
            if self.page_methods is not None
            else [PageMethod("wait_for_timeout", 60000)]
        )
        page_methods = (
            self.page_methods
            if self.page_methods is not None
            else [PageMethod("wait_for_timeout", 60000)]
        )
        meta = {
            "playwright": True,
            "playwright_context": "har_context",
            "playwright_context_kwargs": {
                "record_har_path": har_path,  # HAR file destination
                "record_har_url_filter": "**/*",  # capture all URLs
                "no_viewport": True,
            },
            "playwright_page_methods": page_methods,
            "playwright_page_goto_methods": page_methods_goto,
            "playwright_include_page": True, # needed to await page events
            "playwright_page_event_handlers":{
                "requestfinished": lambda request: handler_request("requestfinished", request, hc),
                "requestfailed": lambda request: handler_request("requestfailed", request, hc),
                "request": lambda request: handler_request("request", request, hc),
                "response": lambda response: handler_response("response", response, hc),
            },
            "handlers_context": hc,
        }
        if overwrite_meta:
            meta.update(overwrite_meta)
        return scrapy.Request(
            url,
            callback=self.parse,
            errback=self.errback,
            meta=meta
        )
    
    async def start(self):
        yield self._playwright_request(
            url=self.url,
        )

    async def errback(self, failure):
        # Any error in the download chain (timeouts, DNS, connection resets, errors raised in the
        # PageMethods/goto) lands here instead of silently dropping the request. Log it with the URL
        # and full traceback, then close the Playwright page if one made it onto the request so the
        # browser context is not leaked.
        request = failure.request
        logger.error(
            "request failed",
            url=request.url,
            exception_type=failure.type.__name__,
            exception=str(failure.value),
            traceback=failure.getTraceback(),
        )
        page = request.meta.get("playwright_page")
        if page is not None:
            await page.close()

    async def parse(self, response):
        path_info = derive_path_info(response)
        page_name = path_info.default_str()

        if "settle_status" in response.meta:
            logger.info(
                "settle outcome",
                page=page_name,
                url=response.url,
                status=response.meta["settle_status"],
            )
        
        await populate_body(response=response)
        page = response.meta["playwright_page"]
        await page.close()
        
        # storing main page body, meta
        pages_path = output_dir(Path(self.output_base), self.url) / "pages"
        pages_path.mkdir(parents=True, exist_ok=True)
        (pages_path / f"{page_name}.html").write_bytes(
            response.body
        )
        metadata_path = pages_path / "metadata"
        metadata_path.mkdir(parents=True, exist_ok=True)
        (metadata_path / f"{page_name}.headers.json").write_text(
            json.dumps(dict(response.headers.to_unicode_dict()), indent=4)
        )
        (metadata_path / f"{page_name}.meta.json").write_text(
            json.dumps(dict(response.meta), indent=4, default=str)
        )

        captured_pages_path = pages_path / 'captured'
        captured_pages_path_static = captured_pages_path / "static"
        captured_pages_path.mkdir(parents=True, exist_ok=True)
        captured_pages_path_static.mkdir(parents=True, exist_ok=True)
        for response in response.meta['handlers_context']["response"]:
            # storing captured responses
            path_info = derive_path_info(response['r'], timings=response['timing'])
            _start_time = int(path_info.start_time) if path_info.start_time else '0'
            page_name = f"{_start_time}-{path_info.status}-{path_info.hostname}{path_info.normalized_path[:100]}"
            
            if path_info.extension in ['.js', '.css', '.jpg', '.woff', '.png', '.woff2', '.ttf']:
                page_path = captured_pages_path_static / page_name
            else:
                page_path = captured_pages_path / page_name
            page_path.mkdir(parents=True, exist_ok=True)
            if response['body']:
                (page_path / (path_info.file_name[:200] or 'page.html')).write_bytes(
                    response['body']
                )
            
            metadata = {k: v for k, v in response.items() if k not in ["r", "body"]}
            (page_path / "metadata.json").write_text(
                json.dumps(dict(metadata), indent=4)
            )




def reset_outputs(base_dir: Path) -> None:
    """Delete this engine's ``<base_dir>/outputs/<engine>/`` subtree so a run starts clean (no
    stale captures from a prior run skew the analysis). Scoped to the active engine so a patchright
    run does not wipe the playwright captures, and vice-versa."""
    outputs = engine_outputs_dir(base_dir)
    if outputs.exists():
        shutil.rmtree(outputs)
        logger.info("cleared previous outputs", path=str(outputs))


def run_capture(
    output_base: Path,
    urls: list[str],
    page_methods: list[PageMethod] | None = None,
    page_methods_goto: list[PageMethod] | None = None,
    spider: type[CaptureHarSpider] | None = None
) -> None:
    """Capture (and analyze) a HAR for each URL, writing under ``output_base/outputs/<engine>/``.

    ``output_base`` is the calling spider's folder, so each spider keeps its own captures next to
    its code. Call this from a per-spider ``capture_har.py`` launcher.

    ``page_methods`` are Playwright PageMethods run on each page before its body is captured (e.g.
    a ``wait_for_response`` PageMethod to gate on a specific XHR). When None, each page just settles
    for 60s. The same list is applied to every URL.
    """
    spider = CaptureHarSpider if spider is None else spider
    output_base = Path(output_base)
    reset_outputs(output_base)
    settings = get_project_settings()
    process = CrawlerProcess(settings)

    @defer.inlineCallbacks
    def crawl_sequentially():
        # One crawl per URL: each gets its own browser context, so its HAR is captured and flushed
        # independently (one shared context would write only a single, mixed har.har).
        for url in urls:
            logger.info("capturing HAR", url=url, engine=ENGINE)
            yield process.crawl(
                spider,
                url=url,
                output_base=str(output_base),
                page_methods=page_methods,
                page_methods_goto=page_methods_goto
            )

            # Brief pause between targets if it is not the last one.
            if url != urls[-1]:
                delay_seconds = 3
                logger.info(f"Waiting {delay_seconds} seconds before the next crawl...")
                yield defer.DeferredList([defer.succeed(time.sleep(delay_seconds))])

        process.stop()

    crawl_sequentially()
    process.start()  # This call blocks until all crawls are complete

    # Crawl finished and every HAR is flushed to disk — turn each one into a scraper-developer
    # report (analysis.md + analysis.json next to the har.har).
    logger.info("analyzing captured HAR files")
    analyze_all_outputs(output_base / "outputs")
