# Appearance failure investigation

Investigated October 28, 2026, after the owner reported incorrect text sizes
and severely cut-off portraits in Chrome on Windows. Release `8b4279f` was
rolled back by `3659651`; production remains on the original website. All
changes described below are local to `feature/design-refinements` and require
new approval before deployment.

## Finding

A concrete browser-cache upgrade bug reproduces the reported symptoms. Both
the original and released HTML referenced the same `assets/styles.css` URL,
but the release changed the HTML structure and the corresponding CSS rules.
Reading the public site's headers showed `Cache-Control: max-age=600` on both
HTML and CSS. A returning browser could therefore combine newly fetched HTML
with a still-fresh, ten-minute-old stylesheet.

This was reproduced in installed Chrome on Windows (155.0.8059.86), using a
real browser cache and a loopback server with the same cache lifetime:

1. Load the original homepage from `/`, warming its CSS cache.
2. Switch the local server to the released Git snapshot.
3. Open `/index.html`, a new HTML URL whose stylesheet URL is unchanged.
4. Compare the result with the release in a fresh Chrome context.

The server recorded only one request for `/assets/styles.css`, from the
original version. The upgraded page genuinely reused the old cached CSS;
the test did not inject or substitute a stylesheet.

| Element | Intended release with matching CSS | New HTML with cached original CSS |
| --- | --- | --- |
| Dominant homepage H1 | 76px | 14.4px, uppercase label styling |
| Jordan image CSS height | 320px | 1,356px |
| Marlena image CSS height | 320px | 2,048px |

The old `.hero-text h1` rule styled the small “Water Resources Consulting”
label. In the new HTML, that selector instead matched the full headline,
making it tiny. The original portrait rules did not size the new `picture`
wrappers or override the new image height attributes; `object-fit: cover`
then filled extremely tall image boxes, enlarging/cutting off the faces.

I cannot inspect the historical contents of the owner's browser cache, so
this is a reproduced matching failure rather than a claim of direct access
to that session. It is a strong explanation for the fresh browser checks
passing while an existing visitor saw broken formatting.

## Why the earlier checks missed it

The earlier tests opened fresh browser contexts. Their request interception
also disabled Playwright HTTP caching, and the preview server deliberately
sent `no-store`. The production byte comparisons additionally used unique
query strings. Those checks established that a complete, fresh release was
present and could render correctly, but did not exercise an existing visitor
upgrading from the old page and cached assets. That was a gap in the release
verification, not something the visitor should have to work around.

## Fix prepared on the feature branch

- New HTML references physical CSS/JS files with content hashes in their
  names, such as `site.1cef2eb35ccd.css`. The new URL cannot reuse the original
  unversioned stylesheet from a browser or intermediary cache.
- The editable shared stylesheet for the refined design is `assets/site.css`.
  `assets/styles.css` is restored to the original production contents so
  cached original HTML can continue loading its matching legacy CSS.
- Shared CSS, contact CSS, the configuration script and the form handler all
  receive versioned snapshots, keeping the HTML and related assets aligned.
- `python dev/version_assets.py` generates snapshots and updates HTML.
  `--check` fails if source files, snapshots or page references disagree.
  Line endings are normalized for consistent names on Windows and GitHub.
- Published snapshots must be retained, so older cached HTML continues to
  find the exact CSS/JS that was published with it. The helper never deletes
  or overwrites an existing snapshot with different contents.

Future rollbacks should restore the previous HTML while retaining published
CSS/JS snapshots and their image dependencies for cached visitors. Deleting
those assets during a rollback could strand cached HTML with missing files.

This uses only Python's standard library for release preparation. It adds no
framework, bundler, CDN script or production runtime dependency. No visual
redesign, image recropping, endpoint change, mail setting or DNS change is part
of this fix. Images already have separate original/optimized filenames.

Previously cached HTML from the failed release can remain until its cache
lifetime expires; the server cannot rewrite a document already in a browser's
cache. The original site has been restored, and future releases using the
versioned assets prevent this mismatch when the new HTML is fetched.

## Verification and evidence

All **20 browser tests passed**: the existing 17 tests plus three cache checks.
The cache tests intentionally avoid Playwright routing and never submit a form.
They demonstrate the old-release failure, preserve original CSS compatibility,
check snapshot integrity, and compare warm-cache upgrades with fresh loads at
1440, 1024, 768, 390 and 360px. Cached and fresh layouts now match, including
headline sizes and portrait frame dimensions. Contact-page upgrades from the
failed release are also checked with its unversioned CSS/JS cached first.

To repeat the investigation and checks:

```powershell
python dev/reproduce_cache.py
python dev/version_assets.py --check
python -m unittest discover -s tests -v
```

Screenshots and the original measured values are generated locally under
ignored `test-results/cache-investigation/`:

- `warm-cache-release-hero.png` and `warm-cache-release-portraits.png`: reproduced failure.
- `fresh-release-hero.png` and `fresh-release-portraits.png`: fresh original release.
- `fixed-warm-cache-home-1440.png` and `fixed-warm-cache-home-390.png`: fixed upgrade.
- `fixed-warm-cache-contact-1440.png` and `fixed-warm-cache-contact-390.png`: fixed contact upgrade.
- `metrics.json`: computed sizes and server asset-request history.

The new design and form are not republished. Future release verification must
include both a fresh load and an actual cached-browser upgrade, followed by
owner review in Chrome. Rollback commit `3659651` remains production main.

This fix branch descends from the previously released feature commit, while
main contains its rollback. A future approved release must explicitly restore
the feature set together with this cache fix; simply merging or cherry-picking
only the fix onto the rollback can leave missing form assets or conflicts.
Prepare and test that complete release tree before any new production push.

## References

- [HTTP caching and content-versioned URLs](https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Caching)
- [Playwright routing disables HTTP caching](https://playwright.dev/python/docs/api/class-browsercontext#browser-context-route)
- [CSS object-fit cropping behavior](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/object-fit)
