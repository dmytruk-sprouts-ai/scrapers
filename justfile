default:
    @just --list

_require-venv:
    @test -x .venv/bin/scrapy || { echo "scraper venv missing — run: just init"; exit 1; }

init:
    uv venv .venv
    uv pip install --python .venv -r docker/requirements.txt
    .venv/bin/playwright install chromium

sync:
    uv pip install --python .venv -r docker/requirements.txt

# Collect ~LIMIT sample records + run stats into scraper/spiders/<SPIDER>/samples/.
#   just sample books_toscrape_com        (defaults to 20)
#   just sample books_toscrape_com 50
sample SPIDER LIMIT='20': _require-venv
    cd scrapers && ../.venv/bin/python -m scraper.sample_runner {{SPIDER}} {{LIMIT}}

# Run a full crawl of SPIDER. Extra scrapy args pass straight through, e.g.
#   just crawl books_toscrape_com -O out.jsonl -s CLOSESPIDER_PAGECOUNT=5
crawl SPIDER *ARGS: _require-venv
    cd scrapers && ../.venv/bin/scrapy crawl {{SPIDER}} {{ARGS}}

# Capture a HAR for SPIDER, writing into scraper/spiders/<SPIDER>/outputs/<engine>/.
# ENGINE=patchright (default) or playwright; each writes its own tree, so run both to compare:
#   just capture-har sirup_inaproc_id            # patchright
#   just capture-har sirup_inaproc_id playwright # playwright
capture-har SPIDER ENGINE='patchright': _require-venv
    cd scrapers && SCRAPER_PW_ENGINE={{ENGINE}} ../.venv/bin/python -m scraper.spiders.{{SPIDER}}.capture_har

# Run the detection harness. Runs every engine (playwright + patchright) — each in its own isolated
# subprocess — then writes the combined comparison. Outputs land under outputs/<variant>/.
crawl-check-protection: _require-venv
    cd scrapers && ../.venv/bin/python -m scraper.spiders._detection_check.detection_check