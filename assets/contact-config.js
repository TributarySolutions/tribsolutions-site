// Public configuration only. Never put email addresses, credentials, or tokens here.
// "live" enables Formspree in this unpublished version; "demo" simulates locally.
// Confirm actual delivery to Zoho and obtain release approval before publishing.
window.CONTACT_FORM_CONFIG = Object.freeze({
  mode: "live", // Change to "demo" for success/failure simulations without sending.
  endpoint: "https://formspree.io/f/mnppdeaj" // Public endpoint identifier, not a secret.
});
