(() => {
  "use strict";

  const form = document.getElementById("contact-form");
  const fields = document.getElementById("contact-fields");
  const button = document.getElementById("submit-inquiry");
  const status = document.getElementById("form-status");
  const newInquiry = document.getElementById("new-inquiry");
  const demoPanel = document.getElementById("demo-panel");
  const outcome = document.getElementById("demo-outcome");
  const inputs = ["full-name", "email", "organization", "message"].map(id => document.getElementById(id));
  const config = window.CONTACT_FORM_CONFIG;
  let busy = false;
  let completed = false;

  function announce(message, state, focus = false) {
    status.textContent = message;
    status.dataset.state = state;
    if (focus) status.focus();
  }

  // Attach before enabling any controls; configuration failures stay closed.
  form.addEventListener("submit", submit);
  if (!config || !["demo", "live"].includes(config.mode) || typeof config.endpoint !== "string") {
    announce("The inquiry form is unavailable. Please use the Google inquiry form below.", "error");
    return;
  }
  const demo = config.mode === "demo" || config.endpoint === "";
  if (!demo && !/^https:\/\/formspree\.io\/f\/[a-zA-Z0-9]+$/.test(config.endpoint)) {
    announce("The inquiry form is unavailable. Please use the Google inquiry form below.", "error");
    return;
  }
  if (!demo) form.action = config.endpoint;
  demoPanel.hidden = !demo;
  button.textContent = demo ? "Test inquiry" : "Send inquiry";
  form.noValidate = true; // HTML5 constraints are checked below with inline messages.
  fields.disabled = false;
  announce("", "ready");

  function validate(input) {
    const value = input.value.trim();
    let error = "";
    if (input.required && !value) {
      error = input.name === "name" ? "Please enter your full name." :
        input.name === "email" ? "Please enter your email address." : "Please enter a project description or inquiry.";
    } else if (input.value.length > input.maxLength) {
      error = `Please use no more than ${input.maxLength.toLocaleString("en-US")} characters.`;
    } else if (input.validity.typeMismatch) {
      error = "Please enter a valid email address, such as name@example.com.";
    }
    const errorElement = document.getElementById(input.getAttribute("aria-describedby").split(" ").pop());
    errorElement.textContent = error;
    errorElement.hidden = !error;
    if (error) input.setAttribute("aria-invalid", "true");
    else input.removeAttribute("aria-invalid");
    return !error;
  }

  inputs.forEach(input => {
    input.addEventListener("input", () => {
      if (input.hasAttribute("aria-invalid")) validate(input);
    });
  });

  async function submit(event) {
    event.preventDefault();
    if (busy || completed || fields.disabled) return;
    const invalid = inputs.filter(input => !validate(input));
    if (invalid.length) {
      announce("Please review the highlighted fields and try again.", "error");
      invalid[0].focus();
      return;
    }
    // Capture before disabling the fieldset (disabled controls are omitted by FormData).
    const data = new FormData(form);
    inputs.forEach(input => data.set(input.name, input.value.trim()));
    busy = true;
    fields.disabled = true;
    outcome.disabled = true;
    fields.setAttribute("aria-busy", "true");
    button.textContent = demo ? "Testing…" : "Sending…";
    announce(demo ? "Simulating submission. No message is being sent…" : "Sending your inquiry…", "pending");
    let timeout;
    try {
      if (demo) {
        await new Promise(resolve => setTimeout(resolve, 850));
        if (outcome.value === "failure") throw new Error("demo");
      } else {
        const controller = new AbortController();
        timeout = setTimeout(() => controller.abort(), 15000);
        const response = await fetch(config.endpoint, {
          method: "POST",
          body: data,
          headers: { Accept: "application/json" },
          credentials: "omit",
          referrerPolicy: "strict-origin-when-cross-origin",
          signal: controller.signal
        });
        // Do not render untrusted server text or automatically retry an uncertain request.
        if (!response.ok) throw new Error(response.status === 429 ? "rate-limit" : "server");
        const result = await response.json();
        // Formspree's current API confirms success with a string `next` field.
        // Accept the earlier `ok: true` shape too, but never a conflicting error.
        const confirmed = result && typeof result === "object" && !Array.isArray(result) &&
          !("error" in result) && !("errors" in result) && result.ok !== false &&
          (result.ok === true || (typeof result.next === "string" && result.next.length > 0));
        if (!confirmed) throw new Error("unconfirmed");
      }
      completed = true;
      announce(demo ? "Demo successful. No message was sent. Start a new test to try again." :
        "Thank you. Your inquiry has been submitted. We’ll get back to you as soon as possible.", "success", true);
      button.textContent = demo ? "Test complete" : "Inquiry submitted";
      newInquiry.hidden = false;
    } catch (error) {
      const message = demo ? "Demo failure simulated. No message was sent. Your entries are still here; choose Successful submission to try again." :
        error.message === "rate-limit" ? "Too many attempts. Please wait a few minutes before trying again. Your entries are still here." :
        error.message === "server" ? "Your inquiry could not be submitted. Your entries are still here. Please try again later or use the Google inquiry form below." :
        "We couldn’t confirm submission. Your entries are still here. Please wait before trying again to avoid sending twice, or use the Google inquiry form below.";
      announce(message, "error", true);
      fields.disabled = false;
      button.textContent = demo ? "Test inquiry" : "Send inquiry";
    } finally {
      clearTimeout(timeout);
      busy = false;
      outcome.disabled = false;
      fields.removeAttribute("aria-busy");
    }
  }

  newInquiry.addEventListener("click", () => {
    form.reset();
    completed = false;
    fields.disabled = false;
    inputs.forEach(input => {
      input.removeAttribute("aria-invalid");
      const error = document.getElementById(input.getAttribute("aria-describedby").split(" ").pop());
      error.textContent = "";
      error.hidden = true;
    });
    newInquiry.hidden = true;
    button.textContent = demo ? "Test inquiry" : "Send inquiry";
    announce("", "ready");
    inputs[0].focus();
  });
})();
