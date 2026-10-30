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
- Hoogstens een voornaam. Geen adres, geen straat en niets herkenbaars op de foto's (huisnummer, nummerplaat, gezichten zonder akkoord). Maak typeplaatjes, serienummers en QR-codes op de toestellen onleesbaar (vervagen).
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
     "facts": ["Merk", "8 kWh", "4,92 kWp"],
     "brands": ["zendure"],
     "setup": "zendure-solarflow-2400-ac-plus",
     "featured": true
   }
   ```
   - `brands`: de merken in de installatie, het belangrijkste eerst, met de slugs uit `brands` in `site.json` (`sigenergy`, `zendure`, `goodwe`, `solis`; andere merken in kleine letters, bv. `dyness`).
   - `setup`: een korte sleutel voor het type opstelling. Het blok "Uit onze realisaties" onderaan een productpagina toont per opstelling maar één kaart, zodat bezoekers verschillende opstellingen zien in plaats van drie keer dezelfde. Twee foto's van dezelfde installatie krijgen dezelfde sleutel.
   - `featured`: `false` houdt de installatie enkel op `/realisaties/` en uit het blok op de productpagina's. Zo kiezen we welke installaties in de kijker blijven als er veel gelijkaardige bijkomen.
   - `"wide": true` laat een liggende foto (bv. drie toestellen naast elkaar) op `/realisaties/` over twee kolommen lopen.
3. Is er voor dezelfde installatie een klantcase, voeg dan `"link": "/realisaties/<slug>/"` en `"link_label": "Lees de klantcase"` toe aan de kaart, zoals bij de Dyness- en Solis-kaarten.
4. Het blok "Uit onze realisaties" (`{{realisaties_<merk>}}`, max. drie kaarten, nieuwste eerst) vult zich vanzelf aan op de productpagina's van Sigenergy, Zendure en GoodWe/Solis. Noem nergens aantallen ("onze eerste", "al tien"): het is altijd een greep uit.
5. `python3 tools/make_image_variants.py`, daarna bouwen en publiceren met de skill `smartpeak-publiceren`.

## Klantcase

- Neem de goedgekeurde tekst zo letterlijk mogelijk over. Verzin geen citaten, situaties of details. Wat niet in de goedgekeurde tekst staat, laat je weg of vraag je na.
- Meta-blok met `slug`, `image`, `image_alt`, `schema_type: "Article"` en `published`.
- Link naar de productpagina's van de gebruikte toestellen, en zet bronnen bij technische beweringen.
- Laat de feiten controleren met de skill `smartpeak-feitencheck` voor je publiceert.
