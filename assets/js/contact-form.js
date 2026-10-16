import { submitContactLead } from "./contact-lead.js";

const form = document.getElementById("contactformulier");

function sourcePage() {
  const params = new URLSearchParams(location.search);
  if (params.get("van")) return params.get("van");
  try {
    const referrer = new URL(document.referrer);
    if (referrer.origin === location.origin && referrer.pathname !== location.pathname) {
      return referrer.pathname + referrer.search;
    }
    if (document.referrer) return referrer.href;
  } catch {
    // no or invalid referrer
  }
  return "rechtstreeks";
}

function preselectSubject() {
  const wanted = (new URLSearchParams(location.search).get("onderwerp") || "").toLowerCase();
  const select = form.elements.subject;
  for (const option of select.options) {
    if (wanted && option.value.toLowerCase().startsWith(wanted)) select.value = option.value;
  }
}

function prefillMessage() {
  const text = new URLSearchParams(location.search).get("bericht");
  const field = form.elements.message;
  if (text && !field.value) field.value = text.slice(0, 1500);
}

function setStatus(kind, html) {
  const status = form.querySelector(".form-status");
  status.className = `form-status form-status-${kind}`;
  status.innerHTML = html;
  status.hidden = false;
}

if (form) {
  const openedAt = Date.now();
  form.elements.source.value = sourcePage();
  preselectSubject();
  prefillMessage();

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const data = Object.fromEntries(new FormData(form));
    if (data.website || Date.now() - openedAt < 3000) {
      setStatus("ok", "Bedankt, je bericht is verstuurd.");
      form.reset();
      return;
    }
    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    button.textContent = "Versturen…";
    try {
      await submitContactLead(data);
      form.querySelectorAll(".field, .form-actions, .form-note").forEach((el) => { el.hidden = true; });
      setStatus("ok", `<strong>Bedankt, ${data.name.split(" ")[0].replace(/[<>&]/g, "")}.</strong> We hebben je bericht goed ontvangen en nemen zo snel mogelijk contact met je op.`);
      form.querySelector(".form-status").focus();
    } catch (error) {
      console.warn("Contactformulier versturen mislukt", error);
      const mail = encodeURIComponent(data.subject);
      setStatus("error", `Je bericht kon niet verstuurd worden. Probeer het opnieuw, of mail ons rechtstreeks op <a href="mailto:info@smartpeak.be?subject=${mail}">info@smartpeak.be</a>.`);
      button.disabled = false;
      button.textContent = "Verstuur";
    }
  });
}
