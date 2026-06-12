default:
    @just --list

_require-venv:
    @test -x .venv/bin/scrapy || { echo "scraper venv missing — run: just init"; exit 1; }

init:
    sudo apt install pv
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

_compose := "docker compose -f docker/docker-compose.yml"

# Bring up the ProtonVPN tunnel (gluetun) in the background. Needs docker/.env
# (cp docker/.env.example docker/.env, fill WIREGUARD_PRIVATE_KEY -- see docker/README.md).
vpn-up:
    {{_compose}} up -d gluetun

# Tear down the VPN tunnel and any scraper containers.
vpn-down:
    {{_compose}} down

# Like `crawl`, but routed through the VPN (kill-switched). Brings gluetun up
# first (idempotent), then runs the crawl in a netns-shared container. e.g.
#   just crawl-vpn sirup_inaproc_id -O out.jsonl -s CLOSESPIDER_PAGECOUNT=5
# xvfb-run gives the headed (patchright stealth) browser a virtual display.
crawl-vpn SPIDER *ARGS: vpn-up
    {{_compose}} run --build --service-ports scraper scrapy crawl {{SPIDER}}


# Capture a HAR for SPIDER, writing into scraper/spiders/<SPIDER>/outputs/<engine>/.
# ENGINE=patchright (default) or playwright; each writes its own tree, so run both to compare:
#   just capture-har sirup_inaproc_id            # patchright
#   just capture-har sirup_inaproc_id playwright # playwright
capture-har SPIDER ENGINE='patchright': _require-venv
    cd scrapers && SCRAPER_PW_ENGINE={{ENGINE}} ../.venv/bin/python -m scraper.spiders.{{SPIDER}}.capture_har


crawl-ip:
    just crawl-vpn ipinfo_io

crawl-httpbin:
    just crawl-vpn httpbin

crawl-cloudflare-challange:
    just crawl-vpn cloudflare-challange

crawl-th:
    xdg-open "http://localhost:6080/vnc_lite.html?autoconnect=true&resize=scale"
    just crawl-vpn gprocurement_go_th

crawl-th-details:
    just crawl-vpn gprocurement_details

test-vnc: vpn-up
    {{_compose}} run --build --service-ports scraper sleep infinity

prod-deploy:
    docker build --platform linux/amd64 -t scrapers:latest -f docker/Dockerfile .
    docker image ls scrapers:latest
    docker save scrapers:latest | pv | gzip | ssh -i ~/.ssh/sprouts_scraping_vm_id_rsa scraping@104.64.207.128 'gunzip | docker load'
    ssh -i ~/.ssh/sprouts_scraping_vm_id_rsa scraping@104.64.207.128 'docker image ls'


prod-run-vnc:
    # 1. Copy ./docker -> ~/scraping-procurement on the VM
    rsync -avz --mkpath -e "ssh -i ~/.ssh/sprouts_scraping_vm_id_rsa" ./docker scraping@104.64.207.128:~/scraping-procurement
    # 2. Open SSH with VNC forwarding, then run the scraper container in the foreground
    xdg-open "http://localhost:6080/vnc_lite.html?autoconnect=true&resize=scale"
    ssh -t -i ~/.ssh/sprouts_scraping_vm_id_rsa -L 6080:localhost:6080 scraping@104.64.207.128 \
        'cd ~/scraping-procurement && docker compose -f ./docker/docker-compose.prod.yml up vnc-test'
    # access VNC: http://localhost:6080/vnc_lite.html?autoconnect=true&resize=scale



prod-run CONTAINER:
    # 1. Copy ./docker -> ~/scraping-procurement on the VM
    rsync -avz --mkpath -e "ssh -i ~/.ssh/sprouts_scraping_vm_id_rsa" ./docker scraping@104.64.207.128:~/scraping-procurement
    xdg-open "http://localhost:6080/vnc_lite.html?autoconnect=true&resize=scale"
    # 2. Open SSH with VNC forwarding, then run the scraper container in the foreground
    ssh -t -i ~/.ssh/sprouts_scraping_vm_id_rsa -L 6080:localhost:6080 scraping@104.64.207.128 \
        'cd ~/scraping-procurement && docker compose -f ./docker/docker-compose.prod.yml up {{CONTAINER}}'
    

prod-stop:
    ssh -i ~/.ssh/sprouts_scraping_vm_id_rsa scraping@104.64.207.128 \
        'cd ~/scraping-procurement && docker compose -f ./docker/docker-compose.prod.yml down'

setup-vm:
    ssh -t -i ~/.ssh/sprouts_scraping_vm_id_rsa scraping@104.64.207.128 '\
        curl -fsSL https://get.docker.com -o get-docker.sh && \
        sudo sh ./get-docker.sh && \
        sudo usermod -aG docker $USER && \
        exec newgrp docker'




# https://process5.gprocurement.go.th/egp-upload-service/v1/downloadFileTest?fileId=f2b4f0a0f2a54c1d9ee7a31aa7b76938

# 2
# 69059344814
# https://process5.gprocurement.go.th/egp-upload-service/v1/downloadFileTest?fileId=20000f60dee74b4e891c0c4e4785c8a9

# 3
# 69069229752
# https://process3.gprocurement.go.th/egp2procmainWeb/jsp/procsearch.sch?pid=69069229752&servlet=gojsp&proc_id=ShowHTMLFile&processFlows=Procure

# 4
# 69069237412
# https://process3.gprocurement.go.th/egp2procmainWeb/jsp/procsearch.sch?pid=69069237412&servlet=gojsp&proc_id=ShowHTMLFile&processFlows=Procure

# 5
# 69069237331
# https://process3.gprocurement.go.th/egp2procmainWeb/jsp/procsearch.sch?pid=69069237331&servlet=gojsp&proc_id=ShowHTMLFile&processFlows=Procure