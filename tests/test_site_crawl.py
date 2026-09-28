"""Tests for scripts/site_crawl.py against a local fixture site (tests/fixtures/crawl-site/).

The fixture is served by http.server on 127.0.0.1 in a background thread. The
production validator (google_auth.validate_url + DNS check) blocks loopback, so
the tests inject a validator that allows exactly this one fixture origin and
delegates every other URL to the real validator. There is no env-var bypass.
"""

import gzip
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import pytest

pytest.importorskip("requests")
pytest.importorskip("bs4")

import site_crawl as sc  # noqa: E402
from conftest import FIXTURES, ROOT  # noqa: E402

SITE = os.path.join(FIXTURES, "crawl-site")

REDIRECTS = {
    "/redirect-a": (301, "/redirect-b"),
    "/redirect-b": (302, "/page-2.html"),
    "/redirect-single": (301, "/page-2.html"),
    "/loop-a": (302, "/loop-b"),
    "/loop-b": (302, "/loop-a"),
    "/to-metadata": (302, "http://169.254.169.254/latest/meta-data/"),
    "/to-loopback": (302, "http://127.0.0.1/admin"),
}


class FixtureHandler(BaseHTTPRequestHandler):
    origin = ""

    def log_message(self, *args):  # keep pytest output clean
        pass

    def _send(self, status, body=b"", ctype="text/html; charset=utf-8", extra=None):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _template(self, rel):
        path = os.path.realpath(os.path.join(SITE, rel.lstrip("/")))
        if not path.startswith(os.path.realpath(SITE) + os.sep) or not os.path.isfile(path):
            return None
        with open(path, "r", encoding="utf-8") as fh:
            return fh.read().replace("{{ORIGIN}}", self.origin).encode("utf-8")

    def do_HEAD(self):
        self.do_GET()

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in REDIRECTS:
            status, loc = REDIRECTS[path]
            return self._send(status, extra={"Location": loc})
        if path == "/header-noindex":
            body = self._template("header-noindex.html")
            return self._send(200, body, extra={"X-Robots-Tag": "noindex"})
        if path.endswith(".xml.gz"):
            body = self._template(path[:-3])
            if body is None:
                return self._send(404, b"not found", "text/plain")
            return self._send(200, gzip.compress(body), "application/gzip")
        rel = "index.html" if path == "/" else path
        body = self._template(rel)
        if body is None:
            return self._send(404, b"<h1>Not found</h1>")
        ctype = {"txt": "text/plain", "xml": "application/xml"}.get(
            rel.rsplit(".", 1)[-1], "text/html; charset=utf-8")
        return self._send(200, body, ctype)


@pytest.fixture(scope="module")
def site():
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    origin = f"http://127.0.0.1:{server.server_address[1]}"
    FixtureHandler.origin = origin
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield origin
    server.shutdown()
    server.server_close()


def fixture_validator(origin):
    """Allow exactly the fixture origin; everything else goes to the real validator."""
    allowed = sc.host_of(origin)
    return lambda url: sc.host_of(url) == allowed or sc.default_validator(url)


@pytest.fixture(scope="module")
def crawl(site):
    return sc.crawl_site(site + "/", max_pages=50, max_depth=3, delay=0,
                         validator=fixture_validator(site), sleep=lambda s: None)


# ---------------------------------------------------------------- unit tests

def test_user_agent_uses_plugin_version():
    with open(os.path.join(ROOT, ".claude-plugin", "plugin.json"), encoding="utf-8") as fh:
        version = json.load(fh)["version"]
    assert sc.default_user_agent().startswith(f"claude-seo-crawler/{version}")


@pytest.mark.parametrize("raw,kwargs,expected", [
    ("HTTPS://Example.COM:443/a/#frag", {}, "https://example.com/a/"),
    ("http://example.com", {}, "http://example.com/"),
    ("http://example.com:8080/x?b=2&a=1", {"sort_query": True}, "http://example.com:8080/x?a=1&b=2"),
    ("https://example.com/dir/", {"trailing_slash": "strip"}, "https://example.com/dir"),
    ("https://example.com/dir", {"trailing_slash": "add"}, "https://example.com/dir/"),
    ("https://example.com/file.html", {"trailing_slash": "add"}, "https://example.com/file.html"),
    ("mailto:a@example.com", {}, None),
    ("ftp://example.com/x", {}, None),
])
def test_normalize_url(raw, kwargs, expected):
    assert sc.normalize_url(raw, **kwargs) == expected


def test_default_validator_blocks_private_targets():
    for url in ("http://127.0.0.1:8000/", "http://localhost/", "http://169.254.169.254/",
                "http://10.0.0.5/", "http://[::1]/", "file:///etc/passwd"):
        assert sc.default_validator(url) is False, url


def test_robots_crawl_delay_and_rfc9309_status_handling():
    r = sc.Robots("User-agent: *\nCrawl-delay: 5\nDisallow: /x/\n", 200,
                  "https://example.com/robots.txt")
    assert r.crawl_delay() == 5.0
    assert not r.allowed("https://example.com/x/y") and r.allowed("https://example.com/y")
    assert sc.Robots(None, 404, "u").allowed("https://example.com/any")
    assert not sc.Robots(None, 503, "u").allowed("https://example.com/any")
    assert not sc.Robots(None, None, "u").allowed("https://example.com/any")


def test_sitemap_parser_rejects_entities_and_reads_gzip():
    body = b'<?xml version="1.0"?><urlset><url><loc>https://e.com/a</loc></url></urlset>'
    assert sc.parse_sitemap_xml(gzip.compress(body)) == ("urlset", ["https://e.com/a"])
    with pytest.raises(ValueError):
        sc.parse_sitemap_xml(b'<?xml version="1.0"?><!DOCTYPE x [<!ENTITY a "b">]><urlset/>')


def test_html_to_markdown_prefers_main_and_strips_chrome():
    html = ("<html><body><nav>Menu</nav><main><h1>Title</h1><p>Hello <a href='/x'>link</a></p>"
            "<ul><li>one<ul><li>nested</li></ul></li><li>two</li></ul></main>"
            "<footer>Foot</footer><script>var a=1;</script></body></html>")
    md = sc.html_to_markdown(html, "https://example.com/page")
    assert md.startswith("# Title")
    assert "[link](https://example.com/x)" in md
    assert "- one\n  - nested\n- two" in md
    assert "Menu" not in md and "Foot" not in md and "var a" not in md


def test_renderer_reports_missing_playwright(monkeypatch):
    import sys
    monkeypatch.setitem(sys.modules, "playwright", None)
    monkeypatch.setitem(sys.modules, "playwright.sync_api", None)
    with sc.Renderer(validator=lambda u: True) as r:
        assert r.error and "playwright not installed" in r.error
        assert r.render("https://example.com/") is None


# ----------------------------------------------------------- fixture-site tests

def test_start_url_on_loopback_blocked_by_default(site):
    assert "error" in sc.crawl_site(site + "/", max_pages=1, delay=0)
    assert "error" in sc.map_site(site + "/")
    assert "error" in sc.scrape_page(site + "/")
    assert sc.main(["crawl", site + "/", "--json"]) == 2


def test_redirects_to_private_addresses_are_blocked(site):
    fetcher = sc.Fetcher(validator=fixture_validator(site), timeout=5)
    for path, target in (("/to-metadata", "169.254.169.254"), ("/to-loopback", "127.0.0.1/admin")):
        res = fetcher.fetch(site + path)
        assert res["error"] == "blocked_by_validator", path
        assert target in res["final_url"]
        assert res["body"] == b""
        assert res["redirect_chain"][0]["status"] == 302


def test_fetch_size_cap(site):
    res = sc.Fetcher(validator=fixture_validator(site), max_bytes=100).fetch(site + "/")
    assert res["truncated"] and res["bytes"] == 100


def test_map_discovers_sitemaps_index_gzip_and_robots(site):
    out = sc.map_site(site + "/", validator=fixture_validator(site), sleep=lambda s: None)
    urls = {u["url"]: u["sources"] for u in out["urls"]}
    assert site + "/orphan.html" in urls  # from the gzipped child sitemap
    assert any(s.endswith("sitemap-extra.xml.gz") for s in urls[site + "/orphan.html"])
    assert site + "/about.html" in urls
    assert out["robots_txt"]["sitemaps"] == [site + "/sitemap.xml"]
    kinds = {f["url"].rsplit("/", 1)[-1]: f["kind"] for f in out["sitemap_files"]}
    assert kinds["sitemap.xml"] == "index" and kinds["sitemap-extra.xml.gz"] == "urlset"
    assert out["total_urls"] == 7


def test_map_link_discovery_adds_link_source(site):
    out = sc.map_site(site + "/", discover_links=True, max_pages=30, delay=0,
                      validator=fixture_validator(site), sleep=lambda s: None)
    urls = {u["url"]: u["sources"] for u in out["urls"]}
    assert "links" in urls[site + "/missing.html"]
    assert any("robots-blocked" in s for s in urls[site + "/private/secret.html"])


def test_crawl_page_record_fields(crawl, site):
    pages = {p["url"]: p for p in crawl["pages"]}
    home = pages[site + "/"]
    assert home["status"] == 200 and home["title"] == "Fixture Home"
    assert home["jsonld_types"] == ["Organization", "WebSite"]
    assert home["images_missing_alt"] == 1
    assert home["h1_count"] == 1 and home["word_count"] > 5
    assert home["external_links"] >= 1 and home["internal_links"] > 5
    assert home["canonical_is_self"] is True
    about = pages[site + "/about.html"]  # the #team fragment was stripped
    assert {h["lang"] for h in about["hreflang"]} == {"en", "sv"}
    assert crawl["summary"]["user_agent"].startswith("claude-seo-crawler/")
    assert crawl["summary"]["crawl_complete"] is True


def test_report_broken_internal_links(crawl, site):
    broken = {b["url"]: b for b in crawl["report"]["broken_internal_links"]}
    assert broken[site + "/missing.html"]["status"] == 404
    assert site + "/" in broken[site + "/missing.html"]["linked_from"]


def test_report_redirect_chains_and_loops(crawl, site):
    chains = {c["url"]: c for c in crawl["report"]["redirect_chains"]}
    assert chains[site + "/redirect-a"]["hops"] == 2
    assert chains[site + "/redirect-a"]["final_url"] == site + "/page-2.html"
    assert [h["status"] for h in chains[site + "/redirect-a"]["chain"]] == [301, 302]
    assert site + "/redirect-single" not in chains  # one hop is not a chain
    assert [l["url"] for l in crawl["report"]["redirect_loops"]] == [site + "/loop-a"]


def test_report_duplicates(crawl, site):
    titles = {d["value"]: d["urls"] for d in crawl["report"]["duplicate_titles"]}
    assert titles["Blog Post"] == [site + "/blog/post-1.html", site + "/blog/post-2.html"]
    descs = {d["value"] for d in crawl["report"]["duplicate_descriptions"]}
    assert descs == {"A blog post on the fixture site."}


def test_report_robots_blocked_and_noindex(crawl, site):
    blocked = crawl["report"]["blocked_by_robots"]
    assert [b["url"] for b in blocked] == [site + "/private/secret.html"]
    assert site + "/private/secret.html" not in {p["url"] for p in crawl["pages"]}
    noindex = {n["url"]: n for n in crawl["report"]["noindex_pages"]}
    assert noindex[site + "/noindex.html"]["meta_robots"] == "noindex, follow"
    assert noindex[site + "/header-noindex"]["x_robots_tag"] == "noindex"


def test_report_orphans_and_sitemap_canonicals(crawl, site):
    assert crawl["report"]["orphan_candidates"] == [site + "/orphan.html"]
    non_canon = crawl["report"]["non_canonical_in_sitemap"]
    assert [n["url"] for n in non_canon] == [site + "/canonical-dup.html"]
    assert non_canon[0]["canonical"] == site + "/about.html"
    issues = {i["url"]: i["issues"] for i in crawl["report"]["sitemap_url_issues"]}
    assert issues[site + "/noindex.html"] == ["noindex"]


def test_report_blocked_unsafe_redirects(crawl, site):
    blocked = {b["url"]: b for b in crawl["report"]["blocked_unsafe_urls"]}
    assert set(blocked) == {site + "/to-metadata", site + "/to-loopback"}
    assert "169.254.169.254" in blocked[site + "/to-metadata"]["final_url"]


def test_include_exclude_and_budget(site):
    out = sc.crawl_site(site + "/", max_pages=3, delay=0, use_sitemaps=False,
                        exclude=[r"/blog/"], validator=fixture_validator(site),
                        sleep=lambda s: None)
    urls = [p["url"] for p in out["pages"]]
    assert len(urls) == 3 and not any("/blog/" in u for u in urls)
    assert out["summary"]["crawl_complete"] is False
    assert out["summary"]["urls_filtered_by_include_exclude"] >= 2


def test_delay_is_applied_between_requests(site):
    waits = []
    sc.crawl_site(site + "/", max_pages=3, delay=0.5, use_sitemaps=False,
                  validator=fixture_validator(site), sleep=waits.append)
    assert waits and all(w == 0.5 for w in waits)


def test_check_external_uses_validator(site):
    out = sc.crawl_site(site + "/", max_pages=1, delay=0, use_sitemaps=False,
                        check_external=True, external_budget=5,
                        validator=lambda u: sc.host_of(u) == sc.host_of(site),
                        sleep=lambda s: None)
    checks = out["report"]["external_link_checks"]
    assert checks and checks[0]["url"] == "https://example.com/partner"
    assert checks[0]["error"] == "blocked_by_validator"  # never left the machine


def test_jsonl_output(site, tmp_path):
    path = tmp_path / "pages.jsonl"
    out = sc.crawl_site(site + "/", max_pages=4, delay=0, use_sitemaps=False,
                        validator=fixture_validator(site), jsonl_path=str(path),
                        sleep=lambda s: None)
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == out["summary"]["pages_fetched"] == 4
    assert json.loads(lines[0])["url"] == site + "/"


def test_scrape_markdown_and_record(site):
    out = sc.scrape_page(site + "/about.html", validator=fixture_validator(site))
    assert out["record"]["title"] == "About Fixture"
    assert out["robots_allowed"] is True
    md = out["markdown"]
    assert md.startswith("# About")
    assert "**fixtures**" in md and f"[tests]({site}/blog/post-1.html)" in md
    assert "| Name | Role |" in md and "| --- | --- |" in md
    assert "Home" not in md  # nav stripped


def _chromium_available():
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        return False
    try:
        with sync_playwright() as p:
            p.chromium.launch(headless=True).close()
        return True
    except Exception:
        return False


@pytest.mark.skipif(not _chromium_available(), reason="Playwright Chromium not installed")
def test_scrape_render_executes_js_and_blocks_private_requests(site):
    raw = sc.scrape_page(site + "/js.html", validator=fixture_validator(site))
    assert "Rendered by JavaScript" not in raw["markdown"]
    out = sc.scrape_page(site + "/js.html", render=True, validator=fixture_validator(site))
    assert out["render_error"] is None
    assert out["markdown"].startswith("# Rendered by JavaScript")
    assert any("169.254.169.254" in u for u in out["render_blocked_requests"])
