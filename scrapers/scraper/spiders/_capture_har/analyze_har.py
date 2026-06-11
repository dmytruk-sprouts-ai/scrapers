"""Turn a captured ``har.har`` into a scraper-dev report (``analysis.md`` + ``analysis.json``).

:mod:`capture_har` records a full HAR of one browser visit per target (the page document plus every
sub-request: scripts, XHR/fetch, images, and — crucially — any anti-bot challenge traffic). A raw
1 MB HAR is unreadable; this module parses it with `haralyzer <https://haralyzer.readthedocs.io/>`_
and distills exactly what someone writing a scraper for that site needs to decide *how* to scrape:

* **Protection verdict** — which anti-bot/WAF vendor guards the site (Cloudflare, DataDome, Akamai,
  PerimeterX, Imperva, Turnstile/reCAPTCHA/hCaptcha, …), proven by the URLs, response headers and
  cookies in the capture, and whether the target document was actually delivered or blocked.
* **The landing document** — final status/type/size and the request headers (User-Agent, client
  hints, Accept-Language) that got it, plus any ``Accept-CH``/``critical-CH`` the server demands.
* **Session cookies** — the gate cookies a vendor sets (``cf_clearance``, ``datadome``, ``_abck`` …)
  that a stateless scraper must obtain/replay.
* **Data endpoints** — JSON / XHR APIs hit while rendering, i.e. candidates to scrape directly and
  skip the HTML entirely.
* **Timeline, host breakdown, statistics** — the request waterfall, third-party hosts, status/type
  mix, and timing.
* **Recommendations** — a derived "try this" (plain HTTP vs. impersonation vs. full browser, cookie
  reuse, direct-API) based on all of the above.

Run it standalone to (re)analyze HARs already on disk under ``outputs/`` (no crawling)::

    python -m scraper.spiders._capture_har.analyze_har
    python -m scraper.spiders._capture_har.analyze_har path/to/har.har
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import structlog
from haralyzer import HarParser

logger = structlog.get_logger(__name__)

OUTPUTS_DIR = Path(__file__).resolve().parent / "outputs"
HAR_NAME = "har_file.har"
REPORT_JSON = "har_analysis.json"
REPORT_MD = "har_analysis.md"

# --------------------------------------------------------------------------- protection signatures
#
# Each vendor is recognised from any of three independent kinds of evidence in the capture: a URL
# pattern (a request to the vendor's challenge/telemetry endpoint), a response *header* (set by the
# edge in front of the origin), or a *cookie* the vendor plants to track/clear a session. Cookies
# are the highest-value signal for a scraper — they are exactly what a stateless client must carry —
# so they are reported with extra prominence below. Patterns are matched case-insensitively.
PROTECTION_SIGNATURES: list[dict] = [
    {
        "vendor": "Cloudflare",
        "kind": "CDN / WAF / Bot Management",
        "url": [r"/cdn-cgi/challenge-platform/", r"challenges\.cloudflare\.com", r"/cdn-cgi/"],
        "headers": ["cf-ray", "cf-mitigated", "cf-cache-status", "cf-chl-out"],
        "header_values": {"server": r"cloudflare"},
        "cookies": ["cf_clearance", "__cf_bm", "__cfwaitingroom", "cf_chl_", "cf_use_ob"],
    },
    {
        "vendor": "Cloudflare Turnstile",
        "kind": "CAPTCHA / challenge widget",
        "url": [r"challenges\.cloudflare\.com/turnstile", r"/turnstile/v0/"],
        "headers": [],
        "header_values": {},
        "cookies": [],
    },
    {
        "vendor": "DataDome",
        "kind": "Bot Management / CAPTCHA",
        "url": [r"captcha-delivery\.com", r"datadome", r"js\.datadome\.co"],
        "headers": ["x-datadome", "x-dd-b", "x-datadome-cid"],
        "header_values": {"set-cookie": r"datadome="},
        "cookies": ["datadome"],
    },
    {
        "vendor": "PerimeterX / HUMAN",
        "kind": "Bot Management",
        "url": [r"/_px/", r"perimeterx", r"px-cloud\.net", r"/px/xhr", r"captcha\.px-cdn"],
        "headers": ["x-px", "x-px-block"],
        "header_values": {},
        "cookies": ["_px", "_pxhd", "_pxvid", "pxcts", "_px2", "_px3"],
    },
    {
        "vendor": "Akamai Bot Manager",
        "kind": "CDN / Bot Management",
        "url": [r"/akam/", r"\.akamai", r"/_bm/", r"ds\.bm\."],
        "headers": ["x-akamai-transformed", "akamai-grn", "x-akamai-request-id"],
        "header_values": {"server": r"akamaighost"},
        "cookies": ["_abck", "ak_bmsc", "bm_sz", "bm_sv", "bm_mi"],
    },
    {
        "vendor": "Imperva / Incapsula",
        "kind": "CDN / WAF",
        "url": [r"/_Incapsula_Resource", r"incapsula"],
        "headers": ["x-iinfo", "x-cdn"],
        "header_values": {"x-cdn": r"incapsula", "set-cookie": r"(incap_ses_|visid_incap_)"},
        "cookies": ["incap_ses_", "visid_incap_", "nlbi_", "reese84", "___utmvc"],
    },
    {
        "vendor": "Kasada",
        "kind": "Bot Management",
        "url": [r"/_kpsdk", r"kasada", r"\.kpsdk\."],
        "headers": ["x-kpsdk-ct", "x-kpsdk-v"],
        "header_values": {},
        "cookies": ["KP_UIDz", "__kp"],
    },
    {
        "vendor": "AWS WAF",
        "kind": "WAF",
        "url": [r"/.well-known/awswaf", r"token\.awswaf\.com"],
        "headers": ["x-amzn-waf-action"],
        "header_values": {"server": r"awselb", "set-cookie": r"aws-waf-token="},
        "cookies": ["aws-waf-token"],
    },
    {
        "vendor": "Queue-it",
        "kind": "Virtual waiting room",
        "url": [r"queue-it\.net", r"\.queue-it\."],
        "headers": [],
        "header_values": {},
        "cookies": ["Queue-it", "QueueITAccepted"],
    },
    {
        "vendor": "Sucuri",
        "kind": "CDN / WAF",
        "url": [r"sucuri"],
        "headers": ["x-sucuri-id", "x-sucuri-cache"],
        "header_values": {},
        "cookies": ["sucuri_cloudproxy_"],
    },
    {
        "vendor": "Google reCAPTCHA",
        "kind": "CAPTCHA widget",
        "url": [r"google\.com/recaptcha", r"recaptcha/", r"gstatic\.com/recaptcha"],
        "headers": [],
        "header_values": {},
        "cookies": [],
    },
    {
        "vendor": "hCaptcha",
        "kind": "CAPTCHA widget",
        "url": [r"hcaptcha\.com", r"\.hcaptcha\."],
        "headers": [],
        "header_values": {},
        "cookies": [],
    },
]

# Interstitial titles / body phrases that mean "a challenge was served instead of the page". The
# document title is the cleanest tell Playwright records; we also keep a couple of body phrases.
CHALLENGE_TITLES = (
    "just a moment",
    "attention required",
    "verify you are human",
    "checking your browser",
    "access denied",
    "pardon our interruption",
    "are you a robot",
    "one more step",
)

# Statuses that, on the *document* request, signal the page was withheld rather than delivered.
BLOCK_STATUSES = {401, 403, 429, 503}


# --------------------------------------------------------------------------- small helpers


def _header_value(headers: list[dict], name: str) -> str | None:
    """First value of header ``name`` (case-insensitive) from a HAR header list, or None."""
    name = name.lower()
    for h in headers:
        if h.get("name", "").lower() == name:
            return h.get("value", "")
    return None


def _all_header_values(headers: list[dict], name: str) -> list[str]:
    """Every value of header ``name`` (case-insensitive) — Set-Cookie repeats per cookie."""
    name = name.lower()
    return [h.get("value", "") for h in headers if h.get("name", "").lower() == name]


def _cookie_name(set_cookie_value: str) -> str:
    """``name`` out of a ``name=value; Path=/; ...`` Set-Cookie header value."""
    return set_cookie_value.split("=", 1)[0].strip()


def _transfer_size(entry) -> int:
    """Bytes on the wire for a response, preferring Playwright's ``_transferSize``."""
    raw = entry.raw_entry["response"]
    size = raw.get("_transferSize")
    if isinstance(size, int) and size >= 0:
        return size
    body = entry.response.bodySize or 0
    headers = raw.get("headersSize") or 0
    return max(body, 0) + max(headers, 0)


def _resource_type(entry) -> str:
    """Coarse resource class from the response MIME type (+ URL), for the timeline and stats.

    Playwright's HAR does not record ``_resourceType``, so derive it: this is what tells a reader at
    a glance which rows are the page, which are scripts/assets, and which are data (XHR/JSON).
    """
    mime = (entry.response.mimeType or "").lower()
    url = entry.url.lower()
    if "json" in mime:
        return "json"
    if "html" in mime:
        return "document"
    if "javascript" in mime or "ecmascript" in mime or url.endswith(".js"):
        return "script"
    if "css" in mime or url.endswith(".css"):
        return "stylesheet"
    if mime.startswith("image/"):
        return "image"
    if mime.startswith("font/") or "font" in mime:
        return "font"
    if mime.startswith(("audio/", "video/")):
        return "media"
    if mime.startswith("text/plain"):
        # Most text/plain in a browser capture is beacon/telemetry XHR (challenge flows especially).
        return "xhr"
    return "other"


def _host(url: str) -> str:
    return urlparse(url).hostname or ""


def _matches_any(text: str, patterns: list[str]) -> str | None:
    """Return the first pattern that matches ``text`` (case-insensitive), else None."""
    for p in patterns:
        if re.search(p, text, re.I):
            return p
    return None


# --------------------------------------------------------------------------- detection


def detect_protections(entries: list) -> list[dict]:
    """Scan every entry's URL, response headers and cookies for each vendor's fingerprints.

    Returns one record per detected vendor with the concrete evidence (so a human can verify the
    verdict against the HAR), most-evidenced vendor first.
    """
    found: dict[str, dict] = {}

    def hit(sig: dict, kind: str, signal: str, evidence: str) -> None:
        # Group by (via, signal) and keep a count + one example, so a header like ``cf-ray`` that
        # appears on every response collapses to one line ("seen on N responses") instead of dozens.
        rec = found.setdefault(
            sig["vendor"],
            {"vendor": sig["vendor"], "category": sig["kind"], "evidence": {}},
        )
        slot = rec["evidence"].setdefault(
            (kind, signal), {"via": kind, "signal": signal, "example": evidence, "count": 0}
        )
        slot["count"] += 1

    for entry in entries:
        url = entry.url
        resp_headers = entry.raw_entry["response"]["headers"]
        set_cookies = _all_header_values(resp_headers, "set-cookie")
        for sig in PROTECTION_SIGNATURES:
            if (p := _matches_any(url, sig["url"])):
                hit(sig, "url", p, url[:120])
            for hdr in sig["headers"]:
                if (val := _header_value(resp_headers, hdr)) is not None:
                    hit(sig, "header", hdr, f"{hdr}: {val[:80]}")
            for hdr, pat in sig.get("header_values", {}).items():
                for val in _all_header_values(resp_headers, hdr):
                    if re.search(pat, val, re.I):
                        hit(sig, "header", hdr, f"{hdr}: {val[:80]}")
            for cookie_prefix in sig["cookies"]:
                for sc in set_cookies:
                    if _cookie_name(sc).lower().startswith(cookie_prefix.lower()):
                        hit(sig, "cookie", cookie_prefix, _cookie_name(sc))

    records = []
    for rec in found.values():
        rec["evidence"] = list(rec["evidence"].values())
        records.append(rec)
    return sorted(records, key=lambda r: len(r["evidence"]), reverse=True)


def collect_set_cookies(entries: list) -> list[dict]:
    """Every cookie the site set during the visit — the session state a scraper must reproduce."""
    seen: dict[str, dict] = {}
    for entry in entries:
        for sc in _all_header_values(entry.raw_entry["response"]["headers"], "set-cookie"):
            name = _cookie_name(sc)
            attrs = [p.strip() for p in sc.split(";")[1:]]
            seen.setdefault(
                name,
                {
                    "name": name,
                    "set_by": _host(entry.url),
                    "attributes": "; ".join(attrs)[:120],
                },
            )
    return list(seen.values())


def find_document_entries(entries: list, page_url: str) -> list:
    """Document (top-level navigation) requests for the target — the ones whose URL is the page URL.

    A challenge flow shows up here as e.g. ``307 → 403`` with no final ``200``; a clean fetch is a
    single ``200``. Matching is by scheme+host+path (query/fragments ignored).
    """
    target = urlparse(page_url)
    target_key = (target.hostname, target.path.rstrip("/"))
    docs = []
    for entry in entries:
        if _resource_type(entry) not in ("document", "other"):
            continue
        u = urlparse(entry.url)
        if (u.hostname, u.path.rstrip("/")) == target_key:
            docs.append(entry)
    return docs


def find_data_endpoints(entries: list, protection_hosts: set[str]) -> list[dict]:
    """XHR/JSON requests that are real data, not anti-bot telemetry — direct-scrape candidates.

    A JSON (or ``/api/``) response that isn't served by a detected protection host is often the
    cleanest way to scrape the site: hit the API and skip HTML parsing entirely.
    """
    out = []
    for entry in entries:
        rtype = _resource_type(entry)
        host = _host(entry.url)
        is_api = rtype == "json" or re.search(r"/(api|graphql|gql|v\d)/", entry.url, re.I)
        if not is_api or host in protection_hosts:
            continue
        out.append(
            {
                "method": entry.request.method,
                "status": entry.status,
                "url": entry.url,
                "mime": entry.response.mimeType,
                "size_bytes": _transfer_size(entry),
            }
        )
    return out


# --------------------------------------------------------------------------- report assembly


def _offset_ms(entry, t0: datetime | None) -> float:
    if t0 is None or entry.startTime is None:
        return 0.0
    return round((entry.startTime - t0).total_seconds() * 1000, 1)


def analyze_page(page) -> dict:
    """Build the full structured report for one HAR page (one target visit)."""
    entries = list(page.entries)
    t0 = entries[0].startTime if entries else None

    protections = detect_protections(entries)
    protection_hosts = {
        _host(e.url)
        for sig in PROTECTION_SIGNATURES
        for e in entries
        if _matches_any(e.url, sig["url"])
    }
    cookies = collect_set_cookies(entries)
    docs = find_document_entries(entries, page.url)
    final_doc = docs[-1] if docs else None
    data_endpoints = find_data_endpoints(entries, protection_hosts)

    # Verdict: was the target page delivered, or blocked/challenged?
    try:
        title = page.title or ""
    except AttributeError:
        # happens when staticfiles served from local cache
        title = ""
    title_is_challenge = any(m in title.lower() for m in CHALLENGE_TITLES)
    doc_status = final_doc.status if final_doc else None
    blocked = bool(protections) and (
        title_is_challenge or (doc_status in BLOCK_STATUSES) or doc_status is None
    )
    if not protections and doc_status and 200 <= doc_status < 300 and not title_is_challenge:
        verdict = "clear"
    elif blocked:
        verdict = "blocked"
    elif protections:
        verdict = "protected-but-delivered"
    else:
        verdict = "unknown"

    # Document request header profile — the headers that fetched (or were rejected for) the page.
    doc_req_headers: dict[str, str] = {}
    if final_doc:
        for h in final_doc.raw_entry["request"]["headers"]:
            doc_req_headers[h["name"]] = h["value"]
    accept_ch = critical_ch = None
    if final_doc:
        rh = final_doc.raw_entry["response"]["headers"]
        accept_ch = _header_value(rh, "accept-ch")
        critical_ch = _header_value(rh, "critical-ch")

    # Timeline.
    timeline = [
        {
            "n": i,
            "offset_ms": _offset_ms(e, t0),
            "time_ms": round(e.time, 1) if e.time else 0,
            "method": e.request.method,
            "status": e.status,
            "type": _resource_type(e),
            "size_bytes": _transfer_size(e),
            "host": _host(e.url),
            "url": e.url,
        }
        for i, e in enumerate(entries)
    ]

    # Host breakdown.
    host_counts: Counter = Counter()
    host_bytes: defaultdict = defaultdict(int)
    for e in entries:
        host_counts[_host(e.url)] += 1
        host_bytes[_host(e.url)] += _transfer_size(e)
    hosts = sorted(
        (
            {
                "host": h,
                "requests": n,
                "bytes": host_bytes[h],
                "is_protection": h in protection_hosts,
            }
            for h, n in host_counts.items()
        ),
        key=lambda r: r["requests"],
        reverse=True,
    )

    # Stats.
    status_counts = Counter(e.status for e in entries)
    type_counts = Counter(_resource_type(e) for e in entries)

    return {
        "target_url": page.url,
        "page_title": title,
        "verdict": verdict,
        "verdict_detail": _verdict_detail(verdict, protections, doc_status, title_is_challenge),
        "captured_entries": len(entries),
        "total_bytes": page.get_total_size(entries),
        "page_load_time_ms": page.page_load_time,
        "time_to_first_byte_ms": round(page.time_to_first_byte, 1)
        if page.time_to_first_byte
        else page.time_to_first_byte,
        "protections": protections,
        "session_cookies": cookies,
        "document": _document_summary(final_doc, docs, accept_ch, critical_ch, doc_req_headers),
        "data_endpoints": data_endpoints,
        "hosts": hosts,
        "stats": {
            "by_status": dict(sorted(status_counts.items())),
            "by_type": dict(type_counts.most_common()),
        },
        "timeline": timeline,
        "recommendations": build_recommendations(
            verdict, protections, cookies, data_endpoints, accept_ch or critical_ch
        ),
    }


def _verdict_detail(verdict, protections, doc_status, title_is_challenge) -> str:
    names = ", ".join(p["vendor"] for p in protections) or "none"
    match verdict:
        case "clear":
            return "Target document returned 2xx with no protection fingerprints — scrapable as-is."
        case "blocked":
            why = "challenge interstitial" if title_is_challenge else f"document HTTP {doc_status}"
            return f"Blocked by {names} ({why}); the real page was not delivered in this capture."
        case "protected-but-delivered":
            return f"{names} present but the document was delivered — protection is passive."
        case _:
            return "Could not classify — no clear document response in the capture."


def _document_summary(final_doc, docs, accept_ch, critical_ch, req_headers) -> dict:
    if final_doc is None:
        return {"chain": [], "note": "no top-level document request matched the target URL"}
    # Headers a scraper most likely needs to mirror.
    key_req = {
        k: req_headers[k]
        for k in (
            "User-Agent",
            "Accept",
            "Accept-Language",
            "Accept-Encoding",
            "Referer",
            "sec-ch-ua",
            "sec-ch-ua-platform",
            "sec-ch-ua-mobile",
            "Upgrade-Insecure-Requests",
        )
        if k in req_headers
    }
    return {
        "final_status": final_doc.status,
        "final_mime": final_doc.response.mimeType,
        "http_version": final_doc.response.httpVersion,
        "size_bytes": _transfer_size(final_doc),
        "chain": [{"status": d.status, "url": d.url} for d in docs],
        "request_headers": key_req,
        "accept_ch": accept_ch,
        "critical_ch": critical_ch,
    }


def build_recommendations(
    verdict, protections, cookies, data_endpoints, needs_client_hints
) -> list[str]:
    """Derive an actionable 'try this' list from the verdict and evidence."""
    recs: list[str] = []
    vendors = {p["vendor"] for p in protections}
    cookie_names = [c["name"] for c in cookies]

    if verdict == "clear":
        recs.append(
            "No anti-bot detected — a plain HTTP client (requests/Scrapy) should work; reach for a "
            "browser only if content is JS-rendered."
        )
    elif {"Cloudflare", "Cloudflare Turnstile"} & vendors:
        recs.append(
            "Cloudflare challenge in play — use a real browser (scrapy-playwright/stealth) to "
            "solve it, or reuse a valid `cf_clearance` cookie + the *exact* matching User-Agent."
        )
    elif "DataDome" in vendors:
        recs.append(
            "DataDome present — needs a browser or a captcha-solving flow; carry the `datadome` "
            "cookie and a consistent UA/IP across requests."
        )
    elif "Akamai Bot Manager" in vendors:
        recs.append(
            "Akamai Bot Manager present — the `_abck`/`bm_sz` cookies must be earned by a real "
            "browser and replayed; sensor-data spoofing is fragile."
        )
    elif "PerimeterX / HUMAN" in vendors:
        recs.append(
            "PerimeterX/HUMAN present — use a browser; the `_px*` cookies gate access and rotate."
        )
    elif vendors:
        recs.append(
            f"Protection present ({', '.join(sorted(vendors))}) — favour a real browser and replay "
            "its cookies; validate that plain HTTP isn't silently served a soft block."
        )

    if cookie_names:
        recs.append(
            "Persist & replay these cookies across requests: " + ", ".join(cookie_names[:8])
        )
    if data_endpoints:
        recs.append(
            f"{len(data_endpoints)} JSON/API endpoint(s) seen — consider scraping them directly "
            "instead of parsing HTML (check whether they need the session cookies above)."
        )
    if needs_client_hints:
        recs.append(
            "Server requests UA client hints (Accept-CH/critical-CH) — send matching `sec-ch-ua*` "
            "headers consistent with your User-Agent, or use a browser that emits them."
        )
    if not recs:
        recs.append("No specific blockers detected; start with a plain HTTP client.")
    return recs


# --------------------------------------------------------------------------- rendering


def render_markdown(report: dict, source: Path) -> str:
    r = report
    verdict_glyph = {
        "clear": "🟢 clear",
        "protected-but-delivered": "🟡 protected (delivered)",
        "blocked": "🔴 blocked",
        "unknown": "⚪ unknown",
    }
    L: list[str] = []
    generated = datetime.now().astimezone().isoformat(timespec="seconds")
    L += [f"# HAR analysis — {r['target_url']}", ""]
    L += [f"_Source: `{source.name}` · generated {generated}_", ""]

    L += ["## Verdict", ""]
    L += [f"- **Status:** {verdict_glyph.get(r['verdict'], r['verdict'])}"]
    L += [f"- {r['verdict_detail']}"]
    L += [f"- **Page title:** {r['page_title'] or '—'}"]
    L += [
        f"- **Captured:** {r['captured_entries']} requests · "
        f"{r['total_bytes'] / 1024:.0f} KiB · "
        f"load {r['page_load_time_ms'] or '—'} ms · TTFB {r['time_to_first_byte_ms'] or '—'} ms",
        "",
    ]

    L += ["## Protection", ""]
    if r["protections"]:
        for p in r["protections"]:
            L.append(f"### {p['vendor']} — {p['category']}")
            for ev in p["evidence"]:
                times = f" _(×{ev['count']})_" if ev["count"] > 1 else ""
                L.append(f"- `{ev['via']}` **{ev['signal']}** — {ev['example']}{times}")
            L.append("")
    else:
        L += ["No anti-bot / WAF fingerprints found in the capture.", ""]

    doc = r["document"]
    L += ["## Landing document", ""]
    if doc.get("chain"):
        L += [f"- **Final:** HTTP {doc['final_status']} · {doc['final_mime']} · "
              f"{doc['http_version']} · {doc['size_bytes']} B"]
        if len(doc["chain"]) > 1:
            L.append("- **Chain:** " + " → ".join(f"{c['status']}" for c in doc["chain"]))
        if doc.get("accept_ch"):
            L.append(f"- **Accept-CH:** `{doc['accept_ch'][:160]}`")
        if doc.get("critical_ch"):
            L.append(f"- **critical-CH:** `{doc['critical_ch'][:160]}`")
        L.append("")
        if doc.get("request_headers"):
            L += ["**Request headers used:**", "", "| header | value |", "|---|---|"]
            for k, v in doc["request_headers"].items():
                L.append(f"| {k} | {v[:90]} |")
            L.append("")
    else:
        L += [f"- {doc.get('note', 'no document request matched')}", ""]

    L += ["## Session cookies", ""]
    if r["session_cookies"]:
        L += ["| cookie | set by | attributes |", "|---|---|---|"]
        for c in r["session_cookies"]:
            L.append(f"| `{c['name']}` | {c['set_by']} | {c['attributes']} |")
        L.append("")
    else:
        L += ["No cookies were set during the capture.", ""]

    L += ["## Data endpoints (direct-scrape candidates)", ""]
    if r["data_endpoints"]:
        L += ["| method | status | size | url |", "|---|---|---|---|"]
        for d in r["data_endpoints"]:
            L.append(f"| {d['method']} | {d['status']} | {d['size_bytes']} B | {d['url'][:90]} |")
        L.append("")
    else:
        L += ["No JSON/API responses observed (page is likely server-rendered HTML).", ""]

    L += ["## Hosts contacted", "", "| host | requests | bytes | protection |", "|---|---|---|---|"]
    for h in r["hosts"]:
        flag = "⚠️" if h["is_protection"] else ""
        L.append(f"| {h['host']} | {h['requests']} | {h['bytes']} | {flag} |")
    L.append("")

    by_status = ", ".join(f"{k}×{v}" for k, v in r["stats"]["by_status"].items())
    by_type = ", ".join(f"{k}×{v}" for k, v in r["stats"]["by_type"].items())
    L += ["## Statistics", ""]
    L.append(f"- **By status:** {by_status}")
    L.append(f"- **By type:** {by_type}")
    L.append("")

    L += ["## Request timeline", "",
          "| # | +ms | dur | method | status | type | size | host | url |",
          "|---|---|---|---|---|---|---|---|---|"]
    for t in r["timeline"]:
        L.append(
            f"| {t['n']} | {t['offset_ms']:.0f} | {t['time_ms']:.0f} | {t['method']} | "
            f"{t['status']} | {t['type']} | {t['size_bytes']} | {t['host']} | {t['url'][:70]} |"
        )
    L.append("")

    L += ["## Recommendations", ""]
    for rec in r["recommendations"]:
        L.append(f"- {rec}")
    L.append("")

    return "\n".join(L)


# --------------------------------------------------------------------------- orchestration


def analyze_har(har_path: Path) -> dict:
    """Parse one HAR file and return its structured report (first page; multi-page is rare here)."""
    parser = HarParser.from_file(str(har_path))
    if not parser.pages:
        raise ValueError(f"HAR has no pages: {har_path}")
    report = analyze_page(parser.pages[0])
    report["_meta"] = {
        "source_har": har_path.name,
        "har_creator": parser.creator,
        "browser": parser.browser,
    }
    return report


def write_report(report: dict, out_dir: Path, source: Path) -> tuple[Path, Path]:
    """Write ``analysis.json`` + ``analysis.md`` next to the HAR."""
    json_path = out_dir / REPORT_JSON
    md_path = out_dir / REPORT_MD
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(report, source), encoding="utf-8")
    return json_path, md_path


def analyze_har_file(har_path: Path) -> dict:
    """Analyze one HAR and write its report alongside it. Returns the report."""
    report = analyze_har(har_path)
    json_path, md_path = write_report(report, har_path.parent, har_path)
    logger.info(
        "har analyzed",
        target=report["target_url"],
        verdict=report["verdict"],
        protections=[p["vendor"] for p in report["protections"]],
        markdown=str(md_path),
        json=str(json_path),
    )
    return report


def analyze_all_outputs(outputs_dir: Path = OUTPUTS_DIR) -> dict[str, dict]:
    """Analyze every ``outputs/<engine>/<domain>/har.har`` produced by a capture run.

    Reports are keyed by ``"<engine>/<domain>"`` so the playwright and patchright captures of the
    same site stay distinct.
    """
    reports: dict[str, dict] = {}
    if not outputs_dir.exists():
        logger.warning("no outputs dir to analyze", outputs_dir=str(outputs_dir))
        return reports
    for har_path in sorted(outputs_dir.glob(f"*/*/{HAR_NAME}")):
        engine, domain = har_path.parent.parent.name, har_path.parent.name
        try:
            reports[f"{engine}/{domain}"] = analyze_har_file(har_path)
        except Exception:
            logger.exception("failed to analyze har", har=str(har_path))
    if not reports:
        logger.warning("no har files found to analyze", outputs_dir=str(outputs_dir))
    return reports


if __name__ == "__main__":
    if len(sys.argv) > 1:
        analyze_har_file(Path(sys.argv[1]).resolve())
    else:
        analyze_all_outputs()
