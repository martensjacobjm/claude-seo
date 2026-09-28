#!/usr/bin/env python3
"""
Free, documented keyword data sources: an alternative to paid DataForSEO calls.

Orchestrates the existing Claude SEO modules instead of duplicating their auth:
    - Google Search Console Search Analytics API  (gsc_query.py, google_auth.py)
    - Google Ads API Keyword Planner               (keyword_planner.py)
    - Bing Webmaster Tools API (JSON endpoint)     (bing_webmaster.py, backlinks_auth.py)
    - Wikimedia Analytics API pageviews            (optional topic-interest proxy)

Subcommands:
    own-queries <site>   GSC top queries/pages (+ Bing query stats if configured),
                         merged per query, with heuristic opportunity flags.
    ideas <seed...>      Keyword ideas from Keyword Planner and/or Bing
                         GetRelatedKeywords, source and volume semantics per row.
    volume <kw...>       Volumes from every configured source, one row per
                         keyword+source with an explicit unit (never summed).
    trends <kw...>       Official Google Trends API status (alpha, application-
                         gated, request schema not public): returns
                         "not_available". Optional --wikipedia proxy series.
    sources              Which sources are configured and what each needs.

Hard rule: this script never queries Google or Bing search result pages and
never calls undocumented endpoints. Google's spam policies define "sending
automated queries to Google", including "scraping results for rank-checking
purposes", as machine-generated traffic that violates the Google Terms of
Service (developers.google.com/search/docs/essentials/spam-policies, checked
2026-09-28; policies.google.com/terms, effective 2026-07-30). Both
www.google.com/robots.txt and www.bing.com/robots.txt disallow /search.

Graceful degradation: a source that is not configured is skipped with a setup
hint in `skipped`; the command still exits 0 with whatever data it has. Every
data row carries `source`; every result carries a `notes` array.

UNVERIFIED IMPLEMENTATION ASSUMPTIONS (not stated in Microsoft's reference):
    - Bing GetRelatedKeywords/GetKeyword DateTime query params are sent as
      JSON-quoted "\\/Date(ms)\\/" strings (the JSON endpoint's documented
      response DateTime format); string params are JSON-quoted as in the
      documented GetQueryPageDetailStats sample. If Bing rejects the format,
      its error is reported per keyword in `errors`.
    - Bing `Impressions` is treated as strict/exact-match and `BroadImpressions`
      as broad-match impressions (Bing documents only the property names).

Usage:
    python free_keyword_data.py sources --json
    python free_keyword_data.py own-queries sc-domain:example.com --days 28 --json
    python free_keyword_data.py own-queries https://example.com/ --page https://example.com/pricing
    python free_keyword_data.py ideas "running shoes" "trail shoes" --country us --language en-US
    python free_keyword_data.py volume "running shoes" --wikipedia --json
    python free_keyword_data.py trends "running shoes" --wikipedia
"""

import argparse
import json
import os
import re
import statistics
import sys
from datetime import date, datetime, timedelta, timezone
from typing import Optional
from urllib.parse import quote, urlparse

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPTS_DIR)

from google_auth import validate_url  # noqa: E402  (stdlib-only module)

try:
    import requests
except ImportError:  # only network sources need requests
    requests = None

CHECKED = "2026-09-28"
USER_AGENT = "ClaudeSEO/1.8.1 (+https://github.com/AgriciDaniel/claude-seo) free_keyword_data.py"

# Heuristic thresholds (documented in output, adjustable via CLI)
DEFAULT_MIN_IMPRESSIONS = 100
STRIKING_MIN_POS = 4.0
STRIKING_MAX_POS = 20.0
LOW_CTR_FACTOR = 0.5

SOURCE_INFO = {
    "gsc": {
        "name": "Google Search Console Search Analytics API",
        "data": "Your own site's queries/pages: clicks, impressions, CTR, average position",
        "cost": "No charge (Search Console API usage limits apply)",
        "quota": "1,200 QPM per site and per user; 40,000 QPM / 30,000,000 QPD per project; "
                 "max 50K rows per day per search type; rowLimit 1-25,000 per request",
        "requires": "Verified property + OAuth token or service account added as a user",
        "setup": "python scripts/google_auth.py --auth --creds /path/to/client_secret.json "
                 "(or set service_account_path in ~/.config/claude-seo/google-api.json); "
                 "pip install google-api-python-client",
        "docs": "https://developers.google.com/webmaster-tools/v1/searchanalytics/query",
    },
    "bing_webmaster": {
        "name": "Bing Webmaster Tools API (JSON)",
        "data": "Own-site GetQueryStats/GetPageStats/GetPageQueryStats (weekly); keyword "
                "research GetKeywordStats (weekly impressions), GetKeyword, GetRelatedKeywords",
        "cost": "No charge (Bing Webmaster account)",
        "quota": "Not published by Microsoft; script waits 1 s between calls",
        "requires": "Bing Webmaster account + API key (one per user); own-site methods need a verified site",
        "setup": "Bing Webmaster Tools > Settings > API Access > Generate API Key; put it in "
                 "~/.config/claude-seo/backlinks-api.json as bing_api_key or env BING_WEBMASTER_API_KEY",
        "docs": "https://learn.microsoft.com/dotnet/api/microsoft.bing.webmaster.api.interfaces.iwebmasterapi"
                "?view=bing-webmaster-dotnet",
    },
    "google_ads_keyword_planner": {
        "name": "Google Ads API KeywordPlanIdeaService",
        "data": "Keyword ideas and historical metrics: avg_monthly_searches ('Approximate number "
                "of monthly searches ... averaged for the past 12 months'), competition, bids",
        "cost": "No API fee documented (non-compliance fees only); Google Ads account needed",
        "quota": "1 request/second per customer ID; Basic access 15,000 operations/day",
        "requires": "Developer token with Basic or Standard access (Test access = test accounts only; "
                    "Explorer access blocks KeywordPlanIdeaService); OAuth with the adwords scope; "
                    "pip install google-ads",
        "setup": "Apply in Google Cloud Console > Google Ads API overview (brand verification required for "
                 "Basic); add ads_developer_token, ads_customer_id, ads_login_customer_id to "
                 "~/.config/claude-seo/google-api.json",
        "docs": "https://developers.google.com/google-ads/api/docs/api-policy/access-levels",
    },
    "google_trends_api": {
        "name": "Google Trends API (alpha)",
        "data": "Consistently scaled search interest, rolling 5 years, daily/weekly/monthly/yearly, regions",
        "cost": "No pricing published",
        "quota": "Not published",
        "requires": "Acceptance into the application-gated alpha; request schema is not public",
        "setup": "Apply at https://developers.google.com/search/apis/trends#apply",
        "docs": "https://developers.google.com/search/apis/trends",
    },
    "wikimedia_pageviews": {
        "name": "Wikimedia Analytics API (pageviews per article)",
        "data": "Wikipedia article pageviews: a topic-interest PROXY, not search volume (heuristic)",
        "cost": "Free, no key; data CC0",
        "quota": "Unidentified clients 10 req/min; identified User-Agent 200 req/min",
        "requires": "Opt-in with --wikipedia; requests library; descriptive User-Agent (sent)",
        "setup": "None",
        "docs": "https://doc.wikimedia.org/generated-data-platform/aqs/analytics-api/reference/page-views.html",
    },
}

POLICY_NOTE = (
    "No SERP scraping: Google spam policies call automated queries to Google, including "
    "'scraping results for rank-checking purposes', machine-generated traffic that violates the "
    "Google Terms of Service (developers.google.com/search/docs/essentials/spam-policies; "
    "policies.google.com/terms). Rankings for arbitrary keywords have no free legal source; "
    "for your own site use GSC/Bing average position."
)


# --------------------------------------------------------------------------- #
# Source detection (patched in tests)
# --------------------------------------------------------------------------- #

def _gsc_status() -> dict:
    """Is GSC usable? Needs google-api-python-client and OAuth/service-account creds."""
    try:
        import googleapiclient  # noqa: F401
    except ImportError:
        return {"configured": False, "reason": "google-api-python-client not installed"}
    from google_auth import check_credentials
    chk = check_credentials("gsc")
    return {"configured": bool(chk.get("available")), "reason": chk.get("error"),
            "method": chk.get("method")}


def _bing_status() -> dict:
    """Is the Bing Webmaster API usable? Needs an API key and requests."""
    if requests is None:
        return {"configured": False, "reason": "requests library not installed"}
    from backlinks_auth import get_bing_api_key
    key = get_bing_api_key()
    return {"configured": bool(key), "reason": None if key else "no bing_api_key configured"}


def _kp_status() -> dict:
    """Is Keyword Planner usable? Needs google-ads, developer token and customer ID."""
    try:
        import google.ads.googleads  # noqa: F401
    except ImportError:
        return {"configured": False, "reason": "google-ads library not installed"}
    from google_auth import load_config
    cfg = load_config()
    missing = [k for k in ("ads_developer_token", "ads_customer_id") if not cfg.get(k)]
    if missing:
        return {"configured": False, "reason": "missing config: " + ", ".join(missing)}
    return {"configured": True, "reason": None,
            "note": "Access level (Basic/Standard needed) cannot be checked offline"}


def _trends_status() -> dict:
    return {"configured": False,
            "reason": "Google Trends API is an application-gated alpha with no public request "
                      "schema; this script does not implement it"}


def _wiki_status() -> dict:
    if requests is None:
        return {"configured": False, "reason": "requests library not installed"}
    return {"configured": True, "reason": None, "note": "opt-in via --wikipedia"}


def sources_report() -> dict:
    """Build the `sources` command output."""
    checks = {
        "gsc": _gsc_status, "bing_webmaster": _bing_status,
        "google_ads_keyword_planner": _kp_status, "google_trends_api": _trends_status,
        "wikimedia_pageviews": _wiki_status,
    }
    rows = []
    for key, fn in checks.items():
        st = fn()
        row = {"source": key, **SOURCE_INFO[key], "configured": st["configured"],
               "status_reason": st.get("reason"), "checked": CHECKED}
        if st.get("note"):
            row["status_note"] = st["note"]
        rows.append(row)
    return {
        "command": "sources", "status": "ok", "rows": rows,
        "configured": [r["source"] for r in rows if r["configured"]],
        "notes": [POLICY_NOTE,
                  "configured=true means credentials/libraries were found locally; it does not "
                  "prove the account has access (e.g. Google Ads API access level)."],
    }


def _skip(source: str, reason: Optional[str]) -> dict:
    return {"source": source, "reason": reason or "not configured",
            "setup": SOURCE_INFO[source]["setup"]}


# --------------------------------------------------------------------------- #
# Pure helpers (tested directly)
# --------------------------------------------------------------------------- #

def normalize_query(q: str) -> str:
    """Case-fold and collapse whitespace so GSC and Bing query strings line up."""
    return re.sub(r"\s+", " ", (q or "").strip().lower())


def ctr_pct(clicks: float, impressions: float) -> Optional[float]:
    return round(clicks / impressions * 100, 2) if impressions else None


def _pos_bucket(pos: Optional[float]) -> Optional[str]:
    if pos is None or pos <= 0:
        return None
    if pos < 4:
        return "1-3"
    if pos <= 10:
        return "4-10"
    if pos <= 20:
        return "11-20"
    return "21+"


def flag_opportunities(rows: list, min_impressions: int = DEFAULT_MIN_IMPRESSIONS,
                       low_ctr_factor: float = LOW_CTR_FACTOR) -> dict:
    """
    Add heuristic `flags` to rows of one source (in place).

    striking_distance: position 4-20 and impressions >= min_impressions.
    low_ctr: impressions >= min_impressions and CTR < low_ctr_factor x the median
             CTR of this site's own rows in the same position bucket
             (1-3, 4-10, 11-20, 21+), using rows with >= min_impressions.
    Returns the per-bucket median CTRs used as the baseline.
    """
    baseline = {}
    buckets = {}
    for r in rows:
        b = _pos_bucket(r.get("position"))
        if b and r.get("impressions", 0) >= min_impressions and r.get("ctr_pct") is not None:
            buckets.setdefault(b, []).append(r["ctr_pct"])
    for b, vals in buckets.items():
        if len(vals) >= 3:  # too few rows = no meaningful site baseline
            baseline[b] = round(statistics.median(vals), 2)
    for r in rows:
        flags = []
        pos, imp = r.get("position"), r.get("impressions", 0)
        if pos is not None and STRIKING_MIN_POS <= pos <= STRIKING_MAX_POS and imp >= min_impressions:
            flags.append("striking_distance")
        b = _pos_bucket(pos)
        if (b in baseline and imp >= min_impressions and r.get("ctr_pct") is not None
                and r["ctr_pct"] < baseline[b] * low_ctr_factor):
            flags.append("low_ctr")
        r["flags"] = flags
    return baseline


def merge_query_rows(gsc_rows: list, bing_rows: list) -> list:
    """
    Merge per-engine query rows by normalized query.

    Clicks and impressions are summed into `combined` (same unit, different
    engines). Positions and CTRs are kept per engine and never averaged across
    engines. `source` lists the engines that contributed.
    """
    merged = {}
    for engine, rows in (("gsc", gsc_rows), ("bing_webmaster", bing_rows)):
        for r in rows:
            key = normalize_query(r["query"])
            m = merged.setdefault(key, {"query": key, "engines": {}})
            m["engines"][engine] = {k: r.get(k) for k in
                                    ("clicks", "impressions", "ctr_pct", "position", "flags")}
    out = []
    for m in merged.values():
        engines = m["engines"]
        clicks = sum((e.get("clicks") or 0) for e in engines.values())
        imps = sum((e.get("impressions") or 0) for e in engines.values())
        flags = sorted({f"{f}:{src}" for src, e in engines.items() for f in (e.get("flags") or [])})
        out.append({
            "query": m["query"],
            "source": "+".join(sorted(engines)),
            "combined": {"clicks": clicks, "impressions": imps, "ctr_pct": ctr_pct(clicks, imps),
                         "note": "sum across engines; position is per engine only"},
            "gsc": engines.get("gsc"),
            "bing_webmaster": engines.get("bing_webmaster"),
            "flags": flags,
        })
    out.sort(key=lambda r: r["combined"]["impressions"], reverse=True)
    return out


def parse_ms_date(value) -> Optional[date]:
    """Parse the JSON endpoint's '/Date(1316156400000-0700)/' into a UTC date."""
    m = re.search(r"Date\((-?\d+)", str(value or ""))
    if not m:
        return None
    return datetime.fromtimestamp(int(m.group(1)) / 1000, tz=timezone.utc).date()


def aggregate_bing_query_stats(raw: list, start: date, end: date, key: str = "Query") -> list:
    """
    Aggregate weekly Bing QueryStats rows in [start, end] per query.

    Clicks/impressions are summed; position = impression-weighted mean of
    AvgImpressionPosition (rows with position <= 0 are excluded from it).
    """
    acc = {}
    for r in raw or []:
        d = parse_ms_date(r.get("Date"))
        if d is None or d < start or d > end:
            continue
        q = r.get(key) or ""
        a = acc.setdefault(q, {"clicks": 0, "impressions": 0, "pos_w": 0.0, "pos_imp": 0, "weeks": 0})
        imp = r.get("Impressions") or 0
        a["clicks"] += r.get("Clicks") or 0
        a["impressions"] += imp
        a["weeks"] += 1
        pos = r.get("AvgImpressionPosition")
        if pos is not None and pos > 0 and imp:
            a["pos_w"] += pos * imp
            a["pos_imp"] += imp
    out = []
    for q, a in acc.items():
        out.append({
            "query" if key == "Query" else "page": q,
            "clicks": a["clicks"], "impressions": a["impressions"],
            "ctr_pct": ctr_pct(a["clicks"], a["impressions"]),
            "position": round(a["pos_w"] / a["pos_imp"], 1) if a["pos_imp"] else None,
            "weeks": a["weeks"], "source": "bing_webmaster",
        })
    out.sort(key=lambda r: r["impressions"], reverse=True)
    return out


def group_volumes(rows: list) -> list:
    """Group volume rows per keyword, keyed by source AND unit; never add units together."""
    grouped = {}
    for r in rows:
        k = normalize_query(r["keyword"])
        g = grouped.setdefault(k, {"keyword": k, "values": []})
        g["values"].append({x: r.get(x) for x in ("source", "metric", "value", "unit", "period",
                                                  "volume_semantics")})
    for g in grouped.values():
        g["units"] = sorted({v["unit"] for v in g["values"]})
        g["comparable"] = len(g["units"]) <= 1
    return list(grouped.values())


def month_window(months: int, today: Optional[date] = None):
    """Last `months` complete calendar months: (first day of first, last day of last)."""
    today = today or date.today()
    end = today.replace(day=1) - timedelta(days=1)
    y, m = end.year, end.month - (max(months, 1) - 1)
    while m <= 0:
        y, m = y - 1, m + 12
    return date(y, m, 1), end


def site_to_bing_url(site: str) -> str:
    """'sc-domain:example.com' or a URL -> 'https://example.com/' for Bing."""
    if site.startswith("sc-domain:"):
        return f"https://{site.split(':', 1)[1].strip('/')}/"
    url = site if site.startswith("http") else f"https://{site}"
    p = urlparse(url)
    return f"{p.scheme}://{p.netloc}/"


def check_site(site: str) -> Optional[str]:
    """Return an error string if the site/URL is not a public http(s) target."""
    url = site_to_bing_url(site)
    if not validate_url(url):
        return f"Invalid or non-public site: {site}"
    return None


# --------------------------------------------------------------------------- #
# Source fetchers (network; patched in tests)
# --------------------------------------------------------------------------- #

def fetch_gsc(site: str, start: str, end: str, dimension: str, limit: int,
              page: Optional[str] = None) -> dict:
    """GSC rows for one dimension ('query' or 'page') via gsc_query.query_search_analytics."""
    try:
        import gsc_query
    except (ImportError, SystemExit):
        return {"rows": [], "error": "google-api-python-client not installed"}
    filters = [{"dimension": "page", "operator": "equals", "expression": page}] if page else None
    res = gsc_query.query_search_analytics(site, start_date=start, end_date=end,
                                           dimensions=[dimension], row_limit=min(limit, 25000),
                                           filters=filters)
    rows = []
    for r in res.get("rows", [])[:limit]:
        rows.append({dimension: r.get(dimension, (r.get("keys") or [""])[0]),
                     "clicks": r.get("clicks", 0), "impressions": r.get("impressions", 0),
                     "ctr_pct": ctr_pct(r.get("clicks", 0), r.get("impressions", 0)),
                     "position": r.get("position"), "source": "gsc"})
    return {"rows": rows, "error": res.get("error")}


def _bing(endpoint: str, params: dict) -> dict:
    import bing_webmaster as bw
    from backlinks_auth import get_bing_api_key
    return bw._bing_request(endpoint, get_bing_api_key(), params)


def _q(value: str) -> str:
    """JSON-quote a string param, as in the documented JSON GET samples."""
    return json.dumps(value)


def _ms(d: date) -> str:
    ms = int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp() * 1000)
    return f'"\\/Date({ms})\\/"'


def fetch_bing_own(site: str, start: date, end: date, page: Optional[str] = None) -> dict:
    """Bing GetQueryStats (or GetPageQueryStats for one page) + GetPageStats, aggregated."""
    site_url = site_to_bing_url(site)
    if page:
        q = _bing("GetPageQueryStats", {"siteUrl": site_url, "page": _q(page)})
    else:
        q = _bing("GetQueryStats", {"siteUrl": site_url})
    if q.get("status") != "success":
        return {"queries": [], "pages": [], "error": q.get("error")}
    out = {"queries": aggregate_bing_query_stats(q.get("data") or [], start, end), "pages": [],
           "error": None}
    if not page:
        p = _bing("GetPageStats", {"siteUrl": site_url})
        if p.get("status") == "success":
            out["pages"] = aggregate_bing_query_stats(p.get("data") or [], start, end)
        else:
            out["error"] = f"GetPageStats: {p.get('error')}"
    return out


def fetch_kp_ideas(seeds: list, language_id: str, location_id: str, limit: int) -> dict:
    import keyword_planner as kp
    return kp.generate_keyword_ideas(seeds, language_id=language_id,
                                     location_id=location_id, limit=limit)


def fetch_kp_volumes(keywords: list, language_id: str, location_id: str) -> dict:
    import keyword_planner as kp
    return kp.get_keyword_volumes(keywords, language_id=language_id, location_id=location_id)


def fetch_bing_related(seed: str, country: str, language: str, start: date, end: date) -> dict:
    return _bing("GetRelatedKeywords", {"q": _q(seed), "country": _q(country),
                                        "language": _q(language),
                                        "startDate": _ms(start), "endDate": _ms(end)})


def fetch_bing_keyword_stats(keyword: str, country: str, language: str) -> dict:
    return _bing("GetKeywordStats", {"q": _q(keyword), "country": _q(country),
                                     "language": _q(language)})


def fetch_wikipedia(keyword: str, project: str, months: int) -> dict:
    """Resolve keyword to the top Wikipedia article and fetch monthly user pageviews."""
    if requests is None:
        return {"error": "requests library not installed"}
    headers = {"User-Agent": USER_AGENT}
    lang = project.split(".")[0]
    try:
        s = requests.get(f"https://{lang}.wikipedia.org/w/api.php",
                         params={"action": "query", "list": "search", "srsearch": keyword,
                                 "srlimit": 1, "format": "json"}, headers=headers, timeout=30)
        s.raise_for_status()
        hits = s.json().get("query", {}).get("search", [])
        if not hits:
            return {"error": "no matching Wikipedia article"}
        title = hits[0]["title"]
        start, end = month_window(months)
        url = ("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/"
               f"{project}/all-access/user/{quote(title.replace(' ', '_'), safe='')}/monthly/"
               f"{start:%Y%m%d}00/{end:%Y%m%d}00")
        r = requests.get(url, headers=headers, timeout=30)
        r.raise_for_status()
        items = r.json().get("items", [])
        series = [{"month": i["timestamp"][:6], "views": i["views"]} for i in items]
        return {"article": title, "series": series, "error": None}
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        return {"error": f"Wikimedia API error: {e}"}


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #

def _dates(days: int, today: Optional[date] = None):
    today = today or date.today()
    end = today - timedelta(days=3)  # GSC data lag
    return end - timedelta(days=days - 1), end


def cmd_own_queries(site: str, days: int = 28, limit: int = 1000, page: Optional[str] = None,
                    min_impressions: int = DEFAULT_MIN_IMPRESSIONS, top: int = 100) -> dict:
    """GSC (+ Bing) own-site query/page performance with heuristic opportunity flags."""
    start, end = _dates(days)
    result = {"command": "own-queries", "site": site, "status": "ok",
              "date_range": {"start": str(start), "end": str(end)},
              "queries": [], "pages": [], "skipped": [], "errors": [],
              "heuristics": {"min_impressions": min_impressions,
                             "striking_distance": f"position {STRIKING_MIN_POS:g}-{STRIKING_MAX_POS:g} "
                                                  f"and impressions >= {min_impressions}",
                             "low_ctr": f"CTR < {LOW_CTR_FACTOR:g} x median CTR of this site's rows "
                                        "in the same position bucket (per engine, >= 3 rows)",
                             "label": "heuristic"},
              "notes": [POLICY_NOTE]}
    gsc_q, gsc_p, bing_q, bing_p = [], [], [], []

    gst = _gsc_status()
    if gst["configured"]:
        rq = fetch_gsc(site, str(start), str(end), "query", limit, page)
        gsc_q = rq["rows"]
        if rq.get("error"):
            result["errors"].append({"source": "gsc", "error": rq["error"]})
        if not page:
            rp = fetch_gsc(site, str(start), str(end), "page", limit)
            gsc_p = rp["rows"]
            if rp.get("error"):
                result["errors"].append({"source": "gsc", "error": rp["error"]})
        result["notes"].append(
            "GSC: position is the average topmost position of your site; CTR recomputed as "
            "clicks/impressions x 100. Anonymized queries are omitted from query rows, so query "
            "totals are below property totals. Search Analytics exposes at most 50K rows per day "
            "per search type.")
    else:
        result["skipped"].append(_skip("gsc", gst.get("reason")))

    bst = _bing_status()
    if bst["configured"]:
        rb = fetch_bing_own(site, start, end, page)
        bing_q, bing_p = rb["queries"], rb["pages"]
        if rb.get("error"):
            result["errors"].append({"source": "bing_webmaster", "error": rb["error"]})
        result["notes"].append(
            "Bing: GetQueryStats/GetPageStats return weekly rows ('updated every week'); rows whose "
            "week date falls in the range are summed, so the window edge is approximate. Position = "
            "impression-weighted AvgImpressionPosition.")
    else:
        result["skipped"].append(_skip("bing_webmaster", bst.get("reason")))

    baselines = {}
    for name, rows in (("gsc", gsc_q), ("bing_webmaster", bing_q)):
        if rows:
            baselines[name] = flag_opportunities(rows, min_impressions)
    result["heuristics"]["ctr_baseline_by_bucket"] = baselines

    merged = merge_query_rows(gsc_q, bing_q)
    result["queries"] = merged[:top]
    result["opportunities"] = [r for r in merged if r["flags"]][:top]
    pages = [dict(p, flags=[]) for p in gsc_p] + [dict(p, flags=[]) for p in bing_p]
    for name, rows in (("gsc", [p for p in pages if p["source"] == "gsc"]),
                       ("bing_webmaster", [p for p in pages if p["source"] == "bing_webmaster"])):
        if rows:
            flag_opportunities(rows, min_impressions)
    pages.sort(key=lambda r: r["impressions"], reverse=True)
    result["pages"] = pages[:top]
    result["counts"] = {"gsc_queries": len(gsc_q), "bing_queries": len(bing_q),
                        "merged_queries": len(merged), "pages": len(pages)}
    if not gsc_q and not bing_q:
        result["status"] = "no_data"
    elif result["skipped"] or result["errors"]:
        result["status"] = "partial"
    return result


def cmd_ideas(seeds: list, country: str = "us", language: str = "en-US",
              ads_language_id: str = "1000", ads_location_id: str = "2840",
              limit: int = 50, days: int = 90) -> dict:
    """Keyword ideas from Keyword Planner and/or Bing GetRelatedKeywords."""
    result = {"command": "ideas", "seeds": seeds, "status": "ok", "rows": [], "skipped": [],
              "errors": [], "notes": [POLICY_NOTE]}
    kst = _kp_status()
    if kst["configured"]:
        res = fetch_kp_ideas(seeds, ads_language_id, ads_location_id, limit)
        if res.get("error"):
            result["errors"].append({"source": "google_ads_keyword_planner", "error": res["error"]})
        for i in res.get("ideas", []):
            result["rows"].append({
                "keyword": i.get("keyword"), "source": "google_ads_keyword_planner",
                "metric": "avg_monthly_searches", "value": i.get("avg_monthly_searches"),
                "unit": "google_searches_per_month_avg_12m",
                "period": "past 12 months",
                "volume_semantics": "single approximate integer from the API; may be coarse for "
                                    "low/no-spend accounts (reported, not documented)",
                "competition": i.get("competition"),
                "low_top_of_page_bid": i.get("low_top_of_page_bid"),
                "high_top_of_page_bid": i.get("high_top_of_page_bid"),
            })
        result["notes"].append(
            f"Keyword Planner: language constant {ads_language_id}, geo target {ads_location_id}. "
            "avg_monthly_searches is documented as 'Approximate number of monthly searches on this "
            "query, averaged for the past 12 months'.")
    else:
        result["skipped"].append(_skip("google_ads_keyword_planner", kst.get("reason")))

    bst = _bing_status()
    if bst["configured"]:
        end = date.today() - timedelta(days=1)
        start = end - timedelta(days=days - 1)
        for seed in seeds:
            res = fetch_bing_related(seed, country, language, start, end)
            if res.get("status") != "success":
                result["errors"].append({"source": "bing_webmaster", "seed": seed,
                                         "error": res.get("error")})
                continue
            for k in (res.get("data") or [])[:limit]:
                result["rows"].append({
                    "keyword": k.get("Query"), "seed": seed, "source": "bing_webmaster",
                    "metric": "impressions", "value": k.get("Impressions"),
                    "broad_impressions": k.get("BroadImpressions"),
                    "unit": "bing_impressions_in_period",
                    "period": f"{start} to {end}",
                    "volume_semantics": "exact count of Bing impressions over the period "
                                        f"({country}/{language}); not monthly searches, not Google",
                })
        result["notes"].append(
            "Bing GetRelatedKeywords: Impressions treated as strict match, BroadImpressions as broad "
            "match (Microsoft documents names only). Keyword research data covers up to the last "
            "six months (Bing help).")
    else:
        result["skipped"].append(_skip("bing_webmaster", bst.get("reason")))

    result["notes"].append("Units differ per source (see `unit`): never compare Google monthly "
                           "averages with Bing period impressions as if they were one number.")
    if not result["rows"]:
        result["status"] = "no_data"
    elif result["skipped"] or result["errors"]:
        result["status"] = "partial"
    return result


def cmd_volume(keywords: list, country: str = "us", language: str = "en-US",
               ads_language_id: str = "1000", ads_location_id: str = "2840",
               weeks: int = 4, wikipedia: bool = False, wiki_project: str = "en.wikipedia",
               months: int = 12) -> dict:
    """Volumes from each configured source; one row per keyword+source with explicit unit."""
    result = {"command": "volume", "keywords": keywords, "status": "ok", "rows": [],
              "skipped": [], "errors": [], "notes": [POLICY_NOTE]}
    kst = _kp_status()
    if kst["configured"]:
        res = fetch_kp_volumes(keywords, ads_language_id, ads_location_id)
        if res.get("error"):
            result["errors"].append({"source": "google_ads_keyword_planner", "error": res["error"]})
        for k in res.get("keywords", []):
            result["rows"].append({
                "keyword": k.get("keyword"), "source": "google_ads_keyword_planner",
                "metric": "avg_monthly_searches", "value": k.get("avg_monthly_searches"),
                "unit": "google_searches_per_month_avg_12m", "period": "past 12 months",
                "volume_semantics": "approximate; may be coarse for low/no-spend accounts",
                "competition": k.get("competition"),
            })
    else:
        result["skipped"].append(_skip("google_ads_keyword_planner", kst.get("reason")))

    bst = _bing_status()
    if bst["configured"]:
        for kw in keywords:
            res = fetch_bing_keyword_stats(kw, country, language)
            if res.get("status") != "success":
                result["errors"].append({"source": "bing_webmaster", "keyword": kw,
                                         "error": res.get("error")})
                continue
            stats = sorted(res.get("data") or [], key=lambda s: parse_ms_date(s.get("Date")) or date.min)
            recent = stats[-weeks:] if weeks > 0 else stats
            weekly = [{"week": str(parse_ms_date(s.get("Date"))), "impressions": s.get("Impressions"),
                       "broad_impressions": s.get("BroadImpressions")} for s in stats]
            result["rows"].append({
                "keyword": kw, "source": "bing_webmaster", "metric": "impressions",
                "value": sum((s.get("Impressions") or 0) for s in recent) if recent else None,
                "unit": f"bing_impressions_last_{len(recent)}_weeks",
                "period": (f"{weekly[-len(recent)]['week']} to {weekly[-1]['week']}" if recent else None),
                "volume_semantics": f"exact sum of Bing weekly impressions ({country}/{language}); "
                                    "empty history = no data, not zero demand",
                "weekly": weekly,
            })
    else:
        result["skipped"].append(_skip("bing_webmaster", bst.get("reason")))

    if wikipedia:
        for kw in keywords:
            w = fetch_wikipedia(kw, wiki_project, months)
            if w.get("error"):
                result["errors"].append({"source": "wikimedia_pageviews", "keyword": kw,
                                         "error": w["error"]})
                continue
            views = [p["views"] for p in w["series"]]
            result["rows"].append({
                "keyword": kw, "source": "wikimedia_pageviews", "metric": "pageviews",
                "value": round(sum(views) / len(views)) if views else None,
                "unit": "wikipedia_pageviews_per_month_avg", "period": f"last {len(views)} months",
                "volume_semantics": "HEURISTIC topic-interest proxy: human pageviews of the "
                                    f"best-matching {wiki_project} article, not search volume",
                "matched_article": w["article"], "series": w["series"],
            })
        result["notes"].append("Wikipedia pageviews are a heuristic proxy; check matched_article.")

    result["by_keyword"] = group_volumes(result["rows"])
    result["notes"].append("Values are grouped per source and unit and are never summed or averaged "
                           "across sources. `comparable` is false when a keyword has mixed units.")
    if not result["rows"]:
        result["status"] = "no_data"
    elif result["skipped"] or result["errors"]:
        result["status"] = "partial"
    return result


def cmd_trends(keywords: list, wikipedia: bool = False, wiki_project: str = "en.wikipedia",
               months: int = 24) -> dict:
    """Google Trends API is not usable here; explain why, optionally add a Wikipedia proxy."""
    result = {
        "command": "trends", "keywords": keywords, "status": "not_available", "rows": [],
        "source": "google_trends_api",
        "reason": ("The official Google Trends API is an alpha open only to accepted applicants "
                   "(announced 2025-07-24; docs still say 'accepting applications for alpha "
                   "testers' as of 2026-09-28). Its request schema is not public, so it cannot be "
                   "implemented or verified here. Scraping trends.google.com or unofficial "
                   "wrappers (pytrends) is not used: undocumented endpoints."),
        "setup": SOURCE_INFO["google_trends_api"]["setup"],
        "skipped": [_skip("google_trends_api", _trends_status()["reason"])],
        "errors": [],
        "notes": [POLICY_NOTE,
                  "Alternatives: Bing GetKeywordStats weekly impressions (`volume` command, "
                  "`weekly` field), Keyword Planner monthly_search_volumes (12 months), your own GSC "
                  "impressions by date."],
    }
    if wikipedia:
        for kw in keywords:
            w = fetch_wikipedia(kw, wiki_project, months)
            if w.get("error"):
                result["errors"].append({"source": "wikimedia_pageviews", "keyword": kw,
                                         "error": w["error"]})
                continue
            result["rows"].append({"keyword": kw, "source": "wikimedia_pageviews",
                                   "unit": "wikipedia_pageviews_per_month",
                                   "label": "heuristic proxy, not Google Trends",
                                   "matched_article": w["article"], "series": w["series"]})
        if result["rows"]:
            result["status"] = "not_available_proxy_only"
    return result


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def _print_text(res: dict):
    cmd = res.get("command")
    print(f"=== free_keyword_data {cmd}: {res.get('status')} ===")
    if cmd == "sources":
        for r in res["rows"]:
            mark = "OK " if r["configured"] else "-- "
            print(f"  {mark}{r['source']:28s} {r['cost']}")
            if not r["configured"]:
                print(f"       setup: {r['setup']}")
    elif cmd == "own-queries":
        for r in res.get("queries", [])[:25]:
            c = r["combined"]
            print(f"  {r['query'][:45]:45s} {r['source']:20s} imp={c['impressions']:>7} "
                  f"clk={c['clicks']:>5} {','.join(r['flags'])}")
    elif cmd in ("ideas", "volume"):
        for r in res.get("rows", [])[:50]:
            print(f"  {str(r['keyword'])[:40]:40s} {r['source']:28s} {r['value']!s:>9} {r['unit']}")
    elif cmd == "trends":
        print(f"  {res['reason']}")
    for s in res.get("skipped", []):
        print(f"  skipped {s['source']}: {s['reason']} -> {s['setup']}")
    for e in res.get("errors", []):
        print(f"  error {e['source']}: {e.get('error')}")
    for n in res.get("notes", []):
        print(f"  note: {n}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Free, documented keyword data sources "
                                                 "(GSC, Bing Webmaster, Keyword Planner).")
    sub = parser.add_subparsers(dest="command", required=True)

    def common(p):
        p.add_argument("--json", "-j", action="store_true", help="JSON output")

    p = sub.add_parser("own-queries", help="Own-site queries/pages from GSC (+ Bing)")
    p.add_argument("site", help="GSC property (sc-domain:example.com or https://example.com/)")
    p.add_argument("--days", type=int, default=28)
    p.add_argument("--limit", type=int, default=1000, help="Max GSC rows per dimension")
    p.add_argument("--page", help="Only queries for this page URL")
    p.add_argument("--min-impressions", type=int, default=DEFAULT_MIN_IMPRESSIONS)
    p.add_argument("--top", type=int, default=100)
    common(p)

    for name, hlp in (("ideas", "Keyword ideas"), ("volume", "Keyword volumes")):
        p = sub.add_parser(name, help=hlp)
        p.add_argument("keywords", nargs="+")
        p.add_argument("--country", default="us", help="Bing country (ISO 3166, lowercase)")
        p.add_argument("--language", default="en-US", help="Bing language tag")
        p.add_argument("--ads-language-id", default="1000", help="Google Ads language constant")
        p.add_argument("--ads-location-id", default="2840", help="Google Ads geo target constant")
        if name == "ideas":
            p.add_argument("--limit", type=int, default=50)
            p.add_argument("--days", type=int, default=90, help="Bing period (max ~180)")
        else:
            p.add_argument("--weeks", type=int, default=4, help="Bing weeks to sum")
            p.add_argument("--wikipedia", action="store_true", help="Add Wikipedia pageviews proxy")
            p.add_argument("--wiki-project", default="en.wikipedia")
            p.add_argument("--months", type=int, default=12)
        common(p)

    p = sub.add_parser("trends", help="Google Trends API status (+ optional Wikipedia proxy)")
    p.add_argument("keywords", nargs="+")
    p.add_argument("--wikipedia", action="store_true")
    p.add_argument("--wiki-project", default="en.wikipedia")
    p.add_argument("--months", type=int, default=24)
    common(p)

    p = sub.add_parser("sources", help="Which free sources are configured")
    common(p)

    args = parser.parse_args(argv)

    if args.command == "own-queries":
        err = check_site(args.site) or (
            f"Invalid or non-public page URL: {args.page}" if args.page and not validate_url(args.page)
            else None)
        if err:
            res = {"command": "own-queries", "status": "error", "error": err, "notes": []}
            print(json.dumps(res, indent=2) if args.json else f"Error: {err}")
            return 1
        res = cmd_own_queries(args.site, args.days, args.limit, args.page,
                              args.min_impressions, args.top)
    elif args.command == "ideas":
        res = cmd_ideas(args.keywords, args.country, args.language, args.ads_language_id,
                        args.ads_location_id, args.limit, args.days)
    elif args.command == "volume":
        res = cmd_volume(args.keywords, args.country, args.language, args.ads_language_id,
                         args.ads_location_id, args.weeks, args.wikipedia, args.wiki_project,
                         args.months)
    elif args.command == "trends":
        res = cmd_trends(args.keywords, args.wikipedia, args.wiki_project, args.months)
    else:
        res = sources_report()

    res["generated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if args.json:
        print(json.dumps(res, indent=2, default=str))
    else:
        _print_text(res)
    return 0


if __name__ == "__main__":
    sys.exit(main())
