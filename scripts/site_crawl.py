#!/usr/bin/env python3
"""
Free, self-hosted site crawler for Claude SEO (built-in alternative to the
Firecrawl extension). No API key, no credits: it runs on requests + BeautifulSoup
(and optionally Playwright for JavaScript rendering).

Subcommands:
    map <url>      Discover URLs from robots.txt Sitemap lines, /sitemap.xml,
                   sitemap indexes and .xml.gz files, plus optional link discovery.
    crawl <url>    Polite BFS crawl of one host with per-page SEO records and a
                   site report (broken links, redirect chains/loops, duplicate
                   titles/descriptions, robots-blocked, noindex, orphan candidates,
                   non-canonical sitemap URLs).
    scrape <url>   One page to clean main-content markdown plus its SEO record.

Usage:
    python site_crawl.py map https://example.com --json
    python site_crawl.py map https://example.com --discover-links --max-pages 50
    python site_crawl.py crawl https://example.com --max-pages 100 --max-depth 3 --json
    python site_crawl.py crawl https://example.com --include '/blog/' --jsonl pages.jsonl
    python site_crawl.py scrape https://example.com/pricing --render --json

Safety:
    Every URL (start URL, each redirect hop, each discovered URL, sitemap files,
    external HEAD checks, and every request made by the Playwright renderer) is
    checked with safe_fetch.validate_public_url(): validate_url() from
    google_auth.py plus a DNS check that rejects hosts resolving to private,
    loopback, link-local or reserved addresses (incl. IPv4-mapped IPv6), and
    direct connections are pinned to the validated IP (DNS rebinding).
    Redirects are followed manually so each hop is validated. Responses are
    capped (--max-bytes). Only http/https. Crawling never leaves the start host
    (after the start URL's own redirects); external links are only counted, or
    HEAD-checked with --check-external under a separate budget.

    The validator is dependency-injected (see crawl_site(validator=...)); tests
    pass a validator that allows exactly one local fixture origin. There is no
    environment-variable escape hatch.

Politeness defaults:
    User-Agent "claude-seo-crawler/<plugin version>", robots.txt honored for that
    token (RFC 9309: 4xx robots.txt = allow all, 5xx/unreachable = disallow all),
    delay 1.0 s between requests (or Crawl-delay if larger), concurrency 1,
    max 100 pages.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import threading
import time
import zlib
from collections import defaultdict, deque
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, Iterable, Optional
from urllib import robotparser
from urllib.parse import parse_qsl, urlencode, urljoin, urlparse, urlunparse
from xml.etree import ElementTree

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ROOT = os.path.dirname(SCRIPT_DIR)
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import safe_fetch  # noqa: E402  (shared SSRF-safe validation + pinned sessions)

try:
    import requests
except ImportError:  # pragma: no cover - reported at runtime
    requests = None

DEFAULT_MAX_BYTES = 5 * 1024 * 1024
SITEMAP_MAX_BYTES = 50 * 1024 * 1024  # sitemaps.org limit (uncompressed)
MAX_SITEMAP_FILES = 50
MAX_REDIRECTS = 10
REDIRECT_CODES = {301, 302, 303, 307, 308}
HTML_TYPES = ("text/html", "application/xhtml+xml")

Validator = Callable[[str], bool]


# --------------------------------------------------------------------------
# Identity
# --------------------------------------------------------------------------

def plugin_version() -> str:
    """Read the plugin version from .claude-plugin/plugin.json at runtime."""
    path = os.path.join(PLUGIN_ROOT, ".claude-plugin", "plugin.json")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return str(json.load(fh).get("version") or "0")
    except (OSError, ValueError):
        return "0"


ROBOTS_TOKEN = "claude-seo-crawler"


def default_user_agent() -> str:
    """Named crawler UA: claude-seo-crawler/<version> (+repo URL)."""
    return f"{ROBOTS_TOKEN}/{plugin_version()} (+https://github.com/AgriciDaniel/claude-seo)"


# --------------------------------------------------------------------------
# URL safety and normalization
# --------------------------------------------------------------------------

_ip_is_public = safe_fetch.is_public_ip
# validate_url() plus DNS resolution: every resolved address must be public.
default_validator = safe_fetch.validate_public_url


def ensure_scheme(url: str) -> str:
    """Add https:// when the user typed a bare host."""
    url = url.strip()
    if "://" not in url:
        url = "https://" + url
    return url


def normalize_url(url: str, sort_query: bool = False,
                  trailing_slash: str = "keep") -> Optional[str]:
    """Canonical form for de-duplication; None for non-http(s) URLs.

    Lower-cases scheme and host, drops default ports and the fragment, uses "/"
    for an empty path, optionally sorts query parameters, and applies the
    trailing-slash policy ("keep", "strip" or "add"; the root path is untouched).
    """
    try:
        p = urlparse(url.strip())
    except ValueError:
        return None
    scheme = p.scheme.lower()
    if scheme not in ("http", "https") or not p.hostname:
        return None
    host = p.hostname.lower()
    if ":" in host:
        host = f"[{host}]"
    try:
        port = p.port
    except ValueError:
        return None
    if port and not ((scheme == "http" and port == 80) or (scheme == "https" and port == 443)):
        host = f"{host}:{port}"
    path = p.path or "/"
    if trailing_slash == "strip" and path != "/" and path.endswith("/"):
        path = path.rstrip("/") or "/"
    elif trailing_slash == "add" and not path.endswith("/"):
        last = path.rsplit("/", 1)[-1]
        if "." not in last:
            path += "/"
    query = p.query
    if sort_query and query:
        query = urlencode(sorted(parse_qsl(query, keep_blank_values=True)))
    return urlunparse((scheme, host, path, "", query, ""))


def host_of(url: str) -> str:
    """Host plus non-default port, lower-cased (the crawl scope key)."""
    n = normalize_url(url)
    return urlparse(n).netloc if n else ""


# --------------------------------------------------------------------------
# Fetching (manual redirects, per-hop validation, size cap)
# --------------------------------------------------------------------------

class Fetcher:
    """HTTP client that validates every hop and caps response size."""

    def __init__(self, validator: Validator = default_validator,
                 user_agent: Optional[str] = None, timeout: float = 20.0,
                 max_bytes: int = DEFAULT_MAX_BYTES,
                 max_redirects: int = MAX_REDIRECTS):
        if requests is None:
            raise RuntimeError("requests library required: pip install requests")
        self.validator = validator
        self.user_agent = user_agent or default_user_agent()
        self.timeout = timeout
        self.max_bytes = max_bytes
        self.max_redirects = max_redirects
        self._local = threading.local()

    def _session(self):
        s = getattr(self._local, "session", None)
        if s is None:
            # Connections are pinned to an address that passed the same check.
            s = safe_fetch.make_session(safe_fetch.address_check_for(self.validator))
            s.trust_env = True
            s.headers.update({
                "User-Agent": self.user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
            })
            self._local.session = s
        return s

    def fetch(self, url: str, method: str = "GET", allowed_host: Optional[str] = None,
              max_bytes: Optional[int] = None) -> dict:
        """Fetch url, following redirects manually.

        allowed_host: when set, a redirect to another host is recorded but not
        followed (error "offsite_redirect").
        """
        cap = max_bytes or self.max_bytes
        out = {
            "requested_url": url, "final_url": url, "status": None,
            "redirect_chain": [], "redirect_loop": False, "content_type": None,
            "x_robots_tag": None, "headers": {}, "response_time_ms": None,
            "bytes": 0, "truncated": False, "body": b"", "error": None,
        }
        current = url
        seen = {normalize_url(url) or url}
        started = time.monotonic()
        for _ in range(self.max_redirects + 1):
            if not self.validator(current):
                out["error"] = "blocked_by_validator"
                out["final_url"] = current
                break
            try:
                resp = self._session().request(
                    method, current, allow_redirects=False, stream=True,
                    timeout=self.timeout)
            except requests.exceptions.RequestException as exc:
                out["error"] = f"{type(exc).__name__}: {exc}"[:300]
                out["final_url"] = current
                break
            try:
                status = resp.status_code
                location = resp.headers.get("Location")
                if status in REDIRECT_CODES and location:
                    nxt = urljoin(current, location)
                    out["redirect_chain"].append(
                        {"url": current, "status": status, "location": nxt})
                    key = normalize_url(nxt)
                    if key is None:
                        out.update(status=status, final_url=current,
                                   error="redirect_to_unsupported_scheme")
                        break
                    if key in seen:
                        out.update(status=status, final_url=nxt, redirect_loop=True,
                                   error="redirect_loop")
                        break
                    seen.add(key)
                    if not self.validator(nxt):
                        out.update(status=status, final_url=nxt, error="blocked_by_validator")
                        break
                    if allowed_host and host_of(nxt) != allowed_host:
                        out.update(status=status, final_url=nxt, error="offsite_redirect")
                        break
                    current = nxt
                    continue
                out["status"] = status
                out["final_url"] = current
                out["content_type"] = resp.headers.get("Content-Type")
                out["x_robots_tag"] = resp.headers.get("X-Robots-Tag")
                out["headers"] = {k: v for k, v in resp.headers.items()
                                  if k.lower() in ("content-type", "x-robots-tag",
                                                   "content-length", "last-modified")}
                if method != "HEAD":
                    body = bytearray()
                    for chunk in resp.iter_content(chunk_size=65536):
                        body.extend(chunk)
                        if len(body) > cap:
                            out["truncated"] = True
                            del body[cap:]
                            break
                    out["body"] = bytes(body)
                    out["bytes"] = len(body)
                break
            finally:
                resp.close()
        else:
            out["error"] = f"too_many_redirects (>{self.max_redirects})"
        out["response_time_ms"] = int((time.monotonic() - started) * 1000)
        return out


def decode_body(body: bytes, content_type: Optional[str]) -> str:
    """Decode with the declared charset, else a <meta charset>, else UTF-8."""
    charset = None
    m = re.search(r"charset=([\w-]+)", content_type or "", re.I)
    if m:
        charset = m.group(1)
    else:
        m = re.search(rb"<meta[^>]+charset=[\"']?([\w-]+)", body[:4096], re.I)
        if m:
            charset = m.group(1).decode("ascii", "ignore")
    try:
        return body.decode(charset or "utf-8", errors="replace")
    except LookupError:
        return body.decode("utf-8", errors="replace")


def is_html(content_type: Optional[str]) -> bool:
    return bool(content_type) and content_type.split(";")[0].strip().lower() in HTML_TYPES


# --------------------------------------------------------------------------
# Rendering (optional Playwright)
# --------------------------------------------------------------------------

class Renderer:
    """Headless Chromium renderer; every browser request is validated.

    Honors PLAYWRIGHT_BROWSERS_PATH (Playwright reads it itself). If Playwright
    or the browser is missing, .error is set and render() returns None.
    """

    def __init__(self, validator: Validator = default_validator,
                 user_agent: Optional[str] = None, timeout: float = 30.0):
        self.validator = validator
        self.user_agent = user_agent or default_user_agent()
        self.timeout_ms = int(timeout * 1000)
        self.error: Optional[str] = None
        self.blocked_requests: list = []
        self._pw = self._browser = None

    def __enter__(self):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            self.error = ("playwright not installed: pip install playwright && "
                          "playwright install chromium (browsers path: "
                          f"{os.environ.get('PLAYWRIGHT_BROWSERS_PATH') or 'default'})")
            return self
        try:
            self._pw = sync_playwright().start()
            self._browser = self._pw.chromium.launch(headless=True)
        except Exception as exc:  # browser binary missing etc.
            self.error = f"playwright launch failed: {exc}"[:400]
            self._close()
        return self

    def _close(self):
        try:
            if self._browser:
                self._browser.close()
        finally:
            if self._pw:
                self._pw.stop()
            self._browser = self._pw = None

    def __exit__(self, *exc):
        self._close()
        return False

    def render(self, url: str) -> Optional[str]:
        if self._browser is None:
            return None
        context = self._browser.new_context(user_agent=self.user_agent)
        try:
            page = context.new_page()

            def guard(route):
                if self.validator(route.request.url) or route.request.url.startswith(("data:", "blob:")):
                    route.continue_()
                else:
                    self.blocked_requests.append(route.request.url[:200])
                    route.abort()

            page.route("**/*", guard)
            page.goto(url, wait_until="networkidle", timeout=self.timeout_ms)
            return page.content()
        except Exception as exc:
            self.error = f"render failed: {exc}"[:400]
            return None
        finally:
            context.close()


# --------------------------------------------------------------------------
# robots.txt
# --------------------------------------------------------------------------

class Robots:
    """robots.txt for one origin, evaluated for the claude-seo-crawler token."""

    def __init__(self, text: Optional[str], status: Optional[int], url: str):
        self.url = url
        self.status = status
        self.parser = robotparser.RobotFileParser()
        self.parser.set_url(url)
        if status is not None and 200 <= status < 300 and text is not None:
            self.parser.parse(text.splitlines())
            self.mode = "parsed"
        elif status is not None and 400 <= status < 500:
            self.parser.allow_all = True
            self.mode = "allow_all (robots.txt 4xx)"
        else:
            self.parser.disallow_all = True
            self.mode = "disallow_all (robots.txt 5xx/unreachable)"

    def allowed(self, url: str) -> bool:
        return self.parser.can_fetch(ROBOTS_TOKEN, url)

    def crawl_delay(self) -> Optional[float]:
        d = self.parser.crawl_delay(ROBOTS_TOKEN)
        return float(d) if d is not None else None

    def sitemaps(self) -> list:
        return list(self.parser.site_maps() or [])


def load_robots(fetcher: Fetcher, origin_url: str) -> Robots:
    p = urlparse(origin_url)
    url = f"{p.scheme}://{p.netloc}/robots.txt"
    res = fetcher.fetch(url, max_bytes=512 * 1024)
    text = decode_body(res["body"], res["content_type"]) if res["body"] else ""
    return Robots(text, res["status"], url)


# --------------------------------------------------------------------------
# Sitemaps
# --------------------------------------------------------------------------

def _gunzip_capped(data: bytes, cap: int) -> bytes:
    d = zlib.decompressobj(16 + zlib.MAX_WBITS)
    out = d.decompress(data, cap + 1)
    if len(out) > cap:
        raise ValueError("decompressed sitemap exceeds size cap")
    return out


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def parse_sitemap_xml(data: bytes) -> tuple:
    """Return (kind, locs) where kind is 'index', 'urlset' or 'unknown'."""
    if data[:2] == b"\x1f\x8b":
        data = _gunzip_capped(data, SITEMAP_MAX_BYTES)
    if b"<!ENTITY" in data[:4096].upper():
        raise ValueError("sitemap declares XML entities; refused")
    root = ElementTree.fromstring(data)
    kind = {"sitemapindex": "index", "urlset": "urlset"}.get(_local(root.tag), "unknown")
    locs = []
    for el in root.iter():
        if _local(el.tag) == "loc" and el.text and el.text.strip():
            locs.append(el.text.strip())
    return kind, locs


def discover_sitemaps(fetcher: Fetcher, start_url: str, robots: Optional[Robots] = None,
                      extra: Iterable[str] = (),
                      pause: Callable[[], None] = lambda: None) -> dict:
    """Walk robots.txt Sitemap lines, /sitemap.xml and nested indexes.

    Only sitemap files and page URLs on the start host are used.
    """
    host = host_of(start_url)
    p = urlparse(normalize_url(start_url))
    origin = f"{p.scheme}://{p.netloc}"
    queue = deque()
    for sm in (robots.sitemaps() if robots else []):
        queue.append((sm, "robots.txt"))
    queue.append((origin + "/sitemap.xml", "sitemap.xml"))
    for sm in extra:
        queue.append((sm, "user"))
    visited, files, urls, errors, skipped = set(), [], {}, [], []
    while queue and len(visited) < MAX_SITEMAP_FILES:
        sm_url, source = queue.popleft()
        key = normalize_url(sm_url)
        if not key or key in visited:
            continue
        visited.add(key)
        if host_of(key) != host:
            skipped.append({"url": sm_url, "reason": "offhost_sitemap"})
            continue
        pause()
        res = fetcher.fetch(key, max_bytes=SITEMAP_MAX_BYTES)
        entry = {"url": key, "source": source, "status": res["status"], "kind": None,
                 "count": 0}
        if res["error"] or res["status"] != 200:
            entry["error"] = res["error"] or f"HTTP {res['status']}"
            if source != "sitemap.xml" or res["status"] not in (404, 410):
                errors.append(entry)
            files.append(entry)
            continue
        try:
            kind, locs = parse_sitemap_xml(res["body"])
        except (ElementTree.ParseError, ValueError, zlib.error, EOFError) as exc:
            entry["error"] = f"parse_error: {exc}"[:200]
            errors.append(entry)
            files.append(entry)
            continue
        entry["kind"], entry["count"] = kind, len(locs)
        files.append(entry)
        for loc in locs:
            if kind == "index":
                queue.append((loc, "sitemap-index"))
            else:
                n = normalize_url(loc)
                if n and host_of(n) == host:
                    urls.setdefault(n, {"url": n, "sources": set()})["sources"].add(
                        "sitemap:" + key)
                elif n:
                    skipped.append({"url": loc, "reason": "offhost_url"})
    return {"files": files, "urls": urls, "errors": errors, "skipped": skipped[:50]}


# --------------------------------------------------------------------------
# Page records
# --------------------------------------------------------------------------

def _robots_tokens(value: Optional[str]) -> set:
    tokens = set()
    for part in re.split(r"[,\s]+", (value or "").lower()):
        part = part.split(":")[-1].strip()
        if part:
            tokens.add(part)
    return tokens


def _jsonld_types(schema: list) -> list:
    types = []
    for item in schema:
        if not isinstance(item, dict):
            continue
        t = item.get("@type")
        for v in (t if isinstance(t, list) else [t]):
            if isinstance(v, str) and v not in types:
                types.append(v)
    return types


def page_record(fetch: dict, html: Optional[str], parsed: Optional[dict],
                depth: Optional[int] = None) -> dict:
    """Flatten a fetch result and parse_html() output into one SEO record."""
    final = fetch["final_url"]
    rec = {
        "url": fetch["requested_url"],
        "final_url": final,
        "status": fetch["status"],
        "redirect_chain": fetch["redirect_chain"],
        "redirect_hops": len(fetch["redirect_chain"]),
        "redirect_loop": fetch["redirect_loop"],
        "content_type": fetch["content_type"],
        "response_time_ms": fetch["response_time_ms"],
        "bytes": fetch["bytes"],
        "truncated": fetch["truncated"],
        "depth": depth,
        "error": fetch["error"],
        "x_robots_tag": fetch["x_robots_tag"],
        "title": None, "meta_description": None, "meta_robots": None,
        "canonical": None, "canonical_is_self": None, "hreflang": [],
        "h1_count": 0, "word_count": 0, "internal_links": 0, "external_links": 0,
        "images_missing_alt": 0, "jsonld_types": [], "noindex": False,
    }
    if parsed:
        canonical = parsed.get("canonical")
        canonical_abs = urljoin(final, canonical) if canonical else None
        rec.update({
            "title": parsed.get("title"),
            "meta_description": parsed.get("meta_description"),
            "meta_robots": parsed.get("meta_robots"),
            "canonical": canonical_abs,
            "canonical_is_self": (None if not canonical_abs else
                                  normalize_url(canonical_abs) == normalize_url(final)),
            "hreflang": [{"lang": h.get("lang"),
                          "href": urljoin(final, h.get("href") or "")}
                         for h in parsed.get("hreflang", [])],
            "h1_count": len(parsed.get("h1", [])),
            "word_count": parsed.get("word_count", 0),
            "internal_links": len(parsed["links"]["internal"]),
            "external_links": len(parsed["links"]["external"]),
            "images_missing_alt": sum(1 for i in parsed.get("images", [])
                                      if i.get("alt") is None),
            "jsonld_types": _jsonld_types(parsed.get("schema", [])),
        })
    tokens = _robots_tokens(rec["meta_robots"]) | _robots_tokens(rec["x_robots_tag"])
    rec["noindex"] = bool(tokens & {"noindex", "none"})
    return rec


def _parse(html: str, base_url: str) -> dict:
    from parse_html import parse_html  # lazy: bs4 needed only when parsing
    return parse_html(html, base_url)


# --------------------------------------------------------------------------
# Crawl
# --------------------------------------------------------------------------

def _compile(patterns: Optional[Iterable[str]]) -> list:
    return [re.compile(p) for p in (patterns or [])]


def crawl_site(start_url: str, *, max_pages: int = 100, max_depth: int = 3,
               delay: float = 1.0, concurrency: int = 1,
               include: Optional[Iterable[str]] = None,
               exclude: Optional[Iterable[str]] = None,
               sort_query: bool = False, trailing_slash: str = "keep",
               use_sitemaps: bool = True, render: bool = False,
               check_external: bool = False, external_budget: int = 20,
               timeout: float = 20.0, user_agent: Optional[str] = None,
               max_bytes: int = DEFAULT_MAX_BYTES,
               validator: Validator = default_validator,
               jsonl_path: Optional[str] = None,
               sleep: Callable[[float], None] = time.sleep) -> dict:
    """Crawl one host breadth-first and return {"summary", "report", "pages"}."""
    start_url = ensure_scheme(start_url)
    norm = lambda u: normalize_url(u, sort_query, trailing_slash)  # noqa: E731
    start = norm(start_url)
    if not start or not validator(start):
        return {"error": f"URL rejected by validator (private/loopback/non-http): {start_url}"}
    fetcher = Fetcher(validator, user_agent, timeout, max_bytes)
    inc, exc = _compile(include), _compile(exclude)

    # Resolve the start URL's own redirects (e.g. apex -> www) to fix the scope.
    probe = fetcher.fetch(start)
    if probe["error"] and probe["status"] is None:
        return {"error": f"start URL failed: {probe['error']}", "start_url": start}
    scope_url = norm(probe["final_url"]) or start
    host = host_of(scope_url)
    robots = load_robots(fetcher, scope_url)
    crawl_delay = robots.crawl_delay()
    effective_delay = max(delay, crawl_delay or 0.0)
    concurrency = max(1, min(int(concurrency), 5))

    sitemap = (discover_sitemaps(fetcher, scope_url, robots,
                                 pause=lambda: sleep(effective_delay)) if use_sitemaps
               else {"files": [], "urls": {}, "errors": [], "skipped": []})
    sitemap_urls = set(sitemap["urls"])

    def in_scope(u: str) -> bool:
        if host_of(u) != host:
            return False
        if inc and not any(r.search(u) for r in inc):
            return False
        return not any(r.search(u) for r in exc)

    main_q = deque([(scope_url, 0)])
    if start != scope_url:
        main_q.appendleft((start, 0))
    side_q = deque((u, 0) for u in sorted(sitemap_urls) if u not in (start, scope_url))
    queued = {start, scope_url} | set(u for u, _ in side_q)
    pages: dict = {}
    inlinks = defaultdict(set)
    external = defaultdict(set)
    robots_blocked = {}
    filtered = 0
    fetched = 0
    renderer = Renderer(validator, user_agent, timeout) if render else None
    render_error = None
    jsonl = open(jsonl_path, "w", encoding="utf-8") if jsonl_path else None

    prefetched = {start: probe}

    def work(item):
        url, depth = item
        res = prefetched.pop(url, None) or fetcher.fetch(url, allowed_host=host)
        return url, depth, res

    try:
        if renderer:
            renderer.__enter__()
            render_error = renderer.error
        first = True
        while (main_q or side_q) and fetched < max_pages:
            batch = []
            while (main_q or side_q) and len(batch) < min(concurrency, max_pages - fetched):
                url, depth = (main_q or side_q).popleft()
                if not validator(url):
                    pages[url] = {"url": url, "error": "blocked_by_validator", "status": None,
                                  "depth": depth}
                    continue
                if not robots.allowed(url):
                    robots_blocked[url] = depth
                    continue
                batch.append((url, depth))
            if not batch:
                continue
            if not first and effective_delay > 0 and not (
                    len(batch) == 1 and batch[0][0] in prefetched):
                sleep(effective_delay)
            first = False
            if len(batch) == 1:
                results = [work(batch[0])]
            else:
                with ThreadPoolExecutor(max_workers=len(batch)) as pool:
                    results = list(pool.map(work, batch))
            for url, depth, res in results:
                fetched += 1
                html = parsed = None
                final = norm(res["final_url"]) or res["final_url"]
                if res["status"] == 200 and is_html(res["content_type"]) and res["body"]:
                    html = decode_body(res["body"], res["content_type"])
                    if renderer and renderer._browser is not None:
                        rendered = renderer.render(final)
                        if rendered:
                            html = rendered
                        else:
                            render_error = renderer.error
                    parsed = _parse(html, final)
                rec = page_record(res, html, parsed, depth)
                rec["in_sitemap"] = url in sitemap_urls
                pages[url] = rec
                if final != url and final not in pages and host_of(final) == host:
                    queued.add(final)
                if jsonl:
                    jsonl.write(json.dumps(rec, ensure_ascii=False) + "\n")
                if not parsed:
                    continue
                for link in parsed["links"]["internal"]:
                    target = norm(link["href"])
                    if not target:
                        continue
                    if host_of(target) != host:
                        external[target].add(final)
                        continue
                    if target != final:
                        inlinks[target].add(final)
                    if target in queued:
                        continue
                    if not in_scope(target):
                        filtered += 1
                        queued.add(target)
                        continue
                    if depth + 1 <= max_depth:
                        queued.add(target)
                        main_q.append((target, depth + 1))
                for link in parsed["links"]["external"]:
                    target = norm(link["href"])
                    if target and host_of(target) == host:  # e.g. http vs https
                        inlinks[target].add(final)
                    elif target:
                        external[target].add(final)
    finally:
        if renderer:
            renderer.__exit__(None, None, None)
        if jsonl:
            jsonl.close()

    external_checks = []
    if check_external:
        for target in sorted(external)[:max(0, external_budget)]:
            if effective_delay > 0:
                sleep(min(effective_delay, 1.0))
            res = fetcher.fetch(target, method="HEAD")
            if res["status"] in (405, 501):
                res = fetcher.fetch(target, max_bytes=16 * 1024)
            external_checks.append({"url": target, "status": res["status"],
                                    "error": res["error"],
                                    "linked_from": sorted(external[target])[:20]})

    report = build_report(pages, inlinks, robots_blocked, sitemap_urls, external_checks,
                          entry_urls={start, scope_url})
    crawl_complete = not main_q and not side_q
    summary = {
        "start_url": start, "scope_host": host, "user_agent": fetcher.user_agent,
        "robots_txt": {"url": robots.url, "status": robots.status, "mode": robots.mode,
                       "crawl_delay": crawl_delay},
        "effective_delay_s": effective_delay, "concurrency": concurrency,
        "pages_fetched": fetched, "max_pages": max_pages, "max_depth": max_depth,
        "crawl_complete": crawl_complete,
        "urls_remaining_in_queue": len(main_q) + len(side_q),
        "urls_filtered_by_include_exclude": filtered,
        "external_links_unique": len(external),
        "sitemap_files": sitemap["files"], "sitemap_urls": len(sitemap_urls),
        "sitemap_errors": sitemap["errors"],
        "render": bool(render), "render_error": render_error,
        "counts": {k: len(v) for k, v in report.items() if isinstance(v, (list, dict))},
    }
    if not crawl_complete:
        summary["note"] = ("Crawl stopped at the page budget; broken-link and orphan "
                           "findings cover only fetched pages.")
    return {"summary": summary, "report": report,
            "pages": [pages[k] for k in pages]}


def build_report(pages: dict, inlinks: dict, robots_blocked: dict, sitemap_urls: set,
                 external_checks: list, entry_urls: Iterable[str] = ()) -> dict:
    """Derive the site-level findings from per-page records."""
    def linked_from(u):
        return sorted(inlinks.get(u, ()))[:50]

    ok_html = [p for p in pages.values()
               if p.get("status") == 200 and p.get("content_type") and is_html(p["content_type"])]
    broken, chains, loops, noindex, blocked_ssrf, offsite = [], [], [], [], [], []
    for url, p in pages.items():
        status = p.get("status")
        if p.get("error") == "blocked_by_validator":
            blocked_ssrf.append({"url": url, "final_url": p.get("final_url"),
                                 "redirect_chain": p.get("redirect_chain", []),
                                 "linked_from": linked_from(url)})
            continue
        if p.get("error") == "offsite_redirect":
            offsite.append({"url": url, "target": p.get("final_url"),
                            "linked_from": linked_from(url)})
        if (status and status >= 400) or (status is None and p.get("error")):
            broken.append({"url": url, "status": status, "error": p.get("error"),
                           "linked_from": linked_from(url)})
        if p.get("redirect_loop"):
            loops.append({"url": url, "chain": p["redirect_chain"],
                          "linked_from": linked_from(url)})
        elif p.get("redirect_hops", 0) > 1:
            chains.append({"url": url, "hops": p["redirect_hops"],
                           "chain": p["redirect_chain"], "final_url": p["final_url"],
                           "final_status": status, "linked_from": linked_from(url)})
        if p.get("noindex"):
            noindex.append({"url": p.get("final_url") or url,
                            "meta_robots": p.get("meta_robots"),
                            "x_robots_tag": p.get("x_robots_tag")})

    def dupes(field):
        groups = defaultdict(set)
        for p in ok_html:
            v = (p.get(field) or "").strip()
            if v:
                groups[v].add(p["final_url"])
        return [{"value": v, "urls": sorted(us)} for v, us in sorted(groups.items())
                if len(us) > 1]

    linked = set(inlinks)
    entry = set(entry_urls)
    orphans = sorted(u for u in sitemap_urls if u not in linked and u not in entry)
    sitemap_issues = []
    for u in sorted(sitemap_urls):
        p = pages.get(u)
        if not p:
            continue
        issues = []
        if p.get("redirect_hops"):
            issues.append("redirects")
        if p.get("status") and p["status"] != 200:
            issues.append(f"status_{p['status']}")
        if p.get("canonical_is_self") is False:
            issues.append("canonical_points_elsewhere")
        if p.get("noindex"):
            issues.append("noindex")
        if issues:
            sitemap_issues.append({"url": u, "issues": issues,
                                   "canonical": p.get("canonical"),
                                   "final_url": p.get("final_url")})
    return {
        "broken_internal_links": broken,
        "redirect_chains": chains,
        "redirect_loops": loops,
        "duplicate_titles": dupes("title"),
        "duplicate_descriptions": dupes("meta_description"),
        "blocked_by_robots": [{"url": u, "linked_from": linked_from(u)}
                              for u in sorted(robots_blocked)],
        "noindex_pages": noindex,
        "orphan_candidates": orphans,
        "non_canonical_in_sitemap": [s for s in sitemap_issues
                                     if "canonical_points_elsewhere" in s["issues"]],
        "sitemap_url_issues": sitemap_issues,
        "blocked_unsafe_urls": blocked_ssrf,
        "offsite_redirects": offsite,
        "external_link_checks": external_checks,
        "pages_missing_title": sorted(p["final_url"] for p in ok_html if not p.get("title")),
        "pages_multiple_or_no_h1": sorted(p["final_url"] for p in ok_html
                                          if p.get("h1_count") != 1),
    }


# --------------------------------------------------------------------------
# Map
# --------------------------------------------------------------------------

def map_site(start_url: str, *, discover_links: bool = False, max_pages: int = 50,
             max_depth: int = 2, delay: float = 1.0, limit: int = 5000,
             search: Optional[str] = None, timeout: float = 20.0,
             user_agent: Optional[str] = None, validator: Validator = default_validator,
             sleep: Callable[[float], None] = time.sleep) -> dict:
    """Discover same-host URLs from sitemaps (and optionally links)."""
    start_url = ensure_scheme(start_url)
    start = normalize_url(start_url)
    if not start or not validator(start):
        return {"error": f"URL rejected by validator (private/loopback/non-http): {start_url}"}
    fetcher = Fetcher(validator, user_agent, timeout)
    robots = load_robots(fetcher, start)
    sm_delay = max(delay, robots.crawl_delay() or 0.0)
    sm = discover_sitemaps(fetcher, start, robots, pause=lambda: sleep(sm_delay))
    urls = {u: {"url": u, "sources": set(e["sources"])} for u, e in sm["urls"].items()}
    crawl_summary = None
    if discover_links:
        res = crawl_site(start, max_pages=max_pages, max_depth=max_depth, delay=delay,
                         use_sitemaps=False, timeout=timeout, user_agent=user_agent,
                         validator=validator, sleep=sleep)
        if "error" not in res:
            crawl_summary = {k: res["summary"][k] for k in
                             ("pages_fetched", "crawl_complete", "robots_txt")}
            for p in res["pages"]:
                for key in (p.get("url"), normalize_url(p.get("final_url") or "")):
                    if key and host_of(key) == host_of(start) and p.get("status"):
                        urls.setdefault(key, {"url": key, "sources": set()})["sources"].add("links")
            for b in res["report"]["blocked_by_robots"]:
                urls.setdefault(b["url"], {"url": b["url"], "sources": set()})["sources"].add(
                    "links (robots-blocked, not fetched)")
    rows = sorted(urls.values(), key=lambda r: r["url"])
    if search:
        rows = [r for r in rows if search.lower() in r["url"].lower()]
    total = len(rows)
    rows = rows[:limit]
    patterns = defaultdict(int)
    for r in rows:
        segs = [x for x in urlparse(r["url"]).path.split("/") if x]
        patterns[f"/{segs[0]}/*" if len(segs) > 1 else "/ (root pages)"] += 1
    return {
        "start_url": start, "user_agent": fetcher.user_agent,
        "robots_txt": {"url": robots.url, "status": robots.status, "mode": robots.mode,
                       "sitemaps": robots.sitemaps(), "crawl_delay": robots.crawl_delay()},
        "sitemap_files": sm["files"], "sitemap_errors": sm["errors"],
        "skipped": sm["skipped"], "link_discovery": crawl_summary,
        "total_urls": total, "returned": len(rows), "truncated": total > len(rows),
        "patterns": dict(sorted(patterns.items(), key=lambda kv: -kv[1])),
        "urls": [{"url": r["url"], "sources": sorted(r["sources"])} for r in rows],
    }


# --------------------------------------------------------------------------
# Scrape (markdown)
# --------------------------------------------------------------------------

STRIP_TAGS = ("script", "style", "noscript", "nav", "footer", "header", "aside",
              "form", "svg", "iframe", "template", "button")


def html_to_markdown(html: str, base_url: str) -> str:
    """Main-content markdown: prefer <main>/<article>/[role=main], strip chrome."""
    from bs4 import BeautifulSoup, NavigableString, Tag  # lazy import
    try:
        import lxml  # noqa: F401
        parser = "lxml"
    except ImportError:
        parser = "html.parser"
    soup = BeautifulSoup(html, parser)
    root = (soup.find("main") or soup.find(attrs={"role": "main"})
            or soup.find("article") or soup.body or soup)
    for tag in root.find_all(STRIP_TAGS):
        tag.decompose()
    for tag in root.find_all(attrs={"aria-hidden": "true"}):
        tag.decompose()

    def inline(node) -> str:
        if isinstance(node, NavigableString):
            return re.sub(r"\s+", " ", str(node))
        if not isinstance(node, Tag):
            return ""
        name = node.name
        inner = "".join(inline(c) for c in node.children)
        if name == "a" and node.get("href"):
            href = urljoin(base_url, node["href"])
            text = inner.strip()
            return f"[{text}]({href})" if text else ""
        if name == "img":
            return f"![{node.get('alt') or ''}]({urljoin(base_url, node.get('src') or '')})"
        if name in ("strong", "b"):
            return f"**{inner.strip()}**" if inner.strip() else ""
        if name in ("em", "i"):
            return f"*{inner.strip()}*" if inner.strip() else ""
        if name == "code":
            return f"`{inner.strip()}`"
        if name == "br":
            return "\n"
        return inner

    blocks: list = []

    def render_list(lst, depth) -> list:
        items = []
        for i, li in enumerate(lst.find_all("li", recursive=False), 1):
            marker = f"{i}." if lst.name == "ol" else "-"
            text = "".join(inline(c) for c in li.children
                           if not (isinstance(c, Tag) and c.name in ("ul", "ol"))).strip()
            items.append("  " * depth + f"{marker} {text}")
            for sub_list in li.find_all(["ul", "ol"], recursive=False):
                items.extend(render_list(sub_list, depth + 1))
        return items

    def block(node, list_depth=0):
        for child in node.children:
            if isinstance(child, NavigableString):
                text = re.sub(r"\s+", " ", str(child)).strip()
                if text:
                    blocks.append(text)
                continue
            if not isinstance(child, Tag):
                continue
            name = child.name
            if re.fullmatch(r"h[1-6]", name):
                text = inline(child).strip()
                if text:
                    blocks.append("#" * int(name[1]) + " " + text)
            elif name == "p":
                text = inline(child).strip()
                if text:
                    blocks.append(text)
            elif name in ("ul", "ol"):
                items = render_list(child, list_depth)
                if items:
                    blocks.append("\n".join(items))
            elif name == "pre":
                blocks.append("```\n" + child.get_text().rstrip("\n") + "\n```")
            elif name == "blockquote":
                text = inline(child).strip()
                if text:
                    blocks.append("\n".join("> " + ln for ln in text.splitlines()))
            elif name == "table":
                rows = []
                for tr in child.find_all("tr"):
                    cells = [inline(td).strip().replace("|", "\\|")
                             for td in tr.find_all(["th", "td"])]
                    if cells:
                        rows.append("| " + " | ".join(cells) + " |")
                if rows:
                    width = rows[0].count(" | ") + 1
                    rows.insert(1, "| " + " | ".join(["---"] * width) + " |")
                    blocks.append("\n".join(rows))
            elif name == "img":
                blocks.append(inline(child))
            elif name == "hr":
                blocks.append("---")
            elif name in ("a", "strong", "b", "em", "i", "span", "code", "small", "label"):
                text = inline(child).strip()
                if text:
                    blocks.append(text)
            else:
                block(child, list_depth)

    block(root)
    md = "\n\n".join(b for b in blocks if b.strip())
    return re.sub(r"\n{3,}", "\n\n", md).strip() + "\n"


def scrape_page(url: str, *, render: bool = False, timeout: float = 20.0,
                user_agent: Optional[str] = None, max_bytes: int = DEFAULT_MAX_BYTES,
                validator: Validator = default_validator) -> dict:
    """Fetch one page and return its SEO record plus clean markdown."""
    url = normalize_url(ensure_scheme(url)) or url
    if not validator(url):
        return {"error": f"URL rejected by validator (private/loopback/non-http): {url}"}
    fetcher = Fetcher(validator, user_agent, timeout, max_bytes)
    res = fetcher.fetch(url)
    out = {"url": url, "render": render, "render_error": None, "robots_allowed": None}
    try:
        out["robots_allowed"] = load_robots(fetcher, res["final_url"]).allowed(res["final_url"])
    except Exception:  # robots is advisory for a single user-requested page
        pass
    html = parsed = None
    if res["status"] == 200 and is_html(res["content_type"]) and res["body"]:
        html = decode_body(res["body"], res["content_type"])
        if render:
            with Renderer(validator, user_agent, timeout) as r:
                rendered = r.render(res["final_url"]) if r.error is None else None
                out["render_error"] = r.error
                out["render_blocked_requests"] = r.blocked_requests[:50]
            if rendered:
                html = rendered
        parsed = _parse(html, res["final_url"])
    out["record"] = page_record(res, html, parsed)
    out["markdown"] = html_to_markdown(html, res["final_url"]) if html else ""
    return out


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------

def _importable(module: str) -> bool:
    try:
        __import__(module)
        return True
    except ImportError:
        return False


def _print_human(cmd: str, result: dict) -> None:
    if "error" in result and cmd != "scrape":
        print(f"Error: {result['error']}")
        return
    if cmd == "map":
        print(f"Site: {result['start_url']}")
        print(f"URLs discovered: {result['total_urls']}")
        for pat, n in list(result["patterns"].items())[:15]:
            print(f"  {pat:30s} {n}")
        for r in result["urls"][:50]:
            print(f"  {r['url']}  [{', '.join(r['sources'])}]")
    elif cmd == "crawl":
        s = result["summary"]
        print(f"Crawled {s['pages_fetched']} pages on {s['scope_host']} "
              f"(complete: {s['crawl_complete']}, robots: {s['robots_txt']['mode']})")
        for k, v in s["counts"].items():
            print(f"  {k:32s} {v}")
    else:
        if result.get("error"):
            print(f"Error: {result['error']}")
            return
        rec = result["record"]
        print(f"# {rec.get('title') or rec['final_url']}  (HTTP {rec['status']})\n")
        print(result["markdown"])


def main(argv: Optional[list] = None) -> int:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--timeout", type=float, default=20.0, help="Per-request timeout (s)")
    common.add_argument("--user-agent", help="Override the claude-seo-crawler UA "
                        "(robots.txt is still evaluated for the claude-seo-crawler token)")
    common.add_argument("--render", action="store_true",
                        help="Render JavaScript with Playwright Chromium (slower)")
    common.add_argument("--json", action="store_true", help="Print JSON")
    common.add_argument("--output", help="Also write the full JSON result to this file")
    common.add_argument("--max-bytes", type=int, default=DEFAULT_MAX_BYTES,
                        help="Response size cap per page (bytes)")

    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0],
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    pm = sub.add_parser("map", parents=[common], help="Discover URLs (sitemaps, links)")
    pm.add_argument("url")
    pm.add_argument("--discover-links", action="store_true",
                    help="Also follow internal links (polite mini-crawl)")
    pm.add_argument("--max-pages", type=int, default=50)
    pm.add_argument("--max-depth", type=int, default=2)
    pm.add_argument("--delay", type=float, default=1.0)
    pm.add_argument("--limit", type=int, default=5000, help="Max URLs returned")
    pm.add_argument("--search", help="Only URLs containing this substring")

    pc = sub.add_parser("crawl", parents=[common], help="BFS crawl with SEO report")
    pc.add_argument("url")
    pc.add_argument("--max-pages", type=int, default=100)
    pc.add_argument("--max-depth", type=int, default=3)
    pc.add_argument("--delay", type=float, default=1.0,
                    help="Seconds between requests (robots Crawl-delay wins if larger)")
    pc.add_argument("--concurrency", type=int, default=1, help="Parallel requests (max 5)")
    pc.add_argument("--include", action="append", help="Regex; only matching URLs (repeatable)")
    pc.add_argument("--exclude", action="append", help="Regex; skip matching URLs (repeatable)")
    pc.add_argument("--sort-query", action="store_true", help="Sort query params when de-duplicating")
    pc.add_argument("--trailing-slash", choices=["keep", "strip", "add"], default="keep")
    pc.add_argument("--no-sitemap", action="store_true", help="Do not read sitemaps")
    pc.add_argument("--check-external", action="store_true",
                    help="HEAD-check external links (separate budget)")
    pc.add_argument("--external-budget", type=int, default=20)
    pc.add_argument("--jsonl", help="Write one JSON record per page to this file")
    pc.add_argument("--include-pages", action="store_true",
                    help="Include every page record in the JSON output")

    ps = sub.add_parser("scrape", parents=[common], help="One page to markdown + SEO record")
    ps.add_argument("url")
    ps.add_argument("--markdown-out", help="Write the markdown to this file")

    args = parser.parse_args(argv)
    missing = [name for name, mod in (("requests", "requests"), ("beautifulsoup4", "bs4"))
               if mod == "requests" and requests is None
               or mod == "bs4" and not _importable("bs4")]
    if missing:
        print(json.dumps({"error": f"missing dependencies: pip install {' '.join(missing)}"}))
        return 1

    if args.cmd == "map":
        result = map_site(args.url, discover_links=args.discover_links,
                          max_pages=args.max_pages, max_depth=args.max_depth,
                          delay=args.delay, limit=args.limit, search=args.search,
                          timeout=args.timeout, user_agent=args.user_agent)
    elif args.cmd == "crawl":
        result = crawl_site(args.url, max_pages=args.max_pages, max_depth=args.max_depth,
                            delay=args.delay, concurrency=args.concurrency,
                            include=args.include, exclude=args.exclude,
                            sort_query=args.sort_query, trailing_slash=args.trailing_slash,
                            use_sitemaps=not args.no_sitemap, render=args.render,
                            check_external=args.check_external,
                            external_budget=args.external_budget, timeout=args.timeout,
                            user_agent=args.user_agent, max_bytes=args.max_bytes,
                            jsonl_path=args.jsonl)
        if "error" not in result and not args.include_pages:
            result = dict(result)
            result["pages"] = f"{len(result['pages'])} records omitted (use --include-pages or --jsonl)"
    else:
        result = scrape_page(args.url, render=args.render, timeout=args.timeout,
                             user_agent=args.user_agent, max_bytes=args.max_bytes)
        if args.markdown_out and result.get("markdown"):
            with open(args.markdown_out, "w", encoding="utf-8") as fh:
                fh.write(result["markdown"])

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, ensure_ascii=False, default=list)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False, default=list))
    else:
        _print_human(args.cmd, result)
    return 2 if "error" in result and result.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
