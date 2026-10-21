---
name: smartpeak-artikel
description: "Schrijf of herwerk een artikel (content/artikels/) of hulpgids (pages/hulp/) voor smartpeak.be, met SEO-meta, bronnen, interne links en Belgische context. Gebruik bij elke nieuwe of aangepaste tekst op de site."
---

# Artikel of hulpgids schrijven

## 1. Kies het soort pagina

| Soort | Waar | Meta |
|---|---|---|
| Artikel (nieuws, uitleg, trends) | `content/artikels/<slug>.html` → `/artikels/<slug>/` | `title`, `description`, `date`, `image`, `image_alt`, optioneel `modified`, `legacy_path` |
| Hulpgids (stappen, instellingen, "hoe doe ik") | `pages/hulp/<slug>.html` | `title`, `card_title`, `description`, `summary`, `section: "hulp"`, `order`, `path`, `slug`, `image`, `image_alt`, `schema_type: "Article"`, `published` |

Bekijk een bestaand voorbeeld van hetzelfde soort voor de opbouw: `pages/hulp/sigenstor-instellen-mysigen.html`, `content/artikels/omvormer-valt-uit-zonnige-dagen.html`.

- **title:** maximaal 60 tekens samen met " | SmartPeak". De build laat het achtervoegsel weg als het te lang wordt, maar kies liever een korte titel.
- **description:** 120 tot 155 tekens, concreet, met de zoekterm.
- **date / published:** de echte publicatiedatum. Een tekst mag niet verwijzen naar iets dat op die datum nog niet gebeurd was.
- **image:** de belangrijkste infographic (zie skill `smartpeak-infographic`). `slug` zorgt dat er een deelafbeelding gemaakt wordt.

## 2. Onderzoek eerst

- Zoek de actuele stand: regels en bedragen veranderen. Gebruik officiële bronnen eerst (Fluvius, Vlaamse Nutsregulator, Synergrid, Vlaanderen.be, FOD Economie, de handleiding of wiki van de fabrikant).
- Voor zoekintentie: kijk welke vragen mensen echt stellen (Google-suggesties, fora, concurrenten) en beantwoord die.
- Inspiratiesites van Kevin: haal er de vragen en de structuur uit, nooit tekst. Neem geen prijzen over.
- Bestaande artikels bevatten al gecontroleerde feiten met bronnen. Zie `../smartpeak-feitencheck/references/onderwerpen.md`.

## 3. Schrijfstijl

- Nederlands zoals in Vlaanderen, je-vorm, korte zinnen, concreet. Geen hype en geen marketingtaal.
- Begin met het antwoord op de vraag, daarna de uitleg.
- Elke afbeelding, tabel en tekst vertelt iets anders. Laat een tabel, een infographic en de tekst eronder **niet** hetzelfde herhalen. Een `figcaption` die enkel herhaalt wat op de afbeelding staat, laat je weg. De `alt`-tekst beschrijft wel de volledige inhoud van de afbeelding.
- Benoem Belgische aandachtspunten waar ze spelen: het capaciteitstarief (gemiddelde van de maandpieken over 12 maanden, minimum 2,5 kW), 800 W op een stopcontact tegenover een eigen kring, aanmelden bij Fluvius, keuring, Bebat, de Synergrid-lijsten (C10/26, plug-and-play).
- Geen terugverdientijd, geen prijzen van onze installaties (bedragen uit officiële bronnen mogen, met bron). Sigenergy nooit "onze voorkeur".
- Een hulpgids is nuttig voor wie het product al heeft, en laat wie twijfelt zien wat het kan.

## 4. Vaste onderdelen

- Inline links naar de bronnen bij elke bewering, met `rel="noopener"` op externe links.
- Interne links naar de productpagina (`/oplossingen/...`), verwante artikels, `/batterij-iets-voor-mij/#analyse` en `/contact/`.
- Onderaan een `<h3>Bronnen</h3>` met een lijst.
- Een hulpgids eindigt met wat SmartPeak doet bij een installatie ("Plaatsen wij je ...?").
- Afbeeldingen in de tekst: `<figure><a href="..." class="figure-zoom"><img src="..." alt="..." loading="lazy" decoding="async"></a></figure>`, zodat je op een gsm kan inzoomen.
- Brede tabellen hoeven geen extra code: de build zet ze in een scrollvak.

## 5. Koppel de pagina

- Hulpgids: verschijnt vanzelf in `/hulp/` via `section`. Pas de `description` van `pages/hulp/index.html` aan als het onderwerp er nieuw is.
- Zet een korte verwijzing op de bijhorende productpagina of in een verwant artikel.

## 6. Daarna

1. Infographics maken: skill `smartpeak-infographic`.
2. Feiten laten controleren: skill `smartpeak-feitencheck`. Verwerk de opmerkingen.
3. Social-pakket: skill `smartpeak-social`, in dezelfde pull request (korte teksten en carrousel, niet zichtbaar op de site, met een link naar de pagina). Laat het mee controleren door de feitencontrole.
4. Publiceren: skill `smartpeak-publiceren`.
5. Meld Kevin wat hij zelf moet nakijken (bijvoorbeeld namen in een app die je niet kon zien).
