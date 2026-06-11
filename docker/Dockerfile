# Sandbox image: the toolchain the agent uses to investigate sites and run generated scrapers.
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System deps: curl (probing) + libs Playwright/Chromium need are installed via
# `playwright install --with-deps` below.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates git  \
    && rm -rf /var/lib/apt/lists/*

# Scraping toolchain (single source of truth, shared with the local `just scraper-install` venv).
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Browser + its OS dependencies.
RUN playwright install --with-deps chromium

WORKDIR /workspace

CMD ["sleep", "infinity"]
