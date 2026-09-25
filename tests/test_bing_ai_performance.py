"""Tests for the Bing AI Performance export parser (synthetic fixtures)."""

import os

import bing_webmaster as bw
from conftest import FIXTURES

DIR = os.path.join(FIXTURES, "bing-ai-performance")
ALL = [os.path.join(DIR, f) for f in ("trend.csv", "pages.csv", "queries.csv")]


def _write(tmp_path, name, text):
    p = tmp_path / name
    p.write_text(text, encoding="utf-8")
    return str(p)


def test_parses_all_three_exports():
    res = bw.parse_ai_performance(ALL, site_url="example.com")
    assert res["status"] == "success"
    data = res["data"]
    assert [f["type"] for f in data["source_files"]] == ["trend", "pages", "queries"]
    assert data["totals"]["total_citations"] == 56
    assert data["top_cited_pages"][0]["page"].endswith("/guides/heat-pump-sizing")
    assert data["warnings"] == []


def test_title_row_above_header_is_skipped():
    data = bw.parse_ai_performance([ALL[0]])["data"]
    assert data["source_files"][0]["columns_mapped"]["date"] == "Date"
    assert data["counts"]["trend_days"] == 4


def test_percent_share_and_multi_label_intent():
    data = bw.parse_ai_performance([ALL[2]])["data"]
    q = {r["query"]: r for r in data["top_grounding_queries"]}
    assert q["how to size a heat pump"]["citation_share_pct"] == 8.0
    assert q["waive home inspection risks"]["intent"] == ["Informational", "Commercial"]
    assert data["intent_breakdown"] == {"Informational": 29, "Commercial": 6}


def test_fraction_share_is_converted_to_percent(tmp_path):
    path = _write(tmp_path, "q.csv", "Grounding queries,Citations,Citation rate\nfoo,3,0.125\nbar,1,0.5\n")
    q = {r["query"]: r for r in bw.parse_ai_performance([path])["data"]["top_grounding_queries"]}
    assert q["foo"]["citation_share_pct"] == 12.5
    assert q["bar"]["citation_share_pct"] == 50.0


def test_unknown_columns_are_reported_not_guessed(tmp_path):
    path = _write(tmp_path, "x.csv", "Alpha,Beta\n1,2\n")
    data = bw.parse_ai_performance([path])["data"]
    assert data["source_files"][0]["type"] == "unknown"
    assert data["warnings"]


def test_missing_file_is_a_warning_not_a_crash():
    res = bw.parse_ai_performance([os.path.join(DIR, "does-not-exist.csv")])
    assert res["data"]["warnings"]
