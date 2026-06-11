# HAR analysis — https://www.scrapingcourse.com/cloudflare-challenge

_Source: `har_file.har` · generated 2026-06-11T00:11:48+02:00_

## Verdict

- **Status:** 🟡 protected (delivered)
- Cloudflare, Cloudflare Turnstile present but the document was delivered — protection is passive.
- **Page title:** Cloudflare Challenge - ScrapingCourse.com
- **Captured:** 26 requests · 913 KiB · load 4725 ms · TTFB 63.2 ms

## Protection

### Cloudflare — CDN / WAF / Bot Management
- `header` **cf-ray** — cf-ray: a09bb6a51d4c5aab-VIE _(×21)_
- `header` **cf-mitigated** — cf-mitigated: challenge
- `header` **server** — server: cloudflare _(×21)_
- `url` **/cdn-cgi/challenge-platform/** — https://www.scrapingcourse.com/cdn-cgi/challenge-platform/h/g/orchestrate/chl_page/v1?ray=a09bb6a51d4c5aab _(×9)_
- `url` **challenges\.cloudflare\.com** — https://challenges.cloudflare.com/turnstile/v0/g/8fc8ed1d8752/api.js?onload=NoWu9&render=explicit _(×3)_
- `header` **cf-chl-out** — cf-chl-out: xDgD9zbGSK2UTCwqglfWQaGMX+A+fWCt7PoV48RxI9m7HGtr0Sm+1zOGAT7R+qzjIJa1ZLKyZ95oVCJT _(×2)_
- `cookie` **cf_clearance** — cf_clearance
- `header` **cf-cache-status** — cf-cache-status: DYNAMIC _(×8)_

### Cloudflare Turnstile — CAPTCHA / challenge widget
- `url` **challenges\.cloudflare\.com/turnstile** — https://challenges.cloudflare.com/turnstile/v0/g/8fc8ed1d8752/api.js?onload=NoWu9&render=explicit _(×3)_

## Landing document

- **Final:** HTTP 200 · text/html; charset=UTF-8 · h3 · 2867 B
- **Chain:** 307 → 403 → 200

**Request headers used:**

| header | value |
|---|---|
| User-Agent | Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Sa |
| Accept | text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/* |
| Referer | https://www.scrapingcourse.com/cloudflare-challenge?__cf_chl_tk=n5IM0wdH_mer1DBH.JfWygOauZ |
| sec-ch-ua | "Chromium";v="148", "Google Chrome";v="148", "Not/A)Brand";v="99" |
| sec-ch-ua-platform | "Linux" |
| sec-ch-ua-mobile | ?0 |
| Upgrade-Insecure-Requests | 1 |

## Session cookies

| cookie | set by | attributes |
|---|---|---|
| `cf_clearance` | www.scrapingcourse.com | HttpOnly; SameSite=None; Partitioned; Secure; Path=/; Domain=scrapingcourse.com; Expires=Thu, 10 Jun 2027 22:11:47 GMT |
| `AWSALB` | www.scrapingcourse.com | Expires=Wed, 17 Jun 2026 22:11:47 GMT; Path=/ |
| `AWSALBCORS` | www.scrapingcourse.com | Expires=Wed, 17 Jun 2026 22:11:47 GMT; Path=/; SameSite=None; Secure |
| `XSRF-TOKEN` | www.scrapingcourse.com | expires=Thu, 11 Jun 2026 00:11:47 GMT; Max-Age=7200; path=/; samesite=lax |
| `scrapingcoursecom_session` | www.scrapingcourse.com | expires=Thu, 11 Jun 2026 00:11:47 GMT; Max-Age=7200; path=/; httponly; samesite=lax |

## Data endpoints (direct-scrape candidates)

No JSON/API responses observed (page is likely server-rendered HTML).

## Hosts contacted

| host | requests | bytes | protection |
|---|---|---|---|
| www.scrapingcourse.com | 11 | 185743 | ⚠️ |
| challenges.cloudflare.com | 9 | 513468 | ⚠️ |
| stackpath.bootstrapcdn.com | 2 | 41539 |  |
| code.jquery.com | 1 | 24937 |  |
| cdn.jsdelivr.net | 1 | 6978 |  |
| www.googletagmanager.com | 1 | 164307 |  |
| region1.google-analytics.com | 1 | 0 |  |

## Statistics

- **By status:** -1×1, 200×21, 302×1, 307×1, 401×1, 403×1
- **By type:** script×9, document×5, xhr×4, image×4, other×2, stylesheet×2

## Request timeline

| # | +ms | dur | method | status | type | size | host | url |
|---|---|---|---|---|---|---|---|---|
| 0 | 0 | 41 | GET | 307 | other | 97 | www.scrapingcourse.com | https://www.scrapingcourse.com/cloudflare-challenge |
| 1 | 40 | 12 | GET | 403 | document | 5435 | www.scrapingcourse.com | https://www.scrapingcourse.com/cloudflare-challenge |
| 2 | 78 | 46 | GET | 200 | script | 69290 | www.scrapingcourse.com | https://www.scrapingcourse.com/cdn-cgi/challenge-platform/h/g/orchestr |
| 3 | 144 | 80 | GET | 200 | script | 21853 | challenges.cloudflare.com | https://challenges.cloudflare.com/turnstile/v0/g/8fc8ed1d8752/api.js?o |
| 4 | 288 | 27 | POST | 200 | xhr | 16576 | www.scrapingcourse.com | https://www.scrapingcourse.com/cdn-cgi/challenge-platform/h/g/flow/ov1 |
| 5 | 342 | 50 | GET | 200 | document | 86572 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/turns |
| 6 | 413 | 33 | GET | 200 | image | 208 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/cmg/1 |
| 7 | 607 | 217 | POST | 200 | xhr | 371469 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/flow/ |
| 8 | 3157 | 16 | GET | 200 | image | 1835 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/d/a09 |
| 9 | 3530 | 18 | GET | 401 | xhr | 1700 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/pat/a |
| 10 | 3654 | 62 | POST | 200 | document | 7987 | challenges.cloudflare.com | https://challenges.cloudflare.com/cdn-cgi/challenge-platform/h/g/flow/ |
| 11 | 3749 | 55 | POST | 200 | document | 4801 | www.scrapingcourse.com | https://www.scrapingcourse.com/cdn-cgi/challenge-platform/h/g/flow/ov1 |
| 12 | 3819 | 300 | POST | 200 | document | 2867 | www.scrapingcourse.com | https://www.scrapingcourse.com/cloudflare-challenge |
| 13 | 4142 | 78 | GET | 200 | stylesheet | 25485 | stackpath.bootstrapcdn.com | https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.c |
| 14 | 4143 | 70 | GET | 302 | script | 0 | challenges.cloudflare.com | https://challenges.cloudflare.com/turnstile/v0/api.js |
| 15 | 4144 | 154 | GET | 200 | stylesheet | 4927 | www.scrapingcourse.com | https://www.scrapingcourse.com/build/assets/app-DxJb4DfE.css |
| 16 | 4144 | 160 | GET | 200 | script | 13457 | www.scrapingcourse.com | https://www.scrapingcourse.com/build/assets/app-D2jpX1vH.js |
| 17 | 4145 | 101 | GET | 200 | script | 24937 | code.jquery.com | https://code.jquery.com/jquery-3.5.1.slim.min.js |
| 18 | 4145 | 421 | GET | 200 | script | 6978 | cdn.jsdelivr.net | https://cdn.jsdelivr.net/npm/@popperjs/core@2.5.2/dist/umd/popper.min. |
| 19 | 4187 | 26 | GET | 200 | script | 21844 | challenges.cloudflare.com | https://challenges.cloudflare.com/turnstile/v0/g/8fc8ed1d8752/api.js |
| 20 | 4205 | 105 | GET | 200 | script | 16054 | stackpath.bootstrapcdn.com | https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/js/bootstrap.min.js |
| 21 | 4206 | 274 | GET | 200 | script | 164307 | www.googletagmanager.com | https://www.googletagmanager.com/gtag/js?id=G-NZGD14H87G |
| 22 | 4206 | 215 | GET | 200 | image | 1192 | www.scrapingcourse.com | https://www.scrapingcourse.com/assets/images/logo.svg |
| 23 | 4207 | 216 | GET | 200 | image | 1407 | www.scrapingcourse.com | https://www.scrapingcourse.com/assets/images/challenge.svg |
| 24 | 4339 | 182 | GET | 200 | xhr | 65694 | www.scrapingcourse.com | https://www.scrapingcourse.com/assets/fonts/SpaceGrotesk-VariableFont_ |
| 25 | 4460 | -1 | POST | -1 | other | 0 | region1.google-analytics.com | https://region1.google-analytics.com/g/collect?v=2&tid=G-NZGD14H87G&gt |

## Recommendations

- Cloudflare challenge in play — use a real browser (scrapy-playwright/stealth) to solve it, or reuse a valid `cf_clearance` cookie + the *exact* matching User-Agent.
- Persist & replay these cookies across requests: cf_clearance, AWSALB, AWSALBCORS, XSRF-TOKEN, scrapingcoursecom_session
