import collections
import json
from typing import Any

import scrapy

from scraper.browser_profile import IMPERSONATE, navigation_headers


async def handler_request(event: str, r, hc: dict[str, Any]):
    hc[event].append({"r": r, "method": r.method, "url": r.url, "headers": r.headers})


async def handler_response(
    event: str, r, hc: dict[str, Any]
):  # 3xx redirects / failed responses have no body
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


async def populate_body(response):  # 3xx redirects / failed responses have no body
    # playwright page musdt be present
    page = response.meta["playwright_page"]

    for entry in response.meta["handlers_context"].get("response", []):
        try:
            entry["body"] = await entry["r"].body()
        except Exception:
            entry["body"] = None

    await page.close()


def _value_diff(a: str, b: str) -> str:
    """One-line summary of where two header values diverge.

    Points at the first differing character so long values (Accept,
    Sec-Ch-Ua, User-Agent) don't have to be eyeballed.
    """
    i = next((n for n, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    if i == len(a) == len(b):
        return "identical"
    shared = a[:i]
    return (
        f"first differ at index {i} after {shared!r}: "
        f"browser→{a[i : i + 12]!r} candidate→{b[i : i + 12]!r}"
    )


def _list_diff(a: list, b: list) -> str:
    """Summarise how two ordered lists differ.

    Reports items present on only one side, and — if the membership is the
    same but the order isn't — flags the reorder (order is itself a tell for
    cipher suites, extensions and supported groups).
    """
    sa, sb = set(map(str, a)), set(map(str, b))
    only_browser = [x for x in a if str(x) not in sb]
    only_candidate = [x for x in b if str(x) not in sa]
    parts: list[str] = []
    if only_browser:
        parts.append(f"only in browser: {only_browser}")
    if only_candidate:
        parts.append(f"only in candidate: {only_candidate}")
    if not parts:
        parts.append("same items, order differs")
    return "; ".join(parts)


def _explain_diff(a, b) -> str:
    """Dispatch to a list- or string-aware diff explanation."""
    if isinstance(a, list) and isinstance(b, list):
        return _list_diff(a, b)
    return _value_diff(str(a), str(b))


def _diff_fields(
    ref: dict,
    cand: dict,
    *,
    title: str,
    omit_label: str,
    extra_label: str,
    raise_on_diff: bool,
) -> list[str]:
    """Compare two flat dicts and render a grouped, readable report.

    Values may be strings or lists. Groups problems into three buckets
    (present-only-in-reference, present-only-in-candidate, value mismatch)
    and raises ValueError with the rendered report when raise_on_diff is set.
    """
    missing: list[str] = []
    extra: list[str] = []
    value: list[str] = []

    for key in sorted(set(ref) | set(cand)):
        in_ref = key in ref
        in_cand = key in cand
        if in_ref and not in_cand:
            missing.append(f"    - {key}: {ref[key]!r}")
        elif in_cand and not in_ref:
            extra.append(f"    - {key}: {cand[key]!r}")
        elif ref[key] != cand[key]:
            value.append(
                f"    - {key}:\n"
                f"        browser   = {ref[key]!r}\n"
                f"        candidate = {cand[key]!r}\n"
                f"        diff      = {_explain_diff(ref[key], cand[key])}"
            )

    sections: list[str] = []
    if missing:
        sections.append(f"  {omit_label}:\n" + "\n".join(missing))
    if extra:
        sections.append(f"  {extra_label}:\n" + "\n".join(extra))
    if value:
        sections.append("  value mismatch:\n" + "\n".join(value))

    problems = missing + extra + value
    if problems and raise_on_diff:
        count = len(problems)
        raise ValueError(
            f"{title} ({count} problem{'s' if count != 1 else ''}):\n"
            + "\n".join(sections)
        )
    return problems


def _normalize(headers: dict, ignore: frozenset) -> dict:
    """Coerce a header payload into a flat {lowercased-name: value} dict.

    Unwraps httpbin-style ``{"headers": {...}}`` envelopes, lowercases header
    names so comparison is case-insensitive, and drops anything in ``ignore``
    (which is expected to be lowercased already).
    """
    if isinstance(headers.get("headers"), dict):
        headers = headers["headers"]
    return {
        name.lower(): value
        for name, value in headers.items()
        if name.lower() not in ignore
    }


DEFAULT_IGNORE = frozenset(
    {
        "host",
        "content-length",
        "connection",
        # Request cache directives: present only when the cache is bypassed (hard
        # reload, DevTools "disable cache", or Playwright HAR recording). They track
        # cache state, not browser identity, so they are noise for a consistency
        # check — real Chrome omits them on a normal navigation.
        "pragma",
        "cache-control",
        "x-amzn-trace-id",  # httpbin / AWS
        "x-forwarded-for",
        "x-forwarded-proto",
        "x-forwarded-port",
        "x-forwarded-host",
        "x-real-ip",
        "cf-connecting-ip",
        "cf-ray",
        "cdn-loop",
        "forwarded",
        "via",
    }
)


def compare_headers(
    reference: dict,
    candidate: dict,
    ignore: frozenset = DEFAULT_IGNORE,
    raise_on_diff: bool = True,
) -> list[str]:
    """
    Compare candidate headers against a reference (the real browser).

    Returns a list of human-readable problems. If raise_on_diff is True and
    any problem is found, raises HeaderMismatch instead of returning.

    Three failure modes are reported:
      - missing : header the real browser sends but the candidate omits
      - extra   : header the candidate sends that the browser does not (a tell)
      - value   : header present in both but with a different value
    """
    return _diff_fields(
        _normalize(reference, ignore),
        _normalize(candidate, ignore),
        title="Header-consistency check failed",
        omit_label="missing (browser sends, candidate omits)",
        extra_label="extra (candidate sends, browser does not — a tell)",
        raise_on_diff=raise_on_diff,
    )


def assert_headers_match(reference: dict, candidate: dict, **kw) -> None:
    """Convenience wrapper: raise HeaderMismatch unless headers match."""
    compare_headers(reference, candidate, raise_on_diff=True, **kw)


def _extension_field(extensions: list, name_prefix: str, field: str):
    """Pull a field out of the named TLS extension (matched by name prefix)."""
    for ext in extensions or []:
        if ext.get("name", "").startswith(name_prefix):
            return ext.get(field)
    return None


def _h2_frame(http2: dict, frame_type: str) -> dict:
    for frame in http2.get("sent_frames", []) or []:
        if frame.get("frame_type") == frame_type:
            return frame
    return {}


def _h2_headers(http2: dict, ignore: frozenset) -> dict:
    """Parse the h2 HEADERS frame into an ordered {name: value} dict.

    Header *order* is a fingerprint (Chrome does not randomize it) and header
    *values* (user-agent, sec-ch-ua, …) must match the real browser, so we keep
    both. Names are lowercased; anything in ``ignore`` is dropped. Insertion
    order is preserved, so iterating the dict yields the wire order.
    """
    out: dict[str, str] = {}
    for line in _h2_frame(http2, "HEADERS").get("headers") or []:
        # ":method: GET" -> (":method", "GET"); "user-agent: X" -> ("user-agent", "X")
        if line.startswith(":"):
            name, _, value = line[1:].partition(": ")
            name = ":" + name
        else:
            name, _, value = line.partition(": ")
        name = name.strip().lower()
        if name.lstrip(":") in ignore:
            continue
        out[name] = value
    return out


def _degrease(items: list | None) -> list | None:
    """Drop GREASE placeholders from a TLS list.

    Chrome emits a GREASE entry (RFC 8701) in its ciphers, extensions,
    supported groups and supported versions, and *randomizes its value on
    every handshake* (0x0a0a, 0x1a1a, …). Comparing it would flag every
    connection as different, so it is stripped before comparison.
    """
    if items is None:
        return None
    return [x for x in items if "GREASE" not in str(x)]


def _flatten_fingerprint(payload: dict) -> dict:
    """Extract the stable, fingerprint-defining fields from a tls.peet.ws payload.

    Drops everything that varies per connection — both the obvious noise
    (client_random, session_id, key_share blobs, ECH data, ip/ports, TCP
    seq/ack) and the two things Chrome itself randomizes every handshake:
    GREASE values (stripped) and TLS extension *order* (compared as a set).

    Notably absent: ja3 / ja3_hash. JA3 hashes the extensions in wire order,
    so Chrome's per-handshake shuffle makes it differ every time — it is not a
    usable target. JA4 sorts the extensions and ignores GREASE, so it is the
    stable replacement and is what we compare instead.
    """
    tls = payload.get("tls", {}) or {}
    http2 = payload.get("http2", {}) or {}
    exts = tls.get("extensions", []) or []

    extension_names = _degrease([e.get("name") for e in exts]) or None

    flat = {
        # headline fingerprints — the actual pass/fail signals
        "ja4": tls.get("ja4"),
        "peetprint_hash": tls.get("peetprint_hash"),
        "akamai_fingerprint_hash": http2.get("akamai_fingerprint_hash"),
        # detail strings — explain *why* a headline hash differs
        "ja4_r": tls.get("ja4_r"),
        "peetprint": tls.get("peetprint"),
        "akamai_fingerprint": http2.get("akamai_fingerprint"),
        "tls_version_record": tls.get("tls_version_record"),
        "tls_version_negotiated": tls.get("tls_version_negotiated"),
        # GREASE-stripped lists; cipher/group/version order is stable in Chrome
        "ciphers": _degrease(tls.get("ciphers")),
        "supported_groups": _degrease(
            _extension_field(exts, "supported_groups", "supported_groups")
        ),
        "supported_versions": _degrease(
            _extension_field(exts, "supported_versions", "versions")
        ),
        "signature_algorithms": _extension_field(
            exts, "signature_algorithms", "signature_algorithms"
        ),
        "alpn": _extension_field(
            exts, "application_layer_protocol_negotiation", "protocols"
        ),
        # extension order is randomized by Chrome -> compare the set, not order
        "extension_set": sorted(extension_names) if extension_names else None,
        "h2_settings": _h2_frame(http2, "SETTINGS").get("settings"),
        # NB: h2 request headers (order + values) are added in compare_tls,
        # which has both payloads and can isolate pure reordering from membership.
    }
    # Drop absent fields so they don't show up as spurious mismatches.
    return {k: v for k, v in flat.items() if v is not None}


def compare_tls(
    reference: dict,
    candidate: dict,
    ignore: frozenset = DEFAULT_IGNORE,
    raise_on_diff: bool = True,
) -> list[str]:
    """Compare a candidate's TLS/HTTP2 fingerprint against the real browser's.

    Both arguments are raw tls.peet.ws /api/all payloads. Returns a list of
    human-readable problems (or raises ValueError when raise_on_diff is set).
    """
    ref = _flatten_fingerprint(reference)
    cand = _flatten_fingerprint(candidate)

    # HTTP/2 request headers carried in the HEADERS frame: compare each value
    # individually (so a wrong user-agent / sec-ch-ua surfaces as its own diff)
    # and, separately, the order of the headers the two sides share (a pure
    # reorder is a tell on its own; membership diffs are already reported per
    # header, so restricting to shared headers avoids double-counting them).
    ref_h = _h2_headers(reference.get("http2", {}) or {}, ignore)
    cand_h = _h2_headers(candidate.get("http2", {}) or {}, ignore)
    for name, val in ref_h.items():
        ref[f"h2 header[{name}]"] = val
    for name, val in cand_h.items():
        cand[f"h2 header[{name}]"] = val
    shared = set(ref_h) & set(cand_h)
    ref["h2_header_order"] = [n for n in ref_h if n in shared]
    cand["h2_header_order"] = [n for n in cand_h if n in shared]

    return _diff_fields(
        ref,
        cand,
        title="TLS/HTTP2 fingerprint check failed",
        omit_label="missing (present for browser, absent for candidate)",
        extra_label="extra (present for candidate, absent for browser)",
        raise_on_diff=raise_on_diff,
    )


def assert_tls_match(reference: dict, candidate: dict, **kw) -> None:
    """Convenience wrapper: raise unless the TLS/HTTP2 fingerprint matches."""
    compare_tls(reference, candidate, raise_on_diff=True, **kw)


class HTTPBinHeadersSpider(scrapy.Spider):
    name = "httpbin"

    @classmethod
    def update_settings(cls, settings):
        playwright = {
            "PLAYWRIGHT_BROWSER_TYPE": "chromium",
            "PLAYWRIGHT_LAUNCH_OPTIONS": {
                "executable_path": "/usr/bin/google-chrome",
                "headless": False,
                "channel": "chrome",
                # Kept for parity with the default variant so the A/B isolates the engine. patchright
                # also manages navigator.webdriver itself; this arg can be dropped to test which scores
                # cleaner.
                "args": ["--disable-blink-features=AutomationControlled"],
            },
            "PLAYWRIGHT_CONTEXTS": {
                "default": {"no_viewport": True, "locale": "en-US"}
            },
            "PLAYWRIGHT_PROCESS_REQUEST_HEADERS": None,
        }
        handlers = {
            "DOWNLOAD_HANDLERS": {
                "https": "scraper.handlers.HybridDownloadHandler",
                "http": "scraper.handlers.HybridDownloadHandler",
            },
        }

        super().update_settings(settings)  # type: ignore
        settings.setdict(
            {
                "CONCURRENT_REQUESTS_PER_DOMAIN": 1,
                "HTTPERROR_ALLOW_ALL": True,
                "ROBOTSTXT_OBEY": False,
                "RETRY_ENABLED": False,
                **playwright,
                **handlers,
            },
            priority="spider",
        )

    async def start(self):
        # must be initialized here, to be able to mutate in handlers
        hc = collections.defaultdict(list)
        meta = {
            "playwright": True,
            "playwright_include_page": True,  # needed to await page events
            "playwright_page_event_handlers": {
                "requestfinished": lambda request: handler_request(
                    "requestfinished", request, hc
                ),
                "requestfailed": lambda request: handler_request(
                    "requestfailed", request, hc
                ),
                "request": lambda request: handler_request("request", request, hc),
                "response": lambda response: handler_response("response", response, hc),
            },
            "handlers_context": hc,
        }
        yield scrapy.Request(
            "https://httpbin.org/headers", callback=self.parse_playwright, meta=meta
        )
        yield scrapy.Request(
            "https://tls.peet.ws/api/all", callback=self.parse_playwright, meta=meta
        )

    def parse_playwright(self, response):
        body = response.selector.xpath("//pre/text()").get()
        # Send our prepared, canonical Chrome profile (see scraper.browser_profile)
        # and turn off curl_cffi's default headers, so the candidate presents
        # exactly that profile rather than curl_cffi's (different-version,
        # different-OS) defaults. This spider's job is to prove the profile still
        # matches a real browser.
        impersonate_meta = {
            "impersonate": IMPERSONATE,
            "impersonate_args": {"default_headers": False},
            # Stop RefererMiddleware adding a Referer the real navigation lacked.
            "referrer_policy": "no-referrer",
        }
        print("-" * 80)
        print("playwright")
        print("-" * 80)
        print(response.url)
        loaded = json.loads(body)
        print(json.dumps(loaded, indent=4))

        replay_headers = navigation_headers()

        if "httpbin.org" in response.url:
            meta = {**impersonate_meta, "palywright_headers": loaded}
            yield scrapy.Request(
                "https://httpbin.org/headers",
                callback=self.parse_cffi,
                dont_filter=True,
                headers=replay_headers,
                meta=meta,
            )
        else:
            meta = {**impersonate_meta, "palywright_tls_handshake": loaded}
            yield scrapy.Request(
                "https://tls.peet.ws/api/all",
                callback=self.parse_cffi,
                dont_filter=True,
                headers=replay_headers,
                meta=meta,
            )

    def parse_cffi(self, response):
        print("-" * 80)
        print("cffi")
        print("-" * 80)
        loaded = response.json()
        print(response.url)
        print(json.dumps(loaded, indent=4))
        if "httpbin.org" in response.url:
            compare_headers(
                response.meta["palywright_headers"], loaded, raise_on_diff=True
            )
        else:
            compare_tls(
                response.meta["palywright_tls_handshake"], loaded, raise_on_diff=True
            )
