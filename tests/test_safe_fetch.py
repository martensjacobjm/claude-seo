"""Tests for scripts/safe_fetch.py (SSRF-safe fetching) against a local http.server.

The production validator refuses loopback, so tests inject a validator that
allows exactly the fixture origin and delegates every other URL to the real
validator. DNS answers are faked by monkeypatching socket.getaddrinfo; no
test touches the internet.
"""

import socket
from urllib.parse import urlparse

import pytest
import requests

import fetch_page as fp
import free_keyword_data as fkd
import google_auth
import repo_live_diff as rld
import safe_fetch as sf
import site_crawl as sc
import verify_backlinks as vb
from local_http_server import LocalSite, html

METADATA = "http://169.254.169.254/latest/meta-data/"
_real_getaddrinfo = socket.getaddrinfo


def fixture_validator(site_url):
    """Allow exactly the fixture origin; everything else goes to the real validator."""
    origin = urlparse(site_url).netloc

    def check(url):
        return urlparse(url).netloc == origin or sf.validate_public_url(url)
    return check


def fetcher(site_url, **kw):
    s = requests.Session()
    s.trust_env = False  # never route the loopback test server through a proxy
    return sf.SafeFetcher(validator=fixture_validator(site_url), timeout=5, session=s, **kw)


def fake_dns(monkeypatch, answers):
    """Make getaddrinfo return answers[host] (a list, or a callable) for listed hosts."""
    def fake(host, port, *args, **kwargs):
        if host in answers:
            value = answers[host]
            addrs = value() if callable(value) else value
            return [(socket.AF_INET6 if ":" in a else socket.AF_INET, socket.SOCK_STREAM, 6, "",
                     (a, port or 0)) for a in addrs]
        return _real_getaddrinfo(host, port, *args, **kwargs)
    monkeypatch.setattr(socket, "getaddrinfo", fake)


@pytest.fixture
def site():
    with LocalSite() as s:
        s.routes["/"] = html("Home", "<p>ok</p>")
        s.routes["/to-metadata"] = (302, {"Location": METADATA}, "")
        s.routes["/to-loopback"] = (301, {"Location": "http://127.0.0.1:1/admin"}, "")
        s.routes["/to-private-name"] = (302, {"Location": "http://intranet.example/"}, "")
        s.routes["/to-file"] = (302, {"Location": "file:///etc/passwd"}, "")
        s.routes["/to-mapped"] = (302, {"Location": "http://[::ffff:169.254.169.254]/"}, "")
        s.routes["/r0"] = (302, {"Location": "/r1"}, "")
        s.routes["/r1"] = (302, {"Location": "/r2"}, "")
        s.routes["/r2"] = (302, {"Location": "/r3"}, "")
        s.routes["/r3"] = (302, {"Location": "/"}, "")
        s.routes["/big"] = (200, {"Content-Type": "text/plain"}, "x" * 20000)
        s.routes["/links"] = html("Links", '<a href="https://target.example/page">Target</a>'
                                  + "<p>" + "word " * 60 + "</p>")
        yield s


# --- validation ------------------------------------------------------------------

@pytest.mark.parametrize("url", [
    "http://127.0.0.1/", "http://localhost/", "http://169.254.169.254/", "http://10.0.0.5/",
    "http://192.168.1.1/", "http://172.16.0.1/", "http://100.64.0.1/", "http://0.0.0.0/",
    "http://[::1]/", "http://[fd00::1]/", "http://[fe80::1]/", "http://224.0.0.1/",
    "http://metadata.google.internal/", "http://2130706433/", "http://0x7f.1/",
])
def test_literal_private_targets_refused(url):
    assert sf.validate_public_url(url, resolve=False) is False
    assert google_auth.validate_url(url) is False


@pytest.mark.parametrize("url", [
    "http://[::ffff:127.0.0.1]/", "http://[::ffff:a9fe:a9fe]/", "http://[::ffff:10.0.0.1]/",
    "http://[2002:7f00:1::1]/", "http://[64:ff9b::a9fe:a9fe]/", "http://[2001::1]/",
])
def test_ipv4_mapped_6to4_nat64_forms_refused(url):
    assert sf.validate_public_url(url, resolve=False) is False


@pytest.mark.parametrize("url", ["file:///etc/passwd", "ftp://example.com/", "gopher://example.com/",
                                 "javascript:alert(1)", "//example.com/", "example.com"])
def test_non_http_scheme_refused(url):
    assert sf.validate_public_url(url) is False


def test_public_addresses_allowed():
    for ip in ("93.184.216.34", "8.8.8.8", "2606:4700::1111", "::ffff:8.8.8.8"):
        assert sf.is_public_ip(ip), ip


def test_hostname_resolving_to_private_ip_refused(monkeypatch):
    fake_dns(monkeypatch, {"intranet.example": ["10.0.0.5"],
                           "mixed.example": ["93.184.216.34", "127.0.0.1"],
                           "mapped.example": ["::ffff:169.254.169.254"],
                           "public.example": ["93.184.216.34"]})
    assert sf.validate_public_url("http://intranet.example/") is False
    assert "10.0.0.5" in sf.check_public_url("http://intranet.example/")
    assert sf.validate_public_url("http://mixed.example/") is False  # ANY bad address
    assert sf.validate_public_url("http://mapped.example/") is False
    assert sf.validate_public_url("http://public.example/") is True
    # google_auth keeps literal-only behavior by default; resolve=True adds DNS.
    assert google_auth.validate_url("http://intranet.example/") is True
    assert google_auth.validate_url("http://intranet.example/", resolve=True) is False


def test_scripts_share_the_validator():
    assert sc.default_validator is sf.validate_public_url
    assert rld.default_validator is sf.validate_public_url
    assert issubclass(rld.SafeFetcher, sf.SafeFetcher)


# --- per-hop validation ------------------------------------------------------------

@pytest.mark.parametrize("path,needle", [
    ("/to-metadata", "169.254.169.254"),
    ("/to-loopback", "127.0.0.1:1"),
    ("/to-file", "file:///etc/passwd"),
    ("/to-mapped", "::ffff:169.254.169.254"),
])
def test_redirect_to_non_public_target_refused(site, path, needle):
    f = fetcher(site.base_url)
    res = f.fetch(site.base_url + path)
    assert res["blocked"] is True and res["error_kind"] == "blocked"
    assert res["status"] is None and needle in res["final_url"]
    assert res["hops"][0]["status"] in (301, 302)
    assert f.requests_made == 1  # the refused hop was never requested


def test_redirect_to_hostname_resolving_private_refused(site, monkeypatch):
    fake_dns(monkeypatch, {"intranet.example": ["10.1.2.3"]})
    res = fetcher(site.base_url).fetch(site.base_url + "/to-private-name")
    assert res["blocked"] is True and res["final_url"] == "http://intranet.example/"


def test_hop_limit(site):
    res = fetcher(site.base_url, max_redirects=2).fetch(site.base_url + "/r0")
    assert res["error_kind"] == "too_many_redirects" and res["status"] is None
    assert len(res["hops"]) == 3
    ok = fetcher(site.base_url, max_redirects=4).fetch(site.base_url + "/r0")
    assert ok["status"] == 200 and len(ok["hops"]) == 4 and ok["final_url"] == site.base_url + "/"


def test_body_cap(site):
    res = fetcher(site.base_url, max_bytes=1000).fetch(site.base_url + "/big")
    assert res["status"] == 200 and res["truncated"] is True
    assert res["bytes"] == 1000 and len(res["body"]) == 1000


def test_production_fetcher_refuses_loopback_start_url(site):
    res = sf.safe_get(site.base_url + "/")
    assert res["blocked"] is True and res["status"] is None


# --- connect-time pinning (DNS rebinding) ------------------------------------------

def test_dns_rebinding_refused_at_connect_time(site, monkeypatch):
    port = urlparse(site.base_url).port
    answers = iter([["93.184.216.34"]])  # first lookup (validator): public; then loopback

    fake_dns(monkeypatch, {"rebind.test": lambda: next(answers, ["127.0.0.1"])})
    session = sf.make_session()
    session.trust_env = False
    res = sf.SafeFetcher(session=session, timeout=5).fetch(f"http://rebind.test:{port}/")
    assert res["blocked"] is True and res["status"] is None
    assert "connect time" in res["error"]


def test_pinned_session_connects_to_validated_ip_and_keeps_host(site, monkeypatch):
    port = urlparse(site.base_url).port
    fake_dns(monkeypatch, {"pinned.test": ["127.0.0.1"]})
    seen = []
    site.routes["/"] = html("Home", "<p>ok</p>")

    def allow_pinned(url):
        seen.append(url)
        return urlparse(url).hostname == "pinned.test"
    session = sf.make_session(sf.address_check_for(allow_pinned))
    session.trust_env = False
    res = sf.SafeFetcher(validator=allow_pinned, session=session, timeout=5).fetch(
        f"http://pinned.test:{port}/")
    assert res["status"] == 200 and "ok" in res["text"]


# --- scripts using the shared module ------------------------------------------------

def test_fetch_page_refuses_redirect_to_metadata(site):
    res = fp.fetch_page(site.base_url + "/to-metadata", fetcher=fetcher(site.base_url))
    assert res["error"].startswith("Blocked:") and res["content"] is None
    assert res["redirect_details"] == [{"url": site.base_url + "/to-metadata", "status_code": 302}]


def test_fetch_page_redirect_details_and_content(site):
    res = fp.fetch_page(site.base_url + "/r2", fetcher=fetcher(site.base_url))
    assert res["error"] is None and res["status_code"] == 200
    assert res["url"] == site.base_url + "/"
    assert res["redirect_chain"] == [site.base_url + "/r2", site.base_url + "/r3"]
    assert [d["status_code"] for d in res["redirect_details"]] == [302, 302]
    assert "<p>ok</p>" in res["content"] and "Content-Type" in res["headers"]


def test_fetch_page_default_path_blocks_loopback(site):
    res = fp.fetch_page(site.base_url + "/")
    assert res["error"].startswith("Blocked:")


def test_verify_backlinks_refuses_redirect_to_metadata(site):
    res = vb.verify_single_backlink(site.base_url + "/to-metadata", "https://target.example/",
                                    fetcher=fetcher(site.base_url))
    assert res["status"] == "error" and "blocked" in res["error"].lower()
    assert res["target_found"] is False


def test_verify_backlinks_injected_fetcher_verifies_link(site, monkeypatch):
    monkeypatch.setattr(vb, "DOMAIN_DELAY", 0)
    res = vb.verify_single_backlink(site.base_url + "/links", "https://target.example/",
                                    fetcher=fetcher(site.base_url))
    assert res["status"] == "verified" and res["target_found"] is True


def test_verify_backlinks_default_path_blocks_loopback(site):
    res = vb.verify_single_backlink(site.base_url + "/", "https://target.example/")
    assert res["status"] == "error" and "SSRF" in res["error"]


def test_wikipedia_project_cannot_inject_a_host():
    res = fkd.fetch_wikipedia("seo", "localhost:8080/x?.wikipedia", 3)
    assert "invalid Wikimedia project" in res["error"]
