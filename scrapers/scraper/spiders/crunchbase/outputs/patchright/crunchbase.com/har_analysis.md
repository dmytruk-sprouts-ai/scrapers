# HAR analysis — https://www.crunchbase.com/organization/nvidia

_Source: `har_file.har` · generated 2026-06-10T16:43:13+02:00_

## Verdict

- **Status:** 🟡 protected (delivered)
- Cloudflare, Cloudflare Turnstile present but the document was delivered — protection is passive.
- **Page title:** NVIDIA - Crunchbase Company Profile & Funding
- **Captured:** 52 requests · 926 KiB · load 6320 ms · TTFB 111.8 ms

## Protection

### Cloudflare — CDN / WAF / Bot Management
- `header` **cf-ray** — cf-ray: a099256ec8d2c4f7-VIE _(×25)_
- `header` **cf-mitigated** — cf-mitigated: challenge
- `header` **server** — server: cloudflare _(×25)_
- `url` **/cdn-cgi/challenge-platform/** — https://www.crunchbase.com/cdn-cgi/challenge-platform/h/g/orchestrate/chl_page/v1?ray=a099256ec8d2c4f7 _(×12)_
- `cookie` **__cf_bm** — __cf_bm _(×6)_
- `url` **challenges\.cloudflare\.com** — https://challenges.cloudflare.com/turnstile/v0/g/8fc8ed1d8752/api.js?onload=NoWu9&render=explicit
- `header` **cf-chl-out** — cf-chl-out: d4ydsUWFSYOyKagkQSrPN1Xks7P/iXbyQmJzQ6xWzGnOQ9RKirbNcdBfAEUEnSJhHKAJx219jM/l5GvT _(×2)_
- `cookie` **cf_clearance** — cf_clearance _(×2)_
- `header` **cf-cache-status** — cf-cache-status: DYNAMIC _(×10)_

### Cloudflare Turnstile — CAPTCHA / challenge widget
- `url` **challenges\.cloudflare\.com/turnstile** — https://challenges.cloudflare.com/turnstile/v0/g/8fc8ed1d8752/api.js?onload=NoWu9&render=explicit

## Landing document

- **Final:** HTTP 200 · text/html; charset=utf-8 · HTTP/2.0 · 116946 B
- **Chain:** 307 → 403 → 200

**Request headers used:**

| header | value |
|---|---|
| User-Agent | Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Sa |
| Accept | text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/* |
| Referer | https://www.crunchbase.com/organization/nvidia?__cf_chl_tk=N8vPCxXPLopVUO3pCeG1iAepf8dt.yq |
| sec-ch-ua | "Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99" |
| sec-ch-ua-platform | "Linux" |
| sec-ch-ua-mobile | ?0 |
| Upgrade-Insecure-Requests | 1 |

## Session cookies

| cookie | set by | attributes |
|---|---|---|
| `__cf_bm` | www.crunchbase.com | HttpOnly; SameSite=None; Secure; Path=/; Domain=crunchbase.com; Expires=Wed, 10 Jun 2026 15:13:04 GMT |
| `cf_clearance` | www.crunchbase.com | HttpOnly; SameSite=None; Partitioned; Secure; Path=/; Domain=crunchbase.com; Expires=Thu, 10 Jun 2027 14:43:08 GMT |
| `cb_analytics_consent` | www.crunchbase.com | Expires=Fri, 09-Jun-28 14:43:09 GMT; Path=/ |
| `cid` | www.crunchbase.com | expires=Fri, 09-Jun-28 14:43:09 GMT; domain=.crunchbase.com; path=/ |

## Data endpoints (direct-scrape candidates)

| method | status | size | url |
|---|---|---|---|
| GET | 200 | 2600 B | https://cdn.cookielaw.org/consent/d71c660f-7eb5-4a5e-983e-ca1d7f1e56d4/d71c660f-7eb5-4a5e- |
| GET | 200 | 288 B | https://geolocation.onetrust.com/cookieconsentpub/v1/geo/location |
| GET | 200 | 18870 B | https://cdn.cookielaw.org/consent/d71c660f-7eb5-4a5e-983e-ca1d7f1e56d4/019d9788-16a1-7e8a- |
| GET | 200 | 2946 B | https://cdn.cookielaw.org/scripttemplates/202304.1.0/assets/otFloatingRounded.json |

## Hosts contacted

| host | requests | bytes | protection |
|---|---|---|---|
| images.crunchbase.com | 25 | 59497 |  |
| www.crunchbase.com | 11 | 232716 | ⚠️ |
| challenges.cloudflare.com | 7 | 492985 | ⚠️ |
| cdn.cookielaw.org | 7 | 137527 |  |
| fonts.gstatic.com | 1 | 26861 |  |
| geolocation.onetrust.com | 1 | 288 |  |

## Statistics

- **By status:** 200×48, 302×1, 307×1, 401×1, 403×1
- **By type:** image×29, script×6, document×5, xhr×4, json×4, stylesheet×2, other×1, font×1

## Request timeline

| # | +ms | dur | method | status | type | size | host | url |
|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 81 | GET | 307 | other | 92 | www.crunchbase.com | https://www.crunchbase.com/organization/nvidia |
| 1 | 81 | 14 | GET | 403 | document | 4746 | www.crunchbase.com | https://www.crunchbase.com/organization/nvidia |
| 2 | 145 | 45 | GET | 200 | script | 65229 | www.crunchbase.com | https://www.crunchbase.com/cdn-cgi/challenge-platform/h/g/orchestrate/ |
| 3 | 210 | 148 | GET | 200 | script | 21850 | challenges.cloudflare.com | https://challenges.cloudflare.com/turnstile/v0/g/8fc8ed1d8752/api.js?o |
| 4 | 355 | 45 | POST | 200 | xhr | 16709 | www.crunchbase.com | https://www.crunchbase.com/cdn-cgi/challenge-platform/h/g/flow/ov1/216 |
| 5 | 424 | 50 | GET | 200 | document | 89215 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/turns |
| 6 | 496 | 38 | GET | 200 | image | 208 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/cmg/1 |
| 7 | 709 | 131 | POST | 200 | xhr | 371654 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/flow/ |
| 8 | 1318 | 21 | GET | 401 | xhr | 1702 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/pat/a |
| 9 | 1561 | 19 | GET | 200 | image | 450 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/d/a09 |
| 10 | 3984 | 49 | POST | 200 | document | 7906 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/flow/ |
| 11 | 4060 | 51 | POST | 200 | document | 5017 | www.crunchbase.com | https://www.crunchbase.com/cdn-cgi/challenge-platform/h/g/flow/ov1/216 |
| 12 | 4131 | 1905 | POST | 200 | document | 116946 | www.crunchbase.com | https://www.crunchbase.com/organization/nvidia |
| 13 | 5872 | 51 | GET | 200 | stylesheet | 10732 | www.crunchbase.com | https://www.crunchbase.com/styles.20274c59d7011192.css |
| 14 | 5872 | 111 | GET | 200 | script | 9293 | cdn.cookielaw.org | https://cdn.cookielaw.org/scripttemplates/otSDKStub.js |
| 15 | 5872 | 36 | GET | 200 | image | 10669 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,w_2000,f_auto,q_auto: |
| 16 | 5931 | 69 | GET | 200 | image | 1797 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_160,w_160,f_auto,b_ |
| 17 | 6059 | 240 | GET | 200 | font | 26861 | fonts.gstatic.com | https://fonts.gstatic.com/s/publicsans/v21/ijwRs572Xtc6ZYQws9YVwnNGfJ4 |
| 18 | 6059 | 44 | GET | 200 | image | 1063 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_thumb,h_50,w_50,f_auto,g_ |
| 19 | 6060 | 45 | GET | 200 | image | 1126 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_thumb,h_50,w_50,f_auto,g_ |
| 20 | 6068 | 76 | GET | 200 | json | 2600 | cdn.cookielaw.org | https://cdn.cookielaw.org/consent/d71c660f-7eb5-4a5e-983e-ca1d7f1e56d4 |
| 21 | 6124 | 77 | GET | 200 | image | 13177 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,w_2000,f_auto,q_auto: |
| 22 | 6124 | 84 | GET | 200 | image | 1543 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_15,f_auto,q_auto:ec |
| 23 | 6125 | 84 | GET | 200 | image | 1531 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_15,f_auto,q_auto:ec |
| 24 | 6125 | 86 | GET | 200 | image | 2034 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_15,f_auto,q_auto:ec |
| 25 | 6125 | 89 | GET | 200 | image | 4098 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_15,f_auto,q_auto:ec |
| 26 | 6125 | 103 | GET | 200 | image | 3170 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_15,f_auto,q_auto:ec |
| 27 | 6125 | 109 | GET | 200 | image | 5952 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_15,f_auto,q_auto:ec |
| 28 | 6126 | 109 | GET | 200 | image | 746 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_40,w_40,f_auto,q_au |
| 29 | 6126 | 112 | GET | 200 | image | 1026 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_40,w_40,f_auto,q_au |
| 30 | 6126 | 112 | GET | 200 | image | 883 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_40,w_40,f_auto,q_au |
| 31 | 6126 | 111 | GET | 200 | image | 981 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_40,w_40,f_auto,q_au |
| 32 | 6127 | 117 | GET | 200 | image | 801 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_40,w_40,f_auto,q_au |
| 33 | 6127 | 120 | GET | 200 | image | 749 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_40,w_40,f_auto,q_au |
| 34 | 6127 | 122 | GET | 200 | image | 817 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_40,w_40,f_auto,q_au |
| 35 | 6127 | 124 | GET | 200 | image | 1234 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_40,w_40,f_auto,q_au |
| 36 | 6128 | 126 | GET | 200 | image | 1045 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_40,w_40,f_auto,q_au |
| 37 | 6128 | 131 | GET | 200 | image | 814 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_40,w_40,f_auto,q_au |
| 38 | 6128 | 130 | GET | 200 | image | 1166 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_40,w_40,f_auto,q_au |
| 39 | 6128 | 138 | GET | 200 | image | 748 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_40,w_40,f_auto,q_au |
| 40 | 6129 | 139 | GET | 200 | image | 805 | images.crunchbase.com | https://images.crunchbase.com/image/upload/c_pad,h_40,w_40,f_auto,q_au |
| 41 | 6129 | 139 | GET | 200 | image | 1522 | images.crunchbase.com | https://images.crunchbase.com/image/upload/v1613675726/clientapp/logo_ |
| 42 | 6212 | 86 | GET | 302 | script | 0 | www.crunchbase.com | https://www.crunchbase.com/cdn-cgi/challenge-platform/scripts/jsd/main |
| 43 | 6289 | 86 | GET | 200 | json | 288 | geolocation.onetrust.com | https://geolocation.onetrust.com/cookieconsentpub/v1/geo/location |
| 44 | 6294 | 12 | GET | 200 | script | 10675 | www.crunchbase.com | https://www.crunchbase.com/cdn-cgi/challenge-platform/h/g/scripts/jsd/ |
| 45 | 6412 | 92 | GET | 200 | script | 99314 | cdn.cookielaw.org | https://cdn.cookielaw.org/scripttemplates/202304.1.0/otBannerSdk.js |
| 46 | 6412 | 83 | GET | 200 | image | 1701 | www.crunchbase.com | https://www.crunchbase.com/favicon.ico?v=2.0 |
| 47 | 6465 | 29 | POST | 200 | xhr | 869 | www.crunchbase.com | https://www.crunchbase.com/cdn-cgi/challenge-platform/h/g/jsd/oneshot/ |
| 48 | 6496 | 34 | GET | 200 | json | 18870 | cdn.cookielaw.org | https://cdn.cookielaw.org/consent/d71c660f-7eb5-4a5e-983e-ca1d7f1e56d4 |
| 49 | 6542 | 26 | GET | 200 | json | 2946 | cdn.cookielaw.org | https://cdn.cookielaw.org/scripttemplates/202304.1.0/assets/otFloating |
| 50 | 6542 | 27 | GET | 200 | stylesheet | 3901 | cdn.cookielaw.org | https://cdn.cookielaw.org/scripttemplates/202304.1.0/assets/otCommonSt |
| 51 | 6634 | 57 | GET | 200 | image | 603 | cdn.cookielaw.org | https://cdn.cookielaw.org/logos/static/ot_close.svg |

## Recommendations

- Cloudflare challenge in play — use a real browser (scrapy-playwright/stealth) to solve it, or reuse a valid `cf_clearance` cookie + the *exact* matching User-Agent.
- Persist & replay these cookies across requests: __cf_bm, cf_clearance, cb_analytics_consent, cid
- 4 JSON/API endpoint(s) seen — consider scraping them directly instead of parsing HTML (check whether they need the session cookies above).
