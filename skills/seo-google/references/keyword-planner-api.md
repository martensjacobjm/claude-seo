# Google Ads API - Keyword Planner Reference

Gold-standard source for keyword search volume. DataForSEO gets its volume data from Google Ads -- this cuts out the middleman.

## Prerequisites (More Complex Than Other Google APIs)

1. **Google Ads account** -- a manager account is optional ([access levels](https://developers.google.com/google-ads/api/docs/api-policy/access-levels))
2. **Developer Token** with Basic or Standard access -- Test access reaches only test accounts and Explorer access cannot call KeywordPlanIdeaService
3. **OAuth token with the `https://www.googleapis.com/auth/adwords` scope** ([source](https://developers.google.com/google-ads/api/docs/oauth/internals)). `python scripts/google_auth.py --auth --creds client_secret.json` requests it (since 2026-09-28). Tokens created earlier lack it: re-run `--auth` once. `python scripts/google_auth.py --check ads` shows the status
4. Config keys in `~/.config/claude-seo/google-api.json`: `ads_developer_token`, `ads_customer_id`, optional `ads_login_customer_id`, and `oauth_client_path`

## Key Methods

### GenerateKeywordIdeas
Generate keyword suggestions from seed terms.

**Returns per keyword:**
- `text`: Keyword string
- `avg_monthly_searches`: approximate monthly searches averaged over the past 12 months (single integer)
- `competition`: LOW / MEDIUM / HIGH (for ads, not organic)
- `competition_index`: 0-100 competition score
- `low_top_of_page_bid_micros`: ~20th percentile CPC in micros
- `high_top_of_page_bid_micros`: ~80th percentile CPC in micros
- `monthly_search_volumes[]`: Per-month volume for last 12 months

### GenerateKeywordHistoricalMetrics
Get volume data for specific keywords.

Same return fields as above but for exact keyword list instead of suggestions.

### GenerateKeywordForecastMetrics
Predict clicks, impressions, and cost for keywords.

## Configuration

Add to `~/.config/claude-seo/google-api.json`:

```json
{
  "ads_developer_token": "YOUR_DEV_TOKEN",
  "ads_customer_id": "123-456-7890",
  "ads_login_customer_id": "123-456-7890"
}
```

## Rate Limits

- Keyword Planning requests are more strictly rate-limited than other Ads API services
- Exact QPM/QPS not publicly documented
- Google recommends caching results

## Python Library

```bash
pip install google-ads
```

Uses `google-ads` library (separate from `google-api-python-client`).

## Important Notes

- **Volume accuracy** [H]: coarser numbers for accounts without ad spend are reported for the Keyword Planner UI but not stated in the API reference; treat no-spend values as approximate
- **Competition score**: Measures advertiser competition for ads, NOT organic ranking difficulty
- **CPC bids**: Reflect what advertisers pay, useful for estimating keyword commercial value
- **Location targeting**: Use location IDs (2840 = United States, 2826 = United Kingdom)
- **Language targeting**: Use language IDs (1000 = English, 1003 = Spanish)
