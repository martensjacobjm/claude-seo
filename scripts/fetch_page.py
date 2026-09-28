#!/usr/bin/env python3
"""
Fetch a web page with proper headers and error handling.

Usage:
    python fetch_page.py https://example.com
    python fetch_page.py https://example.com --output page.html
"""

import argparse
import os
import sys
from typing import Callable, Optional
from urllib.parse import urlparse

try:
    import requests
except ImportError:
    print("Error: requests library required. Install with: pip install requests")
    sys.exit(1)

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from safe_fetch import MAX_BODY_BYTES, safe_request  # noqa: E402


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


def fetch_page(
    url: str,
    timeout: int = 30,
    follow_redirects: bool = True,
    max_redirects: int = 5,
    user_agent: Optional[str] = None,
    validator: Optional[Callable[[str], bool]] = None,
) -> dict:
    """
    Fetch a web page and return response details.

    Args:
        url: The URL to fetch
        timeout: Request timeout in seconds
        follow_redirects: Whether to follow redirects
        max_redirects: Maximum number of redirects to follow
        user_agent: Custom User-Agent string
        validator: URL check for every hop (default: validate_url with DNS
            resolution); injectable for tests, never relaxed by env vars

    Returns:
        Dictionary with:
            - url: Final URL after redirects
            - status_code: HTTP status code
            - content: Response body
            - headers: Response headers
            - redirect_chain: List of redirect URLs
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

    # SSRF prevention: redirects are followed manually and every hop is
    # checked with validate_url(url, resolve=True) (or the injected validator)
    # before it is requested, so a public URL cannot bounce to 127.0.0.1,
    # 169.254.169.254 or an RFC 1918 address.
    headers = dict(DEFAULT_HEADERS)
    if user_agent:
        headers["User-Agent"] = user_agent

    res = safe_request(
        url,
        session=requests.Session(),
        headers=headers,
        timeout=timeout,
        max_redirects=max_redirects,
        max_bytes=MAX_BODY_BYTES,
        validator=validator,
        follow_redirects=follow_redirects,
    )

    if res.error_kind == "blocked":
        result["error"] = f"Blocked: {res.final_url} is not a public address (SSRF protection)"
    elif res.error_kind == "too_many_redirects":
        result["error"] = f"Too many redirects (max {max_redirects})"
    elif res.error_kind == "request":
        e = res.exception
        if isinstance(e, requests.exceptions.Timeout):
            result["error"] = f"Request timed out after {timeout} seconds"
        elif isinstance(e, requests.exceptions.SSLError):
            result["error"] = f"SSL error: {e}"
        elif isinstance(e, requests.exceptions.ConnectionError):
            result["error"] = f"Connection error: {e}"
        else:
            result["error"] = f"Request failed: {e}"
    elif res.error_kind == "read":
        result["error"] = f"Request failed: {res.exception}"
    else:
        result["url"] = res.final_url
        result["status_code"] = res.status
        result["content"] = res.text
        result["headers"] = res.headers

        # Track redirect chain with status codes
        if res.hops:
            result["redirect_chain"] = [h["url"] for h in res.hops]
            result["redirect_details"] = [
                {"url": h["url"], "status_code": h["status"]}
                for h in res.hops
            ]

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
