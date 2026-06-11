"""Canonical browser request profile, shared across every scraper.

The curl_cffi-based scrapers must present the *same* identity as the real
Chrome we benchmark against: the same TLS/HTTP2 impersonation target and the
same request headers (values **and** order). Defining that here — once — keeps
every spider consistent and gives the ``httpbin`` consistency spider a single
source of truth to validate against.

Captured from Chrome 148 on Linux (X11). When bumping the targeted Chrome
version, update ``CHROME_VERSION`` / ``PLATFORM`` (and ``IMPERSONATE`` if a
newer curl_cffi target is needed); the ``httpbin`` spider compares this profile
against a live browser and will flag any drift.
"""

from __future__ import annotations

# curl_cffi impersonation target — drives the TLS ClientHello and HTTP/2
# settings/pseudo-header order. Header *values* are supplied explicitly below
# (with default_headers=False) so they cannot fall out of sync with this.
IMPERSONATE = "chrome"

# The User-Agent and the Sec-CH-UA client hints must all agree on one Chrome
# major version and one platform, or the mismatch is itself a tell.
CHROME_VERSION = "148"
PLATFORM = "Linux"

USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    f"(KHTML, like Gecko) Chrome/{CHROME_VERSION}.0.0.0 Safari/537.36"
)

SEC_CH_UA = (
    f'"Chromium";v="{CHROME_VERSION}", '
    f'"Google Chrome";v="{CHROME_VERSION}", '
    '"Not/A)Brand";v="99"'
)

# Headers for a top-level document navigation, in Chrome's wire order. ``Host``
# is added by curl_cffi from the URL; per-connection/server headers (Cookie,
# X-Amzn-Trace-Id, …) are intentionally absent. Insertion order is significant:
# it is replayed verbatim, so keep it as captured.
_NAVIGATION_HEADERS: dict[str, str] = {
    "sec-ch-ua": SEC_CH_UA,
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": f'"{PLATFORM}"',
    "upgrade-insecure-requests": "1",
    "user-agent": USER_AGENT,
    "accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8,"
        "application/signed-exchange;v=b3;q=0.7"
    ),
    "sec-fetch-site": "none",
    "sec-fetch-mode": "navigate",
    "sec-fetch-user": "?1",
    "sec-fetch-dest": "document",
    "accept-encoding": "gzip, deflate, br, zstd",
    "accept-language": "en-US",
    "priority": "u=0, i",
}


def navigation_headers() -> dict[str, str]:
    """A fresh copy of the canonical navigation headers (safe to mutate)."""
    return dict(_NAVIGATION_HEADERS)
