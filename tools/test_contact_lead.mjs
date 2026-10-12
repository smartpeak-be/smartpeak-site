// Runs the contact form submission against the Firestore emulator loaded with the
// battery-roi-tool security rules. Started by .github/workflows/test-contact-form.yml.
import assert from "node:assert/strict";
import { submitContactLead } from "../assets/js/contact-lead.js";

const host = process.env.FIRESTORE_EMULATOR_HOST || "127.0.0.1:8080";
const baseUrl = `http://${host}/v1/projects/demo-smartpeak/databases/(default)/documents`;
const asOwner = { headers: { Authorization: "Bearer owner" } };

async function read(path) {
  const response = await fetch(`${baseUrl}/${path}`, asOwner);
  assert.equal(response.status, 200, `could not read ${path}`);
  return (await response.json()).fields;
}

const form = {
  name: "Test Klant",
  email: "test@example.com",
  phone: "+32 470 00 00 00",
  subject: "Offerte",
  message: "Ik heb 12 panelen en een laadpaal.\n<b>geen html</b>",
  source: "/oplossingen/sigenergy-sigenstor/",
};

const leadId = await submitContactLead(form, { baseUrl });
const lead = await read(`leads/${leadId}`);
assert.equal(lead.status.stringValue, "hot_lead");
assert.ok(lead.hotLeadAt.timestampValue, "hotLeadAt set");
assert.ok(lead.createdAt.timestampValue, "createdAt set");
assert.match(lead.notes.stringValue, /Onderwerp: Offerte/);
assert.match(lead.notes.stringValue, /Vanaf pagina: \/oplossingen\/sigenergy-sigenstor\//);

const mail = await read(`mail/lead_contact_${leadId}`);
assert.deepEqual(mail.to.arrayValue.values.map((v) => v.stringValue), ["kevin@smartpeak.be", "ruben@smartpeak.be"]);
const html = mail.message.mapValue.fields.html.stringValue;
assert.ok(!html.includes("<b>geen html</b>"), "message is escaped");
assert.match(mail.message.mapValue.fields.subject.stringValue, /^Nieuwe contactaanvraag: Test Klant \(Offerte\)$/);

// The rules must still refuse what they are meant to refuse.
const rejected = await fetch(`${baseUrl}/leads`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ fields: { customerName: { stringValue: "x" }, email: { stringValue: "x@y.be" }, phone: { stringValue: "1" } } }),
});
assert.equal(rejected.status, 403, "rules reject unknown fields");

console.log(`Contact form OK: lead ${leadId} is hot and the notification mail is queued.`);
