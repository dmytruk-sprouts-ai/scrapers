"""Select the Playwright backend (vanilla ``playwright`` vs. ``patchright``) for a harness run.

``scrapy_playwright`` hardcodes ``from playwright.async_api import ...`` and is a single module
imported once per process; it also does ``isinstance(page, Page)`` against those imported symbols.
So to drive it with `patchright <https://github.com/Kaliiiiiiiiii-Vinyzu/patchright>`_ — a patched
Playwright that closes the CDP-level automation leaks (``Runtime.enable``, main-world execution)
that vanilla Playwright exposes to Cloudflare et al. — we alias ``patchright`` *as* ``playwright``
in ``sys.modules`` **before** ``scrapy_playwright`` is first imported. Then both the objects and the
type symbols are patchright's, so the isinstance checks pass and nothing else has to change.

The alias is process-global (one backend per process), so the engine is chosen **per run** via the
``SCRAPER_PW_ENGINE`` env var rather than per spider. Harness entrypoints namespace their output by
:data:`ENGINE`, so running once per engine leaves the ``outputs/playwright/`` and
``outputs/patchright/`` trees side by side.

Usage — first import line of each Playwright harness entrypoint::

    from scraper.playwright_engine import ENGINE, install_engine
    install_engine()  # must run before anything imports scrapy_playwright
"""

from __future__ import annotations

import importlib
import os
import sys

# Which backend this process drives. Default keeps the existing vanilla-Playwright behaviour.
ENGINE = os.environ.get("SCRAPER_PW_ENGINE", "playwright")

# Submodules scrapy_playwright imports from ``playwright`` (handler.py, _utils.py, headers.py). The
# parent ``_impl`` is included so ``playwright._impl._errors`` resolves cleanly.
_ALIASED_SUBMODULES = ("async_api", "_impl", "_impl._errors")


def install_engine() -> str:
    """Alias ``patchright`` as ``playwright`` when ``SCRAPER_PW_ENGINE=patchright``; else no-op.

    Returns the active engine name. Idempotent and safe to call multiple times, but it MUST run
    before ``scrapy_playwright`` is imported anywhere in the process — otherwise that module will
    have already bound the vanilla ``playwright`` classes and the swap won't take.
    """
    if ENGINE == "patchright":
        import patchright  # noqa: F401  (presence proves the dependency is installed)

        sys.modules["playwright"] = patchright
        for sub in _ALIASED_SUBMODULES:
            sys.modules[f"playwright.{sub}"] = importlib.import_module(f"patchright.{sub}")
    return ENGINE
