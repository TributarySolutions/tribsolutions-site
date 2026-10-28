"""Reproduce the released HTML/stylesheet mismatch using real Chrome caching.

No routing/interception is used: Playwright routing disables HTTP caching.
No submissions are made. All site files come from local Git snapshots.
"""
from collections import Counter
from functools import lru_cache
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json
import mimetypes
import subprocess
from threading import Thread
from urllib.parse import unquote, urlsplit

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "test-results/cache-investigation"
OUTPUT.mkdir(parents=True, exist_ok=True)
state = {"ref": "6ad3d2c"}
hits = []


@lru_cache(maxsize=64)
def blob(ref, path):
    return subprocess.run(["git", "show", f"{ref}:{path}"], cwd=ROOT,
                          capture_output=True, check=True).stdout


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = unquote(urlsplit(self.path).path).lstrip("/") or "index.html"
        if path not in ("index.html", "contact.html") and not (
            path.startswith("assets/") and ".." not in path and "\\" not in path
        ):
            self.send_error(404)
            return
        try:
            data = (ROOT / path).read_bytes() if state["ref"] == "WORKTREE" else blob(state["ref"], path)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.send_error(404)
            return
        hits.append((state["ref"], self.path))
        self.send_response(200)
        self.send_header("Content-Type", mimetypes.guess_type(path)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "max-age=600")
        self.end_headers()
        try:
            self.wfile.write(data)
        except ConnectionError:
            pass

    def log_message(self, *args):
        pass


def observe(page, label):
    page.evaluate("document.fonts.ready")
    for image in page.locator(".profile-photo").all():
        image.scroll_into_view_if_needed()
        image.evaluate("el => el.decode()")
    metrics = page.evaluate("""() => ({
      headingText: document.querySelector('.hero-text h1').textContent,
      headingFont: getComputedStyle(document.querySelector('.hero-text h1')).fontSize,
      portraits: [...document.querySelectorAll('.profile-photo')].map(img => ({
        cssWidth: getComputedStyle(img).width,
        cssHeight: getComputedStyle(img).height,
        renderedWidth: img.getBoundingClientRect().width,
        renderedHeight: img.getBoundingClientRect().height,
        fit: getComputedStyle(img).objectFit,
        parentWidth: img.parentElement.getBoundingClientRect().width,
        parentHeight: img.parentElement.getBoundingClientRect().height
      })),
      horizontalOverflow: document.documentElement.scrollWidth > innerWidth
    })""")
    page.evaluate("window.scrollTo({top:0, behavior:'instant'})")
    page.screenshot(path=str(OUTPUT / f"{label}-hero.png"))
    page.locator(".principal-grid").screenshot(path=str(OUTPUT / f"{label}-portraits.png"))
    print(label, json.dumps(metrics), flush=True)
    return metrics


if __name__ == "__main__":
    with ThreadingHTTPServer(("127.0.0.1", 0), Handler) as server:
        Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_port}"
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
            print("Chrome version:", browser.version, flush=True)
            context = browser.new_context(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
            page = context.new_page()
            page.goto(base + "/")
            original = observe(page, "original")
            state["ref"] = "8b4279f"
            page.goto(base + "/index.html")  # New HTML URL; cached shared CSS URL.
            mixed = observe(page, "warm-cache-release")
            print("Stylesheet requests after upgrade:", Counter(ref for ref, path in hits if path == "/assets/styles.css"), flush=True)
            fresh = browser.new_context(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
            fresh_page = fresh.new_page()
            fresh_page.goto(base + "/index.html")
            clean = observe(fresh_page, "fresh-release")
            (OUTPUT / "metrics.json").write_text(json.dumps({"chrome": browser.version, "original": original,
                "warm_cache": mixed, "fresh_release": clean, "server_hits": hits}, indent=2), encoding="utf-8")
            browser.close()
        server.shutdown()
