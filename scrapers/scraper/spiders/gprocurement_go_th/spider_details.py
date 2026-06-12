"""Detail-only gprocurement spider — no Playwright, pure curl_cffi.

A standalone test harness for the per-project detail chain. Given a list of project ids it
bootstraps a session and fetches every detail endpoint for each id, with **no browser**:

  bootstrap:  GET  egp-agpc01-web/announcement   (F5 sets TS4c538cb7027)
              POST egp-amas22-service/.../app-hidden {"appname":"agpc01"}
                                                     (server sets Xsrf-Token + TS0174b17a)
  per id:     generateToken -> getProjectDetail -> getProcurementDetail -> greenBook -> infoDeptSub

Why this works without Cloudflare (see har_analysis / research notes): the Turnstile gate only
mints the session-level ``X-Announcement-Token`` that the *listing* endpoint requires. The detail
chain carries **no** such token — generateToken is authorized purely by the session cookies plus a
per-request ``X-Xsrf-Token`` that is signed client-side from the ``Xsrf-Token`` cookie. Those
cookies are issued by F5 / a plain POST, independently of any Turnstile solve. So the whole detail
chain is reachable with curl_cffi alone, *provided you already know the project ids* (which in
production still come from the Turnstile-gated listing — that's the other spider's job).

Usage::

    scrapy crawl gprocurement_details -a ids=69069212137,69069212138
    scrapy crawl gprocurement_details -a ids_file=ids.txt   # one id per line

    # Read ids straight out of the listing spider's partition files (the default source):
    scrapy crawl gprocurement_details                       # every partition found
    scrapy crawl gprocurement_details -a partitions=2569-1  # one partition
    scrapy crawl gprocurement_details -a partitions=2569-1,2569-all  # a chosen subset

With no ``ids``/``ids_file`` and no ``partitions`` filter, every partition file the listing
spider has written is read. Explicit ``ids``/``ids_file`` take precedence and suppress the
partition default unless ``partitions`` is also passed (then both sources are merged, de-
duplicated). If nothing is found it falls back to ``DEFAULT_IDS`` (a known-good HAR id).
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode

import scrapy
import structlog
from scrapy.exceptions import CloseSpider
from scrapy.utils.project import data_path

from scraper.browser_profile import IMPERSONATE, navigation_headers
from scraper.items import BaseItem
from scraper.proxies import pick_proxy

from . import crypto

logger = structlog.get_logger(__name__)

ORIGIN = "https://process5.gprocurement.go.th"
# Base for the announcement service the detail endpoints live under.
DETAIL_ENDPOINT = f"{ORIGIN}/egp-atpj27-service/pb/a-egp-allt-project/announcement"
RDB_DEPT_URL = f"{ORIGIN}/egp-rdb-service/infoDeptSub"
# Legacy "view announcement document" servlet (lives on process3). The SPA's chkProject() builds a
# hidden form and POSTs it here in a new tab; the response is the announcement HTML document. It is
# authorized by the session cookies alone — no X-Xsrf-Token / X-Announcement-Token. The per-document
# fields (templateType / announceFlag / itemNumber / seqNo) come straight out of the greenBook list.
DOC_HOST = "https://process3.gprocurement.go.th"
SHOWFILE_URL = f"{DOC_HOST}/egp2procmainWeb/jsp/procsearch.sch"
# The Angular SPA shell — fetching it earns the first F5 cookie (TS4c538cb7027).
SPA_URL = f"{ORIGIN}/egp-agpc01-web/announcement?keywordSearch="
# Bootstraps the Xsrf-Token + TS0174b17a cookies; the SPA posts this on load.
APP_HIDDEN_URL = f"{ORIGIN}/egp-amas22-service/pb/a-master/app-hidden"
APP_HIDDEN_BODY = json.dumps({"appname": "agpc01"})

# The project ids consumed here are produced by the *listing* spider (gprocurement_go_th),
# which appends them to one file per partition inside its httpcache dir. We mirror that
# spider's name — not this one's — when locating the directory and files (see
# GprocurementGoTh._project_ids_path / _partition_dir in spider.py).
LISTING_SPIDER_NAME = "gprocurement_go_th"
# Per-partition id files look like "<listing-spider>-pagination-<spec>.project_ids.txt",
# where <spec> is "<budgetYear>-<projectStatus|all>" (e.g. "2569-1", "2569-all"). That
# <spec> is what `partitions=` selects on.
PROJECT_IDS_PREFIX = f"{LISTING_SPIDER_NAME}-pagination-"
PROJECT_IDS_SUFFIX = ".project_ids.txt"
PROJECT_IDS_GLOB = f"{PROJECT_IDS_PREFIX}*{PROJECT_IDS_SUFFIX}"


def _set_cookie_value(response, name: str) -> str | None:
    """Pull one cookie's value out of a response's Set-Cookie headers."""
    prefix = f"{name}=".encode()
    for raw in response.headers.getlist("Set-Cookie"):
        if raw.startswith(prefix):
            return raw.split(b";", 1)[0].split(b"=", 1)[1].decode("latin1")
    return None


class GprocurementDetailsSpider(scrapy.Spider):
    """Fetch the full detail chain for a configured list of project ids, browserless."""

    name = "gprocurement_details"

    # Known-good id captured in the HAR; used when no ids are passed on the command line.
    # One in-flight chain at a time, mirroring the listing spider's polite cadence.
    DETAIL_TOKEN_PRIORITY = 1
    DETAIL_PROJECT_PRIORITY = 2
    DETAIL_PROCUREMENT_PRIORITY = 3
    DETAIL_GREENBOOK_PRIORITY = 4
    DETAIL_DEPTSUB_PRIORITY = 5
    # Documents fan out after greenBook; keep them ahead of infoDeptSub so a started chain drains
    # all its documents before the final step (higher priority value = served first).
    DETAIL_DOC_PRIORITY = 6

    @classmethod
    def update_settings(cls, settings):
        super().update_settings(settings)  # type: ignore
        settings.setdict(
            {
                "DOWNLOAD_HANDLERS": {
                    "https": "scraper.handlers.HybridDownloadHandler",
                    "http": "scraper.handlers.HybridDownloadHandler",
                },
                # Polite, single-flight — no browser, but still gentle on the API.
                "CONCURRENT_REQUESTS": 5,
                "DOWNLOAD_DELAY": 1.0,
                "RANDOMIZE_DOWNLOAD_DELAY": True,
                "URLLENGTH_LIMIT": 0,
                "HTTPERROR_ALLOW_ALL": True,
                "ROBOTSTXT_OBEY": False,
                "RETRY_ENABLED": False,
                # Detail endpoints are token-bound / single-use; never serve them from cache.
                "HTTPCACHE_ENABLED": True,
                # Validate raw content (shared), then parse into the canonical + extra JSONL files.
                "ITEM_PIPELINES": {
                    "scraper.pipelines.ValidationPipeline": 300,
                    "scraper.spiders.gprocurement_go_th.pipeline.GprocurementJsonlPipeline": 800,
                },
            },
            priority="spider",
        )

    def __init__(
        self,
        ids: str | None = None,
        ids_file: str | None = None,
        partitions: str | None = None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        # Stash the id-source args; resolution is deferred to start(), where self.settings
        # (and thus the httpcache dir) is finally available — it isn't set yet in __init__.
        self._ids_arg = ids
        self._ids_file_arg = ids_file
        self._partitions_arg = partitions
        # One sticky-session proxy for the whole crawl. The detail chain shares a single cookie
        # jar (cf) and the API may bind / rate-limit on egress IP, so every leg must exit from the
        # same IP. Pick once here and thread it through every request via meta['proxy'].
        self.proxy = pick_proxy()
        logger.info(
            "details spider configured",
            proxy=self.proxy.username if self.proxy else None,
        )

    # ------------------------------------------------------------------ id sources
    def _partition_dir(self) -> Path:
        # The listing spider writes its partitions into data_path(HTTPCACHE_DIR)/<safe name>,
        # keyed off *its* name. Reproduce that path so we read the same folder it wrote.
        cachedir = data_path(self.settings["HTTPCACHE_DIR"], createdir=True)
        safe_name = "".join(
            c if c.isalnum() else "_" for c in LISTING_SPIDER_NAME
        ).rstrip("_")
        return Path(cachedir) / safe_name

    def _partition_files(self) -> dict[str, Path]:
        # Map partition spec ("<budgetYear>-<projectStatus|all>") -> its id file, for every
        # partition the listing spider has written. Sorted for a stable, predictable order.
        out: dict[str, Path] = {}
        for path in sorted(self._partition_dir().glob(PROJECT_IDS_GLOB)):
            spec = path.name[len(PROJECT_IDS_PREFIX) : -len(PROJECT_IDS_SUFFIX)]
            out[spec] = path
        return out

    def _load_partition_ids(self, wanted: list[str] | None) -> list[str]:
        # Read ids from the selected partition files. wanted=None means "all partitions";
        # otherwise only the listed specs are read (unknown ones are warned and skipped).
        available = self._partition_files()
        if not available:
            logger.warning(
                "no partition id files found", dir=str(self._partition_dir())
            )
            return []
        if wanted is None:
            specs = list(available)
        else:
            specs = []
            for spec in wanted:
                if spec in available:
                    specs.append(spec)
                else:
                    logger.warning(
                        "requested partition not found; skipping",
                        partition=spec,
                        available=list(available),
                        via_proxy=self.proxy.username if self.proxy else None,
                    )
        ids: list[str] = []
        for spec in specs:
            with available[spec].open(encoding="utf-8") as fh:
                file_ids = [line.strip() for line in fh if line.strip()]
            logger.info(
                "loaded partition ids",
                partition=spec,
                n=len(file_ids),
                path=str(available[spec]),
                via_proxy=self.proxy.username if self.proxy else None,
            )
            ids += file_ids
        return ids

    def _resolve_project_ids(self) -> list[str]:
        # Merge every configured id source, de-duplicating while preserving first-seen order.
        project_ids: list[str] = []
        seen: set[str] = set()

        def add(values) -> None:
            for value in values:
                value = str(value).strip()
                if value and value not in seen:
                    seen.add(value)
                    project_ids.append(value)

        if self._ids_arg:
            add(self._ids_arg.split(","))
        if self._ids_file_arg:
            with open(self._ids_file_arg, encoding="utf-8") as fh:
                add(fh)
        # Partition files are the default source: read them when no explicit ids were given,
        # or whenever `partitions=` is passed (a chosen subset; None here means all of them).
        if self._partitions_arg or not (self._ids_arg or self._ids_file_arg):
            wanted = (
                [p.strip() for p in self._partitions_arg.split(",") if p.strip()]
                if self._partitions_arg
                else None
            )
            add(self._load_partition_ids(wanted))

        return project_ids or list(self.DEFAULT_IDS)

    def _proxy_meta(self) -> dict:
        # HttpProxyMiddleware reads meta['proxy'] and splits the credentials out into a
        # Proxy-Authorization header, which scrapy_impersonate then re-applies to curl_cffi —
        # so the whole chain exits from the one IP picked at startup.
        return {"proxy": self.proxy.url} if self.proxy else {}

    # ------------------------------------------------------------------ bootstrap
    async def start(self):
        # Resolve ids now (not in __init__): partition files live under the httpcache dir,
        # which is only knowable once self.settings is wired up by the crawler.
        self.project_ids = self._resolve_project_ids()
        logger.info("details spider ids resolved", n_ids=len(self.project_ids))

        # TEMP proxy check: fire a few ipinfo.io/json requests through the chosen proxy and log the
        # egress IP. If the proxy is wired in correctly every line shows the proxy's exit IP, not
        # this host's. Remove once verified.
        for i in range(3):
            yield scrapy.Request(
                "https://ipinfo.io/json",
                callback=self.parse_ipinfo,
                headers=navigation_headers(),
                meta={
                    "impersonate": IMPERSONATE,
                    "impersonate_args": {"default_headers": False},
                    "referrer_policy": "no-referrer",
                    "ipinfo_n": i,
                    **self._proxy_meta(),
                },
                dont_filter=True,
            )

        # Seed www_visit (normally set by www.gprocurement.go.th) so we look like a returning
        # visitor, then fetch the SPA shell to earn the first F5 cookie.
        yield scrapy.Request(
            SPA_URL,
            callback=self.parse_spa,
            headers=navigation_headers(),
            cookies={"www_visit": "true"},
            meta={
                "impersonate": IMPERSONATE,
                "impersonate_args": {"default_headers": False},
                "referrer_policy": "no-referrer",
                "cookiejar": "cf",
                **self._proxy_meta(),
            },
            dont_filter=True,
        )

    def parse_ipinfo(self, response):
        # TEMP: log the egress IP seen by ipinfo.io so we can confirm the proxy is in use.
        try:
            data = response.json()
        except Exception:
            data = {"raw": response.text[:200]}
        logger.info(
            "ipinfo proxy check",
            n=response.meta.get("ipinfo_n"),
            status=response.status,
            ip=data.get("ip"),
            org=data.get("org"),
            country=data.get("country"),
            via_proxy=self.proxy.username if self.proxy else None,
        )

    def parse_spa(self, response):
        # SPA shell loaded; now POST app-hidden to mint the Xsrf-Token + TS0174b17a cookies.
        headers = self._api_headers()
        headers["origin"] = ORIGIN
        yield scrapy.Request(
            APP_HIDDEN_URL,
            method="POST",
            body=APP_HIDDEN_BODY,
            callback=self.parse_bootstrap,
            headers=headers,
            meta={
                "impersonate": IMPERSONATE,
                "impersonate_args": {"default_headers": False},
                "referrer_policy": "no-referrer",
                "cookiejar": "cf",
                **self._proxy_meta(),
            },
            dont_filter=True,
        )

    def parse_bootstrap(self, response):
        # Harvest the Xsrf-Token cookie value — every detail request re-signs it into X-Xsrf-Token.
        xsrf_cookie = _set_cookie_value(response, "Xsrf-Token")
        if not xsrf_cookie:
            raise CloseSpider(
                f"bootstrap failed: no Xsrf-Token cookie from {response.url} "
                f"(status {response.status})"
            )
        logger.info(
            "session bootstrapped",
            xsrf_cookie=xsrf_cookie[:12] + "…",
            via_proxy=self.proxy.username if self.proxy else None,
        )
        tokens = {"xsrf-cookie": xsrf_cookie}
        for project_id in self.project_ids:
            yield self._generate_token_request(project_id, tokens)

    # ------------------------------------------------------------------ headers
    def _api_headers(self) -> dict:
        # Canonical Chrome profile reshaped to the announcement XHR's fetch/CORS form.
        headers = navigation_headers()
        headers.pop("upgrade-insecure-requests", None)
        headers.pop("sec-fetch-user", None)
        headers.update(
            {
                "accept": "application/json, text/plain, */*",
                "content-type": "application/json",
                "sec-fetch-site": "same-origin",
                "sec-fetch-mode": "cors",
                "sec-fetch-dest": "empty",
            }
        )
        return headers

    def _detail_headers(
        self,
        tokens: dict,
        project_id: str,
        announcement_token: str | None = None,
        post: bool = False,
    ) -> dict:
        # X-Xsrf-Token is re-minted per request from the Xsrf-Token cookie; the per-project
        # announcement token (from generateToken) authorizes the detail GETs.
        headers = self._api_headers()
        headers["x-xsrf-token"] = crypto.xsrf_token(tokens["xsrf-cookie"])
        # The SPA sends the procurement detail route as Referer on every detail XHR.
        headers["referer"] = (
            f"{ORIGIN}/egp-agpc01-web/announcement/procurement/{crypto.route_param(project_id)}"
        )
        if announcement_token:
            headers["x-announcement-token"] = announcement_token
        if post:
            headers["origin"] = ORIGIN
        return headers

    def _detail_request(
        self,
        url: str,
        callback,
        tokens: dict,
        project_id: str,
        meta_extra: dict,
        announcement_token: str | None = None,
        method: str = "GET",
        body: str | None = None,
        priority: int = 0,
    ) -> scrapy.Request:
        return scrapy.Request(
            url,
            method=method,
            body=body,
            callback=callback,
            headers=self._detail_headers(
                tokens,
                project_id,
                announcement_token=announcement_token,
                post=method == "POST",
            ),
            priority=priority,
            dont_filter=True,
            meta={
                "impersonate": IMPERSONATE,
                "impersonate_args": {"default_headers": False},
                "referrer_policy": "no-referrer",
                "cookiejar": "cf",
                "api_tokens": tokens,
                **self._proxy_meta(),
                **meta_extra,
            },
        )

    # ------------------------------------------------------------------ detail chain
    def _generate_token_request(self, project_id: str, tokens: dict) -> scrapy.Request:
        project_id = str(project_id)
        body = json.dumps({"key": crypto.generate_token_key(project_id)})
        logger.info("detail 1/5 generateToken queued", project_id=project_id)
        return self._detail_request(
            f"{DETAIL_ENDPOINT}/generateToken",
            self.parse_token,
            tokens,
            project_id,
            method="POST",
            body=body,
            priority=self.DETAIL_TOKEN_PRIORITY,
            meta_extra={"project_id": project_id, "detail": {}},
        )

    def _detail_json(self, response):
        # Detail endpoints answer {"response": {"responseCode": "0", ...}, "data": ...}.
        if response.status != 200:
            return None
        try:
            payload = response.json()
        except Exception:
            return None
        if (payload.get("response") or {}).get("responseCode") != "0":
            return None
        return payload.get("data")

    def parse_token(self, response):
        project_id = response.meta["project_id"]
        token = self._detail_json(response)
        if not token:
            logger.warning(
                "generateToken failed; skipping detail",
                status=response.status,
                project_id=project_id,
                body=response.text[:200],
                via_proxy=self.proxy.username if self.proxy else None,
            )
            return
        logger.info(
            "detail 1/5 generateToken done",
            project_id=project_id,
            via_proxy=self.proxy.username if self.proxy else None,
        )
        detail = response.meta["detail"]
        logger.info(
            "detail 2/5 getProjectDetail queued",
            project_id=project_id,
            via_proxy=self.proxy.username if self.proxy else None,
        )
        yield self._detail_request(
            f"{DETAIL_ENDPOINT}/getProjectDetail?projectId={project_id}",
            self.parse_project_detail,
            response.meta["api_tokens"],
            project_id,
            announcement_token=token,
            priority=self.DETAIL_PROJECT_PRIORITY,
            meta_extra={
                "project_id": project_id,
                "announcement_token": token,
                "detail": detail,
            },
        )

    def parse_project_detail(self, response):
        project_id = response.meta["project_id"]
        token = response.meta["announcement_token"]
        detail = response.meta["detail"]
        detail["getProjectDetail"] = response.text
        logger.info(
            "detail 2/5 getProjectDetail done",
            project_id=project_id,
            status=response.status,
            bytes=len(response.body),
            via_proxy=self.proxy.username if self.proxy else None,
        )
        logger.info(
            "detail 3/5 getProcurementDetail queued",
            project_id=project_id,
            via_proxy=self.proxy.username if self.proxy else None,
        )
        yield self._detail_request(
            f"{DETAIL_ENDPOINT}/getProcurementDetail?projectId={project_id}",
            self.parse_procurement_detail,
            response.meta["api_tokens"],
            project_id,
            announcement_token=token,
            priority=self.DETAIL_PROCUREMENT_PRIORITY,
            meta_extra={
                "project_id": project_id,
                "announcement_token": token,
                "project_data": self._detail_json(response) or {},
                "detail": detail,
            },
        )

    def parse_procurement_detail(self, response):
        project_id = response.meta["project_id"]
        token = response.meta["announcement_token"]
        detail = response.meta["detail"]
        detail["getProcurementDetail"] = response.text
        project_data = response.meta["project_data"]
        procurement_data = self._detail_json(response) or {}

        method_id = project_data.get("methodId") or procurement_data.get("methodId")
        announce_type = project_data.get("announceType", "")
        logger.info(
            "detail 3/5 getProcurementDetail done",
            project_id=project_id,
            status=response.status,
            method_id=method_id,
            dept_id=procurement_data.get("deptId"),
            via_proxy=self.proxy.username if self.proxy else None,
        )
        params = urlencode(
            {
                "mode": "LINK",
                "methodId": method_id or "",
                "tempProjectId": project_id,
                "pageAnnounceType": announce_type,
            }
        )
        logger.info("detail 4/5 greenBook queued", project_id=project_id)
        yield self._detail_request(
            f"{DETAIL_ENDPOINT}/greenBook?{params}",
            self.parse_green_book,
            response.meta["api_tokens"],
            project_id,
            announcement_token=token,
            priority=self.DETAIL_GREENBOOK_PRIORITY,
            meta_extra={
                "project_id": project_id,
                "announcement_token": token,
                "dept_id": procurement_data.get("deptId"),
                "dept_sub_id": procurement_data.get("deptSubId"),
                "detail": detail,
            },
        )

    def parse_green_book(self, response):
        project_id = response.meta["project_id"]
        detail = response.meta["detail"]
        detail["greenBook"] = response.text
        detail.setdefault("documents", [])
        dept_id = response.meta["dept_id"]
        dept_sub_id = response.meta["dept_sub_id"]

        # The greenBook payload carries the list of downloadable announcement documents. Each entry
        # has everything chkProject() needs to POST the ShowHTMLFile servlet.
        data = self._detail_json(response) or {}
        docs = data.get("greenBookAnnouncementTypeLinkDto") or []
        logger.info(
            "detail 4/5 greenBook done",
            project_id=project_id,
            status=response.status,
            bytes=len(response.body),
            n_documents=len(docs),
            via_proxy=self.proxy.username if self.proxy else None,
        )
        yield from self._drain_documents(
            response, project_id, detail, list(docs), dept_id, dept_sub_id
        )

    # ------------------------------------------------------------------ document download
    def _drain_documents(
        self, response, project_id, detail, pending, dept_id, dept_sub_id
    ):
        """Fetch the next pending announcement document, or move on once they're all done."""
        if pending:
            doc, *rest = pending
            yield self._document_request(
                response, project_id, detail, doc, rest, dept_id, dept_sub_id
            )
            return
        # All documents fetched (or none) — continue the chain.
        # infoDeptSub lives on a different service and needs no announcement token — just the
        # session cookies + a signed X-Xsrf-Token. Skip it if no dept ids were found.
        if dept_id and dept_sub_id:
            params = urlencode({"deptId": dept_id, "deptSubId": dept_sub_id})
            logger.info("detail 5/5 infoDeptSub queued", project_id=project_id)
            yield self._detail_request(
                f"{RDB_DEPT_URL}?{params}",
                self.parse_dept_sub,
                response.meta["api_tokens"],
                project_id,
                priority=self.DETAIL_DEPTSUB_PRIORITY,
                meta_extra={"project_id": project_id, "detail": detail},
            )
        else:
            logger.info(
                "detail done (no dept ids; skipping infoDeptSub), emitting item",
                project_id=project_id,
                n_documents=len(detail.get("documents", [])),
                via_proxy=self.proxy.username if self.proxy else None,
            )
            yield self._build_detail_item(project_id, detail, response)

    def _document_request(
        self, response, project_id, detail, doc, pending, dept_id, dept_sub_id
    ):
        # ShowHTMLFile is a plain top-level form navigation (sec-fetch-dest: document), not an XHR:
        # so we send the navigation headers + an x-www-form-urlencoded body, no XSRF/announce token.
        doc_project_id = str(doc.get("projectId") or project_id)
        body = urlencode(
            {
                "pass": "F",
                "templateType": doc.get("templateType", ""),
                "temp_Announ": doc.get("announceFlag", ""),
                "temp_itemNo": doc.get("itemNumber", ""),
                "seqNo": doc.get("seqNo", ""),
                "announceId": "",
                "projectId": doc_project_id,
            }
        )
        params = urlencode(
            {
                "pid": doc_project_id,
                "servlet": "gojsp",
                "proc_id": "ShowHTMLFile",
                "processFlows": "Procure",
            }
        )
        headers = navigation_headers()
        headers["content-type"] = "application/x-www-form-urlencoded"
        headers["origin"] = ORIGIN
        headers["referer"] = f"{ORIGIN}/"
        # process3 is the same registrable domain as process5 but a different host.
        headers["sec-fetch-site"] = "same-site"
        logger.info(
            "document queued",
            project_id=project_id,
            announce_type=doc.get("announceType"),
            seq_no=doc.get("seqNo"),
            via_proxy=self.proxy.username if self.proxy else None,
        )
        return scrapy.Request(
            f"{SHOWFILE_URL}?{params}",
            method="POST",
            body=body,
            callback=self.parse_document,
            headers=headers,
            priority=self.DETAIL_DOC_PRIORITY,
            dont_filter=True,
            meta={
                "impersonate": IMPERSONATE,
                "impersonate_args": {"default_headers": False},
                "referrer_policy": "no-referrer",
                "cookiejar": "cf",
                "api_tokens": response.meta["api_tokens"],
                "project_id": project_id,
                "detail": detail,
                "doc": doc,
                "pending": pending,
                "dept_id": dept_id,
                "dept_sub_id": dept_sub_id,
                **self._proxy_meta(),
            },
        )

    def parse_document(self, response):
        project_id = response.meta["project_id"]
        detail = response.meta["detail"]
        doc = response.meta["doc"]
        detail.setdefault("documents", []).append(
            {
                "announceType": doc.get("announceType"),
                "templateType": doc.get("templateType"),
                "itemNumber": doc.get("itemNumber"),
                "seqNo": doc.get("seqNo"),
                "url": response.url,
                "status": response.status,
                "content": response.text,
            }
        )
        logger.info(
            "document fetched",
            project_id=project_id,
            announce_type=doc.get("announceType"),
            status=response.status,
            bytes=len(response.body),
            via_proxy=self.proxy.username if self.proxy else None,
        )
        yield from self._drain_documents(
            response,
            project_id,
            detail,
            response.meta["pending"],
            response.meta["dept_id"],
            response.meta["dept_sub_id"],
        )

    def parse_dept_sub(self, response):
        project_id = response.meta["project_id"]
        detail = response.meta["detail"]
        detail["infoDeptSub"] = response.text
        logger.info(
            "detail 5/5 infoDeptSub done, emitting item",
            project_id=project_id,
            status=response.status,
            via_proxy=self.proxy.username if self.proxy else None,
        )
        yield self._build_detail_item(project_id, detail, response)

    def _build_detail_item(self, project_id: str, detail: dict, response) -> BaseItem:
        # One record per project. getProjectDetail is the "main" body (-> content); the other
        # endpoints ride along in extra so the record stays whole.
        item = BaseItem()
        item["request_url"] = (
            f"{ORIGIN}/egp-agpc01-web/announcement/procurement/{crypto.route_param(project_id)}"
        )
        item["response_url"] = response.url
        item["domain"] = "gprocurement.go.th"
        item["status"] = response.status
        item["scraped_at"] = datetime.now(UTC).isoformat()
        item["content"] = detail.get("getProjectDetail", "")
        item["extra"] = {
            "project_id": project_id,
            "getProcurementDetail": detail.get("getProcurementDetail"),
            "greenBook": detail.get("greenBook"),
            "infoDeptSub": detail.get("infoDeptSub"),
            # The announcement HTML documents linked from greenBook (ShowHTMLFile servlet).
            "documents": detail.get("documents", []),
        }
        logger.info("scrapped", via_proxy=self.proxy.username if self.proxy else None)
        return item
