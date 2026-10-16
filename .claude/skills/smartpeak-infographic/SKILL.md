---
name: smartpeak-infographic
description: "Maak een infographic of grafiek in de huisstijl van smartpeak.be (SVG in tools/article_charts.py, gerenderd naar WebP). Gebruik wanneer een artikel of hulpgids een afbeelding nodig heeft; geen stockfoto's."
---

# Infographic maken

Alle grafieken en schema's staan als Python-functies in `tools/article_charts.py`. Ze schrijven een SVG van 1600 × 900 in `assets/img/grafieken/`.

## Huisstijl

- Gebruik de helpers in het bestand: `svg(body, titel, ondertitel)`, `text()`, `box()`, `arrow()` + `markers()`, `axes()`, `hours_axis()`.
- Kleuren: de constanten bovenaan (`INK`, `SOFT`, `LINE`, `LEAF`, `LEAF_DEEP`, `LAGOON`, `LAGOON_DEEP`, `RED`). Groen voor "goed / eigen energie", blauwgroen voor "batterij / instelling", rood enkel voor een grens of waarschuwing.
- Lettertype: Instrument Sans, via de renderer. Tekst minstens 21 px, labels 23 tot 30 px.
- Onderaan staat altijd een voetnoot (y = 850 of 868): "Voorbeeld met fictieve waarden …" bij verzonnen cijfers, of de bron bij echte cijfers.

## Werkwijze

1. Bedenk wat de afbeelding toont dat de tekst **niet** al zegt: een verband, een volgorde, een verloop. Herhaal geen tabel of opsomming.
2. Schrijf een functie, bijvoorbeeld `def mijn_schema():`, en voeg een regel `write("bestandsnaam", mijn_schema())` toe onderaan in `__main__`.
3. Bouw en render:
   ```bash
   python3 tools/article_charts.py
   python3 tools/render_svg.py bestandsnaam
   python3 tools/make_image_variants.py
   ```
   `render_svg.py` gebruikt Playwright met de Chromium van de sandbox. `make_image_variants.py` vraagt Pillow en maakt de gsm-versie (`-w640.webp`), de deelafbeelding en de afmetingen in `content/image-sizes.json`.
4. **Bekijk het resultaat** (open de WebP). Controleer:
   - geen tekst die buiten een vak loopt of andere tekst overlapt;
   - labels die niet over lijnen of staven vallen;
   - niets dat tegen de rand plakt.
   Pas aan en render opnieuw tot het klopt.
5. Kijk na dat `git status` enkel je nieuwe bestanden en `tools/article_charts.py` toont. Andere grafieken mogen niet veranderd zijn.

## In de pagina

- `alt`: beschrijf de inhoud volledig in één of twee zinnen, zodat iemand met een schermlezer niets mist.
- Gebruik de afbeelding als `image` in het meta-blok als ze de kern van het artikel samenvat.
- Productfoto's van een fabrikant mogen, met "Afbeelding: <merk>" in het onderschrift. Eigen installatiefoto's enkel met toestemming van de klant.
