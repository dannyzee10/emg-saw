#!/usr/bin/env python3
"""
EMG dashboard server — serves the agent world-map (agent_map.html) with WORKING launch
buttons. A browser can't run a local app from a file:// page (sandbox), so this tiny
localhost server exposes a whitelisted /launch endpoint the map's buttons call via fetch().

    python scripts/emg_map_server.py        # opens http://127.0.0.1:8787/agent_map.html

Safety: binds 127.0.0.1 only, and only launches the fixed TARGETS below — never an
arbitrary command from the query string.
"""
import json
import os
import subprocess
import sys
import threading
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOST, PORT = "127.0.0.1", 8787
PY = sys.executable
SCOPE = os.path.join(ROOT, "emgscope.py")
AGENT_MAP = os.path.join(ROOT, "scripts", "agent_map.py")

# whitelist: target key -> emgscope.py args. Nothing else can be launched.
TARGETS = {
    "sim1":  ["--sim", "--channels", "1"],
    "sim5":  ["--sim", "--channels", "5"],
    "live1": ["--port", "COM8", "--baud", "921600", "--channels", "1",
              "--fs", "2000", "--coupling", "DC", "--kick"],
    "live5": ["--port", "COM8", "--baud", "921600", "--channels", "5",
              "--fs", "2000", "--coupling", "AC", "--kick"],
}


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=ROOT, **k)

    def log_message(self, *a):
        pass  # quiet

    def _json(self, code, obj):
        body = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
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
        if u.path == "/refresh":
            try:
                subprocess.run([PY, AGENT_MAP, "--no-open"], cwd=ROOT, timeout=180)
                return self._json(200, {"ok": True, "msg": "map refreshed"})
            except Exception as e:
                return self._json(500, {"ok": False, "msg": str(e)})
        if u.path == "/":
            self.path = "/agent_map.html"
        return super().do_GET()


def main():
    if not os.path.exists(os.path.join(ROOT, "agent_map.html")):
        subprocess.run([PY, AGENT_MAP, "--no-open"], cwd=ROOT)
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    url = f"http://{HOST}:{PORT}/agent_map.html"
    print(f"EMG dashboard: {url}   (Ctrl+C to stop)")
    threading.Timer(0.6, lambda: webbrowser.open(url)).start()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
        srv.shutdown()


if __name__ == "__main__":
    main()
