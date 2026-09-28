"""Tests for scripts/hreflang_check.py against a local http.server (no internet)."""

from urllib.parse import urlparse

import requests

import hreflang_check as hc
import repo_live_diff as rld
from local_http_server import LocalSite, html


def fetcher():
    s = requests.Session()
    s.trust_env = False

    def loopback_only(url):
        return urlparse(url).hostname == "127.0.0.1" or rld.default_validator(url)

    return rld.SafeFetcher(validator=loopback_only, delay=0, timeout=5, session=s)


def links(pairs):
    return "".join(f'<link rel="alternate" hreflang="{c}" href="{u}">' for c, u in pairs)


def checks(res, severity=None):
    return {(i["check"], i["page"]) for i in res["issues"]
            if severity is None or i["severity"] == severity}


def test_code_tables_and_rules():
    assert len(hc.ISO_639_1) == 183 and len(hc.ISO_3166_1) == 249
    assert hc.validate_code("en-GB") == [] and hc.validate_code("x-default") == []
    assert hc.validate_code("zh-Hant") == [] and hc.validate_code("zh-Hans-US") == []
    assert hc.validate_code("en-uk")[0][0] == "error"          # reserved, use GB
    assert hc.validate_code("es-419")[0][0] == "error"         # not supported by Google
    assert hc.validate_code("eng")[0][0] == "error"            # ISO 639-2
    assert hc.validate_code("SE")[0][0] == "warning"           # Northern Sami, not Sweden
    assert hc.validate_code("US")[0][0] == "error"             # region alone
    assert hc.validate_code("en-gb")[0][0] == "info"           # case-insensitive


def test_link_header_parsing():
    v = ('<https://example.com/file.pdf>; rel="alternate"; hreflang="en", '
         '<https://de.example.com/file.pdf>; rel="alternate"; hreflang="de", '
         '<https://example.com/style.css>; rel=preload')
    got = hc.parse_link_header(v)
    assert [(g["hreflang"], g["href"]) for g in got] == [
        ("en", "https://example.com/file.pdf"), ("de", "https://de.example.com/file.pdf")]


def test_valid_cluster_has_no_errors():
    with LocalSite() as site:
        b = site.base_url
        pairs = [("en", f"{b}/en/"), ("sv-SE", f"{b}/sv/"), ("x-default", f"{b}/en/")]
        site.routes["/en/"] = html("EN", "<p>Hello</p>", links(pairs))
        site.routes["/sv/"] = html("SV", "<p>Hej</p>", links(pairs))
        res = hc.run_check(f"{b}/en/", fetcher())
    assert res["exit_code"] == 0, res["issues"]
    assert res["summary"]["pages_checked"] == 2
    assert not checks(res, "error")


def test_broken_cluster_reports_each_rule():
    with LocalSite() as site:
        b = site.base_url
        en = [("en", f"{b}/en/"), ("de", f"{b}/de/"), ("fr", f"{b}/fr/"),
              ("es-419", f"{b}/es/"), ("it", "/it/"), ("nl", f"{b}/old-nl"),
              ("en", f"{b}/en-alt/")]
        site.routes["/en/"] = html("EN", "", links(en))
        # de: no return link to /en/ and no self reference
        site.routes["/de/"] = html("DE", "", links([("fr", f"{b}/fr/")]))
        # fr: canonical points elsewhere
        site.routes["/fr/"] = html("FR", "", links([("en", f"{b}/en/"), ("fr", f"{b}/fr/")])
                                   + f'<link rel="canonical" href="{b}/fr/main">')
        site.routes["/old-nl"] = (301, {"Location": f"{b}/nl/"}, "")
        site.routes["/nl/"] = html("NL", "", links([("en", f"{b}/en/"), ("nl", f"{b}/nl/")]))
        res = hc.run_check(f"{b}/en/", fetcher())
    errs = checks(res, "error")
    en_url, de_url, fr_url = f"{b}/en/", f"{b}/de/", f"{b}/fr/"
    assert ("missing-return-link", en_url) in errs          # de does not link back
    assert ("missing-self-reference", de_url) in errs
    assert ("non-canonical-with-hreflang", fr_url) in errs
    assert ("target-non-canonical", en_url) in errs
    assert ("relative-url", en_url) in errs
    assert ("duplicate-code", en_url) in errs
    assert ("code", en_url) in errs                          # es-419
    assert ("target-status", en_url) in errs                 # /es/ is 404, /en-alt/ is 404
    assert ("target-redirects", en_url) in checks(res, "warning")
    assert ("no-x-default", en_url) in checks(res, "info")
    assert res["exit_code"] == 1


def test_http_header_and_sitemap_sources():
    with LocalSite() as site:
        b = site.base_url
        hdr = f'<{b}/file.pdf>; rel="alternate"; hreflang="en", <{b}/de/file.pdf>; rel="alternate"; hreflang="de"'
        site.routes["/file.pdf"] = (200, {"Content-Type": "application/pdf", "Link": hdr}, "%PDF")
        site.routes["/de/file.pdf"] = (200, {"Content-Type": "application/pdf", "Link": hdr}, "%PDF")
        site.routes["/robots.txt"] = (200, {"Content-Type": "text/plain"}, "User-agent: *\n")
        alt = (f'<xhtml:link rel="alternate" hreflang="en" href="{b}/a"/>'
               f'<xhtml:link rel="alternate" hreflang="fi" href="{b}/b"/>')
        site.routes["/sitemap.xml"] = (200, {"Content-Type": "application/xml"},
                                       '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/'
                                       'schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">'
                                       f"<url><loc>{b}/a</loc>{alt}</url>"
                                       f"<url><loc>{b}/b</loc>{alt}</url></urlset>")
        site.routes["/a"] = html("A", "")
        site.routes["/b"] = html("B", "")
        pdf = hc.run_check(f"{b}/file.pdf", fetcher())
        sm = hc.run_check(f"{b}/a", fetcher(), crawl_sitemap=True)
    assert pdf["exit_code"] == 0, pdf["issues"]
    assert {a["source"] for a in pdf["pages"][0]["annotations"]} == {"http_header"}
    assert sm["sitemap"]["urls_with_hreflang"] == 2
    assert sm["exit_code"] == 0, sm["issues"]
    assert sm["summary"]["pages_checked"] == 2


def test_redirect_to_metadata_ip_is_refused():
    with LocalSite() as site:
        site.routes["/"] = (302, {"Location": "http://169.254.169.254/computeMetadata/v1/"}, "")
        res = hc.run_check(site.base_url + "/", fetcher())
    assert res["exit_code"] == 2 and "169.254.169.254" in res["error"]
