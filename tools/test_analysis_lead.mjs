// Runs the embedded verbruiksanalyse (battery-roi-tool assets/js/lead-submit.js) against the
// Firestore emulator loaded with the battery-roi-tool rules. The product list is read from the
// real (public) config/products, so the stored result has the real shape.
// Started by .github/workflows/test-contact-form.yml with ROI_DIR pointing at a battery-roi-tool clone.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { pathToFileURL } from "node:url";

const roi = process.env.ROI_DIR || "/tmp/roi";
const { submitLeadAnalysis, loadProductConfigs } = await import(pathToFileURL(`${roi}/assets/js/lead-submit.js`).href);

const host = process.env.FIRESTORE_EMULATOR_HOST || "127.0.0.1:8080";
const baseUrl = `http://${host}/v1/projects/demo-smartpeak/databases/(default)/documents`;
const asOwner = { headers: { Authorization: "Bearer owner" } };
const resultPageUrl = "https://smartpeak-be.github.io/battery-roi-tool/lead-result.html";

async function read(path) {
  const response = await fetch(`${baseUrl}/${path}`, asOwner);
  assert.equal(response.status, 200, `could not read ${path}`);
  return (await response.json()).fields;
}

// One year of daily Fluvius data: injection in summer, more consumption in winter.
function syntheticYearCsv(year = 2025) {
  const rows = ["EAN-code;Meter;Metertype;Register;Volume;Eenheid;Van (datum);Van (tijdstip);Tot (datum);Tot (tijdstip);Geldig sinds"];
  const pad = (n) => String(n).padStart(2, "0");
  const fmt = (d) => `${pad(d.getUTCDate())}-${pad(d.getUTCMonth() + 1)}-${d.getUTCFullYear()}`;
  const v = (x) => x.toFixed(3).replace(".", ",");
  const meta = '="541448820012345678";="1SAG1234567890";Digitaal';
  for (let i = 0; i < 365; i++) {
    const d = new Date(Date.UTC(year, 0, 1 + i));
    const n = new Date(Date.UTC(year, 0, 2 + i));
    const season = Math.sin(Math.PI * (i - 80) / 365);
    const inj = Math.max(0.5, 14 * Math.max(0, season) + 1);
    const afn = Math.max(3, 9 - 5 * season);
    rows.push(`${meta};Afname Dag;${v(afn * 0.45)};kWh;${fmt(d)};00:00;${fmt(n)};00:00;01-01-2020`);
    rows.push(`${meta};Afname Nacht;${v(afn * 0.55)};kWh;${fmt(d)};00:00;${fmt(n)};00:00;01-01-2020`);
    rows.push(`${meta};Injectie Dag;${v(inj)};kWh;${fmt(d)};00:00;${fmt(n)};00:00;01-01-2020`);
    rows.push(`${meta};Injectie Nacht;${v(0)};kWh;${fmt(d)};00:00;${fmt(n)};00:00;01-01-2020`);
  }
  return rows.join("\n") + "\n";
}

const configs = await loadProductConfigs();
console.log(`Product list: ${configs.length} configurations (${configs.filter((c) => c.type.startsWith("ZSF")).length} Zendure).`);

const cases = [
  {
    label: "full year, all optional fields",
    input: { csvText: syntheticYearCsv(), name: "Test Jaar", email: "jaar@example.com", pvInverterKw: 5.2, pricePerKwh: 0.31, houseAgeOver10Years: true },
    expectResult: true,
  },
  {
    label: "30-day Fluvius test file, defaults",
    input: { csvText: readFileSync(`${roi}/e2e/fixtures/test-fluvius.csv`, "utf8"), name: "Test Maand", email: "maand@example.com" },
    expectResult: null, // whatever the calculation gives; the rules must accept it
  },
];

for (const { label, input, expectResult } of cases) {
  const { leadId, resultUrl } = await submitLeadAnalysis(
    { ...input, source: "smartpeak.be/batterij-iets-voor-mij/" },
    { baseUrl, configs, resultPageUrl },
  );
  const lead = await read(`leads/${leadId}`);
  assert.equal(lead.status.stringValue, "cold_lead");
  assert.ok(lead.createdAt.timestampValue, "createdAt set");
  assert.equal(lead.email.stringValue, input.email);
  assert.match(lead.notes.stringValue, /^Verbruiksanalyse via de website \(smartpeak\.be\/batterij-iets-voor-mij\/\)/);
  assert.equal(lead.csvDailyCompact.mapValue.fields.afname.arrayValue.values.length > 0, true);
  if (expectResult) assert.ok(lead.result.mapValue, "lead has a result");

  const mail = await read(`mail/lead_result_${leadId}`);
  assert.equal(mail.to.stringValue, input.email);
  assert.equal(mail.message.mapValue.fields.subject.stringValue, "Je batterij-analyse is klaar SmartPeak");
  assert.ok(mail.message.mapValue.fields.html.stringValue.includes(resultUrl), "mail links the result page");
  const result = lead.result.mapValue ? Object.keys(lead.result.mapValue.fields).join(", ") : "none";
  console.log(`OK ${label}: lead ${leadId}, result fields: ${result}`);
}

// A result mail to another address than the lead's must still be refused.
const root = "projects/demo-smartpeak/databases/(default)/documents";
const commit = (writes) => fetch(`${baseUrl}:commit`, {
  method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ writes }),
});
const now = { fieldPath: "createdAt", setToServerValue: "REQUEST_TIME" };
const created = await commit([{
  update: { name: `${root}/leads/negatieftest`, fields: {
    customerName: { stringValue: "Test Fout" }, email: { stringValue: "fout@example.com" },
    status: { stringValue: "cold_lead" }, hotLeadAt: { nullValue: null }, deletedAt: { nullValue: null },
    resultExpiresAt: { timestampValue: new Date(Date.now() + 86400000).toISOString() },
  } },
  updateTransforms: [now], currentDocument: { exists: false },
}]);
assert.equal(created.status, 200, "plain lead accepted");
const mailTo = (to) => commit([{
  update: { name: `${root}/mail/lead_result_negatieftest`, fields: {
    kind: { stringValue: "lead_result" }, leadId: { stringValue: "negatieftest" }, to: { stringValue: to },
    message: { mapValue: { fields: { subject: { stringValue: "Je batterij-analyse is klaar SmartPeak" }, html: { stringValue: "x" } } } },
  } },
  updateTransforms: [now], currentDocument: { exists: false },
}]);
assert.equal((await mailTo("ander@example.com")).status, 403, "rules reject a result mail to another address");
assert.equal((await mailTo("fout@example.com")).status, 200, "the same mail to the lead's own address is accepted");

console.log("Verbruiksanalyse OK: leads and result mails are accepted by the rules.");
