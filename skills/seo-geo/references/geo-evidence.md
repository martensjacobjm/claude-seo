<!-- Updated: 2026-09-24 -->
# GEO Evidence Register

Every factual claim in `skills/seo-geo/SKILL.md` and `agents/seo-geo.md` must
trace to an entry here. Add a source only after fetching the primary document.

## 1. Evidence Levels

| Tag | Level | Examples |
|-----|-------|----------|
| [V] | Vendor-documented | Google Search Central, Search Console Help, Bing Webmaster blog, OpenAI/Anthropic/Perplexity/Apple crawler docs |
| [R-peer] | Peer-reviewed research | Aggarwal et al., GEO, KDD 2024 |
| [R-preprint] | Preprint, not peer-reviewed | Martinez, GEO critical survey, arXiv 2607.14035 |
| [H] | Practitioner heuristic | Scoring weights, SSR hedge, sameAs consistency, off-site presence |

SKILL.md and the agent use [R] as an umbrella for [R-peer] and [R-preprint].
Vendor suffixes such as [V Google] or [V Bing] only name the vendor and map to [V].
Only [V] findings may be rated Critical or High. [R] and [H] findings are
labeled as such in the output. Blog posts are used only to locate primary sources.

## 2. Vendor-Documented Sources [V]

### Google

| Source | Date | Claim used |
|--------|------|------------|
| [Guide to Optimizing for Generative AI Features](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide) | Last updated 2026-07-10 | AI features rooted in core ranking/quality systems (RAG, query fan-out); "still SEO"; llms.txt not used by Google Search (neither helps nor harms); no chunking requirement, "no ideal page length"; no need to rewrite for AI; fan-out page creation to manipulate AI = scaled content abuse; inauthentic mentions not helpful; no special schema; semantic HTML a good idea but not required; JS processed if not blocked; images/video; Merchant Center + GBP; eligibility = indexed + snippet-eligible + Search Console control; non-commodity content ("7 Tips for First-Time Homebuyers" vs "Why We Waived the Inspection..."); no third-party tool has access to internal systems |
| [AI features and your website](https://developers.google.com/search/docs/appearance/ai-features) | Last updated 2025-12-10 | AI Overviews / AI Mode counted in Performance report, Web search type; Googlebot robots.txt is the control; nosnippet / data-nosnippet / max-snippet / noindex limit display |
| [Search generative AI control (Help 16908024)](https://support.google.com/webmasters/answer/16908024) | Rolled out to all sites 2026-08-31 | Settings > Search generative AI; include/exclude from AI Overviews, AI Mode, Discover gen-AI; default Include; separate from Google-Extended |
| [Gen AI performance reports (blog)](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports) | 2026-06-03; all sites 2026-08-31 | Impressions; Pages, Countries, Devices, Dates (no query dimension or click metric documented) |
| [Gen AI performance report (Help 16984139)](https://support.google.com/webmasters/answer/16984139) | Fetched 2026-09 | AI Overviews + AI Mode; excludes Search Labs; Search type filter "Web: text-based" / "Web: multimodal"; 1,000-row limit; export button; PT dates |
| [Search Analytics API: query](https://developers.google.com/webmaster-tools/v1/searchanalytics/query) | Last updated 2026-08-11 | `type` enum: discover, googleNews, news, image, video, web (no generative-AI type). Inference from absence |
| [Search Central changelog](https://developers.google.com/search/updates) | 2026 | 2026-06-15 llms.txt clarification; FAQ rich result no longer shown from 2026-05-07 |
| [Google common crawlers](https://developers.google.com/crawling/docs/crawlers-fetchers/google-common-crawlers) | Last updated 2026-07-14 | Google-Extended: control token only, no own UA; no impact on Search inclusion or ranking |
| [Google I/O 2026 keynote](https://blog.google/innovation-and-ai/sundar-pichai-io-2026/) | 2026 | AI Overviews 2.5B+ monthly active users; AI Mode 1B+ monthly active users |

### Other AI search vendors

| Source | Claim used |
|--------|------------|
| [OpenAI crawlers](https://developers.openai.com/api/docs/bots) | OAI-SearchBot = ChatGPT search inclusion; GPTBot = training only; ChatGPT-User = user-initiated, robots.txt "may not apply", not used for search inclusion; settings independent; ~24h to take effect |
| [Anthropic crawlers](https://support.claude.com/en/articles/8896518-does-anthropic-crawl-data-from-the-web-and-how-can-site-owners-block-the-crawler) | ClaudeBot = training; Claude-User = user-initiated; Claude-SearchBot = search indexing; robots.txt honored. `anthropic-ai` not listed |
| [Perplexity crawlers](https://docs.perplexity.ai/docs/resources/perplexity-crawlers) | PerplexityBot = search results, not model training; Perplexity-User "generally ignores robots.txt" |
| [Apple Applebot (119829)](https://support.apple.com/en-us/119829) | Applebot = Spotlight/Siri/Safari; Applebot-Extended = training opt-out; nosnippet opts out of world-knowledge answers; follows Googlebot rules if not named; may render JS |
| [Common Crawl CCBot](https://commoncrawl.org/ccbot) | UA `CCBot/2.0`; block with `User-agent: CCBot` |

### Microsoft Bing

| Source | Date | Claim used |
|--------|------|------------|
| [Bing Chat content controls](https://blogs.bing.com/webmaster/september-2023/Announcing-new-options-for-webmasters-to-control-usage-of-their-content-in-Bing-Chat) | 2023-09-22 | NOCACHE: URL/snippet/title only; NOARCHIVE: excluded from answers; both present = treated as NOCACHE; same tags govern training of Microsoft generative AI foundation models; `bingbot` meta name. Post names Bing Chat only; application to Copilot is an inference |
| [AI Performance in Bing Webmaster Tools](https://blogs.bing.com/webmaster/2026/2/Introducing-AI-Performance-in-Bing-Webmaster-Tools-Public-Preview/) | 2026-02 (preview) | Total Citations, Average Cited Pages, Grounding queries (sample), page-level citations, trends; Copilot, Bing AI summaries, partners; headings/tables/FAQ sections; examples, data, cited sources; consistent entities across formats; IndexNow; Bing Places keeps details "current and eligible for inclusion in AI-generated responses" (2026-02-10; names no ChatGPT or Alexa) |
| [New AI visibility insights](https://blogs.bing.com/search/2026/6/New-AI-Visibility-Insights-in-Bing-Webmaster-Tools-Intents-Topics-Citation-Share-Compare/) | 2026-06-16 (preview) | Intents, Topics, Citation Share (share of citations per grounding query; not traffic or quality), Compare |

### Chrome / standards

| Source | Claim used |
|--------|------------|
| [Lighthouse llms.txt audit](https://developer.chrome.com/docs/lighthouse/agentic-browsing/llms-txt) (2026-05-05) | Experimental Agentic Browsing category; 404 = N/A (file optional); server error flagged; unscored; Chrome 150+ |
| [llmstxt.org](https://llmstxt.org/) | A proposal (Jeremy Howard, published 2024-09-03, modified 2026-08-10), not a ratified standard |
| [RSL 1.0](https://rslstandard.org/rsl) | Recommendation published 2025-12-10; robots.txt `License:` directive, HTTP Link header or HTML link |

Not confirmed: that any non-Google engine reads llms.txt for crawling, ranking
or citation. OpenAI and Perplexity crawler pages only link their own docs'
llms.txt; Anthropic's crawler page does not mention it.

## 3. Research [R]

- **Aggarwal et al., "GEO: Generative Engine Optimization"**, KDD 2024,
  [arXiv 2311.09735](https://arxiv.org/abs/2311.09735) [R-peer]. Up to 40%
  visibility gain on GEO-bench; best methods Cite Sources, Quotation Addition,
  Statistics Addition; keyword stuffing little or no improvement. Caveat:
  measured with the source already in a fixed context.
- **Martinez, GEO critical survey 2023-2026**,
  [arXiv 2607.14035](https://arxiv.org/abs/2607.14035) [R-preprint, single
  author, 45 studies]. Original gains "conditional on a source already being
  present in a fixed context"; "topical relevance and context position are the
  most reproducible levers"; "citation-oriented rewrites can impair retrieval";
  "no reviewed technique shows a stable, longitudinal, cross-platform causal
  effect on organic discoverability".

## 4. Ecosystem Measurement

- **HTTP Archive Web Almanac 2025, SEO chapter**
  ([link](https://almanac.httparchive.org/en/2025/seo)): llms.txt on 2.13% of
  desktop / 2.10% of mobile sites. Tokens named in robots.txt (desktop):
  GPTBot 4.5%, ClaudeBot 3.6%, Google-Extended 3.4%, PerplexityBot 2.8%.

## 5. Removed Claims (no primary source found, 2026-09-24)

Do not re-introduce these without a fetched primary source:
(Local SEO and E-E-A-T removals are listed in `skills/seo/references/local-eeat-evidence.md`.)


- "Optimal passage length: 134-167 words" (contradicted by Google: no ideal length, no chunking requirement)
- "Direct answer in first 40-60 words" / "definition in first 60 words" / "X is..." patterns / question-based headings
- "92% of AI Overview citations come from top-10 pages" / "47% below position 5"
- "156% higher selection rates" for multi-modal content
- Ahrefs brand-mention correlations (YouTube ~0.737, Domain Rating ~0.266, "3x more strongly")
- "Only 11% of domains cited by both ChatGPT and AI Overviews"
- "527% AI-referred sessions growth" (SparkToro); "50%+ of all queries"; "1.5 billion users/month" (outdated)
- "ChatGPT 900 million WAU"; "Perplexity 500+ million monthly queries"
- Citation shares "Wikipedia 47.9%", "Reddit 11.3%", "Reddit 46.7%"
- "AI crawlers do NOT execute JavaScript" (blanket claim; Google processes JS, Applebot may render)
- `anthropic-ai` as a current Anthropic token; `Bytespider`, `cohere-ai` purposes (unverified)
- "Allow GPTBot for AI search visibility" (GPTBot is training-only)
- RSL "Backed by Reddit, Yahoo, Medium, Quora, Cloudflare, Akamai, Creative Commons" (partially unverified)
- llms.txt as an "emerging standard" to implement
- Local: "Bing Places powers ChatGPT, Copilot, Alexa"; "ChatGPT sources local data from Yelp/TripAdvisor/BBB/Reddit"; BrightLocal "45% use ChatGPT/AI for local"; Seer "15.9% vs 1.76%" conversion; Whitespark "AI visibility factor" rankings; BuzzStream "66.2% of PR practitioners"

## 6. Heuristics Used and Why [H]

| Heuristic | Rationale |
|-----------|-----------|
| Scoring weights 25/25/15/10/25 | Editorial prioritization; access and content uniqueness are the areas with the most vendor guidance |
| Critical content in initial HTML | Google processes JS, but OpenAI, Anthropic and Perplexity do not document rendering |
| Organization/Person `sameAs` consistency | Supports Bing's "reduce ambiguity" guidance; no vendor documents it as an AI factor |
| Wikipedia / Reddit / YouTube presence | Reported only; no verified correlation data |
| Visible authorship and dates | Trust and freshness proxies; not documented as AI-selection signals |
