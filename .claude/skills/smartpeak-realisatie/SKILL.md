---
name: smartpeak-realisatie
description: "Voeg een installatie toe aan /realisaties/ of maak een klantcase voor smartpeak.be, met foto's, toestemming en enkel de relevante gegevens. Gebruik wanneer Kevin foto's of een dossier van een installatie of klant doorstuurt."
---

# Realisatie of klantcase toevoegen

## Installatie of klantcase?

- **Installatie:** een kaart op `/realisaties/`, in `content/realisaties.json`. Kort: wat er geplaatst is en een paar kenmerken. Geen verhaal van de klant.
- **Klantcase:** een eigen pagina in `pages/realisaties/<slug>.html`, met een teaser bovenaan `pages/realisaties.html`. Enkel met een door de klant goedgekeurde tekst. Voorbeeld: `pages/realisaties/klantcase-mattias-dyness-solis.html`.

Twijfel je, vraag het Kevin.

## Toestemming en privacy

- Gebruik foto's en de naam van een klant enkel als Kevin bevestigt dat de klant akkoord ging. Vraag het als het niet in het dossier staat.
- Hoogstens een voornaam. Geen adres, geen straat en niets herkenbaars op de foto's (huisnummer, nummerplaat, gezichten zonder akkoord).
- Haal uit een dossier enkel wat relevant is voor de site: toestel, capaciteit, vermogen, aantal panelen en kWp. Laat prijzen, contactgegevens en technische meetwaarden van de klant weg.

## Installatie toevoegen

1. Zet de foto's in `assets/img/site/` als `installatie-<merk>-<model>.webp` (breedte ongeveer 1600 px).
2. Voeg bovenaan in `content/realisaties.json` een object toe:
   ```json
   {
     "title": "Merk en model",
     "text": "Eén of twee zinnen: wat er geplaatst is, met capaciteit en vermogen.",
     "image": "/assets/img/site/installatie-....webp",
     "alt": "Wat er op de foto te zien is, zonder persoonsgegevens",
     "facts": ["Merk", "8 kWh", "4,92 kWp"]
   }
   ```
3. Is er voor dezelfde installatie een klantcase, voeg dan `"link": "/realisaties/<slug>/"` en `"link_label": "Lees de klantcase"` toe aan de kaart, zoals bij de Dyness- en Solis-kaarten.
4. `python3 tools/make_image_variants.py`, daarna bouwen en publiceren met de skill `smartpeak-publiceren`.

## Klantcase

- Neem de goedgekeurde tekst zo letterlijk mogelijk over. Verzin geen citaten, situaties of details. Wat niet in de goedgekeurde tekst staat, laat je weg of vraag je na.
- Meta-blok met `slug`, `image`, `image_alt`, `schema_type: "Article"` en `published`.
- Link naar de productpagina's van de gebruikte toestellen, en zet bronnen bij technische beweringen.
- Laat de feiten controleren met de skill `smartpeak-feitencheck` voor je publiceert.
