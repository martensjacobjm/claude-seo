---
name: seo-local
description: >
  Local SEO analysis covering Google Business Profile optimization, NAP
  consistency, citation health, review signals, local schema markup,
  location page quality, multi-location SEO, and industry-specific
  recommendations. Detects business type (brick-and-mortar, SAB, hybrid)
  and industry vertical (restaurant, healthcare, legal, home services,
  real estate, automotive). Use when user says "local SEO", "Google
  Business Profile", "GBP", "map pack", "local pack", "citations",
  "NAP consistency", "local rankings", "service area", "multi-location",
  or "local search".
user-invokable: true
argument-hint: "[url]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "1.8.1"
  category: seo
---

# Local SEO Analysis

## Evidence Rules

Every claim below traces to `skills/seo/references/local-eeat-evidence.md`. Add a row there
(with a fetched primary source) before adding any new number, date or vendor claim.

- [V] vendor-documented (Google, Bing, Apple, schema.org) or law (FTC, HHS). Only [V] may
  drive Critical or High.
- [H survey] practitioner survey (Whitespark 2026, BrightLocal 2026): expert opinion or
  consumer self-reports, never a Google fact. Medium at most; say "practitioner survey".
- [H] heuristic. Medium at most; say "heuristic".

## Key Facts

| Fact | Level | Source |
|------|-------|--------|
| Local results are "mainly based on relevance, distance, and popularity" (prominence) | [V] | GBP Help, local ranking tips |
| More reviews and positive ratings "can help" local ranking; links to the business count toward prominence | [V] | GBP Help, local ranking tips |
| No way to request or pay for better local ranking | [V] | GBP Help, local ranking tips |
| Experts estimate GBP signals at 32% and review signals at 20% of local pack weight | [H survey] | Whitespark LSRF 2026 (47 experts) |

---

## Business Type Detection

Detect from page signals before analysis. This determines which checks apply.

### Brick-and-Mortar
- Physical street address visible in page content or footer
- Google Maps embed with pin/directions
- "Visit us at", "Located at", "Come see us"
- Structured address in LocalBusiness schema

### Service Area Business (SAB)
- No visible physical address
- Service area mentions: "serving [city/region]", "service area includes"
- "We come to you", "On-site service", "Mobile [service]"
- `areaServed` in schema without `address.streetAddress`

### Hybrid
- Both physical address AND service area language present
- "Visit our showroom" combined with "We also serve [areas]"

**Impact on checks**: SABs skip embedded map verification and physical address consistency. Brick-and-mortar gets full NAP + map checks.

---

## Industry Vertical Detection

Detect from page signals and GBP category patterns. Routes to industry-specific checks from `references/local-schema-types.md`.

| Vertical | Detection Signals |
|----------|------------------|
| **Restaurant** | /menu, menu items, reservations, cuisine types, food ordering, "dine-in", "takeout" |
| **Healthcare** | insurance accepted, patients, appointments, NPI, medical terms, "Dr.", HIPAA notice |
| **Legal** | attorney, lawyer, practice areas, bar admission, case results, "free consultation" |
| **Home Services** | service area, emergency service, "free estimate", licensed/insured/bonded, "24/7" |
| **Real Estate** | listings, MLS, properties for sale/rent, agent bio, brokerage, "open house" |
| **Automotive** | inventory, VIN, test drive, dealership, service department, "new/used/certified" |

If no vertical detected, use generic `LocalBusiness` analysis path.

---

## Analysis Dimensions

Dimension weights (25/20/20/15/10/10) are an editorial heuristic [H]; Google publishes no weights.

### 1. GBP Signals (25%)

Google lists "What kind of business you are" (category), address, hours and attributes as info to provide [V]. Practitioner survey: primary GBP category ranks #1 of the local pack factors (Whitespark 2026, score 227) and an incorrect primary category #2 of the negative factors (score 214) [H survey].

**Check for:**
- GBP embed or reference detectable on page (Maps iframe, place ID, reviews widget)
- Primary category appropriateness (infer from page content vs visible GBP data)
- Evidence of relevant secondary categories (no Google-documented optimal number)
- GBP posts presence (Info only; no documented ranking effect)
- Photos/video evidence (Google recommends adding photos and videos [V])
- Q&A content: the My Business Q&A API was discontinued 2025-11-03 [V]; re-home useful questions as an FAQ section on the website [H]
- Google Verified badge: a Local Services Ads badge, relevant only if the business runs LSA [V]
- Business name: flag keywords or taglines in the GBP name; GBP guidelines say unnecessary information in the name "isn't permitted" and can lead to suspension [V]
- Business hours visible on page and complete in GBP, including special hours [V]. "Business is open at time of search" is #5 in the Whitespark 2026 survey [H survey]

**Scoring guide:**
- Full: GBP embed present, category signals align, posts active, photos present
- Partial: Some GBP signals present but incomplete
- Low: No visible GBP integration on website

### 2. Reviews & Reputation (20%)

Google: "More reviews and positive ratings can help your business's local ranking", and replying to reviews is a recommended action [V]. No review count threshold or cadence is Google-documented.

**Check for:**
- Total Google review count visible on page
- Star rating (practitioner survey: 31% of consumers say they only use 4.5+ stars, 68% only 4+; BrightLocal LCRS 2026, 1,002 US adults [H survey])
- Review recency indicators (74% seek reviews from the last three months, same survey [H survey])
- Self-serving `aggregateRating`/`review` markup on the business's own site: not eligible for star snippets, including embedded Google or Facebook review widgets [V]. Report as Info; do not recommend adding it
- Third-party review presence (average consumer uses 6 review sites, same survey [H survey])
- Owner response patterns (42% say they are unlikely to use a business that never replies, same survey [H survey])
- Review gating detection: Google's fake engagement policy does not allow businesses to "Discourage or prohibit negative reviews, or selectively solicit positive reviews from customers" [V]; FTC guidance: "Don't ask for reviews only from customers you think will leave positive ones" [V]. FTC Consumer Review Rule (effective 2024-10-21) violations such as fake or sentiment-conditioned incentivized reviews and review suppression carry civil penalties up to $53,088 per violation [V]

**Industry-specific:**
- Healthcare: never disclose patient information in a reply; HHS OCR settled for $30,000 with a provider that disclosed PHI in responses to negative online reviews (2023) [V]
- Legal: attorney-client privilege considerations in review responses

**Scoring guide:**
- Full: steady recent reviews, high rating, owner responses, multi-platform presence
- Partial: Some reviews but gaps in recency, rating, or response rate
- Low: few reviews, no recent activity, no responses, single platform only
- Thresholds are heuristics [H]; Google publishes none

### 3. Local On-Page SEO (20%)

Practitioner survey: "Dedicated Page for Each Service" ranks #1 of the local organic factors (Whitespark 2026, score 210) [H survey].

**Check for:**
- Title tag contains city/service keywords
- H1 tag with local intent (city + service)
- NAP (Name, Address, Phone) visible in page HTML (footer, contact section, header)
- Dedicated service pages (one page per core service)
- Location page quality for multi-location sites:
  - Doorway abuse [V]: Google's spam policies list "multiple domain names or pages targeted at specific regions or cities that funnel users to one page" and "substantially similar pages"
  - **>60-70% unique content** (heuristic [H], no Google-confirmed threshold)
  - **Swap test** [H]: if you can swap the city name and the content still makes sense, treat it as doorway risk
  - Local photos, area-specific testimonials, local FAQs
- Embedded Google Map (geographic signal reinforcement, not direct ranking factor -- lazy-load to mitigate speed impact)
- Click-to-call button (`tel:` link) and contact form above the fold
- Internal linking architecture: hub-and-spoke, critical pages a few clicks from the homepage [H]
- Contextual internal links with descriptive anchor text (Google link best practices [V]; no link count is documented)

**Multi-location specific:**
- Store locator with individual crawlable URLs (SSR/SSG preferred over CSR)
- Subdirectory structure: `domain.com/locations/city-name/` (heuristic [H])
- Each location page has unique LocalBusiness schema with `@id`

**Scoring guide:**
- Full: City in title + H1, NAP visible, dedicated service pages, no doorway patterns, good internal linking
- Partial: Some local signals but missing service pages or doorway page risk
- Low: Generic title/H1, NAP not visible, thin location pages

### 4. NAP Consistency & Citations (15%)

Google's local ranking help page (fetched 2026-09-25) names links and reviews under prominence and does not mention directories or citations [V]. Practitioner survey: citation signals 6% of local pack weight (Whitespark 2026) [H survey]. NAP consistency is a heuristic for accurate data [H]; Google's documented requirement is accurate, complete GBP info [V].

**Check for:**
- NAP extraction: compare Name, Address, Phone from:
  1. Visible page HTML (footer, contact page)
  2. LocalBusiness JSON-LD schema
  3. Any visible GBP data
  - Flag any discrepancies between these three sources
- Citation presence on Tier 1 directories (check via WebFetch or site: search patterns):
  - Google Business Profile signals on page
  - Yelp: `site:yelp.com "Business Name"`
  - BBB: `site:bbb.org "Business Name"`
  - Facebook business page references
- Apple Business awareness (formerly Apple Business Connect; Maps listing and custom actions [V]). Survey: 27% of consumers use Apple Maps for reviews/recommendations, up from 14% (BrightLocal 2026 [H survey]). Recommend claiming
- Bing Places awareness (helps keep address, hours and contact details current and eligible for inclusion in Bing/Copilot AI-generated responses, per Bing Webmaster blog 2026-02-10 -- recommend claiming and optimizing)
- Industry-specific directory recommendations: load `references/local-schema-types.md` for per-vertical citation sources
- Data aggregator awareness, e.g. Data Axle, Foursquare (heuristic [H]; no reach figures claimed)

**Scoring guide:**
- Full: Consistent NAP across page/schema, Tier 1 citations detected, industry directories present
- Partial: NAP present but inconsistencies, some citations missing
- Low: NAP discrepancies, no detectable citations, no schema address

### 5. Local Schema Markup (10%)

Google: structured data "enables a feature to be present, it does not guarantee that it will be present" [V]. Google documents no ranking benefit, and its AI guide says no special schema is needed for AI features (see `geo-evidence.md`) [V]. Do not promise traffic or ranking gains.

**Check for:**
- LocalBusiness schema presence (extract JSON-LD blocks)
- Required properties: `name`, `address` with PostalAddress sub-properties
- Recommended properties (Google [V]): `geo` (latitude/longitude precision "at least 5 decimal places"), `openingHoursSpecification`, `telephone`, `url`, `priceRange` (shorter than 100 characters), `department`, `menu` and `servesCuisine` (food). `aggregateRating`/`review` only for sites reviewing other businesses
- **Correct subtype for industry** -- load `references/local-schema-types.md`:
  - Restaurant using `Restaurant` not generic `LocalBusiness`
  - Legal using `LegalService` not deprecated `Attorney`
  - Auto dealer using `AutoDealer` (Google's vehicle listing rich result was phased out in 2025 [V])
  - Healthcare using `MedicalClinic`/`Hospital`/`Dentist` not generic `MedicalBusiness`
- SAB-specific: `areaServed` with named cities (schema.org property, not in Google's list [H])
- Multi-location: each location page has own LocalBusiness with unique `@id`, linked via `parentOrganization` to the Organization on the homepage (`branchOf` is superseded in schema.org [V])
- Industry-specific schema patterns (per `references/local-schema-types.md`):
  - Restaurant: Menu + MenuSection + MenuItem + ReserveAction
  - Healthcare: Physician (Person) + MedicalSpecialty + sameAs to NPI
  - Legal: LegalService + Person + Service (practice areas)
  - Home Services: Subtype + areaServed + Service
  - Real Estate: RealEstateAgent + Person + RealEstateListing
  - Automotive: AutoDealer + Car + Offer (separate dept schemas)

**Scoring guide:**
- Full: Correct subtype, all recommended properties, industry-specific patterns, valid JSON-LD
- Partial: LocalBusiness present but generic type or missing recommended properties
- Low: No local schema, or schema with errors/placeholder content

### 6. Local Link & Authority Signals (10%)

Google: prominence is based partly on "how many websites link to your business" [V]. Practitioner survey: link signals 8% of local pack and 24% of local organic weight (Whitespark 2026) [H survey].

**Check for:**
- Local backlink indicators detectable from page:
  - Chamber of Commerce mentions or links
  - BBB accreditation/badge
  - Local news/press mentions
  - Community involvement signals (sponsorships, local events, partnerships)
- "Best of" list presence and local press coverage (earned, authentic mentions only; no AI-visibility weighting is claimed)
- Earned links only; no link velocity target is documented [H]

**Scoring guide:**
- Full: Local authority signals visible (chamber, BBB, press), community involvement evident
- Partial: Some authority signals but limited local link indicators
- Low: No detectable local authority signals

---

## AI Search Impact on Local

**Do not duplicate seo-geo analysis.** Provide local-specific AI context and recommend `/seo geo <url>` for full analysis.

Key local AI facts (vendor-documented; sources in `skills/seo-geo/references/geo-evidence.md`):
- Google: Google Business Profiles (and Merchant Center feeds) can help products and services be visible in AI responses and other Google Search results
- Bing: Bing Places for Business helps keep address, hours and contact details current and eligible for inclusion in AI-generated responses
- Measure with the Search Console Generative AI performance report and Bing Webmaster Tools AI Performance report
- Third-party local AI statistics (share of local searches with AI Overviews, conversion rates, AI local pack sizes) are not used unless a primary source is cited

**Recommendation**: Run `/seo geo <url>` for comprehensive AI search visibility analysis (AI crawler access, snippet eligibility, entity signals, and Search Console / Bing AI visibility reports).

---

## Reference Files

Load on-demand as needed:
- `references/local-seo-signals.md`: Google's local ranking statements, survey factors (labeled), review policy and law, citation tiers, GBP feature changes, update dates
- `references/local-eeat-evidence.md`: Evidence register for the local and E-E-A-T references, including the Removed claims list
- `references/local-schema-types.md`: LocalBusiness subtypes by industry, schema patterns, citation sources per vertical

---

## Output

Generate `LOCAL-SEO-ANALYSIS-{domain}.md` with:

1. **Local SEO Score: XX/100** with dimension breakdown table
2. **Business type**: Brick-and-mortar / SAB / Hybrid
3. **Industry vertical detected** + industry-specific findings
4. **GBP optimization checklist** (detected signals vs missing)
5. **Review health snapshot** (rating, count, velocity indicators, response patterns)
6. **NAP consistency audit** (page vs schema discrepancies, cross-source comparison)
7. **Citation presence check** (Tier 1 directory status)
8. **Local schema status** (present/missing/malformed + ready-to-use fix)
9. **Location page quality** (if multi-location: unique content %, doorway risk, store locator)
10. **Top 10 prioritized actions** (Critical > High > Medium > Low; Critical and High only for [V] findings, survey and heuristic items say so)
11. **Limitations disclaimer**: What this analysis could NOT assess (geo-grid ranking, Domain Authority, comprehensive backlinks, GBP Insights data, real-time local pack position) and which paid tools can fill those gaps

---

## Quick Wins

1. Claim and optimize Apple Business (formerly Apple Business Connect) for Apple Maps
2. Claim and optimize Bing Places (keeps details current and eligible for inclusion in Bing/Copilot AI-generated responses)
3. Fix any NAP discrepancies between page, schema, and GBP
4. Add LocalBusiness schema with correct industry subtype
5. Add `geo` coordinates with 5+ decimal precision
6. Ensure phone number uses `tel:` link for click-to-call
7. Add city + service keyword to title tag and H1

## Medium Effort

1. Create dedicated page for each core service (Whitespark 2026 survey: #1 local organic factor [H survey])
2. Ask every customer for a review on a steady schedule (no gating, no incentives [V])
3. Submit to data aggregators (e.g. Data Axle, Foursquare) for downstream distribution [H]
4. Claim industry-specific directory listings (per vertical recommendations)
5. Add industry-specific schema patterns (Menu for restaurants, Physician for healthcare, etc.)
6. Implement hub-and-spoke internal linking for service/location pages

## High Impact

1. Build local digital PR strategy targeting "best of" lists and local press (earned coverage, no paid or inauthentic mentions)
2. Develop unique, non-swappable content for each location page (>60% unique, heuristic)
3. Maintain accurate, active profiles on the review and directory platforms your customers use (e.g. Yelp, TripAdvisor, BBB, industry directories)
4. Pursue Chamber of Commerce and BBB membership (authority + verification signals)
5. Create community involvement content (sponsorships, local events, partnerships)

---

## DataForSEO Integration (Optional)

If DataForSEO MCP tools are available, use `local_business_data` for live GBP data extraction, `google_local_pack_serp` for real-time local pack positions, and `business_listings` for automated citation auditing across directories.

---

## Error Handling

| Scenario | Action |
|----------|--------|
| URL unreachable (DNS failure, connection refused) | Report the error clearly. Do not guess site content. Suggest the user verify the URL and try again. |
| No local signals detected on page | Report that no local business indicators were found. Suggest the user confirm this is a local business and provide the GBP listing URL if available. |
| NAP not found in page HTML | Check schema and meta tags. If still absent, flag as Medium (heuristic; the QRG asks raters to find contact information). Recommend adding visible NAP to footer and contact page. |
| Industry vertical unclear | Present the top two detected verticals with supporting signals. Ask the user to confirm before applying industry-specific recommendations. |
| Multi-location with 50+ location pages | Apply the quality gates from seo orchestrator (heuristic): WARNING at 30+ pages (enforce 60%+ unique), HARD STOP at 50+ pages (require user justification before continuing). |
