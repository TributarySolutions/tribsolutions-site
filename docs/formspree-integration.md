# Formspree integration

The site is static HTML/CSS with vanilla JavaScript, hosted on GitHub Pages.
The **Vanilla JS / AJAX** integration matches this stack. Existing native
`fetch` code already provides validation, progress, duplicate protection,
success/error states and local simulation, so no SDK, CDN script, React or
build system was added.

## Applied configuration

`assets/contact-config.js` now contains the owner-supplied public endpoint:

```js
window.CONTACT_FORM_CONFIG = Object.freeze({
  mode: "live",
  endpoint: "https://formspree.io/f/mnppdeaj"
});
```

This enables real submissions in the unpublished feature-branch version. It
does not deploy anything. For local success/failure simulations, switch only
`mode` to `"demo"` and reload. A blank endpoint also forces demo mode.

The existing handler assigns the form action from validated configuration and
POSTs `FormData` with `Accept: application/json`. It includes name, email,
optional organization, message and the supported `_gotcha` honeypot. The
browser controls the multipart Content-Type boundary. Notification recipients
are configured in Formspree, not the public client code. No private tokens or
passwords are added to source. Existing CSP already permits
connections to Formspree; no policy change was needed.

One handler correction was needed: Formspree's current client recognizes a
string `next` property as success, while our prior code required `ok: true`.
The handler now accepts both success shapes and rejects conflicting errors,
negative flags and malformed responses. It does not navigate to the returned
URL or render provider HTML. Existing validation/duplicate/progress behavior
is preserved.

## Verification

The new integration test loads the saved configuration, submits to an
intercepted version of the exact configured endpoint, and verifies the
in-page success state. All real Formspree requests are blocked or mocked in
the automated suite. Demo/design checks explicitly select demo mode so they
remain independent of the default live configuration.

Run the full suite with `python -m unittest discover -s tests -v`, then the two
JavaScript syntax checks in README. All 17 browser tests, both JavaScript
syntax checks and the whitespace/diff check passed. The running local server
also returned HTTP 200 for the updated configuration. The automated tests did
not send real messages.

On October 27, 2026, the owner reported successfully receiving an email from
a real submission through the local contact preview. This confirms the local
Formspree-to-email path based on the owner's receipt confirmation. The owner
initially confirmed that **Jordan only** received it.

On October 28, 2026, the owner confirmed the Formspree Email workflow recipient
and Zoho distribution-list address are both `inquiries@tribsolutions.com`.
A direct email to that group reached Marlena. A subsequent fresh submission
through the local contact preview then reached **both Jordan and Marlena**,
as confirmed by the owner. Local end-to-end delivery to both intended recipients
is now verified through owner reports. The agent has not independently inspected
the inboxes or account settings. No production-domain submission has been tested,
and no deployment has been authorized or performed.

The owner subsequently reported completing the project's production domain
restriction with `tribsolutions.com`, following the provided setup instructions.
This is recorded as owner-configured, not independently inspected or tested
from the production origin. Localhost is now outside the permitted domain and
real local submissions can be routed to Formspree's spam inbox.

## Dashboard and real delivery checklist

The local delivery test succeeded as reported above. Complete or confirm these
remaining account checks before production:

1. **Recipient routing confirmed by the owner:** Formspree sends to
   `inquiries@tribsolutions.com`, and Zoho distributes to Jordan and Marlena.
   Retain that distribution list and its membership. No paid multiple-recipient
   Formspree feature or mailbox forwarding rule is used for this route.
2. Keep backend spam filtering enabled and retain the honeypot. This custom
   AJAX form has no CAPTCHA token. A form requiring a CAPTCHA challenge needs
   matching backend-verified integration before use; do not assume the
   dashboard's CAPTCHA setting works with this code unchanged.
3. **Production domain configured by the owner:** `tribsolutions.com`, without
   protocol or www, which Formspree documents as covering subdomains too.
   Preserve that restriction. Referrer suppression can cause filtering despite
   a successful client response. Further local simulations should use demo
   mode or the intercepted test suite, not loosen the production restriction.
4. After an explicitly approved deployment, verify one approved real submission
   from the production origin and its receipt in both inboxes. No public
   staging site has been created.

Start the preview from the repository with `python dev/preview.py`. The local
form is now in **live mode**: its Send inquiry button performs a real external
submission. Use demo mode for further local simulations now that the production
domain is restricted. After an approved deployment and authorization to test
delivery, send one fictional, clearly labeled inquiry from the production page
with a timestamp and a reply address you control. Verify Formspree's dashboard/
spam inbox, then actual receipt in both Zoho inboxes, all fields and Reply-To.
A client success message only establishes backend acceptance; it does not
establish email receipt.

The earlier contact and design handoffs describe the earlier demo-only state.
These integration notes supersede their empty-endpoint/default-demo statements.
The final release preparation changes the homepage's two contact buttons to
`contact.html`. The existing Google Form URL stays available as the contact-page
fallback. The approved design, live production site and DNS are unchanged.
Publishing still requires explicit approval.

## Concrete release awaiting approval

The feature branch contains the approved design refinements, responsive image
variants, live Formspree configuration and the homepage contact-button change.
Both intended inboxes received a local test before the production restriction
was set. No merge, push or production deployment is authorized yet.

Final release-preparation verification on October 28, 2026: all 17 browser
tests passed again, both JavaScript syntax checks passed, and a separate browser
check confirmed that each homepage contact button opens the configured contact
page with its Google fallback present. These checks did not send real inquiries.

After explicit approval, use the existing main/GitHub Pages release path,
retaining CNAME and DNS/mail settings. Check HTTPS, navigation, image loading
and the production contact page, then coordinate a real production-origin
delivery test. A new revert of the recorded release commit(s) restores the
previous production version if required; do not reset/force-push main. The
previous production baseline remains `6ad3d2c`.

## Official sources

- [AJAX integration](https://help.formspree.io/articles/building-your-form/submit-forms-with-javascript-ajax/)
- [Formspree native fetch implementation](https://github.com/formspree/formspree-js/blob/main/packages/formspree-core/src/core.ts)
- [Current success response shape](https://github.com/formspree/formspree-js/blob/main/packages/formspree-core/src/submission.ts)
- [Recipient setup](https://help.formspree.io/articles/form-and-project-settings/changing-a-form-email-address)
- [Domain restrictions](https://help.formspree.io/articles/form-and-project-settings/restrict-to-domain)
- [CAPTCHA settings](https://help.formspree.io/articles/form-and-project-settings/recaptcha-settings)
