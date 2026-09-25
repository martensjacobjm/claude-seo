---
name: seo-content
description: >
  Content quality and E-E-A-T analysis with AI search visibility assessment.
  Use when user says "content quality", "E-E-A-T", "content analysis",
  "readability check", "thin content", or "content audit".
user-invokable: true
argument-hint: "[url]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "1.8.1"
  category: seo
---

# Content Quality & E-E-A-T Analysis

## E-E-A-T Framework (updated Sept 2025 QRG)

Read `skills/seo/references/eeat-framework.md` for full criteria.

Read `skills/seo/references/ranking-signals.md` for what Google docs, the DOJ v. Google record and the 2024 API leak disclose about site-level quality, content effort and originality. Google states "E-E-A-T itself isn't a specific ranking factor"; score E-E-A-T as a proxy for signals its systems do use, never as a factor itself.

### Experience (first-hand signals)
- Original research, case studies, before/after results
- Personal anecdotes, process documentation
- Unique data, proprietary insights
- Photos/videos from direct experience

### Expertise
- Author credentials, certifications, bio
- Professional background relevant to topic
- Technical depth appropriate for audience
- Accurate, well-sourced claims

### Authoritativeness
- External citations, backlinks from authoritative sources
- Brand mentions, industry recognition
- Published in recognized outlets
- Cited by other experts

### Trustworthiness
- Contact information, physical address
- Privacy policy, terms of service
- Customer testimonials, reviews
- Date stamps, transparent corrections
- Secure site (HTTPS)

## Content Metrics

### Word Count Analysis
Compare against page type minimums:
| Page Type | Minimum |
|-----------|---------|
| Homepage | 500 |
| Service page | 800 |
| Blog post | 1,500 |
| Product page | 300+ (400+ for complex products) |
| Location page | 500-600 |

> **Important:** These are **topical coverage floors**, not targets. Google has confirmed word count is NOT a direct ranking factor. The goal is comprehensive topical coverage; a 500-word page that thoroughly answers the query will outrank a 2,000-word page that doesn't. Use these as guidelines for adequate coverage depth, not rigid requirements.

### Readability
- Flesch Reading Ease: target 60-70 for general audience

> **Note:** Flesch Reading Ease is a useful proxy for content accessibility but is NOT a direct Google ranking factor. John Mueller has confirmed Google does not use basic readability scores for ranking. Yoast deprioritized Flesch scores in v19.3. Use readability analysis as a content quality indicator, not as an SEO metric to optimize directly.
- Grade level: match target audience
- Sentence length: average 15-20 words
- Paragraph length: 2-4 sentences

### Keyword Optimization
- Primary keyword in title, H1, first 100 words
- Natural use of the topic's key terms and entities; no keyword-density target (heuristic ranges like 1-3% have no Google source)
- Semantic variations present
- No keyword stuffing (a `KeywordStuffingScore` field exists in the leaked API docs)

### Content Structure
- Logical heading hierarchy (H1 -> H2 -> H3)
- Scannable sections with descriptive headings
- Bullet/numbered lists where appropriate
- Table of contents for long-form content

### Multimedia
- Relevant images with proper alt text
- Videos where appropriate
- Infographics for complex data
- Charts/graphs for statistics

### Internal Linking
- 3-5 relevant internal links per 1000 words
- Descriptive anchor text
- Links to related content
- No orphan pages

### External Linking
- Cite authoritative sources
- Open in new tab for user experience
- Reasonable count (not excessive)

## AI Content Assessment (Sept 2025 QRG addition)

Google's raters now formally assess whether content appears AI-generated.

### Acceptable AI Content
- Demonstrates genuine E-E-A-T
- Provides unique value
- Has human oversight and editing
- Contains original insights

### Low-Quality AI Content Markers
- Generic phrasing, lack of specificity
- No original insight
- Repetitive structure across pages
- No author attribution
- Factual inaccuracies

> **Helpful Content System (March 2024):** The Helpful Content System was merged into Google's core ranking algorithm during the March 2024 core update. It no longer operates as a standalone classifier. Helpfulness signals are now weighted within every core update. The same principles apply (people-first content, demonstrating E-E-A-T, satisfying user intent), but enforcement is continuous rather than through separate HCU updates.

## AI Search Visibility (Google AI Overviews / AI Mode)

Base this section on Google's "Guide to Optimizing for Generative AI Features on Google Search"
(https://developers.google.com/search/docs/fundamentals/ai-optimization-guide, updated 2026-07-10).
Google: "There are no additional requirements to appear in AI Overviews or AI Mode", and both
features "surface relevant links" (https://developers.google.com/search/docs/appearance/ai-features).

**Assess (what Google recommends):**
- **Non-commodity content:** a unique point of view, first-hand experience, expert takes that go beyond common knowledge. Flag content that only restates what is available elsewhere or "could easily be produced by a generative AI model"
- **Organization for readers:** paragraphs, sections and headings that make the page easy to follow
- **Images and video:** high-quality, relevant media that supports the text (cross-check `seo-images`)
- **Technical basics:** page indexed and eligible for a snippet; crawlable (cross-check `seo-technical`)
- **Scaled variants:** separate pages for every query variation or fan-out query made "primarily to manipulate rankings or generative AI responses" violate the scaled content abuse policy

**Do not score or recommend (Google lists these as unnecessary):**
- Rewriting content "just for AI systems" or in a special "quotable"/answer-first style
- "Chunking" content into small pieces; there is "no ideal page length"
- llms.txt or other AI-specific files and markup
- Structured data as a generative AI factor: it "isn't required for generative AI search, and there's no special schema.org markup you need to add" (still worth using for rich-result eligibility)
- Seeking inauthentic "mentions"

**Measure:** the Search Console Generative AI performance report (see `seo-google`). Other AI
platforms (ChatGPT, Perplexity, Copilot) are covered by the `seo-geo` skill; do not apply their
tactics to Google scoring.

## Content Freshness

- Publication date visible
- Last updated date if content has been revised
- Flag content older than 12 months without update for fast-changing topics
- Change visible and schema dates only for substantive updates. Google flags "changing the date of pages to make them seem fresh" as a warning sign

## Site-Level Quality & Effort

See `skills/seo/references/ranking-signals.md` (evidence-graded; leaked attributes show what exists, not weights).
- **Site-wide signals:** Google uses "site-wide signals and classifiers" that "contribute to our understanding of pages" (ranking-systems guide). The leak shows site-level quality-variance fields (`siteQualityStddev`, "spread of the page-level PQ ratings of a site"; weight unknown). Sample pages across sections and report variance. Whether weak sections lower the whole site is an inference, not documented.
- **Effort and originality:** original data, first-hand media, process detail, analysis that is hard to replicate (leak: `contentEffort`, "LLM-based effort estimation for article pages"). Short pages still need unique content (`OriginalContentScore` applies to pages with little content).
- **Topical focus:** flag sections that drift from the site's core topic (leak: `siteFocusScore`, `siteRadius`).
- **YMYL:** apply stricter E-E-A-T checks to health and news pages (leak: `ymylHealthScore`, `ymylNewsScore`).

## Output

### Content Quality Score: XX/100

### E-E-A-T Breakdown
| Factor | Score | Key Signals |
|--------|-------|-------------|
| Experience | XX/25 | ... |
| Expertise | XX/25 | ... |
| Authoritativeness | XX/25 | ... |
| Trustworthiness | XX/25 | ... |

### AI Search Visibility (Google guide): XX/100

### Issues Found
### Recommendations

## DataForSEO Integration (Optional)

If DataForSEO MCP tools are available, use `kw_data_google_ads_search_volume` for real keyword volume data, `dataforseo_labs_bulk_keyword_difficulty` for difficulty scores, `dataforseo_labs_search_intent` for intent classification, and `content_analysis_summary` for content quality analysis.

## Error Handling

| Scenario | Action |
|----------|--------|
| URL unreachable (DNS failure, connection refused) | Report the error clearly. Do not guess page content. Suggest the user verify the URL and try again. |
| Content behind paywall (402/403, login wall) | Report that the content is not publicly accessible. Analyze only the visible portion (meta tags, headers) and note the limitation. |
| Thin content (fewer than 100 words retrievable) | Report the findings as-is rather than guessing. Flag the page as potentially JavaScript-rendered or gated, and suggest the user provide the full text directly. |
