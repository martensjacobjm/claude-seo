"""Tests for the Google Ads OAuth scope handling (no network)."""

import json
import os
import stat

import pytest

import google_auth as ga
import keyword_planner as kp

ADS = "https://www.googleapis.com/auth/adwords"


@pytest.fixture
def cfg(tmp_path, monkeypatch):
    config_path = tmp_path / "google-api.json"
    token_path = tmp_path / "oauth-token.json"
    monkeypatch.setattr(ga, "CONFIG_PATH", str(config_path))
    monkeypatch.setattr(ga, "TOKEN_PATH", str(token_path))
    return config_path, token_path


def _write(path, data):
    path.write_text(json.dumps(data), encoding="utf-8")


def test_oauth_flow_requests_adwords_scope():
    assert ADS in ga.OAUTH_SCOPES.split()
    assert ga.SCOPES["ads"] == ADS
    # Existing scopes are still requested.
    for s in ("indexing", "webmasters", "analytics.readonly"):
        assert f"https://www.googleapis.com/auth/{s}" in ga.OAUTH_SCOPES.split()


def test_token_has_scope_true_false_unknown():
    assert ga.token_has_scope(ADS, {"scope": f"a b {ADS}"}) is True
    assert ga.token_has_scope(ADS, {"scope": "https://www.googleapis.com/auth/webmasters"}) is False
    assert ga.token_has_scope(ADS, {"access_token": "x"}) is None


def test_saved_token_is_owner_only(cfg):
    _, token_path = cfg
    ga._save_oauth_token({"access_token": "x", "scope": ADS})
    assert stat.S_IMODE(os.stat(token_path).st_mode) == 0o600


def test_check_ads_missing_config(cfg):
    config_path, _ = cfg
    _write(config_path, {})
    res = ga.check_credentials("ads")
    assert res["available"] is False
    assert "ads_developer_token" in res["error"] and "ads_customer_id" in res["error"]


def test_check_ads_old_token_without_scope_asks_reauth(cfg):
    config_path, token_path = cfg
    _write(config_path, {"ads_developer_token": "t", "ads_customer_id": "123-456-7890",
                         "oauth_client_path": "/nonexistent/client.json"})
    _write(token_path, {"access_token": "a", "refresh_token": "r",
                        "scope": "https://www.googleapis.com/auth/webmasters"})
    res = ga.check_credentials("ads")
    assert res["available"] is False
    assert "--auth" in res["error"]


def test_check_ads_ok_and_legacy_token_note(cfg):
    config_path, token_path = cfg
    _write(config_path, {"ads_developer_token": "t", "ads_customer_id": "123-456-7890",
                         "oauth_client_path": "/nonexistent/client.json"})
    _write(token_path, {"access_token": "a", "refresh_token": "r", "scope": ADS})
    assert ga.check_credentials("ads")["available"] is True
    _write(token_path, {"access_token": "a", "refresh_token": "r"})
    res = ga.check_credentials("ads")
    assert res["available"] is True and "re-run --auth" in res["note"]


def test_keyword_planner_stops_with_reauth_hint(tmp_path, monkeypatch, capsys):
    home = tmp_path / "home"
    token_dir = home / ".config" / "claude-seo"
    token_dir.mkdir(parents=True)
    _write(token_dir / "oauth-token.json", {"refresh_token": "r",
                                            "scope": "https://www.googleapis.com/auth/webmasters"})
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setattr(kp, "HAS_GOOGLE_ADS", True)
    monkeypatch.setattr(kp, "load_config", lambda: {
        "ads_developer_token": "t", "ads_customer_id": "123-456-7890",
        "oauth_client_path": str(tmp_path / "client.json")})

    class Boom:
        @staticmethod
        def load_from_dict(_):
            raise AssertionError("client must not be built without the adwords scope")

    monkeypatch.setattr(kp, "GoogleAdsClient", Boom, raising=False)
    assert kp._build_ads_client() is None
    assert "Google Ads access" in capsys.readouterr().err
