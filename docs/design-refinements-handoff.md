# Design refinements — review handoff

October 27, 2026. Work is on `feature/design-refinements`, based on the completed
contact-form project (`849d113`). The working tree was clean before starting.
The contact-form branch and production main have not been moved. No push,
merge, public preview, deployment or real form submission was performed.

## Review and baseline

Read-only HTTPS requests confirmed that the live homepage, contact page and
shared stylesheet still match production main (`6ad3d2c`). The development
contact page already contains the custom form, which the live site does not.
The before/after comparison deliberately uses the completed development
version (`849d113`) as the original for both pages. Its homepage is identical
to production; its contact page includes the preserved Demo/Test Mode.

The original layout already worked well for services, biographies and Hank.
The main opportunities were an oversized desktop headline, uneven hero balance,
duplicated navigation styles, low-contrast introductory text, sticky-header
anchor clearance and image payload. Original shared breakpoints were 800,
560 and 480px; the form also used 600 and 360px. The refinements retain those
layout breakpoints and use 720px for shared compact navigation.

## Design decisions

- **Hero:** Reduce the maximum headline from 92px to 76px (about 17%), use
  responsive sizing down to 40px, balance its line wrapping, and modestly
  reduce vertical padding. Preserve every word and the original river image
  and translucent overlay. The smaller text leaves room for the existing
  supporting copy and brings Services higher on the page.
- **Headings:** Make the dominant headline the single H1, with “Water Resources
  Consulting” retained as introductory text. Services and Principals remain
  H2s with H3 card/profile titles. Hank's independent section now has an H2
  with its existing visual size and unchanged copy.
- **Logo panel:** Compare the original and revised hero before retaining the
  panel. Reduce its desktop maximum width from roughly 363px to 340px and
  center the logo/button group beside the text. Keep the existing behavior
  of hiding that large panel on phones, where the navigation logo remains.
- **Cards/profiles:** Keep all six service categories and descriptions. Retain
  row alignment and allow the grid to shrink safely on narrow screens.
  Tighten section-heading spacing from 52px to 36px and section padding from
  92px to 80px. Equal-height principal cards and clipped photo frames keep
  portraits aligned; existing face positions and zooms remain. Restore clear
  spacing and smaller typography for the “Principal” role label.
- **Contact:** Reduce the contact headline maximum from 56px to 48px and
  slightly tighten the surrounding spacing. Preserve the entire form,
  privacy notice, fields, validation, success/error messages, test controls,
  configuration, CSP and backend behavior. The two contact scripts are
  byte-for-byte unchanged apart from Git line-ending normalization.
- **Navigation:** Use Services, Principals and Contact on both pages, mark
  Contact as the current page, and retain the labeled logo as the home link.
  Share focus/mobile rules rather than keeping contact-only copies. Navigation
  links are at least 44px high; primary buttons are at least 48px high.
  Small-screen logo sizing preserves its aspect ratio and avoids overflow.
- **Accessibility:** Add the homepage skip link; retain the form skip link.
  Give anchored sections/form 104px of sticky-header clearance. Use visible
  focus on both light and dark surfaces. Darken introductory labels to
  midnight blue and honor reduced-motion preferences. Remove the existing
  decorative service-card lift effect.
- **Footer:** Retain every word of the copyright and trademark statements;
  use smaller, consistent text and slightly tighter padding on both pages.

## Image loading and performance

All original JPGs and logo assets are preserved without modification. WebP
variants are resized/re-encoded from the full photographs, with no content
changes or cropping baked in. Existing CSS still controls the displayed crops.
Portrait variants use quality 86; the softly overlaid river uses quality 82.
Visual checks covered desktop, tablet and mobile framing.

| Image | Original | Variant(s) |
| --- | ---: | ---: |
| River | 5,934,426 bytes, 4656×3504 | 451,782 bytes at 1920px; 134,162 bytes at 960px |
| Jordan | 159,862 bytes, 2048×1356 | 14,762 bytes at 480px; 38,022 bytes at 960px |
| Marlena | 163,959 bytes, 1356×2048 | 18,486 bytes at 480px; 51,932 bytes at 960px |
| Hank | 268,419 bytes, 2048×1356 | 28,626 bytes at 480px |

At a desktop device pixel ratio of 1, the selected four photograph files total
513,656 bytes, compared with 6,526,666 bytes previously: a **92.1% reduction**.
This is an asset-byte comparison, not a measured real-world loading-time score.
Higher-density screens may select larger portraits. All seven variants together
add less than 740 KB to the repository; originals remain for maintenance.

Portraits use `picture`/`srcset` with existing JPG fallbacks, explicit dimensions,
lazy loading and asynchronous decoding. The river background selects 960px
below 800px and 1920px otherwise. The logo stays eagerly loaded. No dependencies,
fonts, analytics or scripts were added to the public pages. Pillow is only an
optional development tool for regenerating variants.

## Exact preview steps

In PowerShell:

```powershell
Set-Location -LiteralPath 'C:\Users\jordan\OneDrive - Tributary Solutions LLC\Tributary Solutions - Shared Documents\Admin\Website\tribsolutions-site'
git branch --show-current
python dev/preview.py
```

The branch should be `feature/design-refinements`. Open
**http://127.0.0.1:8000/review/**. The four comparison links switch original and
refined versions inside the same frame. Use the full-tab links to inspect the
actual browser width without the review controls. The comparison page is served
only by the development server and is not added to site navigation.

Direct views:

| Page | Original | Refined |
| --- | --- | --- |
| Homepage | http://127.0.0.1:8000/original/index.html | http://127.0.0.1:8000/index.html |
| Contact | http://127.0.0.1:8000/original/contact.html | http://127.0.0.1:8000/contact.html |

If the port is busy, use `python dev/preview.py --port 8001` and change the URLs
accordingly. Stop with Ctrl+C. The server binds only to loopback, blocks metadata
and path traversal, and does not implement POST processing. Git is needed for
the original routes; Python's standard library serves the refined pages.
Temporary preview processes are stopped at handoff. No branch-based public
preview URL is assumed or created.

Test at 1440, 1024, 768, 390 and 360px. Check headline wrapping, image crops,
service stacking, header links, anchored headings, keyboard focus and the form.
Use sample information in Demo/Test Mode and exercise successful and failed
results. No real messages are sent. The existing Google Form links remain.

## Screenshots

Matching full-page captures use a viewport height of 1000px at 1440px width and
844px at 390px width. Originals are from `849d113`. Images are in ignored
`test-results/design/` and are regenerated by the test suite:

| View | Original file | Refined file |
| --- | --- | --- |
| Homepage, 1440px | `original-index-1440.png` | `refined-index-1440.png` |
| Contact, 1440px | `original-contact-1440.png` | `refined-contact-1440.png` |
| Homepage, 390px | `original-index-390.png` | `refined-index-390.png` |
| Contact, 390px | `original-contact-390.png` | `refined-contact-390.png` |
| Hero detail, 1440px | `original-hero-1440.png` | `refined-hero-1440.png` |

Additional refined captures exist for both pages at 1024, 768 and 360px. The
browser runner scrolls to/decode lazy images before capturing and returns to
the top so sticky headers appear correctly. Screenshots were visually reviewed.

## Changed files

Modified: `index.html`, `contact.html`, `assets/styles.css`,
`assets/contact.css`, `dev/preview.py`, and `README.md`.

Added: `assets/banner-960.webp`, `assets/banner-1920.webp`,
`assets/jordan-480.webp`, `assets/jordan-960.webp`, `assets/marlena-480.webp`,
`assets/marlena-960.webp`, `assets/hank-480.webp`, `dev/optimize_images.py`,
`dev/review.html`, `tests/test_design.py`, and this handoff.

Unchanged: contact behavior/configuration scripts, original photographs, logo,
favicon, Google Form destinations, six service descriptions, all biographies,
Hank's copy, copyright/trademark statements and CNAME. The earlier contact
handoff is preserved as a record of that phase.

## Verification and limits

Run:

```powershell
python -m unittest discover -s tests -v
node --check assets/contact.js
node --check assets/contact-config.js
git diff --check
```

The 12 existing contact tests plus 4 design tests passed in installed Edge
(headless Chromium). No real backend requests are sent: every Formspree URL is
intercepted. Existing Google Fonts are loaded for representative typography.

- Both pages fit all five requested widths; the existing contact test also
  passes at 320px. Normal page loads have no console/JavaScript errors.
- All displayed images decode; responsive WebP selections, lazy-loading
  attributes and both river variants are verified. Services retain six cards
  with aligned heights within rows. Visible principal frames match in size.
- Automated comparisons preserve the text of the hero, services, biographies,
  Hank, CTA, footer and contact form. Original assets/scripts are checked
  against the baseline Git blobs.
- One homepage H1, logical heading levels, skip-link focus, page navigation,
  current-page indication, anchor clearance at all five widths and touch
  target heights pass. The prior form tests retain validation, keyboard,
  success/failure, duplicate, timeout and no-JavaScript checks.
- Representative solid-color contrast calculations: navy/page 17.38:1,
  navigation/white 10.82:1, muted copy/soft surface 6.85:1, footer 11.50:1,
  error/white 7.71:1, input border/white 3.38:1. These cover the sampled text
  and control pairs, not a full automated accessibility conformance audit.
- Original comparison routes return baseline bytes and block metadata/source
  traversal. The development review page is available only locally.
- Pages remain static HTML/CSS/JS with relative asset links and unchanged CNAME;
  no server-side hosting requirement was introduced.

No physical iOS/Android, Safari, Firefox, full screen-reader audit, field
performance measurements or account-side GitHub Pages inspection was performed.
GitHub Pages compatibility is checked structurally and locally; there has been
no deployment. Real Formspree/Zoho delivery remains pending from the earlier
task and was not exercised for design refinement.

## Deployment readiness and rollback

The design is ready for review, with the contact form intentionally in demo
mode. The design branch includes the earlier form commit, so deploying it as a
whole would also introduce that custom contact page. Before production, complete
the existing Formspree recipient/domain/spam setup and confirm one explicitly
authorized message in Zoho, then configure the real endpoint in a reviewable
change. Keep the Google fallback unless removal is separately approved.

Obtain explicit approval for the final production diff before merge/push. Use
the existing GitHub Pages workflow; retain CNAME and all DNS/mail records. No
public staging may be created without approval. If only the design should
ship before form setup, prepare a separately reviewed release against production
while retaining the custom-form work on these branches.

The design changes are saved in their own commit after `849d113`. To undo this
phase, prepare a revert of that design commit, which retains the earlier form
project. For any future combined production release, revert its recorded
release/merge commit rather than force-pushing history, using the earlier
contact handoff's rollback instructions. A production rollback push also
requires approval. Nothing currently needs rolling back on the live site.
