// "Hoeveel vermogen hebben mijn panelen nog?" on /artikels/zijn-mijn-zonnepanelen-versleten/.
// A rough band, not a measurement: NREL median of 0,5 % loss per year (Jordan & Kurtz), with a
// band from 0,4 % (JinkoSolar Tiger Neo warranty) to 0,9 % per year (NREL average, Jordan et al. 2016). Runs in the browser, nothing is sent.
document.addEventListener("DOMContentLoaded", () => {
  const form = document.querySelector(".panel-age");
  if (!form) return;
  const yearSelect = form.querySelector("[name=jaar]");
  const kwpInput = form.querySelector("[name=kwp]");
  const result = form.querySelector(".panel-age-result");
  const thisYear = new Date().getFullYear();

  for (let y = thisYear; y >= 2000; y--) {
    const option = document.createElement("option");
    option.value = String(y);
    option.textContent = String(y);
    yearSelect.append(option);
  }

  const pct = (age, rate) => 100 * Math.pow(1 - rate, age);
  const nl = (n, d = 0) => n.toFixed(d).replace(".", ",");

  form.addEventListener("submit", (event) => {
    event.preventDefault();
    const year = Number(yearSelect.value);
    if (!year) { yearSelect.focus(); return; }
    const age = Math.max(0, thisYear - year);
    const typical = pct(age, 0.005);
    const low = pct(age, 0.009);
    const high = pct(age, 0.004);
    const kwp = Number(String(kwpInput.value || "").replace(",", "."));
    let html = `<p class="panel-age-figure">± ${nl(typical)}%</p>`
      + `<p>Panelen van ${year} (${age} jaar oud) leveren vandaag typisch nog zo'n ${nl(typical)}% van hun oorspronkelijke vermogen. Met 0,4 tot 0,9% verlies per jaar ligt dat tussen ${nl(low)}% en ${nl(high)}%.</p>`;
    if (kwp > 0 && kwp < 100) {
      html += `<p>Bij ${nl(kwp, 2)} kWp is dat ongeveer ${nl(kwp * typical / 100, 2)} kWp, tussen ${nl(kwp * low / 100, 2)} en ${nl(kwp * high / 100, 2)} kWp.</p>`;
    }
    if (year <= 2021) {
      html += `<p>Kreeg je installatie groenestroomcertificaten en lopen die nog? Dan mag je panelen enkel vervangen bij een bewezen defect. Lees <a href="/artikels/groenestroomcertificaten-thuisbatterij/">wat er wel mag</a>.</p>`;
    }
    html += `<p class="panel-age-note">Een schatting op basis van gemiddelden, geen meting. Een defect paneel kan veel meer verliezen.</p>`;
    result.innerHTML = html;
    result.hidden = false;
  });
});
