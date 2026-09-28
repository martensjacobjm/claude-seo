"""Tests for free_keyword_data.py: merging, flags, units, degradation (no network)."""

import datetime
import json

import pytest

import free_keyword_data as fk


def _ms(y, m, d):
    ms = int(datetime.datetime(y, m, d, tzinfo=datetime.timezone.utc).timestamp() * 1000)
    return f"/Date({ms}-0700)/"


@pytest.fixture
def nothing_configured(monkeypatch):
    for name in ("_gsc_status", "_bing_status", "_kp_status"):
        monkeypatch.setattr(fk, name, lambda: {"configured": False, "reason": "not set up"})
    monkeypatch.setattr(fk, "_wiki_status", lambda: {"configured": True, "reason": None})


def _on(monkeypatch, *names):
    for name in names:
        monkeypatch.setattr(fk, name, lambda: {"configured": True, "reason": None})


# ---- pure helpers ---------------------------------------------------------

def test_normalize_query_and_ctr():
    assert fk.normalize_query("  Running   SHOES ") == "running shoes"
    assert fk.ctr_pct(5, 200) == 2.5
    assert fk.ctr_pct(0, 0) is None


def test_parse_ms_date_handles_offset_and_garbage():
    assert fk.parse_ms_date(_ms(2026, 9, 5)) == datetime.date(2026, 9, 5)
    assert fk.parse_ms_date("nope") is None


def test_site_to_bing_url_and_ssrf_check():
    assert fk.site_to_bing_url("sc-domain:example.com") == "https://example.com/"
    assert fk.site_to_bing_url("https://www.example.com/blog/") == "https://www.example.com/"
    assert fk.check_site("sc-domain:example.com") is None
    assert fk.check_site("http://127.0.0.1/") is not None
    assert fk.check_site("http://10.0.0.5") is not None


def test_month_window_complete_months():
    s, e = fk.month_window(3, today=datetime.date(2026, 2, 15))
    assert (s, e) == (datetime.date(2025, 11, 1), datetime.date(2026, 1, 31))


def test_flag_opportunities_striking_and_low_ctr():
    rows = [
        {"query": f"q{i}", "impressions": 1000, "clicks": 50, "ctr_pct": 5.0, "position": 6.0}
        for i in range(3)
    ] + [
        {"query": "weak", "impressions": 1000, "clicks": 10, "ctr_pct": 1.0, "position": 7.0},
        {"query": "top", "impressions": 1000, "clicks": 300, "ctr_pct": 30.0, "position": 1.2},
        {"query": "rare", "impressions": 20, "clicks": 0, "ctr_pct": 0.0, "position": 8.0},
        {"query": "deep", "impressions": 500, "clicks": 1, "ctr_pct": 0.2, "position": 35.0},
    ]
    baseline = fk.flag_opportunities(rows, min_impressions=100)
    by = {r["query"]: r["flags"] for r in rows}
    assert baseline == {"4-10": 5.0}
    assert by["weak"] == ["striking_distance", "low_ctr"]
    assert by["q0"] == ["striking_distance"]
    assert by["top"] == []          # position 1-3: not striking distance, bucket has < 3 rows
    assert by["rare"] == []         # below impression threshold
    assert by["deep"] == []         # beyond position 20


def test_merge_keeps_positions_per_engine_and_sums_counts():
    gsc = [{"query": "Running Shoes", "clicks": 10, "impressions": 100, "ctr_pct": 10.0,
            "position": 5.0, "flags": ["striking_distance"]}]
    bing = [{"query": "running  shoes", "clicks": 2, "impressions": 50, "ctr_pct": 4.0,
             "position": 3.0, "flags": []},
            {"query": "bing only", "clicks": 0, "impressions": 10, "ctr_pct": 0.0,
             "position": 9.0, "flags": []}]
    merged = fk.merge_query_rows(gsc, bing)
    top = merged[0]
    assert top["query"] == "running shoes"
    assert top["source"] == "bing_webmaster+gsc"
    assert top["combined"]["clicks"] == 12 and top["combined"]["impressions"] == 150
    assert top["combined"]["ctr_pct"] == 8.0
    assert "position" not in top["combined"]
    assert top["gsc"]["position"] == 5.0 and top["bing_webmaster"]["position"] == 3.0
    assert top["flags"] == ["striking_distance:gsc"]
    assert merged[1]["source"] == "bing_webmaster" and merged[1]["gsc"] is None


def test_aggregate_bing_query_stats_window_and_weighted_position():
    raw = [
        {"Query": "a", "Clicks": 1, "Impressions": 100, "AvgImpressionPosition": 4, "Date": _ms(2026, 9, 5)},
        {"Query": "a", "Clicks": 3, "Impressions": 300, "AvgImpressionPosition": 8, "Date": _ms(2026, 9, 12)},
        {"Query": "a", "Clicks": 9, "Impressions": 900, "AvgImpressionPosition": 1, "Date": _ms(2026, 6, 1)},
        {"Query": "b", "Clicks": 0, "Impressions": 50, "AvgImpressionPosition": -1, "Date": _ms(2026, 9, 12)},
    ]
    out = fk.aggregate_bing_query_stats(raw, datetime.date(2026, 9, 1), datetime.date(2026, 9, 20))
    a = next(r for r in out if r["query"] == "a")
    assert a["clicks"] == 4 and a["impressions"] == 400 and a["weeks"] == 2
    assert a["position"] == 7.0  # (4*100 + 8*300) / 400
    b = next(r for r in out if r["query"] == "b")
    assert b["position"] is None and b["source"] == "bing_webmaster"


def test_group_volumes_never_mixes_units():
    rows = [
        {"keyword": "Shoes", "source": "google_ads_keyword_planner", "value": 1000,
         "unit": "google_searches_per_month_avg_12m"},
        {"keyword": "shoes", "source": "bing_webmaster", "value": 80,
         "unit": "bing_impressions_last_4_weeks"},
        {"keyword": "socks", "source": "bing_webmaster", "value": 5,
         "unit": "bing_impressions_last_4_weeks"},
    ]
    g = {x["keyword"]: x for x in fk.group_volumes(rows)}
    assert len(g["shoes"]["values"]) == 2 and g["shoes"]["comparable"] is False
    assert "total" not in g["shoes"] and g["socks"]["comparable"] is True


# ---- commands with mocked sources ------------------------------------------

def test_sources_report_lists_every_source_with_setup(nothing_configured):
    rep = fk.sources_report()
    names = {r["source"] for r in rep["rows"]}
    assert names == {"gsc", "bing_webmaster", "google_ads_keyword_planner",
                     "google_trends_api", "wikimedia_pageviews"}
    for r in rep["rows"]:
        assert r["setup"] and r["docs"].startswith("https://") and r["checked"] == fk.CHECKED
    assert rep["configured"] == ["wikimedia_pageviews"]
    assert any("scraping" in n for n in rep["notes"])


def test_own_queries_without_sources_degrades(nothing_configured):
    res = fk.cmd_own_queries("sc-domain:example.com")
    assert res["status"] == "no_data"
    assert {s["source"] for s in res["skipped"]} == {"gsc", "bing_webmaster"}
    assert all(s["setup"] for s in res["skipped"]) and res["notes"]


def test_own_queries_gsc_only_partial(monkeypatch, nothing_configured):
    _on(monkeypatch, "_gsc_status")
    calls = []

    def fake_gsc(site, start, end, dimension, limit, page=None):
        calls.append(dimension)
        if dimension == "query":
            return {"rows": [{"query": "shoes", "clicks": 5, "impressions": 500, "ctr_pct": 1.0,
                              "position": 9.0, "source": "gsc"}], "error": None}
        return {"rows": [{"page": "https://example.com/", "clicks": 5, "impressions": 500,
                          "ctr_pct": 1.0, "position": 9.0, "source": "gsc"}], "error": None}

    monkeypatch.setattr(fk, "fetch_gsc", fake_gsc)
    monkeypatch.setattr(fk, "fetch_bing_own", lambda *a, **k: pytest.fail("bing not configured"))
    res = fk.cmd_own_queries("sc-domain:example.com")
    assert calls == ["query", "page"]
    assert res["status"] == "partial"
    assert res["queries"][0]["source"] == "gsc"
    assert res["opportunities"][0]["flags"] == ["striking_distance:gsc"]
    assert res["pages"][0]["source"] == "gsc"
    assert res["heuristics"]["label"] == "heuristic"


def test_ideas_rows_carry_source_and_unit(monkeypatch, nothing_configured):
    _on(monkeypatch, "_kp_status", "_bing_status")
    monkeypatch.setattr(fk, "fetch_kp_ideas", lambda *a: {"ideas": [
        {"keyword": "trail shoes", "avg_monthly_searches": 1000, "competition": "HIGH"}],
        "error": None})
    monkeypatch.setattr(fk, "fetch_bing_related", lambda seed, *a: {"status": "success", "data": [
        {"Query": "trail running shoes", "Impressions": 420, "BroadImpressions": 900}]})
    res = fk.cmd_ideas(["trail shoes"])
    assert res["status"] == "ok"
    srcs = {r["source"]: r for r in res["rows"]}
    assert srcs["google_ads_keyword_planner"]["unit"] == "google_searches_per_month_avg_12m"
    assert srcs["bing_webmaster"]["unit"] == "bing_impressions_in_period"
    assert srcs["bing_webmaster"]["broad_impressions"] == 900
    assert all(r["volume_semantics"] for r in res["rows"])


def test_ideas_bing_error_is_reported_not_raised(monkeypatch, nothing_configured):
    _on(monkeypatch, "_bing_status")
    monkeypatch.setattr(fk, "fetch_bing_related",
                        lambda *a: {"status": "error", "error": "Invalid Bing Webmaster API key"})
    res = fk.cmd_ideas(["x"])
    assert res["status"] == "no_data"
    assert res["errors"][0]["source"] == "bing_webmaster"
    assert res["skipped"][0]["source"] == "google_ads_keyword_planner"


def test_volume_units_per_source_and_bing_week_sum(monkeypatch, nothing_configured):
    _on(monkeypatch, "_kp_status", "_bing_status")
    monkeypatch.setattr(fk, "fetch_kp_volumes", lambda *a: {"keywords": [
        {"keyword": "shoes", "avg_monthly_searches": 5000, "competition": "LOW"}], "error": None})
    weekly = [{"Query": "shoes", "Impressions": i * 10, "BroadImpressions": i * 20,
               "Date": _ms(2026, 8, 1 + 7 * i)} for i in range(4)]
    monkeypatch.setattr(fk, "fetch_bing_keyword_stats",
                        lambda *a: {"status": "success", "data": list(reversed(weekly))})
    res = fk.cmd_volume(["shoes"], weeks=2)
    bing = next(r for r in res["rows"] if r["source"] == "bing_webmaster")
    assert bing["value"] == 20 + 30 and bing["unit"] == "bing_impressions_last_2_weeks"
    assert bing["weekly"][0]["week"] == "2026-08-01"  # sorted oldest first
    grp = res["by_keyword"][0]
    assert grp["comparable"] is False and len(grp["units"]) == 2
    json.dumps(res)  # serialisable


def test_volume_wikipedia_proxy_is_labelled(monkeypatch, nothing_configured):
    monkeypatch.setattr(fk, "fetch_wikipedia", lambda kw, proj, months: {
        "article": "Running shoe", "error": None,
        "series": [{"month": "202607", "views": 100}, {"month": "202608", "views": 300}]})
    res = fk.cmd_volume(["running shoes"], wikipedia=True)
    row = res["rows"][0]
    assert row["source"] == "wikimedia_pageviews" and row["value"] == 200
    assert "HEURISTIC" in row["volume_semantics"] and row["matched_article"] == "Running shoe"
    assert res["status"] == "partial"


def test_trends_not_available(monkeypatch, nothing_configured):
    monkeypatch.setattr(fk, "fetch_wikipedia", lambda *a: pytest.fail("not requested"))
    res = fk.cmd_trends(["shoes"])
    assert res["status"] == "not_available" and res["rows"] == []
    assert "alpha" in res["reason"] and res["setup"].startswith("Apply at https://")


def test_cli_exit_codes(capsys, nothing_configured):
    assert fk.main(["sources", "--json"]) == 0
    out = json.loads(capsys.readouterr().out)
    assert out["command"] == "sources"
    assert fk.main(["volume", "shoes", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["status"] == "no_data"
    assert fk.main(["own-queries", "http://192.168.1.1/", "--json"]) == 1
    assert "non-public" in json.loads(capsys.readouterr().out)["error"]
