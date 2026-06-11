"""Colored Scrapy logging via Rich.

Scrapy logs through the stdlib :mod:`logging` module, so we don't need structlog — installing a
single :class:`rich.logging.RichHandler` on the root logger colorizes every log line (Scrapy core,
middlewares, pipelines and the spiders) with level colors, a timestamp and pretty tracebacks.

``settings.py`` calls :func:`install_rich_logging` at import time and sets ``LOG_ENABLED = False``,
so Scrapy installs a no-op ``NullHandler`` instead of its own plain ``StreamHandler`` — leaving the
Rich handler as the sole owner of the root logger (no duplicated lines).

Color is auto-disabled when stderr is not a TTY (e.g. captured to ``run.log`` or piped), so the file
output stays clean plain text while an interactive ``just crawl`` is colored.
"""

from __future__ import annotations

import logging

from rich.console import Console, Group
from rich.logging import RichHandler
from rich.syntax import Syntax
from rich.theme import Theme

# Distinct, readable colors per level. Rich looks these up as ``logging.level.<name>`` styles.
_THEME = Theme(
    {
        "logging.level.debug": "dim cyan",
        "logging.level.info": "green",
        "logging.level.warning": "yellow",
        "logging.level.error": "bold red",
        "logging.level.critical": "bold white on red",
    }
)

_installed = False


class _PrettyRichHandler(RichHandler):
    """RichHandler that syntax-highlights the Python structures Scrapy logs.

    Scrapy logs structures (versions, overridden settings, enabled middlewares, the final stats
    dump, …) as a label line followed by a ``pprint``-formatted dict/list. We keep that text as-is
    (no re-parsing) and run it through Pygments via :class:`rich.syntax.Syntax`, so keys, strings,
    numbers and booleans get consistent colors instead of a flat blob of text.
    """

    def render_message(self, record, message):  # type: ignore[override]
        label, sep, payload = message.partition("\n")
        if sep and payload.lstrip()[:1] in "{[(":
            head = super().render_message(record, label)
            body = Syntax(payload, "python", background_color="default", word_wrap=True)
            return Group(head, body)
        return super().render_message(record, message)


def install_rich_logging(level: str = "INFO") -> None:
    """Install a Rich handler on the root logger. Idempotent (safe to call more than once)."""
    global _installed
    if _installed:
        return

    # stderr keeps logs off stdout (where Scrapy feeds / the sample runner's marker line live).
    # Console auto-detects a TTY and drops color when the stream is redirected to a file or pipe.
    console = Console(stderr=True, theme=_THEME)
    handler = _PrettyRichHandler(
        console=console,
        level=level,
        show_time=True,
        show_level=True,
        show_path=False,  # the originating module is noise; the logger name is more useful
        markup=False,  # log messages contain unescaped '[' (item reprs, selectors) — don't parse it
        rich_tracebacks=True,
        log_time_format="[%H:%M:%S]",
    )
    # Prepend the logger name (e.g. "scrapy.core.engine") so it's clear which component spoke.
    handler.setFormatter(logging.Formatter("%(name)s  %(message)s"))

    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(level)
    _installed = True
