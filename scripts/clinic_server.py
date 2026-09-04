#!/usr/bin/env python3
"""clinic_server.py — localhost backend for the EMG research-centre web GUI (Phaser).

Serves webapp/ and the endpoints the front-end calls (see webapp/README.md). Binds 127.0.0.1 only.
    GET  /health             -> {ok, ollama, url}          is Michael's brain reachable?
    POST /ask   {message}     -> {ok, answer, action}       Michael (michael.ask); scripted fallback
    GET  /launch?target=key   -> {ok, msg}                  launch the PyQt scope (fixed whitelist)

    python scripts/clinic_server.py      # http://127.0.0.1:8787/
Michael's LLM lives on the GPU server; reach it via an SSH tunnel and MICHAEL_URL, e.g.
    ssh -L 11434:localhost:11434 zrq@10.130.153.169     (then MICHAEL_URL=http://localhost:11434)
"""
import json
import os
import subprocess
import sys
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from michael.michael import ask as michael_ask, URL as OLLAMA_URL

HOST, PORT = "127.0.0.1", 8787
PY = sys.executable
SCOPE = os.path.join(ROOT, "emgscope.py")
WEBAPP = os.path.join(ROOT, "webapp")

# whitelist: only these can be launched (never an arbitrary command)
TARGETS = {
    "sim1":  ["--sim", "--channels", "1"],
    "sim5":  ["--sim", "--channels", "5"],
    "live1": ["--port", "COM8", "--baud", "921600", "--channels", "1", "--fs", "2000", "--coupling", "DC", "--kick"],
    "live5": ["--port", "COM8", "--baud", "921600", "--channels", "5", "--fs", "2000", "--coupling", "AC", "--kick"],
}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=(WEBAPP if os.path.isdir(WEBAPP) else ROOT), **k)

    def log_message(self, *a):
        pass

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/health":
            ollama = False
            try:
                with urllib.request.urlopen(OLLAMA_URL + "/api/tags", timeout=3) as r:
                    ollama = (r.status == 200)
            except Exception:
                ollama = False
            return self._json(200, {"ok": True, "ollama": ollama, "url": OLLAMA_URL})
        if u.path == "/launch":
            target = parse_qs(u.query).get("target", [""])[0]
            args = TARGETS.get(target)
            if args is None:
                return self._json(400, {"ok": False, "msg": f"unknown target '{target}'"})
            try:
                subprocess.Popen([PY, SCOPE, *args], cwd=ROOT)
                return self._json(200, {"ok": True, "msg": f"launched {target}"})
            except Exception as e:
                return self._json(500, {"ok": False, "msg": str(e)})
        return super().do_GET()

    def do_POST(self):
        u = urlparse(self.path)
        n = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(n) if n else b"{}"
        try:
            body = json.loads(raw.decode("utf-8") or "{}")
        except Exception:
            body = {}
        if u.path == "/ask":
            res = michael_ask(body.get("message", ""))
            return self._json(200, {"ok": True, **res})
        return self._json(404, {"ok": False, "msg": "not found"})


def main():
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"clinic server: http://{HOST}:{PORT}/   (Michael -> {OLLAMA_URL})   Ctrl+C to stop")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
        srv.shutdown()


if __name__ == "__main__":
    main()
