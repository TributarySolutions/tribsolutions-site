"""Design regression checks and matching before/after screenshots.

Original means the completed contact-form commit 849d113, not an old live
Google-form contact page. All form submission requests remain blocked.
"""
import os
from pathlib import Path
import subprocess
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

from playwright.sync_api import sync_playwright, expect
from test_contact import preview, ROOT

WIDTHS = (1440, 1024, 768, 390, 360)
OUTPUT = ROOT / "test-results/design"


class DesignTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        class QuietHandler(preview.PreviewHandler):
            def log_message(self, format, *args):
                pass
        cls.server = preview.ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"
        cls.playwright = sync_playwright().start()
        candidates = [os.environ.get("BROWSER_EXECUTABLE", ""),
                      r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
                      r"C:\Program Files\Google\Chrome\Application\chrome.exe"]
        executable = next((p for p in candidates if p and Path(p).is_file()), None)
        cls.browser = cls.playwright.chromium.launch(headless=True, **({"executable_path": executable} if executable else {}))
        OUTPUT.mkdir(parents=True, exist_ok=True)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1440, "height": 1000}, reduced_motion="reduce")
        self.context.route("https://formspree.io/**", lambda route: route.abort())
        self.page = self.context.new_page()
        # Design comparisons keep the preserved demo UI; real delivery is not tested.
        self.page.route("**/assets/contact-config*.js", lambda route: route.fulfill(
            content_type="application/javascript",
            body='window.CONTACT_FORM_CONFIG={mode:"demo",endpoint:"https://formspree.io/f/mnppdeaj"};'))
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.on("console", lambda message: self.errors.append(message.text) if message.type == "error" else None)

    def tearDown(self):
        self.assertEqual(self.errors, [], "No browser or console errors expected")
        self.context.close()

    def ready(self):
        self.page.evaluate("document.fonts.ready")
        for image in self.page.locator("img").all():
            if image.get_attribute("loading") == "lazy":
                image.scroll_into_view_if_needed()
            image.evaluate("el => el.decode()")
        self.page.evaluate("window.scrollTo({top:0, behavior:'instant'})")

    def test_responsive_comparisons_and_images(self):
        for width in WIDTHS:
            height = 1000 if width >= 1024 else 1024 if width == 768 else 844
            self.page.set_viewport_size({"width": width, "height": height})
            for page_name in ("index", "contact"):
                for version in ("original", "refined"):
                    if version == "original" and width not in (1440, 390):
                        continue
                    prefix = "/original/" if version == "original" else "/"
                    self.page.goto(f"{self.base}{prefix}{page_name}.html")
                    self.ready()
                    self.page.screenshot(path=str(OUTPUT / f"{version}-{page_name}-{width}.png"), full_page=True)
                    if page_name == "index" and width == 1440:
                        self.page.screenshot(path=str(OUTPUT / f"{version}-hero-1440.png"))
                    if version == "original":
                        continue
                    self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"Overflow: {page_name}, {width}")
                    for link in self.page.locator(".site-nav a, .btn").all():
                        if link.is_visible():
                            self.assertGreaterEqual(link.bounding_box()["height"], 44)
                    if page_name == "index":
                        expect(self.page.locator(".service-card")).to_have_count(6)
                        cards = [card.bounding_box() for card in self.page.locator(".service-card").all()]
                        for card in cards:
                            row = [other for other in cards if abs(other["y"] - card["y"]) < 2]
                            self.assertLess(max(other["height"] for other in row) - min(other["height"] for other in row), 1)
                        portraits = [p.bounding_box() for p in self.page.locator(".profile-picture").all()]
                        self.assertLess(abs(portraits[0]["width"] - portraits[1]["width"]), 2)
                        self.assertLess(abs(portraits[0]["height"] - portraits[1]["height"]), 2)
                        if width <= 560:
                            self.assertLess(cards[0]["y"], cards[1]["y"])
                        if width > 800:
                            expect(self.page.locator(".hero-logo-box")).to_be_visible()
                    else:
                        expect(self.page.get_by_text("Demo/Test Mode", exact=True)).to_be_visible()
                        for field in self.page.locator("#contact-fields input:not(#website), textarea").all():
                            box = field.bounding_box()
                            self.assertGreaterEqual(box["x"], 0)
                            self.assertLessEqual(box["x"] + box["width"], width)

    def test_content_and_contact_logic_preserved(self):
        for page_name, selectors in [
            ("index", [".hero-text", ".service-grid", ".principal-grid", ".hank-card", ".cta-section", ".site-footer"]),
            ("contact", ["#contact-form", "#demo-panel", ".contact-fallback", ".site-footer"]),
        ]:
            self.page.goto(f"{self.base}/original/{page_name}.html")
            if page_name == "contact":
                expect(self.page.locator("#submit-inquiry")).to_be_enabled()
            original = [" ".join(self.page.locator(s).inner_text().split()) for s in selectors]
            self.page.goto(f"{self.base}/{page_name}.html")
            if page_name == "contact":
                expect(self.page.locator("#submit-inquiry")).to_be_enabled()
            current = [" ".join(self.page.locator(s).inner_text().split()) for s in selectors]
            self.assertEqual(original, current)
        for file in ("CNAME", "assets/logo.png",
                     "assets/jordan.jpg", "assets/marlena.jpg", "assets/hank.jpg", "assets/banner_photo.jpg"):
            original = subprocess.run(["git", "show", f"849d113:{file}"], cwd=ROOT, check=True, capture_output=True).stdout
            self.assertEqual((ROOT / file).read_bytes().replace(b"\r\n", b"\n") if file.endswith((".js", "CNAME")) else (ROOT / file).read_bytes(),
                             original.replace(b"\r\n", b"\n") if file.endswith((".js", "CNAME")) else original, file)

    def test_headings_keyboard_navigation_and_anchor_clearance(self):
        self.page.goto(self.base + "/index.html")
        expect(self.page.locator("h1")).to_have_count(1)
        expect(self.page.locator("h1")).to_have_text("Modeling and decision support for complex river systems.")
        levels = self.page.locator("h1,h2,h3").evaluate_all("els => els.map(el => Number(el.tagName[1]))")
        self.assertTrue(all(b <= a + 1 for a, b in zip(levels, levels[1:])))
        self.page.keyboard.press("Tab")
        expect(self.page.get_by_role("link", name="Skip to main content")).to_be_focused()
        self.page.keyboard.press("Enter")
        expect(self.page.locator("#main-content")).to_be_focused()
        for width in WIDTHS:
            self.page.set_viewport_size({"width": width, "height": 900})
            for label, target in [("Services", "#services"), ("Principals", "#principals")]:
                self.page.get_by_role("navigation").get_by_role("link", name=label, exact=True).click()
                top = self.page.locator(target).bounding_box()["y"]
                bottom = self.page.locator(".site-header").bounding_box()["height"]
                self.assertGreaterEqual(top + 1, bottom, f"Anchor hidden at {width}px")
        self.page.get_by_role("navigation").get_by_role("link", name="Contact", exact=True).click()
        expect(self.page.locator(".site-nav a[aria-current='page']")).to_have_text("Contact")
        self.assertEqual(self.page.locator(".site-nav a").all_text_contents(), ["Services", "Principals", "Contact"])
        self.page.get_by_role("link", name="Tributary Solutions home").click()
        expect(self.page.locator("h1")).to_have_text("Modeling and decision support for complex river systems.")

    def test_image_delivery_and_local_comparison_routes(self):
        self.page.goto(self.base + "/index.html")
        self.ready()
        for image in self.page.locator(".profile-photo, .hank-photo").all():
            self.assertTrue(image.evaluate("el => el.currentSrc.endsWith('.webp')"))
            self.assertEqual(image.get_attribute("loading"), "lazy")
        background = self.page.locator(".hero").evaluate("el => getComputedStyle(el).backgroundImage")
        self.assertIn("banner-1920.webp", background)
        self.page.set_viewport_size({"width": 390, "height": 844})
        self.assertIn("banner-960.webp", self.page.locator(".hero").evaluate("el => getComputedStyle(el).backgroundImage"))
        for url in ("/original/index.html", "/original/contact.html", "/original/assets/styles.css", "/review/", "/assets/banner-1920.webp"):
            with urlopen(self.base + url) as response:
                self.assertEqual(response.status, 200)
        with urlopen(self.base + "/original/assets/styles.css") as response:
            self.assertEqual(response.read(), subprocess.run(["git", "show", "849d113:assets/styles.css"], cwd=ROOT, check=True, capture_output=True).stdout)
        for url in ("/original/.git/config", "/original/assets/../../.git/config", "/original/dev/preview.py", "/dev/review.html"):
            with self.assertRaises(HTTPError) as result:
                urlopen(self.base + url)
            self.assertEqual(result.exception.code, 404)
            result.exception.close()


if __name__ == "__main__":
    unittest.main()
