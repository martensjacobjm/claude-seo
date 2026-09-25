# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Evidence pass (2026-09-24): every added claim cites a primary source (Google Search Central,
Bing, schema.org, Chrome for Developers, arXiv, court records). Unsourced statistics were removed.

Evidence pass (2026-09-25) on the E-E-A-T and local SEO references, `seo-local` and its agent. Each claim was checked against the Quality Rater Guidelines PDF (2025-09-11), Search Central, Google Business Profile Help, schema.org, Apple, eCFR/FTC and HHS; practitioner surveys were kept only where the survey itself was fetched.

### Added
- **Local and E-E-A-T evidence register**: `skills/seo/references/local-eeat-evidence.md` lists the sources (URL, date, claim) for `eeat-framework.md`, `local-schema-types.md`, `local-seo-signals.md`, `seo-local` and its agent, plus a "Removed claims" list. It is copied into the `hemsida` package (`build.py` CANONICAL_COPIES, tests, README). Sources: https://guidelines.raterhub.com/searchqualityevaluatorguidelines.pdf, https://support.google.com/business/answer/7091, https://developers.google.com/search/docs/appearance/structured-data/local-business, https://developers.google.com/search/docs/appearance/structured-data/review-snippet
- **CrUX on BigQuery**: `scripts/crux_bigquery.py`, which gives monthly origin-level Core Web Vitals from the public CrUX dataset (`metrics_summary` / `device_summary`) and a competitor benchmark (`--compare`, up to 10 origins, competition ranking with a `tied` flag). Origins go in as query parameters, and every origin is checked with `validate_url()`. Also adds `--dry-run`, `--print-sql`, a `--max-bytes-billed` cap and the optional `bigquery_project_id` config key. New commands: `/seo google crux-bq` and `/seo google crux-benchmark`. New reference: `skills/seo-google/references/crux-bigquery.md`. `requirements.txt` adds `google-cloud-bigquery>=3.40.0,<4.0.0`; per PyPI, 3.42+ requires Python >= 3.10. `auth-setup.md` gets a BigQuery section. Source: https://developer.chrome.com/docs/crux/guides/bigquery
- **Search Console Generative AI report**: `skills/seo-google/references/gsc-generative-ai-report.md` and `/seo google gen-ai-report`. The report shows impressions for AI Overviews and AI Mode by page, country, device and date. It has no query dimension or click metric, and the "Web: multimodal" filter was added 2026-09-24. It has to be exported by hand: the Search Analytics API `type` enum has no generative-AI value (API reference as of 2026-08-11). Sources: https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports (2026-06-03; all sites since 2026-08-31), https://support.google.com/webmasters/answer/16984139
- **Bing AI Performance export parser**: `python scripts/bing_webmaster.py ai-performance [<url>] --file <export>` and `/seo backlinks ai-performance`. It parses CSV and Excel exports offline (citations, cited pages, sampled grounding queries, trend, compare), and needs no API key and no network access. Bing has no API for this report. The export column names are not documented, so the parser matches headers loosely and reports any columns it does not recognise. Sources: https://blogs.bing.com/webmaster/February-2026/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview, https://blogs.bing.com/search/June-2026/New-AI-Visibility-Insights-in-Bing-Webmaster-Tools-Intents-Topics-Citation-Share-Compare, https://www.bing.com/webmasters/help/ai-performance-9f8e7d6c ("Exports are available in CSV and Excel formats"; "AI Performance data is sampled")
- **Ranking signals reference**: `skills/seo/references/ranking-signals.md` is an evidence-graded map from Google systems disclosed in *United States v. Google LLC* (liability opinion, Doc 1033; remedies opinion, Doc 1436; exhibits PXR0356 and PXR0171) to audit checks. It covers NavBoost, Glue, RankEmbed, DeepRank and the top-level quality and popularity signals, plus 2024 Content Warehouse API leak attributes (hexdocs v0.4.0). It is for context only: the leak shows that attributes exist, not their weights. seo-content, seo-technical, seo-page and seo-backlinks now point to it. Sources: https://storage.courtlistener.com/recap/gov.uscourts.dcd.223205/gov.uscourts.dcd.223205.1033.0.pdf, https://storage.courtlistener.com/recap/gov.uscourts.dcd.223205/gov.uscourts.dcd.223205.1436.0.pdf, https://hexdocs.pm/google_api_content_warehouse/0.4.0/api-reference.html, https://developers.google.com/search/docs/appearance/ranking-systems-guide
- **Worked examples and tests**: `skills/seo-geo/references/geo-examples.md` (robots.txt for search-yes/training-no, wrong vs right finding phrasing, Google's commodity vs non-commodity example, a sample GEO-ANALYSIS.md excerpt, a measurement readout). New `tests/` pytest suite (23 tests, stdlib only) with synthetic fixtures for the Bing AI Performance parser, CrUX BigQuery query planning and benchmark ranking, and the schema hook; CI now runs it.
- **GEO evidence register**: `skills/seo-geo/references/geo-evidence.md` defines the evidence levels ([V] vendor, [R] research, [H] heuristic) and lists the vendor and research sources. It also keeps a "Removed claims" list so unsourced statistics are not added back.
- **Schema**: the Recipe, QAPage, Quiz, MathSolver, EmployerAggregateRating, VacationRental and Movie rows; tables of recent Google changes and schema.org 29.4/30.0/30.1 additions; and a `ProductCategory` (`CategoryCode`) template. Sources: https://developers.google.com/search/docs/appearance/structured-data/search-gallery, https://schema.org/docs/releases.html

### Changed
- **eeat-framework.md** rewritten on the QRG edition of 2025-09-11 and Search Central: Trust is the most important member; E-E-A-T is not a ranking factor by itself; the four YMYL types (incl. Government, Civics & Society); generative AI judged by effort and added value (QRG 4.6.6); the three spam policies dated 2024-03-05 (site reputation now "Site reputation policy"). Weights and score bands marked as heuristics. Removed: the "December 2025 watershed" section and its 71%/67%/52% traffic drops, "E-E-A-T applies to ALL competitive queries", the "AI Overview Evaluation" and "raters evaluate AI-generated" claims, and the RSL backers list. 214 to 188 lines.
- **local-schema-types.md**: Google's LocalBusiness doc (last updated 2026-09-08) and schema.org. Self-serving `aggregateRating`/`review` markup is ineligible for star snippets and is no longer recommended; `image` removed from Google's recommended list; `branchOf` replaced by `parentOrganization`, `menu`/`hasMenu` and `serviceArea`/`areaServed` noted; `IndividualPhysician`, pending `RealEstateListing`, `VeterinaryCare` not a LocalBusiness. Vehicle listing corrected (a Google feature, phased out 2025-06-12, docs removed 2025-09-09; not a schema.org type). HIPAA note now cites the HHS Manasa settlement ($30,000, 2023-06-05). Removed: Webstix 43% CTR, Bruce Clay 50%, Sterling Sky service-area claim, Google Food Ordering date, and all directory traffic, DA, revenue and ownership figures. 230 to 198 lines.
- **local-seo-signals.md**: now leads with Google's own local ranking statements (relevance, distance, prominence; no paid ranking) and GBP name rules. Whitespark 2026 kept as a labeled practitioner survey with corrected scores (Primary GBP Category 227, not 193; Incorrect Primary Category is negative #2 at 214, not #1) and group weights read from the survey chart. BrightLocal LCRS 2026 kept as a labeled consumer survey (1,002 US adults) with only the figures found in the survey. Review policy and law: Google fake engagement policy, FTC guidance, 16 CFR 465 (effective 2024-10-21), $53,088 penalty (16 CFR 1.98; no 2026 adjustment per OMB M-26-11), Google review removals for 2024 and 2025. GBP changes and ranking update dates from GBP Help, the GBP API sunset page and the Search Status Dashboard. 218 to 174 lines.
- **seo-local** (SKILL.md and agent): evidence rules added ([V] only for Critical/High; surveys and heuristics labeled, Medium at most); Key Statistics replaced by Google-documented facts; survey figures labeled; aggregateRating check now reports self-serving markup as ineligible; review gating cites Google and FTC wording; doorway check cites Google's spam policy; missing NAP is Medium (heuristic), not Critical. Same fixes applied to the duplicates in `seo-maps/SKILL.md` and `maps-gbp-checklist.md` (18-day rule, `branchOf`, "optimal 4 categories", Diversity Update, Google Verified as a GBP badge).
- **hemsida** (claude.ai package): points to the new register; the two copied references are no longer described as unsourced.
- **seo-geo rewritten around Google's "Guide to Optimizing for Generative AI Features on Google Search"** (https://developers.google.com/search/docs/fundamentals/ai-optimization-guide, last updated 2026-07-10):
  - llms.txt is now an informational status check only, never scored or recommended. Google's changelog of 2026-06-15 says llms.txt files are not needed for Google Search.
  - Removed: the 134-167 word passage rule, advice to rewrite or chunk content for AI, the "citability" score and the unsourced statistics (Ahrefs correlations, 92%/47%, 527%, and similar).
  - New scoring: Crawler Access & Eligibility, Content Uniqueness, Structure & Semantic HTML, Rich Media, and Entity/Trust/Freshness. The weights are marked as heuristic.
  - New Measurement section covering the Search Console Generative AI report and Bing AI Performance.
  - Research caveats: the original GEO paper (arXiv 2311.09735, KDD 2024) measured its gains in a fixed context. The 2026 survey preprint (arXiv 2607.14035) finds citation-oriented rewrites can impair retrieval.
- **AI crawler tokens corrected against vendor docs** (seo-geo, seo-technical): OAI-SearchBot (ChatGPT search) vs GPTBot (training) vs ChatGPT-User; Claude-SearchBot and Claude-User vs ClaudeBot; PerplexityBot (search) vs Perplexity-User; Google-Extended; Applebot-Extended. The unsourced "~3-5%" robots.txt figure was replaced with HTTP Archive Web Almanac 2025 data (https://almanac.httparchive.org/en/2025/seo).
- **seo-content / seo-page**: "AI citation readiness" is now "AI search visibility" and follows Google's AI optimization guide. The 1-3% keyword density targets were removed; Google has no density target. seo-page and the seo-plan generic template no longer describe FAQPage as "gov/health only" (no site gets the FAQ rich result since 2026-05-07).
- **seo-local / seo-plan / seo-audit**: wording aligned with seo-geo, and unsourced local AI statistics and AI-visibility factor rankings removed (see the geo-evidence.md register). The GBP and Bing Places statements now use vendor wording.
- **seo-schema**: updated to schema.org 30.1 (2026-09-16) and Google's changelog (https://developers.google.com/search/updates):
  - FAQ rich result: no longer shown since 2026-05-07, and its docs were removed 2026-06-15. FAQPage is now Info priority only.
  - Practice problem docs removed 2026-01-06.
  - ClaimReview is phasing out; Fact Check Explorer still supports it.
  - Dataset is used by Dataset Search only.
  - VideoObject has `creator` and supported `interactionStatistic` types (2026-09-24).
  - Review snippet has a new guideline against fake or undisclosed incentivized reviews (2026-07-24).
  - WebSite markup is used for site names; the sitelinks search box was removed 2024-11-29.
  - `returnPolicyCountry`: Google's 2025-03-14 changelog called it required, but the current return-policy doc lists it as recommended (see the 1.1.0 entry below).
- **Leftover unsourced claims removed** outside the five skills: the YouTube "0.737" correlation (seo-dataforseo and its extension mirror, `youtube_search.py` docstring), "Powers ChatGPT, Copilot, Alexa. 900M queries/day" (local-seo-signals.md), FAQ "gov/health" status (pdf/google-seo-reference.md). CI now syntax-checks `crux_bigquery.py`, the backlink scripts and the schema hook; PRIVACY.md lists `crux_bigquery.py`.
- **Orchestrator** (`skills/seo/SKILL.md`): FAQ, llms.txt and HowTo/MathSolver quality-gate rules; the new reference files; the `crux-bq`, `crux-benchmark`, `gen-ai-report` and `ai-performance` routing; and the updated seo-geo subagent description.
- **cwv-thresholds.md**: pass rates replaced with the CrUX August 2026 and Web Almanac 2025 figures. Removed the unverified "December 2025 core update" line. The Lighthouse 13 note now says the 2025-10-10 release changed audits to Insights and made no scoring changes.
- **free-backlink-sources.md / seo-backlinks**: removed unsourced coverage figures ("~15% of web", "45.5T links") and the "only free competitor comparison" claim. Bing `compare` works only for sites verified in the user's account.

### Fixed
- **`bing_webmaster.py ai-performance`**: an unreadable or missing export file now returns a warning instead of raising `FileNotFoundError` when the parser is called as a library (found by the new tests).
- **`bing_webmaster.py`**: `links`, `counts` and `compare` called the undocumented `GetLinkDetails` method (HTTP 404).
  - They now use the documented `GetLinkCounts` and `GetUrlLinks`, with a new `--detail-pages` flag.
  - The output of `links` and `counts` has changed. `links` returns `target_pages` and `links[{source_url, target_url, anchor_text}]`; `date_discovered` was removed because the API does not provide it.
  - `compare` now returns status `error` with null gap fields when either lookup fails.
  - Source: https://learn.microsoft.com/en-us/dotnet/api/microsoft.bing.webmaster.api.interfaces.iwebmasterapi?view=bing-webmaster-dotnet
- **Schema hook**: `hooks.json` passed `$FILE_PATH`, which Claude Code never sets, so the hook did nothing in real sessions.
  - `validate-schema.py` now reads `tool_input.file_path` from the hook event on stdin and writes findings to stderr, so exit 2 reaches Claude. Exit 2 on PostToolUse cannot undo the edit (https://code.claude.com/docs/en/hooks).
  - It now detects nested and compact-IRI `@type` values and `@graph` members.
  - ClaimReview and FAQPage are warnings, not blocking.
  - HowTo in the same block as a MathSolver is a warning.
  - Placeholders are matched only as bracketed tokens, so "replacement battery" is no longer flagged.
  - `--json` always prints JSON.
- **Unsourced claims removed**:
  - the YouTube "0.737" AI-visibility correlation, from the seo-google skill only. It is still in seo-dataforseo and `scripts/youtube_search.py`.
  - the "December 2025 core update weighted mobile CWV" line.
  - the misattributed "December 2025 JS SEO guidance" note.
  - the "~2.5x more likely in AI answers" schema claim.

## [1.8.1] - 2026-04-06

### Added
- **Google Images SERP**: `/seo dataforseo serp-images <keyword>` command for competitive image search analysis
- **Image SERP Analysis**: `/seo images serp <keyword>` cross-skill command combining DataForSEO image results with on-page audit
- **Image File Optimization**: `/seo images optimize <path>` for WebP/AVIF conversion, IPTC/XMP metadata injection, responsive variants, and compression
- **Image ranking factors table**: documents what matters (alt text, filename, page context) vs what does not (EXIF camera data, IPTC keywords)
- **DataForSEO field-config**: `serp.items.images` filter with 10 SEO-relevant fields (type, rank, title, alt, url, source_url, image_url, domain, encoded_url)
- **Tool catalog reference**: `skills/seo-dataforseo/references/tool-catalog.md` for 35+ utility MCP tools (moved from inline list)
- **Table of Contents**: added to `seo-image-gen/references/prompt-engineering.md` (326 lines, per >300 line standard)
- Plugin keywords: `image-serp`, `google-images` added to plugin.json

### Fixed
- **Version mismatch**: unified all 19 SKILL.md files, plugin.json, and CLAUDE.md to v1.8.0 (was 1.7.0/1.7.2/1.8.0 three-way split)
- **Broken reference path**: seo-backlinks now correctly points to `skills/seo/references/backlink-quality.md` (shared reference)
- **Hardcoded absolute paths**: removed `~/.claude/skills/` from `agents/seo-visual.md`, `agents/seo-schema.md`, `skills/seo-image-gen/SKILL.md`, and banana extension copy (now use plugin-relative paths)
- **seo-dataforseo line count**: moved 35-line utility tools list to reference file, reduced from 416 to 380 lines

### Changed
- seo-images description: added trigger phrases for image SERP, metadata, WebP conversion
- seo-dataforseo description: added "Google Images" and image ranking trigger phrases
- seo orchestrator: updated images command to reflect new SERP + optimize capabilities
- CLAUDE.md: updated plugin version reference, images command description

## [1.7.2] - 2026-03-30

### Added
- **Firecrawl extension**: Full-site crawling, scraping, and site mapping via Firecrawl MCP (`extensions/firecrawl/`)
  - 4 commands: crawl, map, scrape, search
  - JS rendering support for SPA/CSR sites (addresses #11)
  - Cross-skill integration with audit, technical, sitemap, and content skills
  - Self-contained install/uninstall scripts (Bash + PowerShell)
- **Backlink analysis skill**: `skills/seo-backlinks/SKILL.md` with `/seo backlinks` command
  - 7-section analysis: profile overview, anchor text, referring domain quality, toxic links, top pages, competitor gap, new/lost links
  - Backlink health score (0-100) with weighted factors
  - Disavow recommendations with export format
  - Requires DataForSEO extension for live data
- **Backlink quality reference**: `skills/seo/references/backlink-quality.md` with 30 toxic link patterns, anchor text benchmarks by industry
- **Excel export**: `--format xlsx` option in `scripts/google_report.py`
  - Sheets: Summary, Queries, Pages, Indexation (conditional on data available)
  - Navy header styling matching PDF palette, auto-column-width, frozen headers, auto-filter
  - New format options: `xlsx`, `all` (pdf+html+xlsx)
- **Ecosystem cross-links**: AI Marketing Claude added to README and CLAUDE.md ecosystem sections

### Changed
- Sub-skill count: 18 -> 19 (added seo-backlinks)
- Extension count: 2 -> 3 (added Firecrawl)
- Orchestrator routing table updated with `/seo backlinks` and `/seo firecrawl` commands
- Audit orchestration: Firecrawl `map` used for URL discovery when available
- `requirements.txt`: added `openpyxl>=3.1.0` for Excel export

## [1.7.1] - 2026-03-30

### Fixed
- install.sh: broken skill copy path `seo/` corrected to `skills/seo/` (h/t @hieu-e via #39)
- install.sh: version tag pinned to v1.7.1 (was stuck at v1.6.0)
- install.ps1: version tag pinned to v1.7.1 (was stuck at v1.6.0)
- install.ps1: removed unnecessary `seo/` fallback path, uses `skills\seo` directly

### Changed
- CI: syntax check expanded from 4 to 15 Python scripts (all v1.7.0 Google API scripts now covered)

## [1.7.0] - 2026-03-28

### Added
- **Google SEO APIs skill**: `skills/seo-google/SKILL.md` with 21 commands across 4 credential tiers
- **Google subagent**: `agents/seo-google.md` for enriched audit data (CWV field data, indexation status, organic traffic)
- **11 Python scripts**: google_auth.py, gsc_query.py, gsc_inspect.py, pagespeed_check.py, crux_history.py, indexing_notify.py, ga4_report.py, google_report.py, youtube_search.py, nlp_analyze.py, keyword_planner.py
- **10 reference files**: auth-setup.md, search-console-api.md, pagespeed-crux-api.md, indexing-api.md, ga4-data-api.md, youtube-api.md, nlp-api.md, keyword-planner-api.md, supplementary-apis.md, rate-limits-quotas.md
- **PDF report generator**: `scripts/google_report.py` with enterprise A4 template, WeasyPrint + matplotlib charts, post-generation quality review
- **OAuth web credential flow**: Browser-based auth with localhost:8085 callback, token refresh, manual code exchange fallback
- **4-tier credential system**: Tier 0 (API key: PSI/CrUX), Tier 1 (+OAuth/SA: GSC/Indexing), Tier 2 (+GA4), Tier 3 (+Ads Keyword Planner)
- **Python dependencies**: google-api-python-client, google-auth, google-auth-oauthlib, google-auth-httplib2, google-analytics-data, matplotlib, weasyprint

### Security
- SSRF protection: `validate_url()` blocks private IPs, loopback, and GCP metadata endpoints in all Google API scripts
- `.gitignore` hardened with 8 credential patterns: `.env`, `client_secret*.json`, `oauth-token.json`, `service_account*.json`
- OAuth tokens no longer store `client_secret` (reads from client_secret.json file only)
- Removed hardcoded user paths from all scripts (mobile_analysis.py, capture scripts)

### Changed
- Sub-skill count: 14 -> 15 core (+ 2 extensions)
- Subagent count: 9 -> 10 core (+ 2 extension) with conditional Google API spawning
- seo-audit spawns seo-google agent when Google API credentials detected
- seo-technical and seo-performance can use CrUX field data when available
- Report Generation Rules added to CLAUDE.md with color palette, dependency, and cross-skill enforcement
- README updated with Google APIs, local SEO, maps, and PDF report features

---

## [1.6.1] - 2026-03-27

### Added
- **Marketplace distribution**: Created `.claude-plugin/marketplace.json` for plugin marketplace submission. Users can now install via `/plugin marketplace add AgriciDaniel/claude-seo`
- **Agent model and turn limits**: All 11 subagents now specify `model: sonnet` and `maxTurns` (15-25) for predictable cost and behavior
- **Plugin keywords**: Added 12 discovery keywords to `plugin.json` for marketplace searchability

### Changed
- **Standard directory structure**: Moved `seo/` orchestrator to `skills/seo/` for auto-discovery compliance. Extension skills (seo-dataforseo, seo-image-gen) and agents copied to standard `skills/` and `agents/` directories
- **plugin.json rewrite**: Removed non-standard `entry_point` field and individual file-path arrays for `skills`/`agents`. All 17 skills and 11 agents now rely on directory auto-discovery per Anthropic plugin spec
- **allowed-tools format**: Converted from YAML arrays to comma-separated strings across all 17 SKILL.md files
- **Metadata standardized**: Added `license: MIT` and `metadata:` block (author, version, category) to all SKILL.md frontmatters
- **Cross-references**: Updated all agent and skill files referencing `seo/references/` to `skills/seo/references/`
- **CLAUDE.md**: Architecture tree updated to reflect new structure

### Fixed
- **Plugin validation**: `claude plugin validate .` now passes cleanly (previously would fail on non-standard fields)

---

## [1.6.0] - 2026-03-23

### Added
- **Local SEO skill**: `skills/seo-local/SKILL.md` for GBP, NAP, citations, reviews, and map pack analysis
- **Maps intelligence skill**: `skills/seo-maps/SKILL.md` for geo-grid rank tracking, GBP auditing, review intelligence, competitor radius mapping
- **Maps subagent**: `agents/seo-maps.md` for parallel maps analysis during audits
- **Local subagent**: `agents/seo-local.md` for parallel local SEO analysis
- **Maps reference files**: 4 new reference files (maps-geo-grid.md, maps-gbp-checklist.md, maps-api-endpoints.md, maps-free-apis.md)
- **Local reference files**: 2 new reference files (local-seo-signals.md, local-schema-types.md)
- **Installer fixes**: Cross-platform install script improvements

### Changed
- Subagent count: 7 -> 9 core (+ 2 extension) with conditional local/maps spawning
- Sub-skill count: 12 -> 14 core (+ 2 extension)

---

## [1.5.0] - 2026-03-19

### Added
- **Frontmatter fields**: `user-invokable`, `argument-hint`, and `allowed-tools` added to all SKILL.md files per Anthropic best practices
- **Error handling sections**: Added to all SKILL.md files with skill-specific guidance
- **Plugin manifest**: `.claude-plugin/plugin.json` updated with all skills and agents registered
- **Version tracking**: `pyproject.toml` with project metadata

### Fixed
- **Em dash elimination**: Replaced em dashes (U+2014) across files with appropriate punctuation (colons, commas, semicolons, periods) to reduce AI detection signals
- **HTML comments before frontmatter**: Removed `<!-- Updated: ... -->` comments from SKILL.md files that preceded the YAML frontmatter delimiter
- **Anthropic compliance audit**: Full audit against official skill-building guidelines, all checks now pass

### Changed
- **Technical SEO**: Updated from "8 categories" to "9 categories" in description (IndexNow added in prior update)

---

## [1.4.0] - 2026-03-12

### Security
- **Install script supply chain fix**: Replaced `irm | iex` Windows PowerShell one-liner with `git clone + powershell -File` as primary install method. Claude Code's own security guardrails flagged the old pattern as a supply chain risk (reported by community member). Added collapsible "review before running" section for Unix curl method.
- **Version pinning**: `install.sh` and `install.ps1` now clone a specific release tag (`v1.3.0`) by default rather than `main`, preventing silent updates. Override with `CLAUDE_SEO_TAG=main`.
- **PowerShell Invoke-External hardening**: Comprehensive `PSNativeCommandUseErrorActionPreference` handling in `Invoke-External` wrapper (fixes Windows git clone stderr false-positive termination, from PR #13 + PR #15).

### Added
- **GEO agent deployed**: `agents/seo-geo.md` created -- `/seo audit` now spawns 7 parallel agents (was 6). GEO analysis covers AI crawler access, llms.txt, passage-level citability, brand mention signals, platform-specific scoring (Google AI Overviews, ChatGPT, Perplexity, Bing Copilot).
- **`--googlebot` flag in `fetch_page.py`**: Detect prerender/dynamic rendering services by comparing response size with default UA vs Googlebot UA. First phase of SPA/CSR support (Issue #11).

### Fixed
- **URL normalization**: `capture_screenshot.py` and `analyze_visual.py` now accept bare domains (`example.com` -> `https://example.com`) via shared `normalize_url()` helper (from PR #16 by @shuofengzhang).
- **GEO weight**: AI Search Readiness weight increased from 5% to 10% in overall SEO Health Score. Technical SEO adjusted to 22%, Content Quality to 23%.
- **FAQPage guidance**: Blanket "remove FAQPage on commercial sites" updated to nuanced guidance -- existing FAQPage -> Info priority (not Critical), noting AI/LLM citation benefit. Adding new FAQPage -> not recommended for Google, note AI benefit. Updated in `seo/SKILL.md`, `agents/seo-schema.md`, `seo/references/schema-types.md`.
- **Uninstall agents list**: Added `seo-geo` to `uninstall.sh` and `uninstall.ps1` removal lists.
- **Python requirement**: Corrected from `3.8+` to `3.10+` in `README.md` and `docs/INSTALLATION.md`.

### Changed
- Subagent count: 6 -> 7 (added seo-geo to core audit pipeline)
- `.gitignore`: Added generated audit artifacts (charts/, PDFs, report.html, firebase-debug.log, generated-schema.json)

---

## [1.3.0] - 2026-03-06

### Added
- **Extension system**: `extensions/` directory convention for self-contained add-ons with install/uninstall scripts
- **DataForSEO extension**: 22 commands across 9 API modules (SERP, keywords, backlinks, on-page, content, business listings, AI visibility, LLM mentions). Install: `./extensions/dataforseo/install.sh`
- **DataForSEO integration**: seo-audit, seo-content, seo-geo, seo-page, seo-plan, seo-technical auto-detect DataForSEO MCP tools for enriched analysis
- **Plugin manifest**: `.claude-plugin/plugin.json` for official plugin directory submission
- **Documentation**: Extensions architecture in ARCHITECTURE.md, 22 new commands in COMMANDS.md, updated MCP integration guide

### Fixed
- **Title tag threshold**: Pre-commit hook now uses 60-char max, aligned with quality-gates.md and echo message
- **SSRF prevention**: Added to `capture_screenshot.py` (defense-in-depth, matching `fetch_page.py`)
- **Frontmatter cleanup**: Removed non-standard `allowed-tools` from main SKILL.md

### Changed
- Sub-skill count: 12 + 1 extension (added seo-dataforseo via DataForSEO extension)
- Subagent count: 6 + 1 optional (added seo-dataforseo agent via extension)
- DataForSEO promoted from "Community" to "Official extension" in MCP docs

---

## [1.2.1] - 2026-02-28

### Fixed
- **User-Agent header**: Changed default from bot-style `ClaudeSEO/1.0` to Chrome-like string with `ClaudeSEO/1.2` suffix. SSR frameworks (Next.js, Nuxt, Angular) now pre-render properly instead of serving empty client-side shells (#9)
- **Custom User-Agent support**: Added `--user-agent` flag to `fetch_page.py` for configurable UA strings

### Added
- **install.cat support**: Added alternative install method via `curl install.cat/AgriciDaniel/claude-seo | bash` to README (#10)

---

## [1.2.0] - 2026-02-19

### Security
- **SSRF prevention**: Added private IP blocking to `fetch_page.py` and `analyze_visual.py`
- **Path traversal prevention**: Added output path sanitization to `capture_screenshot.py` and file validation to `parse_html.py`
- **Install hardening**: Removed `--break-system-packages`, switched to venv-based pip install
- **requirements.txt**: Now persisted to `~/.claude/skills/seo/` for user retry

### Fixed
- **YAML frontmatter parsing**: Removed HTML comments before `---` delimiter in 8 files (skills: seo-content, seo-images, seo-programmatic, seo-schema, seo-technical; agents: seo-content, seo-performance, seo-technical). Thanks @kylewhirl for identifying this in the codex-seo fork.
- **Windows installer**: Merged @kfrancis improvements -- `python -m pip`, `py -3` launcher fallback, requirements.txt persistence, non-fatal subagent copy, better error diagnostics (PR #6)
- **requirements.txt missing after install**: Now copied to skill directory so users can retry (#1)

### Changed
- Python dependencies now installed in a venv at `~/.claude/skills/seo/.venv/` with `--user` fallback (#2)
- Playwright marked as explicitly optional in install output
- Windows installer uses `Resolve-Python` helper for robust Python detection (#5)

---

## [1.1.0] - 2026-02-07

### Security (CRITICAL)
- **urllib3 >=2.6.3**: Fixes CVE-2026-21441 (CVSS 8.9) - decompression bypass vulnerability
- **lxml >=6.0.2**: Updated from 5.3.2 for additional libxml2 security patches
- **Pillow >=12.1.0**: Fixes CVE-2025-48379
- **playwright >=1.55.1**: Fixes CVE-2025-59288 (macOS)
- **requests >=2.32.4**: Fixes CVE-2024-47081, CVE-2024-35195

### Added
- **GEO (Generative Engine Optimization) major enhancement**:
  - Brand mention analysis (3x more important than backlinks for AI visibility)
  - AI crawler detection (GPTBot, OAI-SearchBot, ClaudeBot, PerplexityBot, etc.)
  - llms.txt standard detection and recommendations
  - RSL 1.0 (Really Simple Licensing) detection
  - Passage-level citability scoring (optimal 134-167 words)
  - Platform-specific optimization (Google AI Overviews vs ChatGPT vs Perplexity)
  - Server-side rendering checks for AI crawler accessibility
- **LCP Subparts analysis**: TTFB, resource load delay, resource load time, render delay
- **Soft Navigations API detection** for SPA CWV measurement limitations
- **Schema.org v29.4 additions**: ConferenceEvent, PerformingArtsEvent, LoyaltyProgram
- **E-commerce schema updates**: returnPolicyCountry now required, organization-level policies

### Changed
- **E-E-A-T framework**: Updated for December 2025 core update - now applies to ALL competitive queries, not just YMYL
- **SKILL.md description**: Expanded to leverage new 1024-character limit
- **Schema deprecations expanded**: Added ClaimReview, VehicleListing (June 2025)
- **WebApplication schema**: Added as correct type for browser-based SaaS (vs SoftwareApplication)

### Fixed
- Schema-types.md now correctly distinguishes SoftwareApplication (apps) vs WebApplication (SaaS)

---

## [1.0.0] - 2026-02-07

### Added
- Initial release of Claude SEO
- 9 specialized skills: audit, page, sitemap, schema, images, technical, content, geo, plan
- 6 subagents for parallel analysis: seo-technical, seo-content, seo-schema, seo-sitemap, seo-performance, seo-visual
- Industry templates: SaaS, local service, e-commerce, publisher, agency, generic
- Schema library with deprecation tracking:
  - HowTo schema marked deprecated (September 2023)
  - FAQ schema restricted to government/healthcare sites only (August 2023)
  - SpecialAnnouncement schema marked deprecated (July 31, 2025)
- AI Overviews / GEO optimization skill (seo-geo) - new for 2026
- Core Web Vitals analysis using current metrics:
  - LCP (Largest Contentful Paint): <2.5s
  - INP (Interaction to Next Paint): <200ms - replaced FID on March 12, 2024
  - CLS (Cumulative Layout Shift): <0.1
- E-E-A-T framework updated to September 2025 Quality Rater Guidelines
- Quality gates for thin content and doorway page prevention:
  - Warning at 30+ location pages
  - Hard stop at 50+ location pages
- Pre-commit and post-edit automation hooks
- One-command install and uninstall scripts (Unix and Windows)
- Bounded Python dependency pinning with CVE-aware minimums (lxml >= 5.3.2)

### Architecture
- Follows Anthropic's official Claude Code skill specification (February 2026)
- Standard directory layout: `scripts/`, `references/`, `assets/`
- Valid hook matchers (tool name only, no argument patterns)
- Correct subagent frontmatter fields (name, description, tools)
- CLI command is `claude` (not `claude-code`)
