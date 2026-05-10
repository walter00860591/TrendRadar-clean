#!/usr/bin/env python3
"""Simple webhook receiver for TrendRadar generic webhook notifications."""

import json
import os
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler

LISTEN_PORT = int(os.environ.get("WEBHOOK_PORT", "9080"))
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)


class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length).decode("utf-8")

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = os.path.join(LOG_DIR, f"webhook_{ts}.json")

        # Try to parse as JSON for pretty printing
        try:
            data = json.loads(body)
            pretty = json.dumps(data, ensure_ascii=False, indent=2)
        except json.JSONDecodeError:
            pretty = body
            data = {}

        with open(log_file, "w", encoding="utf-8") as f:
            f.write(pretty)

        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
              f"Received webhook -> {log_file} ({len(body)} bytes)")

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"status": "ok"}).encode())

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        files = sorted(os.listdir(LOG_DIR))
        self.wfile.write(f"TrendRadar Webhook Receiver\n".encode("utf-8"))
        self.wfile.write(f"Received {len(files)} notifications\n".encode("utf-8"))
        self.wfile.write(f"Latest logs: {files[-5:]}\n".encode("utf-8"))

    def log_message(self, format, *args):
        pass  # suppress default logging


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", LISTEN_PORT), WebhookHandler)
    print(f"Webhook receiver listening on port {LISTEN_PORT}")
    print(f"Logs directory: {LOG_DIR}")
    server.serve_forever()
