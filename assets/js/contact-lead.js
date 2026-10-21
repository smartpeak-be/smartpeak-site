// Sends a website contact request into the SmartPeak lead system (battery-roi-tool)
// using only what its public Firestore rules allow, so no keys are needed:
//   1. create a lead (cold_lead) with the contact details in `notes`
//   2. mark it hot_lead; the battery-roi-tool Cloud Function then mails Kevin and Ruben
//      (clients may not write to the `mail` collection)
// The same module runs in the browser and in tools/test_contact_lead.mjs.

export const FIRESTORE_URL =
  "https://firestore.googleapis.com/v1/projects/smartpeak-projects/databases/(default)/documents";

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

  await commit(fetchImpl, baseUrl, [{
    update: { name: leadName, fields: { status: str("hot_lead") } },
    updateMask: { fieldPaths: ["status"] },
    updateTransforms: [{ fieldPath: "hotLeadAt", setToServerValue: "REQUEST_TIME" }],
    currentDocument: { exists: true },
  }]);
  return leadId;
}
