#!/usr/bin/env python3
"""
Shared SSRF-safe HTTP fetching for scripts that request user-supplied URLs.

Redirects are followed manually and every hop (the start URL and each
Location target) must pass a validator before any request is sent to it. The
default validator is ``validate_url(url, resolve=True)`` from google_auth.py:
http/https only, no localhost or metadata host names, and every address the
host resolves to must be globally routable (private, loopback, link-local,
reserved and multicast addresses such as 127.0.0.1, 10.0.0.0/8 and
169.254.169.254 are refused). Response bodies are capped (5 MB by default).

The validator and the requests session are injectable, so tests can talk to
a local http.server through a validator that allows exactly that origin.
There is no environment-variable escape hatch.

Residual risk: the name is resolved once for the check and again by requests
for the connection, so a DNS rebinding server with a very short TTL can still
race the check.

Usage (library):
    from safe_fetch import safe_request
    res = safe_request("https://example.com")
    if res.error: ...
    html = res.text

Usage (CLI, JSON on stdout):
    python safe_fetch.py https://example.com
    python safe_fetch.py https://example.com --method HEAD --max-redirects 3
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional
from urllib.parse import urljoin

_SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)

from google_auth import validate_url  # noqa: E402  (stdlib-only module)

try:
    import requests
except ImportError:  # pragma: no cover - reported at call time
    requests = None

Validator = Callable[[str], bool]

REDIRECT_CODES = {301, 302, 303, 307, 308}
MAX_BODY_BYTES = 5_000_000
MAX_REDIRECTS = 5


def default_validator(url: str) -> bool:
    """Production validator: validate_url() with DNS resolution."""
    return validate_url(url, resolve=True)


@dataclass
class SafeResponse:
    """Outcome of safe_request().

    error_kind is one of None, "blocked", "request", "read",
    "too_many_redirects" or whatever a check_redirect callback returned.
    response is the last requests.Response (already closed, body preloaded)
    or None when no response was received.
    """

    url: str
    final_url: str
    status: Optional[int] = None
    headers: Dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    truncated: bool = False
    hops: List[dict] = field(default_factory=list)
    error: Optional[str] = None
    error_kind: Optional[str] = None
    exception: Optional[BaseException] = None
    response: object = None

    @property
    def text(self) -> str:
        """Body decoded the way requests' Response.text decodes it."""
        if self.response is not None:
            return self.response.text
        return self.body.decode("utf-8", errors="replace")


def safe_request(
    url: str,
    method: str = "GET",
    *,
    session=None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 20.0,
    max_redirects: int = MAX_REDIRECTS,
    max_bytes: int = MAX_BODY_BYTES,
    validator: Optional[Validator] = None,
    follow_redirects: bool = True,
    before_request: Optional[Callable[[str], None]] = None,
    check_redirect: Optional[Callable[[str], Optional[str]]] = None,
) -> SafeResponse:
    """Request url, following redirects manually and validating every hop.

    Args:
        url: Absolute http(s) URL.
        method: HTTP method (redirects keep it; HEAD never reads a body).
        session: requests.Session to reuse (cookies persist across hops).
        headers: Request headers sent on every hop.
        timeout: Per-request timeout in seconds.
        max_redirects: Redirects to follow before giving up.
        max_bytes: Body cap; longer bodies are cut and truncated=True.
        validator: URL check run before each request (default_validator).
        follow_redirects: False returns the first response, 3xx included.
        before_request: Called with each URL just before it is requested
            (politeness delays, request counters).
        check_redirect: Called with each redirect target; a non-empty
            return value stops the chain with that value as error/error_kind.

    Returns:
        SafeResponse. Blocked hops are never requested.
    """
    if requests is None:
        raise RuntimeError("requests library required: pip install requests")
    validator = validator or default_validator
    session = session or requests.Session()
    out = SafeResponse(url=url, final_url=url)
    current = url
    for _ in range(max_redirects + 1):
        out.final_url = current
        if not validator(current):
            out.error_kind = "blocked"
            out.error = (f"blocked: {current} failed URL validation "
                         "(private, loopback, link-local, reserved or metadata address)")
            return out
        if before_request:
            before_request(current)
        try:
            resp = session.request(method, current, headers=headers, timeout=timeout,
                                   allow_redirects=False, stream=True)
        except requests.exceptions.RequestException as exc:
            out.error_kind, out.exception = "request", exc
            out.error = f"{type(exc).__name__}: {exc}"[:300]
            return out
        try:
            location = resp.headers.get("Location")
            if follow_redirects and resp.status_code in REDIRECT_CODES and location:
                nxt = urljoin(current, location)
                out.hops.append({"url": current, "status": resp.status_code,
                                 "location": nxt})
                if check_redirect:
                    problem = check_redirect(nxt)
                    if problem:
                        out.status, out.final_url = resp.status_code, nxt
                        out.error = out.error_kind = problem
                        return out
                current = nxt
                continue
            out.status = resp.status_code
            out.headers = dict(resp.headers)
            out.response = resp
            body = bytearray()
            if method.upper() != "HEAD":
                try:
                    for chunk in resp.iter_content(65536):
                        body.extend(chunk)
                        if len(body) > max_bytes:
                            out.truncated = True
                            del body[max_bytes:]
                            break
                except requests.exceptions.RequestException as exc:
                    out.error_kind, out.exception = "read", exc
                    out.error = f"read error: {exc}"[:300]
            out.body = bytes(body)
            resp._content = out.body  # lets resp.text / resp.json() use the capped body
            resp._content_consumed = True
            return out
        finally:
            resp.close()
    out.error_kind = "too_many_redirects"
    out.error = f"too many redirects (> {max_redirects})"
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="SSRF-safe fetch (manual, validated redirects)")
    parser.add_argument("url", help="http(s) URL to fetch")
    parser.add_argument("--method", default="GET", choices=["GET", "HEAD"])
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--max-redirects", type=int, default=MAX_REDIRECTS)
    parser.add_argument("--max-bytes", type=int, default=MAX_BODY_BYTES)
    args = parser.parse_args()
    res = safe_request(args.url, args.method, timeout=args.timeout,
                       max_redirects=args.max_redirects, max_bytes=args.max_bytes)
    print(json.dumps({
        "url": res.url, "final_url": res.final_url, "status": res.status,
        "hops": res.hops, "headers": res.headers, "bytes": len(res.body),
        "truncated": res.truncated, "error": res.error, "error_kind": res.error_kind,
    }, indent=2))
    sys.exit(1 if res.error else 0)


if __name__ == "__main__":
    main()
