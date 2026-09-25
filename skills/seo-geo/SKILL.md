---
name: seo-geo
description: >
  Optimize for Google AI Overviews / AI Mode, ChatGPT search, Perplexity,
  Bing Copilot and other AI search experiences. Evidence-based Generative
  Engine Optimization (GEO): AI crawler access (robots.txt tokens),
  indexability and snippet eligibility, non-commodity content, semantic
  structure, rich media, entity/brand clarity, Merchant Center/GBP, and
  measurement via Search Console Generative AI and Bing AI Performance
  reports. Use when user says "AI Overviews", "AI Mode", "GEO", "AEO",
  "AI search", "LLM optimization", "Perplexity", "AI citations",
  "ChatGPT search", or "AI visibility".
user-invokable: true
argument-hint: "[url]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "1.8.1"
  category: seo
---
<!-- Updated: 2026-09-24 -->

# AI Search / GEO Optimization (September 2026)

## Core Principle

Google's generative AI features (AI Overviews, AI Mode) are "rooted in our core
Search ranking and quality systems": they ground answers on retrieved pages
(retrieval-augmented generation) and issue related sub-queries (query fan-out).
Google states: "optimizing for generative AI search is optimizing for the search
experience, and thus still SEO." Other engines (ChatGPT search, Perplexity,
Claude, Copilot) likewise depend on their own crawlers or on a search index
(Bing) being able to reach and index the page.

Scale (Google I/O 2026): AI Overviews 2.5B+ monthly active users; AI Mode 1B+
monthly users. No other usage or citation-share statistics are used in this
skill. Sources for every claim: `references/geo-evidence.md`.

## Evidence Levels

Every check and recommendation carries a tag:

| Tag | Meaning |
|-----|---------|
| **[V]** | Vendor-documented (Google, Bing, OpenAI, Anthropic, Perplexity, Apple docs) |
| **[R]** | Research; umbrella for the register's [R-peer] (GEO paper, KDD 2024) and [R-preprint] (2026 GEO survey, labeled "preprint") |
| **[H]** | Practitioner heuristic, including this skill's scoring weights |

Suffixes such as [V Google] or [V Bing] only name the vendor; they map to [V]
in `references/geo-evidence.md`. [V Bing / H] means partly vendor-documented,
partly heuristic.

Rules: a finding may be rated **Critical** or **High** only when backed by [V].
[H] items are labeled "heuristic" in the output. Never cite a statistic that is
not in `references/geo-evidence.md`.

## What NOT to Recommend

Per Google's "Guide to Optimizing for Generative AI Features" (last updated
2026-07-10) [V], these do not help in Google Search:

- Creating `llms.txt` or other AI text / Markdown files ("Google Search itself doesn't use them")
- "Chunking" content or targeting a fixed passage or page length ("There's no ideal page length")
- Rewriting content just for AI systems ("You don't need to write in a specific way just for generative AI search")
- Creating pages for every fan-out query variant to manipulate AI responses (violates the scaled content abuse spam policy)
- Seeking inauthentic "mentions" across the web
- Adding "special" schema for AI ("there's no special schema.org markup you need to add"); structured data remains useful for rich-result eligibility

Research note [R]: the original GEO paper (Aggarwal et al., KDD 2024) reported
visibility gains of up to 40% from methods such as Cite Sources, Quotation
Addition and Statistics Addition, but measured with the source already inside a
fixed context. A 2026 critical survey (preprint, arXiv 2607.14035) finds topical
relevance and context position the most reproducible levers and reports that
citation-oriented rewrites can impair retrieval. Therefore: recommend verifiable
sources and original data as content quality, never "rewrite passages for AI".

---

## GEO Analysis Criteria

The weights are a heuristic [H]; the individual checks carry their own tags.

### 1. Crawler Access & Eligibility (25%)

- robots.txt status per token (table below) [V]
- Page indexable: HTTP 200, no `noindex`, canonical points to itself or an intended URL [V]
- Snippet eligibility: flag `nosnippet`, `max-snippet:0`, or `data-nosnippet` on main content. Google requires a page to be "indexed and eligible to be shown in Google Search with a snippet" [V]
- Search Console > Settings > **Search generative AI** control must be "Include" (default; covers AI Overviews, AI Mode and Discover gen-AI features). The tool cannot read it: ask the user to confirm [V]
- Bing: `<meta name="bingbot" content="noarchive">` (or robots NOARCHIVE) excludes content from chat answers and from training Microsoft's generative AI foundation models; NOCACHE limits both to URL/title/snippet. If both tags are present, Bing treats the page as NOCACHE [V; documented for Bing Chat, 2023-09-22; applies to Copilot by inference]
- Apple: `nosnippet` opts out of Apple's broad world-knowledge answers [V]
- JavaScript: Google processes JS "as long as it isn't blocked" [V]. OpenAI, Anthropic and Perplexity do not document rendering, so check that critical content is present in the initial HTML [H]

### 2. Content Uniqueness & Helpfulness (25%)

- First-hand experience, original data or research, a unique viewpoint [V Google]
- Non-commodity vs commodity: Google contrasts a generic "7 Tips for First-Time Homebuyers" with a first-hand "Why We Waived the Inspection..." account. Flag pages that only restate common knowledge [V]
- Flag scaled near-duplicate pages targeting query variants [V]
- Verifiable claims with cited sources: Bing says "Examples, data, and cited sources help build trust" [V]; GEO paper supports it conditionally [R]

### 3. Structure & Semantic HTML (15%)

- Clear heading hierarchy, logical sections and paragraphs [V Google]
- Semantic HTML: "generally a good idea", not required [V Google]
- Tables, lists and FAQ sections where they serve users: Bing says "Clear headings, tables, and FAQ sections help surface key information" [V Bing]
- No passage-length, answer-length or question-heading rules (no primary source)

### 4. Rich Media (10%)

- Relevant, high-quality images and video that follow image and video SEO best practices [V Google]
- Text, images and video describe the same entities consistently [V Bing]

### 5. Entity, Trust & Freshness (25%)

- Authorship, publication and update dates, clear organization identity [H; aligned with Google helpful-content guidance]
- Consistent entity data across text, images and video [V Bing]
- Organization/Person `sameAs` consistency with official profiles [H]
- Authentic third-party discussion (blogs, videos, forums) can be surfaced by Google's AI features, but must never be manufactured [V Google]
- Merchant Center feeds and Google Business Profile for products/local [V Google]; Bing Places for Business for local [V Bing]
- Freshness; IndexNow for Bing [V Bing]
- Presence on Wikipedia, Reddit, YouTube: [H], report only, no correlation numbers

**Informational only (0 weight, never a scored requirement):** llms.txt, RSL.

---

## AI Crawler Tokens (robots.txt)

| Token | Vendor | Controls | Effect of Disallow |
|-------|--------|----------|--------------------|
| Googlebot | Google | Search crawling, incl. AI Overviews / AI Mode | Removed from Search entirely; the only robots.txt control for Search AI features |
| Google-Extended | Google | Control token only (no own UA): Gemini training and grounding in Gemini Apps / Vertex AI | Does NOT affect Search inclusion or ranking |
| OAI-SearchBot | OpenAI | ChatGPT search results | Not shown in ChatGPT search answers; about 24h to take effect |
| GPTBot | OpenAI | Foundation-model training | Training opt-out only |
| ChatGPT-User | OpenAI | User-initiated fetches | robots.txt "may not apply"; not used for search inclusion |
| PerplexityBot | Perplexity | Perplexity search results; not used for model training | Not crawled for Perplexity search |
| Perplexity-User | Perplexity | User-initiated fetches | "generally ignores robots.txt" |
| Claude-SearchBot | Anthropic | Search indexing / quality | Content not indexed for Claude search |
| Claude-User | Anthropic | User-initiated fetches | May reduce visibility for user-directed search |
| ClaudeBot | Anthropic | Model training | Training opt-out only |
| bingbot | Microsoft | Bing index (Bing, Copilot, AI summaries) | Removed from Bing; use NOCACHE/NOARCHIVE for AI answer control instead (documented for Bing Chat; Copilot by inference) |
| Applebot | Apple | Spotlight / Siri / Safari search; follows Googlebot rules if not named | Removed from Apple search features |
| Applebot-Extended | Apple | Foundation-model training | Training opt-out only |
| CCBot | Common Crawl | Open crawl dataset (used by many model builders) | Excluded from future Common Crawl crawls |

**Guidance:**
- To appear in AI search, allow the search and user tokens: Googlebot, bingbot, OAI-SearchBot, PerplexityBot, Claude-SearchBot, Claude-User, Applebot [V].
- Blocking training tokens (GPTBot, ClaudeBot, Google-Extended, Applebot-Extended, CCBot) is a business decision. No vendor documents that it changes search visibility; OpenAI states its bot settings are independent [V].
- Legacy or unverified tokens (`anthropic-ai`, `Bytespider`, `cohere-ai`): report if present, make no recommendation.

---

## llms.txt (informational only)

Fetch `GET /llms.txt` and report: present (200, text) / absent (404) / server error / non-text response.

- Status: a proposal (llmstxt.org, Jeremy Howard, 2024; revised 2026), not a ratified standard.
- Google Search ignores it; it neither helps nor harms visibility (AI optimization guide; Search Central changelog 2026-06-15) [V].
- No fetched documentation from OpenAI, Anthropic, Perplexity or Microsoft says their search or citation systems read it: report as "unconfirmed".
- Chrome Lighthouse's experimental Agentic Browsing audit marks a 404 as N/A (optional) and flags only server errors [V].

Never add llms.txt to the score, Top 5 changes or Quick Wins. Mention creating
one only if the user explicitly asks about AI agent / developer-tool use.

## RSL (informational)

RSL 1.0 (Really Simple Licensing) is a licensing specification (Recommendation,
published 2025-12-10) declared via a robots.txt `License:` directive, an HTTP
`Link` header, or an HTML link. Report if present. It is a licensing signal,
not a visibility factor.

---

## Platform Notes

- **Google AI Overviews / AI Mode:** core ranking + RAG + query fan-out. Eligibility = indexed + snippet-eligible + Search Console generative AI control "Include". Merchant Center and GBP for products/local [V].
- **Bing / Copilot:** Bing index; NOCACHE / NOARCHIVE controls (documented for Bing Chat; Copilot by inference); IndexNow; Bing Places [V].
- **ChatGPT search:** OAI-SearchBot access [V].
- **Perplexity:** PerplexityBot access [V].
- **Claude:** Claude-SearchBot / Claude-User access [V].
- **Apple:** Applebot access; `nosnippet` opt-out [V].

No platform citation-share percentages are used (none verified from a primary source).

---

## Measurement

1. **Search Console Generative AI performance report** [V] (launched 2026-06-03; all sites since 2026-08-31)
   - Metric: impressions; dimensions: Pages, Countries, Devices, Dates (no query dimension or click metric documented)
   - Search type filter: "Web: text-based" or "Web: multimodal" (images as part of the search)
   - Covers AI Overviews and AI Mode (Discover has a separate report); excludes Search Labs
   - 1,000-row limit; dates in Pacific Time
   - Not available via the Search Analytics API (inferred: the API `type` enum has no generative-AI value, as of 2026-08-11). Workflow: the user exports chart and table via the Export button; this skill reads the CSV (details: `skills/seo-google/references/gsc-generative-ai-report.md`, `/seo google gen-ai-report`)
   - AI Overviews / AI Mode are also counted in the standard Performance report (Web search type)
2. **Bing Webmaster Tools AI Performance** [V] (public preview, Feb 2026)
   - Total Citations, Average Cited Pages, Grounding queries (sampled), page-level citation activity, trends
   - Since 2026-06-16 (preview): Intents, Topics, Citation Share (site's share of citations per grounding query; not traffic or ranking) and Compare
   - Surfaces: Microsoft Copilot, AI summaries in Bing, select partner integrations
   - No API for this report; the UI exports CSV and Excel, and "AI Performance data is sampled" ([Bing help](https://www.bing.com/webmasters/help/ai-performance-9f8e7d6c)). Parse exports with `python scripts/bing_webmaster.py ai-performance <url> --file <export.csv> --json` (see `/seo backlinks ai-performance`). Citations do not indicate ranking
3. **Third-party tools:** optional sampling only. Google warns: "No third-party tool has access to our internal ranking or AI systems."

### DataForSEO Integration (Optional)

If DataForSEO MCP is detected (v3: the `dataforseo` server's `api_request` tool; deprecated v2: per-endpoint tools such as `serp_organic_live_advanced`), use POST `/v3/ai_optimization/chat_gpt/llm_scraper/live/advanced` (`ai_optimization_chat_gpt_scraper`) to check what ChatGPT web search returns for target queries, and `/v3/ai_optimization/llm_mentions/search_mentions/live` (`ai_opt_llm_ment_search`) with `/v3/ai_optimization/llm_mentions/top_mentioned_domains/live` (`ai_opt_llm_ment_top_domains`) for LLM mention tracking. LLM Mentions costs $0.1 per request plus $0.001 per row (DataForSEO pricing, 2026-09-25): confirm before large pulls. Label results "third-party sampling, not vendor data".

---

## Output

Worked examples (robots.txt, finding phrasing, sample report, measurement readout): `references/geo-examples.md`.

Generate `GEO-ANALYSIS.md` with:

1. **GEO Readiness Score: XX/100** (heuristic)
2. **Crawler Access** table per token (search / training / user-initiated)
3. **Indexability & Snippet Eligibility** (+ Search Console generative AI control, user-confirmed)
4. **Content Uniqueness** findings
5. **Structure & Semantic HTML**
6. **Rich Media**
7. **Entity, Trust & Local/Commerce** (GBP, Merchant Center, Bing Places)
8. **Structured data:** rich-result eligibility only (no special AI schema)
9. **Informational:** llms.txt status, RSL status (no recommendation)
10. **Measurement** setup/status (Search Console Gen AI report, Bing AI Performance)
11. **Top 5 Highest-Impact Changes**, each tagged [V] / [R] / [H]

---

## Quick Wins

1. Fix robots.txt for the search tokens the user wants [V]
2. Remove unintended `noindex` / `nosnippet` / `data-nosnippet` / bingbot NOARCHIVE [V]
3. Confirm the Search Console "Search generative AI" control is "Include" [V]
4. Add visible authorship and publication/update dates [H]
5. Verify Google Business Profile and Merchant Center data [V]
6. Enable IndexNow for Bing [V]

## Medium Effort

1. Server-render critical content for non-Google crawlers [H]
2. Add relevant original images and video [V]
3. Make Organization/Person entity data consistent across the site and profiles [V Bing / H]
4. Set up both measurement reports and a baseline export [V]
5. FAQ content is fine where it helps users (Bing mentions FAQ sections), but the FAQ rich result no longer appears in Google since 2026-05-07 [V]

## High Impact

1. Original research, first-hand content, proprietary data [V]
2. Unique tools or calculators that are not commodity content [V]
3. Earn authentic third-party coverage and discussion (never manufactured) [V]

## Error Handling

| Scenario | Action |
|----------|--------|
| URL unreachable (DNS failure, connection refused) | Report the error clearly. Do not guess site content. Suggest the user verify the URL and try again. |
| AI crawlers blocked by robots.txt | Report per token, separating search, training and user-initiated tokens. Give directives only for the search tokens the user wants to allow; treat training blocks as a business choice. |
| No llms.txt found | Report "absent (informational)". Do not recommend creating one for search visibility: Google ignores it; other engines unconfirmed. |
| No structured data detected | Report the gap and recommend schema (Article, Organization, Person) for rich-result eligibility, not for AI visibility. |
| Gen AI report not visible in Search Console | May be low impressions or the site excluded via the Search generative AI control (see help page). |
