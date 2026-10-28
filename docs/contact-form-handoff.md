# Contact form review and handoff

Reviewed and tested October 27, 2026 (America/Denver).

## Current state

Work is on `feature/contact-form-preview`. Production `main` and the locally
recorded `origin/main` remain at
`6ad3d2cc0f77dae200e45257d41a0b7127a0f1ee`. No merge, push, deployment,
registration, purchase, real email transmission, or DNS change was performed.
The configuration is demo mode with an empty endpoint. **Real Formspree delivery
and receipt in Zoho Mail have not been verified.**

## Website review

The site has two HTML pages, one shared stylesheet, local images and `CNAME`
(`www.tribsolutions.com`). There was no JavaScript, build system, test suite,
or tracked GitHub Actions workflow. The original README describes automatic
Pages deployment from main; account-side Pages settings were not available
for independent inspection.

HTTPS requests to the live homepage, contact page and shared CSS returned 200,
and their normalized contents exactly matched the original main files. The
bare domain redirects to www. This was a read-only comparison.

The homepage hero and bottom CTA link directly to
`https://forms.gle/G4qvmoi2aAMYwonu9`. Navigation links to `contact.html`, whose
original button opens that same Google Form. The three live links are unchanged.
The feature contact page retains the Google Form as a fallback; the homepage
and shared stylesheet are unchanged on this branch as well.

Branding uses Montserrat from Google Fonts, navy/midnight blue headings and
buttons, blue-gray accents, pale blue backgrounds, rounded buttons, a sticky
header and 1,200px wrapper. Original mobile breakpoints are 800, 560 and 480px.
Contact-only styles preserve these patterns and stack name/email below 600px.

The original contact experience has clear navigation and a simple button,
but visitors leave the site before seeing the fields or a privacy explanation.
There is no on-site validation, progress or confirmation. Focus styling was
limited to existing navigation/button rules. Google Form internals, account
settings and assistive-technology behavior were not audited. The original
README's placeholder/green-color instructions were stale and are now corrected.

The smallest implementation is HTML constraints, contact-only CSS, two small
scripts, and a managed Formspree endpoint. There is no runtime library,
framework, application server or mail server.

## Files changed

| File | Change |
| --- | --- |
| `contact.html` | Labeled form, inline errors, progress/status, privacy notice, demo controls, fallback, contact-page CSP |
| `assets/contact.css` | Responsive form and focus/error styles |
| `assets/contact-config.js` | Public mode and endpoint configuration, defaulting to demo |
| `assets/contact.js` | Validation, local simulation, fetch, timeout and duplicate protection |
| `dev/preview.py` | Loopback HTTP server with a site-file allowlist |
| `tests/test_contact.py` | Browser tests and screenshot generation |
| `.gitignore` | Python caches and local test output |
| `README.md` | Accurate preview, structure and check instructions |
| `docs/contact-form-handoff.md` | This handoff |

Homepage HTML, shared CSS, image assets and CNAME were not changed.

## Launch and test locally

Run in PowerShell:

```powershell
Set-Location -LiteralPath 'C:\Users\jordan\OneDrive - Tributary Solutions LLC\Tributary Solutions - Shared Documents\Admin\Website\tribsolutions-site'
git branch --show-current
python dev/preview.py
```

The branch should be `feature/contact-form-preview`. Open
**http://127.0.0.1:8000/contact.html**. If needed use
`python dev/preview.py --port 8001`. Stop with Ctrl+C. The preview was launched
and returned HTTP 200 during implementation. The embedded browser was
unavailable, so browser checks used installed Edge in headless mode. Preview
processes are stopped at handoff; the command above restarts it.

Use sample information: `Taylor Example`, `taylor@example.com`,
`Example Water District`, and `Sample inquiry about reservoir modeling.`

1. Confirm **Demo/Test Mode** is visible. Submit blank fields; errors identify
   required fields and focus moves to the first invalid input.
2. Enter an invalid email, then correct it. Organization is optional. Limits
   for name/email/organization/message are 100/254/150/5,000 characters.
   Whitespace-only required fields are rejected.
3. Choose **Successful submission** and **Test inquiry**. Progress appears,
   controls lock, and a demo success appears. Start a new inquiry to reset.
4. Choose **Failed submission**. The error preserves entries. Switch to
   success and retry. Neither demo result sends or externally stores data.
5. Double-click or press Enter repeatedly. Only one attempt runs; after
   success, a new inquiry must be started explicitly.
6. Tab/Shift+Tab through the page. Check the skip link, visible focus, field
   labels/errors and status. Disable JavaScript: the new form stays disabled
   and the Google fallback remains available.
7. Inspect desktop, tablet, phone widths and zoom; check Services, Principals,
   Home, the Google link and the browser console.

Form contents remain in the current browser page. The code does not log them
or write them to local/session storage. Browser autofill remains controlled
by the visitor's browser. Do not use confidential information.

## Formspree and real Zoho delivery test

The owner must supply a company-owned Formspree account and its public endpoint
ID. Set the intended company Zoho Mail recipient **inside Formspree**, not in
source. No password, private key, token or recipient email belongs in this repo.

1. Create a dedicated Formspree test project/form. In Account settings, link
   and verify the existing Zoho Mail address. In the form Workflow, set the
   Email action's recipient to that verified address. Complete activation
   and verification email in Zoho. Formspree sends; Zoho receives. No Google
   account is used for sending or receiving business mail.
2. Retain basic spam filtering and `_gotcha`. No CAPTCHA code is included.
   Choose a new test form's CAPTCHA policy compatible with this no-CAPTCHA
   AJAX integration. If its settings demand a challenge, it is not ready.
   Any future CAPTCHA must use Formspree's matching server verification.
3. In the **test project's** Settings, set **Restrict to Domain** to `localhost`
   if accepted, and use **http://localhost:8000/contact.html** for the real
   test. Do not loosen an existing production project's protection. If your
   account rejects localhost, stop and request an approved HTTPS staging
   origin. No remote staging is needed for demo mode; none was published.
4. On the feature branch, edit `assets/contact-config.js`: set `mode: "live"`
   and `endpoint: "https://formspree.io/f/FORM_ID"`, using the exact public
   endpoint on the form's Integration tab. Reload: demo controls disappear
   and the button reads **Send inquiry**.
5. Send **one** non-sensitive staging inquiry with a unique timestamp and
   a reply address you control. Confirm it appears in Formspree and is
   actually received in Zoho Inbox or Spam. Verify every field and Reply-To.
   Record the test time and receipt confirmation. A success banner is not
   proof of email delivery. Do not load-test the endpoint.
6. Check Formspree's spam inbox. Its honeypot silently ignores filled `_gotcha`
   submissions; domain filtering can also accept/filter silently. Test these
   with sample information and inspect the backend rather than trusting a
   client success message.
7. Restore `mode: "demo"` and `endpoint: ""` until a production release is
   approved. Avoid committing a test endpoint as production configuration.

Before production, configure a production project/endpoint and set **Restrict
to Domain** to **`tribsolutions.com`**, without protocol or www. Formspree
documents that this covers the apex and subdomains. Select the verified Zoho
recipient, check quota/retention, spam filtering and activation. Account-side
protections remain **pending**. The contact page preserves the origin referrer
with `strict-origin-when-cross-origin`; referrer-blocking extensions can still
cause legitimate submissions to be filtered.

## Security review

| Topic | Protection and limits |
| --- | --- |
| Processing | Demo is a local timer with no submission request. Live mode POSTs over HTTPS directly to Formspree; GitHub Pages does not process inquiries. |
| Data | Name, email, optional organization, message, `_gotcha`, and normal network metadata received by Formspree. No attachments or payment/password fields. |
| Storage | No application cookies, database, browser persistence or submission logs. Real messages are stored by Formspree and notification copies by Zoho. Set retention/deletion policies in both; archive limits depend on the Formspree plan. |
| Credentials | Public endpoint ID only. No private credentials or recipient address in source, no mail server, no DNS/SPF/DKIM/DMARC/MX changes. |
| Client protections | HTML5/inline required, email and length checks, whitespace rejection, disabled controls while pending, locked success state, no automatic retries, 15-second timeout, text-only status rendering, strict Formspree HTTPS endpoint allowlist. |
| Spam | Supported `_gotcha` is included. Basic Formspree filtering and rate limits apply once configured; no backend or CAPTCHA protection is claimed verified. Demo does not emulate backend filtering. |
| Account setup | Verify recipient/activation, retain filtering, configure domain restriction and compatible CAPTCHA policy, review quota/spam inbox, secure account access and retention. |
| Page policy | Meta CSP limits scripts to self, styles/fonts to the existing Google Fonts hosts, connections to self/Formspree, native form actions to Formspree, and disables objects/base tags. Header-only policies such as frame-ancestors are not supplied by this meta tag. |
| Preview | Binds to 127.0.0.1, serves allowlisted site files, blocks metadata/traversal and has no POST handler. |
| Residual risks | Client checks/locks can be bypassed. Public endpoints can be abused; referrer restrictions are not authentication. A timeout can occur after acceptance and manual retries can duplicate messages. Backend acceptance does not prove Zoho receipt. |

Existing Google Fonts and the Google fallback remain external services. No
analytics or third-party JavaScript was added. Review Formspree's privacy
terms before production use.

## Verification

All **12 browser tests passed** in installed Microsoft Edge (headless Chromium).
JavaScript syntax checks passed for both scripts. Every Formspree request in
tests is intercepted; no real messages are sent.

| Check | Result |
| --- | --- |
| Responsive layout | Screenshots at 1440, 768, 390 and 320 CSS pixels; no horizontal overflow; visually inspected |
| Validation | Required fields, whitespace, email, error recovery, optional company, oversized values and exact maximum message passed |
| Demo | Success/failure, preserved entries, reset, progress, no outbound POST or application browser storage passed |
| Duplicates | Double-click plus subsequent submit event yields one mocked POST; success remains locked |
| Backend errors | Mocked success, 422/429/500, non-JSON, unconfirmed JSON, network failure and timeout passed; no retry |
| Configuration | Blank endpoint forces demo; unsupported endpoint and missing config remain disabled |
| Accessibility | Labels, required attributes, error associations, first-invalid focus, Tab sequence, focus indicators, live status outside busy subtree, skip link, hidden honeypot and no-JS fallback passed |
| Regression | No normal-demo console errors with fonts reachable; linked local assets return 200; navigation passes; homepage/shared CSS/CNAME unchanged |
| Preview isolation | Metadata, docs, source scripts and traversal requests return 404 |

Generated screenshots are in ignored `test-results/`: `contact-1440.png`,
`contact-768.png`, `contact-390.png`, `contact-320.png`, `contact-success.png`,
`contact-validation.png` and `contact-failure.png`. Run the README checks to
regenerate them. Initial sandboxed Google Fonts requests were blocked; the
final screenshots and console checks loaded real Montserrat with network
access allowed.

Limitations: viewport emulation is not physical phone or Safari/Firefox testing.
No full screen-reader audit was performed. The 320px check tests narrow reflow,
not every real zoom scenario. Formspree account settings, filtering, backend
validation, quotas and actual Zoho notification receipt remain untested.

## Proposed production deployment — requires approval

1. Complete the real delivery test and review final copy, privacy, screenshots
   and production account settings with the owner.
2. After approval to prepare the release, configure the production endpoint
   and live mode on the feature branch. If approved as part of replacing the
   Google workflow, update the homepage's two CTA destinations to
   `contact.html` in a reviewable diff. That change has **not** been made.
   Keep the Google fallback for initial release unless separately authorized.
3. Rerun checks and obtain explicit approval for the concrete final production
   diff before merge/push. Only then use the existing main/Pages workflow.
   Preserve CNAME and DNS/mail settings.
4. A branch alone creates no preview URL. If remote staging is needed,
   propose a separate hosting project/repository without production CNAME
   and obtain approval before publishing it.
5. After approved deployment, check HTTPS/assets/navigation and one approved
   real production-domain test received in Zoho. Monitor filtering/quota.
   Remove the Google fallback only with separate authorization.

## Rollback

Nothing was deployed, so no production rollback is currently needed. Preserve
the feature branch for review. Commit or stash before changing branches;
uncommitted work can follow a checkout.

For a future approved release, record its SHA and merge strategy. Prepare a
new revert commit rather than resetting or force-pushing history:

```powershell
git revert <release-commit-sha>
```

For a merge commit, use `git revert -m 1 <merge-commit-sha>` after confirming
parent 1 is the previous production mainline. Review the restored Google Form
links against baseline `6ad3d2c`, obtain approval before pushing to main (which
redeploys Pages), and check the old contact method after deployment. No DNS
rollback is needed.

## Official references

- [AJAX](https://help.formspree.io/articles/building-your-form/submit-forms-with-javascript-ajax)
- [Verified notification recipient](https://help.formspree.io/articles/form-and-project-settings/changing-a-form-email-address)
- [Honeypot](https://help.formspree.io/articles/building-your-form/honeypot-spam-filtering)
- [Domain restriction and referrer requirements](https://help.formspree.io/articles/form-and-project-settings/restrict-to-domain)
- [CAPTCHA settings](https://help.formspree.io/articles/form-and-project-settings/recaptcha-settings)
- [Rate limits](https://help.formspree.io/articles/form-and-project-settings/system-limits)
- [Storage security](https://formspree.io/security/), [plan/archive details](https://formspree.io/plans)

These sources inform setup guidance; they do not establish account settings.
