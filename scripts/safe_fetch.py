#!/usr/bin/env python3
"""
SSRF-safe HTTP fetching shared by every Claude SEO script that connects to a
user-supplied URL (fetch_page, verify_backlinks, nlp_analyze, repo_live_diff,
hreflang_check, site_crawl, and the Playwright screenshot/visual scripts).

What it guarantees:

* ``validate_public_url(url)``: http/https only; the literal-host checks of
  ``google_auth.validate_url()`` (blocked hostnames such as localhost,
  *.internal and cloud metadata names; IP literals incl. 2130706433-style
  forms); then ``getaddrinfo`` on the host, rejecting the URL if ANY resolved
  address is private (RFC 1918, ULA), loopback, link-local (169.254.169.254),
  shared/CGNAT, reserved, multicast, unspecified, or an IPv4-mapped, 6to4 or
  NAT64 IPv6 address embedding one of those. A name that does not resolve is
  not rejected here (the request then fails with a DNS error; see below).
* ``SafeFetcher`` / ``safe_get()``: redirects are followed manually (max hops)
  and EVERY hop is validated before it is requested; timeouts; streamed body
  with a byte cap; optional polite per-host delay. The validator and the
  requests session are injectable for tests. There is no environment-variable
  bypass: tests inject a validator that allows exactly their fixture origin.

DNS rebinding (check-then-connect race):
    Sessions built by ``make_session()`` (the SafeFetcher default) mount a
    transport adapter whose connections resolve the host once at connect
    time, validate every resolved address, and open the socket to that
    validated IP. TLS SNI, certificate verification and the Host header still
    use the original hostname, so a hostname that answers with a public IP to
    the validator and a private IP to the connection is refused.
    Limitations: (1) when requests routes a URL through an HTTP(S) proxy
    (HTTP_PROXY/HTTPS_PROXY), the proxy resolves the target, so only the
    pre-request check applies; (2) an injected session is used as-is (no
    pinning); (3) the Playwright helpers can only filter browser requests by
    URL, the browser resolves DNS itself.

CLI (debugging aid):
    python safe_fetch.py check <url>          # {"url", "allowed", "reason"}
    python safe_fetch.py get <url> [--head]   # status, final URL, hops (no body)
"""

from __future__ import annotations

import argparse
import json
import os
import re
import socket
import sys
import time
from typing import Callable, Dict, List, Optional
from urllib.parse import urljoin, urlparse

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)
from google_auth import ip_is_public, validate_url  # noqa: E402  (stdlib-only)

try:
    import requests
    from requests.adapters import HTTPAdapter
    from urllib3.connection import HTTPConnection, HTTPSConnection
    from urllib3.connectionpool import HTTPConnectionPool, HTTPSConnectionPool
except ImportError:  # pragma: no cover - reported when a fetch is attempted
    requests = None
    HTTPAdapter = object  # type: ignore[assignment,misc]

REDIRECT_CODES = {301, 302, 303, 307, 308}
MAX_BODY_BYTES = 5_000_000
DEFAULT_TIMEOUT = 20.0
DEFAULT_MAX_REDIRECTS = 5
DEFAULT_USER_AGENT = ("Mozilla/5.0 (compatible; ClaudeSEO/1.8; "
                      "+https://github.com/AgriciDaniel/claude-seo)")
BLOCKED_MESSAGE = "(private, loopback, link-local or metadata address)"

Validator = Callable[[str], bool]
# (scheme, host, port, resolved_ip) -> allowed?
AddressCheck = Callable[[str, str, int, str], bool]


# --- validation ------------------------------------------------------------------

def is_public_ip(ip) -> bool:
    """True only for a globally routable unicast address (see google_auth.ip_is_public)."""
    return ip_is_public(ip)


def resolve_host(host: str) -> Optional[List[str]]:
    """All addresses host resolves to, or None when resolution fails."""
    try:
        infos = socket.getaddrinfo(host.strip("[]").rstrip("."), None)
    except (socket.gaierror, UnicodeError, OSError):
        return None
    return [info[4][0] for info in infos]


def check_public_url(url: str, resolve: bool = True) -> Optional[str]:
    """Return None when url is a public http(s) URL, else the reason it is refused."""
    if not isinstance(url, str) or not validate_url(url):
        return f"{url} failed URL validation {BLOCKED_MESSAGE}"
    if not resolve:
        return None
    host = urlparse(url).hostname or ""
    addrs = resolve_host(host)
    if addrs is None:
        return None  # unresolvable: the request itself fails with a DNS error
    for addr in addrs:
        if not is_public_ip(addr):
            return f"{host} resolves to non-public address {addr.split('%', 1)[0]}"
    return None


def validate_public_url(url: str, resolve: bool = True) -> bool:
    """Literal checks via google_auth.validate_url() plus resolved-IP checks."""
    return check_public_url(url, resolve=resolve) is None


# --- connect-time pinning (DNS rebinding) -----------------------------------------

class BlockedAddressError(OSError):
    """Raised at connect time when a host resolves to a non-public address."""


def default_address_check(scheme: str, host: str, port: int, ip: str) -> bool:
    """Production rule for connect-time checks: the resolved IP must be public."""
    return is_public_ip(ip)


class _PinnedMixin:
    """urllib3 connection that validates and pins the resolved address."""

    _scheme = "http"
    _address_check: AddressCheck = staticmethod(default_address_check)

    def _new_conn(self):  # type: ignore[override]
        if getattr(self, "proxy", None):  # the proxy resolves the target
            return super()._new_conn()  # type: ignore[misc]
        host = self._dns_host  # type: ignore[attr-defined]
        try:
            infos = socket.getaddrinfo(host.rstrip("."), self.port, 0,  # type: ignore[attr-defined]
                                       socket.SOCK_STREAM)
        except (socket.gaierror, UnicodeError, OSError):
            return super()._new_conn()  # type: ignore[misc]  # raises the DNS error
        addrs = [info[4][0] for info in infos]
        for addr in addrs:
            if not self._address_check(self._scheme, host.rstrip("."), self.port, addr):  # type: ignore[attr-defined]
                raise BlockedAddressError(
                    f"blocked: {host} resolved to non-public address "
                    f"{addr.split('%', 1)[0]} at connect time")
        original = host
        self._dns_host = addrs[0]  # type: ignore[attr-defined]  # socket only; SNI/Host keep the name
        try:
            return super()._new_conn()  # type: ignore[misc]
        finally:
            self._dns_host = original  # type: ignore[attr-defined]


class PinnedAdapter(HTTPAdapter):  # type: ignore[misc,valid-type]
    """requests transport adapter that connects only to validated IPs."""

    def __init__(self, address_check: Optional[AddressCheck] = None, **kwargs) -> None:
        self._address_check = address_check or default_address_check
        super().__init__(**kwargs)

    def init_poolmanager(self, *args, **kwargs):
        super().init_poolmanager(*args, **kwargs)
        check = staticmethod(self._address_check)
        http_conn = type("PinnedHTTPConnection", (_PinnedMixin, HTTPConnection),
                         {"_scheme": "http", "_address_check": check})
        https_conn = type("PinnedHTTPSConnection", (_PinnedMixin, HTTPSConnection),
                          {"_scheme": "https", "_address_check": check})
        self.poolmanager.pool_classes_by_scheme = {
            "http": type("PinnedHTTPConnectionPool", (HTTPConnectionPool,),
                         {"ConnectionCls": http_conn}),
            "https": type("PinnedHTTPSConnectionPool", (HTTPSConnectionPool,),
                          {"ConnectionCls": https_conn}),
        }


def address_check_for(validator: Optional[Validator]) -> Optional[AddressCheck]:
    """Connect-time rule matching a URL validator.

    None (production default) for validate_public_url; for an injected test
    validator, an address is allowed when it is public OR the validator
    accepts that origin (so a loopback fixture origin keeps working).
    """
    if validator is None or validator is validate_public_url:
        return None

    def check(scheme: str, host: str, port: int, ip: str) -> bool:
        h = f"[{host}]" if ":" in host else host
        return is_public_ip(ip) or bool(validator(f"{scheme}://{h}:{port}/"))
    return check


def make_session(address_check: Optional[AddressCheck] = None) -> "requests.Session":
    """A requests.Session whose direct connections are validated and pinned."""
    if requests is None:
        raise RuntimeError("requests library required: pip install requests")
    session = requests.Session()
    adapter = PinnedAdapter(address_check)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def _find_blocked(exc: BaseException) -> Optional[BlockedAddressError]:
    """Find a BlockedAddressError in an exception's cause/context/args chain."""
    stack, seen = [exc], set()
    while stack:
        e = stack.pop()
        if id(e) in seen:
            continue
        seen.add(id(e))
        if isinstance(e, BlockedAddressError):
            return e
        for nxt in (e.__cause__, e.__context__, getattr(e, "reason", None),
                    *[a for a in getattr(e, "args", ()) if isinstance(a, BaseException)]):
            if isinstance(nxt, BaseException):
                stack.append(nxt)
    return None


def _error_kind(exc: BaseException) -> str:
    if isinstance(exc, requests.exceptions.Timeout):
        return "timeout"
    if isinstance(exc, requests.exceptions.SSLError):
        return "ssl"
    if isinstance(exc, requests.exceptions.ConnectionError):
        return "connection"
    return "request"


# --- decoding ----------------------------------------------------------------------

def decode_body(body: bytes, content_type: str) -> str:
    """Decode with the header charset, else a <meta charset>, else UTF-8, else Latin-1."""
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


def requests_text(body: bytes, header_items: Dict[str, str]) -> str:
    """Decode body exactly as requests' Response.text would for these headers."""
    resp = requests.models.Response()
    resp._content = body
    resp.headers = requests.structures.CaseInsensitiveDict(header_items)
    resp.encoding = requests.utils.get_encoding_from_headers(resp.headers)
    return resp.text


# --- fetching ----------------------------------------------------------------------

class SafeFetcher:
    """HTTP GET/HEAD with per-hop URL validation, a body cap and optional delay.

    ``validator`` (url -> bool) runs on the start URL and every redirect
    target before it is requested; the default is validate_public_url().
    ``session`` defaults to make_session(), which also pins each connection to
    a validated IP. With an injected validator the connect-time check allows
    an address when it is public OR the validator accepts that origin, so a
    test validator that allows one loopback fixture keeps working.
    """

    def __init__(self, validator: Optional[Validator] = None, delay: float = 0.0,
                 timeout: float = DEFAULT_TIMEOUT, max_redirects: int = DEFAULT_MAX_REDIRECTS,
                 session: Optional["requests.Session"] = None,
                 user_agent: str = DEFAULT_USER_AGENT, max_bytes: int = MAX_BODY_BYTES,
                 headers: Optional[Dict[str, str]] = None) -> None:
        if requests is None:
            raise RuntimeError("requests library required: pip install requests")
        self.validator: Validator = validator or validate_public_url
        self.delay = max(0.0, delay)
        self.timeout = timeout
        self.max_redirects = max_redirects
        self.max_bytes = max_bytes
        self.session = session or make_session(address_check_for(validator))
        self.headers = {"User-Agent": user_agent,
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"}
        self.headers.update(headers or {})
        self._last: Dict[str, float] = {}
        self.requests_made = 0

    def _wait(self, host: str) -> None:
        last = self._last.get(host)
        if last is not None and self.delay:
            remaining = self.delay - (time.monotonic() - last)
            if remaining > 0:
                time.sleep(remaining)
        self._last[host] = time.monotonic()

    def fetch(self, url: str, method: str = "GET", follow_redirects: bool = True,
              max_redirects: Optional[int] = None, headers: Optional[Dict[str, str]] = None,
              max_bytes: Optional[int] = None) -> dict:
        """Fetch url, following redirects manually; every hop is validated.

        Returns a dict: url, final_url, status, headers (lower-cased keys),
        header_items (original case), body (bytes), text, bytes, truncated,
        hops [{url, status, location}], error, error_kind (blocked, timeout,
        ssl, connection, request, read, too_many_redirects) and blocked.
        On a request exception the result also carries "exception" (not
        JSON-safe; get() drops it).
        """
        method = method.upper()
        limit = self.max_redirects if max_redirects is None else max_redirects
        cap = max_bytes or self.max_bytes
        req_headers = dict(self.headers)
        req_headers.update(headers or {})
        result = {"url": url, "final_url": url, "status": None, "headers": {},
                  "header_items": {}, "body": b"", "text": "", "bytes": 0,
                  "truncated": False, "hops": [], "error": None, "error_kind": None,
                  "blocked": False}
        current = url
        for _ in range(limit + 1):
            if not self.validator(current):
                result.update(final_url=current, blocked=True, error_kind="blocked",
                              error=f"blocked: {current} failed URL validation {BLOCKED_MESSAGE}")
                return result
            self._wait(urlparse(current).netloc)
            try:
                self.requests_made += 1
                resp = self.session.request(method, current, headers=req_headers,
                                            timeout=self.timeout, allow_redirects=False,
                                            stream=True)
            except requests.RequestException as exc:
                blocked = _find_blocked(exc)
                if blocked is not None:
                    result.update(final_url=current, blocked=True, error_kind="blocked",
                                  error=str(blocked)[:300])
                else:
                    result.update(final_url=current, error_kind=_error_kind(exc),
                                  error=f"{type(exc).__name__}: {exc}"[:300])
                result["exception"] = exc
                return result
            try:
                loc = resp.headers.get("Location")
                if follow_redirects and resp.status_code in REDIRECT_CODES and loc:
                    nxt = urljoin(current, loc)
                    result["hops"].append({"url": current, "status": resp.status_code,
                                           "location": nxt})
                    if resp.status_code == 303 and method != "HEAD":
                        method = "GET"
                    current = nxt
                    continue
                body = bytearray()
                if method != "HEAD":
                    try:
                        for chunk in resp.iter_content(65536):
                            body.extend(chunk)
                            if len(body) > cap:
                                del body[cap:]
                                result["truncated"] = True
                                break
                    except requests.RequestException as exc:
                        result.update(error_kind="read", error=f"read error: {exc}"[:300])
                content_type = resp.headers.get("Content-Type", "")
                result.update(final_url=current, status=resp.status_code,
                              headers={k.lower(): v for k, v in resp.headers.items()},
                              header_items=dict(resp.headers), body=bytes(body),
                              bytes=len(body), text=decode_body(bytes(body), content_type))
                return result
            finally:
                resp.close()
        result.update(final_url=current, error_kind="too_many_redirects",
                      error=f"too many redirects (> {limit})")
        return result

    def get(self, url: str) -> dict:
        """GET url (JSON-safe result: fetch() without body, header_items, exception)."""
        res = self.fetch(url)
        for key in ("body", "header_items", "exception"):
            res.pop(key, None)
        return res


def safe_get(url: str, **kwargs) -> dict:
    """One-shot GET through a SafeFetcher; kwargs go to SafeFetcher() or fetch()."""
    fetch_keys = {"method", "follow_redirects", "headers", "max_bytes"}
    fetch_kw = {k: kwargs.pop(k) for k in list(kwargs) if k in fetch_keys}
    return SafeFetcher(**kwargs).fetch(url, **fetch_kw)


def playwright_route_guard(validator: Optional[Validator] = None,
                           blocked: Optional[list] = None) -> Callable:
    """Handler for page.route("**/*", ...): abort requests to non-public URLs.

    Chromium resolves DNS itself, so this filters by URL (with a resolved-IP
    check) only; it cannot pin the connection.
    """
    check = validator or validate_public_url

    def guard(route):
        target = route.request.url
        if target.startswith(("data:", "blob:")) or check(target):
            route.continue_()
        else:
            if blocked is not None:
                blocked.append(target[:200])
            route.abort()
    return guard


def main() -> int:
    parser = argparse.ArgumentParser(description="SSRF-safe URL check / fetch (debug aid)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p_check = sub.add_parser("check", help="validate a URL (literal + DNS checks)")
    p_check.add_argument("url")
    p_get = sub.add_parser("get", help="fetch a URL with per-hop validation")
    p_get.add_argument("url")
    p_get.add_argument("--head", action="store_true", help="use HEAD instead of GET")
    p_get.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT)
    args = parser.parse_args()
    if args.cmd == "check":
        reason = check_public_url(args.url)
        print(json.dumps({"url": args.url, "allowed": reason is None, "reason": reason}, indent=2))
        return 0 if reason is None else 1
    res = SafeFetcher(timeout=args.timeout).fetch(args.url, method="HEAD" if args.head else "GET")
    out = {k: res[k] for k in ("url", "final_url", "status", "hops", "bytes", "truncated",
                               "error", "error_kind", "blocked")}
    print(json.dumps(out, indent=2))
    return 0 if res["error"] is None else 1


if __name__ == "__main__":
    sys.exit(main())
