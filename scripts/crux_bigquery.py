#!/usr/bin/env python3
"""
CrUX on BigQuery: monthly Core Web Vitals history and competitor benchmarks.

Queries the public Chrome UX Report dataset on BigQuery
(`chrome-ux-report.materialized.metrics_summary` / `device_summary`) for one
origin (or several, in benchmark mode) and returns monthly p75 LCP/INP/CLS plus
the good / needs-improvement / poor traffic shares per metric.

Unlike the CrUX API (28-day rolling) and the CrUX History API (25 weeks), the
BigQuery dataset holds one row per origin per month going back to 2017, and one
query can compare many origins at once.

Costs: queries run as jobs in YOUR Google Cloud billing project. BigQuery
on-demand pricing gives the first 1 TiB processed per month free, then
$6.25/TiB, with a 10 MB minimum per query (cloud.google.com/bigquery/pricing).
Always run with --dry-run first to see the bytes estimate.

Data freshness: a new monthly dataset is released on the second Tuesday of the
following month (developer.chrome.com/docs/crux/release-notes).

Auth: service account (`service_account_path` in ~/.config/claude-seo/google-api.json)
or Application Default Credentials (`gcloud auth application-default login`).
The claude-seo OAuth token is NOT used: its scopes do not include BigQuery.
The identity needs roles/bigquery.jobUser on the billing project.

Usage:
    python crux_bigquery.py example.com --print-sql              # SQL only, offline
    python crux_bigquery.py example.com --dry-run --json          # bytes estimate
    python crux_bigquery.py https://example.com --json            # all devices, 12 months
    python crux_bigquery.py example.com --device phone --months 6 --json
    python crux_bigquery.py example.com --both-devices --json     # phone + desktop
    python crux_bigquery.py example.com --compare a.com b.com --json
    python crux_bigquery.py example.com --project my-gcp-project --json
"""

import argparse
import datetime
import json
import os
import sys
from typing import Optional
from urllib.parse import urlparse

try:
    from google_auth import load_config, get_service_account_credentials, validate_url
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from google_auth import load_config, get_service_account_credentials, validate_url

DATASET = "chrome-ux-report.materialized"
TABLES = {"all": "metrics_summary", "device": "device_summary"}
DEVICES = ("phone", "desktop", "tablet")
BQ_SCOPE = "https://www.googleapis.com/auth/bigquery"
MAX_COMPETITORS = 10
DEFAULT_MAX_BYTES_BILLED = 10 * 1024 ** 3  # 10 GiB safety cap per query
INSTALL_HINT = "pip install 'google-cloud-bigquery>=3.40.0,<4.0.0'"
PRICING_NOTE = (
    "First 1 TiB/month of query processing is free, then $6.25/TiB on-demand "
    "(cloud.google.com/bigquery/pricing); minimum 10 MB billed per query."
)

# (good_max, poor_min) at p75. Same values as crux_history.py / web.dev/articles/vitals.
THRESHOLDS = {"lcp": (2500, 4000), "inp": (200, 500), "cls": (0.1, 0.25)}
# Materialized-table column prefixes for the good / NI / poor buckets.
BUCKETS = {
    "lcp": ("fast_lcp", "avg_lcp", "slow_lcp"),
    "inp": ("fast_inp", "avg_inp", "slow_inp"),
    "cls": ("small_cls", "medium_cls", "large_cls"),
}


def normalize_origin(raw: str) -> str:
    """
    Turn user input into a CrUX origin (scheme://host[:port], no path).

    Raises:
        ValueError: if the URL is not a public http/https URL (validate_url()).
    """
    raw = (raw or "").strip()
    if "://" not in raw:
        raw = "https://" + raw
    if not validate_url(raw):
        raise ValueError(
            f"Invalid origin '{raw}'. Only http/https URLs to public hosts are accepted."
        )
    parsed = urlparse(raw)
    netloc = parsed.hostname.lower()
    # CrUX origins never carry the scheme's default port.
    if parsed.port and (parsed.scheme, parsed.port) not in (("https", 443), ("http", 80)):
        netloc += f":{parsed.port}"
    return f"{parsed.scheme}://{netloc}"


def start_date(months: int, today: Optional[datetime.date] = None) -> datetime.date:
    """First day of the month `months` months before `today`."""
    today = today or datetime.date.today()
    year, month = today.year, today.month - months
    while month <= 0:
        month += 12
        year -= 1
    return datetime.date(year, month, 1)


def build_sql(by_device: bool) -> str:
    """
    Build the parameterised SQL. Origins, devices and dates are passed as
    BigQuery query parameters, never interpolated into the SQL string.
    """
    table = f"`{DATASET}.{TABLES['device' if by_device else 'all']}`"
    cols = ["yyyymm", "origin"] + (["device"] if by_device else [])
    cols += ["p75_lcp", "p75_inp", "p75_cls"]
    for name, (good, ni, poor) in BUCKETS.items():
        total = f"({good} + {ni} + {poor})"
        cols += [
            f"SAFE_DIVIDE({good}, {total}) AS good_{name}",
            f"SAFE_DIVIDE({ni}, {total}) AS ni_{name}",
            f"SAFE_DIVIDE({poor}, {total}) AS poor_{name}",
        ]
    where = ["date >= @start_date", "origin IN UNNEST(@origins)"]
    if by_device:
        where.append("device IN UNNEST(@devices)")
    order = "origin, " + ("device, " if by_device else "") + "yyyymm DESC"
    return (
        "SELECT\n  " + ",\n  ".join(cols)
        + f"\nFROM\n  {table}\nWHERE\n  " + "\n  AND ".join(where)
        + f"\nORDER BY {order}"
    )


def plan_query(origins: list, devices: Optional[list], months: int,
               today: Optional[datetime.date] = None) -> dict:
    """Return the SQL and a plain-dict description of its parameters."""
    params = {
        "start_date": start_date(months, today).isoformat(),
        "origins": origins,
    }
    if devices:
        params["devices"] = devices
    return {"sql": build_sql(bool(devices)), "parameters": params}


def _bq_parameters(bigquery, params: dict) -> list:
    """Convert the parameter dict into BigQuery query parameter objects."""
    out = [
        bigquery.ScalarQueryParameter(
            "start_date", "DATE", datetime.date.fromisoformat(params["start_date"])
        ),
        bigquery.ArrayQueryParameter("origins", "STRING", params["origins"]),
    ]
    if "devices" in params:
        out.append(bigquery.ArrayQueryParameter("devices", "STRING", params["devices"]))
    return out


def resolve_project(cli_project: Optional[str], config: dict) -> Optional[str]:
    """Billing project precedence: flag > config > env > service-account file."""
    if cli_project:
        return cli_project
    if config.get("bigquery_project_id"):
        return config["bigquery_project_id"]
    if os.environ.get("GOOGLE_CLOUD_PROJECT"):
        return os.environ["GOOGLE_CLOUD_PROJECT"]
    sa_path = config.get("service_account_path")
    if sa_path:
        try:
            with open(os.path.expanduser(sa_path), "r") as f:
                return json.load(f).get("project_id")
        except (OSError, json.JSONDecodeError):
            return None
    return None


def get_client(cli_project: Optional[str]):
    """
    Build a BigQuery client. Returns (client, None) or (None, error message).
    """
    try:
        from google.cloud import bigquery
    except ImportError:
        return None, f"google-cloud-bigquery not installed. Install with: {INSTALL_HINT}"

    config = load_config()
    project = resolve_project(cli_project, config)
    credentials = None
    if config.get("service_account_path"):
        credentials = get_service_account_credentials([BQ_SCOPE])
    if credentials is None:
        try:
            import google.auth
            credentials, adc_project = google.auth.default(scopes=[BQ_SCOPE])
            project = project or adc_project
        except Exception as e:  # DefaultCredentialsError and friends
            return None, (
                "No BigQuery credentials. Configure `service_account_path` in "
                "~/.config/claude-seo/google-api.json or run "
                f"`gcloud auth application-default login`. ({e})"
            )
    if not project:
        return None, (
            "No billing project. BigQuery bills queries to the project that runs "
            "them. Pass --project, set `bigquery_project_id` in "
            "~/.config/claude-seo/google-api.json, or set GOOGLE_CLOUD_PROJECT. "
            "The identity needs roles/bigquery.jobUser on that project."
        )
    try:
        return bigquery.Client(project=project, credentials=credentials), None
    except Exception as e:
        return None, f"Could not create BigQuery client: {e}"


def _num(value):
    """Coerce BigQuery numeric values (possibly Decimal/str) to float."""
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def rate(metric: str, p75) -> Optional[str]:
    """Good / Needs Improvement / Poor for a p75 value."""
    if p75 is None:
        return None
    good, poor = THRESHOLDS[metric]
    if p75 <= good:
        return "Good"
    if p75 > poor:
        return "Poor"
    return "Needs Improvement"


def shape_row(row: dict) -> dict:
    """Convert one result row into the output record."""
    rec = {"yyyymm": int(row["yyyymm"]) if row.get("yyyymm") is not None else None}
    if "device" in row:
        rec["device"] = row["device"]
    rec["p75"] = {m: _num(row.get(f"p75_{m}")) for m in THRESHOLDS}
    for m in THRESHOLDS:
        rec[m] = {
            "good": _num(row.get(f"good_{m}")),
            "ni": _num(row.get(f"ni_{m}")),
            "poor": _num(row.get(f"poor_{m}")),
            "rating": rate(m, rec["p75"][m]),
        }
    # INP may be missing for low-interaction origins: assess on LCP + CLS then.
    required = ["lcp", "cls"] + ([] if rec["p75"]["inp"] is None else ["inp"])
    rec["inp_missing"] = rec["p75"]["inp"] is None
    rec["cwv_pass"] = (
        all(rec[m]["rating"] == "Good" for m in required)
        if rec["p75"]["lcp"] is not None and rec["p75"]["cls"] is not None
        else None
    )
    return rec


def build_benchmark(target: str, rows_by_origin: dict) -> dict:
    """Compare origins on the latest month (and device) they all share."""
    keyed = {}
    for origin, rows in rows_by_origin.items():
        for r in rows:
            keyed.setdefault((r["yyyymm"], r.get("device", "all")), {})[origin] = r
    common = [k for k, v in keyed.items() if len(v) == len(rows_by_origin)]
    if not common:
        return {"error": "No month where all origins have CrUX data."}
    latest_month = max(k[0] for k in common)
    out = {"yyyymm": latest_month, "by_device": {}}
    for key in sorted(k for k in common if k[0] == latest_month):
        entries = keyed[key]
        table = {}
        for metric in THRESHOLDS:
            vals = [e["p75"][metric] for e in entries.values() if e["p75"][metric] is not None]
            # Competition ranking (1 + origins strictly better): equal coarse p75
            # values share a rank instead of being split alphabetically.
            ranks = {
                o: 1 + sum(1 for x in vals if x < e["p75"][metric])
                for o, e in entries.items() if e["p75"][metric] is not None
            }
            tgt = entries.get(target, {}).get("p75", {}).get(metric)
            for o, e in entries.items():
                v = e["p75"][metric]
                table.setdefault(o, {"cwv_pass": e["cwv_pass"]})[metric] = {
                    "p75": v,
                    "good_share": e[metric]["good"],
                    "rank": ranks.get(o),
                    "tied": (v is not None and sum(1 for x in vals if x == v) > 1),
                    "delta_vs_target": (v - tgt) if v is not None and tgt is not None else None,
                }
        out["by_device"][key[1]] = table
    return out


def run(args) -> dict:
    """Execute the command described by parsed args and return a result dict."""
    result = {
        "source": None,
        "origin": None,
        "device": args.device or "all",
        "months": args.months,
        "error": None,
    }
    try:
        origin = normalize_origin(args.origin)
        competitors = [normalize_origin(c) for c in (args.compare or [])]
        # The target is always queried; keep it out of the competitor list.
        competitors = [c for c in dict.fromkeys(competitors) if c != origin]
    except ValueError as e:
        result["error"] = str(e)
        return result
    if len(competitors) > MAX_COMPETITORS:
        result["error"] = f"Too many competitors (max {MAX_COMPETITORS})."
        return result

    origins = list(dict.fromkeys([origin] + competitors))
    if args.both_devices:
        devices = ["phone", "desktop"]
        result["device"] = "phone+desktop"
    elif args.device and args.device != "all":
        devices = [args.device]
    else:
        devices = None

    plan = plan_query(origins, devices, args.months)
    table = TABLES["device" if devices else "all"]
    result.update({
        "source": f"CrUX BigQuery ({DATASET}.{table})",
        "origin": origin,
        "compare": competitors,
        "start_date": plan["parameters"]["start_date"],
        "note": "www and non-www (and http/https) are distinct CrUX origins.",
    })

    if args.print_sql:
        result.update({"mode": "print_sql", **plan})
        return result

    client, err = get_client(args.project)
    if err:
        result["error"] = err
        return result

    from google.cloud import bigquery
    job_config = bigquery.QueryJobConfig(
        query_parameters=_bq_parameters(bigquery, plan["parameters"]),
        maximum_bytes_billed=args.max_bytes_billed,
    )
    try:
        if args.dry_run:
            job_config.dry_run = True
            job_config.use_query_cache = False
            job = client.query(plan["sql"], job_config=job_config)
            nbytes = job.total_bytes_processed or 0
            result.update({
                "mode": "dry_run",
                **plan,
                "billing_project": client.project,
                "total_bytes_processed": nbytes,
                "total_gib": round(nbytes / 1024 ** 3, 4),
                "free_tier_note": PRICING_NOTE,
            })
            return result
        job = client.query(plan["sql"], job_config=job_config)
        rows = [dict(r.items()) for r in job.result()]
        result["bytes_processed"] = job.total_bytes_processed
        result["billing_project"] = client.project
    except Exception as e:  # google.api_core exceptions: Forbidden, BadRequest, ...
        msg = str(e)
        if "bytes billed" in msg.lower():
            msg += " Raise --max-bytes-billed only after checking --dry-run."
        result["error"] = f"BigQuery error: {msg}"
        return result

    rows_by_origin = {o: [] for o in origins}
    for r in rows:
        rows_by_origin.setdefault(r["origin"], []).append(shape_row(r))
    result["rows_by_origin"] = rows_by_origin
    months_seen = [r["yyyymm"] for rs in rows_by_origin.values() for r in rs if r["yyyymm"]]
    result["latest_month"] = max(months_seen) if months_seen else None
    missing = [o for o, rs in rows_by_origin.items() if not rs]
    if missing:
        result["not_in_crux"] = missing
        result["not_in_crux_note"] = (
            "No rows: origin not in the CrUX dataset (insufficient Chrome traffic) "
            "or wrong origin variant (www / http)."
        )
    if competitors:
        present = {o: rs for o, rs in rows_by_origin.items() if rs}
        if origin in present and len(present) > 1:
            result["benchmark"] = build_benchmark(origin, present)
    return result


def _fmt(metric: str, v) -> str:
    if v is None:
        return "-"
    return f"{v:.2f}" if metric == "cls" else f"{int(v)}ms"


def print_human(result: dict) -> None:
    """Print a readable summary to stdout."""
    if result.get("error"):
        print(f"Error: {result['error']}")
        return
    mode = result.get("mode")
    if mode in ("print_sql", "dry_run"):
        print(result["sql"])
        print(f"\nParameters: {json.dumps(result['parameters'])}")
        if mode == "dry_run":
            print(f"Estimated bytes: {result['total_bytes_processed']:,} "
                  f"({result['total_gib']} GiB)\n{result['free_tier_note']}")
        return
    print(f"{result['source']}  since {result['start_date']}")
    for origin, rows in result["rows_by_origin"].items():
        print(f"\n{origin}")
        if not rows:
            print("  (no CrUX data)")
            continue
        print(f"  {'month':<8}{'device':<9}{'LCP':>9}{'INP':>9}{'CLS':>7}  CWV")
        for r in rows:
            cwv = {True: "pass", False: "fail", None: "-"}[r["cwv_pass"]]
            print(f"  {r['yyyymm']:<8}{r.get('device', 'all'):<9}"
                  f"{_fmt('lcp', r['p75']['lcp']):>9}{_fmt('inp', r['p75']['inp']):>9}"
                  f"{_fmt('cls', r['p75']['cls']):>7}  {cwv}")
    if result.get("benchmark", {}).get("by_device"):
        print(f"\nBenchmark ({result['benchmark']['yyyymm']}), rank 1 = best p75:")
        for device, table in result["benchmark"]["by_device"].items():
            for o, m in table.items():
                ranks = " ".join(
                    f"{k.upper()}#{m[k]['rank']}{'(tie)' if m[k].get('tied') else ''}"
                    for k in THRESHOLDS
                )
                print(f"  [{device}] {o}: {ranks}")


def main():
    parser = argparse.ArgumentParser(
        description="Monthly CrUX Core Web Vitals from BigQuery, with competitor benchmark."
    )
    parser.add_argument("origin", help="Origin or URL (path is dropped), e.g. example.com")
    device_group = parser.add_mutually_exclusive_group()
    device_group.add_argument("--device", choices=["all", "phone", "desktop", "tablet"],
                              default=None,
                              help="Device filter (default: all devices combined)")
    device_group.add_argument("--both-devices", action="store_true",
                              help="Phone and desktop rows in one query (device_summary)")
    parser.add_argument("--months", type=int, default=12,
                        help="Months of history, 1-60 (default: 12)")
    parser.add_argument("--compare", nargs="+", metavar="ORIGIN",
                        help=f"Competitor origins to benchmark (max {MAX_COMPETITORS})")
    parser.add_argument("--project",
                        help="Billing project (default: bigquery_project_id in config)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Estimate bytes processed without running the query")
    parser.add_argument("--print-sql", action="store_true",
                        help="Print SQL and parameters only (no credentials needed)")
    parser.add_argument("--max-bytes-billed", type=int, default=DEFAULT_MAX_BYTES_BILLED,
                        help=f"Fail the query above this many bytes (default: {DEFAULT_MAX_BYTES_BILLED})")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    if not 1 <= args.months <= 60:
        parser.error("--months must be between 1 and 60")

    result = run(args)
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print_human(result)
    sys.exit(1 if result.get("error") else 0)


if __name__ == "__main__":
    main()
