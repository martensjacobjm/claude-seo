#!/usr/bin/env python3
"""
Compare a local static-site folder (usually a git repo) with the live site.

Answers the question "is this repo really what is deployed?" before anyone
runs an upload script. A repository that is older than the live site will
silently overwrite newer content when it is deployed by SFTP/FTP.

What it does:

1. Maps local HTML files to URLs: ``index.html`` -> ``/``, ``dir/index.html``
   -> ``/dir/``, ``foo.html`` -> ``/foo.html`` (with ``--clean-urls`` both
   ``/foo`` and ``/foo.html`` are tried, clean form first).
2. Fetches each live URL politely (``--delay`` between requests, default 1 s)
   and validates EVERY redirect hop with ``validate_url()`` from
   ``google_auth.py`` plus a DNS check that the host resolves to a public IP
   (SSRF protection: private, loopback, link-local and metadata addresses
   such as 169.254.169.254 are refused).
3. Compares per page: live status, title, meta description, canonical, H1,
   JSON-LD @types, a normalized visible-text hash and a difflib similarity
   ratio, and records Last-Modified / ETag headers.
4. Reads the live ``/sitemap.xml`` and any ``Sitemap:`` lines in robots.txt
   and lists live URLs that have no local file.
5. Gives a verdict with evidence: "in sync", "repo appears older",
   "repo appears newer" or "diverged". Date evidence compares the live
   Last-Modified header (or sitemap <lastmod>) with the local file's last
   commit date (``git log -1 --format=%cI -- file``) or mtime, and the latest
   year mentioned in the visible text on each side.

Exit codes (so it can gate a deploy script):
    0  in sync (or "repo appears newer" when --allow-newer is given)
    1  differences found (older / newer / diverged): do not deploy blindly
    2  fatal error (bad arguments, base URL blocked or unreachable)

Usage:
    python repo_live_diff.py ./site https://example.com
    python repo_live_diff.py ./site https://example.com --clean-urls --delay 2
    python repo_live_diff.py ./site https://example.com --text
"""

from __future__ import annotations

import argparse
import difflib
import fnmatch
import hashlib
import ipaddress
import json
import os
import re
import socket
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from typing import Callable, Dict, List, Optional, Tuple
from urllib.parse import quote, unquote, urljoin, urlparse

try:
    import requests
except ImportError:
    print(json.dumps({"error": "requests library required: pip install requests"}))
    sys.exit(2)

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
from google_auth import validate_url  # noqa: E402

USER_AGENT = ("Mozilla/5.0 (compatible; ClaudeSEO-SiteSafety/1.0; "
              "+https://github.com/AgriciDaniel/claude-seo)")
REDIRECT_CODES = {301, 302, 303, 307, 308}
MAX_BODY_BYTES = 5_000_000
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "__pycache__", ".github"}


# --- safe fetching ---------------------------------------------------------------

def resolves_public(url: str) -> bool:
    """True unless the host resolves to a non-public address.

    DNS failures return True so the request itself reports the error; the
    string-level validate_url() check has already run.
    """
    host = urlparse(url).hostname
    if not host:
        return False
    try:
        infos = socket.getaddrinfo(host, None)
    except (socket.gaierror, UnicodeError, OSError):
        return True
    for info in infos:
        try:
            ip = ipaddress.ip_address(info[4][0].split("%", 1)[0])
        except ValueError:
            continue
        if not ip.is_global or ip.is_multicast:
            return False
    return True


def default_validator(url: str) -> bool:
    """validate_url() from google_auth.py plus a resolved-IP check."""
    return validate_url(url) and resolves_public(url)


class SafeFetcher:
    """HTTP GET with per-hop URL validation, polite delay and a body cap.

    ``validator`` and ``session`` are injectable so tests can talk to a local
    http.server without weakening the production validator.
    """

    def __init__(self, validator: Optional[Callable[[str], bool]] = None,
                 delay: float = 1.0, timeout: float = 20.0, max_redirects: int = 5,
                 session: Optional["requests.Session"] = None,
                 user_agent: str = USER_AGENT) -> None:
        self.validator = validator or default_validator
        self.delay = max(0.0, delay)
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.session = session or requests.Session()
        self.headers = {"User-Agent": user_agent,
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
        self._last: Dict[str, float] = {}
        self.requests_made = 0

    def _wait(self, host: str) -> None:
        last = self._last.get(host)
        if last is not None and self.delay:
            remaining = self.delay - (time.monotonic() - last)
            if remaining > 0:
                time.sleep(remaining)
        self._last[host] = time.monotonic()

    def get(self, url: str) -> dict:
        """Fetch url following redirects manually; every hop is validated."""
        result = {"url": url, "final_url": url, "status": None, "headers": {}, "text": "",
                  "hops": [], "error": None, "blocked": False}
        current = url
        for _ in range(self.max_redirects + 1):
            if not self.validator(current):
                result.update(final_url=current, blocked=True,
                              error=f"blocked: {current} failed URL validation "
                                    "(private, loopback, link-local or metadata address)")
                return result
            self._wait(urlparse(current).netloc)
            try:
                self.requests_made += 1
                resp = self.session.get(current, headers=self.headers, timeout=self.timeout,
                                        allow_redirects=False, stream=True)
            except requests.RequestException as exc:
                result.update(final_url=current, error=f"{type(exc).__name__}: {exc}"[:300])
                return result
            loc = resp.headers.get("Location")
            if resp.status_code in REDIRECT_CODES and loc:
                nxt = urljoin(current, loc)
                result["hops"].append({"url": current, "status": resp.status_code, "location": nxt})
                resp.close()
                current = nxt
                continue
            body = b""
            try:
                for chunk in resp.iter_content(65536):
                    body += chunk
                    if len(body) > MAX_BODY_BYTES:
                        break
            except requests.RequestException as exc:
                result["error"] = f"read error: {exc}"[:300]
            finally:
                resp.close()
            result.update(final_url=current, status=resp.status_code,
                          headers={k.lower(): v for k, v in resp.headers.items()},
                          text=_decode(body, resp.headers.get("Content-Type", "")))
            return result
        result.update(final_url=current, error=f"too many redirects (> {self.max_redirects})")
        return result


def _decode(body: bytes, content_type: str) -> str:
    m = re.search(r"charset=([\w\-]+)", content_type or "", re.I)
    if m:
        try:
            return body.decode(m.group(1), errors="replace")
        except LookupError:
            pass
    head = body[:2048].decode("ascii", errors="ignore")
    m = re.search(r"<meta[^>]+charset=[\"']?([\w\-]+)", head, re.I)
    for enc in ([m.group(1)] if m else []) + ["utf-8"]:
        try:
            return body.decode(enc)
        except (LookupError, UnicodeDecodeError):
            continue
    return body.decode("latin-1", errors="replace")


# --- HTML extraction --------------------------------------------------------------

class PageExtractor(HTMLParser):
    """Collect SEO-relevant elements and visible text with the stdlib parser."""

    SKIP_TEXT = {"script", "style", "noscript", "template", "svg", "head", "title"}
    VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta",
            "param", "source", "track", "wbr"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.title: Optional[str] = None
        self.meta_description: Optional[str] = None
        self.meta_robots: Optional[str] = None
        self.canonicals: List[str] = []
        self.h1: List[str] = []
        self.lang: Optional[str] = None
        self.hreflang: List[dict] = []
        self._jsonld: List[str] = []
        self._text: List[str] = []
        self._stack: List[str] = []
        self._in_head = False
        self._seen_body = False
        self._title_buf: Optional[List[str]] = None
        self._h1_buf: Optional[List[str]] = None
        self._jsonld_buf: Optional[List[str]] = None

    def handle_starttag(self, tag, attrs):  # noqa: C901 - flat dispatch
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html":
            self.lang = a.get("lang") or self.lang
        elif tag == "head":
            self._in_head = True
        elif tag == "body":
            self._in_head, self._seen_body = False, True
        elif tag == "title" and self.title is None:
            self._title_buf = []
        elif tag == "meta":
            name = a.get("name", "").lower()
            if name == "description" and self.meta_description is None:
                self.meta_description = a.get("content", "").strip()
            elif name == "robots":
                self.meta_robots = a.get("content", "").strip()
        elif tag == "link":
            rels = a.get("rel", "").lower().split()
            if "canonical" in rels and a.get("href"):
                self.canonicals.append(a["href"].strip())
            if "alternate" in rels and "hreflang" in a:
                self.hreflang.append({
                    "hreflang": a.get("hreflang", "").strip(), "href": a.get("href", "").strip(),
                    "in_head": not self._seen_body,
                    "extra_attrs": sorted(k for k in a if k not in {"rel", "hreflang", "href"}),
                })
        elif tag == "h1":
            self._h1_buf = []
        elif tag == "script" and "ld+json" in a.get("type", "").lower():
            self._jsonld_buf = []
        if tag not in self.VOID:
            self._stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in self.VOID and self._stack and self._stack[-1] == tag:
            self._stack.pop()

    def handle_endtag(self, tag):
        if tag == "head":
            self._in_head = False
        elif tag == "title" and self._title_buf is not None:
            self.title = _ws(" ".join(self._title_buf))
            self._title_buf = None
        elif tag == "h1" and self._h1_buf is not None:
            self.h1.append(_ws(" ".join(self._h1_buf)))
            self._h1_buf = None
        elif tag == "script" and self._jsonld_buf is not None:
            self._jsonld.append("".join(self._jsonld_buf))
            self._jsonld_buf = None
        if tag in self._stack:
            while self._stack:
                if self._stack.pop() == tag:
                    break

    def handle_data(self, data):
        if self._title_buf is not None:
            self._title_buf.append(data)
        if self._h1_buf is not None:
            self._h1_buf.append(data)
        if self._jsonld_buf is not None:
            self._jsonld_buf.append(data)
            return
        if self._in_head or any(t in self.SKIP_TEXT for t in self._stack):
            return
        self._text.append(data)

    @property
    def visible_text(self) -> str:
        return _ws(" ".join(self._text))

    @property
    def jsonld_types(self) -> List[str]:
        types: set = set()

        def walk(node):
            if isinstance(node, dict):
                t = node.get("@type")
                if isinstance(t, str):
                    types.add(t)
                elif isinstance(t, list):
                    types.update(x for x in t if isinstance(x, str))
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        for raw in self._jsonld:
            try:
                walk(json.loads(raw))
            except ValueError:
                types.add("<invalid JSON-LD>")
        return sorted(types)


def _ws(s: str) -> str:
    return re.sub(r"\s+", " ", s or "").strip()


def extract(html: str) -> dict:
    """Parse HTML and return the comparable fields."""
    p = PageExtractor()
    try:
        p.feed(html or "")
        p.close()
    except Exception:  # html.parser is lenient; never let a bad page abort the run
        pass
    text = p.visible_text
    years = [int(y) for y in re.findall(r"\b(20[0-9]{2})\b", text)]
    return {
        "title": p.title, "meta_description": p.meta_description,
        "canonical": p.canonicals[0] if p.canonicals else None,
        "h1": p.h1, "jsonld_types": p.jsonld_types, "lang": p.lang,
        "meta_robots": p.meta_robots, "hreflang": p.hreflang,
        "text_hash": hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
        "word_count": len(text.split()), "latest_year_in_text": max(years) if years else None,
        "_text": text,
    }


def similarity(a: str, b: str) -> float:
    """difflib ratio on word sequences (0..1)."""
    wa, wb = a.split(), b.split()
    if not wa and not wb:
        return 1.0
    return round(difflib.SequenceMatcher(None, wa, wb, autojunk=False).ratio(), 4)


# --- local side -------------------------------------------------------------------

def local_pages(root: str, clean_urls: bool, exclude: List[str]) -> List[dict]:
    """List local HTML files with candidate URL paths."""
    pages = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS and not d.startswith("."))
        for name in sorted(filenames):
            if not name.lower().endswith((".html", ".htm")):
                continue
            rel = os.path.relpath(os.path.join(dirpath, name), root).replace(os.sep, "/")
            if any(fnmatch.fnmatch(rel, pat) or fnmatch.fnmatch(name, pat) for pat in exclude):
                continue
            pages.append({"file": rel, "candidates": url_candidates(rel, clean_urls)})
    return pages


def url_candidates(rel: str, clean_urls: bool) -> List[str]:
    """Map a relative file path to candidate URL paths (percent-encoded)."""
    parts = rel.split("/")
    name = parts[-1]
    stem, _ = os.path.splitext(name)
    prefix = "/" + "/".join(quote(p) for p in parts[:-1])
    prefix = prefix if prefix.endswith("/") else prefix + "/"
    if stem.lower() == "index":
        return [prefix]
    exact = prefix + quote(name)
    return [prefix + quote(stem), exact] if clean_urls else [exact]


def path_key(path: str) -> str:
    """Normalize a URL path so /foo, /foo/, /foo.html and /foo/index.html match."""
    p = unquote(path or "/")
    p = re.sub(r"/index\.html?$", "/", p, flags=re.I)
    p = re.sub(r"\.html?$", "", p, flags=re.I)
    if len(p) > 1:
        p = p.rstrip("/")
    return p.lower() or "/"


def git_info(root: str) -> dict:
    """Return basic git facts for root (or is_repo False)."""
    def run(*args):
        return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True, timeout=60)
    try:
        r = run("rev-parse", "--show-toplevel")
    except (OSError, subprocess.SubprocessError):
        return {"is_repo": False}
    if r.returncode != 0:
        return {"is_repo": False}
    head = run("log", "-1", "--format=%h %cI")
    dirty = run("status", "--porcelain")
    h = head.stdout.split() if head.returncode == 0 else []
    return {"is_repo": True, "head_commit": h[0] if h else None,
            "head_date": h[1] if len(h) > 1 else None,
            "uncommitted_changes": bool(dirty.stdout.strip())}


def git_file_date(root: str, rel: str) -> Optional[str]:
    """Committer date (ISO 8601) of the last commit touching rel."""
    try:
        r = subprocess.run(["git", "-C", root, "log", "-1", "--format=%cI", "--", rel],
                           capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return r.stdout.strip() or None if r.returncode == 0 else None


# --- sitemaps ----------------------------------------------------------------------

def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def parse_sitemap(xml_text: str) -> Tuple[List[dict], List[str]]:
    """Return (url entries with loc/lastmod, child sitemap URLs)."""
    try:
        root = ET.fromstring(xml_text.encode("utf-8") if isinstance(xml_text, str) else xml_text)
    except ET.ParseError:
        return [], []
    urls, children = [], []
    if _local(root.tag) == "sitemapindex":
        for sm in root:
            loc = next((c.text for c in sm if _local(c.tag) == "loc" and c.text), None)
            if loc:
                children.append(loc.strip())
    else:
        for u in root:
            if _local(u.tag) != "url":
                continue
            entry = {"loc": None, "lastmod": None, "alternates": []}
            for c in u:
                t = _local(c.tag)
                if t == "loc" and c.text:
                    entry["loc"] = c.text.strip()
                elif t == "lastmod" and c.text:
                    entry["lastmod"] = c.text.strip()
                elif t == "link" and c.get("hreflang") is not None:
                    entry["alternates"].append({"hreflang": c.get("hreflang", "").strip(),
                                                "href": (c.get("href") or "").strip(),
                                                "rel": c.get("rel")})
            if entry["loc"]:
                urls.append(entry)
    return urls, children


def fetch_sitemaps(fetcher: SafeFetcher, base_url: str, max_sitemaps: int = 10) -> dict:
    """Fetch robots.txt Sitemap: lines and /sitemap.xml (following indexes)."""
    queue, sources, entries, errors = [], [], [], []
    robots = fetcher.get(urljoin(base_url, "/robots.txt"))
    if robots["status"] == 200:
        for line in robots["text"].splitlines():
            if line.lower().startswith("sitemap:"):
                queue.append(line.split(":", 1)[1].strip())
    default = urljoin(base_url, "/sitemap.xml")
    if default not in queue:
        queue.append(default)
    seen = set()
    while queue and len(seen) < max_sitemaps:
        sm = queue.pop(0)
        if sm in seen:
            continue
        seen.add(sm)
        res = fetcher.get(sm)
        if res["status"] != 200:
            errors.append({"url": sm, "status": res["status"], "error": res["error"]})
            continue
        urls, children = parse_sitemap(res["text"])
        sources.append({"url": sm, "urls": len(urls), "child_sitemaps": len(children)})
        entries.extend(urls)
        queue.extend(c for c in children if c not in seen)
    return {"sources": sources, "errors": errors, "entries": entries,
            "robots_status": robots["status"]}


# --- comparison ----------------------------------------------------------------------

def _parse_date(value: Optional[str]) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = parsedate_to_datetime(value)
    except (TypeError, ValueError, IndexError):
        dt = None
    if dt is None:
        try:
            dt = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


COMPARE_FIELDS = ("title", "meta_description", "canonical", "h1", "jsonld_types")


def compare(local: dict, live: dict) -> dict:
    """Field-by-field comparison of two extract() results."""
    out = {f"{f}_equal": local.get(f) == live.get(f) for f in COMPARE_FIELDS}
    out["text_hash_equal"] = local["text_hash"] == live["text_hash"]
    out["text_similarity"] = similarity(local["_text"], live["_text"])
    out["identical"] = all(out[f"{f}_equal"] for f in COMPARE_FIELDS) and out["text_hash_equal"]
    out["differences"] = {f: {"local": local.get(f), "live": live.get(f)}
                          for f in COMPARE_FIELDS if not out[f"{f}_equal"]}
    return out


def run_diff(local_dir: str, base_url: str, fetcher: Optional[SafeFetcher] = None,
             clean_urls: bool = False, exclude: Optional[List[str]] = None,
             max_pages: int = 200, check_sitemap: bool = True, allow_newer: bool = False,
             tolerance_hours: float = 24.0) -> dict:
    """Compare local_dir with base_url and return the JSON-serialisable result."""
    fetcher = fetcher or SafeFetcher()
    root = os.path.abspath(local_dir)
    base = base_url if base_url.endswith("/") else base_url + "/"
    base_host = (urlparse(base).hostname or "").lower()
    git = git_info(root)
    result: dict = {"tool": "repo_live_diff", "local_dir": root, "base_url": base,
                    "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                    "git": git, "pages": [], "warnings": []}

    first = fetcher.get(base)
    if first["blocked"] or first["status"] is None:
        result.update(error=first["error"] or "base URL unreachable", exit_code=2,
                      verdict="error")
        return result
    final_host = (urlparse(first["final_url"]).hostname or base_host).lower()
    sitemap_data = None
    sitemap_lastmod: Dict[str, str] = {}
    if check_sitemap:
        sitemap_data = fetch_sitemaps(fetcher, first["final_url"])
        for e in sitemap_data["entries"]:
            if e.get("lastmod"):
                sitemap_lastmod[path_key(urlparse(e["loc"]).path)] = e["lastmod"]

    pages = local_pages(root, clean_urls, exclude or [])
    if len(pages) > max_pages:
        result["warnings"].append(f"{len(pages)} local HTML files; only the first {max_pages} compared")
        pages = pages[:max_pages]
    tol = timedelta(hours=tolerance_hours)

    for pg in pages:
        with open(os.path.join(root, pg["file"]), "rb") as fh:
            local_html = _decode(fh.read(), "")
        loc = extract(local_html)
        entry: dict = {"file": pg["file"], "tried": [], "state": None}
        live_res = None
        for cand in pg["candidates"]:
            url = urljoin(base, cand.lstrip("/")) if cand != "/" else base
            res = first if url == base else fetcher.get(url)
            entry["tried"].append({"url": url, "status": res["status"],
                                   "final_url": res["final_url"], "error": res["error"]})
            if res["status"] is not None and 200 <= res["status"] < 300:
                live_res = res
                break
            if res["blocked"]:
                result["warnings"].append(f"{url}: {res['error']}")
        local_date = git_file_date(root, pg["file"]) if git["is_repo"] else None
        mtime = datetime.fromtimestamp(os.path.getmtime(os.path.join(root, pg["file"])),
                                       timezone.utc).isoformat(timespec="seconds")
        key = path_key(pg["candidates"][0])
        dates = {"local_git_date": local_date, "local_mtime": mtime,
                 "live_last_modified": None, "live_etag": None,
                 "sitemap_lastmod": sitemap_lastmod.get(key)}
        local_view = {k: v for k, v in loc.items() if k not in ("_text", "hreflang")}
        entry["local"] = local_view
        if live_res is None:
            entry["state"] = "only_local"
            entry["live_status"] = entry["tried"][-1]["status"]
        else:
            live = extract(live_res["text"])
            entry["url"] = live_res["url"]
            entry["final_url"] = live_res["final_url"]
            entry["live_status"] = live_res["status"]
            dates["live_last_modified"] = live_res["headers"].get("last-modified")
            dates["live_etag"] = live_res["headers"].get("etag")
            entry["live"] = {k: v for k, v in live.items() if k not in ("_text", "hreflang")}
            cmp_ = compare(loc, live)
            entry["comparison"] = cmp_
            entry["state"] = "identical" if cmp_["identical"] else "differing"
            # date evidence
            live_dt = _parse_date(dates["live_last_modified"]) or _parse_date(dates["sitemap_lastmod"])
            local_dt = _parse_date(local_date) or _parse_date(mtime)
            if not cmp_["identical"] and live_dt and local_dt:
                if live_dt > local_dt + tol:
                    entry["date_signal"] = "live_newer"
                elif local_dt > live_dt + tol:
                    entry["date_signal"] = "local_newer"
            ly, lv = loc.get("latest_year_in_text"), live.get("latest_year_in_text")
            if not cmp_["identical"] and ly and lv and ly != lv:
                entry["year_signal"] = "live_newer" if lv > ly else "local_newer"
        entry["dates"] = dates
        result["pages"].append(entry)

    # live URLs without local files
    local_keys = {path_key(c) for pg in pages for c in pg["candidates"]}
    only_live, off_host = [], 0
    if sitemap_data:
        seen_keys = set()
        for e in sitemap_data["entries"]:
            u = urlparse(e["loc"])
            host = (u.hostname or "").lower()
            if host.removeprefix("www.") not in {base_host.removeprefix("www."),
                                                 final_host.removeprefix("www.")}:
                off_host += 1
                continue
            k = path_key(u.path)
            if k not in local_keys and k not in seen_keys:
                seen_keys.add(k)
                only_live.append({"url": e["loc"], "lastmod": e.get("lastmod")})
        result["live_sitemap"] = {"sources": sitemap_data["sources"],
                                  "errors": sitemap_data["errors"],
                                  "url_count": len(sitemap_data["entries"]),
                                  "off_host_urls": off_host}
    result["only_live"] = only_live

    states = [p["state"] for p in result["pages"]]
    summary = {"local_html_files": len(pages), "identical": states.count("identical"),
               "differing": states.count("differing"), "only_local": states.count("only_local"),
               "only_live": len(only_live), "requests_made": fetcher.requests_made}
    result["summary"] = summary
    verdict, evidence = decide(result, git)
    result["verdict"] = verdict
    result["evidence"] = evidence
    if verdict == "in sync" or (verdict == "repo appears newer" and allow_newer):
        result["exit_code"] = 0
    else:
        result["exit_code"] = 1
    return result


def decide(result: dict, git: dict) -> Tuple[str, List[str]]:
    """Turn per-page states and date/year signals into a verdict + evidence."""
    s = result["summary"]
    ev: List[str] = []
    result["signals"] = {"live_newer": 0, "local_newer": 0}
    if not (s["differing"] or s["only_local"] or s["only_live"]):
        return "in sync", [f"All {s['identical']} local pages match the live site "
                           "(meta fields and visible-text hash)."]
    older = newer = 0
    for p in result["pages"]:
        if p["state"] == "differing":
            c = p["comparison"]
            ev.append(f"{p['file']}: differs (text similarity {c['text_similarity']:.2f}"
                      + (f"; changed: {', '.join(c['differences'])}" if c["differences"] else "")
                      + ")")
            for sig_key, label in (("date_signal", "dates"), ("year_signal", "latest year in text")):
                sig = p.get(sig_key)
                if sig == "live_newer":
                    older += 1
                    d = p["dates"]
                    detail = (f"live Last-Modified {d['live_last_modified'] or d['sitemap_lastmod']} "
                              f"vs local {d['local_git_date'] or d['local_mtime']}"
                              if sig_key == "date_signal" else
                              f"live mentions {p['live']['latest_year_in_text']}, local "
                              f"{p['local']['latest_year_in_text']}")
                    ev.append(f"  {p['file']}: live is newer by {label} ({detail})")
                elif sig == "local_newer":
                    newer += 1
                    ev.append(f"  {p['file']}: local is newer by {label}")
        elif p["state"] == "only_local":
            newer += 1
            ev.append(f"{p['file']}: not found live (status {p.get('live_status')})")
    if s["only_live"]:
        older += s["only_live"]
        sample = ", ".join(x["url"] for x in result["only_live"][:5])
        ev.append(f"{s['only_live']} live sitemap URL(s) have no local file: {sample}")
    if git.get("is_repo") and git.get("head_date"):
        ev.append(f"Local HEAD {git.get('head_commit')} committed {git['head_date']} "
                  "(commit dates show when files were committed, not when content was written).")
    result["signals"] = {"live_newer": older, "local_newer": newer}
    if older and newer:
        lean = ("mostly older" if older >= 2 * newer else
                "mostly newer" if newer >= 2 * older else "mixed")
        ev.insert(0, f"Signals: {older} say the live site is newer, {newer} say the repo is newer "
                     f"({lean}). Diverged means a blind upload would overwrite live-only changes.")
    if older and not newer:
        return "repo appears older", ev
    if newer and not older:
        return "repo appears newer", ev
    return "diverged", ev


def format_text(res: dict) -> str:
    """Short human-readable report."""
    if res.get("error"):
        return f"ERROR: {res['error']}"
    lines = [f"{res['local_dir']}  vs  {res['base_url']}",
             f"Verdict: {res['verdict'].upper()}  (exit {res['exit_code']})",
             f"Summary: {res['summary']}"]
    for p in res["pages"]:
        sim = p.get("comparison", {}).get("text_similarity")
        lines.append(f"  {p['state']:<10} {p['file']:<30} live={p.get('live_status')} "
                     + (f"sim={sim:.2f}" if sim is not None else ""))
    for u in res.get("only_live", []):
        lines.append(f"  only_live  {u['url']}")
    lines.append("Evidence:")
    lines.extend(f"  - {e}" for e in res["evidence"])
    lines.extend(f"  ! {w}" for w in res.get("warnings", []))
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compare a local static-site folder with the live site before deploying.")
    parser.add_argument("local_dir", help="Local site folder (ideally a git checkout)")
    parser.add_argument("base_url", help="Live site base URL, e.g. https://example.com")
    parser.add_argument("--clean-urls", action="store_true",
                        help="Also try /foo for foo.html (clean form first)")
    parser.add_argument("--exclude", action="append", default=[],
                        help="Glob of local files to skip (repeatable)")
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds between requests (default 1)")
    parser.add_argument("--timeout", type=float, default=20.0, help="Request timeout in seconds")
    parser.add_argument("--max-pages", type=int, default=200, help="Max local HTML files to compare")
    parser.add_argument("--no-sitemap", action="store_true", help="Skip live sitemap comparison")
    parser.add_argument("--allow-newer", action="store_true",
                        help="Exit 0 when the verdict is 'repo appears newer'")
    parser.add_argument("--text", action="store_true", help="Human-readable output instead of JSON")
    args = parser.parse_args(argv)

    if not os.path.isdir(args.local_dir):
        print(json.dumps({"error": f"not a directory: {args.local_dir}"}))
        return 2
    if not validate_url(args.base_url):
        print(json.dumps({"error": f"invalid or blocked URL: {args.base_url}"}))
        return 2
    fetcher = SafeFetcher(delay=args.delay, timeout=args.timeout)
    res = run_diff(args.local_dir, args.base_url, fetcher, clean_urls=args.clean_urls,
                   exclude=args.exclude, max_pages=args.max_pages,
                   check_sitemap=not args.no_sitemap, allow_newer=args.allow_newer)
    print(format_text(res) if args.text else json.dumps(res, indent=2, ensure_ascii=False))
    return res["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
