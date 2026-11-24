# AGENTS.md

Public website for Tributary Solutions (www.tribsolutions.com): hand-written static HTML, CSS and JS. No framework, no package install, no build step.
GitHub Pages publishes the root of `main`, so **every push to `main` is a production release**. Work on a branch. Show the diff for review. Never commit to, merge into or push `main` without the owner's explicit approval.

Commands (PowerShell, from the repo root):
- Preview: `python dev/preview.py`, then open http://localhost:8000/ (Ctrl+C to stop). Do not submit the contact form in `live` mode: it sends a real inquiry.
- After editing `assets/site.css`, `contact.css`, `contact.js` or `contact-config.js`: `python dev/version_assets.py`
- Checks: `python dev/version_assets.py --check` and `python -m unittest discover -s tests -v` (needs Playwright)
- New page: copy the structure of an existing page, add it to `PAGES` in `dev/version_assets.py`, and add its link to the nav in every page.

Do not change without the owner's approval:
- `CNAME`, `_config.yml` (keeps internal files off the website), and the DNS and mail settings
- `assets/styles.css` and any published `*.<hash>.css/js` file: never edit, delete or overwrite them
- The original JPG photos in `assets/`
- The Formspree mode (`live`) and endpoint in `assets/contact-config.js`, and the Google Form fallback in `contact.html`
- History on `main`: no reset or force-push. Roll back with `git revert`.

This repository and the site are public. Never add credentials, internal notes or personal contact details.
Company conventions and project notes: Tributary AI library, `Projects/Website/README.md` (not in this repo).
