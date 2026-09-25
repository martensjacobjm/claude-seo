"""Tests for crux_bigquery.py query planning and result shaping (no network)."""

import datetime

import pytest

import crux_bigquery as cb


def test_normalize_origin_drops_path_and_adds_scheme():
    assert cb.normalize_origin("example.com/some/path?q=1") == "https://example.com"
    assert cb.normalize_origin("https://www.example.com/") == "https://www.example.com"


def test_normalize_origin_blocks_private_hosts():
    with pytest.raises(Exception):
        cb.normalize_origin("http://127.0.0.1")


def test_start_date_counts_back_whole_months():
    # CrUX publishes the previous month, so 12 months from Sep 2026 = 202509..202608.
    assert cb.start_date(12, today=datetime.date(2026, 9, 25)) == datetime.date(2025, 9, 1)
    assert cb.start_date(1, today=datetime.date(2026, 1, 10)) == datetime.date(2025, 12, 1)


def test_sql_is_parameterised():
    plan = cb.plan_query(["https://example.com"], None, 6, today=datetime.date(2026, 9, 25))
    assert "example.com" not in plan["sql"]
    assert "@origins" in plan["sql"] and "@start_date" in plan["sql"]
    assert "metrics_summary" in plan["sql"]
    device_plan = cb.plan_query(["https://example.com"], ["phone"], 6)
    assert "device_summary" in device_plan["sql"] and "@devices" in device_plan["sql"]


@pytest.mark.parametrize("metric,value,expected", [
    ("lcp", 2500, "Good"), ("lcp", 2501, "Needs Improvement"), ("lcp", 4001, "Poor"),
    ("inp", 200, "Good"), ("inp", 500, "Needs Improvement"), ("inp", 501, "Poor"),
    ("cls", 0.1, "Good"), ("cls", 0.26, "Poor"),
])
def test_rating_thresholds(metric, value, expected):
    assert cb.rate(metric, value) == expected


def _row(yyyymm, lcp, inp, cls):
    return {"yyyymm": yyyymm, "p75_lcp": lcp, "p75_inp": inp, "p75_cls": cls,
            "good_lcp": 0.8, "ni_lcp": 0.15, "poor_lcp": 0.05}


def test_missing_inp_is_assessed_on_lcp_and_cls():
    rec = cb.shape_row(_row(202608, 2100, None, 0.05))
    assert rec["inp_missing"] is True
    assert rec["cwv_pass"] is True


def test_benchmark_ranks_with_ties_on_latest_shared_month():
    rows = {
        "https://a.example": [cb.shape_row(_row(202608, 2000, 150, 0.05)), cb.shape_row(_row(202607, 1900, 150, 0.05))],
        "https://b.example": [cb.shape_row(_row(202608, 2000, 250, 0.02))],
    }
    bench = cb.build_benchmark("https://a.example", rows)
    assert bench["yyyymm"] == 202608
    table = bench["by_device"]["all"]
    assert table["https://a.example"]["lcp"]["rank"] == 1
    assert table["https://b.example"]["lcp"]["tied"] is True
    assert table["https://b.example"]["inp"]["delta_vs_target"] == 100
