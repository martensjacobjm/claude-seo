#!/usr/bin/env python3
"""
Hreflang validator: HTML <link>, HTTP Link headers and sitemap xhtml:link.

Rules follow Google Search Central, "Tell Google about localized versions of
your page" (https://developers.google.com/search/docs/specialty/international/localized-versions,
page last updated 2026-09-21, verified 2026-09-28):

* Each language version must list itself as well as all other versions
  (self-reference; the set is identical on every version).
* Alternate URLs must be fully qualified (``https://example.com/foo``, not
  ``//example.com/foo`` or ``/foo``); they may be on other domains.
* If two pages don't both point to each other, the tags are ignored
  (return links). Google still processes the pairs that do link back.
* Codes: ISO 639-1 language, optional ISO 15924 script (``zh-Hant``),
  optional ISO 3166-1 alpha-2 region. Other codes such as ``es-419`` are not
  supported; a region alone is invalid; reserved codes (``EU``, ``UN``,
  ``UK``) are ignored by Google. Values are case-insensitive.
* ``x-default`` is recommended (not required) as the fallback for unmatched
  languages.
* When several locales share a language (``en-IE``, ``en-CA``), a generic
  ``en`` page is a good idea.
* <link> tags must be inside a well-formed <head>; don't combine hreflang
  with other attributes such as ``media`` on one <link>.

Additional heuristics (not on that page): hreflang on a URL whose
rel=canonical points elsewhere, alternates that redirect or return non-200,
duplicate codes pointing at different URLs, mixed http/https, and
inconsistent sets between HTML, headers and sitemap.

All fetches go through repo_live_diff.SafeFetcher (the shared
safe_fetch.SafeFetcher with a 1 s default delay): every redirect hop is
validated with validate_url() from google_auth.py and a resolved-IP check,
and connections are pinned to the validated IP.

Exit codes: 0 = no errors, 1 = at least one error-severity issue,
2 = start URL blocked/unreachable or bad arguments.

Usage:
    python hreflang_check.py https://example.com/
    python hreflang_check.py https://example.com/ --crawl-sitemap --max-pages 100
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse, urlunparse

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
from google_auth import validate_url  # noqa: E402
from repo_live_diff import SafeFetcher, extract, fetch_sitemaps  # noqa: E402

GOOGLE_DOC = "https://developers.google.com/search/docs/specialty/international/localized-versions"

# ISO 639-1 (183 codes, 2021+; "bh" was withdrawn).
ISO_639_1 = frozenset("""
aa ab ae af ak am an ar as av ay az ba be bg bi bm bn bo br bs ca ce ch co cr cs cu cv cy
da de dv dz ee el en eo es et eu fa ff fi fj fo fr fy ga gd gl gn gu gv ha he hi ho hr ht
hu hy hz ia id ie ig ii ik io is it iu ja jv ka kg ki kj kk kl km kn ko kr ks ku kv kw ky
la lb lg li ln lo lt lu lv mg mh mi mk ml mn mr ms mt my na nb nd ne ng nl nn no nr nv ny
oc oj om or os pa pi pl ps pt qu rm rn ro ru rw sa sc sd se sg si sk sl sm sn so sq sr ss
st su sv sw ta te tg th ti tk tl tn to tr ts tt tw ty ug uk ur uz ve vi vo wa wo xh yi yo
za zh zu
""".split())

# ISO 3166-1 alpha-2 officially assigned (249 codes).
ISO_3166_1 = frozenset("""
AD AE AF AG AI AL AM AO AQ AR AS AT AU AW AX AZ BA BB BD BE BF BG BH BI BJ BL BM BN BO BQ
BR BS BT BV BW BY BZ CA CC CD CF CG CH CI CK CL CM CN CO CR CU CV CW CX CY CZ DE DJ DK DM
DO DZ EC EE EG EH ER ES ET FI FJ FK FM FO FR GA GB GD GE GF GG GH GI GL GM GN GP GQ GR GS
GT GU GW GY HK HM HN HR HT HU ID IE IL IM IN IO IQ IR IS IT JE JM JO JP KE KG KH KI KM KN
KP KR KW KY KZ LA LB LC LI LK LR LS LT LU LV LY MA MC MD ME MF MG MH MK ML MM MN MO MP MQ
MR MS MT MU MV MW MX MY MZ NA NC NE NF NG NI NL NO NP NR NU NZ OM PA PE PF PG PH PK PL PM
PN PR PS PT PW PY QA RE RO RS RU RW SA SB SC SD SE SG SH SI SJ SK SL SM SN SO SR SS ST SV
SX SY SZ TC TD TF TG TH TJ TK TL TM TN TO TR TT TV TW TZ UA UG UM US UY UZ VA VC VE VG VI
VN VU WF WS YE YT ZA ZM ZW
""".split())

# Reserved / exceptionally reserved / user-assigned: Google ignores these regions.
RESERVED_REGIONS = frozenset({"UK", "EU", "UN", "EZ", "AA", "ZZ", "XK", "AC", "CP", "DG", "EA",
                              "FX", "IC", "SU", "TA"}
                             | {f"Q{c}" for c in "MNOPQRSTUVWXYZ"}
                             | {f"X{c}" for c in "ABCDEFGHIJLMNOPQRSTUVWXYZ"})

# ISO 15924 scripts commonly used in hreflang (others are reported as a warning).
ISO_15924_COMMON = frozenset("""
Adlm Arab Armn Beng Bopo Brai Cans Cher Cyrl Deva Ethi Geor Grek Gujr Guru Hang Hani Hans
Hant Hebr Hira Jpan Kana Khmr Knda Kore Laoo Latn Mlym Mong Mymr Olck Orya Sinh Syrc Taml
Telu Tfng Thaa Thai Tibt Vaii Yiii
""".split())

# Frequent mistakes -> suggestion.
LANG_HINTS = {
    "jp": "ja (Japanese)", "cn": "zh (Chinese)", "dk": "da (Danish)", "gr": "el (Greek)",
    "cz": "cs (Czech)", "ua": "uk (Ukrainian)", "iw": "he (Hebrew)", "in": "id (Indonesian)",
    "ji": "yi (Yiddish)", "eng": "en", "ger": "de", "deu": "de", "fre": "fr", "fra": "fr",
    "swe": "sv", "spa": "es", "nor": "no/nb", "dan": "da", "fin": "fi",
    "vn": "vi (Vietnamese)",
}
AMBIGUOUS_LANG = {
    "se": "'se' is Northern Sami; Swedish is 'sv' (Sweden as region: sv-SE)",
    "be": "'be' is Belarusian; Belgium is a region, e.g. nl-BE/fr-BE/de-BE",
    "ee": "'ee' is Ewe; Estonian is 'et'", "si": "'si' is Sinhala; Slovenian is 'sl'",
}


def validate_code(code: str) -> List[Tuple[str, str]]:
    """Validate one hreflang value. Returns [(severity, message)]."""
    issues: List[Tuple[str, str]] = []
    raw = (code or "").strip()
    if not raw:
        return [("error", "empty hreflang value")]
    if raw.lower() == "x-default":
        return []
    if "_" in raw:
        issues.append(("error", f"'{raw}' uses '_' ; hreflang uses '-' (e.g. en-GB)"))
        raw = raw.replace("_", "-")
    parts = raw.split("-")
    lang = parts[0].lower()
    if lang.upper() in ISO_3166_1 and lang not in ISO_639_1 and len(parts) == 1:
        hint = LANG_HINTS.get(lang)
        issues.append(("error", f"'{raw}': a region alone is not valid; the first code must be a "
                                "language (ISO 639-1)" + (f"; did you mean {hint}?" if hint else "")))
        return issues
    if lang not in ISO_639_1:
        hint = LANG_HINTS.get(lang)
        issues.append(("error", f"'{raw}': '{lang}' is not an ISO 639-1 language code"
                                + (f"; did you mean {hint}?" if hint else "")))
        return issues
    if len(parts) == 1 and lang in AMBIGUOUS_LANG:
        issues.append(("info", f"'{raw}': {AMBIGUOUS_LANG[lang]}"))
    rest = parts[1:]
    if rest and len(rest[0]) == 4 and rest[0].isalpha():
        script = rest[0].title()
        if script not in ISO_15924_COMMON:
            issues.append(("warning", f"'{raw}': script '{rest[0]}' not in the common ISO 15924 list"))
        rest = rest[1:]
    if len(rest) > 1:
        issues.append(("error", f"'{raw}': too many subtags (language[-Script][-REGION] only)"))
        return issues
    if rest:
        region = rest[0]
        up = region.upper()
        if region.isdigit():
            issues.append(("error", f"'{raw}': numeric region '{region}' (UN M.49) is not supported "
                                    "by Google; use ISO 3166-1 alpha-2 country codes"))
        elif up in RESERVED_REGIONS:
            hint = " (use GB)" if up == "UK" else ""
            issues.append(("error", f"'{raw}': '{up}' is a reserved code; Google ignores it{hint}"))
        elif up not in ISO_3166_1:
            issues.append(("error", f"'{raw}': '{region}' is not an ISO 3166-1 alpha-2 region"))
        elif region != up:
            issues.append(("info", f"'{raw}': case-insensitive, but ISO convention is uppercase "
                                   f"region ({lang}-{up})"))
    return issues


def parse_link_header(value: str) -> List[dict]:
    """Parse an HTTP Link header into [{href, rel, hreflang}] (hreflang ones only)."""
    out = []
    if not value:
        return out
    for part in re.findall(r"<[^>]*>[^,<]*(?:\"[^\"]*\"[^,<]*)*", value):
        m = re.match(r"<([^>]*)>(.*)", part.strip(), re.S)
        if not m:
            continue
        href, params = m.group(1).strip(), m.group(2)
        attrs = dict((k.lower(), v.strip('"').strip())
                     for k, v in re.findall(r";\s*([\w\-]+)\s*=\s*(\"[^\"]*\"|[^;,\s]+)", params))
        if "hreflang" in attrs and "alternate" in attrs.get("rel", "").lower().split():
            out.append({"href": href, "hreflang": attrs["hreflang"], "rel": attrs.get("rel")})
    return out


def norm_url(url: str) -> str:
    """Normalize for comparison: lowercase scheme/host, drop fragment and default port."""
    p = urlparse(url.strip())
    netloc = (p.hostname or "").lower()
    if p.port and not ((p.scheme == "http" and p.port == 80) or (p.scheme == "https" and p.port == 443)):
        netloc += f":{p.port}"
    return urlunparse((p.scheme.lower(), netloc, p.path or "/", "", p.query, ""))


def is_absolute(href: str) -> bool:
    p = urlparse(href)
    return p.scheme in ("http", "https") and bool(p.netloc)


class HreflangChecker:
    """Collect annotations for a cluster of alternates and validate them."""

    def __init__(self, fetcher: SafeFetcher, max_pages: int = 50) -> None:
        self.fetcher = fetcher
        self.max_pages = max_pages
        self.pages: Dict[str, dict] = {}
        self.sitemap_ann: Dict[str, List[dict]] = {}
        self.issues: List[dict] = []

    def issue(self, severity: str, check: str, page: Optional[str], detail: str) -> None:
        self.issues.append({"severity": severity, "check": check, "page": page, "detail": detail})

    def load(self, url: str) -> dict:
        """Fetch and parse a page once."""
        key = norm_url(url)
        if key in self.pages:
            return self.pages[key]
        res = self.fetcher.get(url)
        page = {"url": url, "status": res["status"], "final_url": res["final_url"],
                "redirected": bool(res["hops"]), "error": res["error"], "blocked": res["blocked"],
                "canonical": None, "html": [], "header": [], "annotations": []}
        if res["status"] is not None and 200 <= res["status"] < 300:
            ctype = res["headers"].get("content-type", "")
            if "html" in ctype or not ctype:
                ex = extract(res["text"])
                page["canonical"] = urljoin(res["final_url"], ex["canonical"]) if ex["canonical"] else None
                page["html"] = [dict(a, source="html") for a in ex["hreflang"]]
            page["header"] = [dict(a, source="http_header")
                              for a in parse_link_header(res["headers"].get("link", ""))]
        page["annotations"] = page["html"] + page["header"] + [
            dict(a, source="sitemap") for a in self.sitemap_ann.get(key, [])]
        self.pages[key] = page
        return page

    def load_sitemaps(self, base_url: str) -> dict:
        data = fetch_sitemaps(self.fetcher, base_url)
        for e in data["entries"]:
            if e["alternates"]:
                self.sitemap_ann[norm_url(e["loc"])] = e["alternates"]
        return {"sources": data["sources"], "errors": data["errors"],
                "urls_with_hreflang": len(self.sitemap_ann)}

    def crawl(self, start_urls: List[str]) -> None:
        queue = list(start_urls)
        expanded: set = set()
        while queue:
            url = queue.pop(0)
            key = norm_url(url)
            if key in expanded:
                continue
            if key not in self.pages and len(self.pages) >= self.max_pages:
                queue.insert(0, url)
                break
            expanded.add(key)
            page = self.load(url)
            for a in page["annotations"]:
                if is_absolute(a["href"]) and norm_url(a["href"]) not in expanded:
                    queue.append(a["href"])
        queue = [u for u in queue if norm_url(u) not in expanded]
        if queue:
            self.issue("info", "crawl-limit", None,
                       f"stopped after {self.max_pages} pages; {len(queue)} alternates not fetched")

    def validate(self) -> None:  # noqa: C901 - one pass per documented rule
        for key, page in self.pages.items():
            url = page["url"]
            anns = page["annotations"]
            if page["blocked"]:
                self.issue("error", "target-blocked", url, page["error"])
                continue
            if not anns:
                continue
            # 1. codes
            for a in anns:
                for sev, msg in validate_code(a["hreflang"]):
                    self.issue(sev, "code", url, f"{msg} [{a['source']}]")
                if a["source"] == "html" and not a.get("in_head", True):
                    self.issue("error", "link-outside-head", url,
                               f"hreflang {a['hreflang']} appears after <body>; Google reads it only in <head>")
                if a["source"] == "html" and a.get("extra_attrs"):
                    self.issue("warning", "combined-attributes", url,
                               f"hreflang {a['hreflang']} <link> also has {a['extra_attrs']}; "
                               "don't combine hreflang with attributes such as media")
            # 2. relative URLs
            for a in anns:
                if not is_absolute(a["href"]):
                    self.issue("error", "relative-url", url,
                               f"hreflang {a['hreflang']} href '{a['href']}' is not fully qualified "
                               "(must include https:// and host)")
            absolute = [a for a in anns if is_absolute(a["href"])]
            # 3. duplicates
            by_code: Dict[str, set] = {}
            dup_codes: set = set()
            for src in ("html", "http_header", "sitemap"):
                seen: Dict[str, set] = {}
                for a in absolute:
                    if a["source"] == src:
                        seen.setdefault(a["hreflang"].lower(), set()).add(norm_url(a["href"]))
                for code, hrefs in seen.items():
                    by_code.setdefault(code, set()).update(hrefs)
                    if len(hrefs) > 1:
                        dup_codes.add(code)
                        self.issue("error", "duplicate-code", url,
                                   f"'{code}' points to {len(hrefs)} different URLs in {src}")
            for code, hrefs in by_code.items():
                if len(hrefs) > 1 and code not in dup_codes:
                    self.issue("warning", "conflicting-sources", url,
                               f"'{code}' maps to different URLs across HTML/header/sitemap")
            # 4. self-reference
            targets = {norm_url(a["href"]) for a in absolute}
            own = {norm_url(url), norm_url(page["final_url"])}
            if not (own & targets):
                self.issue("error", "missing-self-reference", url,
                           "the page does not list itself; each version must list itself and all others")
            # 5. canonical conflict
            if page["canonical"] and norm_url(page["canonical"]) not in own:
                self.issue("error", "non-canonical-with-hreflang", url,
                           f"page has hreflang but rel=canonical points to {page['canonical']}")
            # 6. x-default / generic language fallback
            codes = {a["hreflang"].lower() for a in anns}
            if "x-default" not in codes:
                self.issue("info", "no-x-default", url,
                           "no x-default; recommended as fallback for unmatched languages")
            langs_with_region: Dict[str, int] = {}
            for c in codes:
                if "-" in c and c != "x-default":
                    langs_with_region[c.split("-")[0]] = langs_with_region.get(c.split("-")[0], 0) + 1
            for lang, n in langs_with_region.items():
                if n > 1 and lang not in codes:
                    self.issue("info", "no-generic-language", url,
                               f"{n} '{lang}-XX' variants but no generic '{lang}' page")
            # 7. protocol mix
            schemes = {urlparse(a["href"]).scheme for a in absolute}
            if len(schemes) > 1:
                self.issue("warning", "mixed-protocols", url, "hreflang set mixes http and https")
            # 8. targets + return links
            for a in absolute:
                tkey = norm_url(a["href"])
                if tkey in own:
                    continue
                target = self.pages.get(tkey)
                if target is None:
                    continue  # not fetched (crawl limit)
                if target["blocked"]:
                    continue
                if target["status"] is None or not 200 <= target["status"] < 300:
                    self.issue("error", "target-status", url,
                               f"{a['hreflang']} -> {a['href']} returned {target['status'] or target['error']}")
                    continue
                if target["redirected"]:
                    self.issue("warning", "target-redirects", url,
                               f"{a['hreflang']} -> {a['href']} redirects to {target['final_url']}; "
                               "use the final URL")
                if target["canonical"] and norm_url(target["canonical"]) not in (
                        tkey, norm_url(target["final_url"])):
                    self.issue("error", "target-non-canonical", url,
                               f"{a['hreflang']} -> {a['href']} canonicalises to {target['canonical']}")
                back = {norm_url(b["href"]) for b in target["annotations"] if is_absolute(b["href"])}
                if not (own & back):
                    self.issue("error", "missing-return-link", url,
                               f"{a['hreflang']} -> {a['href']} does not link back; Google ignores "
                               "hreflang pairs that are not bidirectional")
            # 9. set consistency across the cluster
        sets = {}
        for page in self.pages.values():
            s = frozenset((a["hreflang"].lower(), norm_url(a["href"]))
                          for a in page["annotations"] if is_absolute(a["href"]))
            if s:
                sets[page["url"]] = s
        if len(set(sets.values())) > 1:
            self.issue("warning", "inconsistent-sets", None,
                       f"{len(set(sets.values()))} different hreflang sets across {len(sets)} pages; "
                       "the set should be identical on every version")


def run_check(url: str, fetcher: Optional[SafeFetcher] = None, crawl_sitemap: bool = False,
              max_pages: int = 50) -> dict:
    """Run the full check for url and return the JSON-serialisable result."""
    fetcher = fetcher or SafeFetcher(delay=1.0)
    chk = HreflangChecker(fetcher, max_pages=max_pages)
    result: dict = {"tool": "hreflang_check", "url": url, "reference": GOOGLE_DOC,
                    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    if crawl_sitemap:
        result["sitemap"] = chk.load_sitemaps(url)
    start = chk.load(url)
    if start["blocked"] or start["status"] is None:
        result.update(error=start["error"] or "unreachable", exit_code=2)
        return result
    starts = [url] + ([u for u in list(chk.sitemap_ann)] if crawl_sitemap else [])
    chk.crawl(starts)
    chk.validate()
    result["pages"] = [{"url": p["url"], "status": p["status"], "final_url": p["final_url"],
                        "canonical": p["canonical"],
                        "annotations": [{k: a.get(k) for k in ("hreflang", "href", "source")}
                                        for a in p["annotations"]]}
                       for p in chk.pages.values()]
    counts: Dict[str, int] = {}
    for i in chk.issues:
        counts[i["severity"]] = counts.get(i["severity"], 0) + 1
    result["issues"] = chk.issues
    result["summary"] = {"pages_checked": len(chk.pages), "issues": counts,
                         "annotations_found": sum(len(p["annotations"]) for p in chk.pages.values())}
    if not result["summary"]["annotations_found"]:
        result["summary"]["note"] = "no hreflang annotations found (HTML, Link header or sitemap)"
    result["exit_code"] = 1 if counts.get("error") else 0
    return result


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Validate hreflang (HTML, HTTP headers, sitemap).")
    parser.add_argument("url", help="Page URL to start from")
    parser.add_argument("--crawl-sitemap", action="store_true",
                        help="Also read robots.txt/sitemap.xml xhtml:link annotations and check those URLs")
    parser.add_argument("--max-pages", type=int, default=50, help="Max pages to fetch (default 50)")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds between requests")
    parser.add_argument("--timeout", type=float, default=20.0, help="Request timeout in seconds")
    args = parser.parse_args(argv)
    if not validate_url(args.url):
        print(json.dumps({"error": f"invalid or blocked URL: {args.url}"}))
        return 2
    res = run_check(args.url, SafeFetcher(delay=args.delay, timeout=args.timeout),
                    crawl_sitemap=args.crawl_sitemap, max_pages=args.max_pages)
    print(json.dumps(res, indent=2, ensure_ascii=False))
    return res["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
