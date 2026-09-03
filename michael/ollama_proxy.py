"""Token-auth reverse proxy for Ollama.

Ollama has no authentication, so we must not expose it raw through a public tunnel (frp /
SakuraFrp). This tiny proxy listens on 127.0.0.1:PROXY_PORT, requires a matching
``X-Michael-Token`` header, and only then forwards to the local Ollama (11434). Expose the
PROXY_PORT through the tunnel (not 11434); only holders of the token can reach Michael.

    MICHAEL_TOKEN=<secret> python michael/ollama_proxy.py     # run on the lab server
env:
    MICHAEL_TOKEN        the shared secret (required; refuses all requests if unset)
    MICHAEL_PROXY_PORT   listen port (default 11500) -> this is what the tunnel exposes
    OLLAMA_LOCAL         upstream Ollama (default http://127.0.0.1:11434)
"""
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

TOKEN = os.environ.get("MICHAEL_TOKEN", "")
PROXY_PORT = int(os.environ.get("MICHAEL_PROXY_PORT", "11500"))
OLLAMA = os.environ.get("OLLAMA_LOCAL", "http://127.0.0.1:11434").rstrip("/")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _authorized(self):
        return bool(TOKEN) and self.headers.get("X-Michael-Token", "") == TOKEN

    def _forward(self, method):
        if not self._authorized():
            body = b'{"error":"unauthorized"}'
            self.send_response(401)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
            return
        n = int(self.headers.get("Content-Length", 0) or 0)
        data = self.rfile.read(n) if n else None
        req = urllib.request.Request(
            OLLAMA + self.path, data=data, method=method,
            headers={"Content-Type": self.headers.get("Content-Type", "application/json")})
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                out, code = r.read(), r.status
        except Exception as e:
            msg = str(e).encode()
            self.send_response(502)
            self.send_header("Content-Length", str(len(msg)))
            self.end_headers()
            self.wfile.write(msg)
            return
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(out)))
        self.end_headers()
        self.wfile.write(out)

    def do_GET(self):
        self._forward("GET")

    def do_POST(self):
        self._forward("POST")


def main():
    if not TOKEN:
        print("WARNING: MICHAEL_TOKEN is not set -- every request will be rejected. Set it and re-run.")
    print(f"Michael token-proxy on 127.0.0.1:{PROXY_PORT} -> {OLLAMA}   (expose {PROXY_PORT} via the tunnel)")
    ThreadingHTTPServer(("127.0.0.1", PROXY_PORT), Handler).serve_forever()


if __name__ == "__main__":
    main()
