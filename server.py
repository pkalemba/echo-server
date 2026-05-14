#!/usr/bin/env python3
import json
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

PORT = 3001


class EchoHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress default handler logging

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length) if length else b""

    def _log_request(self, body: bytes):
        logger.info(
            "method=%s path=%s headers=%s body=%s",
            self.command,
            self.path,
            dict(self.headers),
            body.decode("utf-8", errors="replace") if body else "",
        )

    def do_GET(self):
        self._log_request(b"")
        if self.path == "/healthz":
            self._respond(200, {"status": "alive"})
        elif self.path == "/ready":
            self._respond(200, {"status": "ready"})
        else:
            self._respond(200, {"method": "GET", "path": self.path, "headers": dict(self.headers)})

    def do_POST(self):
        body = self._read_body()
        self._log_request(body)
        try:
            parsed = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            parsed = body.decode("utf-8", errors="replace")
        self._respond(200, {"method": "POST", "path": self.path, "headers": dict(self.headers), "body": parsed})

    def do_PUT(self):
        body = self._read_body()
        self._log_request(body)
        try:
            parsed = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            parsed = body.decode("utf-8", errors="replace")
        self._respond(200, {"method": "PUT", "path": self.path, "headers": dict(self.headers), "body": parsed})

    def do_DELETE(self):
        self._log_request(b"")
        self._respond(200, {"method": "DELETE", "path": self.path, "headers": dict(self.headers)})

    def do_PATCH(self):
        body = self._read_body()
        self._log_request(body)
        try:
            parsed = json.loads(body)
        except (json.JSONDecodeError, UnicodeDecodeError):
            parsed = body.decode("utf-8", errors="replace")
        self._respond(200, {"method": "PATCH", "path": self.path, "headers": dict(self.headers), "body": parsed})

    def _respond(self, status: int, payload: dict):
        body = json.dumps(payload, indent=2).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), EchoHandler)
    logger.info("Echo server started")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Echo server stopped")
