#!/usr/bin/env python3
"""Probe the gprocurement Cloudflare-bypass flag.

The announcement SPA calls ``api/v1/cfturnstile/bypasscloudflare?systemName=<ENV>`` on load and
only renders the Turnstile widget when the reply is ``bypassCloudflareStatus == "N"`` (= enforce).
Any other value (e.g. ``"Y"``) means the app skips Turnstile entirely and fires the listing with no
``X-Announcement-Token`` — i.e. the whole listing is reachable with plain curl_cffi, no browser.

This is a server-side ops toggle keyed per ``systemName`` (PROD/DEV/…) that can flip without notice,
so it's worth polling before a run: if it's open, skip the Playwright/Turnstile bootstrap.

Run::

    ./check_bypass.py                 # checks systemName=PROD
    ./check_bypass.py -s PROD DEV     # check several environments
    ./check_bypass.py --json          # machine-readable line per env

Exit code: 0 = bypass OPEN (no Turnstile), 1 = ENFORCED ("N"), 2 = error/unknown. With multiple
envs the code reflects the most permissive result seen (0 if any env is open).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from curl_cffi import requests

# Reuse the canonical Chrome profile (same UA / impersonation target as the spiders) so this probe
# presents the same identity. scrapers/ is three levels up from this file.
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from scraper.browser_profile import IMPERSONATE, navigation_headers  # noqa: E402

URL = (
    "https://process5.gprocurement.go.th"
    "/egp-atpj27-service/pb/a-egp-allt-project/api/v1/cfturnstile/bypasscloudflare"
)


def _headers() -> dict[str, str]:
    # The SPA sends this as a plain JSON XHR; reshape the navigation profile to that form.
    h = navigation_headers()
    h.pop("upgrade-insecure-requests", None)
    h.pop("sec-fetch-user", None)
    h.update(
        {
            "accept": "application/json, text/plain, */*",
            "content-type": "application/json",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "https://process5.gprocurement.go.th/egp-agpc01-web/announcement?keywordSearch=",
        }
    )
    return h


def check(system_name: str, timeout: float = 30.0) -> dict:
    """Probe one environment. Returns a result dict; never raises."""
    result: dict = {"systemName": system_name}
    try:
        resp = requests.get(
            URL,
            params={"systemName": system_name},
            headers=_headers(),
            impersonate=IMPERSONATE,
            timeout=timeout,
        )
        result["http_status"] = resp.status_code
        data = resp.json().get("data") or {}
        status = data.get("bypassCloudflareStatus")
        result["bypassCloudflareStatus"] = status
        # "N" = do NOT bypass (Turnstile enforced); anything else = open.
        if status == "N":
            result["state"] = "enforced"
            result["open"] = False
        elif status is None:
            result["state"] = "unknown"
            result["open"] = None
        else:
            result["state"] = "open"
            result["open"] = True
    except Exception as exc:  # network/JSON/TLS — report, don't crash
        result["error"] = f"{type(exc).__name__}: {exc}"
        result["state"] = "error"
        result["open"] = None
    return result


def _emoji(state: str) -> str:
    return {"open": "🟢", "enforced": "🔴", "unknown": "🟡", "error": "💥"}.get(state, "❓")


def main() -> int:
    ap = argparse.ArgumentParser(description="Probe the gprocurement Cloudflare-bypass flag.")
    ap.add_argument(
        "-s",
        "--system",
        nargs="+",
        default=["PROD"],
        metavar="ENV",
        help="systemName(s) to check (default: PROD).",
    )
    ap.add_argument("--json", action="store_true", help="Emit one JSON object per env.")
    ap.add_argument("--timeout", type=float, default=30.0, help="Per-request timeout seconds.")
    args = ap.parse_args()

    results = [check(name, timeout=args.timeout) for name in args.system]

    for r in results:
        if args.json:
            print(json.dumps(r))
            continue
        state = r["state"]
        line = f"{_emoji(state)} {r['systemName']:6s} {state.upper()}"
        if "bypassCloudflareStatus" in r:
            line += f"  (bypassCloudflareStatus={r['bypassCloudflareStatus']!r}, http={r.get('http_status')})"
        if state == "open":
            line += "  → Turnstile SKIPPED — listing reachable via curl_cffi, no browser"
        elif state == "enforced":
            line += "  → Turnstile required — browser/solver needed for the listing"
        if "error" in r:
            line += f"  {r['error']}"
        print(line)

    # Exit code reflects the most permissive result (0 if any env is open).
    if any(r["open"] is True for r in results):
        return 0
    if any(r["open"] is False for r in results):
        return 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
