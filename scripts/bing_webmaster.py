#!/usr/bin/env python3
"""
Bing Webmaster Tools client for Claude SEO: inbound links via the Webmaster
API, plus an offline parser for AI Performance report exports.

Queries the Bing Webmaster API for inbound link data and link counts (free for
verified site owners). `compare` diffs the linking domains of two sites, which
only works when BOTH sites are verified in your Bing Webmaster account: the API
has no competitor-comparison method and returns link data only for verified
sites. The `ai-performance` command parses CSV/XLSX files that the user
exported from the Bing Webmaster Tools AI Performance report (citations in
Microsoft Copilot, AI-generated summaries in Bing and select partner AI
integrations; grounding queries; cited pages) into normalized JSON.

Usage:
    python bing_webmaster.py links https://example.com --json
    python bing_webmaster.py counts https://example.com --json
    python bing_webmaster.py compare https://example.com https://other-verified-site.com --json
    python bing_webmaster.py ai-performance https://example.com --file queries.csv --file pages.csv --file trend.csv --json
    python bing_webmaster.py ai-performance --file ai_export.xlsx --top 25 --json

Inbound-link methods (documented in the Bing Webmaster API reference,
learn.microsoft.com/dotnet/api/microsoft.bing.webmaster.api.interfaces.iwebmasterapi):
    GetLinkCounts(siteUrl, page) -> {d: {Links: [{Count, Url}], TotalPages}}
        pages on your site that have inbound links, with link counts.
    GetUrlLinks(siteUrl, link, page) -> {d: {Details: [{AnchorText, Url}], TotalPages}}
        inbound links (source URL + anchor) for one of your pages. LinkDetail
        has only AnchorText and Url: no rel/nofollow, country or date data.
    GetUrlTrafficInfo(siteUrl, url) -> {d: {Clicks, Impressions, IsPage, Url}}
        ("domain:" prefix allowed for a whole domain).
Earlier versions of this script called "GetLinkDetails", which is not a
documented method and returns HTTP 404.

AI Performance (ai-performance command). Documented facts come from the Bing
help page https://www.bing.com/webmasters/help/ai-performance-9f8e7d6c and the
Bing Webmaster blog (public preview 2026-02-10; Intents, Topics, Citation Share
and Compare previews June 2026):
    - Not exposed by the Bing Webmaster API: no AI/citation/grounding method
      exists in the IWebmasterApi method list. This command therefore needs no
      API key and makes no network requests.
    - Export: grounding-query data, page-level data and time-series metrics can
      be exported "in CSV and Excel formats"; "Exports reflect the currently
      applied filter" (help page). A filtered export is not a site total.
    - "AI Performance data is sampled"; "Totals may differ across views (for
      example, between pages, grounding queries, and time-series charts)";
      pages and grounding queries "may each be sampled over slightly different
      time windows" (help page). Citations do not indicate rankings, authority,
      or a page's role within an answer (help page).
    - Documented metric definitions (help page): Total Citations = times content
      was visibly referenced during the range; Cited pages = unique pages cited
      on a given day; Average cited pages = average number of unique pages cited
      per day over the range. No rounding rule is documented.
    - UNVERIFIED IMPLEMENTATION ASSUMPTIONS (not documented by Bing):
      * The export column names. Headers are matched tolerantly (case, spaces,
        punctuation ignored) against guessed labels such as "Grounding Query",
        "Page", "Citations", "Citation Share", "Intent", "Topic", "Date",
        "Cited Pages". Unrecognized columns are listed in the output, never
        guessed.
      * Compare: the help page describes Compare only as a chart overlay
        (current period solid, comparison period dashed) and says nothing about
        exporting it. The Last/Prev/Diff citation column aliases are
        speculative, kept in case such an export exists.
      * Headline totals from the trend export: total_citations = sum of daily
        citations; avg_cited_pages = mean of daily cited pages rounded half up.
        Assumed to match the UI cards; not documented by Bing.
"""

import argparse
import csv
import io
import json
import math
import os
import re
import sys
import time
from datetime import datetime, timedelta, timezone
from typing import Optional
from urllib.parse import urlparse

try:
    import requests
except ImportError:  # only the API commands need requests
    requests = None

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPTS_DIR)
try:
    from backlinks_auth import get_bing_api_key, get_bing_verified_sites
    from google_auth import validate_url
except ImportError:
    print("Error: backlinks_auth.py and google_auth.py required in scripts/", file=sys.stderr)
    sys.exit(1)

BING_API_BASE = "https://ssl.bing.com/webmaster/api.svc/json"

# Polite delay between requests
REQUEST_DELAY = 1
_last_request_time = 0

# Inbound-link detail calls (GetUrlLinks) made per `links` run: one per target page
DEFAULT_DETAIL_PAGES = 5


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _error(msg: str, source: str = "bing_webmaster", data=None) -> dict:
    return {"status": "error", "data": data, "error": msg, "metadata": {"source": source}}


def _rate_limit():
    """Enforce polite 1-second delay between Bing API requests."""
    global _last_request_time
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < REQUEST_DELAY and _last_request_time > 0:
        time.sleep(REQUEST_DELAY - elapsed)
    _last_request_time = time.time()


def _bing_request(endpoint: str, api_key: str, params: Optional[dict] = None,
                  method: str = "GET") -> dict:
    """
    Make a request to the Bing Webmaster API.

    Args:
        endpoint: API method name (appended to BING_API_BASE).
        api_key: Bing Webmaster API key.
        params: Query parameters.
        method: HTTP method (GET or POST).

    Returns:
        Standard response dict. On success, `data` is the unwrapped "d" payload.
    """
    if requests is None:
        return _error("requests library required. Install with: pip install requests")
    _rate_limit()

    url = f"{BING_API_BASE}/{endpoint}"
    params = dict(params or {})
    params["apikey"] = api_key
    headers = {"Content-Type": "application/json", "User-Agent": "ClaudeSEO/1.8.0"}

    try:
        if method == "GET":
            response = requests.get(url, params=params, headers=headers, timeout=30)
        else:
            response = requests.post(url, params=params, headers=headers, timeout=30)

        if response.status_code == 401 or (response.status_code == 400 and "InvalidApiKey" in response.text):
            return _error("Invalid Bing Webmaster API key. Get one at https://www.bing.com/webmasters")
        if response.status_code == 403:
            return _error("Access denied. Ensure the site is verified in Bing Webmaster Tools.")
        if response.status_code == 404:
            return _error(f"Bing Webmaster API method not found: {endpoint}")
        response.raise_for_status()

        # Bing API may return empty body for some endpoints; JSON payload is wrapped in "d"
        result_data = response.json() if response.text.strip() else {}
        if isinstance(result_data, dict) and "d" in result_data:
            result_data = result_data["d"]

        return {
            "status": "success",
            "data": result_data,
            "error": None,
            "metadata": {"source": "bing_webmaster", "endpoint": endpoint, "timestamp": _now()},
        }
    except requests.exceptions.Timeout:
        return _error("Request timed out after 30 seconds")
    except (requests.exceptions.RequestException, ValueError) as e:
        return _error(str(e))


def _normalize_site_url(url: str) -> str:
    """Normalize a site URL for Bing API (needs trailing slash for domains)."""
    if not url.startswith("http"):
        url = f"https://{url}"
    parsed = urlparse(url)
    # Bing expects: https://example.com/
    if not parsed.path or parsed.path == "/":
        return f"{parsed.scheme}://{parsed.netloc}/"
    return url


def _json_str_param(value: str) -> str:
    """The JSON endpoint's documented samples pass string args (link, url) JSON-quoted."""
    return json.dumps(value)


def get_link_counts_page(site_url: str, api_key: str, page: int = 0) -> dict:
    """
    GetLinkCounts: pages of your site that have inbound links, with counts.

    Returns:
        Standard response dict; data = {pages: [{url, count}], total_pages}.
    """
    params = {"siteUrl": _normalize_site_url(site_url), "page": page}
    result = _bing_request("GetLinkCounts", api_key, params)
    if result["status"] == "success":
        raw = result["data"] if isinstance(result["data"], dict) else {}
        pages = [{"url": i.get("Url", ""), "count": i.get("Count", 0)}
                 for i in (raw.get("Links") or []) if isinstance(i, dict)]
        result["data"] = {"pages": pages, "total_pages": raw.get("TotalPages", 0)}
    return result


def get_url_links(site_url: str, target_url: str, api_key: str, page: int = 0) -> dict:
    """
    GetUrlLinks: inbound links (source URL + anchor) pointing to one of your pages.

    Returns:
        Standard response dict; data = {links: [{source_url, anchor_text}], total_pages}.
    """
    params = {"siteUrl": _normalize_site_url(site_url), "link": _json_str_param(target_url), "page": page}
    result = _bing_request("GetUrlLinks", api_key, params)
    if result["status"] == "success":
        raw = result["data"] if isinstance(result["data"], dict) else {}
        links = [{"source_url": i.get("Url", ""), "anchor_text": i.get("AnchorText", "")}
                 for i in (raw.get("Details") or []) if isinstance(i, dict)]
        result["data"] = {"links": links, "total_pages": raw.get("TotalPages", 0)}
    return result


def get_link_details(site_url: str, api_key: str, page: int = 0,
                     detail_pages: int = DEFAULT_DETAIL_PAGES) -> dict:
    """
    Get inbound link details for a verified site.

    Calls GetLinkCounts (one result page), then GetUrlLinks (first result page)
    for the `detail_pages` target pages with the most inbound links.

    Args:
        site_url: Verified site URL.
        api_key: Bing API key.
        page: GetLinkCounts page number for pagination (0-based).
        detail_pages: Number of target pages to expand with GetUrlLinks.

    Returns:
        Standard response dict with link data.
    """
    counts = get_link_counts_page(site_url, api_key, page)
    if counts["status"] != "success":
        return counts

    target_pages = sorted(counts["data"]["pages"], key=lambda p: p.get("count") or 0, reverse=True)
    links, detail_errors = [], []
    for target in target_pages[:max(detail_pages, 0)]:
        res = get_url_links(site_url, target["url"], api_key)
        if res["status"] != "success":
            detail_errors.append({"target_url": target["url"], "error": res["error"]})
            continue
        for link in res["data"]["links"]:
            links.append({"source_url": link["source_url"], "target_url": target["url"],
                          "anchor_text": link["anchor_text"]})

    counts["data"] = {
        "site_url": site_url,
        "page": page,
        "total_pages": counts["data"]["total_pages"],
        "target_pages": target_pages,
        "total_returned": len(links),
        "links": links,
        "detail_errors": detail_errors,
        "note": f"Links expanded for the top {min(detail_pages, len(target_pages))} target pages "
                "(first GetUrlLinks page each). Bing returns data only for verified sites.",
    }
    return counts


def get_link_counts(site_url: str, api_key: str) -> dict:
    """
    Get inbound link counts (first GetLinkCounts page) plus domain traffic info.

    Args:
        site_url: Site URL to query.
        api_key: Bing API key.

    Returns:
        Standard response dict with count data.
    """
    result = get_link_counts_page(site_url, api_key, 0)
    if result["status"] != "success":
        return result

    host = urlparse(_normalize_site_url(site_url)).netloc
    traffic = _bing_request("GetUrlTrafficInfo", api_key, {
        "siteUrl": _normalize_site_url(site_url), "url": _json_str_param(f"domain:{host}")})
    pages = result["data"]["pages"]
    result["data"] = {
        "site_url": site_url,
        "pages_with_links_sample": len(pages),
        "inbound_links_sample": sum(p.get("count") or 0 for p in pages),
        "total_result_pages": result["data"]["total_pages"],
        "top_linked_pages": sorted(pages, key=lambda p: p.get("count") or 0, reverse=True)[:20],
        "traffic_info": traffic["data"] if traffic["status"] == "success" else None,
        "traffic_info_error": traffic.get("error"),
        "note": "Counts cover the first GetLinkCounts result page only. For comprehensive data, "
                "use Moz API or DataForSEO.",
    }
    return result


def compare_links(site_url: str, competitor_url: str, api_key: str) -> dict:
    """
    Compare the linking domains of two sites.

    The Bing Webmaster API returns link data only for sites verified in your
    account and has no competitor-comparison method, so this only works when
    BOTH sites are verified in your Bing Webmaster account. For a real
    competitor gap analysis use DataForSEO or Moz.

    If either lookup fails, the gap/shared/unique fields are null (never
    computed against an empty set) and status is "error" with a top-level
    error message.

    Args:
        site_url: Your verified site URL.
        competitor_url: Second verified site URL.
        api_key: Bing API key.

    Returns:
        Standard response dict with comparison data.
    """
    domains = []
    errors = {}
    for label, url in (("site", site_url), ("competitor", competitor_url)):
        res = get_link_details(url, api_key)
        found = set()
        if res["status"] == "success" and isinstance(res["data"], dict):
            for link in res["data"].get("links", []):
                netloc = urlparse(link.get("source_url", "")).netloc
                if netloc:
                    found.add(netloc)
        else:
            errors[label] = res.get("error") or "lookup failed"
        domains.append(found)
    own_domains, competitor_domains = domains

    data = {
        "site_url": site_url,
        "competitor_url": competitor_url,
        "your_linking_domains": None if "site" in errors else len(own_domains),
        "competitor_linking_domains": None if "competitor" in errors else len(competitor_domains),
        "gap_domains": None, "shared_domains": None, "unique_to_you": None,
        "gap_count": None, "shared_count": None, "unique_count": None,
        "errors": errors,
        "note": "Based on a sample of Bing's link data. The API returns link data only for sites "
                "verified in your Bing Webmaster account and has no competitor method; for a real "
                "competitor gap analysis use DataForSEO or Moz.",
    }
    if errors:
        failed = " and ".join(f"{k} ({v})" for k, v in errors.items())
        return {
            "status": "error",
            "data": data,
            "error": f"Link lookup failed for {failed}. No gap computed. Both sites must be verified "
                     "in your Bing Webmaster account; use DataForSEO or Moz for competitor gaps.",
            "metadata": {"source": "bing_webmaster", "comparison": True, "timestamp": _now()},
        }

    gap_domains = competitor_domains - own_domains  # Competitor has, you don't
    shared_domains = own_domains & competitor_domains
    unique_domains = own_domains - competitor_domains  # You have, competitor doesn't
    data.update({
        "gap_domains": sorted(gap_domains)[:50],
        "shared_domains": sorted(shared_domains)[:50],
        "unique_to_you": sorted(unique_domains)[:50],
        "gap_count": len(gap_domains),
        "shared_count": len(shared_domains),
        "unique_count": len(unique_domains),
    })
    return {
        "status": "success",
        "data": data,
        "error": None,
        "metadata": {"source": "bing_webmaster", "comparison": True, "timestamp": _now()},
    }


# ---------------------------------------------------------------------------
# AI Performance export parser (offline, no API key, no network)
# ---------------------------------------------------------------------------

AI_PERF_SOURCE = "bing_webmaster_ai_performance_export"

# canonical column -> normalized header aliases (see _norm_header).
# UNVERIFIED: Bing does not document the export column names; these are guesses.
AI_PERF_COLUMN_ALIASES = {
    "query": {"groundingquery", "groundingqueries", "query", "queries", "keyword"},
    "page": {"page", "pageurl", "url", "citedpage", "citedpageurl", "pages"},
    "citations": {"citations", "totalcitations", "citationcount", "citation"},
    "citation_share": {"citationshare", "citationrate", "share"},
    "intent": {"intent", "intents"},
    "topic": {"topic", "topics", "topicclusters", "topiccluster"},
    "subtopic": {"subtopic", "subtopics"},
    "date": {"date", "day", "datetime"},
    "cited_pages": {"uniquecitedpages", "citedpages", "avgcitedpages", "averagecitedpages"},
    "last_citations": {"lastcitations", "currentcitations"},
    "prev_citations": {"prevcitations", "previouscitations"},
    "diff_citations": {"diffcitations", "change", "difference"},
}
_ALIAS_LOOKUP = {a: canon for canon, aliases in AI_PERF_COLUMN_ALIASES.items() for a in aliases}
# substring fallbacks, checked in order when no exact alias matches
_SUBSTRING_RULES = [
    (lambda h: "grounding" in h, "query"),
    (lambda h: "prev" in h and "citation" in h, "prev_citations"),
    (lambda h: ("last" in h or "current" in h) and "citation" in h, "last_citations"),
    (lambda h: "diff" in h and "citation" in h, "diff_citations"),
    (lambda h: "citation" in h and ("share" in h or "rate" in h), "citation_share"),
    (lambda h: "unique" in h and "page" in h, "cited_pages"),
    (lambda h: "citation" in h, "citations"),
    (lambda h: "subtopic" in h, "subtopic"),
    (lambda h: "topic" in h, "topic"),
    (lambda h: "intent" in h, "intent"),
]
_EMPTY = {"", "-", "—", "–", "n/a", "na", "null", "none"}


def _norm_header(h) -> str:
    """Lowercase a header and strip BOM, quotes, whitespace and _ - . ( ) % / characters."""
    s = str(h or "").replace("﻿", "").lower()
    return re.sub(r"[\s\"'_\-.()%/]", "", s)


def _map_columns(headers: list) -> tuple:
    """Map raw headers to canonical names. Returns ({canonical: index}, [unmapped raw])."""
    mapping, unmapped = {}, []
    for idx, raw in enumerate(headers):
        norm = _norm_header(raw)
        if not norm:
            continue
        canon = _ALIAS_LOOKUP.get(norm)
        if canon is None:
            canon = next((c for rule, c in _SUBSTRING_RULES if rule(norm)), None)
        if canon is None or canon in mapping:
            unmapped.append(str(raw))
        else:
            mapping[canon] = idx
    return mapping, unmapped


def _find_header(rows: list, scan: int = 50) -> int:
    """
    Index of the header row within the first `scan` rows, else -1.

    Picks the row with >= 2 non-empty cells that maps the most columns, preferring
    rows that yield a known table type (so title lines such as
    'Report generated,2026-09-01' above the real header are skipped). Ties go to
    the earliest row.
    """
    best, best_key = -1, None
    for i, row in enumerate(rows[:scan]):
        cells = [c for c in row if str(c if c is not None else "").strip()]
        if len(cells) < 2:
            continue
        cols = _map_columns(list(row))[0]
        if not cols:
            continue
        key = (_classify_table(cols) != "unknown", len(cols))
        if best_key is None or key > best_key:
            best, best_key = i, key
    return best


def _decode(raw: bytes) -> str:
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16")
    for enc in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("latin-1")


def _read_table(path: str) -> tuple:
    """
    Read a CSV/TSV/TXT or XLSX export.

    Returns:
        ([(sheet_name, rows)], error_or_None); rows are lists of raw cell values.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xlsm"):
        try:
            import openpyxl  # lazy: only needed for Excel exports
        except ImportError:
            return [], ("openpyxl is required to read .xlsx exports. Install with: pip install openpyxl "
                        "(listed in requirements.txt), or download/save the report as CSV.")
        try:
            wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
            sheets = [(ws.title, [list(r) for r in ws.iter_rows(values_only=True)]) for ws in wb.worksheets]
            wb.close()
            return sheets, None
        except Exception as e:  # corrupt or non-xlsx file
            return [], f"Could not read Excel file {path}: {e}"
    if ext == ".xls":
        return [], "Legacy .xls is not supported; save the export as .csv or .xlsx."

    with open(path, "rb") as fh:
        text = _decode(fh.read())
    # Pick the delimiter whose header row maps the most columns (tolerates preamble lines
    # that confuse csv.Sniffer); default ',' (or tab for .tsv).
    best_rows, best_score = None, -1
    for delimiter in (("\t", ",", ";") if ext == ".tsv" else (",", ";", "\t")):
        rows = list(csv.reader(io.StringIO(text), delimiter=delimiter))
        hdr = _find_header(rows)
        score = len(_map_columns(rows[hdr])[0]) if hdr >= 0 else 0
        if score > best_score:
            best_rows, best_score = rows, score
    return [(None, best_rows)], None


def _to_number(v, count: bool = False) -> tuple:
    """
    Parse a numeric cell. Returns (number_or_None, had_percent_sign).

    Handles '1,234', '1 234', '12.5%', '12,5' (decimal comma), and numeric cells.
    With count=True (citation counts are whole numbers), '1.234' is read as a
    dot thousands separator (European locale exports).
    """
    if v is None or isinstance(v, bool):
        return None, False
    if isinstance(v, (int, float)):
        if isinstance(v, float) and math.isnan(v):
            return None, False
        return (int(v) if float(v).is_integer() else float(v)), False
    s = str(v).strip().replace(" ", "").replace(" ", "").replace(" ", "").replace(" ", "")
    if s.lower() in _EMPTY:
        return None, False
    pct = s.endswith("%")
    s = s.rstrip("%").lstrip("+")
    if count and re.fullmatch(r"-?\d{1,3}(\.\d{3})+", s):
        s = s.replace(".", "")
    elif "," in s and "." in s:
        s = s.replace(",", "")
    elif "," in s:
        s = s.replace(",", "") if re.fullmatch(r"-?\d{1,3}(,\d{3})+", s) else s.replace(",", ".")
    try:
        num = float(s)
    except ValueError:
        return None, pct
    return (int(num) if num.is_integer() and not pct else num), pct


_DATE_FORMATS = ("%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
                 "%Y/%m/%d", "%m/%d/%Y %H:%M:%S", "%m/%d/%Y %I:%M:%S %p", "%d.%m.%Y", "%b %d, %Y")


def _to_date(v) -> tuple:
    """Parse a date cell to ISO YYYY-MM-DD. Returns (value, parsed_ok)."""
    if v is None:
        return None, False
    if isinstance(v, datetime):
        return v.date().isoformat(), True
    if hasattr(v, "isoformat") and not isinstance(v, str):  # datetime.date
        return v.isoformat(), True
    s = str(v).strip()
    m = re.fullmatch(r"/?Date\((-?\d+)([+-]\d{4})?\)/?", s)  # Bing JSON date: /Date(ms+zzzz)/
    if m:
        dt = datetime.fromtimestamp(int(m.group(1)) / 1000, tz=timezone.utc)
        if m.group(2):
            sign = 1 if m.group(2)[0] == "+" else -1
            dt += sign * timedelta(hours=int(m.group(2)[1:3]), minutes=int(m.group(2)[3:5]))
        return dt.date().isoformat(), True
    s2 = re.sub(r"(\.\d+)?(Z|[+-]\d{2}:?\d{2})$", "", s) if "T" in s else s
    for fmt in _DATE_FORMATS:
        try:
            return datetime.strptime(s2, fmt).date().isoformat(), True
        except ValueError:
            continue
    return s, False


def _classify_table(cols: dict) -> str:
    if "last_citations" in cols and "prev_citations" in cols:
        return "compare"
    if "query" in cols:
        return "queries"
    if "page" in cols:
        return "pages"
    if "date" in cols and ("citations" in cols or "cited_pages" in cols):
        return "trend"
    return "unknown"


def _split_labels(v) -> list:
    """Split an Intent/Topic cell into labels (JSON array, or ';' / '|' separated)."""
    if v is None:
        return []
    s = str(v).strip()
    if not s or s.lower() in _EMPTY:
        return []
    if s.startswith("["):
        try:
            parsed = json.loads(s)
            if isinstance(parsed, list):
                return [str(x).strip() for x in parsed if str(x).strip()]
        except ValueError:
            s = s.strip("[]")
    return [p.strip().strip("'\"") for p in re.split(r"[;|]", s) if p.strip().strip("'\"")]


def _js_round(x: float) -> int:
    """Round half up. Bing documents no rounding rule for Average cited pages;
    this is an implementation choice, not a documented UI behaviour."""
    return int(math.floor(x + 0.5))


def _page_key(url: str) -> str:
    u = url.strip()
    return u[:-1] if u.endswith("/") and u.count("/") > 3 else u


def parse_ai_performance(files: list, site_url: Optional[str] = None, top: int = 20) -> dict:
    """
    Parse Bing Webmaster Tools AI Performance exports into normalized JSON.

    Args:
        files: Paths to CSV/TSV/XLSX files exported from BWT > AI Performance.
        site_url: Optional site label (no request is made).
        top: Number of top pages / queries to return.

    Returns:
        Standard response dict (status, data, error, metadata).
    """
    warnings, source_files = [], []
    trend, pages, queries, compare_rows = {}, {}, {}, []
    page_src, query_src = {}, {}  # key -> path of the file that first supplied it
    compare_dim = None
    share_values = []  # (value, had_pct)
    bad_dates = 0
    tables_recognized = 0

    for path in files:
        sheets, err = _read_table(path)
        if err:
            warnings.append(err)
            source_files.append({"path": path, "type": "error", "error": err})
            continue
        for sheet, rows in sheets:
            hdr = _find_header(rows)
            if hdr < 0:
                first = next((r for r in rows if any(str(c or "").strip() for c in r)), [])
                warnings.append(f"{path}{' [' + sheet + ']' if sheet else ''}: no recognized header row; "
                                f"columns seen: {[str(c) for c in first if c is not None]}")
                source_files.append({"path": path, "sheet": sheet, "type": "unknown", "rows": 0,
                                     "columns_mapped": {}, "columns_unmapped": [str(c) for c in first]})
                continue
            headers = rows[hdr]
            cols, unmapped = _map_columns(headers)
            ttype = _classify_table(cols)
            body = [r for r in rows[hdr + 1:] if any(str(c if c is not None else "").strip() for c in r)]
            info = {"path": path, "sheet": sheet, "type": ttype, "rows": len(body),
                    "columns_mapped": {c: str(headers[i]) for c, i in cols.items()},
                    "columns_unmapped": unmapped}
            source_files.append(info)
            if ttype == "unknown":
                warnings.append(f"{path}: table type not recognized; headers: {[str(h) for h in headers]}")
                continue
            tables_recognized += 1

            def cell(row, name):
                i = cols.get(name)
                return row[i] if i is not None and i < len(row) else None

            skipped_total = 0
            dup_dates = 0
            xfile_pages, xfile_queries = set(), set()  # keys already supplied by another file
            merged_pages, merged_queries = set(), set()  # keys summed within this file
            for row in body:
                first_val = str(row[0] if row and row[0] is not None else "").strip().lower()
                if first_val in ("total", "totals", "grand total"):
                    skipped_total += 1
                    continue
                cit, _ = _to_number(cell(row, "citations"), count=True)
                if ttype == "trend":
                    d, ok = _to_date(cell(row, "date"))
                    if d is None:
                        continue
                    bad_dates += 0 if ok else 1
                    if d in trend:
                        dup_dates += 1
                        continue
                    cp, _ = _to_number(cell(row, "cited_pages"))
                    trend[d] = {"date": d, "citations": cit, "cited_pages": cp}
                elif ttype == "pages":
                    url = str(cell(row, "page") or "").strip()
                    if not url:
                        continue
                    key = _page_key(url)
                    if key in pages and page_src[key] != path:
                        xfile_pages.add(url)  # overlapping export: keep first file's value
                        continue
                    if key in pages:
                        merged_pages.add(url)
                    page_src.setdefault(key, path)
                    entry = pages.setdefault(key, {"page": url, "citations": None})
                    if cit is not None:
                        entry["citations"] = (entry["citations"] or 0) + cit
                elif ttype == "queries":
                    q = str(cell(row, "query") or "").strip()
                    if not q:
                        continue
                    key = q.lower()
                    entry = queries.get(key)
                    if entry is not None and query_src[key] != path:
                        xfile_queries.add(q)  # overlapping export: keep first file's value
                        continue
                    share, had_pct = _to_number(cell(row, "citation_share"))
                    if share is not None:
                        share_values.append((share, had_pct))
                    if entry is None:
                        query_src[key] = path
                        queries[key] = {"query": q, "citations": cit, "citation_share_raw": share,
                                        "intent": _split_labels(cell(row, "intent")),
                                        "topic": _split_labels(cell(row, "topic")),
                                        "subtopic": _split_labels(cell(row, "subtopic"))}
                    else:
                        merged_queries.add(q)
                        if cit is not None:
                            entry["citations"] = (entry["citations"] or 0) + cit
                elif ttype == "compare":
                    dim = "query" if "query" in cols else ("page" if "page" in cols else "row")
                    compare_dim = compare_dim or dim
                    key = str(cell(row, dim) or "").strip() if dim != "row" else str(row[0])
                    last, _ = _to_number(cell(row, "last_citations"), count=True)
                    prev, _ = _to_number(cell(row, "prev_citations"), count=True)
                    diff, _ = _to_number(cell(row, "diff_citations"), count=True)
                    if diff is None and last is not None and prev is not None:
                        diff = last - prev
                    compare_rows.append({"key": key, "last_citations": last,
                                         "prev_citations": prev, "diff_citations": diff})
            if skipped_total:
                warnings.append(f"{path}: skipped {skipped_total} 'Total' summary row(s).")
            if dup_dates:
                warnings.append(f"{path}: {dup_dates} duplicate date row(s) ignored (overlapping trend exports?).")
            for kind, items in (("page", merged_pages), ("grounding query", merged_queries)):
                if items:
                    warnings.append(f"{path}: {len(items)} duplicate {kind} row(s) within this file were merged "
                                    f"(citations summed, first values kept otherwise): "
                                    f"{sorted(items)[:5]}")
            for kind, items in (("page", xfile_pages), ("grounding query", xfile_queries)):
                if items:
                    warnings.append(f"{path}: {len(items)} {kind}(s) already supplied by an earlier --file were "
                                    f"ignored, not summed (overlapping exports?): {sorted(items)[:5]}")

    if bad_dates:
        warnings.append(f"{bad_dates} trend date value(s) could not be parsed and are kept as raw strings.")

    # Citation Share unit: '%' anywhere -> percent; all values <= 1 -> fraction (x100)
    share_unit = None
    if share_values:
        if any(p for _, p in share_values) or any(v > 1 for v, _ in share_values):
            share_unit, factor = "percent", 1
        else:
            share_unit, factor = "fraction_converted", 100
    for q in queries.values():
        raw = q.pop("citation_share_raw")
        q["citation_share_pct"] = round(raw * factor, 2) if raw is not None and share_unit else None

    # Totals
    trend_list = sorted(trend.values(), key=lambda t: t["date"])
    pages_sum = sum(p["citations"] or 0 for p in pages.values()) if pages else None
    queries_sum = sum(q["citations"] or 0 for q in queries.values()) if queries else None
    totals = {"total_citations": None, "avg_cited_pages": None, "days": len(trend_list) or None,
              "date_range": None, "total_citations_basis": None,
              "pages_table_citations_sum": pages_sum, "queries_table_citations_sum": queries_sum}
    if trend_list:
        # Assumption (not documented by Bing): Total Citations = sum of daily citations,
        # Avg. Cited Pages = mean of daily unique cited pages, rounded half up.
        daily_cit = [t["citations"] for t in trend_list if t["citations"] is not None]
        daily_cp = [t["cited_pages"] for t in trend_list if t["cited_pages"] is not None]
        totals["total_citations"] = sum(daily_cit) if daily_cit else None
        totals["avg_cited_pages"] = _js_round(sum(daily_cp) / len(daily_cp)) if daily_cp else None
        totals["total_citations_basis"] = "sum_of_daily_trend" if daily_cit else None
        iso = [t["date"] for t in trend_list if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(t["date"]))]
        totals["date_range"] = {"start": iso[0], "end": iso[-1]} if iso else None
        if not daily_cp:
            warnings.append("Trend export has no cited-pages column; avg_cited_pages is null.")
    elif pages_sum is not None or queries_sum is not None:
        use_pages = pages_sum is not None
        totals["total_citations"] = pages_sum if use_pages else queries_sum
        totals["total_citations_basis"] = "sum_of_pages_table" if use_pages else "sum_of_queries_table"
        warnings.append("No trend export supplied: total_citations is summed from the "
                        f"{'pages' if use_pages else 'queries'} table. Bing notes totals may differ across "
                        "views, and exports reflect the active filter. avg_cited_pages needs the trend export.")

    # Top lists
    page_list = sorted(pages.values(), key=lambda p: p["citations"] or 0, reverse=True)
    for p in page_list:
        p["share_of_citations_pct"] = (round(p["citations"] / pages_sum * 100, 2)
                                       if pages_sum and p["citations"] is not None else None)
    query_list = sorted(queries.values(), key=lambda q: q["citations"] or 0, reverse=True)

    def breakdown(field):
        if not any(q[field] for q in query_list):
            return None
        out = {}
        for q in query_list:
            for label in q[field]:
                out[label] = out.get(label, 0) + (q["citations"] or 0)
        return dict(sorted(out.items(), key=lambda kv: kv[1], reverse=True))

    # Trend summary: equal halves, only with >= 14 days
    trend_summary = None
    if trend_list:
        n = len(trend_list)
        if n >= 14:
            half = n // 2
            first = sum(t["citations"] or 0 for t in trend_list[:half])
            second = sum(t["citations"] or 0 for t in trend_list[-half:])
            trend_summary = {"days_per_half": half, "first_half_citations": first,
                             "second_half_citations": second,
                             "change_pct": round((second - first) / first * 100, 1) if first else None}
        else:
            trend_summary = {"days_per_half": None, "first_half_citations": None,
                             "second_half_citations": None, "change_pct": None,
                             "note": f"Only {n} day(s) of trend data; change needs 14 or more."}

    compare = None
    if compare_rows:
        with_diff = [r for r in compare_rows if r["diff_citations"] is not None]
        compare = {
            "dimension": compare_dim,
            "rows": len(compare_rows),
            "top_gainers": sorted([r for r in with_diff if r["diff_citations"] > 0],
                                  key=lambda r: r["diff_citations"], reverse=True)[:top],
            "top_losers": sorted([r for r in with_diff if r["diff_citations"] < 0],
                                 key=lambda r: r["diff_citations"])[:top],
        }

    data = {
        "site_url": site_url,
        "source_files": source_files,
        "totals": totals,
        "top_cited_pages": page_list[:top],
        "top_grounding_queries": query_list[:top],
        "intent_breakdown": breakdown("intent"),
        "topic_breakdown": breakdown("topic"),
        "trend": trend_list,
        "trend_summary": trend_summary,
        "compare": compare,
        "counts": {"unique_pages": len(pages), "unique_queries": len(queries), "trend_days": len(trend_list)},
        "notes": [
            "Source: user-exported Bing Webmaster Tools AI Performance report (no public API exists). "
            "Surfaces: Microsoft Copilot, AI-generated summaries in Bing, select partner AI integrations.",
            "All AI Performance data is sampled; totals may differ across views (pages, grounding "
            "queries, time series) and views may be sampled over slightly different time windows "
            "(Bing help: https://www.bing.com/webmasters/help/ai-performance-9f8e7d6c).",
            "Exports reflect the filter applied in the UI when exported: do not sum filtered "
            "exports as site totals.",
            "Citations do not indicate ranking, authority, or the role of a page within an answer (Bing).",
            "Export column names and the UI-card equivalence of totals are unverified assumptions.",
            "Not a backlink metric: keep it out of the Backlink Health Score.",
        ],
        "warnings": warnings,
    }
    ok = tables_recognized > 0
    return {
        "status": "success" if ok else "error",
        "data": data,
        "error": None if ok else "No AI Performance table recognized in the supplied file(s). "
                                 "See data.source_files and data.warnings for the headers found.",
        "metadata": {"source": AI_PERF_SOURCE, "parser": "tolerant-header-v1",
                     "citation_share_unit": share_unit, "timestamp": _now()},
    }


def _print_ai_performance(data: dict):
    t = data["totals"]
    print(f"Bing AI Performance export{' for ' + data['site_url'] if data.get('site_url') else ''}")
    if t.get("date_range"):
        print(f"  Period: {t['date_range']['start']} to {t['date_range']['end']} ({t['days']} days)")
    print(f"  Total citations:  {t.get('total_citations')}  (basis: {t.get('total_citations_basis')})")
    print(f"  Avg. cited pages: {t.get('avg_cited_pages')}")
    ts = data.get("trend_summary") or {}
    if ts.get("change_pct") is not None:
        print(f"  Second-half vs first-half citations: {ts['change_pct']:+}%")
    if data["top_cited_pages"]:
        print("\n  Top cited pages:")
        for p in data["top_cited_pages"][:10]:
            print(f"    {str(p['citations']):>8}  {p['page']}")
    if data["top_grounding_queries"]:
        print("\n  Top grounding queries (sample):")
        for q in data["top_grounding_queries"][:10]:
            share = f"  share {q['citation_share_pct']}%" if q.get("citation_share_pct") is not None else ""
            print(f"    {str(q['citations']):>8}  {q['query']}{share}")
    for w in data.get("warnings", []):
        print(f"  Warning: {w}", file=sys.stderr)


def _emit(result: dict, as_json: bool):
    if as_json:
        print(json.dumps(result, indent=2, default=str))
    elif result.get("error"):
        print(f"Error: {result['error']}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        description="Bing Webmaster Tools client for Claude SEO (link API + AI Performance export parser)"
    )
    parser.add_argument(
        "command",
        choices=["links", "counts", "compare", "ai-performance"],
        help="links (inbound), counts (totals), compare (two sites, both verified in your account), "
             "ai-performance (parse a user-exported AI Performance CSV/XLSX; no API key, offline)",
    )
    parser.add_argument("url", nargs="?", default=None,
                        help="Target site URL (required for API commands; optional label for ai-performance)")
    parser.add_argument("competitor_url", nargs="?", default=None,
                        help="Second site URL for 'compare' (must also be verified in your Bing account)")
    parser.add_argument("--page", type=int, default=0, help="Page number for pagination (default: 0)")
    parser.add_argument("--detail-pages", type=int, default=DEFAULT_DETAIL_PAGES,
                        help=f"links: target pages to expand with GetUrlLinks (default: {DEFAULT_DETAIL_PAGES})")
    parser.add_argument("--file", action="append", default=[],
                        help="ai-performance: path to a CSV/TSV/XLSX exported from Bing Webmaster Tools "
                             "> AI Performance (CSV or Excel export; repeatable: queries, pages, trend)")
    parser.add_argument("--top", type=int, default=20,
                        help="ai-performance: number of top pages/queries to return (default: 20)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()
    target = args.url

    # Validate URLs (SSRF protection)
    for label, value in (("URL", target), ("competitor URL", args.competitor_url)):
        if value and value.startswith("http") and not validate_url(value):
            _emit(_error(f"Invalid or blocked {label}: {value}"), args.json)
            sys.exit(1)

    if args.command == "ai-performance":
        if not args.file:
            _emit(_error("ai-performance requires at least one --file (CSV/XLSX exported from "
                         "Bing Webmaster Tools > AI Performance)", AI_PERF_SOURCE), args.json)
            sys.exit(1)
        missing = [f for f in args.file if not os.path.isfile(f)]
        if missing:
            _emit(_error(f"File(s) not found: {', '.join(missing)}", AI_PERF_SOURCE), args.json)
            sys.exit(1)
        result = parse_ai_performance(args.file, site_url=target, top=max(args.top, 1))
        if args.json:
            _emit(result, True)
        elif result["status"] == "success":
            _print_ai_performance(result["data"])
        else:
            _emit(result, False)
            for w in result["data"]["warnings"]:
                print(f"  {w}", file=sys.stderr)
        sys.exit(0 if result["status"] == "success" else 1)

    if not target:
        _emit(_error(f"The '{args.command}' command requires a site URL"), args.json)
        sys.exit(1)
    if args.command == "compare" and not args.competitor_url:
        _emit(_error("compare command requires a competitor URL"), args.json)
        sys.exit(1)

    api_key = get_bing_api_key()
    if not api_key:
        _emit(_error("No Bing Webmaster API key configured. Run: python scripts/backlinks_auth.py --setup"),
              args.json)
        sys.exit(1)

    # Warn if site not in verified list
    verified = get_bing_verified_sites()
    parsed_target = urlparse(target if target.startswith("http") else f"https://{target}")
    if verified and parsed_target.netloc not in verified and parsed_target.netloc.replace("www.", "") not in verified:
        print(f"Warning: {parsed_target.netloc} not in bing_verified_sites config. API may return limited data.",
              file=sys.stderr)

    if args.command == "links":
        result = get_link_details(target, api_key, page=args.page, detail_pages=args.detail_pages)
    elif args.command == "counts":
        result = get_link_counts(target, api_key)
    else:
        result = compare_links(target, args.competitor_url, api_key)

    if args.json:
        _emit(result, True)
    elif result["status"] == "success" and result["data"]:
        data = result["data"]
        if args.command == "links":
            print(f"Bing Inbound Links for: {data.get('site_url', target)} ({data.get('total_returned', 0)} returned)")
            for link in data.get("links", [])[:20]:
                anchor = (link.get("anchor_text") or "")[:40]
                print(f"  {link.get('source_url', '?'):60s} -> {link.get('target_url', '')} [{anchor}]")
        elif args.command == "counts":
            print(f"Bing Link Counts for: {data.get('site_url', target)}")
            print(f"  Pages with inbound links (sample): {data.get('pages_with_links_sample', 'N/A')}")
            print(f"  Inbound links (sample):            {data.get('inbound_links_sample', 'N/A')}")
        elif args.command == "compare":
            print(f"Backlink Gap: {data.get('site_url', '')} vs {data.get('competitor_url', '')}")
            print(f"  Your linking domains:       {data.get('your_linking_domains', 0)}")
            print(f"  Competitor linking domains:  {data.get('competitor_linking_domains', 0)}")
            print(f"  Gap (they have, you don't): {data.get('gap_count', 0)}")
            print(f"  Shared:                     {data.get('shared_count', 0)}")
            print(f"  Unique to you:              {data.get('unique_count', 0)}")
            if data.get("gap_domains"):
                print("\n  Top gap domains:")
                for d in data["gap_domains"][:10]:
                    print(f"    {d}")
    else:
        _emit(result, False)
        errs = (result.get("data") or {}).get("errors") if isinstance(result.get("data"), dict) else None
        for label, msg in (errs or {}).items():
            print(f"  {label}: {msg}", file=sys.stderr)
    if result["status"] != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()
