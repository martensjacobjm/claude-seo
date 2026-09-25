<!-- Updated: 2026-09-25 -->
# Local SEO and E-E-A-T Evidence Register

Every factual claim in `eeat-framework.md`, `local-schema-types.md`, `local-seo-signals.md`,
the four `maps-*.md` references, `skills/seo-local/SKILL.md`, `skills/seo-maps/SKILL.md` and
their agents must trace to a row here. Add a source
only after fetching the primary document. AI search claims live in
`skills/seo-geo/references/geo-evidence.md`. All sources fetched 2026-09-25 unless noted.

## 1. Evidence Levels

| Tag | Level | Severity cap |
|-----|-------|--------------|
| [V] | Vendor documentation (Google, Bing, Apple, schema.org) or law and regulators (eCFR, FTC, HHS) | Any |
| [H survey] | Practitioner survey with published method (Whitespark, BrightLocal) | Medium, labeled "practitioner survey" |
| [H] | Practitioner heuristic, including all scoring weights | Medium, labeled "heuristic" |

A vendor's statement about another company's system is not [V]. Blog posts and news
articles are used only to locate primary sources.

## 2. Vendor and Official Sources [V]

### Google Search Central and Quality Rater Guidelines

| Source | Date | Claim used |
|--------|------|------------|
| [Search Quality Rater Guidelines](https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf) | Edition 2025-09-11 | "Trust is the most important member of the E-E-A-T family"; four YMYL types incl. "YMYL Government, Civics & Society" (election and voting information); "Many or most topics are not YMYL"; "No single rating can directly impact" a page; Experience = "first-hand or life experience"; 4.6.3 to 4.6.5 spam types; 4.6.6 Lowest for content "auto or AI generated ... with little to no effort"; "the use of Generative AI tools alone does not determine the level of effort"; "As an AI language model" example |
| [Creating helpful content](https://developers.google.com/search/docs/fundamentals/creating-helpful-content) | Last updated 2025-12-10 | "trust is most important"; "E-E-A-T itself isn't a specific ranking factor"; more weight for strong E-E-A-T on YMYL; do not change dates to seem fresh |
| [Guidance on generative AI content](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content) | Last updated 2025-12-10 | Many AI pages without added value may violate the scaled content abuse policy |
| [Spam policies](https://developers.google.com/search/docs/essentials/spam-policies) | Last updated 2026-08-28 | Doorway abuse (city pages funnelling to one page, substantially similar pages); expired domain abuse; scaled content abuse; "Site reputation policy" (EEA enforcement change) |
| [Search Central changelog](https://developers.google.com/search/updates) | 2026 | 2024-03-05 three new spam policies; 2023-09-14 HowTo docs removed; SpecialAnnouncement deprecated from 2025-07-31; 2025-06-12 retirement banners; 2025-09-09 vehicle listing and special announcement docs removed |
| [Simplifying the search results page](https://developers.google.com/search/blog/2025/06/simplifying-search-results) | 2025-06-12, update 2025-09-08 | Vehicle Listing, Special Announcement and others phased out; "won't affect how pages are ranked" |
| [LocalBusiness structured data](https://developers.google.com/search/docs/appearance/structured-data/local-business) | Last updated 2026-09-08 | Required `address`, `name`; recommended list; geo "at least 5 decimal places"; priceRange "shorter than 100 characters"; "most specific LocalBusiness sub-type possible"; arrays, not `additionalType`; `image` only in the restaurant carousel |
| [Review snippet](https://developers.google.com/search/docs/appearance/structured-data/review-snippet) | Last updated 2026-09-08 | Self-serving LocalBusiness/Organization reviews ineligible for stars (incl. embedded widgets); "Don't aggregate reviews or ratings from other websites"; no fake or undisclosed incentivized reviews |
| [Structured data policies](https://developers.google.com/search/docs/appearance/structured-data/sd-policies) | Last updated 2026-07-10 | "enables a feature to be present, it does not guarantee"; manual action "doesn't affect how the page ranks" |
| [Link best practices](https://developers.google.com/search/docs/crawling-indexing/links-crawlable) | Last updated 2025-12-10 | Descriptive anchor text |
| [Search Status Dashboard, Ranking](https://status.search.google.com/products/rGHU1u87FJnkP6W2GwMi/history) | Fetched 2026-09-25 | Update start dates and durations 2025 to 2026 |

### Google Business Profile, Maps and Local Services

| Source | Date | Claim used |
|--------|------|------------|
| [Tips to improve your local ranking (7091)](https://support.google.com/business/answer/7091) | Fetched 2026-09-25 | "mainly based on relevance, distance, and popularity"; prominence from links and reviews; "no way to request or pay"; recommended actions: verify ("more likely to show up in search results"), complete info incl. special hours and attributes ("parking or Wi-Fi"), respond to reviews ("shows that you value their feedback"), add photos and videos. No mention of directories (inference from absence) |
| [Guidelines for representing your business (3038177)](https://support.google.com/business/answer/3038177) | Fetched 2026-09-25 | Real-world name; unnecessary info in name "isn't permitted"; SAB hides address; "about 2 hours of driving time"; departments; individual practitioners; "[brand/company]: [practitioner name]"; "Use a local phone number instead of a central call center helpline number whenever possible" |
| [Edit profile (3039617)](https://support.google.com/business/answer/3039617), [Service areas (9157481)](https://support.google.com/business/answer/9157481), [Posts (7342169)](https://support.google.com/business/answer/7342169), [Social links (13580646)](https://support.google.com/business/answer/13580646) | Fetched 2026-09-25 | Description "Do not exceed 750 characters"; "up to 20 service areas"; post types updates, offers, events; social links "available in select regions" |
| [Fake engagement policy (7400114)](https://support.google.com/contributionpolicy/answer/7400114) | Fetched 2026-09-25 | No incentives; do not "Discourage or prohibit negative reviews, or selectively solicit positive reviews from customers"; removes "Content exhibiting unusual volumes or patterns of review contributions" and content "posted from multiple accounts by or at the request of one person" (no thresholds published) |
| [Chat and call history (14919056)](https://support.google.com/business/answer/14919056) | Fetched 2026-09-25 | Both removed as of 2024-07-31 |
| [GBP API sunset dates](https://developers.google.com/my-business/content/sunset-dates) | Last updated 2026-08-28 | Q&A API support ended 2025-09-15, discontinued 2025-11-03; Business Calls API deprecated 2023-05-30 |
| [About Google Verified badge (16498018)](https://support.google.com/localservices/answer/16498018) | Fetched 2026-09-25 | Single LSA badge for all advertisers; Money Back Guarantee discontinued (claims before 2025-12-07) |
| [Tips for business-specific photos (6123536)](https://support.google.com/business/answer/6123536) | Fetched 2026-09-25 | Photo advice; contains no performance statistics |
| [Google Maps fake reviews, 2024](https://blog.google/products-and-platforms/products/maps/google-business-profiles-ai-fake-reviews/) | 2025-04-07 | "more than 240 million policy-violating reviews from 2024" |
| [New ways we're protecting businesses on Maps](https://blog.google/products-and-platforms/products/maps/new-ways-were-protecting-businesses-on-maps/) | 2026-04-16 | "over 292 million policy-violating reviews" in 2025 |

### schema.org, Apple, Bing, US law

| Source | Date | Claim used |
|--------|------|------------|
| [schema.org vocabulary](https://schema.org/version/latest/schemaorg-all-https.jsonld) | Fetched 2026-09-25 | Types and parents in `local-schema-types.md`; `Attorney` deprecated; `branchOf` to `parentOrganization`, `menu` to `hasMenu`, `serviceArea` to `areaServed` superseded; `RealEstateListing` pending; no `RealEstateBrokerage` or `VehicleListing` type (absence); `VeterinaryCare` is a MedicalOrganization |
| [Apple Business](https://business.apple.com/) | Fetched 2026-09-25 | businessconnect.apple.com redirects here; "Put your business on the map"; Custom Actions; Insights |
| Bing Places | 2026-02-10 | Entry in `geo-evidence.md` (AI Performance blog post) |
| [16 CFR Part 465](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-D/part-465) and [Federal Register 2024-18519](https://www.federalregister.gov/documents/2024/08/22/2024-18519/trade-regulation-rule-on-the-use-of-consumer-reviews-and-testimonials) | Published 2024-08-22, effective 2024-10-21 | Fake reviews, sentiment-conditioned incentives (465.4), review suppression (465.7) |
| [16 CFR 1.98](https://www.ecfr.gov/current/title-16/chapter-I/subchapter-A/part-1/subpart-L/section-1.98) | Current eCFR | 45(m)(1)(A) penalty $53,088 |
| [OMB M-26-11](https://www.whitehouse.gov/wp-content/uploads/2026/04/M-26-11-Cancellation-of-Penalty-Inflation-Adjustments-for-2026-Regarding-the-Federal-Civil-Penalties-Inflation-Adjustment-Act-Improvements-Act-of-2015.pdf) | 2026-04-17 | No 2026 cost-of-living multiplier ("there will be no updated cost-of-living adjustment multiplier for 2026"), so $53,088 stands |
| [FTC: Soliciting and paying for online reviews](https://www.ftc.gov/business-guidance/resources/soliciting-paying-online-reviews-guide-marketers) | 2022 | "Don't ask for reviews only from customers you think will leave positive ones" (read via WebFetch; direct fetch returned 403) |
| [HHS OCR: Manasa Health Center](https://www.hhs.gov/hipaa/for-professionals/compliance-enforcement/agreements/manasa/index.html) | 2023-06-05 | $30,000; PHI disclosed in responses to negative online reviews |

### Maps APIs (seo-maps; prices change, re-check before quoting)

| Source | Date | Claim used |
|--------|------|------------|
| [DataForSEO docs: Maps SERP live](https://docs.dataforseo.com/v3/serp/google/maps/live/advanced/), [task_post](https://docs.dataforseo.com/v3/serp/google/maps/task_post/) | Fetched 2026-09-25 | 2,000 calls/min; live = one task per call; task_post max 100 tasks (error 40006); `location_coordinate` "latitude,longitude,zoom", 7 decimals, 3z-21z, default 17z; depth default 100, max 700; mobile 20 results; `maps_search` item fields; `maps_paid_item` |
| DataForSEO docs: [My Business Info live](https://docs.dataforseo.com/v3/business_data/google/my_business_info/live/), [Reviews](https://docs.dataforseo.com/v3/business_data/google/reviews/task_post/), [Extended Reviews](https://docs.dataforseo.com/v3/business_data/google/extended_reviews/task_post/), [Q&A live](https://docs.dataforseo.com/v3/business_data/google/questions_and_answers/live/), [Listings search](https://docs.dataforseo.com/v3/business_data/business_listings/search/live/), [Tripadvisor](https://docs.dataforseo.com/v3/business_data/tripadvisor/reviews/task_post/), [Trustpilot](https://docs.dataforseo.com/v3/business_data/trustpilot/reviews/task_post/) | Fetched 2026-09-25 | `cid:`/`place_id:` in `keyword`; `is_claimed` "verified by its owner"; `total_photos`, `logo`, `work_time.work_hours`; reviews `sort_by` newest/highest_rating/lowest_rating/relevant, depth max 4490; Extended Reviews 3x (keyword), 2x (cid/place_id); live max 30 simultaneous; listings limit max 1000; Tripadvisor 110/min, Trustpilot 30/min |
| DataForSEO pricing: [Maps SERP](https://dataforseo.com/pricing/serp/google-maps-serp-api) (updated 2026-07-03), [Business Info/Updates](https://dataforseo.com/pricing/business-data/business-data-api), [Reviews](https://dataforseo.com/pricing/business-data/google-reviews-api) (2026-06-22), [Q&A](https://dataforseo.com/pricing/business-data/google-questions-and-answers-api-pricing), [Tripadvisor](https://dataforseo.com/pricing/business-data/business-data-api-tripadvisor-pricing), [Trustpilot](https://dataforseo.com/pricing/business-data/business-data-api-trustpilot-reviews-pricing) | Fetched 2026-09-25 | Maps SERP $0.0006/$0.0012/$0.002; operators x5, depth per 100; Info $0.0015/$0.003/$0.0054; Updates $0.0015 + $0.00075 per 10; Reviews $0.00075 per 10; Extended $0.00075 + keyword $0.0015 or cid/place_id $0.00075 per 20; Q&A live $0.0025 per 20; Tripadvisor $0.00075 per 10; Trustpilot $0.00075 per 20 |
| [DataForSEO MCP server page](https://dataforseo.com/seo-mcp-server) and [npm dataforseo-mcp-server](https://www.npmjs.com/package/dataforseo-mcp-server) | Fetched 2026-09-25 | $1 free credit, $50 minimum top-up, credits never expire; v3 (latest 3.1.1, 2026-08-25) tools `api_request`, `docs_search`, `docs_index`, `docs_list_sections`; v2 deprecated |
| [Places API policies](https://developers.google.com/maps/documentation/places/web-service/policies) (updated 2026-09-24), [Service Specific Terms](https://cloud.google.com/maps-platform/terms/maps-service-terms) (modified 2026-06-10) | Fetched 2026-09-25 | place_id "exempt from caching restrictions"; Places API lat/lng cache "up to 30 consecutive calendar days" (14.3) |
| [Place summaries](https://developers.google.com/maps/documentation/places/web-service/place-summaries) (updated 2026-09-17), [Place reference](https://developers.google.com/maps/documentation/places/web-service/reference/rest/v1/places) | Fetched 2026-09-25 | "100-character overviews", limited place types, languages and regions; `businessStatus` values |
| [Apple Maps Server API](https://developer.apple.com/documentation/applemapsserverapi) | Fetched 2026-09-25 | Exists (search, places); needs a Maps identifier and private key |
| [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/) | Fetched 2026-09-25 | "absolute maximum of 1 request per second"; identifying User-Agent; no auto-complete, no "reverse queries in a grid"; bulk "not encouraged", 4 req/min for long or scheduled scripts; LLM clause; cache results |
| [Overpass API wiki](https://wiki.openstreetmap.org/wiki/Overpass_API), [Overpass manual: Commons](https://dev.overpass-api.de/overpass-doc/en/preface/commons.html), [/api/status](https://overpass-api.de/api/status) | Fetched 2026-09-25 | ~10,000 queries and ~1 GB/day (one-off), divide by 100 for regular use; User-Agent; no parallel scripts; 30 s pause on 429/406; defaults 180 s and 512 MiB; slots vary (4 on 2026-09-25) |
| [OSM copyright](https://www.openstreetmap.org/copyright) | Fetched 2026-09-25 | Credit "OpenStreetMap and its contributors"; ODbL |
| [Geoapify pricing](https://www.geoapify.com/pricing), [pricing details](https://www.geoapify.com/pricing-details), [Places docs](https://apidocs.geoapify.com/docs/places/) | Fetched 2026-09-25 | Free 3,000 credits/day, 5 req/s, no card, attribution; 1 credit per 20 places; OSM source; "Cache/store results with no limits"; categories and response properties |
| [Local Falcon KB32: What is SoLV](https://www.localfalcon.com/knowledge-base/kb32-what-is-solv-how-to-interpret-and-use-the-metric) | Updated 2025-11-20 | SoLV® is Local Falcon's trademark: how often a business ranks in the top three positions; no bands published |

## 3. Practitioner Surveys [H survey]

- **Whitespark, Local Search Ranking Factors 2026**
  ([link](https://whitespark.ca/local-search-ranking-factors/)), published 2025-11-06. 47
  invited experts scored 187 factors 0 to 5; "None of the experts have special access to the
  internal workings of Google's local search algorithm." Group weights read from the chart
  image `ranking-factor-groups.png`. Scores used: Primary GBP Category 227, proximity 225,
  keywords in GBP title 223, open at search 189, Dedicated Page for Each Service 210 (organic),
  Incorrect Primary Category 214 (negative #2). Local pack ranks: Primary GBP Category #1,
  Business is Open at Time of Search #5. AI-visibility scores not used.
- **BrightLocal, Local Consumer Review Survey 2026**
  ([link](https://www.brightlocal.com/research/local-consumer-review-survey/)), published
  2026-02-11, 1,002 US adults (SurveyMonkey panel). Figures used: 41% "always" read (29% in
  2025), 31% 4.5+ stars (17%), 68% 4+ stars (55%), 74% last three months, 6 review sites, 42%
  unlikely to use a business that never replies, 80% likely to use a business that responds
  to all reviews, 89% expect a response, 81% within a week, Apple Maps 27% (14%).

## 4. Removed Claims (2026-09-25)

Do not re-introduce these without a fetched primary source:

- E-E-A-T: "December 2025 core update ... watershed moment"; "E-E-A-T now applies to ALL competitive queries"; traffic drops "Affiliate 71%", "Health/YMYL 67%", "E-commerce 52%"; December 2025 "elevated the Experience dimension" (Google published no such description)
- E-E-A-T: "Elections and civic trust" / "Democratic processes" "added Sept 2025" (current QRG has one "Government, Civics & Society" type; the addition date was not verified)
- E-E-A-T: "Raters now formally evaluate whether content appears AI-generated"; "AI Overview Evaluation" section (not found in the QRG text); spam types called "New" in the Sept 2025 QRG (they date from 2024-03-05)
- RSL "Backed by Reddit, Yahoo, Medium, Quora, Cloudflare, Akamai, Creative Commons" (already in geo-evidence.md)
- Schema: "43% CTR increase, Webstix case study"; "Confirmed: John Mueller, Gary Illyes" (replaced by Google docs); `MedicalClinic`/`Hospital`/`Dentist` "eligible for rich results"; `image` as a Google-recommended LocalBusiness property; `aggregateRating` as a recommendation for a business's own site
- Schema: "VehicleListing deprecated June 12, 2025 ... Use Car + Offer instead" (no such schema.org type; the Google feature was phased out); "Feed-based Vehicle Listings via Merchant Center still functional"; "Google Food Ordering discontinued June 2024" (no primary source found); `branchOf` as the location link (superseded)
- Schema: "Bruce Clay study: 50%+ traffic lift" for subdirectories; "HIPAA ... Cannot confirm/deny reviewer is a patient" (replaced by the HHS wording); "Reviews follow practitioner listing"; "Service area in GBP does NOT currently impact rankings (Sterling Sky)"
- Citations: TripAdvisor "1B+ reviews"; Healthgrades "50% of Americans"; Doximity "80% of US physicians"; FindLaw "DA~91", Martindale "DA~84", Justia "DA~70", Super Lawyers "top 5%"; Internet Brands/Thomson Reuters ownership; Thumbtack "$400M revenue", "ChatGPT/Alexa/Zillow"; Angi "-30%"; Porch/Houzz pivots; Zillow "44% of RE search traffic", "integrated into ChatGPT Oct 2025"; Homes.com "100M monthly visitors"; Redfin acquisition; DealerRater syndication
- Ranking factors: Whitespark scores "193", "181", "176" (actual 227/223/214); "Incorrect primary category ... #1 negative factor" (it is #2); links "~26% of local organic" (survey: 24%); "Review Signals up from ~16% in 2023"; "3 of top 5 AI visibility factors are citation-related"
- Search Atlas ML study (proximity "55.2%", reviews "19.2%", "92-93% of variance")
- Sterling Sky: "Magic 10" reviews; "18-Day Rule"; "Diversity Update"; do not link GBP to strongest page; AI local packs "32% fewer businesses"; local pack ads "1% to 22%"; "ChatGPT traffic ~2%"
- BrightLocal: Google "71%" (from 83%), Instagram "37%", TikTok "29%" (not found in the survey text); "88% would use business that responds"; "optimal: 4 additional categories"
- Enforcement: "40% increase over 2023"; "Review deletion rates up 600%+ ... 38% were 5-star (GMBapi.com)"
- GBP: Q&A removed "Dec 3, 2025", "replaced by Ask Maps (Gemini AI)", "no export"; "GBP-hosted websites discontinued" (help page no longer available); "School reviews Apr 30, 2025"; Local Lists "Local Gems, Trending, Top List" (SOCi); "Google Verified badge (replaced Guaranteed/Screened Oct 2025)" as a GBP feature
- GBP insights: posts "No direct ranking impact (WebFX)"; photos "45% more direction requests" (Agency Jet); geotagging "NO impact"; attribute impact claims (WebFX/Sterling Sky)
- Updates: impact descriptions ("Emphasized E-E-A-T, penalized thin/AI content", "behavioral signal weighting", "favored local expertise", "Local Pack often stable"); "June 2025 Core Jun-Jul 17"
- Voice: "58% of voice searches are for local" (BusinessDasher); "4-7 words"; "80%+ of Google Assistant answers from top 3"; assistant data-source table (Siri "+ Yelp", Alexa "Bing Places + Yelp")
- AI local (also in geo-evidence.md): BrightLocal "45%"; Seer "15.9%", "1.76%", "+35%"; Whitespark "Up to 68%" AIO; Ahrefs "-58%" CTR; ChatGPT source list; Perplexity "21.87 citations", "40% more" (Qwairy)
- Local pack: "Standard 3 results"; zero-click "up to 78%" (Similarweb)
- Behavior: "46% of all Google searches seek local information"; "76% of mobile near-me searches lead to visit within 24 hours" (Google's live page no longer carries it); "900% increase in near me searches"; proximity "urban 1-2 miles, rural 5-10+ miles"
- Aggregators and platforms: Foursquare "Powers Uber, Nextdoor, Yahoo, ChatGPT. 500M+ devices"; Neustar "80+ platform partnerships"; Data Axle "Google, Bing, Apple"; Apple "1B+ iPhone users"; Apple Business Connect "usage nearly doubled" (the survey measures Apple Maps use, not Business Connect)
- seo-local: Chamber of Commerce "high Trust Flow, ~80% more consumer visits" (GlueUp); "Google uses BBB for business verification"; "5-10 quality local links/month"; "2-5 contextual internal links per 1,000 words"; HVAC "lost 80% rankings + 63% traffic"; "July 2025 documentation update removed directories" (date not verifiable)

- seo-maps (2026-09-25): "Owner responses (target: 80%+ response rate)" (the survey's 80% is
  consumers likely to use a business that answers all reviews, not a response rate);
  "Whitespark/BrightLocal (Study)" as unlabeled sources; "Critical Fields (Direct Ranking
  Impact)"; GBP post type "product"; "GBP Q&A deprecated Dec 2025 (replaced by Ask Maps
  Gemini AI)"; Verified status "Not directly exposed" (`is_claimed` exposes it); SoLV "Metric
  pioneered by Local Falcon"; SoLV band "Critical"; "healthy = bell curve skewed to 5-star";
  NAP mismatch as Critical/High; Apple "no public API"; Places "storage to place_id only"
- DataForSEO (2026-09-25): "2,000 API calls/minute across all endpoints"; batching 49 live
  tasks in one request; reviews $0.003 per 10 (keyword), "place_id 4x cheaper"; Tripadvisor
  "Billed per 30 reviews", "Standard method only"; My Business Info "$0.0015" as a live price;
  "Up to 700+ results" (listings max 1000); `sort_by` "most_relevant"; response fields
  `contact_info`, `photos_count`, `work_time` in Maps SERP; full audit "~$0.13"/"~$0.33";
  location code "1026339 for Austin" (not checked)
- OSM and Geoapify (2026-09-25): Overpass "~2 concurrent queries per IP", "exponential
  backoff", attribution "Data from OpenStreetMap", data quality "excellent in Europe";
  Nominatim "Bulk geocoding forbidden" (policy: not encouraged, small jobs allowed), field
  `category` with `format=json`, "Best" geocoder; Geoapify "OSM + OpenAddresses + WhosOnFirst
  + GeoNames" for Places, `phone`/`website` in Places results, categories
  `service.financial.accounting`, `commercial.vehicle.car_dealer`; `User-Agent: claude-seo/1.7.0`

## 5. Heuristics Kept [H]

| Heuristic | Rationale |
|-----------|-----------|
| E-E-A-T weights 20/25/25/30 and score bands | Editorial; Trust highest because Google names it most important |
| Local score weights 25/20/20/15/10/10 | Editorial prioritization |
| >60-70% unique location content, swap test | Operationalizes Google's doorway policy; no threshold documented |
| 30+/50+ location page gates | Orchestrator quality gate |
| NAP consistency across page, schema, GBP | Supports Google's "complete and accurate info"; no consistency metric documented |
| Industry directory lists | Where customers look; no reach figures claimed |
| `areaServed` with named cities; subdirectory location URLs | Clear, crawlable structure; not Google-documented for local |
| Maps Health weights 25/20/20/15/10/10 (Tier 0: +10/+10/+5) | Editorial prioritization in `agents/seo-maps.md` |
| GBP checklist: 2/1/0 points, 24 fields, 250+ chars, 10+ photos, 30/7-day recency, 1+ post/week, industry multipliers, score bands | Editorial; Google publishes no per-field weights |
| Grid sizes, radii, 7x7 default; SoLV bands; Visibility Score | Editorial; Local Falcon publishes no bands |
| Review velocity (6 months), rating distribution, response rate reported without a target | Descriptive; Google documents no cadence or rate |
| Review manipulation patterns (2+ of list) | Operationalizes Google's "unusual volumes or patterns"; not proof |
| NAP mismatch Medium (name/address), Low (phone) | No cross-platform consistency rule documented |
