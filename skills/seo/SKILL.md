---
name: seo
description: "Comprehensive SEO analysis for any website or business type. Full site audits, single-page analysis, technical SEO (crawlability, indexability, Core Web Vitals with INP), schema markup, content quality (E-E-A-T), image optimization, sitemap analysis, and GEO / AI search visibility for AI Overviews, AI Mode, ChatGPT search, Perplexity and Bing Copilot. Industry detection for SaaS, e-commerce, local, publishers, agencies. Triggers on: SEO, audit, schema, Core Web Vitals, sitemap, E-E-A-T, AI Overviews, AI Mode, GEO, AEO, technical SEO, content quality, page speed, structured data."
user-invokable: true
argument-hint: "[command] [url]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "1.8.1"
  category: seo
---

# SEO: Universal SEO Analysis Skill

**Invocation:** `/seo $1 $2` where `$1` is the command and `$2` is the URL or argument.

**Scripts:** Located at the plugin root `scripts/` directory.

Comprehensive SEO analysis across all industries (SaaS, local services,
e-commerce, publishers, agencies). Orchestrates 16 specialized sub-skills and 11 subagents
(+ 3 optional extension sub-skills: seo-dataforseo, seo-firecrawl, and seo-image-gen).

## Quick Reference

| Command | What it does |
|---------|-------------|
| `/seo audit <url>` | Full website audit with parallel subagent delegation |
| `/seo page <url>` | Deep single-page analysis |
| `/seo sitemap <url or generate>` | Analyze or generate XML sitemaps |
| `/seo schema <url>` | Detect, validate, and generate Schema.org markup |
| `/seo images <url or optimize>` | Image SEO: on-page audit, SERP analysis, file optimization |
| `/seo technical <url>` | Technical SEO audit (9 categories) |
| `/seo content <url>` | E-E-A-T and content quality analysis |
| `/seo geo <url>` | AI search visibility (AI Overviews, AI Mode, ChatGPT, Perplexity, Copilot): crawler access, eligibility, measurement |
| `/seo plan <business-type>` | Strategic SEO planning |
| `/seo programmatic [url\|plan]` | Programmatic SEO analysis and planning |
| `/seo competitor-pages [url\|generate]` | Competitor comparison page generation |
| `/seo local <url>` | Local SEO analysis (GBP, citations, reviews, map pack) |
| `/seo maps [command] [args]` | Maps intelligence (geo-grid, GBP audit, reviews, competitors) |
| `/seo hreflang [url]` | Hreflang/i18n SEO audit and generation |
| `/seo google [command] [url]` | Google SEO APIs (GSC, PageSpeed, CrUX, Indexing, GA4); also `crux-bq`, `crux-benchmark` (CrUX on BigQuery) and `gen-ai-report` (Search Console Generative AI report, manual export) |
| `/seo backlinks <url>` | Backlink profile analysis (free: Moz, Bing, CC; premium: DataForSEO); `ai-performance --file <export>` parses a Bing AI Performance export |
| `/seo firecrawl [command] <url>` | Full-site crawling and site mapping (extension) |
| `/seo dataforseo [command]` | Live SEO data via DataForSEO (extension) |
| `/seo image-gen [use-case] <description>` | AI image generation for SEO assets (extension) |

## Orchestration Logic

When the user invokes `/seo audit`, delegate to subagents in parallel:
1. Detect business type (SaaS, local, ecommerce, publisher, agency, other)
2. Spawn subagents: seo-technical, seo-content, seo-schema, seo-sitemap, seo-performance, seo-visual, seo-geo
3. If Google API credentials detected (`python scripts/google_auth.py --check`), also spawn seo-google agent
4. If local business detected, also spawn seo-local agent
5. If local business detected AND DataForSEO MCP available, also spawn seo-maps agent
6. If backlink APIs detected (`python scripts/backlinks_auth.py --check`), also spawn seo-backlinks agent
7. If Firecrawl MCP available, use `firecrawl_map` to discover all site URLs before analysis
8. Collect results and generate unified report with SEO Health Score (0-100)
9. Create prioritized action plan (Critical -> High -> Medium -> Low)
10. **Offer PDF report**: "Generate a professional PDF report? Use `/seo google report full`"

For individual commands, load the relevant sub-skill directly.
After any analysis command completes, offer to generate a PDF report via `scripts/google_report.py`.

## Industry Detection

Detect business type from homepage signals:
- **SaaS**: pricing page, /features, /integrations, /docs, "free trial", "sign up"
- **Local Service**: phone number, address, service area, "serving [city]", Google Maps embed --> auto-suggest `/seo local` for deeper analysis
- **E-commerce**: /products, /collections, /cart, "add to cart", product schema
- **Publisher**: /blog, /articles, /topics, article schema, author pages, publication dates
- **Agency**: /case-studies, /portfolio, /industries, "our work", client logos

## Quality Gates

Read `references/quality-gates.md` for thin content thresholds per page type.
Hard rules:
- WARNING at 30+ location pages (enforce 60%+ unique content)
- HARD STOP at 50+ location pages (require user justification)
- Never recommend HowTo schema (deprecated Sept 2023; exception: HowTo paired with a MathSolver, see seo-schema)
- FAQ rich result: no longer shown in Google Search for any site since May 7, 2026; docs removed June 15, 2026 (https://developers.google.com/search/updates). Existing FAQPage -> Info priority only; never recommend adding it for Google benefit; any AI-citation benefit is unverified
- Never recommend llms.txt, content chunking, AI-specific rewrites or special AI schema for Google AI features (Google AI optimization guide, updated 2026-07-10); report llms.txt as informational only
- All Core Web Vitals references use INP, never FID

## Reference Files

Load these on-demand as needed (do NOT load all at startup):
- `references/cwv-thresholds.md`: Current Core Web Vitals thresholds and measurement details
- `references/schema-types.md`: All supported schema types with deprecation status
- `references/eeat-framework.md`: E-E-A-T evaluation criteria (Sept 2025 QRG update)
- `references/quality-gates.md`: Content length minimums, uniqueness thresholds
- `references/local-seo-signals.md`: Local ranking factors, review benchmarks, citation tiers, GBP status
- `references/local-schema-types.md`: LocalBusiness subtypes, industry-specific schema and citation sources
- `references/ranking-signals.md`: Evidence-graded map of Google systems (DOJ v. Google record) and 2024 Content Warehouse API leak attributes to audit checks; context only, not scoring (the leak shows attributes exist, not weights)
- `references/free-backlink-sources.md`, `references/backlink-quality.md`: Backlink source comparison and toxic-link patterns (loaded by seo-backlinks)

Maps-specific references (loaded by seo-maps skill, not at startup):
- `references/maps-geo-grid.md`, `references/maps-gbp-checklist.md`, `references/maps-api-endpoints.md`, `references/maps-free-apis.md`

## Scoring Methodology

### SEO Health Score (0-100)
Weighted aggregate of all categories:

| Category | Weight |
|----------|--------|
| Technical SEO | 22% |
| Content Quality | 23% |
| On-Page SEO | 20% |
| Schema / Structured Data | 10% |
| Performance (CWV) | 10% |
| AI Search Readiness | 10% |
| Images | 5% |

### Priority Levels
- **Critical**: Blocks indexing or causes penalties (immediate fix required)
- **High**: Significantly impacts rankings (fix within 1 week)
- **Medium**: Optimization opportunity (fix within 1 month)
- **Low**: Nice to have (backlog)

## Sub-Skills

This skill orchestrates 15 specialized sub-skills (+ 2 extensions):

1. **seo-audit** -- Full website audit with parallel delegation
2. **seo-page** -- Deep single-page analysis
3. **seo-technical** -- Technical SEO (9 categories)
4. **seo-content** -- E-E-A-T and content quality
5. **seo-schema** -- Schema markup detection and generation
6. **seo-images** -- Image optimization, SERP analysis, file optimization
7. **seo-sitemap** -- Sitemap analysis and generation
8. **seo-geo** -- AI search visibility (AI Overviews, AI Mode, ChatGPT search, Perplexity, Copilot)
9. **seo-plan** -- Strategic planning with templates
10. **seo-programmatic** -- Programmatic SEO analysis and planning
11. **seo-competitor-pages** -- Competitor comparison page generation
12. **seo-hreflang** -- Hreflang/i18n SEO audit and generation
13. **seo-local** -- Local SEO (GBP, NAP, citations, reviews, local schema, multi-location)
14. **seo-maps** -- Maps intelligence (geo-grid, GBP audit, reviews, competitor radius)
15. **seo-google** -- Google SEO APIs (GSC, PageSpeed, CrUX, CrUX on BigQuery, Indexing API, GA4, Generative AI report export)
16. **seo-backlinks** -- Backlink profile analysis (free: Moz, Bing, CC; premium: DataForSEO)
17. **seo-firecrawl** -- Full-site crawling and site mapping via Firecrawl MCP (extension)
18. **seo-dataforseo** -- Live SEO data via DataForSEO MCP (extension)
19. **seo-image-gen** -- AI image generation for SEO assets via Gemini (extension)

## Subagents

For parallel analysis during audits:
- `seo-technical` -- Crawlability, indexability, security, CWV
- `seo-content` -- E-E-A-T, readability, thin content
- `seo-schema` -- Detection, validation, generation
- `seo-sitemap` -- Structure, coverage, quality gates
- `seo-performance` -- Core Web Vitals measurement
- `seo-visual` -- Screenshots, mobile testing, above-fold
- `seo-geo` -- AI crawler access (search vs training tokens), indexability/snippet eligibility, content uniqueness, entity signals, AI visibility measurement (llms.txt reported as informational only)
- `seo-local` -- GBP signals, NAP consistency, reviews, local schema, industry-specific local factors (conditional: spawned when Local Service detected)
- `seo-maps` -- Geo-grid rank tracking, GBP audit, review intelligence, competitor radius mapping (conditional: spawned when Local Service detected AND DataForSEO MCP available)
- `seo-google` -- CWV field data, URL indexation status, organic traffic trends (conditional: spawned when Google API credentials detected)
- `seo-backlinks` -- Backlink profile data: DA/PA, referring domains, anchor text, toxic links (conditional: spawned when Moz/Bing API keys detected or always for CC domain-level metrics)
- `seo-dataforseo` -- Live SERP, keyword, backlink, local SEO data (extension, optional)
- `seo-image-gen` -- SEO image audit and generation plan (extension, optional)
- `seo-firecrawl` -- Full-site crawl and site mapping (extension, optional; used by audit for URL discovery)

## Error Handling

| Scenario | Action |
|----------|--------|
| Unrecognized command | List available commands from the Quick Reference table. Suggest the closest matching command. |
| URL unreachable | Report the error and suggest the user verify the URL. Do not attempt to guess site content. |
| Sub-skill fails during audit | Report partial results from successful sub-skills. Clearly note which sub-skill failed and why. Suggest re-running the failed sub-skill individually. |
| Ambiguous business type detection | Present the top two detected types with supporting signals. Ask the user to confirm before proceeding with industry-specific recommendations. |
