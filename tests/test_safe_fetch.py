"""SSRF tests for safe_fetch.py, validate_url(resolve=True) and the scripts
that fetch user URLs (fetch_page, verify_backlinks, nlp_analyze).

The local server listens on 127.0.0.1, which the production validator refuses.
Tests inject a validator that allows exactly that origin and defers to the
production validator for everything else, so a redirect to 169.254.169.254 is
refused by the real rule. No environment-variable bypass exists or is used.
"""

import socket

import pytest

requests = pytest.importorskip("requests")

import fetch_page as fp  # noqa: E402
import nlp_analyze  # noqa: E402
import safe_fetch as sf  # noqa: E402
import verify_backlinks as vb  # noqa: E402
from google_auth import validate_url  # noqa: E402
from local_http_server import LocalSite, html  # noqa: E402

METADATA = "http://169.254.169.254/latest/meta-data/"


def local_only(site):
    """Allow the fixture origin; everything else goes through the real validator."""
    prefix = site.base_url + "/"
    return lambda url: url.startswith(prefix) or sf.default_validator(url)


def redirect(location, status=302):
    return status, {"Location": location}, ""


@pytest.fixture
def site():
    with LocalSite() as s:
        yield s


def fake_dns(monkeypatch, mapping):
    """Resolve names in mapping to fixed addresses (None: NXDOMAIN); others as usual."""
    real = socket.getaddrinfo

    def getaddrinfo(host, *args, **kwargs):
        if host not in mapping:
            return real(host, *args, **kwargs)
        if mapping[host] is None:
            raise socket.gaierror("no such host")
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (mapping[host], 0))]
    monkeypatch.setattr(socket, "getaddrinfo", getaddrinfo)


# --- validate_url -------------------------------------------------------------------

@pytest.mark.parametrize("url", [
    "http://127.0.0.1/", "http://169.254.169.254/", "http://10.1.2.3/",
    "http://172.16.0.1/", "http://192.168.1.1/", "http://[::1]/",
    "http://[::ffff:127.0.0.1]/", "http://[fe80::1]/", "http://224.0.0.1/",
    "http://240.0.0.1/", "http://100.64.0.1/", "http://0.0.0.0/",
    "http://localhost/", "http://localhost./", "http://app.localhost/",
    "http://metadata.google.internal/", "file:///etc/passwd", "ftp://example.com/",
])
def test_validate_url_rejects_non_public_literals(url):
    assert validate_url(url) is False
    assert validate_url(url, resolve=True) is False


def test_validate_url_resolve_rejects_private_dns(monkeypatch):
    fake_dns(monkeypatch, {"internal.example": "10.0.0.5",
                           "meta.example": "169.254.169.254",
                           "public.example": "93.184.215.14",
                           "nxdomain.example": None})
    assert validate_url("https://internal.example/") is True  # string check only
    assert validate_url("https://internal.example/", resolve=True) is False
    assert validate_url("https://meta.example/", resolve=True) is False
    assert validate_url("https://public.example/", resolve=True) is True
    # Unresolvable names pass; the request itself then fails.
    assert validate_url("https://nxdomain.example/", resolve=True) is True


def test_validate_url_resolve_catches_numeric_host_forms():
    # getaddrinfo reads these as 127.0.0.1; the string check alone cannot.
    assert validate_url("http://2130706433/", resolve=True) is False
    assert validate_url("http://0x7f000001/", resolve=True) is False


# --- safe_request --------------------------------------------------------------------

def test_default_validator_refuses_local_server(site):
    site.routes["/"] = html("Home", "hi")
    res = sf.safe_request(site.base_url + "/")
    assert res.error_kind == "blocked" and res.status is None
    assert site.hits == []


def test_redirect_to_metadata_is_refused(site):
    site.routes["/go"] = redirect(METADATA)
    res = sf.safe_request(site.base_url + "/go", validator=local_only(site))
    assert res.error_kind == "blocked"
    assert res.final_url == METADATA
    assert res.hops == [{"url": site.base_url + "/go", "status": 302, "location": METADATA}]
    assert res.status is None and res.body == b""


def test_redirect_to_rfc1918_and_loopback_is_refused(site):
    for target in ("http://10.0.0.1/admin", "http://127.0.0.1:1/", "http://[::1]/"):
        site.routes["/go"] = redirect(target, 301)
        res = sf.safe_request(site.base_url + "/go", validator=local_only(site))
        assert res.error_kind == "blocked", target
        assert res.final_url == target


def test_redirect_to_host_resolving_private_is_refused(site, monkeypatch):
    fake_dns(monkeypatch, {"rebind.example": "192.168.0.10"})
    site.routes["/go"] = redirect("http://rebind.example/")
    res = sf.safe_request(site.base_url + "/go", validator=local_only(site))
    assert res.error_kind == "blocked" and res.final_url == "http://rebind.example/"


def test_allowed_redirects_are_followed(site):
    site.routes["/a"] = redirect("/b", 301)
    site.routes["/b"] = redirect(site.base_url + "/c", 307)
    site.routes["/c"] = html("C", "done")
    res = sf.safe_request(site.base_url + "/a", validator=local_only(site))
    assert res.error is None and res.status == 200
    assert res.final_url == site.base_url + "/c"
    assert [h["status"] for h in res.hops] == [301, 307]
    assert "done" in res.text


def test_too_many_redirects(site):
    site.routes["/loop"] = redirect("/loop")
    res = sf.safe_request(site.base_url + "/loop", validator=local_only(site),
                          max_redirects=3)
    assert res.error_kind == "too_many_redirects"
    assert len(res.hops) == 4


def test_body_cap(site):
    site.routes["/big"] = (200, {"Content-Type": "text/plain"}, "x" * 200_000)
    res = sf.safe_request(site.base_url + "/big", validator=local_only(site), max_bytes=1000)
    assert res.truncated and len(res.body) == 1000 and len(res.text) == 1000


# --- fetch_page ----------------------------------------------------------------------

def test_fetch_page_redirect_to_metadata_is_refused(site):
    site.routes["/go"] = redirect(METADATA, 301)
    res = fp.fetch_page(site.base_url + "/go", validator=local_only(site))
    assert res["error"].startswith("Blocked:") and METADATA in res["error"]
    assert res["content"] is None and res["status_code"] is None
    assert site.hits == [("GET", "/go")]


def test_fetch_page_default_validator_refuses_loopback(site):
    site.routes["/"] = html("Home", "hi")
    res = fp.fetch_page(site.base_url + "/")
    assert res["error"].startswith("Blocked:")
    assert site.hits == []


def test_fetch_page_private_dns_refused_before_request(monkeypatch):
    fake_dns(monkeypatch, {"evil.example": "127.0.0.1"})

    def no_network(*args, **kwargs):
        raise AssertionError("request sent to a blocked host")
    monkeypatch.setattr(requests.Session, "request", no_network)
    res = fp.fetch_page("http://evil.example/")
    assert res["error"].startswith("Blocked:")


def test_fetch_page_result_shape_unchanged(site):
    site.routes["/old"] = redirect("/new", 301)
    site.routes["/new"] = html("New", "moved here", headers={"X-Test": "1"})
    res = fp.fetch_page(site.base_url + "/old", validator=local_only(site))
    assert set(res) == {"url", "status_code", "content", "headers",
                        "redirect_chain", "redirect_details", "error"}
    assert res["error"] is None and res["status_code"] == 200
    assert res["url"] == site.base_url + "/new"
    assert "moved here" in res["content"]
    assert res["headers"]["X-Test"] == "1"
    assert res["redirect_chain"] == [site.base_url + "/old"]
    assert res["redirect_details"] == [{"url": site.base_url + "/old", "status_code": 301}]


def test_fetch_page_no_redirects_returns_3xx(site):
    site.routes["/old"] = redirect(METADATA, 301)
    res = fp.fetch_page(site.base_url + "/old", follow_redirects=False,
                        validator=local_only(site))
    assert res["error"] is None and res["status_code"] == 301
    assert res["redirect_chain"] == []


def test_fetch_page_too_many_redirects_message(site):
    site.routes["/loop"] = redirect("/loop")
    res = fp.fetch_page(site.base_url + "/loop", max_redirects=2, validator=local_only(site))
    assert res["error"] == "Too many redirects (max 2)"


# --- verify_backlinks ----------------------------------------------------------------

def test_head_check_redirect_to_metadata_is_refused(site):
    site.routes["/src"] = redirect(METADATA)
    res = vb._head_check(site.base_url + "/src", validator=local_only(site))
    assert res["exists"] is False and "SSRF" in res["error"]
    assert site.hits == [("HEAD", "/src")]


def test_verify_backlink_follows_safe_redirect(site, monkeypatch):
    monkeypatch.setattr(vb, "DOMAIN_DELAY", 0)
    site.routes["/src"] = redirect("/page", 301)
    site.routes["/page"] = html("P", '<a href="https://target.example/x">Target</a>')
    res = vb.verify_single_backlink(site.base_url + "/src", "https://target.example/x",
                                    validator=local_only(site))
    assert res["status"] == "verified" and res["anchor_text"] == "Target"


# --- nlp_analyze ---------------------------------------------------------------------

def test_nlp_analyze_redirect_to_metadata_is_refused(site, monkeypatch):
    def no_api(*args, **kwargs):
        raise AssertionError("NLP API must not be called")
    monkeypatch.setattr(nlp_analyze, "analyze_text", no_api)
    site.routes["/doc"] = redirect(METADATA)
    res = nlp_analyze.analyze_url(site.base_url + "/doc", validator=local_only(site))
    assert "blocked" in res["error"] and METADATA in res["error"]


def test_nlp_analyze_default_validator_refuses_loopback(site):
    res = nlp_analyze.analyze_url(site.base_url + "/doc")
    assert res["error"].startswith("Invalid URL")
    assert site.hits == []
