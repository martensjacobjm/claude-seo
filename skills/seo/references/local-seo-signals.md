<!-- Updated: 2026-09-25 -->
# Local SEO Ranking Signals & Benchmarks

Register with URLs, dates and removed claims: `local-eeat-evidence.md`.

## Evidence Levels

| Tag | Meaning | Severity cap |
|-----|---------|--------------|
| [V] | Vendor-documented (Google Business Profile Help, Search Central, Bing, Apple) or law (FTC, HHS) | Any |
| [H survey] | Practitioner survey (Whitespark, BrightLocal): opinions or consumer self-reports, not Google facts | Medium; say "practitioner survey" or "heuristic" |
| [H] | Practitioner rule of thumb | Medium; say "heuristic" |

Only [V] may drive Critical or High. Never present a survey figure as a Google ranking fact.

---

## What Google Says About Local Ranking [V]

Google Business Profile Help, "Tips to improve your local ranking on Google" (fetched
2026-09-25):

- "Local results are mainly based on relevance, distance, and popularity." The page then
  defines **Relevance**, **Distance** and **Prominence**.
- Prominence is "based on info like how many websites link to your business and how many
  reviews you have. More reviews and positive ratings can help your business's local ranking."
- "There's no way to request or pay for a better local ranking on Google."
- Recommended actions: verify the business, keep information complete and accurate (address,
  hours including special hours, category, attributes), respond to reviews, add photos and
  videos, add in-store products (retail, eligible countries).
- The current page does not mention directories or citations.

GBP guidelines [V]: the business name "should reflect your business's real-world name";
"Including unnecessary information in your business name isn't permitted, and could result
in the suspension of your Business Profile." Keyword-stuffed names are a policy risk.

---

## Whitespark Local Search Ranking Factors 2026 [H survey]

Practitioner survey published 2025-11-06: 47 invited local SEO experts scored 187 factors
(0 to 5). Whitespark: "None of the experts have special access to the internal workings of
Google's local search algorithm." Expert opinion, not measurement.

**Factor group weights (experts' estimates):**

| Group | Local pack/Maps | Local organic |
|-------|-----------------|---------------|
| GBP signals | 32% | 7% |
| Review signals | 20% | 6% |
| On-page signals | 15% | 33% |
| Behavioural signals | 9% | 10% |
| Link signals | 8% | 24% |
| Citation signals | 6% | 7% |
| Personalization | 6% | 8% |
| Social signals | 4% | 5% |

**Top local pack/Maps factors (score):** 1. Primary GBP Category (227); 2. Proximity of address
to the point of search (225); 3. Keywords in GBP Business Title (223); 4. Physical address in
city of search (213); 5. Business is open at time of search (189); 6. High numerical Google
ratings (181); 7. Address showing on GBP, not SAB (176); 8. Additional GBP categories (173);
9. Quantity of native Google reviews with text (170).

Factor 3 conflicts with GBP name guidelines: report it, never recommend adding keywords to a
business name.

**Top local organic factors:** 1. Dedicated page for each service (210); 2. Geographic keyword
relevance of content (190); 3. Quality/authority of inbound links to domain (187).

**Top negative factors:** 1. Business marked as permanently closed (217); 2. Incorrect primary
category (214); 3. Other profiles in the same category at the same address (188).

The survey's "AI search visibility" scores are not used (see `geo-evidence.md`, Removed claims).

---

## Reviews

### Policy and law [V]

- **Google Maps fake engagement policy:** do not "Discourage or prohibit negative reviews, or
  selectively solicit positive reviews from customers", and do not offer incentives for
  reviews. Review gating falls under this.
- **FTC guidance** (Soliciting and Paying for Online Reviews, 2022): "Don't ask for reviews
  only from customers you think will leave positive ones."
- **FTC Consumer Review Rule** (16 CFR Part 465): published 2024-08-22, effective 2024-10-21.
  Covers fake reviews, incentives conditioned on sentiment, and review suppression (465.7).
  Civil penalty for rule violations: up to $53,088 per violation (16 CFR 1.98, current
  eCFR; no 2026 inflation adjustment).
- **Google structured data:** a business's own reviews in LocalBusiness markup are not
  eligible for star snippets (see `local-schema-types.md`).
- **Google enforcement:** "blocked or removed more than 240 million policy-violating reviews
  from 2024" (Google blog, 2025-04-07); "over 292 million policy-violating reviews" in 2025
  (Google blog, 2026-04-16).

### Consumer behavior: BrightLocal Local Consumer Review Survey 2026 [H survey]

Published 2026-02-11; representative panel of 1,002 US adult consumers (SurveyMonkey).
Self-reported attitudes, not ranking data.

| Finding | Value |
|---------|-------|
| "Always" read reviews when browsing for businesses | 41% (29% in 2025) |
| Only use a business with 4.5+ stars | 31% (17% in 2025) |
| Only use a business with 4+ stars | 68% (55% in 2025) |
| Seek reviews written in the last three months | 74% |
| Review sites used by the average consumer | 6 |
| Unlikely to use a business that never replies to reviews | 42% |
| Apple Maps usage for reviews/recommendations | 27% (14% in 2025) |

---

## Citation Sources

### Tier 1 platforms

| Source | Why it matters |
|--------|----------------|
| Google Business Profile | Google's own local listing; verification and complete info are Google-recommended [V] |
| Apple Business (formerly Apple Business Connect; businessconnect.apple.com redirects to business.apple.com) | Apple: "Put your business on the map"; Maps listing, custom actions, insights [V] |
| Bing Places for Business | Keeps address, hours and contact details current and "eligible for inclusion in AI-generated responses" (Bing Webmaster blog, 2026-02; see `geo-evidence.md`) [V] |
| Facebook, Yelp | Widely used consumer platforms [H] |

### Tier 2 and aggregators [H]

BBB, Yellow Pages, Nextdoor, Foursquare; data aggregators such as Data Axle and Foursquare
distribute listings to other platforms. No partnership or reach figures are claimed.
Industry-specific directories: see `local-schema-types.md`.

---

## GBP Feature Changes [V]

| Change | Date | Source |
|--------|------|--------|
| Chat and call history removed from Business Profile | 2024-07-31 | GBP Help 14919056 |
| My Business Q&A API discontinued (support ended 2025-09-15) | 2025-11-03 | GBP API sunset dates |
| My Business Business Calls API deprecated | 2023-05-30 | GBP API sunset dates |
| Local Services Ads: single "Google Verified" badge replaces earlier LSA badges; Money Back Guarantee discontinued | 2025 | Local Services Help 16498018 |

"Google Verified" is a Local Services Ads badge, not an organic GBP feature. Consumer-facing
Q&A: the API is gone; re-home useful Q&A as FAQ content on the website [H].

---

## Google Ranking Updates 2025-2026 [V]

Google Search Status Dashboard (start date, duration). Google publishes no local-specific
impact for these; do not attribute a local ranking change to an update without data.

| Update | Start | Duration |
|--------|-------|----------|
| March 2025 core update | 2025-03-13 | 13 days, 21 hours |
| June 2025 core update | 2025-06-30 | 16 days, 18 hours |
| August 2025 spam update | 2025-08-26 | 26 days, 15 hours |
| December 2025 core update | 2025-12-11 | 18 days, 2 hours |
| February 2026 Discover update | 2026-02-05 | 21 days, 17 hours |
| March 2026 spam update | 2026-03-24 | 19 hours, 30 minutes |
| March 2026 core update | 2026-03-27 | 12 days, 4 hours |
| May 2026 core update | 2026-05-21 | 11 days, 21 hours |
| June 2026 spam update | 2026-06-24 | 2 days, 1 hour |
| August 2026 spam update | 2026-08-18 | 2 days, 16 hours |
| September 2026 spam update | 2026-09-24 | ongoing at fetch |

---

## Proximity and Intent [H]

- Distance is a documented factor [V]; how far it reaches varies by query, category and
  density of competitors (heuristic, no fixed radius is documented).
- Service-area businesses: GBP says the service area "shouldn't extend farther than about 2
  hours of driving time from where your business is based", adding "For some businesses,
  larger service areas may be appropriate" [V].
- AI search and local: vendor statements only, see `skills/seo-geo/references/geo-evidence.md`.
