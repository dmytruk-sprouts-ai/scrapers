"""Shared pytest fixtures for offline spider tests.

These keep generated spider tests FAST and OFFLINE — they call the spider's parse callbacks
directly against fabricated HtmlResponses. Never start a live server or a CrawlerProcess here.
"""

import os

import pytest
from scrapy import Request
from scrapy.http import HtmlResponse


@pytest.fixture
def make_response():
    """Build a Scrapy ``HtmlResponse`` from a URL and HTML body, for offline parse tests."""

    def _make(url: str, body: str, encoding: str = "utf-8") -> HtmlResponse:
        return HtmlResponse(
            url=url,
            request=Request(url=url),
            body=body.encode(encoding),
            encoding=encoding,
        )

    return _make


@pytest.fixture
def split_output():
    """Split a callback's yielded output into ``(items, requests)``.

    ``requests`` are the ``scrapy.Request`` follow-ups; ``items`` is everything else (BaseItem /
    dicts). Saves every test from re-writing ``[r for r in results if isinstance(r, Request)]``.
    """

    def _split(results):
        items, requests = [], []
        for obj in results:
            (requests if isinstance(obj, Request) else items).append(obj)
        return items, requests

    return _split


@pytest.fixture
def assert_provenance():
    """Assert a yielded record carries the flat provenance fields, populated."""

    def _assert(item):
        for field in ("request_url", "response_url", "domain", "status", "scraped_at", "content"):
            assert item.get(field), f"missing/empty provenance field: {field}"

    return _assert


@pytest.fixture
def response_from_file(request):
    """Build an ``HtmlResponse`` from a snippet in a ``fixtures/`` dir next to the test file.

    For SHORT hand-written snippets only — do NOT commit full captured pages.
    """

    def _make(filename: str, url: str, encoding: str = "utf-8") -> HtmlResponse:
        path = os.path.join(os.path.dirname(str(request.path)), "fixtures", filename)
        with open(path, "rb") as fh:
            body = fh.read()
        return HtmlResponse(url=url, request=Request(url=url), body=body, encoding=encoding)

    return _make
