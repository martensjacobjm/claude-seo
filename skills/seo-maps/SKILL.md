---
name: seo-maps
description: >
  Maps intelligence for local SEO — geo-grid rank tracking, GBP profile
  auditing via API, review intelligence across Google/Tripadvisor/Trustpilot,
  cross-platform NAP verification (Google/Bing/Apple/OSM), competitor
  radius mapping, and LocalBusiness schema generation from API data.
  Three-tier capability: free (Overpass + Geoapify), DataForSEO (full
  intelligence), DataForSEO + Google (maximum coverage). Use when user
  says "maps", "geo-grid", "rank tracking", "GBP audit", "review
  velocity", "competitor radius", "maps analysis", "local rank
  tracking", "Share of Local Voice", or "SoLV".
user-invokable: true
argument-hint: "[command] [url|keyword|location]"
license: MIT
compatibility: "DataForSEO MCP for Tier 1+, Google Maps API for Tier 2"
metadata:
  author: AgriciDaniel
  version: "1.8.1"
  category: seo
---

# Maps Intelligence (March 2026)

Maps platform analysis for local businesses. Works with external APIs to assess
how a business appears on Google Maps, Bing Places, Apple Maps, and OpenStreetMap.

**Evidence rule:** every API, limit, price and Google claim here traces to a row in
`references/local-eeat-evidence.md` (section "Maps APIs" and the GBP sources). Add a row there
before adding a new fact. Only [V] (vendor-documented) findings may be Critical or High.
Scores, weights, SoLV bands, velocity and fake-review rules are heuristics [H]: label them
"heuristic" in output and cap them at Medium.

**Boundary with seo-local:** This skill analyzes the business on maps PLATFORMS
(via APIs). seo-local analyzes local SEO signals on the WEBSITE (via HTML fetch).
Do not duplicate seo-local on-page analysis. Recommend `/seo local <url>` for
website-level checks.

---

## Quick Reference

| Command | What it does | Tier |
|---------|-------------|------|
| `/seo maps <url>` | Full maps presence audit (auto-selects tier) | 0+ |
| `/seo maps grid <keyword> <location>` | Geo-grid rank scan (7x7, 1 keyword default) | 1+ |
| `/seo maps reviews <business> <location>` | Cross-platform review intelligence | 1+ |
| `/seo maps competitors <keyword> <location>` | Competitor radius mapping | 0+ |
| `/seo maps nap <business-name>` | Cross-platform NAP verification | 0+ |
| `/seo maps schema <business-name>` | Generate LocalBusiness JSON-LD from data | 0+ |
| `/seo maps gbp <business> <location>` | GBP completeness audit | 1+ |

---

## Three-Tier Capability Detection

Before any analysis, detect the available capability tier:

### Tier 0 (Free)
**Detection:** No DataForSEO MCP tools available.
**Capabilities:** Overpass API competitor discovery, Geoapify POI search, Nominatim geocoding (one-off lookups; show the user https://operations.osmfoundation.org/policies/nominatim/ as its policy requires), static GBP checklist, schema generation, cross-platform NAP guidance.
**Load:** `references/maps-free-apis.md`

### Tier 1 (DataForSEO)
**Detection:** a DataForSEO MCP tool is available: `api_request` (dataforseo-mcp-server 3.x; `extensions/dataforseo/install.sh` installs `dataforseo-mcp-server@3`) or `business_data_business_listings_search` (deprecated v2 server). With v3, call endpoints by path, e.g. `/v3/serp/google/maps/live/advanced`. The v2 server had no Maps SERP, My Business Info or Reviews tools: with v2 only, run listings search and handle grid, GBP and reviews as Tier 0 (tell the user v3 is needed).
**Capabilities:** Everything in Tier 0 PLUS geo-grid rank tracking, live GBP profile audit, review intelligence (velocity, sentiment, distribution), GBP post activity, Q&A data (Google's own Q&A API was discontinued 2025-11-03; treat empty results as no data), Tripadvisor/Trustpilot reviews.
**Load:** `references/maps-api-endpoints.md`

### Tier 2 (DataForSEO + Google Maps Platform)
**Detection:** Tier 1 available AND Google Maps API key in environment.
**Capabilities:** Everything in Tier 1 PLUS Places API (New) Place Details, `businessStatus` (OPERATIONAL, CLOSED_TEMPORARILY, CLOSED_PERMANENTLY), AI-powered place summaries (100-character overviews, only for some place types, languages and regions), photos.
**Note:** Google Maps Platform terms: `place_id` may be cached indefinitely; latitude/longitude from the Places API for up to 30 consecutive calendar days; other Places content may not be cached or stored except as the terms allow.

**Always communicate the detected tier to the user** at the start of analysis.

---

## Geo-Grid Rank Tracking (Tier 1+)

Simulates Google Maps searches from multiple GPS coordinates to show ranking
variation across a geographic area. Requires DataForSEO.

**Load:** `references/maps-geo-grid.md` for algorithm, SoLV formula, heatmap format.
**Load:** `references/maps-api-endpoints.md` for Maps SERP endpoint details.

### Workflow

1. Geocode business address to get center lat/lng
2. Generate grid points (default: 7x7, 5km radius, heuristic) with the offset formula in `maps-geo-grid.md`
3. **Display cost estimate and ask for confirmation before proceeding**
4. Send one Maps SERP task per grid point with `location_coordinate` (live: one task per call; standard `task_post`: up to 100 tasks per call)
5. Find target business rank (`rank_group` among `maps_search` items, matched on `cid`/`place_id`) at each point
6. Calculate SoLV (Local Falcon's definition: share of points in the top 3): `(top_3_count / total_points) * 100`
7. Render ASCII heatmap in output

### Cost Warning (REQUIRED)

Before every geo-grid scan, display:
```
Geo-Grid Scan: [keyword] at [location]
Grid: 7x7 (49 points) | Keywords: [N] | Est. cost: $[amount]
DataForSEO credits will be consumed. Proceed?
```

---

## GBP Profile Audit (Tier 1 preferred, Tier 0 manual)

Audits 24 profile fields. Google says complete, accurate info makes a business "more likely to show up"; it publishes no per-field weights, so the score is a heuristic [H].

**Load:** `references/maps-gbp-checklist.md` for full checklist and scoring.

### Tier 1 Workflow

1. Fetch business profile via DataForSEO My Business Info API (keyword or CID)
2. Map API response fields to the 24-field checklist (`is_claimed` gives verification status)
3. Score each field: Present + Optimized = 2pts, Present = 1pt, Missing = 0pts (max 48)
4. Apply industry-specific weight multipliers
5. Normalize to 0-100 scale

### Tier 0 Workflow

1. Fetch the business website via WebFetch
2. Extract any visible GBP signals (Maps embed, place references, review widgets)
3. Apply static checklist based on detectable signals
4. Mark undetectable fields as "Unknown (requires DataForSEO for live data)"

---

## Review Intelligence (Tier 1+)

Cross-platform review analysis: velocity, sentiment, rating distribution, fake detection.

**Reference:** `references/local-seo-signals.md` for benchmarks (shared with seo-local).

### Workflow

1. Fetch Google reviews via DataForSEO Reviews API (sort by newest)
2. Calculate review velocity: reviews per month over last 6 months [H]
3. Note gaps in review recency (heuristic; Google documents no review cadence, see `references/local-eeat-evidence.md`)
4. Report the rating distribution (`rating_distribution`); no "healthy" shape is documented, so describe it rather than grade it
5. Calculate owner response rate: reviews with `owner_answer` / reviews fetched. Google recommends replying to reviews [V]; no target rate is documented
6. Fetch Tripadvisor and Trustpilot reviews (if available)
7. Cross-platform comparison table

### Possible Review Manipulation Signals [H]

Google's policy removes "Content exhibiting unusual volumes or patterns of review
contributions that are indicative of efforts to manipulate a place's rating" and content
posted "from multiple accounts by or at the request of one person" [V, fake engagement
policy 7400114]. It publishes no detection thresholds. The patterns below are heuristics:
report "possible pattern, not proof", cap at Medium, never accuse, and point to Google's
review reporting flow.

Flag reviews matching 2+ of these patterns:
- Uniform timing (multiple reviews same day/hour)
- Reviewer accounts with a single review (`reviews_count` = 1) or no profile history
- Exclusively 5-star volume spike vs the business's own 6-month baseline
- Identical or near-identical text across reviews
- Sudden volume spike without corresponding marketing activity (ask the user)
- Reviewer location vs business location: manual check only (the Reviews API returns no reviewer location)

---

## Competitor Radius Mapping (Tier 0+)

Identify and analyze competitors within a defined radius.

### Tier 0 (Overpass API)

**Load:** `references/maps-free-apis.md` for query templates.

1. Geocode business address
2. Query Overpass API for businesses with same OSM tag within radius
3. Parse results: name, address, phone, website, distance from center
4. Sort by distance, present as competitor landscape table

### Tier 1 (DataForSEO)

1. Use Maps SERP API with business keyword + location
2. Extract top 20 competitors with full profile data
3. Compare: rating, review count, categories, photos, attributes
4. Calculate competitive density: competitors per km^2 (descriptive, heuristic)

---

## Cross-Platform NAP Verification (Tier 0+)

Check business listing consistency across Google, Bing Places, Apple, and OSM.

### Workflow

1. Search for business name on each platform:
   - Google: infer from GBP data or Maps SERP result
   - Bing: `WebFetch https://www.bing.com/maps?q=BUSINESS+NAME+LOCATION`
   - Apple: manual check (the Apple Maps Server API needs an Apple Developer Maps key and is not integrated here; businesses manage listings in Apple Business at business.apple.com, where businessconnect.apple.com now redirects)
   - OSM: Overpass search (Nominatim only for a single address lookup)
2. Extract NAP (Name, Address, Phone) from each source
3. Compare for consistency: exact match, partial match, missing, or conflicting
4. Flag discrepancies as Medium (name or address mismatch) or Low (phone mismatch), labeled heuristic: Google documents no cross-platform consistency rule. A GBP name that breaks Google's name guideline (3038177) is a separate [V] finding
5. Recommend claiming unclaimed profiles

---

## Schema Generation (Tier 0+)

Generate LocalBusiness JSON-LD markup from collected data.

**Reference:** `references/local-schema-types.md` for industry subtypes (shared with seo-local).

### Workflow

1. Determine most specific schema subtype for the industry
2. Populate Google-required properties: `name`, `address` (plus `@type`; `image` is valid schema.org but not in Google's LocalBusiness list)
3. Add recommended properties: `telephone`, `url`, `geo`, `openingHoursSpecification`, `priceRange`
4. Add strategic properties for multi-location: `parentOrganization` (supersedes `branchOf`), `areaServed`, `sameAs`
5. Add `aggregateRating` only when the site reviews other businesses: self-serving review markup is not eligible for star snippets
6. Output valid JSON-LD block ready for implementation

**Do NOT generate self-serving review markup** -- Google ignores LocalBusiness review markup from the business itself. Only mark up third-party reviews visible on the page.

---

## Reference Files

Load on-demand as needed (do NOT load all at startup):
- `references/maps-api-endpoints.md`: DataForSEO endpoint details, params, costs
- `references/maps-free-apis.md`: Overpass, Geoapify, Nominatim query templates
- `references/maps-geo-grid.md`: Grid algorithm, SoLV formula, heatmap rendering
- `references/maps-gbp-checklist.md`: 24-field GBP audit with industry weights
- `references/local-eeat-evidence.md`: Evidence register (sources, removed claims)
- `references/local-seo-signals.md`: Ranking factors, review benchmarks (shared)
- `references/local-schema-types.md`: LocalBusiness subtypes by industry (shared)

---

## Output

Generate `MAPS-ANALYSIS-{domain}.md` with:

1. **Maps Health Score: XX/100** with dimension breakdown table
2. **Capability tier detected** (Tier 0 or Tier 1) with explanation of what's available
3. **Geo-grid heatmap** (Tier 1): ASCII grid with SoLV percentage and average rank
4. **GBP profile audit**: field-by-field scoring with industry-specific weights
5. **Review intelligence**: velocity chart, rating distribution, response rate, cross-platform comparison
6. **Competitor landscape**: count in radius, top 5 by rating/reviews, competitive density
7. **Cross-platform presence**: Google/Bing/Apple/OSM listing status
8. **Schema recommendation**: generated LocalBusiness JSON-LD (if missing or incomplete)
9. **Top 10 prioritized actions** (Critical > High > Medium > Low)
10. **Cost report**: DataForSEO credits consumed during analysis (Tier 1 only)
11. **Limitations disclaimer**: what could not be assessed at current tier

### Finding Phrasing (invented example data)

| Situation | Wrong | Right |
|-----------|-------|-------|
| SoLV 18% | "Critical: nearly invisible" | "Medium (heuristic): in the top 3 at 9 of 49 points (18%); competitor X leads at 31 points" |
| 55% owner replies | "High: below 80% target" | "Medium (heuristic): 55% of the last 100 reviews have a reply. Google recommends replying to reviews [V]; no target rate is documented" |
| 6 five-star reviews on one day | "Critical: fake reviews detected" | "Medium (heuristic): possible review pattern, not proof: 6 five-star reviews on 2026-05-02 from single-review accounts. Report via Google if you suspect abuse" |
| `is_claimed: false` | "Low: claim profile" | "High [V]: profile not verified; Google says verified businesses are more likely to show up" |

---

## Cross-Skill Delegation

- Website on-page local signals: recommend `/seo local <url>`
- Full AI search visibility: recommend `/seo geo <url>`
- Schema validation and fixes: recommend `/seo schema <url>`
- Live SERP and keyword data: recommend `/seo dataforseo [command]`

---

## Error Handling

| Scenario | Action |
|----------|--------|
| DataForSEO MCP not available | Drop to Tier 0. Inform user: "DataForSEO not detected. Running free-tier analysis. For geo-grid tracking and review intelligence, install the DataForSEO extension." |
| Business not found in Maps SERP | Try My Business Info with keyword. If still not found, report "Business not found in Google Maps for this location." |
| Geocoding fails (Nominatim) | Ask user to provide coordinates or a more specific address. |
| API rate limit hit | Report the limit. Suggest waiting or using standard (queued) method instead of live. |
| No reviews found | Report zero review state. Recommend asking every customer for a review on a steady schedule (no gating, no incentives). |
| Multi-location detected | Ask user which location to analyze, or offer batch mode with per-location cost estimate. |
