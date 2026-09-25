<!-- Updated: 2026-09-25 -->
# DataForSEO Maps & Business Data API Endpoints

All endpoint, limit and price facts below are [V] from DataForSEO's own docs and pricing
pages, fetched 2026-09-25. Sources, dates and removed claims: `local-eeat-evidence.md`
(section "Maps APIs"). Prices change: re-check the pricing page before quoting a cost.

---

## MCP Server Versions (Tier 1 detection)

- `dataforseo-mcp-server` 3.x (npm `latest` is 3.1.1, 2026-08-25) exposes four generic tools:
  `api_request`, `docs_search`, `docs_index`, `docs_list_sections`. Call endpoints by path,
  e.g. `api_request` with path `/v3/serp/google/maps/live/advanced` and the task in `data`.
  It uses `.ai` paths by default (cropped response, no `cost`, `depth` defaults to 10); set
  `noAiMode: true` for the standard path, for `cost`, and for `task_post` calls (DataForSEO
  documents `.ai` for Live and Task GET endpoints only).
- The deprecated v2 server exposed one tool per endpoint, e.g.
  `business_data_business_listings_search`. Detect either.
- `extensions/dataforseo/install.sh` installs `dataforseo-mcp-server@3` (major pinned), so new
  installs get v3 and a future 4.x cannot replace it silently. v3.1.x needs Node.js 22+.

---

## Authentication & Limits

- HTTP Basic Auth (login:password)
- Up to **2,000 API calls/minute** on the Maps SERP, My Business Info, Reviews and
  Business Listings endpoints. Exceptions: Tripadvisor reviews **110**/min, Trustpilot
  reviews **30**/min
- **Live** calls carry **one task** each. **task_post** calls carry up to **100 tasks**
  (more returns error 40006)
- Business Data **live** endpoints: at most **30 simultaneous** calls
- $1 free trial credit, $50 minimum top-up, credits never expire

---

## Google Maps SERP API (Geo-Grid Backbone)

**Endpoints:** `POST https://api.dataforseo.com/v3/serp/google/maps/live/advanced` (live) or
`/v3/serp/google/maps/task_post` (standard queue, batchable)
**Pricing source:** https://dataforseo.com/pricing/serp/google-maps-serp-api

### Request Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `keyword` | Yes | Search query (e.g., "dentist") |
| `location_name` / `location_code` / `location_coordinate` | One of them | Location. Codes come from the locations endpoint |
| `location_coordinate` | - | `"latitude,longitude,zoom"`: max 7 decimals, zoom 3z-21z, default 17z |
| `language_code` | No | e.g. "en" |
| `device` | No | "desktop" (default) or "mobile" (mobile returns 20 results per SERP) |
| `depth` | No | Default 100, max 700. Billed per SERP of up to 100 results |

**Critical for geo-grid:** Use `location_coordinate` to simulate searches from specific GPS points. Format: `"40.7128,-74.0060,15z"`.

### Response Fields (`maps_search` items)

`rank_group`, `rank_absolute`, `title`, `domain`, `url`, `contact_url`, `book_online_url`, `rating` (`value`, `votes_count`), `rating_distribution`, `snippet`, `address`, `address_info`, `place_id`, `cid`, `feature_id`, `phone`, `main_image`, `total_photos`, `category`, `additional_categories`, `category_ids`, `work_hours` (`timetable`, `current_status`), `latitude`, `longitude`, `is_claimed`, `local_justifications`, `is_directory_item`, `price_level`

Ads come back as separate `maps_paid_item` items: rank the target among `maps_search` items only.

### Pricing (per SERP page of up to 100 results)

| Method | Cost per SERP | Turnaround |
|--------|--------------|------------|
| Standard | $0.0006 | 5 min (target 45 min; "Extended processing may occur") |
| Priority | $0.0012 | Up to 1 min on average |
| **Live** | **$0.002** | Up to 6 s on average |

Multipliers: x5 for each search operator (`site:`, `intitle:` etc.) in `keyword`; x2 for
`calculate_rectangles`; `depth` above 100 bills per extra 100 results.

---

## Google My Business Info API (Single Business Deep-Dive)

**Endpoint:** `POST https://api.dataforseo.com/v3/business_data/google/my_business_info/live`
**Pricing source:** https://dataforseo.com/pricing/business-data/business-data-api

### Input Options (`keyword` field)

- Business name (e.g., "Starbucks Austin TX") plus a location
- `"cid:194604053573767737"` or `"place_id:GhIJQWDl0CIeQUARxks3icF8U8A"` (doc examples)

### Response Fields

`title`, `description`, `category`, `category_ids`, `additional_categories`, `address_info`, `phone`, `url`, `contact_url`, `book_online_url`, `domain`, `logo`, `main_image`, `total_photos`, `is_claimed` ("shows whether the entity is verified by its owner on Google Maps"), `attributes` (`available_attributes`, `unavailable_attributes`), `place_topics`, `rating`, `rating_distribution`, `work_time.work_hours` (`timetable`, `current_status`), `popular_times`, `local_business_links` (reservation, order, menu), `cid`, `place_id`, `latitude`, `longitude`

**Cost per profile:** Standard $0.0015 (up to 45 min), Priority $0.003 (up to 1 min), **Live $0.0054** (up to 6 s)

**Use case:** Deep-dive on the TARGET business. Maps SERP for competitor discovery.

---

## Google Reviews API (Sentiment & Velocity)

**Endpoint:** `POST https://api.dataforseo.com/v3/business_data/google/reviews/task_post`
**Pricing source:** https://dataforseo.com/pricing/business-data/google-reviews-api

### Parameters

| Parameter | Description |
|-----------|-------------|
| `keyword` / `cid` / `place_id` | One of them identifies the business |
| `depth` | Default 10, max 4490; set in multiples of 10; billed per 10 reviews |
| `sort_by` | `newest`, `highest_rating`, `lowest_rating`, `relevant` (default) |

### Response Fields (per review)

`review_text`, `original_review_text`, `time_ago`, `timestamp`, `rating.value`, `review_id`, `review_url`, `profile_name`, `profile_url`, `reviews_count` (reviewer's total), `photos_count`, `local_guide`, `owner_answer`, `owner_timestamp`, `images`, `review_highlights`. No reviewer location.

### Pricing

| Endpoint | Unit | Standard | Priority |
|----------|------|----------|----------|
| Google Reviews | per 10 reviews | $0.00075 | $0.0015 |
| Extended Reviews, `cid`/`place_id` | per 20 reviews | $0.0015 | $0.003 |
| Extended Reviews, `keyword` | per 20 reviews | $0.00225 | $0.0045 |

Extended Reviews (`/v3/business_data/google/extended_reviews/task_post`) charges 2x the base
rate for `cid`/`place_id` and 3x for `keyword`. The plain Reviews endpoint lists no surcharge
by identifier. Prefer `cid`/`place_id` for Extended Reviews (a third cheaper than `keyword`).

---

## Google Q&A API

**Endpoint:** `POST https://api.dataforseo.com/v3/business_data/google/questions_and_answers/live`

Returns questions, answers and dates. Live: $0.0025 per 20 questions; standard and priority
queues also exist.

**Note:** Google discontinued its own My Business Q&A API on 2025-11-03 (GBP API sunset
page). The DataForSEO endpoint page does not mention a change, and the current public state
of Q&A on Maps was not verified. Treat an empty result as "no data", not as a profile gap.

---

## Business Listings Search (Pre-Indexed Database)

**Endpoint:** `POST https://api.dataforseo.com/v3/business_data/business_listings/search/live`

Queries DataForSEO's database of Google Maps listings (not a live Google search). `limit`
defaults to 100, max 1000 per request; page with `offset`.

**Categories Aggregation:** `/v3/business_data/business_listings/categories_aggregation/live` provides category taxonomy.

**v2 MCP tool name:** `business_data_business_listings_search` (v3: `api_request` with the path above)

---

## Cross-Platform Review APIs

### Tripadvisor

- Search: `/v3/business_data/tripadvisor/search/task_post`
- Reviews: `/v3/business_data/tripadvisor/reviews/task_post`
- $0.00075 per 10 reviews (standard), $0.0015 (high priority); `language_code`/`language_name` adds $0.00075 per task (standard). Queue only, no live. 110 calls/min.

### Trustpilot

- Search: `/v3/business_data/trustpilot/search/task_post`
- Reviews: `/v3/business_data/trustpilot/reviews/task_post`
- $0.00075 per 20 reviews (standard), $0.0015 (high priority). Queue only, no live. 30 calls/min.

---

## Cost Estimation Table

Arithmetic from the prices above (2026-09-25). Recalculate if the pricing pages change.

| Operation | Calls | Mode | Est. Cost |
|-----------|-------|------|-----------|
| 7x7 geo-grid, 1 keyword | 49 | Live | $0.098 |
| 7x7 geo-grid, 3 keywords | 147 | Live | $0.294 |
| 3x3 geo-grid, 1 keyword | 9 | Live | $0.018 |
| Target business profile | 1 | Live | $0.0054 |
| 100 reviews (Reviews, depth 100) | 1 | Standard | $0.0075 |
| 20 competitor profiles | 20 | Standard | $0.03 (Live: $0.108) |
| GBP posts audit (10 updates) | 1 | Standard | $0.00225 |
| Q&A retrieval (up to 20) | 1 | Live | $0.0025 |
| **Full audit (1-keyword grid)** | **~73** | Mixed | **~$0.15** |
| **Full audit (3-keyword grid)** | **~171** | Mixed | **~$0.34** |

**Grid formula:** `grid_size^2 x keywords x $0.002` (live) or `x $0.0006` (standard), for
`depth` <= 100 and no search operators.
