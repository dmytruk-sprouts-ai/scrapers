# Packaging for scrapyd-deploy: the whole `scraper` project ships as one egg, and every
# spider under scraper/spiders/ is deployed together. Per-spider run.log / meta.json files are
# plain data and are NOT collected by find_packages, so they stay out of the egg.

from setuptools import find_packages, setup

setup(
    name="scraper",
    version="1.0",
    packages=find_packages(),
    entry_points={"scrapy": ["settings = scraper.settings"]},
)
