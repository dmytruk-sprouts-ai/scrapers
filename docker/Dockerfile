# Sandbox image: the toolchain the agent uses to investigate sites and run generated scrapers.
FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System deps: curl (probing) + xvfb (virtual X server -- the spiders run headed
# for patchright stealth, so they need a display). Other Playwright/Chromium libs
# come via `playwright install --with-deps` below.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates git x11vnc xvfb xauth novnc websockify \
    && rm -rf /var/lib/apt/lists/*

# Scraping toolchain (single source of truth, shared with the local `just scraper-install` venv).
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# Browsers + their OS dependencies. The spiders launch with channel="chrome"
# (real Google Chrome stable -- the patchright stealth setup vs Cloudflare), so
# install the chrome channel as well as bundled chromium. `chrome` puts Google
# Chrome at /opt/google/chrome/chrome, where channel="chrome" looks for it.
# Install Chrome manually
# to get latest: https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt-get update && \
    apt-get install -y wget && \
    wget -O /tmp/google-chrome.deb \
      https://dl.google.com/linux/chrome/deb/pool/main/g/google-chrome-stable/google-chrome-stable_148.0.7778.178-1_amd64.deb && \
    apt-get install -y /tmp/google-chrome.deb && \
    rm -f /tmp/google-chrome.deb

# Skip Playwright browser downloads
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

WORKDIR /workspace


