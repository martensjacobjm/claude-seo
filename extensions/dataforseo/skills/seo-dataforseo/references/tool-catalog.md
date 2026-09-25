<!-- Updated: 2026-09-25 -->
# DataForSEO: v2 Tool Name to v3 Endpoint Map

> Load this when a skill names a DataForSEO tool, or when you need an endpoint
> without a dedicated `/seo dataforseo` command.

## How to call (dataforseo-mcp-server 3.x)

v3 (npm `dataforseo-mcp-server` 3.0.0+, 2026-08-11; `latest` 3.1.1, 2026-08-25) has four
tools: `api_request`, `docs_index`, `docs_list_sections`, `docs_search`. Claude Code
shows them with the server prefix, e.g. `mcp__dataforseo__api_request`.
`api_request` input: `method` (GET/POST/PUT/DELETE, required), `path` (e.g.
`/v3/backlinks/summary/live`) or `url`, `data` (task object or array of task objects),
`noAiMode` (boolean, default false). v3 has no v2 compatibility mode or flag.

- Default `.ai` mode: cropped response, no `cost` field, floats rounded, and `depth`/`limit`
  default to **10**. Pass `depth`/`limit` explicitly. Set `noAiMode: true` when you need the
  cost, the full schema, or a `task_post`/`tasks_ready` call (`.ai` is documented for Live
  and Task GET endpoints only).
- Live endpoints take one task per call; the server drops extra tasks with a warning.
- Unsure of a field? `docs_search` with the path (e.g. `serp/google/organic/live/advanced`).
- v2 (deprecated) exposed one tool per endpoint. Use the name below only if `api_request`
  is absent. v2 tools used their own parameter names; v3 takes the raw API fields.

Sources: v2 names and paths from the npm tarballs `dataforseo-mcp-server@2.9.13` and
`@2.8.10`; every path checked against https://docs.dataforseo.com/v3/llms.txt (2026-09-25).

## SERP

| v2 tool | v3 `api_request` |
|---|---|
| `serp_organic_live_advanced` | POST `/v3/serp/{google,bing,yahoo}/organic/live/advanced` |
| `serp_locations` | GET `/v3/serp/{se}/locations` (add `/{country_iso}` for cities) |
| `serp_youtube_organic_live_advanced` | POST `/v3/serp/youtube/organic/live/advanced` |
| `serp_youtube_video_info_live_advanced` | POST `/v3/serp/youtube/video_info/live/advanced` |
| `serp_youtube_video_comments_live_advanced` | POST `/v3/serp/youtube/video_comments/live/advanced` |
| `serp_youtube_video_subtitles_live_advanced` | POST `/v3/serp/youtube/video_subtitles/live/advanced` |
| `serp_youtube_locations` | GET `/v3/serp/youtube/locations` |
| none in v2 (never shipped) | POST `/v3/serp/google/images/live/advanced` |
| none in v2 | POST `/v3/serp/google/maps/live/advanced`, `/v3/serp/google/local_finder/live/advanced` |

## Keywords Data

| v2 tool | v3 `api_request` |
|---|---|
| `kw_data_google_ads_search_volume` | POST `/v3/keywords_data/google_ads/search_volume/live` |
| `kw_data_google_ads_locations` | GET `/v3/keywords_data/google_ads/locations` |
| `kw_data_google_trends_explore` | POST `/v3/keywords_data/google_trends/explore/live` |
| `kw_data_google_trends_categories` | GET `/v3/keywords_data/google_trends/categories` |
| `kw_data_dfs_trends_explore` | POST `/v3/keywords_data/dataforseo_trends/explore/live` |
| `kw_data_dfs_trends_demography` | POST `/v3/keywords_data/dataforseo_trends/demography/live` |
| `kw_data_dfs_trends_subregion_interests` | POST `/v3/keywords_data/dataforseo_trends/subregion_interests/live` |

## DataForSEO Labs (all POST, `/v3/dataforseo_labs/...`)

| v2 tool | v3 path suffix |
|---|---|
| `dataforseo_labs_google_keyword_ideas` | `google/keyword_ideas/live` |
| `dataforseo_labs_google_keyword_suggestions` | `google/keyword_suggestions/live` |
| `dataforseo_labs_google_related_keywords` | `google/related_keywords/live` |
| `dataforseo_labs_google_keyword_overview` | `google/keyword_overview/live` |
| `dataforseo_labs_google_historical_keyword_data` | `google/historical_keyword_data/live` |
| `dataforseo_labs_bulk_keyword_difficulty` | `google/bulk_keyword_difficulty/live` |
| `dataforseo_labs_search_intent` | `google/search_intent/live` |
| `dataforseo_labs_google_keywords_for_site` | `google/keywords_for_site/live` |
| `dataforseo_labs_google_ranked_keywords` | `google/ranked_keywords/live` |
| `dataforseo_labs_google_relevant_pages` | `google/relevant_pages/live` |
| `dataforseo_labs_google_competitors_domain` | `google/competitors_domain/live` |
| `dataforseo_labs_google_serp_competitors` | `google/serp_competitors/live` |
| `dataforseo_labs_google_domain_intersection` | `google/domain_intersection/live` |
| `dataforseo_labs_google_page_intersection` | `google/page_intersection/live` |
| `dataforseo_labs_google_domain_rank_overview` | `google/domain_rank_overview/live` |
| `dataforseo_labs_google_historical_rank_overview` | `google/historical_rank_overview/live` |
| `dataforseo_labs_google_historical_serps` (2.8: `..._historical_serp`) | `google/historical_serps/live` |
| `dataforseo_labs_bulk_traffic_estimation` | `google/bulk_traffic_estimation/live` |
| `dataforseo_labs_google_subdomains` | `google/subdomains/live` |
| `dataforseo_labs_google_top_searches` | `google/top_searches/live` |
| `dataforseo_labs_amazon_bulk_search_volume` | `amazon/bulk_search_volume/live` |
| `dataforseo_labs_amazon_related_keywords` | `amazon/related_keywords/live` |
| `dataforseo_labs_amazon_ranked_keywords` | `amazon/ranked_keywords/live` |
| `dataforseo_labs_amazon_product_competitors` | `amazon/product_competitors/live` |
| `dataforseo_labs_amazon_product_kw_intersections` | `amazon/product_keyword_intersections/live` |
| `dataforseo_labs_amazon_product_rank_overview` | `amazon/product_rank_overview/live` |
| `dataforseo_labs_available_filters` | GET `available_filters` |

## Backlinks (all POST `/v3/backlinks/<name>/live` unless noted)

| v2 tool | `<name>` |
|---|---|
| `backlinks_summary` | `summary` |
| `backlinks_backlinks` | `backlinks` |
| `backlinks_anchors` | `anchors` |
| `backlinks_referring_domains` | `referring_domains` |
| `backlinks_referring_networks` | `referring_networks` |
| `backlinks_domain_pages` / `backlinks_domain_pages_summary` | `domain_pages` / `domain_pages_summary` |
| `backlinks_competitors` | `competitors` |
| `backlinks_domain_intersection` / `backlinks_page_intersection` | `domain_intersection` / `page_intersection` |
| `backlinks_timeseries_summary` | `timeseries_summary` |
| `backlinks_timeseries_new_lost_summary` | `timeseries_new_lost_summary` |
| `backlinks_bulk_spam_score` | `bulk_spam_score` |
| `backlinks_bulk_ranks` / `backlinks_bulk_backlinks` | `bulk_ranks` / `bulk_backlinks` |
| `backlinks_bulk_referring_domains` | `bulk_referring_domains` |
| `backlinks_bulk_new_lost_backlinks` | `bulk_new_lost_backlinks` |
| `backlinks_bulk_new_lost_referring_domains` | `bulk_new_lost_referring_domains` |
| `backlinks_bulk_pages_summary` | `bulk_pages_summary` |
| `backlinks_available_filters` | GET `/v3/backlinks/available_filters` |

## OnPage, Domain Analytics, Content Analysis, Business Data

| v2 tool | v3 `api_request` |
|---|---|
| `on_page_instant_pages` | POST `/v3/on_page/instant_pages` |
| `on_page_content_parsing` | POST `/v3/on_page/content_parsing/live` |
| `on_page_lighthouse` | POST `/v3/on_page/lighthouse/live/json` |
| `domain_analytics_technologies_domain_technologies` | POST `/v3/domain_analytics/technologies/domain_technologies/live` |
| `domain_analytics_technologies_available_filters` | GET `/v3/domain_analytics/technologies/available_filters` |
| `domain_analytics_whois_overview` | POST `/v3/domain_analytics/whois/overview/live` |
| `domain_analytics_whois_available_filters` | GET `/v3/domain_analytics/whois/available_filters` |
| `content_analysis_search` | POST `/v3/content_analysis/search/live` |
| `content_analysis_summary` | POST `/v3/content_analysis/summary/live` |
| `content_analysis_phrase_trends` | POST `/v3/content_analysis/phrase_trends/live` |
| `business_data_business_listings_search` | POST `/v3/business_data/business_listings/search/live` |
| `business_data_business_listings_filters` | GET `/v3/business_data/business_listings/available_filters` |
| none in v2 | POST `/v3/business_data/google/my_business_info/live`; `/v3/business_data/google/reviews/task_post` (`noAiMode: true`) then GET `.../reviews/task_get/{id}` |

## AI Optimization

| v2 tool | v3 `api_request` |
|---|---|
| `ai_optimization_chat_gpt_scraper` | POST `/v3/ai_optimization/chat_gpt/llm_scraper/live/advanced` |
| `ai_optimization_chat_gpt_scraper_locations` | GET `/v3/ai_optimization/chat_gpt/llm_scraper/locations` |
| `ai_optimization_llm_response` | POST `/v3/ai_optimization/{chat_gpt,claude,gemini,perplexity}/llm_responses/live` |
| `ai_optimization_llm_models` | GET `/v3/ai_optimization/{llm}/llm_responses/models` |
| `ai_optimization_keyword_data_search_volume` | POST `/v3/ai_optimization/ai_keyword_data/keywords_search_volume/live` |
| `ai_opt_kw_data_loc_and_lang` | GET `/v3/ai_optimization/ai_keyword_data/locations_and_languages` |
| `ai_opt_llm_ment_search` | POST `/v3/ai_optimization/llm_mentions/search_mentions/live` * |
| `ai_opt_llm_ment_top_domains` | POST `/v3/ai_optimization/llm_mentions/top_mentioned_domains/live` * |
| `ai_opt_llm_ment_top_pages` | POST `/v3/ai_optimization/llm_mentions/top_mentioned_pages/live` * |
| `ai_opt_llm_ment_agg_metrics` | POST `/v3/ai_optimization/llm_mentions/target_metrics/live` * |
| `ai_opt_llm_ment_cross_agg_metrics` | POST `/v3/ai_optimization/llm_mentions/multi_target_metrics/live` * |
| `ai_opt_llm_ment_loc_and_lang` | GET `/v3/ai_optimization/llm_mentions/locations_and_languages` |
| `ai_optimization_llm_mentions_filters` | GET `/v3/ai_optimization/llm_mentions/available_filters` |

\* The v2 server called `search/live`, `top_domains/live`, `top_pages/live`,
`aggregated_metrics/live` and `cross_aggregated_metrics/live`. The docs index no longer
lists those; the paths above are the documented ones. Run `docs_search` on the path
before a first call to confirm the request fields.

## Merchant (Amazon)

| v2 tool | v3 `api_request` |
|---|---|
| `merchant_amazon_products_live_advanced` | POST `/v3/merchant/amazon/products/live/advanced` |
| `merchant_amazon_asin_live_advanced` | POST `/v3/merchant/amazon/asin/live/advanced` |
| `merchant_amazon_sellers_live_advanced` | POST `/v3/merchant/amazon/sellers/live/advanced` |
| `merchant_amazon_locations` | GET `/v3/merchant/amazon/locations` |
