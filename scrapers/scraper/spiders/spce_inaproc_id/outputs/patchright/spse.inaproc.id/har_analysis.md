# HAR analysis — https://spse.inaproc.id/jakarta/lelang

_Source: `har_file.har` · generated 2026-06-12T11:06:53+02:00_

## Verdict

- **Status:** 🟡 protected (delivered)
- Cloudflare, Cloudflare Turnstile present but the document was delivered — protection is passive.
- **Page title:** LPSE Provinsi DKI Jakarta - Cari Paket
- **Captured:** 67 requests · 1403 KiB · load 8054 ms · TTFB 127.3 ms

## Protection

### Cloudflare — CDN / WAF / Bot Management
- `header` **cf-ray** — cf-ray: a0a7b0c55e25c2fa-VIE _(×57)_
- `header` **cf-mitigated** — cf-mitigated: challenge
- `header` **server** — server: cloudflare _(×57)_
- `url` **/cdn-cgi/challenge-platform/** — https://spse.inaproc.id/cdn-cgi/challenge-platform/h/g/orchestrate/chl_page/v1?ray=a0a7b0c55e25c2fa _(×9)_
- `cookie` **__cf_bm** — __cf_bm _(×3)_
- `url` **challenges\.cloudflare\.com** — https://challenges.cloudflare.com/turnstile/v0/g/8fc8ed1d8752/api.js?onload=NoWu9&render=explicit
- `header` **cf-chl-out** — cf-chl-out: PZvOuEuYXofldONoJSihKc9rOVjJFyT6ImcRgeuR3qkpYqWMhJ6kSRZgK8rQxT5fyq+Zl+gArf65GDbT _(×2)_
- `cookie` **cf_clearance** — cf_clearance
- `header` **cf-cache-status** — cf-cache-status: DYNAMIC _(×42)_
- `url` **/cdn-cgi/** — https://spse.inaproc.id/cdn-cgi/scripts/5c5dd728/cloudflare-static/email-decode.min.js _(×3)_

### Cloudflare Turnstile — CAPTCHA / challenge widget
- `url` **challenges\.cloudflare\.com/turnstile** — https://challenges.cloudflare.com/turnstile/v0/g/8fc8ed1d8752/api.js?onload=NoWu9&render=explicit

## Landing document

- **Final:** HTTP 200 · text/html; charset=utf-8 · HTTP/2.0 · 8215 B
- **Chain:** 307 → 403 → 200

**Request headers used:**

| header | value |
|---|---|
| User-Agent | Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Sa |
| Accept | text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/* |
| Referer | https://spse.inaproc.id/jakarta/lelang?__cf_chl_tk=o0ckyxXCdA2hxUS.Q2qovvAfSfNFlYIg7IkcIS2 |
| sec-ch-ua | "Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99" |
| sec-ch-ua-platform | "Linux" |
| sec-ch-ua-mobile | ?0 |
| Upgrade-Insecure-Requests | 1 |

## Session cookies

| cookie | set by | attributes |
|---|---|---|
| `__cf_bm` | spse.inaproc.id | HttpOnly; SameSite=None; Secure; Path=/; Domain=inaproc.id; Expires=Fri, 12 Jun 2026 09:34:52 GMT |
| `cf_clearance` | spse.inaproc.id | HttpOnly; SameSite=None; Partitioned; Secure; Path=/; Domain=inaproc.id; Expires=Sat, 12 Jun 2027 09:04:56 GMT |
| `SPSE_ERRORS` | spse.inaproc.id | Max-Age=0; Expires=Fri, 12 Jun 2026 09:04:56 GMT; Path=/; Secure; SameSite=Lax |
| `SPSE_SESSION` | spse.inaproc.id | Max-Age=1800; Expires=Fri, 12 Jun 2026 09:34:56 GMT; Path=/; Secure; HTTPOnly; SameSite=Lax |
| `SPSE_FLASH` | spse.inaproc.id | Max-Age=0; Expires=Fri, 12 Jun 2026 09:04:56 GMT; Path=/; Secure; HTTPOnly; SameSite=Lax |
| `_cfuvid` | spse.inaproc.id | HttpOnly; SameSite=None; Secure; Path=/; Domain=inaproc.id |

## Data endpoints (direct-scrape candidates)

No JSON/API responses observed (page is likely server-rendered HTML).

## Hosts contacted

| host | requests | bytes | protection |
|---|---|---|---|
| spse.inaproc.id | 34 | 174911 | ⚠️ |
| unpkg.com | 13 | 161506 |  |
| storage.googleapis.com | 8 | 153502 |  |
| challenges.cloudflare.com | 7 | 477848 | ⚠️ |
| cdnjs.cloudflare.com | 3 | 294141 |  |
| static.cloudflareinsights.com | 1 | 11672 |  |
| www.googletagmanager.com | 1 | 164135 |  |

## Statistics

- **By status:** 200×55, 204×1, 307×9, 401×1, 403×1
- **By type:** script×26, other×11, image×10, stylesheet×10, document×5, xhr×4, json×1

## Request timeline

| # | +ms | dur | method | status | type | size | host | url |
|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 94 | GET | 307 | other | 84 | spse.inaproc.id | https://spse.inaproc.id/jakarta/lelang |
| 1 | 93 | 16 | GET | 403 | document | 24870 | spse.inaproc.id | https://spse.inaproc.id/jakarta/lelang |
| 2 | 170 | 65 | GET | 200 | script | 65764 | spse.inaproc.id | https://spse.inaproc.id/cdn-cgi/challenge-platform/h/g/orchestrate/chl |
| 3 | 246 | 100 | GET | 200 | script | 21847 | challenges.cloudflare.com | https://challenges.cloudflare.com/turnstile/v0/g/8fc8ed1d8752/api.js?o |
| 4 | 391 | 34 | POST | 200 | xhr | 16702 | spse.inaproc.id | https://spse.inaproc.id/cdn-cgi/challenge-platform/h/g/flow/ov1/290065 |
| 5 | 454 | 75 | GET | 200 | document | 86170 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/turns |
| 6 | 538 | 33 | GET | 200 | image | 208 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/cmg/1 |
| 7 | 748 | 171 | POST | 200 | xhr | 353760 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/flow/ |
| 8 | 1257 | 66 | GET | 200 | image | 6166 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/d/a0a |
| 9 | 1699 | 25 | GET | 401 | xhr | 1702 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/pat/a |
| 10 | 4015 | 59 | POST | 200 | document | 7995 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/flow/ |
| 11 | 4101 | 115 | POST | 200 | document | 5091 | spse.inaproc.id | https://spse.inaproc.id/cdn-cgi/challenge-platform/h/g/flow/ov1/290065 |
| 12 | 4242 | 392 | POST | 200 | document | 8215 | spse.inaproc.id | https://spse.inaproc.id/jakarta/lelang |
| 13 | 4634 | 146 | GET | 200 | stylesheet | 24533 | unpkg.com | https://unpkg.com/bootstrap@4.6.2/dist/css/bootstrap.min.css |
| 14 | 4635 | 118 | GET | 200 | stylesheet | 7344 | unpkg.com | https://unpkg.com/font-awesome@4.7.0/css/font-awesome.min.css |
| 15 | 4635 | 105 | GET | 200 | stylesheet | 2376 | unpkg.com | https://unpkg.com/datatables.net-bs4@1.13.5/css/dataTables.bootstrap4. |
| 16 | 4635 | 105 | GET | 200 | stylesheet | 1315 | unpkg.com | https://unpkg.com/datatables.net-buttons-bs4@1.6.5/css/buttons.bootstr |
| 17 | 4635 | 108 | GET | 200 | stylesheet | 1755 | unpkg.com | https://unpkg.com/eonasdan-bootstrap-datetimepicker@4.17.47/build/css/ |
| 18 | 4636 | 116 | GET | 200 | stylesheet | 2644 | unpkg.com | https://unpkg.com/bootstrap-select@1.13.18/dist/css/bootstrap-select.m |
| 19 | 4637 | 118 | GET | 200 | stylesheet | 732 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/css/bootstrap-dialog.min.css |
| 20 | 4637 | 130 | GET | 200 | stylesheet | 7070 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/css/application.css |
| 21 | 4637 | 128 | GET | 200 | stylesheet | 317 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/css/strength.css |
| 22 | 4638 | 160 | GET | 200 | stylesheet | 19527 | cdnjs.cloudflare.com | https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min. |
| 23 | 4638 | 132 | GET | 307 | other | 0 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/images/global/logo-spse.svg |
| 24 | 4638 | 138 | GET | 307 | other | 0 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/images/imgng/lpse-nama.png |
| 25 | 4639 | 177 | GET | 200 | script | 11672 | static.cloudflareinsights.com | https://static.cloudflareinsights.com/beacon.min.js/v833ccba57c9e4d279 |
| 26 | 4639 | 300 | GET | 307 | other | 0 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/images/transparent-loading-gif- |
| 27 | 4640 | 296 | GET | 307 | other | 0 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/images/global/instagram.png |
| 28 | 4640 | 299 | GET | 307 | other | 0 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/images/global/facebook.png |
| 29 | 4640 | 301 | GET | 307 | other | 0 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/images/global/x.png |
| 30 | 4640 | 300 | GET | 307 | other | 0 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/images/global/youtube.png |
| 31 | 4641 | 133 | GET | 200 | script | 739 | spse.inaproc.id | https://spse.inaproc.id/cdn-cgi/scripts/5c5dd728/cloudflare-static/ema |
| 32 | 4641 | 142 | GET | 200 | script | 3994 | spse.inaproc.id | https://spse.inaproc.id/cdn-cgi/scripts/7d0fa10a/cloudflare-static/roc |
| 33 | 4759 | 2091 | GET | 200 | image | 12342 | storage.googleapis.com | https://storage.googleapis.com/spse-public-prod/public/images/global/l |
| 34 | 4766 | 2105 | GET | 200 | image | 712 | storage.googleapis.com | https://storage.googleapis.com/spse-public-prod/127/public/images/imgn |
| 35 | 4935 | 258 | GET | 200 | other | 157281 | cdnjs.cloudflare.com | https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/webfonts/fa- |
| 36 | 4936 | 258 | GET | 200 | other | 117333 | cdnjs.cloudflare.com | https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/webfonts/fa- |
| 37 | 4939 | 3082 | GET | 200 | image | 125205 | storage.googleapis.com | https://storage.googleapis.com/spse-public-prod/127/public/images/tran |
| 38 | 4941 | 2008 | GET | 200 | image | 944 | storage.googleapis.com | https://storage.googleapis.com/spse-public-prod/public/images/global/f |
| 39 | 4943 | 2009 | GET | 200 | image | 1741 | storage.googleapis.com | https://storage.googleapis.com/spse-public-prod/public/images/global/i |
| 40 | 4946 | 2008 | GET | 200 | image | 879 | storage.googleapis.com | https://storage.googleapis.com/spse-public-prod/public/images/global/x |
| 41 | 4949 | 2013 | GET | 200 | image | 743 | storage.googleapis.com | https://storage.googleapis.com/spse-public-prod/public/images/global/y |
| 42 | 4955 | 125 | GET | 200 | script | 4078 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/js/common-v2.js |
| 43 | 4955 | 127 | GET | 200 | script | 928 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/js/datatable-handler.js |
| 44 | 4956 | 133 | GET | 200 | script | 453 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/js/message-constants.js |
| 45 | 4956 | 135 | GET | 200 | script | 2449 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/js/jquery.webticker.min.js |
| 46 | 4956 | 137 | GET | 200 | script | 2061 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/js/jquery.maskedinput.min.js |
| 47 | 4957 | 145 | GET | 200 | script | 1241 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/js/resumeable-upload.js |
| 48 | 4957 | 153 | GET | 200 | script | 4747 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/js/tus/tus.js |
| 49 | 4958 | 155 | GET | 200 | script | 1650 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/js/strength.js |
| 50 | 4959 | 159 | GET | 200 | script | 803 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/js/jquery.cookie.min.js |
| 51 | 4959 | 159 | GET | 200 | script | 1464 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/js/jquery.jclock.min.js |
| 52 | 4959 | 166 | GET | 200 | script | 6429 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/js/bootstrap-dialog.min.js |
| 53 | 4960 | 169 | GET | 200 | script | 1306 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/js/datatables-v1.config.js |
| 54 | 4960 | 190 | GET | 200 | script | 10020 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/js/bootstrap-datetimepicker.min |
| 55 | 4960 | 328 | GET | 200 | script | 164135 | www.googletagmanager.com | https://www.googletagmanager.com/gtag/js?id=G-KLDH3FQ7DR |
| 56 | 8020 | 41 | GET | 200 | script | 30796 | unpkg.com | https://unpkg.com/jquery@3.7.1/dist/jquery.min.js |
| 57 | 8081 | 41 | GET | 307 | other | 0 | spse.inaproc.id | https://spse.inaproc.id/jakarta/public/images/global/inaproc.png |
| 58 | 8099 | 39 | GET | 200 | script | 7931 | unpkg.com | https://unpkg.com/popper.js@1.16.1/dist/umd/popper.min.js |
| 59 | 8123 | 463 | GET | 200 | image | 10936 | storage.googleapis.com | https://storage.googleapis.com/spse-public-prod/public/images/global/i |
| 60 | 8142 | 34 | GET | 200 | script | 15683 | unpkg.com | https://unpkg.com/bootstrap@4.6.2/dist/js/bootstrap.min.js |
| 61 | 8184 | 34 | GET | 200 | script | 18957 | unpkg.com | https://unpkg.com/moment@2.29.4/min/moment.min.js |
| 62 | 8228 | 46 | GET | 200 | script | 30254 | unpkg.com | https://unpkg.com/datatables.net@1.13.5/js/jquery.dataTables.min.js |
| 63 | 8299 | 41 | GET | 200 | script | 1623 | unpkg.com | https://unpkg.com/datatables.net-bs4@1.13.5/js/dataTables.bootstrap4.m |
| 64 | 8346 | 36 | GET | 200 | script | 16295 | unpkg.com | https://unpkg.com/bootstrap-select@1.13.18/dist/js/bootstrap-select.mi |
| 65 | 8435 | 726 | POST | 200 | json | 2891 | spse.inaproc.id | https://spse.inaproc.id/jakarta/dt/lelang?tahun=2027 |
| 66 | 8445 | 36 | POST | 204 | xhr | 813 | spse.inaproc.id | https://spse.inaproc.id/cdn-cgi/rum? |

## Recommendations

- Cloudflare challenge in play — use a real browser (scrapy-playwright/stealth) to solve it, or reuse a valid `cf_clearance` cookie + the *exact* matching User-Agent.
- Persist & replay these cookies across requests: __cf_bm, cf_clearance, SPSE_ERRORS, SPSE_SESSION, SPSE_FLASH, _cfuvid
