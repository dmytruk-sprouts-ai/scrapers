"""Sticky-session proxies shared between the Playwright leg and the curl_cffi leg.

Cloudflare binds the cf_clearance it issues to the IP that solved the challenge. Because we
hand the browser's cookies to curl_cffi, the curl_cffi replay MUST exit from the *same* IP —
otherwise the clearance is rejected and the challenge re-triggers.

Each line below is one swiftproxy credential whose username carries a distinct ``sid_<n>``
session id. swiftproxy pins a session id to one exit IP for the ``time_10`` window (10 min), so
reusing the same credential across both legs guarantees the same egress IP. We therefore pick a
single :class:`Proxy` per crawl and thread it through every request in the chain.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from urllib.parse import quote

# host:port:username:password — usernames differ only by sid, i.e. distinct sticky sessions.
_RAW_PROXIES = """

"""


@dataclass(frozen=True)
class Proxy:
    """One sticky-session proxy, rendered for either consumer."""

    host: str
    port: int
    username: str
    password: str

    @property
    def url(self) -> str:
        """``http://user:pass@host:port`` for Scrapy/curl_cffi (``request.meta['proxy']``).

        Credentials are URL-encoded so any reserved characters in the swiftproxy username
        (``_``, digits — currently safe, but encoded defensively) cannot corrupt the authority.
        """
        return (
            f"http://{quote(self.username, safe='')}:{quote(self.password, safe='')}"
            f"@{self.host}:{self.port}"
        )

    @property
    def playwright(self) -> dict[str, str]:
        """Per-context proxy dict for Playwright (``playwright_context_kwargs['proxy']``)."""
        return {
            "server": f"http://{self.host}:{self.port}",
            "username": self.username,
            "password": self.password,
        }


def _parse(line: str) -> Proxy:
    host, port, username, password = line.split(":")
    return Proxy(host=host, port=int(port), username=username, password=password)


PROXIES: list[Proxy] = [_parse(line) for line in _RAW_PROXIES.split() if line.strip()]


def pick_proxy() -> Proxy | None:
    """One proxy for the whole crawl — same egress IP across the Playwright + curl_cffi legs."""
    return random.choice(PROXIES) if PROXIES else None
