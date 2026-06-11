# HAR analysis — https://www.gprocurement.go.th/new_index.html

_Source: `har_file.har` · generated 2026-06-11T18:37:36+02:00_

## Verdict

- **Status:** 🟡 protected (delivered)
- Cloudflare, Cloudflare Turnstile present but the document was delivered — protection is passive.
- **Page title:** eGP All Web
- **Captured:** 57 requests · 13182 KiB · load 35328 ms · TTFB 2235.1 ms

## Protection

### Cloudflare — CDN / WAF / Bot Management
- `url` **challenges\.cloudflare\.com** — https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit _(×2)_
- `header` **cf-ray** — cf-ray: a0a1fe4aa8855b95-VIE _(×14)_
- `header` **server** — server: cloudflare _(×14)_
- `url` **/cdn-cgi/challenge-platform/** — https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/turnstile/f/ov2/av0/rch/kcei5/0x4AAAAAABuINxkTjFy-_hpH/ _(×12)_
- `header` **cf-chl-out** — cf-chl-out: Rrfods6qxXPOsGr3XHqO17OE6UCdehqVZyqbHlrLibmwx1LogK0+242voqdabfbEaheWq19R0DwmDJht _(×2)_

### Cloudflare Turnstile — CAPTCHA / challenge widget
- `url` **challenges\.cloudflare\.com/turnstile** — https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit _(×2)_

## Landing document

- **Final:** HTTP 302 · x-unknown · http/1.0 · 689 B

**Request headers used:**

| header | value |
|---|---|
| User-Agent | Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Sa |
| Accept | text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/* |
| sec-ch-ua | "Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99" |
| sec-ch-ua-platform | "Linux" |
| sec-ch-ua-mobile | ?0 |
| Upgrade-Insecure-Requests | 1 |

## Session cookies

| cookie | set by | attributes |
|---|---|---|
| `www_visit` | www.gprocurement.go.th | Path=/; Domain=.gprocurement.go.th; Secure; HttpOnly |
| `TS01e91d66` | www.gprocurement.go.th | Path=/; Domain=.www.gprocurement.go.th |
| `TS7431b39c027` | www.gprocurement.go.th | Path=/ |
| `TS4c538cb7027` | process5.gprocurement.go.th | Path=/ |
| `Xsrf-Token` | process5.gprocurement.go.th | Path=/; Version=1; Secure; Httponly |
| `TS0174b17a` | process5.gprocurement.go.th | Path=/ |

## Data endpoints (direct-scrape candidates)

| method | status | size | url |
|---|---|---|---|
| POST | 200 | 1589 B | https://process5.gprocurement.go.th/egp-amas22-service/pb/a-master/app-hidden |
| POST | 200 | 1771 B | https://process5.gprocurement.go.th/egp-amas22-service/pb/a-master/app-ver |
| GET | 200 | 8178 B | https://process5.gprocurement.go.th/egp-rdb-service/rdbsysm011/listProvince |
| GET | 200 | 5246 B | https://process5.gprocurement.go.th/egp-rdb-service/listProcureMethod |
| GET | 200 | 1627 B | https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/api/v1/cfturn |
| GET | 200 | 1697 B | https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/api/v1/cfturn |
| GET | 200 | 11427 B | https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/announcement? |
| GET | 200 | 1587 B | https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/announcement/ |
| GET | 200 | 1697 B | https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/api/v1/cfturn |
| GET | 200 | 11138 B | https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/announcement? |
| GET | 200 | 1586 B | https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-project/announcement/ |

## Hosts contacted

| host | requests | bytes | protection |
|---|---|---|---|
| process5.gprocurement.go.th | 40 | 12361216 |  |
| challenges.cloudflare.com | 14 | 904820 | ⚠️ |
| www.gprocurement.go.th | 3 | 267848 |  |

## Statistics

- **By status:** 200×53, 302×2, 401×2
- **By type:** script×20, json×11, image×10, document×6, xhr×4, font×3, other×2, stylesheet×1

## Request timeline

| # | +ms | dur | method | status | type | size | host | url |
|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 1688 | GET | 302 | other | 689 | www.gprocurement.go.th | https://www.gprocurement.go.th/new_index.html |
| 1 | 1267 | 556 | GET | 200 | document | 1634 | www.gprocurement.go.th | https://www.gprocurement.go.th/homepage.html |
| 2 | 1829 | 33 | GET | 200 | image | 265525 | www.gprocurement.go.th | https://www.gprocurement.go.th/content/queen.jpg |
| 3 | 2620 | 2023 | GET | 200 | document | 1561 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/announcement?keywor |
| 4 | 3989 | 4755 | GET | 200 | stylesheet | 274320 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/styles.124878ba6c37 |
| 5 | 3990 | 1297 | GET | 200 | script | 18276 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/polyfills.a052d679d |
| 6 | 3990 | 16634 | GET | 200 | script | 630754 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/scripts.c8f2401c9e4 |
| 7 | 3991 | 1291 | GET | 200 | script | 5041 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/main.04c281d2396cb9 |
| 8 | 8793 | 32 | GET | 200 | image | 125211 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/bg.5f1aac6a1818f691 |
| 9 | 8793 | 26 | GET | 200 | font | 15867 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/CSChatThaiUI.2e18ce |
| 10 | 20356 | 30 | GET | 200 | script | 205316 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/537.2497dc59d8e16be |
| 11 | 20357 | 31 | GET | 200 | script | 63937 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/692.8df0b1adef90c6b |
| 12 | 20357 | 31 | GET | 200 | script | 24369 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/998.22734751ac11868 |
| 13 | 20357 | 42 | GET | 200 | script | 106921 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/472.3bb6c2341219198 |
| 14 | 20358 | 42 | GET | 200 | script | 5193 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/91.62a62d0cca887da7 |
| 15 | 20358 | 61 | GET | 200 | script | 58847 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/921.536253842d96079 |
| 16 | 20358 | 61 | GET | 200 | script | 8490 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/824.6de209d186bca27 |
| 17 | 20358 | 80 | GET | 200 | script | 37140 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/732.3bb9ba06b34d988 |
| 18 | 20359 | 700 | GET | 200 | script | 1230166 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/506.b345190b8300583 |
| 19 | 20359 | 700 | GET | 200 | script | 1412 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/411.ef931e8fec707c8 |
| 20 | 20359 | 805 | GET | 200 | script | 6729712 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/90.b8355fa5534e09cb |
| 21 | 20359 | 809 | GET | 200 | script | 170181 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/453.843493ff0b45477 |
| 22 | 20359 | 816 | GET | 200 | script | 668439 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/981.6870b986214a493 |
| 23 | 20360 | 828 | GET | 200 | script | 1107992 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/744.7d7ff6ece738a49 |
| 24 | 21618 | 729 | GET | 200 | script | 5042 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-aann09-web/remoteEntry.js |
| 25 | 22351 | 9410 | GET | 200 | script | 418091 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-aann09-web/594.dcabd3aaef1da85 |
| 26 | 31941 | 432 | GET | 200 | image | 5181 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/assets/images/remar |
| 27 | 31942 | 20 | GET | 200 | image | 49213 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/assets/images/logo. |
| 28 | 31942 | 447 | GET | 200 | image | 4018 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/assets/images/logo- |
| 29 | 31990 | 3205 | GET | 200 | image | 163881 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/header-bg.5321acaee |
| 30 | 31991 | 67 | GET | 200 | font | 49966 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/KanitRegular.e15eb4 |
| 31 | 31991 | 76 | GET | 200 | font | 129136 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-agpc01-web/material-icon.59322 |
| 32 | 32043 | 467 | POST | 200 | json | 1589 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-amas22-service/pb/a-master/app |
| 33 | 32044 | 502 | POST | 200 | json | 1771 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-amas22-service/pb/a-master/app |
| 34 | 32045 | 480 | GET | 200 | json | 8178 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-rdb-service/rdbsysm011/listPro |
| 35 | 32045 | 1093 | GET | 200 | json | 5246 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-rdb-service/listProcureMethod |
| 36 | 32046 | 1151 | GET | 200 | json | 1627 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-p |
| 37 | 32997 | 68 | GET | 302 | other | 0 | challenges.cloudflare.com | https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit |
| 38 | 33045 | 35 | GET | 200 | script | 21792 | challenges.cloudflare.com | https://challenges.cloudflare.com/turnstile/v0/g/8fc8ed1d8752/api.js |
| 39 | 33095 | 38 | GET | 200 | document | 89288 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/turns |
| 40 | 33156 | 44 | GET | 200 | image | 208 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/cmg/1 |
| 41 | 33352 | 124 | POST | 200 | xhr | 343143 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/flow/ |
| 42 | 34486 | 17 | GET | 200 | image | 818 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/d/a0a |
| 43 | 34680 | 21 | GET | 401 | xhr | 1697 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/pat/a |
| 44 | 36605 | 63 | POST | 200 | document | 5836 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/flow/ |
| 45 | 36672 | 622 | GET | 200 | json | 1697 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-p |
| 46 | 37299 | 735 | GET | 200 | json | 11427 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-p |
| 47 | 38037 | 1203 | GET | 200 | json | 1587 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-p |
| 48 | 326684 | 1663 | GET | 200 | document | 87138 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/turns |
| 49 | 328323 | 20 | GET | 200 | image | 208 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/cmg/1 |
| 50 | 328530 | 191 | POST | 200 | xhr | 341564 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/flow/ |
| 51 | 331091 | 23 | GET | 200 | image | 5678 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/d/a0a |
| 52 | 331558 | 23 | GET | 401 | xhr | 1699 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/pat/a |
| 53 | 331716 | 59 | POST | 200 | document | 5751 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/flow/ |
| 54 | 331781 | 1809 | GET | 200 | json | 1697 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-p |
| 55 | 333363 | 748 | GET | 200 | json | 11138 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-p |
| 56 | 334114 | 553 | GET | 200 | json | 1586 | process5.gprocurement.go.th | https://process5.gprocurement.go.th/egp-atpj27-service/pb/a-egp-allt-p |

## Recommendations

- Cloudflare challenge in play — use a real browser (scrapy-playwright/stealth) to solve it, or reuse a valid `cf_clearance` cookie + the *exact* matching User-Agent.
- Persist & replay these cookies across requests: www_visit, TS01e91d66, TS7431b39c027, TS4c538cb7027, Xsrf-Token, TS0174b17a
- 11 JSON/API endpoint(s) seen — consider scraping them directly instead of parsing HTML (check whether they need the session cookies above).
