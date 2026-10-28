# Tributary Solutions

Static HTML/CSS website hosted on GitHub Pages at
[www.tribsolutions.com](https://www.tribsolutions.com).

The repository's production branch is `main`; the original repository
instructions indicate that pushes to `main` deploy automatically. Treat a
merge/push to that branch as a production release.

## Contact form preview

Work is on `feature/contact-form-preview`. The custom form defaults to
**Demo/Test Mode**, with no endpoint configured. No build, package installation,
or account is needed for the demo. The existing Google contact form remains
available.

From PowerShell in this repository:

```powershell
python dev/preview.py
```

Open **http://127.0.0.1:8000/contact.html**. Enter sample information, choose a
simulated result, and select **Test inquiry**. Stop with **Ctrl+C**. If that port
is busy, run `python dev/preview.py --port 8001` and open the matching port.

The server binds only to this computer, serves only site files, and does not
receive inquiry submissions. A feature branch does **not** create a separate
GitHub Pages preview URL.

See [the review and handoff](docs/contact-form-handoff.md) for manual tests,
security review, Formspree/Zoho setup, deployment and rollback instructions.
**Do not merge, push, publish, or replace the Google Form without approval.**

## Files and design

| Path | Purpose |
| --- | --- |
| `index.html` | Existing homepage; both Google Form buttons unchanged |
| `contact.html` | Custom form and Google fallback |
| `assets/styles.css` | Existing shared styles, unchanged |
| `assets/contact.css` | Responsive form, focus and error styles |
| `assets/contact-config.js` | Public demo/live mode and Formspree endpoint |
| `assets/contact.js` | Validation, demo and submission handling |
| `assets/` | Existing logo, favicon, photos and placeholders |
| `CNAME` | Existing Pages custom domain, unchanged |
| `dev/preview.py` | Python standard-library HTTP preview |
| `tests/test_contact.py` | Headless browser regression checks |

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
They never send real messages. The existing Google Fonts hosts must be reachable
for the strict visual/console check. Screenshots go in ignored `test-results/`.
