# HAR analysis — https://sirup.inaproc.id/sirup/caripaketctr/index

_Source: `har_file.har` · generated 2026-06-10T20:22:45+02:00_

## Verdict

- **Status:** 🟡 protected (delivered)
- Cloudflare, Cloudflare Turnstile present but the document was delivered — protection is passive.
- **Page title:** RUP - Cari Paket Penyedia
- **Captured:** 70 requests · 2932 KiB · load 5224 ms · TTFB 120.0 ms

## Protection

### Cloudflare — CDN / WAF / Bot Management
- `header` **cf-ray** — cf-ray: a09a67108b4aa2c1-VIE _(×65)_
- `header` **cf-mitigated** — cf-mitigated: challenge
- `header` **server** — server: cloudflare _(×65)_
- `url` **/cdn-cgi/challenge-platform/** — https://sirup.inaproc.id/cdn-cgi/challenge-platform/h/g/orchestrate/chl_page/v1?ray=a09a67108b4aa2c1 _(×9)_
- `cookie` **__cf_bm** — __cf_bm _(×3)_
- `url` **challenges\.cloudflare\.com** — https://challenges.cloudflare.com/turnstile/v0/g/8fc8ed1d8752/api.js?onload=NoWu9&render=explicit
- `header` **cf-chl-out** — cf-chl-out: EWMrv8KPKygkEjuJlRLnmz3BaEwh/cCo0H0eyf/G21GQQt0CVUiXsVWGzPtL5QxObb0M3K/tU+HiDq4+ _(×2)_
- `cookie` **cf_clearance** — cf_clearance
- `header` **cf-cache-status** — cf-cache-status: DYNAMIC _(×50)_
- `url` **/cdn-cgi/** — https://sirup.inaproc.id/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js _(×3)_

### Cloudflare Turnstile — CAPTCHA / challenge widget
- `url` **challenges\.cloudflare\.com/turnstile** — https://challenges.cloudflare.com/turnstile/v0/g/8fc8ed1d8752/api.js?onload=NoWu9&render=explicit

## Landing document

- **Final:** HTTP 200 · text/html; charset=utf-8 · HTTP/2.0 · 39797 B
- **Chain:** 307 → 403 → 200

**Request headers used:**

| header | value |
|---|---|
| User-Agent | Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Sa |
| Accept | text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/* |
| Referer | https://sirup.inaproc.id/sirup/caripaketctr/index?__cf_chl_tk=0jbzhhOvKxIt6CDjcCkZK6NfrMpi |
| sec-ch-ua | "Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99" |
| sec-ch-ua-platform | "Linux" |
| sec-ch-ua-mobile | ?0 |
| Upgrade-Insecure-Requests | 1 |

## Session cookies

| cookie | set by | attributes |
|---|---|---|
| `__cf_bm` | sirup.inaproc.id | HttpOnly; SameSite=None; Secure; Path=/; Domain=inaproc.id; Expires=Wed, 10 Jun 2026 18:52:38 GMT |
| `cf_clearance` | sirup.inaproc.id | HttpOnly; SameSite=None; Partitioned; Secure; Path=/; Domain=inaproc.id; Expires=Thu, 10 Jun 2027 18:22:42 GMT |
| `PLAY_ERRORS` | sirup.inaproc.id | Max-Age=0; Expires=Wed, 10 Jun 2026 18:22:42 GMT; Path=/sirup/; Secure; SameSite=Lax |
| `PLAY_FLASH` | sirup.inaproc.id | Max-Age=0; Expires=Wed, 10 Jun 2026 18:22:42 GMT; Path=/sirup/; Secure; HTTPOnly; SameSite=Lax |
| `PLAY_SESSION` | sirup.inaproc.id | Max-Age=1800; Expires=Wed, 10 Jun 2026 18:52:42 GMT; Path=/sirup/; Secure; HTTPOnly; SameSite=Lax |
| `_cfuvid` | sirup.inaproc.id | HttpOnly; SameSite=None; Secure; Path=/; Domain=inaproc.id |

## Data endpoints (direct-scrape candidates)

No JSON/API responses observed (page is likely server-rendered HTML).

## Hosts contacted

| host | requests | bytes | protection |
|---|---|---|---|
| sirup.inaproc.id | 53 | 2261393 | ⚠️ |
| challenges.cloudflare.com | 7 | 493307 | ⚠️ |
| cdn.datatables.net | 4 | 38104 |  |
| cdn.jsdelivr.net | 2 | 31091 |  |
| static.cloudflareinsights.com | 1 | 11672 |  |
| cdnjs.cloudflare.com | 1 | 4302 |  |
| www.googletagmanager.com | 1 | 163872 |  |
| region1.google-analytics.com | 1 | 0 |  |

## Statistics

- **By status:** 200×65, 204×2, 307×1, 401×1, 403×1
- **By type:** script×37, stylesheet×10, xhr×9, image×6, document×5, json×2, other×1

## Request timeline

| # | +ms | dur | method | status | type | size | host | url |
|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 86 | GET | 307 | other | 95 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/caripaketctr/index |
| 1 | 86 | 15 | GET | 403 | document | 24865 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/caripaketctr/index |
| 2 | 142 | 66 | GET | 200 | script | 66038 | sirup.inaproc.id | https://sirup.inaproc.id/cdn-cgi/challenge-platform/h/g/orchestrate/ch |
| 3 | 226 | 73 | GET | 200 | script | 21848 | challenges.cloudflare.com | https://challenges.cloudflare.com/turnstile/v0/g/8fc8ed1d8752/api.js?o |
| 4 | 375 | 28 | POST | 200 | xhr | 16707 | sirup.inaproc.id | https://sirup.inaproc.id/cdn-cgi/challenge-platform/h/g/flow/ov1/33006 |
| 5 | 435 | 54 | GET | 200 | document | 86529 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/turns |
| 6 | 511 | 37 | GET | 200 | image | 208 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/cmg/1 |
| 7 | 719 | 150 | POST | 200 | xhr | 371274 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/flow/ |
| 8 | 1061 | 24 | GET | 401 | xhr | 1698 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/pat/a |
| 9 | 1157 | 19 | GET | 200 | image | 3830 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/d/a09 |
| 10 | 4060 | 55 | POST | 200 | document | 7920 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/flow/ |
| 11 | 4143 | 57 | POST | 200 | document | 4859 | sirup.inaproc.id | https://sirup.inaproc.id/cdn-cgi/challenge-platform/h/g/flow/ov1/33006 |
| 12 | 4217 | 812 | POST | 200 | document | 39797 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/caripaketctr/index |
| 13 | 4555 | 72 | GET | 200 | stylesheet | 431 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/stylesheets/droid-sans.css |
| 14 | 4556 | 70 | GET | 200 | stylesheet | 2117 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/plugin/bootstrap-3.3.5-dist/css/ |
| 15 | 4556 | 102 | GET | 200 | stylesheet | 21685 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/plugin/bootstrap-3.3.5-dist/css/ |
| 16 | 4557 | 74 | GET | 200 | stylesheet | 6092 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/plugin/font-awesome-4.4.0/css/fo |
| 17 | 4557 | 80 | GET | 200 | stylesheet | 2820 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/stylesheets/main.css |
| 18 | 4557 | 79 | GET | 200 | stylesheet | 127 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/views/app.css |
| 19 | 4558 | 74 | GET | 200 | stylesheet | 1424 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/stylesheets/cari-paket.css |
| 20 | 4558 | 82 | GET | 200 | image | 2473 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/images/web/logo-header-latihan.p |
| 21 | 4558 | 73 | GET | 200 | script | 741 | sirup.inaproc.id | https://sirup.inaproc.id/cdn-cgi/scripts/5c5dd728/cloudflare-static/em |
| 22 | 4559 | 84 | GET | 200 | stylesheet | 1108 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/plugin/DataTables/DataTables-1.1 |
| 23 | 4559 | 83 | GET | 200 | stylesheet | 1346 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/stylesheets/bootstrap-datetimepi |
| 24 | 4778 | 159 | GET | 200 | xhr | 21587 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/font/s-BiyweUPV0v-yRb-cjciPk_vAr |
| 25 | 4779 | 163 | GET | 200 | xhr | 27479 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/font/droid-sans-bold.ttf |
| 26 | 4779 | 168 | GET | 200 | xhr | 64616 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/plugin/font-awesome-4.4.0/fonts/ |
| 27 | 5030 | 44 | GET | 200 | image | 29986 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/images/web/lkpp.png |
| 28 | 5030 | 41 | GET | 200 | image | 1214 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/images/web/siruplatihan.png |
| 29 | 5030 | 82 | GET | 200 | image | 856778 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/berkas/banner/banner_sirup_migra |
| 30 | 5031 | 62 | GET | 200 | script | 4037 | sirup.inaproc.id | https://sirup.inaproc.id/cdn-cgi/scripts/7d0fa10a/cloudflare-static/ro |
| 31 | 5031 | 117 | GET | 200 | script | 11672 | static.cloudflareinsights.com | https://static.cloudflareinsights.com/beacon.min.js/v833ccba57c9e4d279 |
| 32 | 5102 | 117 | GET | 200 | script | 708 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/ga/ga.js |
| 33 | 5102 | 131 | GET | 200 | script | 1279 | cdn.datatables.net | https://cdn.datatables.net/1.10.19/js/dataTables.bootstrap.min.js |
| 34 | 5103 | 207 | GET | 200 | script | 4302 | cdnjs.cloudflare.com | https://cdnjs.cloudflare.com/ajax/libs/numeral.js/2.0.6/numeral.min.js |
| 35 | 5103 | 142 | GET | 200 | script | 1165 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/plugin/bootstrap-datetimepicker- |
| 36 | 5104 | 132 | GET | 200 | script | 9746 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/javascripts/bootstrap-datetimepi |
| 37 | 5104 | 134 | GET | 200 | script | 13493 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/javascripts/moment.min.js |
| 38 | 5104 | 136 | GET | 200 | script | 7168 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/plugin/jquery-validation-1.14.0/ |
| 39 | 5104 | 138 | GET | 200 | script | 585 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/plugin/DataTables/Plugins/api/fn |
| 40 | 5105 | 141 | GET | 200 | script | 1957 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/plugin/DataTables/DataTables-1.1 |
| 41 | 5105 | 220 | GET | 200 | script | 6268 | cdn.datatables.net | https://cdn.datatables.net/buttons/1.5.2/js/buttons.html5.min.js |
| 42 | 5105 | 148 | GET | 200 | script | 1109 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/javascripts/moner/buttons.print. |
| 43 | 5106 | 216 | GET | 200 | script | 382094 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/javascripts/moner/vfs_fonts136.j |
| 44 | 5106 | 230 | GET | 200 | script | 393597 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/javascripts/moner/pdfmake.min136 |
| 45 | 5106 | 162 | GET | 200 | script | 31288 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/javascripts/moner/jszip.min313.j |
| 46 | 5106 | 162 | GET | 200 | script | 6973 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/javascripts/moner/buttons.flash. |
| 47 | 5107 | 173 | GET | 200 | script | 6299 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/javascripts/moner/dataTables.but |
| 48 | 5107 | 176 | GET | 200 | script | 29099 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/plugin/DataTables/DataTables-1.1 |
| 49 | 5107 | 194 | GET | 200 | script | 12564 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/platform.js-master/platform.js |
| 50 | 5107 | 323 | GET | 200 | stylesheet | 20482 | cdn.jsdelivr.net | https://cdn.jsdelivr.net/npm/bootstrap@3.3.5/dist/css/bootstrap.min.cs |
| 51 | 5108 | 180 | GET | 200 | script | 10609 | cdn.jsdelivr.net | https://cdn.jsdelivr.net/npm/bootstrap@3.3.5/dist/js/bootstrap.min.js |
| 52 | 5108 | 186 | GET | 200 | script | 364 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/javascripts/sumberDanaHelper.js |
| 53 | 5108 | 195 | GET | 200 | script | 1378 | cdn.datatables.net | https://cdn.datatables.net/1.13.6/js/dataTables.bootstrap.min.js |
| 54 | 5109 | 198 | GET | 200 | script | 29179 | cdn.datatables.net | https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js |
| 55 | 5109 | 223 | GET | 200 | script | 26488 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/javascripts/loader.js |
| 56 | 5109 | 212 | GET | 200 | script | 866 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/javascripts/jquery.ticker.min.js |
| 57 | 5110 | 220 | GET | 200 | script | 4852 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/javascripts/neatrup/akunting.js |
| 58 | 5110 | 215 | GET | 200 | script | 3236 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/javascripts/jquery.dataTables.co |
| 59 | 5111 | 228 | GET | 200 | script | 65529 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/plugin/jquery-ui-1.11.4.custom/j |
| 60 | 5111 | 223 | GET | 200 | script | 34646 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/javascripts/jquery-1.11.3.min.js |
| 61 | 5111 | 406 | GET | 200 | script | 163872 | www.googletagmanager.com | https://www.googletagmanager.com/gtag/js?id=G-D78WKTMJC6 |
| 62 | 5467 | 24 | GET | 200 | script | 3201 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/javascripts/jquery.dataTables.co |
| 63 | 5539 | 108 | POST | 204 | xhr | 0 | region1.google-analytics.com | https://region1.google-analytics.com/g/collect?v=2&tid=G-D78WKTMJC6&gt |
| 64 | 5539 | 31 | GET | 200 | script | 4828 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/javascripts/neatrup/akunting.js |
| 65 | 5573 | 24 | GET | 200 | script | 844 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/javascripts/jquery.ticker.min.js |
| 66 | 5777 | 246 | GET | 200 | json | 457 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/plugin/DataTables-1.10.7/extensi |
| 67 | 5781 | 23 | POST | 204 | xhr | 174 | sirup.inaproc.id | https://sirup.inaproc.id/cdn-cgi/rum? |
| 68 | 6025 | 50 | GET | 200 | xhr | 18187 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/public/plugin/bootstrap-3.3.5-dist/font |
| 69 | 6026 | 229 | GET | 200 | json | 1454 | sirup.inaproc.id | https://sirup.inaproc.id/sirup/caripaketctr/search?tahunAnggaran=2026& |

## Recommendations

- Cloudflare challenge in play — use a real browser (scrapy-playwright/stealth) to solve it, or reuse a valid `cf_clearance` cookie + the *exact* matching User-Agent.
- Persist & replay these cookies across requests: __cf_bm, cf_clearance, PLAY_ERRORS, PLAY_FLASH, PLAY_SESSION, _cfuvid
