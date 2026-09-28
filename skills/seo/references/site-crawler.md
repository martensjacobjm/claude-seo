# Built-in Site Crawler (`scripts/site_crawl.py`)

Free, self-hosted replacement for the Firecrawl extension. No API key, no credits.
Runs on `requests` + `beautifulsoup4` (+ `lxml`); `--render` adds Playwright Chromium.
Use it whenever the Firecrawl MCP tools (`firecrawl_map`, `firecrawl_crawl`,
`firecrawl_scrape`) are not available. Use it only on sites you own or have
permission to audit, and keep crawls small on sites you do not control.

## Commands

```bash
# URL discovery (robots.txt Sitemap lines, /sitemap.xml, indexes, .xml.gz)
python scripts/site_crawl.py map https://example.com --json
python scripts/site_crawl.py map https://example.com --discover-links --max-pages 50 --json
python scripts/site_crawl.py map https://example.com --search blog --limit 500 --json

# Polite BFS crawl of one host + site report
python scripts/site_crawl.py crawl https://example.com --json
python scripts/site_crawl.py crawl https://example.com --max-pages 300 --max-depth 4 \
    --include '/blog/' --exclude '\?page=' --jsonl pages.jsonl --json
python scripts/site_crawl.py crawl https://example.com --check-external --external-budget 30 --json

# One page to clean markdown + SEO record (optionally JS-rendered)
python scripts/site_crawl.py scrape https://example.com/pricing --json
python scripts/site_crawl.py scrape https://app.example.com/ --render --markdown-out page.md
```

Global flags (all subcommands): `--timeout` (s, default 20), `--user-agent`,
`--render`, `--json`, `--output FILE` (full JSON), `--max-bytes` (default 5 MB).

Crawl flags: `--max-pages` (100), `--max-depth` (3), `--delay` (1.0 s),
`--concurrency` (1, capped at 5), `--include`/`--exclude` (regex, repeatable),
`--sort-query`, `--trailing-slash keep|strip|add`, `--no-sitemap`,
`--check-external`, `--external-budget` (20), `--jsonl FILE`, `--include-pages`.

Exit codes: 0 ok, 1 missing dependency, 2 URL rejected or start URL failed.

## Mapping from former Firecrawl commands

| Firecrawl | Built-in | Notes |
|-----------|----------|-------|
| `firecrawl_map(url, search, limit)` | `map <url> --search --limit` | Sitemaps by default; `--discover-links` adds a link crawl |
| `firecrawl_crawl(url, limit, maxDepth, includePaths, excludePaths)` | `crawl <url> --max-pages --max-depth --include --exclude` | Regex, not glob: `/blog/*` becomes `--include '/blog/'` |
| `firecrawl_scrape(url, onlyMainContent, formats=[markdown])` | `scrape <url>` | Main content = `<main>`, `[role=main]`, `<article>`, else `<body>` |
| `firecrawl_scrape` with JS rendering | `scrape <url> --render` | Playwright Chromium |
| `firecrawl_search(query, url)` | none | Use `map --search` on URLs, or WebSearch with `site:` |
| `formats: ["screenshot"]` | `scripts/capture_screenshot.py` | |
| Anti-bot / proxy rotation | none (by design) | See Limits |

## Crawl output

`{"summary": ..., "report": ..., "pages": ...}` (`pages` only with
`--include-pages`; use `--jsonl` for large crawls).

**summary**: `start_url`, `scope_host`, `user_agent`, `robots_txt` (url, status,
mode, crawl_delay), `effective_delay_s`, `pages_fetched`, `crawl_complete`,
`urls_remaining_in_queue`, `urls_filtered_by_include_exclude`,
`external_links_unique`, `sitemap_files`, `sitemap_urls`, `sitemap_errors`,
`render_error`, `counts` (items per report key), and a `note` when the page
budget ran out.

**Per-page record** (also one line per page in `--jsonl`):

| Field | Meaning |
|-------|---------|
| `url`, `final_url`, `status` | Requested (normalized) URL, URL after redirects, final HTTP status |
| `redirect_chain`, `redirect_hops`, `redirect_loop` | Each hop as `{url, status, location}` |
| `content_type`, `response_time_ms`, `bytes`, `truncated` | Response facts (`truncated` = hit `--max-bytes`) |
| `depth`, `in_sitemap`, `error` | BFS depth (sitemap-only URLs use 0), sitemap membership, fetch error |
| `title`, `meta_description`, `h1_count`, `word_count` | From `parse_html.parse_html()` |
| `meta_robots`, `x_robots_tag`, `noindex` | `noindex` is true for `noindex` or `none` in either |
| `canonical`, `canonical_is_self` | Absolute canonical and whether it matches `final_url` |
| `hreflang` | `[{lang, href}]`, hrefs resolved |
| `internal_links`, `external_links`, `images_missing_alt`, `jsonld_types` | Counts and JSON-LD `@type`s (`@graph` flattened) |

**report** keys:

| Key | Finding |
|-----|---------|
| `broken_internal_links` | Internal URLs with 4xx/5xx or connection errors, with `linked_from` |
| `redirect_chains` | More than one hop, with every hop and the final status |
| `redirect_loops` | Redirect that returns to a URL already in the chain |
| `duplicate_titles`, `duplicate_descriptions` | Same value on 2+ HTML pages that returned 200 |
| `blocked_by_robots` | Discovered URLs disallowed for `claude-seo-crawler` (never fetched) |
| `noindex_pages` | Meta robots or X-Robots-Tag noindex/none |
| `orphan_candidates` | In a sitemap but not linked from any crawled page (entry URL excluded) |
| `non_canonical_in_sitemap` | Sitemap URLs whose canonical points elsewhere |
| `sitemap_url_issues` | Sitemap URLs that redirect, are non-200, noindex or non-canonical |
| `blocked_unsafe_urls` | URLs or redirect hops rejected by the SSRF validator |
| `offsite_redirects` | Internal URLs that redirect to another host (not followed) |
| `external_link_checks` | Only with `--check-external`: status per external URL |
| `pages_missing_title`, `pages_multiple_or_no_h1` | Quick on-page flags |

Orphan and broken-link findings are complete only when `crawl_complete` is
true. With a page budget, say so in the report ("based on N crawled pages").
Orphans are candidates: pages may be linked from JavaScript navigation (retry
with `--render`) or from pages outside `--include`.

## map output

`robots_txt` (with `sitemaps`), `sitemap_files` (url, source, status, kind,
count), `total_urls`, `patterns` (first path segment breakdown, e.g.
`/blog/*`), `urls` as `[{url, sources}]`. Sources: `sitemap:<file>`, `links`,
`links (robots-blocked, not fetched)`.

## scrape output

`record` (the per-page record above), `markdown`, `robots_allowed` (advisory:
a single user-requested page is fetched regardless, like a browser), and with
`--render`: `render_error`, `render_blocked_requests`.

## Politeness defaults

- User-Agent `claude-seo-crawler/<plugin version>` (read from
  `.claude-plugin/plugin.json`). `--user-agent` changes the header only;
  robots.txt is still evaluated for the `claude-seo-crawler` token.
- robots.txt per RFC 9309: 2xx parsed, 4xx = allow all, 5xx or unreachable =
  disallow all. `Crawl-delay` is honored when larger than `--delay`.
- 1 request at a time, 1.0 s apart; sitemap files are fetched with the same delay.
- Default budget 100 pages, depth 3. Sitemap-only URLs are crawled after the
  link frontier, so they never crowd out linked pages.
- External links are never crawled; `--check-external` sends HEAD (GET if 405)
  to at most `--external-budget` URLs.

## Safety

- Every URL is checked before it is requested: the start URL, each redirect
  hop (redirects are followed manually, max 10), each discovered URL, sitemap
  files, external checks and every request the Playwright page makes.
  Check = `validate_url()` from `google_auth.py` plus a DNS lookup that rejects
  private, loopback, link-local (169.254.169.254), reserved and multicast addresses.
- Only http/https. Response bodies are capped (`--max-bytes`; sitemaps 50 MB,
  gzip decompression capped too). Sitemaps declaring XML entities are refused.
- Crawl scope is the host the start URL finally resolves to (so `example.com`
  -> `www.example.com` works); redirects to other hosts are recorded, not followed.
- Tests inject a validator that allows exactly one local fixture origin; there
  is no environment-variable bypass.

## Limits

- No CAPTCHA solving, no anti-bot or WAF bypass, no proxy rotation, no login.
  A 403/429 or challenge page is a finding to report, not something to work around.
- Do not run large crawls against sites you do not own or have permission to
  audit. Keep competitor checks to `scrape` or a small `map`.
- No site search (Firecrawl `search`); no screenshots (use `capture_screenshot.py`).
- `--render` is slow (one Chromium page per URL) and needs
  `pip install playwright && playwright install chromium`; `PLAYWRIGHT_BROWSERS_PATH`
  is respected. Without it the crawl continues on raw HTML and reports `render_error`.
- DNS is checked before each request, but a hostile DNS server could still
  rebind between check and connect; do not point the crawler at untrusted
  internal networks.
- Near-duplicate content detection is not included (exact title/description only).
