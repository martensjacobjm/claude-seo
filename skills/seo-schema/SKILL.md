---
name: seo-schema
description: >
  Detect, validate, and generate Schema.org structured data. JSON-LD format
  preferred. Use when user says "schema", "structured data", "rich results",
  "JSON-LD", or "markup".
user-invokable: true
argument-hint: "[url]"
license: MIT
metadata:
  author: AgriciDaniel
  version: "1.8.1"
  category: seo
---

# Schema Markup Analysis & Generation

## Detection

1. Scan page source for JSON-LD `<script type="application/ld+json">`
2. Check for Microdata (`itemscope`, `itemprop`)
3. Check for RDFa (`typeof`, `property`)
4. Always recommend JSON-LD as primary format (Google's stated preference)

## Validation

- Check required properties per schema type
- Validate against Google's supported rich result types
- Test for common errors:
  - Missing @context
  - Invalid @type
  - Wrong data types
  - Placeholder text
  - Relative URLs (should be absolute)
  - Invalid date formats
- Flag deprecated types (see below)

## Schema Type Status (as of September 2026)

Read `references/schema-types.md` (in the `seo` skill) for the full list and sources. Key rules:

- Schema.org vocabulary: v30.1 (2026-09-16), https://schema.org/docs/releases.html
- Google status: https://developers.google.com/search/updates and the search gallery (https://developers.google.com/search/docs/appearance/structured-data/search-gallery)

### ACTIVE (recommend freely):
Organization, LocalBusiness, SoftwareApplication, WebApplication, Product (with Certification markup as of April 2025), ProductGroup, Offer, Service, Article, BlogPosting, NewsArticle, Review, AggregateRating, BreadcrumbList, WebSite (site names), WebPage, Person, ProfilePage, ContactPage, VideoObject, ImageObject, Event, JobPosting, Course, DiscussionForumPosting, Recipe, QAPage, Quiz (Education Q&A), MathSolver, EmployerAggregateRating, VacationRental, Movie

Special cases (still supported, narrow scope):
- **Dataset**: used by Google Dataset Search only, not Google Search (clarified Nov 5, 2025)
- **Book** (Book actions): deprecation reversed Nov 5, 2025; still used by a Search feature

### VIDEO & SPECIALIZED (recommend freely):
BroadcastEvent, Clip, SeekToAction, SoftwareSourceCode

See `schema/templates.json` for ready-to-use JSON-LD templates for these types.

> **JSON-LD and JavaScript rendering:** Google warns that dynamically generated Product markup "can make Shopping crawls less frequent and less reliable" (https://developers.google.com/search/docs/appearance/structured-data/generate-structured-data-with-javascript). For Product/Offer, include JSON-LD in the initial server-rendered HTML.

> **AI search:** Google says structured data isn't required for generative AI search and no special schema.org markup is needed (https://developers.google.com/search/docs/fundamentals/ai-optimization-guide). Recommend schema for rich-result eligibility, not as an AI-citation lever.

### NO GOOGLE RICH RESULT / PHASING OUT (Info only, don't block):
- **FAQPage**: FAQ rich result no longer shown from May 7, 2026; docs removed June 15, 2026 (https://developers.google.com/search/updates#deprecating-the-faq-rich-result-feature). Replaces the Aug 2023 gov/health restriction. Don't recommend adding; existing markup is harmless. AI-citation benefit is unverified.
- **ClaimReview**: being phased out of Google Search; still supported by Fact Check Explorer (https://developers.google.com/search/docs/appearance/structured-data/factcheck)

### DEPRECATED (never recommend):
- **HowTo**: Rich results removed September 2023 (exception: HowTo paired with MathSolver, which Google's math-solver doc still documents)
- **SpecialAnnouncement**: Deprecated July 31, 2025
- **Course info, Estimated salary, Learning video, Vehicle listing**: no longer shown; docs removed Sep 9, 2025 (Google feature names, not schema.org types)
- **Practice problem**: deprecated Nov 5, 2025; docs removed Jan 6, 2026
- FAQPage is not a deprecated type: see the Info-only section above.

### Recent Google property changes (source: https://developers.google.com/search/updates):
- **VideoObject** (2026-09-24): `creator` (or `author`), Person/Organization with `name` or `alternateName`, `url` recommended; `interactionStatistic` interactionType WatchAction, LikeAction, CommentAction or ShareAction
- **Review snippet** (2026-07-24): no fake or undisclosed incentivized reviews on the page or in markup
- **Product** (2026-07-07): `category` accepts Text or CategoryCode (Google Product Taxonomy); "Sale duration" via `validFrom` + `validThrough`/`priceValidUntil`
- **Product** (2026-05-20): `hasAdultConsideration` required for adult-oriented products; only value Google supports: `https://schema.org/SexualContentConsideration` (https://developers.google.com/search/docs/appearance/structured-data/merchant-listing)
- **Organization** (2025-11-12): merchant-level shipping policy markup supported

## Generation

When generating schema for a page:
1. Identify page type from content analysis
2. Select appropriate schema type(s)
3. Generate valid JSON-LD with all required + recommended properties
4. Include only truthful, verifiable data. Use placeholders clearly marked for user to fill
5. Validate output before presenting

## Common Schema Templates

### Organization
```json
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "[Company Name]",
  "url": "[Website URL]",
  "logo": "[Logo URL]",
  "contactPoint": {
    "@type": "ContactPoint",
    "telephone": "[Phone]",
    "contactType": "customer service"
  },
  "sameAs": [
    "[Facebook URL]",
    "[LinkedIn URL]",
    "[Twitter URL]"
  ]
}
```

### LocalBusiness
```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "[Business Name]",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "[Street]",
    "addressLocality": "[City]",
    "addressRegion": "[State]",
    "postalCode": "[ZIP]",
    "addressCountry": "US"
  },
  "telephone": "[Phone]",
  "openingHours": "Mo-Fr 09:00-17:00",
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": "[Lat]",
    "longitude": "[Long]"
  }
}
```

### Article/BlogPosting
```json
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "[Title]",
  "author": {
    "@type": "Person",
    "name": "[Author Name]"
  },
  "datePublished": "[YYYY-MM-DD]",
  "dateModified": "[YYYY-MM-DD]",
  "image": "[Image URL]",
  "publisher": {
    "@type": "Organization",
    "name": "[Publisher]",
    "logo": {
      "@type": "ImageObject",
      "url": "[Logo URL]"
    }
  }
}
```

## Output

- `SCHEMA-REPORT.md`: detection and validation results
- `generated-schema.json`: ready-to-use JSON-LD snippets

### Validation Results
| Schema | Type | Status | Issues |
|--------|------|--------|--------|
| ... | ... | ✅/⚠️/❌ | ... |

### Recommendations
- Missing schema opportunities
- Validation fixes needed
- Generated code for implementation

## Error Handling

| Scenario | Action |
|----------|--------|
| URL unreachable | Report connection error with status code. Suggest verifying URL and checking if the page requires authentication. |
| No schema markup found | Report that no JSON-LD, Microdata, or RDFa was detected. Recommend appropriate schema types based on page content analysis. |
| Invalid JSON-LD syntax | Parse and report specific syntax errors (missing brackets, trailing commas, unquoted keys). Provide corrected JSON-LD output. |
| Deprecated schema type detected (not FAQPage/ClaimReview) | Flag the deprecated type with its retirement date. Recommend the current replacement type or advise removal if no replacement exists. |
| FAQPage or ClaimReview detected | Info priority: valid schema.org but no (or phasing-out) Google rich result. Don't block; don't recommend adding. |
