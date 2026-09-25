# Free Backlink Data Sources

Reference for the seo-backlinks skill. Loaded on demand when analyzing backlinks
with free sources.

## Source Comparison

| Source | Auth | Any Domain? | Data Quality | Coverage vs Commercial | Rate Limit |
|--------|------|-------------|-------------|----------------------|------------|
| **Moz API** | API key (free signup) | Yes | ★★★★☆ | ~70% for DA/PA (unverified estimate) | 1 req/10s, 2,500 rows/mo |
| **Bing Webmaster** | API key (free) | Verified sites only | ★★★☆☆ | Not published | Not documented (script waits 1s between calls) |
| **Common Crawl** | None (public) | Yes | ★★★☆☆ | ~25-40% domains (unverified estimate) | N/A |
| **Verification Crawler** | None | Yes | ★★★★★ (binary) | N/A (checks known links) | 1 req/s per domain |
| **DataForSEO** (paid) | API key | Yes | ★★★★★ | ~90%+ (unverified estimate) | Per plan |

Star ratings and weights below are this skill's own heuristics, not vendor figures.

## Confidence Weighting

When merging data from multiple sources, apply confidence weights to each metric:

| Source | Weight | Rationale |
|--------|--------|-----------|
| DataForSEO | 1.00 | Commercial-grade, real-time, comprehensive |
| Verification Crawler | 0.95 | Direct observation (binary: link exists or not) |
| Moz API | 0.85 | Large commercial index, established metrics, 3-day update lag |
| Bing Webmaster | 0.70 | Sampled inbound links for verified sites only, authoritative for Bing-indexed pages |
| Common Crawl | 0.50 | Domain-level only, quarterly updates, no anchor text |

**Composite formula:**
```
weighted_score = Σ(source_score × confidence × factor_weight) / Σ(confidence × factor_weight)
```

When only Common Crawl is available, cap the maximum health score at 70/100 and note
"limited to domain-level metrics" in the report.

## Source Details

### Moz API (Tier 1)
- **Endpoint:** `https://api.moz.com/jsonrpc` (JSON-RPC 2.0)
- **Free tier:** 2,500 rows/month, 1 request per 10 seconds (verify current limits at https://moz.com/products/api — free tier limits may change)
- **Signup:** https://moz.com/products/api (credit card required, not charged)
- **Data:** Domain Authority (0-100), Page Authority, Spam Score (1-17%), link counts,
  referring domains, anchor text distribution
- **Script:** `scripts/moz_api.py`
- **Commands:** `metrics`, `domains`, `anchors`, `pages`
- **Blind spots:** No link velocity, no toxic link patterns beyond Spam Score,
  3-day update lag, smaller index than Ahrefs/Semrush

### Bing Webmaster Tools (Tier 2)
- **Endpoint:** `https://ssl.bing.com/webmaster/api.svc/json/`
- **Free tier:** Free for verified sites; Microsoft publishes no link-API quota
- **Signup:** https://www.bing.com/webmasters (Microsoft account)
- **Comparison:** Competitor comparison only for sites verified in your account (no
  competitor method in the API). `compare` returns status `error` when either site's
  lookup fails; use DataForSEO or Moz for real competitor gaps
- **Data:** Pages with inbound-link counts (`GetLinkCounts`), inbound links with source URL
  and anchor text per page (`GetUrlLinks`). `LinkDetail` has only `AnchorText` and `Url`:
  no rel/nofollow, country or discovery date
  ([LinkDetail](https://learn.microsoft.com/en-us/dotnet/api/microsoft.bing.webmaster.api.interfaces.linkdetail?view=bing-webmaster-dotnet))
- **Script:** `scripts/bing_webmaster.py`
- **Commands:** `links`, `counts`, `compare`, `ai-performance` (offline export parser)
- **AI Performance (citations in Copilot, Bing AI summaries and select partner integrations):**
  UI-only, public preview since Feb 2026
  ([Bing blog](https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview));
  Intents, Topics, Citation Share and Compare added June 2026
  ([Bing blog](https://blogs.bing.com/search/June-2026/New-AI-Visibility-Insights-in-Bing-Webmaster-Tools-Intents-Topics-Citation-Share-Compare)).
  Not in the [Webmaster API method list](https://learn.microsoft.com/en-us/dotnet/api/microsoft.bing.webmaster.api.interfaces.iwebmasterapi?view=bing-webmaster-dotnet).
  Export CSV or Excel from the UI and parse with `ai-performance`. Per the
  [help page](https://www.bing.com/webmasters/help/ai-performance-9f8e7d6c), all AI Performance
  data is sampled, totals may differ across views, and exports reflect the active filter
  (never sum filtered exports as site totals). Not a backlink signal.
- **Blind spots:** Only Bing-indexed pages, verified sites only, no rel/nofollow or
  country data, no authority metrics, no spam scoring

### Common Crawl Web Graph (Always Available)
- **Data source:** `s3://commoncrawl/projects/hyperlinkgraph/`
- **Releases:** Quarterly (e.g., cc-main-2025-18)
- **No auth needed:** Public data, free to download
- **Data:** Domain-level in-degree, PageRank, harmonic centrality, referring domains
- **Script:** `scripts/commoncrawl_graph.py`
- **Cache:** `~/.cache/claude-seo/commoncrawl/` (90-day TTL)
- **Blind spots:** No anchor text, no page-level data, monthly/quarterly freshness,
  domain-level only (e.g., "nytimes.com links to example.com" but not which page)

### Verification Crawler (Always Available)
- **No auth needed:** Uses existing fetch_page.py + parse_html.py
- **Data:** Binary verification (link exists/lost/moved), anchor text, rel attributes
- **Script:** `scripts/verify_backlinks.py`
- **Input:** JSON file with `[{"source_url": "..."}]` entries
- **Polite crawling:** 1-second delay between requests to same domain
- **Best for:** Checking if known backlinks still exist, monitoring link health

## When to Recommend DataForSEO Upgrade

Suggest the paid DataForSEO extension when:
- User needs **toxic link detection** beyond Moz's basic Spam Score
- User needs **competitor gap analysis** at scale (Bing only compares verified sites)
- User needs **link velocity trends** (new/lost links over time)
- User needs **real-time data** (free sources update monthly at best)
- User manages **multiple client sites** (free tier limits are per-account)
- User needs **disavow file generation** with confidence scoring

## Data Quality Reality Check

- No primary source quantifies how much of a commercial backlink index free sources
  capture; do not quote coverage percentages as fact
- Free sources return samples; treat counts as lower bounds, not totals
- **Referring domain count matters more than raw backlink count** for SEO
- Top 50-100 referring domains capture the majority of link authority

## Five Systematic Biases in Free Data

1. **Popularity bias:** Free tools crawl popular sites more, underrepresenting niche sites
2. **Truncation bias:** All free tools cap at 100-1,000 links, hiding the long tail
3. **Own-site restriction:** GSC and Ahrefs Webmaster Tools only work for verified properties
4. **Missing quality metrics:** Raw CC data lacks authority/toxicity scores
5. **Freshness lag:** Free sources update monthly at best vs. minutes for commercial
