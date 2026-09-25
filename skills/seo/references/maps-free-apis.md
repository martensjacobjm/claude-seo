<!-- Updated: 2026-09-25 -->
# Free Maps APIs for claude-seo

Limits and policies below are [V] from each operator's own pages, fetched 2026-09-25.
Sources and removed claims: `local-eeat-evidence.md` (section "Maps APIs"). All three
services share donated or free capacity: identify the app, cache results, stay far below
the limits.

---

## Overpass API (Best Free Option for Competitor Discovery)

**Base URL:** `https://overpass-api.de/api/interpreter`
**Docs:** https://wiki.openstreetmap.org/wiki/Overpass_API and https://dev.overpass-api.de/overpass-doc/en/preface/commons.html
**License:** ODbL. Credit "OpenStreetMap and its contributors" and state that the data is
under the Open Database License (https://www.openstreetmap.org/copyright)

### Usage Limits

- Guideline for one-off use: under ~10,000 queries and ~1 GB download per day. For
  regular (scheduled) use, divide by 100: under 100 queries and 10 MB per day
- Slots per user (IP) vary with server load; `https://overpass-api.de/api/status` shows
  the current number (4 on 2026-09-25). Do not run scripts in parallel
- Send a `User-Agent` or `Referer` that identifies the app. A stock curl agent got
  HTTP 406 on 2026-09-25
- On HTTP 429 or 406, pause 30 seconds before the next request
- Defaults: 180 s run time, 512 MiB memory per query; `[timeout:25]` for light queries
- Commercial use should use a self-hosted or paid Overpass server

### Query Templates

```bash
UA="claude-seo/1.8.1 (+https://github.com/AgriciDaniel/claude-seo)"
```

**Restaurants within 5km radius:**
```bash
curl -s -A "$UA" "https://overpass-api.de/api/interpreter" \
  --data-urlencode 'data=[out:json][timeout:25];(node["amenity"="restaurant"](around:5000,LAT,LNG);way["amenity"="restaurant"](around:5000,LAT,LNG););out body;>;out skel qt;'
```

**All businesses on a street:**
```bash
curl -s -A "$UA" "https://overpass-api.de/api/interpreter" \
  --data-urlencode 'data=[out:json][timeout:25];way["name"="STREET_NAME"]["addr:city"="CITY"];(._;>;);out body;'
```

**Competitor POIs by category in bounding box:**
```bash
curl -s -A "$UA" "https://overpass-api.de/api/interpreter" \
  --data-urlencode 'data=[out:json][timeout:25];(node["amenity"="dentist"](SOUTH,WEST,NORTH,EAST);way["amenity"="dentist"](SOUTH,WEST,NORTH,EAST););out body;>;out skel qt;'
```

### Key OSM Tags for Local SEO

| Category | OSM Tag | Examples |
|----------|---------|---------|
| Food & Drink | `amenity=restaurant`, `amenity=cafe`, `amenity=fast_food` | Restaurants, cafes, takeaway |
| Healthcare | `amenity=dentist`, `amenity=doctors`, `amenity=pharmacy` | Dental, medical, pharmacy |
| Legal | `office=lawyer`, `office=notary` | Law firms, notaries |
| Home Services | `craft=plumber`, `craft=electrician`, `craft=hvac` | Trades, contractors |
| Retail | `shop=supermarket`, `shop=clothes`, `shop=car` | All retail types |
| Automotive | `shop=car`, `shop=car_repair`, `amenity=fuel` | Dealers, repair, gas |
| Hospitality | `tourism=hotel`, `tourism=motel`, `tourism=guest_house` | Accommodation |
| Financial | `amenity=bank`, `office=insurance`, `office=accountant` | Banks, insurance, accounting |

### Response Fields

Each element returns: `id`, `lat`, `lon`, `tags` object containing `name`, `phone`, `website`, `opening_hours`, `addr:street`, `addr:housenumber`, `addr:city`, `addr:postcode`, `cuisine`, `brand`, etc.

### Limitations

- No reviews, ratings, or popularity data
- No GBP-specific information
- Volunteer-contributed data: coverage and freshness vary by area; may be outdated
- The public server is often overloaded; do not expect high reliability
- Interactive tester: https://overpass-turbo.eu/

---

## Geoapify Places API (Structured POI Search)

**Base URL:** `https://api.geoapify.com/v2/places`
**Docs:** https://apidocs.geoapify.com/docs/places/
**Pricing:** https://www.geoapify.com/pricing and https://www.geoapify.com/pricing-details

### Free Plan

- **3,000 credits/day**, up to 5 requests/second, no credit card
- Places API: 1 credit per request returning up to 20 places, plus 1 credit per additional 20
- Commercial and production use allowed on the free plan, with attribution: "Powered by
  Geoapify" plus the data source (OpenStreetMap)
- Places API docs: "Cache/store results with no limits"
- Daily quota is "soft": sustained overuse gets an upgrade request, then possible blocking

### Query Template

```bash
curl -s "https://api.geoapify.com/v2/places?categories=catering.restaurant&filter=circle:LNG,LAT,5000&limit=20&apiKey=YOUR_KEY"
```

`filter=circle:lon,lat,radiusMeters` (longitude first).

### Category Hierarchy

Dot-separated categories, e.g. `catering.restaurant`, `commercial.supermarket`, `healthcare.dentist`, `service.financial.bank`, `commercial.vehicle`, `service.vehicle.repair.car`

### Response Format

GeoJSON FeatureCollection. Documented `properties`: `name`, `country`, `state`, `postcode`, `city`, `street`, `housenumber`, `lat`, `lon`, `formatted`, `address_line1`, `address_line2`, `categories`, `distance`, `place_id`. Contact details (phone, website) come from the Place Details API via `place_id`.

### Advantages Over Raw Overpass

- Cleaner, structured responses
- Hierarchical category taxonomy (400+ categories); OpenStreetMap is the Places data source
- API key with a credit quota and documented rate limit

---

## Nominatim (Geocoding Only)

**Base URL:** `https://nominatim.openstreetmap.org`
**Docs:** https://nominatim.org/release-docs/latest/api/Overview/
**Policy:** https://operations.osmfoundation.org/policies/nominatim/

The policy has a section for LLMs: an LLM may suggest this service only if it prominently
points to the usage policy and explains its restrictions. Always show the policy link and
the rules below to the user when using or suggesting Nominatim.

### Usage Policy (public server)

- **Absolute maximum 1 request/second**, summed over all users of the app
- Valid `User-Agent` or `Referer` identifying the app (stock library agents rejected)
- Display attribution; data is ODbL
- Forbidden: auto-complete, **systematic queries** (including "reverse queries in a grid"
  and "downloading all POIs in an area"), scraping of details pages
- Bulk geocoding is "not encouraged"; small one-time jobs only: single thread, one machine,
  results cached. Scripts running over a day or on a schedule: max 4 requests/minute
- Repeated identical queries may be classified as faulty and blocked: cache results

### Forward Geocoding

```bash
curl -s "https://nominatim.openstreetmap.org/search?q=123+Main+St+Austin+TX&format=json&addressdetails=1" \
  -H "User-Agent: claude-seo/1.8.1 (+https://github.com/AgriciDaniel/claude-seo)"
```

### Reverse Geocoding

```bash
curl -s "https://nominatim.openstreetmap.org/reverse?lat=40.7128&lon=-74.0060&format=json" \
  -H "User-Agent: claude-seo/1.8.1 (+https://github.com/AgriciDaniel/claude-seo)"
```

### Response Fields

`place_id`, `lat`, `lon`, `display_name`, `importance`, `class` (`category` in `format=jsonv2`), `type`, `address` object with `addressdetails=1` (house_number, road, city, state, postcode, country)

### Best Use

- Address-to-coordinates conversion for the geo-grid center point (one lookup)
- Reverse geocoding to validate one business address
- **NOT suitable** for business listing discovery or for grid points (policy forbids both)

---

## Rate Limit Enforcement Pattern

```bash
# Nominatim: a few one-off lookups only, 1 req/sec max, cache each result
UA="claude-seo/1.8.1 (+https://github.com/AgriciDaniel/claude-seo)"
for addr in "${addresses[@]}"; do
  curl -s -G "https://nominatim.openstreetmap.org/search" \
    --data-urlencode "q=${addr}" -d format=json -H "User-Agent: $UA"
  sleep 1.1
done

# Overpass: one query at a time; on HTTP 429 or 406 wait 30 s before retrying
# Geoapify: stay at or under 5 req/sec on the free plan
```

---

## Comparison Table

| Feature | Overpass | Geoapify | Nominatim |
|---------|---------|----------|-----------|
| Business discovery | Yes (tags) | Yes (categories) | No (policy forbids POI harvesting) |
| Reviews/ratings | No | No | No |
| Geocoding | No | Yes (Geocoding API) | Yes |
| Limit | ~10k queries/day one-off, ~100/day regular | 3k credits/day, 5 req/s | 1 req/s |
| Auth required | No (User-Agent) | API key | No (User-Agent) |
| Caching | Asked to cache | "Cache/store results with no limits" | Required for bulk |
| Data | OSM | OSM (Places) | OSM |
| Best for | Radius competitor search | Structured POI search | Single address resolution |
