// Snelle check on /batterij-iets-voor-mij/: five questions, a first direction, no numbers.
// It only follows the criteria on that page; the real advice still comes from the consumption
// data and the site visit. Nothing is sent anywhere unless the visitor clicks through to contact.
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".quick-check");
  const result = document.querySelector(".qc-result");
  if (!form || !result) return;

  const LABELS = {
    panelen: { ja: "ja", gepland: "gepland", nee: "nee" },
    verbruik: { avond: "vooral 's ochtends en 's avonds", dag: "vooral overdag", "weet-niet": "weet ik niet" },
    wagen: { ja: "ja", gepland: "gepland", nee: "nee" },
    warmtepomp: { ja: "ja", gepland: "gepland", nee: "nee" },
    contract: { dynamisch: "dynamisch", "vast-variabel": "vast of variabel", "weet-niet": "weet ik niet" },
  };
  const QUESTIONS = {
    panelen: "Zonnepanelen", verbruik: "Meeste verbruik", wagen: "Elektrische wagen of laadpaal",
    warmtepomp: "Warmtepomp", contract: "Energiecontract",
  };

  const advise = (a) => {
    const reasons = [];
    let score = 0;
    if (a.panelen === "ja") { score += 2; reasons.push("Met zonnepanelen kan de batterij je overschot van overdag bewaren voor later."); }
    if (a.panelen === "gepland") { score += 1; reasons.push("Plaats je binnenkort zonnepanelen, dan nemen we de batterij best meteen mee in het ontwerp."); }
    if (a.panelen === "nee") reasons.push("Zonder zonnepanelen haalt een batterij haar voordeel vooral uit een dynamisch contract en het afvlakken van pieken.");
    if (a.verbruik === "avond") { score += 2; reasons.push("Wie vooral 's ochtends en 's avonds verbruikt, injecteert overdag vaak veel. Precies dat overschot vangt een batterij op."); }
    if (a.verbruik === "weet-niet") { score += 1; reasons.push("Wanneer je het meest verbruikt, zie je in je gegevens van Mijn Fluvius. Dat bekijken we graag samen."); }
    if (a.verbruik === "dag") reasons.push("Verbruik je overdag al veel zelf, dan blijft er minder over om op te slaan.");
    if (a.wagen !== "nee") { score += 1; reasons.push("Een elektrische wagen is een groot verbruik dat je met een batterij en slimme sturing beter spreidt."); }
    if (a.warmtepomp !== "nee") { score += 1; reasons.push("Een warmtepomp verhoogt je verbruik en je pieken, zeker in de winter. Dat telt mee in de keuze van het vermogen."); }
    if (a.contract === "dynamisch") { score += 1; reasons.push("Met een dynamisch contract kan de batterij laden wanneer stroom goedkoop is en leveren wanneer hij duur is."); }

    let title = "Een batterij past waarschijnlijk goed bij je situatie";
    let text = "Veel van wat een batterij interessant maakt, is bij jou van toepassing. Hoe groot de batterij moet zijn en welk vermogen ze nodig heeft, hangt af van je echte verbruik.";
    if (score <= 2 || (a.panelen === "nee" && a.contract !== "dynamisch")) {
      title = "Misschien is iets anders een betere eerste stap";
      text = "Een batterij is mogelijk, maar het voordeel is in jouw situatie waarschijnlijk kleiner. Soms levert iets anders meer op, zoals je verwarming of warm water slimmer sturen. Ook dat bekijken we graag met je.";
    } else if (score <= 4) {
      title = "Een batterij kan zinvol zijn, je verbruik beslist";
      text = "Er zijn duidelijke redenen voor een batterij, maar het hangt sterk af van hoeveel je injecteert en wanneer je verbruikt. Je gegevens uit Mijn Fluvius geven daar snel uitsluitsel over.";
    }
    return { title, text, reasons };
  };

  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(form));
    const error = form.querySelector(".qc-error");
    if (Object.keys(QUESTIONS).some((key) => !data[key])) {
      error.hidden = false;
      return;
    }
    error.hidden = true;
    const { title, text, reasons } = advise(data);
    const summary = "Snelle check op de website:\n" + Object.keys(QUESTIONS)
      .map((key) => `- ${QUESTIONS[key]}: ${LABELS[key][data[key]]}`).join("\n") + "\n\n";
    const contact = "/contact/?onderwerp=afspraak&van=snelle-check&bericht=" + encodeURIComponent(summary);
    result.innerHTML = `<h3>${esc(title)}</h3><p>${esc(text)}</p>` +
      `<ul>${reasons.map((r) => `<li>${esc(r)}</li>`).join("")}</ul>` +
      `<p>Dit is een eerste richting, geen advies. Dat geven we pas na een blik op je verbruik en een plaatsbezoek.</p>` +
      `<div class="hero-actions"><a class="button" href="${contact}">Bespreek het met ons</a>` +
      `<a class="button button-ghost" href="#analyse">Laat je verbruik bekijken</a></div>`;
    result.hidden = false;
    result.focus();
  });
});
