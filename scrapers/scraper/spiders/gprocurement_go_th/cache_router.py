# cache.py  — drop this next to your spider
import hashlib
import time
import json
import re
from pathlib import Path
import hashlib
import json
from pathlib import Path
from urllib.parse import urlsplit, unquote

import structlog

logger = structlog.get_logger(__name__)
# directory next to THIS file, regardless of CWD
CACHE_DIR = Path(__file__).resolve().parent / "asset_cache"
CACHE_DIR.mkdir(exist_ok=True)


# re.compile(r"\.(png|jpe?g|gif|webp|svg|avif|ico|bmp)$", re.IGNORECASE),  # images
IS_IMAGE_URL = re.compile(r"\.(png|jpe?g)$", re.IGNORECASE)  # images

# What to cache. Either substrings/filenames or compiled regexes — both work.
CACHE_PATTERNS = [
    IS_IMAGE_URL,
    re.compile(r"/static/.*\.js$"), # regex
    re.compile(r"\.(woff2?|ttf)$"), # fonts
    "www.gprocurement.go.th/wps/wcm/connect/",
    re.compile(r"^https://[a-z0-9.-]+\.gprocurement\.go\.th/egp-agpc01-web/\d+\.[0-9a-f]{8,20}\.js$")
]

IGNORE = [
    "cdnjs.cloudflare.com",
    re.compile(r"\.(json)$", re.IGNORECASE),  # images
]

ABORT = [
    "wps/wcm/connect/bab0932e-03a8-4acd-b03f-39b3d4390a5b/depa.png"
]

def _should_abort(url: str) -> bool:
    for p in ABORT:
        match p:
            case re.Pattern() if p.search(url):
                return True
            case str() if p in url:
                return True
    return False

def _should_cache(url: str) -> bool:
    for p in IGNORE:
        match p:
            case re.Pattern() if p.search(url):
                return False
            case str() if p in url:
                return False
            
    for p in CACHE_PATTERNS:
        match p:
            case re.Pattern() if p.search(url):
                return True
            case str() if p in url:
                return True
    return False


CACHE_DIR = Path(__file__).resolve().parent / "asset_cache"


def _paths(url: str):
    parts = urlsplit(url)
    # path like /static/js/jquery.min.js  → mirror it under CACHE_DIR
    rel = unquote(parts.path).lstrip("/") or "index"
    name = Path(rel)

    # if there's a query (?v=123), keep the real filename but add a short tag
    if parts.query:
        tag = hashlib.sha256(parts.query.encode()).hexdigest()[:8]
        name = name.with_name(f"{name.stem}.{tag}{name.suffix}")

    # include host so two sites' /app.js don't collide
    body_path = CACHE_DIR / parts.netloc / name
    body_path.parent.mkdir(parents=True, exist_ok=True)
    meta_path = body_path.with_name(body_path.name + ".meta.json")
    return body_path, meta_path


async def cache_route(route):
    req = route.request
    url = req.url

    if not _should_cache(url):
        logger.warning("not cache", url=url)
        return await route.continue_()

    body_path, meta_path = _paths(url)

    # HIT → serve body + status + headers from disk, no network
    if body_path.exists() and meta_path.exists():
        meta = json.loads(meta_path.read_text())
        data = body_path.read_bytes()
        logger.info(
            "cache hit", 
            url=url, 
            size=len(data),
        )
        return await route.fulfill(
            status=meta["status"], headers=meta["headers"], body=data,
        )

    if _should_abort(url):
        logger.warning(
            "aborting", 
            url=url, 
        )
        return await route.abort("aborted")
    
    logger.warning("cache miss, fetching", url=url)
    # MISS → fetch over network, persist everything, then fulfill
    t0 = time.perf_counter()
    
    resp = await route.fetch(timeout=60_000)
    
    t_fetch = time.perf_counter() - t0

    t1 = time.perf_counter()
    body = await resp.body()
    t_body = time.perf_counter() - t1

    logger.info(
        "fetched",
        url=url,
        status=resp.status,
        size=len(body),
        fetch_s=round(t_fetch, 3),
        body_s=round(t_body, 3),
        total_s=round(t_fetch + t_body, 3),
    )

    # only cache successful responses; pass others through without persisting
    if resp.status != 200:
        logger.warning("not caching, non-200", url=url, status=resp.status)
        return await route.fulfill(
            status=resp.status, headers=resp.headers, body=body
        )

    meta = {
        "status": resp.status,
        "headers": dict(resp.headers),   # cache the headers too
        "url": url,
    }
    body_path.write_bytes(body)
    meta_path.write_text(json.dumps(meta))
    return await route.fulfill(
        status=resp.status, headers=resp.headers, body=body
    )