# Run scrapers through ProtonVPN in a container

Routes a full `scrapy crawl` through ProtonVPN's WireGuard tunnel with a kill
switch. gluetun runs the VPN in userspace; the `scraper` container shares its
network namespace, so **every** request the crawl makes — curl_cffi, requests,
and Playwright/Chromium alike — egresses through the tunnel. If the VPN drops,
gluetun's firewall blocks everything: the crawl cannot fall back to your real IP.

Use this for the geo/Cloudflare-gated targets (`sirup_inaproc_id`,
`spce_inaproc_id`, `gprocurement_go_th`) where an Indonesian exit matters.

The `scraper` image is the same full toolchain as `just init` (see `Dockerfile`
+ `requirements.txt`), so any spider runs unchanged.

## 1. Get your ProtonVPN WireGuard key

1. Log in at <https://account.protonvpn.com> → **Downloads** / **WireGuard
   configuration**.
2. Create a WireGuard config; pick **Indonesia** if offered (Proton's coverage
   changes — any country still hides your IP, but won't satisfy a geo-restriction).
3. Open the downloaded `.conf` and copy the value after `PrivateKey = `.

```bash
cp docker/.env.example docker/.env
# put the PrivateKey into WIREGUARD_PRIVATE_KEY in docker/.env
```

`.env` and `*.conf` are gitignored — treat the private key as a secret.

## 2. Bring up the tunnel and confirm the exit IP is NOT yours

```bash
just vpn-up
docker compose -f docker/docker-compose.yml logs -f gluetun   # wait for "healthy"

# read the exit IP through the tunnel:
docker compose -f docker/docker-compose.yml run --rm scraper \
    python -c "import urllib.request; print(urllib.request.urlopen('https://ipinfo.io/json',timeout=15).read().decode())"
```

Verify `ip`/`country` is the VPN's (e.g. `"country": "ID"`), **not** your home
IP. Don't proceed until this is confirmed.

> The first `scraper` run builds the image (~2GB: scrapy + Playwright + Chromium).

## 3. Run a crawl through the VPN

Use the `just` wrapper (mirrors `just crawl`, extra scrapy args pass through):

```bash
# smoke test:
just crawl-vpn books_toscrape_com -O /workspace/scrapers/vpn-smoke.jsonl -s CLOSESPIDER_PAGECOUNT=2

# the real target, from the Indonesian exit:
just crawl-vpn sirup_inaproc_id -O out.jsonl -s CLOSESPIDER_PAGECOUNT=5
```

`scrapers/` is bind-mounted read-write, so feed exports, `samples/`, `outputs/`,
and the Scrapy httpcache land back on the host. Paths in `-O` are resolved inside
the container — use `/workspace/scrapers/...` for an explicit location, or a bare
filename to write into the project dir.

## 4. Tear down

```bash
just vpn-down
```

## Notes & guardrails

- **No leaks:** every `scraper` packet egresses through gluetun. If the exit IP
  ever equals your own, stop — the netns sharing isn't active.
- **Kill-switch check:** with the tunnel down (`just vpn-down`), a `crawl-vpn`
  should fail to reach the network rather than leak to your real IP.
- If gluetun errors that it needs an address, uncomment `WIREGUARD_ADDRESSES`
  in `docker-compose.yml` (Proton default `10.2.0.2/32`).
- gluetun stays up across multiple `crawl-vpn` runs, keeping the tunnel warm.
- This shares gluetun config with `../container/` (the `ip_bypass.py` probe);
  that stack is independent and unchanged.
