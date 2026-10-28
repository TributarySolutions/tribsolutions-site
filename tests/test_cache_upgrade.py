"""Real Chrome cache-upgrade tests: no Playwright request routing is used.

Warm an actual browser cache with the old website, change the local server's
release, then navigate to newly fetched HTML using the same cached asset URLs.
No form is submitted. Server-side snapshots never contact Formspree.
"""
import importlib.util
import os
from pathlib import Path
import subprocess
from threading import Thread
import unittest

from playwright.sync_api import sync_playwright, expect
from test_contact import ROOT

spec = importlib.util.spec_from_file_location("cache_fixture", ROOT / "dev/reproduce_cache.py")
fixture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fixture)
version_spec = importlib.util.spec_from_file_location("asset_versions", ROOT / "dev/version_assets.py")
versions = importlib.util.module_from_spec(version_spec)
version_spec.loader.exec_module(versions)


class CacheUpgradeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = fixture.ThreadingHTTPServer(("127.0.0.1", 0), fixture.Handler)
        Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        cls.playwright = sync_playwright().start()
        candidates = [os.environ.get("BROWSER_EXECUTABLE", ""),
                      r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                      r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"]
        executable = next((p for p in candidates if p and Path(p).is_file()), None)
        cls.browser = cls.playwright.chromium.launch(headless=True, **({"executable_path": executable} if executable else {}))

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        fixture.hits.clear()
        fixture.state["ref"] = "6ad3d2c"
        self.contexts = []
        self.backend_requests = []

    def tearDown(self):
        for context in self.contexts:
            context.close()
        self.assertEqual(self.backend_requests, [])

    def page(self, width=1440, height=1000):
        context = self.browser.new_context(viewport={"width": width, "height": height}, reduced_motion="reduce")
        # Routing would disable the HTTP cache and invalidate this test.
        context.on("request", lambda request: self.backend_requests.append(request.url)
                   if request.url.startswith("https://formspree.io/") else None)
        self.contexts.append(context)
        return context.new_page()

    def ready(self, page):
        page.evaluate("document.fonts.ready")
        for image in page.locator("img").all():
            if image.get_attribute("loading") == "lazy":
                image.scroll_into_view_if_needed()
            image.evaluate("el => el.decode()")
        page.evaluate("window.scrollTo({top:0, behavior:'instant'})")

    def layout(self, page):
        self.ready(page)
        return page.evaluate("""() => ({
          headingFont: getComputedStyle(document.querySelector('h1')).fontSize,
          headingHeight: document.querySelector('h1').getBoundingClientRect().height,
          footerFont: getComputedStyle(document.querySelector('.site-footer p')).fontSize,
          pageWidth: document.documentElement.scrollWidth,
          samples: [...document.querySelectorAll('.service-card, .profile-picture, .profile-photo, .contact-card input, .contact-card textarea')].map(el => ({
            width: Math.round(el.getBoundingClientRect().width * 100) / 100,
            height: Math.round(el.getBoundingClientRect().height * 100) / 100,
            font: getComputedStyle(el).fontSize
          }))
        })""")

    def test_cache_fixture_reproduces_the_failed_release(self):
        page = self.page()
        page.goto(self.base + "/")
        self.ready(page)
        fixture.state["ref"] = "8b4279f"
        page.goto(self.base + "/index.html")
        self.ready(page)
        expect(page.locator("h1")).to_have_text("Modeling and decision support for complex river systems.")
        self.assertEqual(page.locator("h1").evaluate("el => getComputedStyle(el).fontSize"), "14.4px")
        self.assertEqual(page.locator(".profile-photo").evaluate_all("els => els.map(el => getComputedStyle(el).height)"), ["1356px", "2048px"])
        css_hits = [ref for ref, path in fixture.hits if path == "/assets/styles.css"]
        self.assertEqual(css_hits, ["6ad3d2c"], "The old CSS must really have come from HTTP cache")

    def test_cached_and_fresh_visitors_get_the_same_fixed_layout(self):
        for width in (1440, 1024, 768, 390, 360):
            with self.subTest(width=width):
                fixture.state["ref"] = "6ad3d2c"
                cached = self.page(width)
                cached.goto(self.base + "/")
                self.ready(cached)
                fixture.state["ref"] = "WORKTREE"
                cached.goto(self.base + "/index.html")
                warm_layout = self.layout(cached)
                fresh = self.page(width)
                fresh.goto(self.base + "/index.html")
                self.assertEqual(warm_layout, self.layout(fresh))
                self.assertLessEqual(warm_layout["pageWidth"], width)
                self.assertGreaterEqual(float(warm_layout["headingFont"].removesuffix("px")), 40)
                styles = cached.locator('link[rel="stylesheet"]').evaluate_all("els => els.map(el => el.getAttribute('href'))")
                self.assertIn(versions.snapshots()["assets/site.css"][0], styles)
                if width in (1440, 390):
                    cached.screenshot(path=str(fixture.OUTPUT / f"fixed-warm-cache-home-{width}.png"), full_page=True)
                # Also warm the failed contact release's unversioned CSS/JS before upgrading.
                fixture.state["ref"] = "8b4279f"
                contact = self.page(width)
                contact.goto(self.base + "/contact.html")
                self.ready(contact)
                fixture.state["ref"] = "WORKTREE"
                contact.goto(self.base + "/contact.html?upgrade=fixed")
                warm_contact = self.layout(contact)
                fresh.goto(self.base + "/contact.html?upgrade=fresh")
                self.assertEqual(warm_contact, self.layout(fresh))
                expect(contact.locator("#contact-form")).to_have_attribute("action", "https://formspree.io/f/mnppdeaj")
                expect(contact.locator("#submit-inquiry")).to_have_text("Send inquiry")
                if width in (1440, 390):
                    contact.screenshot(path=str(fixture.OUTPUT / f"fixed-warm-cache-contact-{width}.png"), full_page=True)

    def test_snapshots_are_current_and_original_styles_remain_compatible(self):
        versions.version_assets(check=True)
        original = subprocess.run(["git", "show", "6ad3d2c:assets/styles.css"], cwd=ROOT, check=True, capture_output=True).stdout
        self.assertEqual(versions.normalized(ROOT / "assets/styles.css"), original.replace(b"\r\n", b"\n"))


if __name__ == "__main__":
    unittest.main()
