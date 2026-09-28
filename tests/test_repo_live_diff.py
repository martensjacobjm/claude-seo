"""Tests for scripts/repo_live_diff.py against a local http.server (no internet)."""

import os
import subprocess
from urllib.parse import urlparse

import pytest
import requests

import repo_live_diff as rld
from local_http_server import LocalSite, html

INDEX_BODY = "<h1>Flyttstädning i Malung</h1><p>Vi städar ditt hem. Ring oss 2025.</p>"
ABOUT_OLD = "<h1>Om oss</h1><p>Vi startade 2024 och städar i Malung.</p>"
ABOUT_NEW = "<h1>Om oss</h1><p>Vi startade 2024, har nu fem anställda och städar i Sälen 2026.</p>"
LD = ('<script type="application/ld+json">{"@context":"https://schema.org",'
      '"@type":"LocalBusiness","name":"X"}</script>')


def loopback_only(url):
    """Test validator: allow the local test server, run the real checks for anything else."""
    return urlparse(url).hostname == "127.0.0.1" or rld.default_validator(url)


def fetcher():
    s = requests.Session()
    s.trust_env = False  # never route the loopback test server through a proxy
    return rld.SafeFetcher(validator=loopback_only, delay=0, timeout=5, session=s)


def _doc(title, body, head=""):
    return html(title, body, head)[2]


@pytest.fixture
def local_repo(tmp_path):
    d = tmp_path / "site"
    d.mkdir()
    (d / "index.html").write_text(_doc("Hem", INDEX_BODY, LD), encoding="utf-8")
    (d / "om-oss.html").write_text(_doc("Om oss", ABOUT_OLD), encoding="utf-8")
    env = dict(os.environ, GIT_AUTHOR_DATE="2025-11-09T11:49:45+01:00",
               GIT_COMMITTER_DATE="2025-11-09T11:49:45+01:00")
    g = ["git", "-C", str(d), "-c", "user.name=T", "-c", "user.email=t@example.com",
         "-c", "commit.gpgsign=false"]
    subprocess.run(g + ["init", "-q"], check=True, capture_output=True)
    subprocess.run(g + ["add", "-A"], check=True, capture_output=True)
    subprocess.run(g + ["commit", "-q", "-m", "old"], check=True, capture_output=True, env=env)
    return d


def _serve_live(site, about_body=ABOUT_NEW, extra_sitemap=True):
    b = site.base_url
    site.routes["/"] = html("Hem", INDEX_BODY, LD)
    site.routes["/om-oss.html"] = html(
        "Om oss", about_body, headers={"Last-Modified": "Mon, 21 Sep 2026 10:00:00 GMT",
                                       "ETag": '"abc"'})
    site.routes["/robots.txt"] = (200, {"Content-Type": "text/plain"},
                                  f"User-agent: *\nSitemap: {b}/sitemap.xml\n")
    urls = ["/", "/om-oss.html"] + (["/nyheter"] if extra_sitemap else [])
    site.routes["/sitemap.xml"] = (200, {"Content-Type": "application/xml"},
                                   '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/'
                                   'schemas/sitemap/0.9">' + "".join(
                                       f"<url><loc>{b}{u}</loc></url>" for u in urls) + "</urlset>")


def test_url_mapping():
    assert rld.url_candidates("index.html", False) == ["/"]
    assert rld.url_candidates("blog/index.html", True) == ["/blog/"]
    assert rld.url_candidates("om-oss.html", False) == ["/om-oss.html"]
    assert rld.url_candidates("om-oss.html", True) == ["/om-oss", "/om-oss.html"]
    assert rld.url_candidates("tjänster.html", False) == ["/tj%C3%A4nster.html"]
    assert rld.path_key("/om-oss.html") == rld.path_key("/om-oss/") == "/om-oss"
    assert rld.path_key("/blog/index.html") == "/blog"


def test_extract_fields():
    ex = rld.extract(_doc("Hem", INDEX_BODY, LD + '<link rel="canonical" href="https://x.se/">'
                          '<meta name="description" content="Städ">'))
    assert ex["title"] == "Hem" and ex["meta_description"] == "Städ"
    assert ex["canonical"] == "https://x.se/" and ex["h1"] == ["Flyttstädning i Malung"]
    assert ex["jsonld_types"] == ["LocalBusiness"]
    assert "LocalBusiness" not in ex["_text"] and "Vi städar" in ex["_text"]
    assert ex["latest_year_in_text"] == 2025


def test_repo_older_than_live(local_repo):
    with LocalSite() as site:
        _serve_live(site)
        res = rld.run_diff(str(local_repo), site.base_url, fetcher())
    s = res["summary"]
    assert (s["identical"], s["differing"], s["only_local"], s["only_live"]) == (1, 1, 0, 1)
    about = next(p for p in res["pages"] if p["file"] == "om-oss.html")
    assert about["dates"]["live_last_modified"].startswith("Mon, 21 Sep 2026")
    assert about["dates"]["local_git_date"].startswith("2025-11-09")
    assert about["date_signal"] == "live_newer" and about["year_signal"] == "live_newer"
    assert 0 < about["comparison"]["text_similarity"] < 1
    assert res["only_live"][0]["url"].endswith("/nyheter")
    assert res["verdict"] == "repo appears older"
    assert res["exit_code"] == 1


def test_in_sync(local_repo):
    with LocalSite() as site:
        _serve_live(site, about_body=ABOUT_OLD, extra_sitemap=False)
        res = rld.run_diff(str(local_repo), site.base_url, fetcher())
    assert res["verdict"] == "in sync" and res["exit_code"] == 0


def test_diverged_when_both_sides_have_unique_pages(local_repo):
    (local_repo / "kontakt.html").write_text(_doc("Kontakt", "<h1>Kontakt</h1>"), encoding="utf-8")
    with LocalSite() as site:
        _serve_live(site)
        res = rld.run_diff(str(local_repo), site.base_url, fetcher())
    assert res["summary"]["only_local"] == 1
    assert res["verdict"] == "diverged" and res["exit_code"] == 1


def test_redirect_to_metadata_ip_is_refused():
    with LocalSite() as site:
        site.routes["/"] = (302, {"Location": "http://169.254.169.254/latest/meta-data/"}, "")
        res = fetcher().get(site.base_url + "/")
    assert res["blocked"] is True and res["status"] is None
    assert "169.254.169.254" in res["error"]
    assert res["hops"][0]["status"] == 302


def test_production_validator_still_blocks_loopback_and_metadata():
    assert rld.default_validator("http://127.0.0.1:8000/") is False
    assert rld.default_validator("http://169.254.169.254/") is False
    assert rld.default_validator("http://localhost/") is False
    assert rld.default_validator("file:///etc/passwd") is False


def test_base_url_unreachable_is_fatal(local_repo):
    res = rld.run_diff(str(local_repo), "http://127.0.0.1:9/", rld.SafeFetcher(delay=0))
    assert res["exit_code"] == 2 and "blocked" in res["error"]
