"""Virtual phone — the SMS app on Jan Kowalski's handset.

A web UI (phone.jan.pl in the twin) that shows the SMS inbox pulled from the
virtual carrier. A human reads the one-time code here; an automat can read the
very same inbox over the mesh. Opening it records a phone:// URI event.

    GET /            SMS inbox (auto-refreshing), big text for OCR
    GET /api/inbox   JSON inbox for automation
    GET /health
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

sys.path.insert(0, "/opt/twin")
from twinlib import emit  # noqa: E402

SMS_URL = os.environ.get("SMS_URL", "http://sms-gateway:9810")
OWNER = os.environ.get("PHONE_OWNER", "jan")
MSISDN = os.environ.get("PHONE_MSISDN", "+48500100200")

PAGE = """<!doctype html><html lang=pl><head><meta charset=utf-8><title>Telefon Jana</title>
<meta http-equiv=refresh content=3>
<style>body{{font-family:Arial,sans-serif;background:#111;color:#eee;margin:0}}
.bar{{background:#0a4;padding:16px 20px;font-size:24px}} .msg{{border-bottom:1px solid #333;padding:20px 24px}}
.from{{color:#7bf;font-size:22px}} .text{{font-size:30px;margin-top:8px}}
.empty{{padding:40px;font-size:26px;color:#888}}</style></head>
<body><div class=bar>SMS — {msisdn}</div>{body}</body></html>"""


def _inbox() -> list:
    try:
        with urllib.request.urlopen(f"{SMS_URL}/inbox/{MSISDN}", timeout=4) as resp:
            return json.load(resp).get("messages", [])
    except Exception:
        return []


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        return

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            self.send_response(200); self.end_headers(); self.wfile.write(b"ok"); return
        if path == "/api/inbox":
            emit(f"phone://{OWNER}/sms/query/read", actor=OWNER, msisdn=MSISDN)
            body = json.dumps({"ok": True, "messages": _inbox()}).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers(); self.wfile.write(body); return
        # HTML inbox
        emit(f"phone://{OWNER}/sms/query/open", actor=OWNER, msisdn=MSISDN)
        msgs = list(reversed(_inbox()))
        if msgs:
            rows = "".join(
                f"<div class=msg><div class=from>{m['from']}</div>"
                f"<div class=text>{m['text']}</div></div>" for m in msgs)
        else:
            rows = "<div class=empty>Brak wiadomosci SMS.</div>"
        page = PAGE.format(msisdn=MSISDN, body=rows).encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(page)))
        self.end_headers(); self.wfile.write(page)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "9830"))
    print(f"phone {OWNER} on :{port}", flush=True)
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
