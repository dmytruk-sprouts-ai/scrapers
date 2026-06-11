import structlog
import time
import asyncio

logger = structlog.get_logger(__name__)

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

def is_page_blocked_cloudflare(html, url):
    return "<title>Just a moment...</title>" in html


async def wait_for_load_cloudflare_default(
    page,
    *,
    ready_js: str | None = None,
    timeout: float = 25.0,
    poll: float = 0.3,
    wait_for_user_action_if_blocked: bool = False,
):
    return await wait_for_page_load(page, ready_js=ready_js, is_page_blocked=is_page_blocked_cloudflare, timeout=timeout, poll=poll, wait_for_user_action_if_blocked=wait_for_user_action_if_blocked)
    
async def wait_for_page_load(
    page,
    *,
    ready_js: str | None = None,
    is_page_blocked = None,
    timeout: float = 25.0,
    poll: float = 0.3,
    wait_for_user_action_if_blocked: bool = False,
):
    deadline = time.monotonic() + timeout

    warned = False
    blocked = False
    while True:
        if ready_js is not None:
            ready = bool(await page.evaluate(f"() => ({ready_js})"))
            if ready:
                logger.warning("page is ready", url=page.url)
                return  
        
        if is_page_blocked:

            try:
                html = await page.content()
                url = page.url
            except Exception:  # execution context destroyed mid-navigation (e.g. a redirect) — retry
                logger.warning("execution context destroyed mid-navigation, retrying", url=page.url)
                html, url, = None, page.url

            if html:
                blocked = is_page_blocked(html, url)
        
                if blocked and not warned:  # observability — surfaced once, from Python (invisible)
                    warned = True
                    logger.warning("blocked page detected", url=url)
                elif blocked:
                    logger.warning("page is still blocked", url=url, abort_in=deadline-time.monotonic())

        if not blocked:
            logger.warning("page is not blocked", url=page.url)
            return
        
        # Honor the deadline unless we are parked on a challenge for a human to solve.
        if not (wait_for_user_action_if_blocked and blocked) and time.monotonic() >= deadline:
            logger.warning("page did not pass checks in time", url=page.url)
            return
        await asyncio.sleep(poll)