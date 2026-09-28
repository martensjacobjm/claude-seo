# Free Keyword Data Sources

Reference for keyword research without paid DataForSEO calls. Script:
`scripts/free_keyword_data.py` (`sources`, `own-queries`, `ideas`, `volume`, `trends`).
All facts below were checked against primary docs on **2026-09-28** unless noted.

## Hard rule: no SERP scraping

Never query Google or Bing result pages or undocumented endpoints (including
trends.google.com internals or wrappers such as pytrends).
- Google spam policies, "Machine-generated traffic": "sending automated queries to Google.
  This includes scraping results for rank-checking purposes or other types of automated
  access to Google Search conducted without express permission ... Such activities violate
  our spam policies and the Google Terms of Service."
  https://developers.google.com/search/docs/essentials/spam-policies (updated 2026-08-28)
- Google Terms of Service (effective 2026-07-30) forbid "using automated means to access
  content from any of our services in violation of the machine-readable instructions on our
  web pages (for example, robots.txt files ...)". https://policies.google.com/terms
- `www.google.com/robots.txt` and `www.bing.com/robots.txt` both `Disallow: /search`.

## Verified sources

| Source | What you get | Cost | Quota / limits | Access needed | Docs (date on page) |
|--------|-------------|------|----------------|---------------|---------------------|
| **GSC Search Analytics API** | Own-site queries/pages: clicks, impressions, CTR, avg position | No charge | 1,200 QPM per site and per user; 40,000 QPM and 30M QPD per project; 50K rows/day per search type; rowLimit 1-25,000 (default 1,000), page with startRow | Verified property; OAuth or service account added as user | [query](https://developers.google.com/webmaster-tools/v1/searchanalytics/query) (2026-08-11), [limits](https://developers.google.com/webmaster-tools/limits) (2025-08-28), [all data](https://developers.google.com/webmaster-tools/v1/how-tos/all-your-data) (2025-08-28) |
| **Google Ads API Keyword Planner** (`KeywordPlanIdeaService`) | Ideas + historical metrics: `avg_monthly_searches`, 12 monthly volumes, competition, top-of-page bids | No API fee documented (rate sheet lists only non-compliance fees) | 1 req/s per customer ID for GenerateKeywordIdeas / HistoricalMetrics / Forecast; Basic = 15,000 ops/day | Developer token at **Basic** or Standard. Test = test accounts only; Explorer blocks all planning services. Basic needs brand verification (automated review). Manager account no longer required | [access levels](https://developers.google.com/google-ads/api/docs/api-policy/access-levels), [developer token](https://developers.google.com/google-ads/api/docs/api-policy/developer-token), [quotas](https://developers.google.com/google-ads/api/docs/best-practices/quotas) (all 2026-09-23), [metrics](https://developers.google.com/google-ads/api/reference/rpc/v25/KeywordPlanHistoricalMetrics) (2026-07-22) |
| **Google Trends API** | Consistently scaled interest, rolling 5 years, daily to yearly, regions | No pricing published | Not published | **Alpha, application-gated.** Page still says "accepting applications for alpha testers"; request schema not public | [trends](https://developers.google.com/search/apis/trends), [announcement](https://developers.google.com/search/blog/2025/07/trends-api) (2025-07-24) |
| **Bing Webmaster keyword research** | `GetKeywordStats(q, country, language)` weekly impressions; `GetKeyword(q, country, language, startDate, endDate)`; `GetRelatedKeywords(same)` related terms with `Impressions` + `BroadImpressions` | Free | Not published ("unchanged" after protocol retirement) | Bing Webmaster account + API key (one per user; not site-bound) | [IWebmasterApi](https://learn.microsoft.com/dotnet/api/microsoft.bing.webmaster.api.interfaces.iwebmasterapi?view=bing-webmaster-dotnet), [help](https://www.bing.com/webmasters/help/keyword-research-628070b6) |
| **Bing Webmaster own-site stats** | `GetQueryStats(siteUrl)`, `GetPageStats(siteUrl)`, `GetPageQueryStats(siteUrl, page)`: Clicks, Impressions, AvgClickPosition, AvgImpressionPosition per week ("updated every week") | Free | Not published | Verified site + API key | [GetQueryStats](https://learn.microsoft.com/dotnet/api/microsoft.bing.webmaster.api.interfaces.iwebmasterapi.getquerystats?view=bing-webmaster-dotnet), [GetPageQueryStats](https://learn.microsoft.com/dotnet/api/microsoft.bing.webmaster.api.interfaces.iwebmasterapi.getpagequerystats?view=bing-webmaster-dotnet) |
| **Wikimedia pageviews** (heuristic) | Monthly human pageviews per Wikipedia article: topic-interest **proxy**, not search volume | Free, no key; data CC0 | 10 req/min unidentified, 200 req/min with a descriptive User-Agent | None | [page views](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/reference/page-views.html), [access policy](https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/documentation/access-policy.html), [rate limits](https://www.mediawiki.org/wiki/Wikimedia_APIs/Rate_limits) (2026-06-03) |

### Notes per source
- **GSC**: dimensions `query, page, country, device, searchAppearance, date, hour`; filter
  operators `contains, equals, notContains, notEquals, includingRegex, excludingRegex` (RE2).
  You can filter on a dimension without grouping by it. `searchAppearance`: query grouped by
  it first to list values, then filter per type. Position is your own site's average; there
  is no competitor data. Anonymized queries are dropped from query rows.
- **Keyword Planner**: `avg_monthly_searches` = "Approximate number of monthly searches on
  this query, averaged for the past 12 months" (int64, a single number). Ranges/bucketing for
  low- or no-spend accounts is widely reported for the Keyword Planner UI but is **not**
  stated in the API reference: treat values from a no-spend account as coarse.
  `scripts/keyword_planner.py` reuses the Claude SEO OAuth token, which is minted without the
  `https://www.googleapis.com/auth/adwords` scope; Ads calls need a token with that scope.
- **Bing**: SOAP and POX endpoints were retired 2026-08-31; only
  `https://ssl.bing.com/webmaster/api.svc/json/<Method>` remains (same key, same methods,
  DateTime as `/Date(ms)/`). Microsoft documents keyword method names and properties only;
  treating `Impressions` as strict and `BroadImpressions` as broad match is an assumption.
  Bing counts are exact impressions on Bing, not Google monthly searches.
- **Wikipedia**: the script resolves the keyword to the top search hit (MediaWiki Action API)
  and reports `matched_article`; check it before using the number.

## Units: never mix silently

| Source | Unit label in script output |
|--------|-----------------------------|
| Keyword Planner | `google_searches_per_month_avg_12m` |
| Bing GetKeywordStats | `bing_impressions_last_N_weeks` |
| Bing GetRelatedKeywords | `bing_impressions_in_period` |
| Wikipedia | `wikipedia_pageviews_per_month_avg` (heuristic) |

`volume` groups values per keyword by source and unit, sets `comparable: false` when units
differ, and never sums or averages across sources.

## DataForSEO endpoint to free alternative

| DataForSEO (v3 path) | Free, legal alternative | Gap |
|----------------------|------------------------|-----|
| `keywords_data/google_ads/search_volume` | Keyword Planner `volume` (Basic access) | Coarse without spend; needs Ads setup |
| `dataforseo_labs/google/keyword_ideas`, `keyword_suggestions`, `related_keywords` | Keyword Planner ideas; Bing GetRelatedKeywords | No difficulty score; Bing data is Bing-only |
| `keywords_data/google_trends/explore` | None generally available (Trends API alpha). Proxies: Keyword Planner 12-month volumes, Bing weekly stats, GSC impressions by date, Wikipedia pageviews | No Google Trends index |
| `dataforseo_labs/google/bulk_keyword_difficulty` | **None.** Heuristics only (e.g. Keyword Planner competition is ad competition, not SEO difficulty) | Real gap |
| `dataforseo_labs/google/search_intent` | None as data; classify manually from the query text | Real gap |
| `serp/google/organic/live/advanced` (rank for any keyword) | **None.** Own-site average position from GSC / Bing only | Scraping is prohibited |
| `dataforseo_labs/google/ranked_keywords` (own domain) | GSC `own-queries` (+ Bing GetQueryStats) | Only your verified sites |
| `ranked_keywords`, `competitors_domain`, `domain_intersection`, `bulk_traffic_estimation` for competitors | **None** | No free competitor keyword or traffic data |
| `backlinks/*` | Partial: see `free-backlink-sources.md` (Moz free tier, Bing for own verified sites, Common Crawl) | No full commercial link index |
| `ai_optimization/*` (LLM mentions, ChatGPT scraper) | **None.** For own site: Bing Webmaster AI Performance export (`bing_webmaster.py ai-performance`) and GSC generative AI report export | No cross-site LLM mention data |
| `on_page/*` | Local tools: `fetch_page.py`, `parse_html.py`, PageSpeed Insights API | Not a DataForSEO equivalent in scale |

## Recommended order
1. `python scripts/free_keyword_data.py sources` to see what is configured.
2. Own-site demand first: `own-queries <property>` (real clicks/impressions/position).
3. Expansion: `ideas <seeds...>`, then `volume <keywords...>`.
4. Use DataForSEO only for the gaps marked **None** above, and say that it is paid.
