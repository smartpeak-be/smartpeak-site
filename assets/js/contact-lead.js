// Sends a website contact request into the SmartPeak lead system (battery-roi-tool)
// using only what its public Firestore rules allow, so no keys are needed:
//   1. create a lead (cold_lead) with the contact details in `notes`
//   2. mark it hot_lead and queue a `lead_contact` mail to Kevin and Ruben
// The same module runs in the browser and in tools/test_contact_lead.mjs.

export const FIRESTORE_URL =
  "https://firestore.googleapis.com/v1/projects/smartpeak-projects/databases/(default)/documents";

const NOTIFY = ["kevin@smartpeak.be", "ruben@smartpeak.be"];
const RESULT_TTL_DAYS = 30;

const str = (value) => ({ stringValue: String(value) });

function documentRoot(baseUrl) {
  const marker = "/documents";
  return baseUrl.slice(baseUrl.indexOf("/projects/") + 1, baseUrl.indexOf(marker) + marker.length);
}

function randomId() {
  const chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789";
  const bytes = crypto.getRandomValues(new Uint8Array(20));
  return Array.from(bytes, (b) => chars[b % chars.length]).join("");
}

function escapeHtml(value) {
  return String(value ?? "").replace(/[&<>"']/g, (c) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
  }[c]));
}

function oneLine(value, max) {
  return String(value ?? "").replace(/\s+/g, " ").trim().slice(0, max);
}

export function buildNotes(form) {
  const lines = [
    "Contactformulier website",
    `Onderwerp: ${oneLine(form.subject, 80)}`,
    form.phone ? `Telefoon: ${oneLine(form.phone, 40)}` : null,
    form.postcode ? `Postcode: ${oneLine(form.postcode, 10)}` : null,
    form.solar ? `Zonnepanelen: ${oneLine(form.solar, 40)}` : null,
    form.source ? `Vanaf pagina: ${oneLine(form.source, 200)}` : null,
    "",
    String(form.message ?? "").trim(),
  ].filter((line) => line !== null);
  return lines.join("\n").slice(0, 2000);
}

function mailHtml(form, leadId) {
  const row = (label, value) => value
    ? `<tr><td style="padding:4px 12px 4px 0;color:#6b7a8d;white-space:nowrap;vertical-align:top">${label}</td>` +
      `<td style="padding:4px 0">${value}</td></tr>`
    : "";
  const email = escapeHtml(form.email);
  return `<!DOCTYPE html><html><head><meta charset="utf-8"></head>
<body style="margin:0;padding:24px;background:#f4f6f8;font-family:-apple-system,'Segoe UI',Roboto,sans-serif;color:#1f272e">
<table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;background:#fff;border-radius:12px;padding:24px 28px">
<tr><td>
<p style="margin:0 0 4px;font-size:20px;font-weight:700">SmartPeak</p>
<p style="margin:0 0 20px;color:#6b7a8d;font-size:13px">Nieuwe contactaanvraag via het contactformulier op de website</p>
<table cellpadding="0" cellspacing="0" style="font-size:15px;line-height:1.5;margin-bottom:16px">
${row("Naam", `<strong>${escapeHtml(form.name)}</strong>`)}
${row("E-mail", `<a href="mailto:${email}">${email}</a>`)}
${row("Telefoon", form.phone ? `<a href="tel:${escapeHtml(form.phone)}">${escapeHtml(form.phone)}</a>` : "")}
${row("Postcode", escapeHtml(form.postcode))}
${row("Zonnepanelen", escapeHtml(form.solar))}
${row("Onderwerp", escapeHtml(form.subject))}
${row("Vanaf pagina", escapeHtml(form.source))}
</table>
<div style="white-space:pre-wrap;background:#f3f7f5;border-radius:8px;padding:14px 16px;font-size:15px;line-height:1.5">${escapeHtml(form.message)}</div>
<p style="margin:20px 0 0;color:#6b7a8d;font-size:13px">De aanvraag staat als hot lead in het dashboard (lead-id ${escapeHtml(leadId)}).</p>
</td></tr></table></body></html>`;
}

async function commit(fetchImpl, baseUrl, writes) {
  const response = await fetchImpl(`${baseUrl}:commit`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ writes }),
  });
  if (!response.ok) {
    throw new Error(`Firestore ${response.status}: ${(await response.text()).slice(0, 300)}`);
  }
}

export async function submitContactLead(form, { baseUrl = FIRESTORE_URL, fetchImpl = fetch } = {}) {
  const root = documentRoot(baseUrl);
  const leadId = randomId();
  const leadName = `${root}/leads/${leadId}`;
  const expires = new Date(Date.now() + RESULT_TTL_DAYS * 86400000).toISOString();

  await commit(fetchImpl, baseUrl, [{
    update: {
      name: leadName,
      fields: {
        customerName: str(oneLine(form.name, 120)),
        email: str(String(form.email).trim()),
        notes: str(buildNotes(form)),
        status: str("cold_lead"),
        hotLeadAt: { nullValue: null },
        deletedAt: { nullValue: null },
        resultExpiresAt: { timestampValue: expires },
      },
    },
    updateTransforms: [{ fieldPath: "createdAt", setToServerValue: "REQUEST_TIME" }],
    currentDocument: { exists: false },
  }]);

  const subject = `Nieuwe contactaanvraag: ${oneLine(form.name, 80)} (${oneLine(form.subject, 40)})`;
  await commit(fetchImpl, baseUrl, [
    {
      update: { name: leadName, fields: { status: str("hot_lead") } },
      updateMask: { fieldPaths: ["status"] },
      updateTransforms: [{ fieldPath: "hotLeadAt", setToServerValue: "REQUEST_TIME" }],
      currentDocument: { exists: true },
    },
    {
      update: {
        name: `${root}/mail/lead_contact_${leadId}`,
        fields: {
          kind: str("lead_contact"),
          leadId: str(leadId),
          to: { arrayValue: { values: NOTIFY.map(str) } },
          message: { mapValue: { fields: {
            subject: str(subject.slice(0, 200)),
            html: str(mailHtml(form, leadId)),
          } } },
        },
      },
      updateTransforms: [{ fieldPath: "createdAt", setToServerValue: "REQUEST_TIME" }],
      currentDocument: { exists: false },
    },
  ]);
  return leadId;
}
