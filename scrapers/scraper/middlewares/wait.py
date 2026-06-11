"""Wait helpers so the detection harness captures a *settled* page, not a half-loaded one.

Two failure modes motivate this (see the spiders in :mod:`detection_check`):

* **async compute on a static URL** — creepjs (``FP ID: Computing...``), browserscan skeleton,
  incolumitas (empty ``#detection-tests``); the page never navigates, the verdict fills in later;
* **post-challenge redirect** — Cloudflare/crunchbase show ``Verification successful. Waiting for
  <host> to respond`` and *then* navigate to the real page, so a capture taken when ``driver.get()``
  returns grabs the redirect "bridge" page instead of the destination.

The strategy is condition-based with a hard deadline: wait until no challenge/transition marker
remains AND the DOM has stopped changing for a few polls, optionally gated on a per-site "verdict
is present" predicate (``ready_js``). If a challenge marker is *stuck* (one we cannot solve), we
give up once the DOM has been static for a long-ish window and capture the challenge page anyway,
rather than hanging until the hard timeout. On timeout nothing is raised — the caller still
captures whatever is on screen, and the analyzer surfaces the blocked/computing state from the HTML.
"""
    

from __future__ import annotations

import asyncio
import time

import structlog
from scrapy_playwright.page import PageMethod

from scraper.spiders._detection_check.analysis import _BLOCK_MARKERS

logger = structlog.get_logger(__name__)

# Challenge interstitials + the redirect "bridge" shown between a solved challenge and the real
# origin. While any of these is on screen we have NOT reached the destination page. Reuses the
# analyzer's block markers (so waiter and analyzer agree) plus a few transition-only phrases.
TRANSITION_MARKERS: tuple[str, ...] = (
    *_BLOCK_MARKERS,
    "verification successful. waiting for",  # Cloudflare -> origin redirect bridge (crunchbase)
    "checking your browser",
    "challenge-running",
)

# A normal page is "settled" after its DOM size has been unchanged for STABLE_POLLS polls. If a
# transition marker is stuck, we capture the challenge page once it has been static for STUCK_POLLS.
STABLE_POLLS = 3
STUCK_POLLS = 20

# Settle outcomes (returned by the waiters and propagated to the response). Distinguishing them
# matters: a capture can be clean, blocked by a challenge, or one of two distinct timeouts.
SETTLED = "settled"  # clean: no marker, DOM stable, ready predicate satisfied
BLOCKED = "blocked"  # a challenge/transition marker was still present (captured anyway)
TIMEOUT_UNSTABLE = "timeout_unstable"    # deadline hit, DOM never stopped changing (didn't render)
TIMEOUT_NOT_READY = "timeout_not_ready"  # deadline hit, DOM stable but ready_js never became true


def _timeout_status(blocked: bool, stable: int) -> str:
    """Classify why a settle hit its deadline without returning SETTLED."""
    if blocked:
        return BLOCKED
    if stable < STABLE_POLLS:
        return TIMEOUT_UNSTABLE
    return TIMEOUT_NOT_READY  # stable but the per-site ready_js predicate never passed


def wait_until_settled(
    driver, *, ready_js: str | None = None, timeout: float = 25.0, poll: float = 0.3
) -> str:
    """Selenium: block until the page is settled. Returns a settle-outcome constant
    (``SETTLED`` / ``BLOCKED`` / ``TIMEOUT_UNSTABLE`` / ``TIMEOUT_NOT_READY``).

    Never raises — on a non-settled outcome the caller still captures ``page_source`` so the
    analyzer can report the (blocked / still-computing) state from the saved HTML. ``ready_js`` is
    an optional boolean JS *expression* that must be truthy for the page to count as ready.
    """
    deadline = time.monotonic() + timeout
    last_state = None
    stable = 0
    warned = False
    last_blocked = False
    while time.monotonic() < deadline:
        try:
            if driver.execute_script("return document.readyState") != "complete":
                time.sleep(poll)
                continue
            html = driver.page_source
            url = driver.current_url
            ready = bool(driver.execute_script(f"return ({ready_js});")) if ready_js else True
        except Exception:  # transient (mid-navigation) — retry until the deadline
            logger.warning("context destroyed mid-navigation, retrying", url=_safe_url(driver))
            time.sleep(poll)
            continue

        low = html.lower()
        marker = next((m for m in TRANSITION_MARKERS if m in low), None)
        blocked = marker is not None
        last_blocked = blocked
        if blocked and not warned:  # observability: surface the block once in the Scrapy log
            warned = True
            logger.warning("transition marker detected", marker=marker, url=url)
        # Compare DOM *size* (robust to same-width text churn like a ticking clock), plus the URL so
        # a redirect resets stability and we never settle on the bridge page.
        state = (len(html), url)
        if state == last_state:
            stable += 1
        else:
            stable = 0
            last_state = state

        if not blocked and ready and stable >= STABLE_POLLS:
            return SETTLED
        if blocked and stable >= STUCK_POLLS:  # stuck on a challenge — capture it, don't hang
            return BLOCKED
        time.sleep(poll)

    status = _timeout_status(last_blocked, stable)
    logger.warning("page did not settle before timeout", url=_safe_url(driver), status=status)
    return status


def _safe_url(driver) -> str:
    try:
        return driver.current_url
    except Exception:
        return "?"


# Navigation-response status codes that typically carry an anti-bot challenge/interstitial.
_CHALLENGE_STATUSES = {403, 429, 503}


def log_challenge_response(response) -> None:
    """Playwright ``response`` event handler: log Cloudflare/anti-bot challenges to the Scrapy log
    by inspecting the HTTP status + headers of the main-frame navigation, NOT by emitting anything
    into the page. This is invisible to the site — unlike an in-page ``console.warn`` (which runs
    through the page's own, possibly-hooked, ``console`` and would leak our internal tag).

    Wire in via ``meta["playwright_page_event_handlers"] = {"response": log_challenge_response}``.
    """
    try:
        if not response.request.is_navigation_request():
            return  # ignore subresources (images/xhr/etc.) — only the document matters
        headers = response.headers  # already lower-cased by Playwright
        cf_mitigated = headers.get("cf-mitigated")
        if cf_mitigated or response.status in _CHALLENGE_STATUSES:
            logger.warning(
                "challenge response",
                url=response.url,
                status=response.status,
                cf_mitigated=cf_mitigated,
                server=headers.get("server"),
            )
    except Exception:  # an event handler must never break the download
        logger.debug("could not inspect response for challenge", exc_info=True)


async def settle_page(
    page,
    *,
    ready_js: str | None = None,
    timeout: float = 25.0,
    poll: float = 0.3,
    wait_for_user_if_blocked: bool = False,
) -> str:
    """Playwright settle loop, run entirely in our process — zero in-page footprint.

    Passed as a *callable* ``PageMethod`` (see :func:`settle_page_methods`); scrapy-playwright
    invokes it as ``await settle_page(page, **kwargs)`` after navigation and before it captures the
    content. Unlike an in-page ``wait_for_function`` (which polls inside the page's main world and
    leaves ``window.*`` state behind), this polls ``page.content()`` — an out-of-process DOM
    serialization the site cannot observe — for marker-absence + DOM-size stability, optionally
    gated on ``ready_js``. A detected challenge is logged to the Scrapy log. Returns a settle
    outcome (``SETTLED`` / ``BLOCKED`` / ``TIMEOUT_UNSTABLE`` / ``TIMEOUT_NOT_READY``).

    With ``wait_for_user_if_blocked`` the loop ignores the deadline *while a marker is present*, so
    a challenge can be solved in the headful window; it continues once the marker clears.
    """
    deadline = time.monotonic() + timeout
    last_state = None
    stable = 0
    warned = False
    last_blocked = False
    while True:
        try:
            html = await page.content()
            url = page.url
            ready = bool(await page.evaluate(f"() => ({ready_js})")) if ready_js else True
        except Exception:  # execution context destroyed mid-navigation (e.g. a redirect) — retry
            logger.warning("execution context destroyed mid-navigation, retrying", url=page.url)
            html, url, ready = None, page.url, False

        if html is not None:
            low = html.lower()  # page.content() includes <head>/<title>, where CF puts its marker
            marker = next((m for m in TRANSITION_MARKERS if m in low), None)
            last_blocked = blocked = marker is not None
            if blocked and not warned:  # observability — surfaced once, from Python (invisible)
                warned = True
                logger.warning("transition marker detected", marker=marker, url=url)

            # DOM *size* (robust to same-width churn like a clock) + URL (a redirect resets
            # stability so we never settle on the bridge page).
            state = (len(html), url)
            if state == last_state:
                stable += 1
            else:
                stable = 0
                last_state = state

            if not blocked and ready and stable >= STABLE_POLLS:
                return SETTLED
            if blocked and not wait_for_user_if_blocked and stable >= STUCK_POLLS:
                return BLOCKED  # stuck on a challenge we won't solve — capture it, don't hang

        # Honor the deadline unless we are parked on a challenge for a human to solve.
        if not (wait_for_user_if_blocked and last_blocked) and time.monotonic() >= deadline:
            status = _timeout_status(last_blocked, stable)
            logger.warning("page did not settle before timeout", url=url, status=status)
            return status
        await asyncio.sleep(poll)


def settle_page_methods(
    *, ready_js: str | None = None, timeout: float = 25.0, wait_for_user_if_blocked: bool = False
) -> list[PageMethod]:
    """Wrap :func:`settle_page` as a single callable ``PageMethod`` for scrapy-playwright."""
    return [
        PageMethod(
            settle_page,
            ready_js=ready_js,
            timeout=timeout,
            wait_for_user_if_blocked=wait_for_user_if_blocked,
        )
    ]
