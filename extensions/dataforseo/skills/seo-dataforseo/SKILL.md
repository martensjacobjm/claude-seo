---
name: seo-dataforseo
description: >
  Live SEO data via DataForSEO MCP server. SERP analysis (Google, Bing, Yahoo,
  YouTube, Google Images), keyword research (volume, difficulty, intent, trends),
  backlink profiles, on-page analysis (Lighthouse, content parsing), competitor
  analysis, content analysis, business listings, AI visibility (ChatGPT scraper,
  LLM mention tracking), and domain analytics. Requires DataForSEO extension
  installed. Use when user says "dataforseo", "live SERP", "keyword volume",
  "backlink data", "competitor data", "AI visibility check", "LLM mentions",
  "image SERP", "google images", "image rankings", or "real search data".
user-invokable: true
argument-hint: "[command] [query]"
license: MIT
compatibility: "Requires DataForSEO MCP server (dataforseo-mcp-server 3.x api_request; deprecated 2.x per-endpoint tools also detected)"
metadata:
  author: AgriciDaniel
  version: "1.8.1"
  category: seo
---

# DataForSEO: Live SEO Data (Extension)

Live search data via the DataForSEO MCP server. Provides real-time SERP results
(organic + images), keyword metrics, backlink profiles, on-page analysis, content
analysis, business listings, AI visibility checking, and LLM mention tracking
across 10 DataForSEO APIs, called by endpoint path.

## Prerequisites

This skill requires the DataForSEO extension to be installed:
```bash
./extensions/dataforseo/install.sh
```

**Check availability:** DataForSEO is available when either is present:
- **v3** (`dataforseo-mcp-server` 3.x, what the installer sets up): the `dataforseo`
  server's `api_request` tool (shown as `mcp__dataforseo__api_request`, next to
  `docs_search`, `docs_index`, `docs_list_sections`). Call endpoints by path.
- **v2** (deprecated 2.x server): per-endpoint tools such as `serp_organic_live_advanced`.

If neither is present, say so visibly ("DataForSEO MCP not detected") and give the
install command. Never fall back silently to WebSearch or free APIs as if they were
DataForSEO data.

## Calling Convention (v3)

```
api_request({ method: "POST", path: "/v3/serp/google/organic/live/advanced",
  data: [{ keyword: "best coffee", location_code: 2840, language_code: "en", depth: 10 }] })
```

- `data` is the request body: one task object or an array of task objects. Live
  endpoints take **one task per call** (extra tasks are dropped with a warning).
- Default `.ai` mode trims the response, drops the `cost` field and sets `depth`/`limit`
  to **10** unless you pass them. Set `noAiMode: true` to get `cost` (needed for the
  cost report), the full schema, or to call `task_post`/`tasks_ready` endpoints.
- GET endpoints (locations, filters) take no `data`.
- Unsure of a field? Run `docs_search` with the path (e.g. `backlinks/summary/live`).
- Each command below lists **v3:** the endpoint and **v2:** the old tool name. Use the
  v2 name only when `api_request` is absent. Full map: `references/tool-catalog.md`.

## API Credit Awareness

DataForSEO charges per API call. Be efficient:
- Prefer bulk endpoints over multiple single calls
- Use default parameters (US, English) unless user specifies otherwise
- Pass `depth`/`limit` explicitly; they drive both result count and cost
- Cache results mentally within a session; don't re-fetch the same data
- Warn user before running expensive operations (full backlink crawls, large keyword lists)

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/seo dataforseo serp <keyword>` | Google organic SERP results |
| `/seo dataforseo serp-images <keyword>` | Google Images SERP results |
| `/seo dataforseo serp-youtube <keyword>` | YouTube search results |
| `/seo dataforseo youtube <video_id>` | YouTube video deep analysis |
| `/seo dataforseo keywords <seed>` | Keyword ideas and suggestions |
| `/seo dataforseo volume <keywords>` | Search volume for keywords |
| `/seo dataforseo difficulty <keywords>` | Keyword difficulty scores |
| `/seo dataforseo intent <keywords>` | Search intent classification |
| `/seo dataforseo trends <keyword>` | Google Trends data |
| `/seo dataforseo backlinks <domain>` | Full backlink profile |
| `/seo dataforseo competitors <domain>` | Competitor domain analysis |
| `/seo dataforseo ranked <domain>` | Ranked keywords for domain |
| `/seo dataforseo intersection <domains>` | Keyword/backlink overlap |
| `/seo dataforseo traffic <domains>` | Bulk traffic estimation |
| `/seo dataforseo subdomains <domain>` | Subdomains with ranking data |
| `/seo dataforseo top-searches <domain>` | Top queries mentioning domain |
| `/seo dataforseo onpage <url>` | On-page analysis (Lighthouse + parsing) |
| `/seo dataforseo tech <domain>` | Technology stack detection |
| `/seo dataforseo whois <domain>` | WHOIS registration data |
| `/seo dataforseo content <keyword/url>` | Content analysis and trends |
| `/seo dataforseo listings <keyword>` | Business listings search |
| `/seo dataforseo ai-scrape <query>` | ChatGPT web scraper for GEO |
| `/seo dataforseo ai-mentions <keyword>` | LLM mention tracking for GEO |

---

## SERP Analysis

### `/seo dataforseo serp <keyword>`

Fetch live Google organic search results.

**v3:** POST `/v3/serp/google/organic/live/advanced` · **v2:** `serp_organic_live_advanced`

**Default parameters:** location_code=2840 (US), language_code=en, device=desktop, depth=10. Billing is per 10 results, so depth=100 costs 10x; raise depth only when the user needs positions past 10.

**Also supports:** Bing and Yahoo: swap the engine in the path (`/v3/serp/bing/organic/live/advanced`, `/v3/serp/yahoo/organic/live/advanced`). On v2 use the tool's `search_engine` parameter.

**Output:** Rank, URL, title, description, domain, featured snippets, AI overview references, People Also Ask.

### `/seo dataforseo serp-youtube <keyword>`

Fetch YouTube search results for video-rich queries.

**v3:** POST `/v3/serp/youtube/organic/live/advanced` · **v2:** `serp_youtube_organic_live_advanced`

**Output:** Video title, channel, views, upload date, description, URL.

### `/seo dataforseo youtube <video_id>`

Deep analysis of a specific YouTube video: info, comments, and subtitles.

**v3:** POST `/v3/serp/youtube/video_info/live/advanced`, `/v3/serp/youtube/video_comments/live/advanced`, `/v3/serp/youtube/video_subtitles/live/advanced` · **v2:** `serp_youtube_video_info_live_advanced`, `serp_youtube_video_comments_live_advanced`, `serp_youtube_video_subtitles_live_advanced`

**Parameters:** video_id (the YouTube video ID, e.g., "dQw4w9WgXcQ")

**Output:** Video metadata (title, channel, views, likes, description), top comments with engagement, subtitle/transcript text.

### `/seo dataforseo serp-images <keyword>`

Fetch live Google Images search results. See which images rank for a keyword,
which domains dominate image results, and identify visual content opportunities.

**v3:** POST `/v3/serp/google/images/live/advanced` · **v2:** none (the 2.x server had no Google Images tool; this command needs v3)

**Default parameters:** location_code=2840 (US), language_code=en, device=desktop, depth=100 (Images bills per SERP of up to 100 results)

**Parameters:** keyword (required), depth (optional, max 200, billed per 100-result SERP), search_param (optional, e.g. "site:example.com")

**Cost warning:** Using `site:` or `filetype:` operators incurs **5x API cost**. Warn user before running filtered queries.

**Output:** Position, title, alt text, source page URL, direct image URL, domain, encoded URL.

**Analysis to provide:**
- Domain dominance: which sites own the most image positions (top 10 domains by count)
- Alt text patterns: common title/alt text patterns in top-ranking images
- Format distribution: WebP vs JPEG vs PNG in top results (infer from image_url extension)
- Opportunity identification: keywords where user has organic rankings but no image presence

---

## Keyword Research

### `/seo dataforseo keywords <seed>`

Generate keyword ideas, suggestions, and related terms from a seed keyword.

**v3:** POST `/v3/dataforseo_labs/google/keyword_ideas/live`, `/v3/dataforseo_labs/google/keyword_suggestions/live`, `/v3/dataforseo_labs/google/related_keywords/live` · **v2:** `dataforseo_labs_google_keyword_ideas`, `dataforseo_labs_google_keyword_suggestions`, `dataforseo_labs_google_related_keywords`

**Default parameters:** location_code=2840 (US), language_code=en, limit=50

**Output:** Keyword, search volume, CPC, competition level, keyword difficulty, trend.

### `/seo dataforseo volume <keywords>`

Get search volume and metrics for a list of keywords.

**v3:** POST `/v3/keywords_data/google_ads/search_volume/live` · **v2:** `kw_data_google_ads_search_volume`

**Parameters:** keywords (array, comma-separated), location_code, language_code

**Output:** Keyword, monthly search volume, CPC, competition, monthly trend data.

### `/seo dataforseo difficulty <keywords>`

Calculate keyword difficulty scores for ranking competitiveness.

**v3:** POST `/v3/dataforseo_labs/google/bulk_keyword_difficulty/live` · **v2:** `dataforseo_labs_bulk_keyword_difficulty`

**Parameters:** keywords (array), location_code, language_code

**Output:** Keyword, difficulty score (0-100), interpretation (Easy/Medium/Hard/Very Hard).

### `/seo dataforseo intent <keywords>`

Classify keywords by user search intent.

**v3:** POST `/v3/dataforseo_labs/google/search_intent/live` · **v2:** `dataforseo_labs_search_intent`

**Parameters:** keywords (array), location_code, language_code

**Output:** Keyword, intent type (informational, navigational, commercial, transactional), confidence score.

### `/seo dataforseo trends <keyword>`

Analyze keyword trends over time using Google Trends data.

**v3:** POST `/v3/keywords_data/google_trends/explore/live` · **v2:** `kw_data_google_trends_explore`

**Parameters:** keywords (array), location_code, date_from, date_to, language_code

**Output:** Keyword, time series data, trend direction, seasonality signals.

---

## Domain & Competitor Analysis

### `/seo dataforseo backlinks <domain>`

Comprehensive backlink profile analysis.

**v3:** POST `/v3/backlinks/{summary,backlinks,anchors,referring_domains,bulk_spam_score,timeseries_summary}/live` · **v2:** `backlinks_summary`, `backlinks_backlinks`, `backlinks_anchors`, `backlinks_referring_domains`, `backlinks_bulk_spam_score`, `backlinks_timeseries_summary`

**Default parameters:** limit=100 per sub-call

**Output:** Total backlinks, referring domains, domain rank, spam score, top anchors, new/lost backlinks over time, dofollow ratio, top referring domains.

### `/seo dataforseo competitors <domain>`

Identify competing domains and estimate traffic.

**v3:** POST `/v3/dataforseo_labs/google/{competitors_domain,domain_rank_overview,bulk_traffic_estimation}/live` · **v2:** `dataforseo_labs_google_competitors_domain`, `dataforseo_labs_google_domain_rank_overview`, `dataforseo_labs_bulk_traffic_estimation`

**Output:** Competitor domains, keyword overlap %, estimated traffic, domain rank, common keywords.

### `/seo dataforseo ranked <domain>`

List keywords a domain ranks for with positions and page data.

**v3:** POST `/v3/dataforseo_labs/google/ranked_keywords/live`, `/v3/dataforseo_labs/google/relevant_pages/live` · **v2:** `dataforseo_labs_google_ranked_keywords`, `dataforseo_labs_google_relevant_pages`

**Default parameters:** limit=100, location_code=2840

**Output:** Keyword, position, URL, search volume, traffic share, SERP features.

### `/seo dataforseo intersection <domain1> <domain2> [...]`

Find shared keywords and backlink sources across 2-20 domains.

**v3:** POST `/v3/dataforseo_labs/google/domain_intersection/live`, `/v3/backlinks/domain_intersection/live` · **v2:** `dataforseo_labs_google_domain_intersection`, `backlinks_domain_intersection`

**Parameters:** domains (2-20 array)

**Output:** Shared keywords with positions per domain, shared backlink sources, unique keywords per domain.

### `/seo dataforseo traffic <domains>`

Estimate organic search traffic for one or more domains.

**v3:** POST `/v3/dataforseo_labs/google/bulk_traffic_estimation/live` · **v2:** `dataforseo_labs_bulk_traffic_estimation`

**Parameters:** domains (array)

**Output:** Domain, estimated organic traffic, estimated traffic cost, top keywords.

### `/seo dataforseo subdomains <domain>`

Enumerate subdomains with their ranking data and traffic estimates.

**v3:** POST `/v3/dataforseo_labs/google/subdomains/live` · **v2:** `dataforseo_labs_google_subdomains`

**Parameters:** target (domain), location_code, language_code

**Output:** Subdomain, ranked keywords count, estimated traffic, organic cost.

### `/seo dataforseo top-searches <domain>`

Find the most popular search queries that mention a specific domain in results.

**v3:** POST `/v3/dataforseo_labs/google/top_searches/live` · **v2:** `dataforseo_labs_google_top_searches`

**Parameters:** target (domain), location_code, language_code

**Output:** Query, search volume, domain position, SERP features, traffic share.

---

## Technical / On-Page

### `/seo dataforseo onpage <url>`

Run on-page analysis including Lighthouse audit and content parsing.

**v3:** POST `/v3/on_page/instant_pages`, `/v3/on_page/content_parsing/live`, `/v3/on_page/lighthouse/live/json` · **v2:** `on_page_instant_pages`, `on_page_content_parsing`, `on_page_lighthouse`

**Usage:**
- Instant pages (`on_page_instant_pages`): quick page analysis (status codes, meta tags, content size, page timing, broken links, on-page checks)
- Content parsing (`on_page_content_parsing`): extract and parse page content (plain text, word count, structure)
- Lighthouse (`on_page_lighthouse`): full Lighthouse audit (performance score, accessibility, best practices, SEO, Core Web Vitals)

**Output:** Pages crawled, status codes, meta tags, titles, content size, load times, Lighthouse scores, broken links, resource analysis.

### `/seo dataforseo tech <domain>`

Detect technologies used on a domain.

**v3:** POST `/v3/domain_analytics/technologies/domain_technologies/live` · **v2:** `domain_analytics_technologies_domain_technologies`

**Output:** Technology name, version, category (CMS, analytics, CDN, framework, etc.).

### `/seo dataforseo whois <domain>`

Retrieve WHOIS registration data.

**v3:** POST `/v3/domain_analytics/whois/overview/live` · **v2:** `domain_analytics_whois_overview`

**Output:** Registrar, creation date, expiration date, nameservers, registrant info (if public).

---

## Content & Business Data

### `/seo dataforseo content <keyword/url>`

Analyze content quality, search for content by topic, and track phrase trends.

**v3:** POST `/v3/content_analysis/{search,summary,phrase_trends}/live` · **v2:** `content_analysis_search`, `content_analysis_summary`, `content_analysis_phrase_trends`

**Parameters:** keyword (for search/trends) or URL (for summary)

**Output:** Content matches with quality scores, sentiment analysis, readability metrics, phrase trend data over time.

### `/seo dataforseo listings <keyword>`

Search business listings for local SEO competitive analysis.

**v3:** POST `/v3/business_data/business_listings/search/live` · **v2:** `business_data_business_listings_search`

**Parameters:** keyword, location (optional)

**Output:** Business name, description, category, address, phone, domain, rating, review count, claimed status.

---

## AI Visibility / GEO

### `/seo dataforseo ai-scrape <query>`

Scrape what ChatGPT web search returns for a query. Real GEO visibility check: see which sources ChatGPT cites for your target keywords.

**v3:** POST `/v3/ai_optimization/chat_gpt/llm_scraper/live/advanced` · **v2:** `ai_optimization_chat_gpt_scraper`

**Parameters:** query, location_code (optional), language_code (optional). Look up locations with GET `/v3/ai_optimization/chat_gpt/llm_scraper/locations` (v2: `ai_optimization_chat_gpt_scraper_locations`).

**Output:** ChatGPT response content, cited sources/URLs, referenced domains.

### `/seo dataforseo ai-mentions <keyword>`

Track how LLMs mention brands, domains, and topics. Critical for GEO. Measures actual AI visibility across multiple LLM platforms.

**v3:** POST `/v3/ai_optimization/llm_mentions/{search_mentions,top_mentioned_domains,top_mentioned_pages,target_metrics}/live` · **v2:** `ai_opt_llm_ment_search`, `ai_opt_llm_ment_top_domains`, `ai_opt_llm_ment_top_pages`, `ai_opt_llm_ment_agg_metrics`

**Parameters:** keyword, location_code (optional), language_code (optional). Look up locations/languages with GET `/v3/ai_optimization/llm_mentions/locations_and_languages` (v2: `ai_opt_llm_ment_loc_and_lang`).

**Cost warning:** LLM Mentions is billed per request plus per row (see pricing). Confirm with the user before large `limit` values.

**Workflow:**
1. Search mentions: `search_mentions/live` (find mentions of a brand/keyword across LLM responses)
2. Top cited domains: `top_mentioned_domains/live` (which domains are most cited for this topic)
3. Top cited pages: `top_mentioned_pages/live` (which specific pages are most cited)
4. Aggregate metrics: `target_metrics/live` (overall mention volume, trends)

**Output:** LLM mention count, top cited domains with frequency, top cited pages, mention trends over time, cross-platform visibility scores.

**Advanced:** `multi_target_metrics/live` (v2: `ai_opt_llm_ment_cross_agg_metrics`) for multi-target comparison (how mentions differ across ChatGPT, Claude, Perplexity, etc.).

---

## Available Utility Tools

Other endpoints (location lookups, filters, bulk and historical data, Amazon) have no
dedicated command. Load `references/tool-catalog.md` for the full v2-name to v3-path map.

## Cross-Skill Integration

When DataForSEO is detected (v3 `api_request` or v2 tools), other claude-seo skills use
live data. Paths are v3; the v2 tool name is in parentheses:

- **seo-audit**: spawn the `seo-dataforseo` agent for SERP, backlink, on-page, and listings data
- **seo-technical**: `/v3/on_page/instant_pages` (`on_page_instant_pages`), `/v3/on_page/lighthouse/live/json` (`on_page_lighthouse`), `/v3/domain_analytics/technologies/domain_technologies/live` for stack detection
- **seo-content**: `/v3/keywords_data/google_ads/search_volume/live` (`kw_data_google_ads_search_volume`), `/v3/dataforseo_labs/google/bulk_keyword_difficulty/live`, `/v3/dataforseo_labs/google/search_intent/live`, `/v3/content_analysis/summary/live`
- **seo-page**: `/v3/serp/google/organic/live/advanced` (`serp_organic_live_advanced`), `/v3/backlinks/summary/live` (`backlinks_summary`)
- **seo-images**: `/v3/serp/google/images/live/advanced` (v3 only), cross-referenced with the on-page image audit
- **seo-geo**: `/v3/ai_optimization/chat_gpt/llm_scraper/live/advanced` (`ai_optimization_chat_gpt_scraper`), `/v3/ai_optimization/llm_mentions/search_mentions/live` (`ai_opt_llm_ment_search`)
- **seo-plan**: `/v3/dataforseo_labs/google/{competitors_domain,domain_intersection,bulk_traffic_estimation}/live`
- **seo-backlinks**, **seo-local**, **seo-maps**: see those skills for their endpoints

## Error Handling

- **MCP server not connected**: Report that DataForSEO extension is not installed or MCP server is unreachable. Suggest running `./extensions/dataforseo/install.sh`
- **API authentication failed**: Report invalid credentials. Suggest checking DataForSEO API login/password in MCP config
- **Rate limit exceeded**: Report the limit hit and suggest waiting before retrying
- **No results returned**: Report "no data found" for the query rather than guessing. Suggest broadening the query or checking location/language codes
- **Invalid location code**: Report the error and look up the code (GET `/v3/serp/google/locations`, or the endpoint's own locations list)
- **Unknown path / 404 from `api_request`**: Check the path with `docs_index` or `docs_search`; paths in `references/tool-catalog.md` were verified 2026-09-25

## Output Formatting

Match existing claude-seo output patterns:
- Use tables for comparative data
- Prioritize issues as Critical > High > Medium > Low
- Include specific, actionable recommendations
- Show scores as XX/100 where applicable
- Note data source as "DataForSEO (live)" to distinguish from static analysis
- Report the credits used when known (the `cost` field needs `noAiMode: true` on v3)
