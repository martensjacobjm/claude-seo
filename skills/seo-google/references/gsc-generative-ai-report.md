<!-- Updated: 2026-09-24 -->
# Search Console Generative AI Performance Report

Google's first-party measure of how often a site's pages appear in AI Overviews and
AI Mode. **UI only: there is no API access.** The skill must ask the user for an export.

## Status

- Announced 2026-06-03 on the Search Central blog, with separate **Search** and
  **Discover** reports.
- Rolled out to all websites worldwide as of 2026-08-31.
- The same impressions are also included in the overall Performance report.

## Search Report (AI Overviews + AI Mode)

| Item | Detail |
|------|--------|
| Features covered | AI Overviews, AI Mode. Search Labs experiments are excluded. |
| Metric | **Impressions only.** Google's documentation lists no clicks, CTR, position or query dimension. |
| Pages | Final URL linked by the AI feature, after redirects (canonical-assigned) |
| Countries | Yes |
| Devices | Desktop, tablet, mobile |
| Dates | Pacific Time; hourly, daily, weekly or monthly granularity |
| Search-type filter | Web: text-based, Web: multimodal (image used in the search; added 2026-09-24) |
| Table limit | Usual 1,000-row limit of the Performance report applies |

**Aggregation:** chart totals are aggregated by property, the page table by page, so
totals and summed page rows can differ. This is expected.

## Discover Report

- Dimensions: Pages, Countries, Dates (no device dimension).
- Pages = the canonical page that served as the **source** of the information, not
  the page where the user lands.
- One impression per result per session; all data aggregated by page.

## Getting the Data (Manual Export)

The Search Console API `searchanalytics.query` `type` values are `discover`,
`googleNews`, `news`, `image`, `video`, `web`. As of the API reference dated
2026-08-11 there is no generative-AI type or dimension, and neither the help page nor
the launch post mentions API access. **Never claim API access.** Google has not said
it will never add it; re-check the API reference before relying on this.

Ask the user:
1. Search Console > Performance > **Generative AI** (Search, and Discover if relevant).
2. Pick the date range (match the range used for `gsc_query.py`) and the **search-type
   filter**. Ask which filter the export used; record it with the data.
3. **Export** (CSV or Google Sheets) and share the file(s).
4. Parse the Pages, Countries, Devices and Dates tabs.

Values shown as `~` or `-` in the UI export as zeros: do not read them as true zeros
in trend analysis without noting this.

## Interpretation

- **AI share per page (approximate):** Gen AI impressions / total Web impressions from
  `gsc_query.py` (dimension `page`, `--type web`, same dates). Gen AI impressions are
  already part of the overall Performance totals: **never add the two together**.
  Web multimodal reporting (Lens, Circle to Search, image uploads, Chrome "Search this
  image") was added to the Performance and Gen AI reports on 2026-09-24. The API
  reference (updated 2026-08-11) lists only `web`, with no multimodal type.
  **Unverified:** whether API `web` counts include multimodal searches. So the numerator
  and denominator may cover different traffic. Prefer a UI-to-UI comparison (Performance
  and Gen AI exports with the same search-type filter), and label any API-based ratio
  as approximate.
- **Clicks:** clicks on external links in an AI Overview or AI Mode count as clicks in
  the regular Performance report only; they cannot be separated per feature there.
- **Position:** an AI Overview occupies one position and all its links share it;
  AI Mode position follows standard results-page methodology.
- **Pages with high Gen AI impressions** are the pages Google already uses as sources:
  protect them (freshness, accuracy, crawlability) before optimizing others.
- **Device / country gaps** point to where AI features show the site least.
- Report the date range and the export date; data is not comparable with Bing's
  AI Performance report (different engines and metrics).

## Report Missing or Empty

Possible reasons given by Google:
- Gradual rollout (for properties that do not yet see it).
- Too few impressions in generative AI features.
- The site is **excluded** via Settings > **Search generative AI**.

The Search generative AI control (all sites since 2026-08-31) includes or excludes a
property's links and content from AI Overviews, AI Mode and Discover generative AI
features. Google says the control is not used as a ranking or inclusion signal for
other parts of Search, and it does not affect AI training (that is `Google-Extended`).
Exclusion generally takes a few days: 1-2 days after the change goes live, and some
content takes longer because of caching and propagation. Ask the user to check this
setting before diagnosing content problems.

## Sources

- https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports
- https://developers.google.com/search/blog/2026/09/web-multimodal-in-sc (2026-09-24)
- https://support.google.com/webmasters/answer/16984139 (Search report)
- https://support.google.com/webmasters/answer/16983858 (Discover report)
- https://support.google.com/webmasters/answer/16908024 (Search generative AI control)
- https://support.google.com/webmasters/answer/7042828 (Performance report: AI features)
- https://developers.google.com/webmaster-tools/v1/searchanalytics/query (API types)
