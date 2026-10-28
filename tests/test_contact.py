"""Headless browser checks. Requires Python Playwright; no runtime site dependencies.

Run: python -m unittest discover -s tests -v
All Formspree requests are intercepted. No real messages are sent.
"""
import importlib.util
import json
import os
from pathlib import Path
import re
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.request import urlopen

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("preview", ROOT / "dev/preview.py")
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)


class ContactTests(unittest.TestCase):
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

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()
        cls.server.shutdown()
        cls.server.server_close()

    def setUp(self):
        self.context = self.browser.new_context(viewport={"width": 1440, "height": 1000})
        # Never contact the real backend, even if someone later changes public config.
        self.context.route("https://formspree.io/**", lambda route: route.abort())
        self.page = self.context.new_page()
        # Exercise simulations explicitly even when the saved configuration is live.
        self.configure(mode="demo", endpoint="https://formspree.io/f/mnppdeaj")
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))

    def tearDown(self):
        self.assertEqual(self.errors, [], "Unexpected JavaScript exception")
        self.context.close()

    def open(self):
        self.page.goto(self.base + "/contact.html")
        expect(self.page.locator("#submit-inquiry")).to_be_enabled()

    def fill(self, organization="Example Water District"):
        self.page.get_by_label("Full name", exact=False).fill("Taylor Example")
        self.page.get_by_label("Email address", exact=False).fill("taylor@example.com")
        self.page.get_by_label("Organization/company", exact=False).fill(organization)
        self.page.get_by_label("Project description or inquiry", exact=False).fill("Sample inquiry about reservoir modeling.")

    def configure(self, mode="live", endpoint="https://formspree.io/f/testonly"):
        config = json.dumps({"mode": mode, "endpoint": endpoint})
        self.page.route("**/assets/contact-config*.js", lambda route: route.fulfill(
            content_type="application/javascript", body="window.CONTACT_FORM_CONFIG=" + config))

    def mock(self, status=200, body=None, content_type="application/json"):
        self.posts = []

        def respond(route):
            self.posts.append(route.request)
            route.fulfill(status=status, content_type=content_type,
                          body=json.dumps({"ok": True} if body is None else body) if content_type == "application/json" else body)
        self.page.route("https://formspree.io/**", respond)

    def test_demo_success_failure_duplicate_and_reset(self):
        requests = []
        self.page.on("request", lambda request: requests.append(request))
        self.open()
        expect(self.page.get_by_text("Demo/Test Mode", exact=True)).to_be_visible()
        self.fill(organization="")  # optional company really is optional
        self.page.locator("#submit-inquiry").dblclick()
        expect(self.page.locator("#contact-fields")).to_have_attribute("aria-busy", "true")
        expect(self.page.locator("#form-status").locator("xpath=ancestor::*[@aria-busy='true']")).to_have_count(0)
        expect(self.page.locator("#submit-inquiry")).to_be_disabled()
        expect(self.page.locator("#form-status")).to_contain_text("Demo successful")
        self.page.locator("#contact-form").dispatch_event("submit")
        expect(self.page.locator("#form-status")).to_contain_text("Demo successful")
        expect(self.page.locator("#submit-inquiry")).to_be_disabled()
        self.page.get_by_role("button", name="Start a new inquiry").click()
        expect(self.page.locator("#full-name")).to_have_value("")
        expect(self.page.locator("#full-name")).to_be_focused()
        self.fill()
        self.page.locator("#demo-outcome").select_option("failure")
        self.page.locator("#submit-inquiry").click()
        expect(self.page.locator("#form-status")).to_contain_text("Demo failure simulated")
        expect(self.page.locator("#email")).to_have_value("taylor@example.com")
        expect(self.page.locator("#submit-inquiry")).to_be_enabled()
        self.page.locator("#demo-outcome").select_option("success")
        self.page.locator("#submit-inquiry").click()
        expect(self.page.locator("#form-status")).to_contain_text("Demo successful")
        self.assertFalse([r for r in requests if r.method != "GET"], "Demo must never send a request containing form data")
        self.assertEqual(self.page.evaluate("Object.keys(localStorage).length + Object.keys(sessionStorage).length"), 0)

    def test_saved_formspree_configuration_with_intercepted_submission(self):
        # Load the real public configuration, but intercept the entire backend call.
        self.page.unroute("**/assets/contact-config*.js")
        self.mock(body={"next": "https://formspree.io/thanks"})
        self.open()
        expect(self.page.locator("#contact-form")).to_have_attribute("action", "https://formspree.io/f/mnppdeaj")
        expect(self.page.locator("#demo-panel")).to_be_hidden()
        expect(self.page.locator("#submit-inquiry")).to_have_text("Send inquiry")
        self.fill()
        self.page.locator("#submit-inquiry").click()
        expect(self.page.locator("#form-status")).to_contain_text("Your inquiry has been submitted")
        self.assertEqual(len(self.posts), 1)
        self.assertEqual(self.posts[0].url, "https://formspree.io/f/mnppdeaj")

    def test_required_whitespace_email_and_error_recovery(self):
        self.open()
        self.page.locator("#submit-inquiry").click()
        expect(self.page.locator("[aria-invalid=true]")).to_have_count(3)
        expect(self.page.locator("#full-name")).to_be_focused()
        self.fill()
        self.page.locator("#full-name").fill("   ")
        self.page.locator("#message").fill("   ")
        self.page.locator("#email").fill("invalid-address")
        self.page.locator("#submit-inquiry").click()
        expect(self.page.locator("#email-error")).to_contain_text("valid email address")
        expect(self.page.locator("[aria-invalid=true]")).to_have_count(3)
        self.fill()
        expect(self.page.locator("[aria-invalid=true]")).to_have_count(0)
        self.page.locator("#submit-inquiry").click()
        expect(self.page.locator("#form-status")).to_contain_text("Demo successful")

    def test_input_limits_and_maximum_valid_message(self):
        self.open()
        self.fill()
        for selector, limit in [("#full-name", 100), ("#email", 254), ("#organization", 150), ("#message", 5000)]:
            field = self.page.locator(selector)
            self.assertEqual(field.get_attribute("maxlength"), str(limit))
            # Simulate tampering/programmatic values, which bypass native typing caps.
            field.evaluate("(el, n) => el.value = 'x'.repeat(n + 1)", limit)
            self.page.locator("#submit-inquiry").click()
            expect(field).to_have_attribute("aria-invalid", "true")
            self.fill()
        self.page.locator("#message").fill("x" * 5000)
        self.page.locator("#submit-inquiry").click()
        expect(self.page.locator("#form-status")).to_contain_text("Demo successful")

    def test_live_payload_and_duplicate_suppression_with_mock_backend(self):
        self.configure()
        self.mock()
        self.open()
        expect(self.page.locator("#demo-panel")).to_be_hidden()
        self.fill()
        self.page.locator("#submit-inquiry").dblclick()
        expect(self.page.locator("#form-status")).to_contain_text("Your inquiry has been submitted")
        self.page.locator("#contact-form").dispatch_event("submit")
        self.assertEqual(len(self.posts), 1)
        payload = self.posts[0].post_data_buffer.decode()
        for value in ['name="name"', 'name="email"', 'name="organization"', 'name="message"', 'name="_gotcha"', "taylor@example.com"]:
            self.assertIn(value, payload)
        self.assertEqual(self.posts[0].headers["accept"], "application/json")
        self.assertNotIn("cookie", self.posts[0].headers)
        self.assertEqual(self.posts[0].headers["referer"], self.base + "/")

    def test_live_rejections_and_unconfirmed_responses_preserve_entries(self):
        for code, body, kind, expected in [
            (422, {"errors": [{"message": "<script>unsafe</script>"}]}, "application/json", "could not be submitted"),
            (429, {}, "application/json", "Too many attempts"),
            (500, {}, "application/json", "could not be submitted"),
            (200, "<html>CAPTCHA</html>", "text/html", "couldn’t confirm"),
            (200, {"ok": False}, "application/json", "couldn’t confirm"),
            (200, {"next": 123}, "application/json", "couldn’t confirm"),
            (200, {"ok": False, "next": "/thanks"}, "application/json", "couldn’t confirm"),
            (200, {"error": "Rejected", "next": "/thanks"}, "application/json", "couldn’t confirm"),
            (200, [], "application/json", "couldn’t confirm"),
        ]:
            with self.subTest(status=code, body=body):
                self.configure()
                self.mock(code, body, kind)
                self.open()
                self.fill()
                self.page.locator("#submit-inquiry").click()
                expect(self.page.locator("#form-status")).to_contain_text(expected)
                expect(self.page.locator("#email")).to_have_value("taylor@example.com")
                expect(self.page.locator("#submit-inquiry")).to_be_enabled()
                self.assertEqual(len(self.posts), 1)

    def test_network_failure(self):
        self.configure()
        self.open()
        self.fill()
        self.page.locator("#submit-inquiry").click()
        expect(self.page.locator("#form-status")).to_contain_text("couldn’t confirm")
        expect(self.page.locator("#message")).not_to_have_value("")
        expect(self.page.locator("#submit-inquiry")).to_be_enabled()

    def test_timeout_does_not_retry(self):
        self.configure()
        self.page.add_init_script("const original = window.setTimeout; window.setTimeout = (fn, ms, ...args) => original(fn, ms === 15000 ? 80 : ms, ...args);")
        attempts = []
        self.page.route("https://formspree.io/**", lambda route: attempts.append(route))
        self.open()
        self.fill()
        self.page.locator("#submit-inquiry").click()
        expect(self.page.locator("#form-status")).to_contain_text("couldn’t confirm")
        self.assertEqual(len(attempts), 1)
        attempts[0].abort()

    def test_blank_endpoint_is_always_demo_and_invalid_endpoint_fails_closed(self):
        self.configure(mode="live", endpoint="")
        self.open()
        expect(self.page.locator("#demo-panel")).to_be_visible()
        self.configure(endpoint="https://other.example/collect")
        self.page.reload()
        expect(self.page.locator("#submit-inquiry")).to_be_disabled()
        expect(self.page.locator("#form-status")).to_contain_text("unavailable")

    def test_missing_config_and_missing_javascript_fail_closed(self):
        self.page.route("**/assets/contact-config*.js", lambda route: route.fulfill(content_type="application/javascript", body=""))
        self.page.goto(self.base + "/contact.html")
        expect(self.page.locator("#submit-inquiry")).to_be_disabled()
        expect(self.page.locator("#form-status")).to_contain_text("unavailable")
        nojs = self.browser.new_context(java_script_enabled=False)
        page = nojs.new_page()
        page.goto(self.base + "/contact.html")
        expect(page.locator("#submit-inquiry")).to_be_disabled()
        expect(page.locator("noscript .form-notice")).to_be_visible()
        expect(page.get_by_role("link", name="Open the Google inquiry form")).to_be_visible()
        nojs.close()

    def test_keyboard_labels_focus_and_honeypot(self):
        self.open()
        self.page.keyboard.press("Tab")
        expect(self.page.get_by_role("link", name="Skip to inquiry form")).to_be_focused()
        self.page.keyboard.press("Enter")
        self.page.keyboard.press("Tab")
        expect(self.page.locator("#full-name")).to_be_focused()
        self.page.keyboard.press("Tab")
        expect(self.page.locator("#email")).to_be_focused()
        self.page.keyboard.press("Tab")
        expect(self.page.locator("#organization")).to_be_focused()
        self.page.keyboard.press("Tab")
        expect(self.page.locator("#message")).to_be_focused()
        self.page.keyboard.press("Tab")
        expect(self.page.locator("#submit-inquiry")).to_be_focused()
        style = self.page.locator("#submit-inquiry").evaluate("el => [getComputedStyle(el).outlineStyle, getComputedStyle(el).outlineWidth]")
        self.assertEqual(style, ["solid", "3px"])
        expect(self.page.locator("#website")).to_be_hidden()
        self.assertIn("Project description", self.page.locator("#contact-form").aria_snapshot())

    def test_responsive_layout_screenshots_and_console(self):
        console_errors = []
        failed_local = []
        self.page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
        self.page.on("response", lambda response: failed_local.append(response.url) if response.url.startswith(self.base) and response.status >= 400 else None)
        self.open()
        destination = ROOT / "test-results"
        destination.mkdir(exist_ok=True)

        def screenshot(filename):
            # Reset scroll so full-page captures place the sticky header at the top.
            self.page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
            self.page.screenshot(path=str(destination / filename), full_page=True)

        for width, height in [(1440, 1000), (768, 1024), (390, 844), (320, 800)]:
            self.page.set_viewport_size({"width": width, "height": height})
            self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"Horizontal overflow at {width}px")
            screenshot(f"contact-{width}.png")
        # Stress reflow: a 640 CSS pixel viewport at 200% zoom is 320 CSS pixels.
        self.assertEqual(failed_local, [])
        self.assertEqual(console_errors, [], "Check external font access if this environment is offline")
        self.fill()
        self.page.locator("#submit-inquiry").click()
        expect(self.page.locator("#form-status")).to_contain_text("Demo successful")
        screenshot("contact-success.png")
        self.page.locator("#new-inquiry").click()
        self.page.locator("#submit-inquiry").click()
        screenshot("contact-validation.png")
        self.fill()
        self.page.locator("#demo-outcome").select_option("failure")
        self.page.locator("#submit-inquiry").click()
        expect(self.page.locator("#form-status")).to_contain_text("Demo failure simulated")
        screenshot("contact-failure.png")

    def test_existing_navigation_assets_and_preview_access(self):
        self.open()
        self.page.get_by_role("link", name="Services", exact=True).click()
        self.assertTrue(self.page.url.endswith("index.html#services"))
        expect(self.page.locator("#services")).to_be_visible()
        self.page.get_by_role("link", name="Principals", exact=True).click()
        self.assertTrue(self.page.url.endswith("index.html#principals"))
        self.page.get_by_role("link", name="Contact", exact=True).click()
        expect(self.page.locator("#contact-form")).to_be_visible()
        self.assertEqual(self.page.get_by_role("link", name="Open the Google inquiry form").get_attribute("href"), "https://forms.gle/G4qvmoi2aAMYwonu9")
        for filename in ["index.html", "contact.html"]:
            content = (ROOT / filename).read_text(encoding="utf-8")
            for link in re.findall(r'(?:src|href)="([^"]+)"', content):
                if link.startswith(("http", "#")):
                    continue
                with urlopen(self.base + "/" + link.split("#")[0]) as response:
                    self.assertEqual(response.status, 200)
        for path in [".git/config", "README.md", "dev/preview.py", "assets/../.git/config", "assets/%2e%2e/.git/config"]:
            with self.assertRaises(HTTPError) as result:
                urlopen(self.base + "/" + path)
            self.assertEqual(result.exception.code, 404)
            result.exception.close()


if __name__ == "__main__":
    unittest.main()
