"""Loopback-only preview; serves site files, never the repository or documentation."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
import argparse
import mimetypes

ROOT = Path(__file__).resolve().parents[1]


class PreviewHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.serve_file()

    def do_HEAD(self):
        self.serve_file(head=True)

    def serve_file(self, head=False):
        path = unquote(urlsplit(self.path).path).lstrip("/") or "index.html"
        target = (ROOT / path).resolve()
        allowed = target in (ROOT / "index.html", ROOT / "contact.html") or (
            target.is_relative_to(ROOT / "assets")
            and target.suffix.lower() in {".css", ".js", ".jpg", ".png", ".svg"}
        )
        if not allowed or not target.is_file():
            self.send_error(404)
            return
        data = target.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(target)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if not head:
            self.wfile.write(data)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", args.port), PreviewHandler) as server:
        print(f"Local preview: http://127.0.0.1:{args.port}/contact.html", flush=True)
        print("Press Ctrl+C to stop. This server does not accept form submissions.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
