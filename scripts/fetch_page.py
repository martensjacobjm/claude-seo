#!/usr/bin/env python3
"""
Fetch a web page with proper headers and error handling.

SSRF protection: the URL and every redirect hop are validated with
safe_fetch.validate_public_url() (google_auth.validate_url() literal checks
plus a resolved-IP check) before they are requested, redirects are followed
manually, and connections are pinned to the validated IP (see safe_fetch.py).

Usage:
    python fetch_page.py https://example.com
    python fetch_page.py https://example.com --output page.html
"""

import argparse
import os
import sys
from typing import Optional
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import safe_fetch  # noqa: E402


DEFAULT_USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 ClaudeSEO/1.2"
)

# Googlebot UA for prerender/dynamic rendering detection.
# Prerender services (Prerender.io, Rendertron) serve fully rendered HTML to
# Googlebot but raw JS shells to other UAs. Comparing response sizes between
# DEFAULT_USER_AGENT and GOOGLEBOT_USER_AGENT reveals whether a site uses
# dynamic rendering, a key signal for SPA detection.
GOOGLEBOT_USER_AGENT = (
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
)

DEFAULT_HEADERS = {
    "User-Agent": DEFAULT_USER_AGENT,
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
}


def _prepared_url(url: str) -> str:
    """URL as requests sends it (adds "/" path, IDNA host, percent-encoding)."""
    try:
        prep = requests.models.PreparedRequest()
        prep.prepare_url(url, None)
        return prep.url
    except requests.exceptions.RequestException:
        return url


def fetch_page(
    url: str,
    timeout: int = 30,
    follow_redirects: bool = True,
    max_redirects: int = 5,
    user_agent: Optional[str] = None,
    fetcher: Optional["safe_fetch.SafeFetcher"] = None,
) -> dict:
    """
    Fetch a web page and return response details.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds
        follow_redirects: Whether to follow redirects
        max_redirects: Maximum number of redirects to follow
        user_agent: Custom User-Agent string
        fetcher: Optional safe_fetch.SafeFetcher (tests inject a validator/session);
            when given, its own timeout is used.

    Returns:
        Dictionary with:
            - url: Final URL after redirects
            - status_code: HTTP status code
            - content: Response body
            - headers: Response headers
            - redirect_chain: List of redirect URLs
            - redirect_details: List of {url, status_code} per redirect hop
            - error: Error message if failed
    """
    result = {
        "url": url,
        "status_code": None,
        "content": None,
        "headers": {},
        "redirect_chain": [],
        "redirect_details": [],
        "error": None,
    }

    # Validate URL
    parsed = urlparse(url)
    if not parsed.scheme:
        url = f"https://{url}"
        parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        result["error"] = f"Invalid URL scheme: {parsed.scheme}"
        return result

    headers = dict(DEFAULT_HEADERS)
    if user_agent:
        headers["User-Agent"] = user_agent

    # SSRF prevention: start URL and every redirect hop are validated
    # (literal host + resolved IPs) and connections are pinned.
    fetcher = fetcher or safe_fetch.SafeFetcher(timeout=timeout, max_redirects=max_redirects)
    res = fetcher.fetch(url, headers=headers, follow_redirects=follow_redirects,
                        max_redirects=max_redirects)

    # Track redirect chain with status codes (hops actually requested),
    # URLs in the same normalized form requests' Response.url used.
    result["redirect_chain"] = [_prepared_url(h["url"]) for h in res["hops"]]
    result["redirect_details"] = [
        {"url": _prepared_url(h["url"]), "status_code": h["status"]} for h in res["hops"]
    ]

    if res["error_kind"] == "blocked":
        reason = safe_fetch.check_public_url(res["final_url"]) or res["error"]
        result["error"] = f"Blocked: {reason}"
        return result
    if res["error_kind"] == "too_many_redirects":
        result["error"] = f"Too many redirects (max {max_redirects})"
        return result
    exc = res.get("exception")
    if res["error_kind"] == "timeout":
        result["error"] = f"Request timed out after {timeout} seconds"
        return result
    if res["error_kind"] == "ssl":
        result["error"] = f"SSL error: {exc}"
        return result
    if res["error_kind"] == "connection":
        result["error"] = f"Connection error: {exc}"
        return result
    if res["error_kind"] in ("request", "read"):
        result["error"] = f"Request failed: {exc or res['error']}"
        return result

    result["url"] = _prepared_url(res["final_url"])
    result["status_code"] = res["status"]
    result["content"] = safe_fetch.requests_text(res["body"], res["header_items"])
    result["headers"] = res["header_items"]
    return result


def main():
    parser = argparse.ArgumentParser(description="Fetch a web page for SEO analysis")
    parser.add_argument("url", help="URL to fetch")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--timeout", "-t", type=int, default=30, help="Timeout in seconds")
    parser.add_argument("--no-redirects", action="store_true", help="Don't follow redirects")
    parser.add_argument("--user-agent", help="Custom User-Agent string")
    parser.add_argument(
        "--googlebot",
        action="store_true",
        help=(
            "Use Googlebot UA to detect dynamic rendering / prerender services. "
            "Compare response size with default UA to identify SPA prerender configuration."
        ),
    )

    args = parser.parse_args()

    ua = args.user_agent
    if args.googlebot:
        ua = GOOGLEBOT_USER_AGENT

    result = fetch_page(
        args.url,
        timeout=args.timeout,
        follow_redirects=not args.no_redirects,
        user_agent=ua,
    )

    if result["error"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result["content"])
        print(f"Saved to {args.output}")
    else:
        print(result["content"])

    # Print metadata to stderr
    print(f"\nURL: {result['url']}", file=sys.stderr)
    print(f"Status: {result['status_code']}", file=sys.stderr)
    if result["redirect_details"]:
        for rd in result["redirect_details"]:
            print(f"  {rd['status_code']} -> {rd['url']}", file=sys.stderr)
        print(f"  {result['status_code']} -> {result['url']} (final)", file=sys.stderr)
    elif result["redirect_chain"]:
        print(f"Redirects: {' -> '.join(result['redirect_chain'])}", file=sys.stderr)


if __name__ == "__main__":
    main()
