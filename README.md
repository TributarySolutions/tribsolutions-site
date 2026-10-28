# Tributary Solutions

Static HTML/CSS website hosted on GitHub Pages at
[www.tribsolutions.com](https://www.tribsolutions.com).

The repository's production branch is `main`; the original repository
instructions indicate that pushes to `main` deploy automatically. Treat a
merge/push to that branch as a production release.

## Design refinement preview

Current work is on `feature/design-refinements`, based on the completed
contact-form commit `849d113`. Production and the contact-form branch are
unchanged. Run `python dev/preview.py`, then open
**http://127.0.0.1:8000/review/** to switch between original and refined pages.
The comparison uses the same browser viewport; the original contact page is
the custom form from the previous project, not the live Google-link page.

The refined pages are `/index.html` and `/contact.html`; the original pages are
`/original/index.html` and `/original/contact.html`. The review route exists only
in the local development server. Stop it with Ctrl+C.

See [the design handoff](docs/design-refinements-handoff.md) for the design
decisions, screenshots, complete changed-file list and verification results.
Screenshots for all requested widths are in ignored `test-results/design/`.

## Contact form preview

The custom form was introduced on `feature/contact-form-preview`. The current
unpublished version now uses the owner-provided Formspree endpoint
`https://formspree.io/f/mnppdeaj` with `mode: "live"`. Submitting the local form
will send a real inquiry to Formspree. The owner confirmed receipt of a real
local-preview test in Jordan's inbox on October 27, 2026. Delivery to Marlena
and the production dashboard settings still need confirmation. The existing Google
contact form remains available.

From PowerShell in this repository:

```powershell
python dev/preview.py
```

Open **http://localhost:8000/contact.html**. It now shows **Send inquiry**.
For simulations, change `mode` to `"demo"` in `assets/contact-config.js` and
reload; choose a simulated result and select **Test inquiry**. Return to
`"live"` when ready for an authorized real delivery test. Stop with **Ctrl+C**. If that port
is busy, run `python dev/preview.py --port 8001` and open the matching port.

The server binds only to this computer, serves only site files, and does not
receive inquiry submissions. A feature branch does **not** create a separate
GitHub Pages preview URL.

See [the review and handoff](docs/contact-form-handoff.md) for manual tests,
security review, Formspree/Zoho setup, deployment and rollback instructions.
The latest [Formspree integration notes](docs/formspree-integration.md) record
the configured endpoint, current mode, testing and remaining dashboard work.
**Do not merge, push, publish, or replace the Google Form without approval.**

## Files and design

| Path | Purpose |
| --- | --- |
| `index.html` | Refined homepage; both Google Form destinations unchanged |
| `contact.html` | Custom form and Google fallback |
| `assets/styles.css` | Shared site styles, navigation and accessibility |
| `assets/contact.css` | Responsive form, focus and error styles |
| `assets/contact-config.js` | Public demo/live mode and Formspree endpoint |
| `assets/contact.js` | Validation, demo and submission handling |
| `assets/` | Existing logo, favicon, photos and placeholders |
| `CNAME` | Existing Pages custom domain, unchanged |
| `dev/preview.py` | Python standard-library HTTP preview |
| `dev/review.html` | Local-only before/after switching view |
| `dev/optimize_images.py` | Recreates WebP variants with development-only Pillow |
| `tests/test_contact.py` | Headless browser regression checks |
| `tests/test_design.py` | Design/content regression checks and matching screenshots |

Branding uses Montserrat, navy `#071330`, midnight blue `#0c4160`, blue-gray
`#738fa7`, and misty blue `#c3ceda`. Shared variables remain in
`assets/styles.css`. Photo crops use `.photo-jordan`, `.photo-marlena`, and
`.photo-hank` in that file.

## Automated checks

With Python Playwright available:

```powershell
python -m unittest discover -s tests -v
node --check assets/contact.js
node --check assets/contact-config.js
```

Playwright is a development-only tool, already installed here. The site has no
JavaScript package dependencies. On another machine, run
`python -m pip install playwright`. The tests use installed Edge/Chrome on
Windows; otherwise run `python -m playwright install chromium` or set
`BROWSER_EXECUTABLE` to an installed Chromium browser executable.

Tests start/stop their own loopback server and intercept all Formspree requests.
They explicitly select demo mode for simulations/design screenshots and separately
test the saved live configuration against a mocked endpoint. They never send real
messages. The existing Google Fonts hosts must be reachable
for the strict visual/console check. Screenshots go in ignored `test-results/`.

The original JPG photographs are preserved. Responsive WebP variants are
selected by the page and CSS; the portraits use JPG fallback sources and lazy
loading. To regenerate variants, use `python dev/optimize_images.py` with Pillow
installed. Pillow is not required to serve the site.
