<!-- Updated: 2026-09-25 -->
# GBP Profile Completeness Checklist (Via API)

This checklist scores a Google Business Profile using data retrieved from
the DataForSEO My Business Info API. It measures profile completeness on
the maps PLATFORM, not on-page signals (seo-local handles on-page).

## Sources and Evidence Levels

- [V] Google: [Tips to improve your local ranking (7091)](https://support.google.com/business/answer/7091),
  [Guidelines for representing your business (3038177)](https://support.google.com/business/answer/3038177),
  [Edit your Business Profile (3039617)](https://support.google.com/business/answer/3039617),
  [Service areas (9157481)](https://support.google.com/business/answer/9157481),
  [Posts (7342169)](https://support.google.com/business/answer/7342169). All fetched 2026-09-25.
- [H survey] Whitespark Local Search Ranking Factors 2026 (expert survey) and BrightLocal
  Local Consumer Review Survey 2026 (1,002 US adults). Label as "practitioner survey".
- [H] Everything else: the point scale, field groups, thresholds (counts, days) and industry
  multipliers are editorial heuristics. Label them "heuristic" in output.

Google says complete and accurate info makes a business "more likely to show up in local
search results" (7091). It does not publish per-field ranking weights. A low score here is
at most Medium severity unless the finding itself is a [V] guideline violation.

Register: `local-eeat-evidence.md`.

---

## Scoring System [H]

Each field: **Present + Optimized = 2pts**, **Present = 1pt**, **Missing = 0pts**

Total possible: 48 points (24 fields). Normalize to 0-100 scale: `(score / 48) * 100`

---

## Core Fields (Google-recommended profile info)

| # | Field | Points | Optimized Criteria |
|---|-------|--------|-------------------|
| 1 | **Primary category** | 2 | Most specific category for the business (e.g., "Cosmetic Dentist" not "Dentist") [H]. #1 local pack factor in Whitespark 2026 [H survey] |
| 2 | **Additional categories** | 2 | Relevant categories only (no Google-documented optimal number) |
| 3 | **Business name** | 2 | Matches real-world name; no unnecessary info [V 3038177] |
| 4 | **Physical address** | 2 | Complete (if customers visit) [V 7091]; matches website NAP [H] |
| 5 | **Phone number** | 2 | "Use a local phone number instead of a central call center helpline number whenever possible" [V 3038177]; matches website [H] |
| 6 | **Website URL** | 2 | Points to the page that best represents this location [H] |
| 7 | **Business hours** | 2 | Complete, incl. special hours [V 7091]. Open-at-search-time = #5 local pack factor in Whitespark 2026 [H survey] |
| 8 | **Verified status** | 2 | Verified: "more likely to show up in search results" [V 7091] |

**Subtotal: 16 points (8 fields)**

---

## Important Fields

| # | Field | Points | Optimized Criteria |
|---|-------|--------|-------------------|
| 9 | **Business description** | 2 | Google max 750 characters [V 3039617]; 250+ chars covering primary service and area [H] |
| 10 | **Services list** | 2 | All core services listed with descriptions [H] |
| 11 | **Products** | 2 | Key products/services with prices (if applicable) [H] |
| 12 | **Photos** | 2 | Photos recommended [V 7091]; 10+ across logo, cover, interior, exterior, team, products [H] |
| 13 | **Photo recency** | 2 | Photos uploaded within last 30 days [H] |
| 14 | **Attributes** | 2 | Relevant attributes set, e.g. parking, Wi-Fi [V 7091 examples] |
| 15 | **Service areas** | 2 | Defined for SABs; Google allows up to 20 service areas [V 9157481] |
| 16 | **Menu/services link** | 2 | Menu URL (restaurants) or services URL (others) [H] |

**Subtotal: 16 points (8 fields)**

---

## Supplementary Fields

| # | Field | Points | Optimized Criteria |
|---|-------|--------|-------------------|
| 17 | **Google Posts** | 2 | Post types: updates, offers, events [V 7342169]; 1+/week [H] |
| 18 | **Post recency** | 2 | Post within last 7 days [H] |
| 19 | **Booking link** | 2 | Appointment/reservation URL configured [H] |
| 20 | **Social profiles** | 2 | GBP social media links (select regions only [V 13580646]) or `sameAs` [H] |
| 21 | **Logo** | 2 | Square logo uploaded [H] |
| 22 | **Cover photo** | 2 | On-brand, high-resolution cover image [H] |
| 23 | **Videos** | 2 | At least 1 video [H]; Google recommends photos and videos [V 7091] |
| 24 | **Owner responses** | 2 | Reply to reviews [V 7091: replies show "you value their feedback"]. Optimized: replies to all or nearly all recent reviews [H]. Consumer data: 80% of consumers say they are likely to use a business that responds to all reviews; 42% unlikely if it never replies (BrightLocal LCRS 2026) [H survey] |

**Subtotal: 16 points (8 fields)**

Q&A is not scored: Google discontinued the My Business Q&A API on 2025-11-03 (GBP API sunset
page), and website FAQ content belongs to `/seo local`.

---

## Industry-Specific Weight Adjustments [H]

When scoring, apply multipliers to fields that matter more for specific industries
(editorial heuristics, not Google-documented):

### Restaurant
- Menu/services link: **x2** (critical for food-related searches)
- Photos: **x1.5** (food photos drive engagement)
- Booking link: **x1.5** (reservation systems expected)
- Attributes: **x1.5** (dietary, dine-in/takeout/delivery critical)

### Healthcare
- Business hours: **x1.5** (patients need accurate hours)
- Attributes: **x1.5** (insurance, accessibility, telehealth)
- Services list: **x2** (insurance and procedure matching)

### Legal
- Business description: **x1.5** (practice area clarity)
- Services list: **x2** (practice area matching)
- Photos: **x0.5** (less central for legal)

### Home Services
- Service areas: **x2** (SAB model depends on this)
- Business hours: **x1.5** (emergency availability)
- Photos: **x1.5** (before/after project photos)

### Real Estate
- Photos: **x2** (property photos critical)
- Social profiles: **x1.5** (agent branding)
- Posts: **x1.5** (listing updates)

### Automotive
- Products: **x2** (vehicle inventory)
- Photos: **x2** (vehicle photos)
- Services list: **x1.5** (sales + service departments)

### Re-normalization After Multipliers

After applying industry multipliers, re-normalize so the total remains 0-100:
```
final_score = (weighted_raw_score / max_possible_weighted_score) * 100
```
`max_possible_weighted_score` = sum over the 24 fields of `2 x multiplier` (48 with no
multipliers). This keeps scores comparable across industries.

---

## Score Interpretation [H]

| Score | Rating | Action |
|-------|--------|--------|
| 90-100 | Excellent | Maintain posting cadence and photo freshness |
| 75-89 | Good | Fill remaining gaps in supplementary fields |
| 50-74 | Needs Work | Address Core + Important gaps |
| 25-49 | Poor | Major profile gaps. Prioritize Core fields |
| 0-24 | Very poor | Profile barely exists or unclaimed. Start with verification + Core fields |

The rating is a heuristic label, not a severity. Severity follows the evidence rule above.

---

## Data Mapping (DataForSEO → Checklist)

| Checklist Field | DataForSEO My Business Info Field |
|----------------|----------------------------------|
| Primary category | `category` (`category_ids`) |
| Additional categories | `additional_categories` |
| Business name | `title` |
| Address | `address_info` |
| Phone | `phone` |
| Website | `url`, `domain` |
| Hours | `work_time.work_hours` (`timetable`, `current_status`) |
| Description | `description` |
| Services / Products | Not a documented response field: "Unknown (manual check required)" |
| Photos | `total_photos`, `main_image` |
| Logo | `logo` |
| Attributes | `attributes` (`available_attributes`, `unavailable_attributes`) |
| Booking / menu link | `book_online_url`, `local_business_links` (types `reservation`, `order`, `menu`) |
| Popular times | `popular_times` (informational, not scored) |
| Posts | My Business Updates API |
| Owner responses | Reviews API `owner_answer` per review |
| Verified status | `is_claimed` ("shows whether the entity is verified by its owner on Google Maps") |
