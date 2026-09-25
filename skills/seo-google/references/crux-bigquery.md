<!-- Updated: 2026-09-24 -->
# CrUX on BigQuery Reference

Script: `scripts/crux_bigquery.py`. Public dataset: `chrome-ux-report` (Google Cloud project).

## When to Use It

| Need | Use |
|------|-----|
| Current p75 for a URL or origin (28-day rolling) | CrUX API (`pagespeed_check.py --crux-only`) |
| Weekly trend, last 25 collection periods | CrUX History API (`crux_history.py`) |
| **Monthly history over many months, per device** | **BigQuery** (`crux_bigquery.py`) |
| **Benchmark an origin against competitors in one query** | **BigQuery** (`crux_bigquery.py --compare`) |

BigQuery is origin-level only (no URL-level rows). Use it when the APIs cannot
answer the question: it needs a billing project and costs bytes past the free tier.

## Dataset Layout

- Raw monthly tables: `chrome-ux-report.all.YYYYMM` and `chrome-ux-report.country_CC.YYYYMM`
  (histogram-based, larger and more expensive to scan).
- Materialized summary tables (recommended, "quicker access for querying the data"):

| Table | Grain |
|-------|-------|
| `chrome-ux-report.materialized.metrics_summary` | month + origin |
| `chrome-ux-report.materialized.device_summary` | month + origin + device |
| `chrome-ux-report.materialized.country_summary` | month + origin + device + country |
| `chrome-ux-report.materialized.origin_summary` | list of all origins |

- There is also an `experimental` dataset (`experimental.global`, `experimental.country`).

## Materialized Columns

No histograms: data is aggregated into fractions per assessment bucket plus a
coarse 75th percentile.

| Pattern | Meaning |
|---------|---------|
| `yyyymm` | Release month (treat as INT64, e.g. `202608`) |
| `date` | First day of the month (`YYYY-MM-01`); `metrics_summary` is partitioned on it |
| `origin`, `rank` | Origin and popularity rank bucket |
| `device` | `desktop`, `phone`, `tablet` (device_summary / country_summary) |
| `[fast\|avg\|slow]_<metric>` | Traffic fraction good / needs improvement / poor (`fast_lcp`, `avg_inp`, ...) |
| `[small\|medium\|large]_cls` | CLS fractions good / NI / poor |
| `p75_<metric>` | Coarse p75 in ms (`p75_lcp`, `p75_inp`); `p75_cls` is unitless |
| `[desktop\|phone\|tablet]Density` | Device share of traffic |

In `device_summary` the good share must be normalised per device:
`fast_inp / (fast_inp + avg_inp + slow_inp)`. The script does this for every metric.

Raw tables use different names (advanced use only): INP is `interaction_to_next_paint`,
CLS is `layout_instability.cumulative_layout_shift`, device is `form_factor.name`.
`effective_connection_type` was removed from February 2025.

## Example SQL (Google's CrUX cookbook pattern)

```sql
SELECT yyyymm, device, p75_inp,
  fast_inp / (fast_inp + avg_inp + slow_inp) AS pct_good_inp
FROM `chrome-ux-report.materialized.device_summary`
WHERE date >= '2025-03-01'
  AND origin = 'https://web.dev'
  AND device IN ('desktop', 'phone')
```

The script uses query parameters (`@start_date`, `@origins`, `@devices`) instead of
string literals, so user input is never interpolated into SQL.

## Release Cadence

- New monthly data lands on the **second Tuesday of the following month**.
- Latest as of 2026-09-24: **August 2026 dataset (`202608`)**, published 2026-09-08.
- Month N data is therefore unavailable until mid month N+1: say so in reports.

## Cost and Access

- Queries bill to **your** project. On-demand: first **1 TiB/month free**, then
  **$6.25/TiB**; minimum 10 MB billed per query and per table referenced.
  (The CrUX guide still quotes an older $5/TB rate; the pricing page is authoritative.)
- IAM: `roles/bigquery.jobUser` (permission `bigquery.jobs.create`) on the billing project.
- Auth: service account (`service_account_path`) or Application Default Credentials
  (`gcloud auth application-default login`). The claude-seo OAuth token is **not**
  used: its scopes exclude `bigquery` / `cloud-platform`.
- Billing project precedence: `--project` > `bigquery_project_id` in
  `~/.config/claude-seo/google-api.json` > `GOOGLE_CLOUD_PROJECT` > service-account
  `project_id` > ADC project.
- Safety cap: `--max-bytes-billed` (default 10 GiB) makes BigQuery fail the job instead
  of billing more.

## Workflow

1. `python scripts/crux_bigquery.py <origin> --dry-run --json` and report
   `total_gib` to the user.
2. Run without `--dry-run` once the user accepts the estimate.
3. `--both-devices` for phone vs desktop (cannot be combined with `--device`);
   `--compare a.com b.com` (max 10) for a benchmark. Default ports (`:443`, `:80`) are
   dropped because CrUX origins never include them.
4. `--print-sql` prints SQL and parameters without credentials (debugging, tests).

## Interpreting Output

- `rows_by_origin[origin][]`: `yyyymm`, optional `device`, `p75.{lcp,inp,cls}`,
  per-metric `{good, ni, poor, rating}`, `cwv_pass`, `inp_missing`.
- `cwv_pass`: all p75 values Good. If INP is null (too few interactions), the
  assessment uses LCP + CLS and flags `inp_missing`.
- `not_in_crux`: origin has no rows (insufficient Chrome traffic or wrong variant:
  `www` vs apex and `http` vs `https` are distinct origins).
- `benchmark`: latest month shared by all origins; per metric `rank` (1 = lowest p75)
  and `delta_vs_target` (competitor p75 minus target p75). Ranks use competition
  ranking: equal p75 values share a rank and are flagged `tied: true`. Because p75 is
  bucketed, a tie means "not distinguishable here", not "identical performance".
- The p75 here is coarse (bucketed). For precise current values use the CrUX API.

## Context: Origin Pass Rates

CrUX August 2026 dataset: 55.6% of 18,294,881 origins have good Core Web Vitals
(LCP 68.1%, CLS 81.5%, INP 85.3% good). Chrome flags a continued INP regression.

## Sources

- https://developer.chrome.com/docs/crux/bigquery
- https://developer.chrome.com/docs/crux/guides/bigquery
- https://developer.chrome.com/docs/crux/release-notes
- https://github.com/GoogleChrome/CrUX/tree/main/sql (cookbook)
- https://cloud.google.com/bigquery/pricing
- https://cloud.google.com/bigquery/docs/running-queries (dry runs, IAM)
