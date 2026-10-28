"""Loopback-only preview; serves site files, never the repository or documentation."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit
from functools import lru_cache
import argparse
import mimetypes
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ORIGINAL_REF = "849d113"  # Completed contact-form project, before design refinements.


@lru_cache(maxsize=32)
def original_file(path):
    return subprocess.run(["git", "show", f"{ORIGINAL_REF}:{path}"], cwd=ROOT,
                          check=True, capture_output=True).stdout


class PreviewHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.serve_file()

    def do_HEAD(self):
        self.serve_file(head=True)

    def serve_file(self, head=False):
        path = unquote(urlsplit(self.path).path).lstrip("/") or "index.html"
        if path == "review/":
            self.send_file((ROOT / "dev/review.html").read_bytes(), "text/html", head)
            return
        original = path.startswith("original/")
        if original:
            path = path.removeprefix("original/") or "index.html"
        target = (ROOT / path).resolve()
        allowed = target in (ROOT / "index.html", ROOT / "contact.html") or (
            target.is_relative_to(ROOT / "assets")
            and target.suffix.lower() in {".css", ".js", ".jpg", ".png", ".svg", ".webp"}
        )
        if not allowed or not target.is_file():
            self.send_error(404)
            return
        try:
            data = original_file(target.relative_to(ROOT).as_posix()) if original else target.read_bytes()
        except subprocess.CalledProcessError:
            self.send_error(404)
            return
        self.send_file(data, mimetypes.guess_type(target)[0] or "application/octet-stream", head)

    def send_file(self, data, content_type, head):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        if not head:
            try:
                self.wfile.write(data)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass  # The browser navigated away while an asset was loading.


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    with ThreadingHTTPServer(("127.0.0.1", args.port), PreviewHandler) as server:
        print(f"Local preview: http://127.0.0.1:{args.port}/contact.html", flush=True)
        print(f"Before/after review: http://127.0.0.1:{args.port}/review/", flush=True)
        print("Press Ctrl+C to stop. This server does not accept form submissions.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
