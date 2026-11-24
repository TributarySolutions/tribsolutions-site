# Tributary Solutions

Static HTML/CSS website hosted on GitHub Pages at
[www.tribsolutions.com](https://www.tribsolutions.com).

The production branch is `main`. GitHub Pages publishes it automatically, so
**every merge or push to `main` is a production release**. Make changes on a
branch and merge them through a pull request only with the owner's approval.
AI tools: read [AGENTS.md](AGENTS.md) first.

## Current state

- **Live since October 28, 2026 (`e6b7e59`):** the refined design, responsive
  images, cache-safe versioned CSS/JS and the custom contact form. An earlier
  release, `8b4279f`, was rolled back by `3659651` after a browser-cache
  formatting failure; `e6b7e59` is the corrected complete release. See the
  [appearance investigation](docs/appearance-investigation.md).
- **Contact form:** posts to Formspree in `live` mode. The endpoint and mode
  are in `assets/contact-config.js`. Formspree accepts submissions only from
  `tribsolutions.com` and notifies the company inquiries address, which Zoho
  forwards to both principals. The owner confirmed on November 24, 2026 that
  a real inquiry from the live site was delivered. The homepage
  contact buttons open the custom form. The Google Form link stays on the
  contact page as the fallback the form's error messages point to; do not
  remove it without the owner's approval.
- **Internal files are not published:** `_config.yml` excludes `README.md`,
  `AGENTS.md`, `CLAUDE.md`, `docs/`, `dev/` and `tests/` from the website
  (released November 24, 2026). Add any new internal file or folder to its
  `exclude:` list. The repository itself remains public on GitHub.
- **`docs/`** holds the October 2026 handoff and investigation records. They
  describe the work as it stood before release; this README is the current
  summary.

## Local preview

From PowerShell in this repository:

```powershell
python dev/preview.py
```

Open **http://localhost:8000/**. Stop with **Ctrl+C**. If that port is busy,
run `python dev/preview.py --port 8001` and open the matching port. The server
binds only to this computer, serves only site files, and does not receive
inquiry submissions. It ignores `_config.yml`, so excluded files still appear
locally. A branch does **not** create a GitHub Pages preview URL.

**The local contact form is in `live` mode: submitting it sends a real
inquiry** (which the domain restriction may also filter as spam). For trials,
change `mode` to `"demo"` in `assets/contact-config.js`, reload, choose a
simulated result and select **Test inquiry**. Restore `"live"` before
committing.

**http://localhost:8000/review/** switches between the refined pages and the
pre-redesign originals (`/original/index.html` and `/original/contact.html`,
served from commit `849d113`). This route exists only on the local server. See
[the design handoff](docs/design-refinements-handoff.md) for the design
decisions.

## Releasing and rolling back

1. Work on a branch; run the [automated checks](#automated-checks) and
   preview locally.
2. Open a pull request to `main`. The owner reviews it, including a
   returning-visitor (cached browser) check for CSS/JS changes, and merges it.
3. Confirm Pages built the merge commit:
   `gh api repos/TributarySolutions/tribsolutions-site/pages/builds/latest --jq "{status, commit, created_at}"`.
   Then check the live pages.
4. To roll back, revert the release or merge commit (`git revert -m 1 <merge-sha>`
   for a merge) in a new pull request. Never reset or force-push `main`. Keep
   published hashed CSS/JS snapshots and their images so cached older pages
   still find matching files.

Preserve `CNAME`, `_config.yml`, and the DNS and mail settings. Form setup,
security review and the original manual tests are in
[the contact handoff](docs/contact-form-handoff.md) and the
[Formspree notes](docs/formspree-integration.md).

## Files and design

| Path | Purpose |
| --- | --- |
| `index.html` | Refined homepage; both contact buttons open the custom contact page |
| `contact.html` | Custom form and Google fallback |
| `assets/site.css` | Editable shared styles for the refined site |
| `assets/site.<hash>.css` | Immutable release snapshot referenced by the new pages |
| `assets/styles.css` | Original production CSS, preserved for cached original HTML |
| `assets/contact.css` | Responsive form, focus and error styles |
| `assets/contact-config.js` | Public demo/live mode and Formspree endpoint |
| `assets/contact.js` | Validation, demo and submission handling |
| `assets/` | Existing logo, favicon, photos and placeholders |
| `CNAME` | Pages custom domain |
| `_config.yml` | Jekyll `exclude:` list that keeps internal files off the website |
| `AGENTS.md`, `CLAUDE.md` | Instructions for AI tools (not published on the website) |
| `docs/` | October 2026 handoff and investigation records |
| `dev/preview.py` | Python standard-library HTTP preview |
| `dev/review.html` | Local-only before/after switching view |
| `dev/optimize_images.py` | Recreates WebP variants with development-only Pillow |
| `dev/version_assets.py` | Generates/checks content-versioned CSS/JS release snapshots |
| `dev/reproduce_cache.py` | Reproduces the failed release using a real Chrome cache |
| `tests/test_contact.py` | Headless browser regression checks |
| `tests/test_design.py` | Design/content regression checks and matching screenshots |
| `tests/test_cache_upgrade.py` | Returning-visitor cache upgrade tests in Chrome |

Branding uses Montserrat, navy `#071330`, midnight blue `#0c4160`, blue-gray
`#738fa7`, and misty blue `#c3ceda`. Shared variables remain in
`assets/site.css`. Photo crops use `.photo-jordan`, `.photo-marlena`, and
`.photo-hank` in that file.

After editing `assets/site.css`, `assets/contact.css`, `assets/contact.js`, or
`assets/contact-config.js`, run `python dev/version_assets.py`. It writes
content-hashed snapshots and updates page references. Edit the named source
files, not their generated snapshots. Keep previously published snapshots so
cached older HTML retains matching assets. Do not overwrite `assets/styles.css`
with the new design: cached original pages still reference that legacy URL.

## Automated checks

With Python Playwright available:

```powershell
python dev/version_assets.py --check
python -m unittest discover -s tests -v
node --check assets/contact.js
node --check assets/contact-config.js
```

Playwright is a development-only tool, already installed here. The site has no
JavaScript package dependencies. On another machine, run
`python -m pip install playwright`. The tests use installed Edge/Chrome on
Windows; otherwise run `python -m playwright install chromium` or set
`BROWSER_EXECUTABLE` to an installed Chromium browser executable.

Tests start/stop their own loopback server. Form-submission tests intercept all
Formspree requests. Cache-upgrade tests use real Chrome HTTP caching without
request routing and never submit the form. Other tests explicitly select demo
mode for simulations/design screenshots and separately
test the saved live configuration against a mocked endpoint. They never send real
messages. The existing Google Fonts hosts must be reachable
for the strict visual/console check. Screenshots go in ignored `test-results/`.

The original JPG photographs are preserved. Responsive WebP variants are
selected by the page and CSS; the portraits use JPG fallback sources and lazy
loading. To regenerate variants, use `python dev/optimize_images.py` with Pillow
installed. Pillow is not required to serve the site.
