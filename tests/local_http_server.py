"""Tiny threaded HTTP server on 127.0.0.1 for offline tests (no internet).

Routes map a path to (status, headers, body). Tests reach it through an
injected validator; the production validator still refuses loopback.
"""

import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Dict, Tuple

Route = Tuple[int, Dict[str, str], str]


class _Handler(BaseHTTPRequestHandler):
    routes: Dict[str, Route] = {}

    def do_GET(self):  # noqa: N802 - http.server API
        self._respond(send_body=True)

    def do_HEAD(self):  # noqa: N802 - http.server API
        self._respond(send_body=False)

    def _respond(self, send_body):
        self.server.hits.append((self.command, self.path))
        status, headers, body = self.server.routes.get(
            self.path, (404, {"Content-Type": "text/html"}, "<h1>Not found</h1>"))
        data = body.encode("utf-8")
        self.send_response(status)
        for k, v in headers.items():
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if send_body:
            self.wfile.write(data)

    def log_message(self, *args):  # keep pytest output clean
        pass


class LocalSite:
    """Context manager: start a server, expose base_url and a mutable routes dict."""

    def __init__(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
        self.server.routes = {}
        self.server.hits = []
        self.routes = self.server.routes
        self.hits = self.server.hits  # (method, path) of every request served
        self.base_url = f"http://127.0.0.1:{self.server.server_address[1]}"
        self._thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self._thread.start()
        return self

    def __exit__(self, *exc):
        self.server.shutdown()
        self.server.server_close()


def html(title, body, head_extra="", status=200, headers=None) -> Route:
    """Build an HTML route."""
    h = {"Content-Type": "text/html; charset=utf-8"}
    h.update(headers or {})
    doc = (f"<!doctype html><html lang='en'><head><title>{title}</title>{head_extra}</head>"
           f"<body>{body}</body></html>")
    return status, h, doc
