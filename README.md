# smartpeak.be

Statische website van SmartPeak, gehost op GitHub Pages. Vervangt de WordPress-site op smartpeak.be.

## Lokaal bouwen

Enkel Python 3.10+ nodig, geen extra pakketten.

```bash
python3 build.py
python3 tools/check_site.py          # links, ankers, één h1, title/description/canonical
python3 -m http.server 8000 --directory _site
```

## Waar staat wat

| Pad | Inhoud |
|---|---|
| `site.json` | contactgegevens, navigatie, doorverwijzingen van oude URL's |
| `templates/layout.html` | header, footer, metadata (gedeeld door alle pagina's) |
| `templates/post-cta.html` | de groene oproepband onderaan artikels en pagina's (`{{cta}}`) |
| `pages/**/*.html` | handgeschreven pagina's; `path` in het meta-blok bepaalt de URL |
| `content/artikels/*.html` | artikels, gepubliceerd op `/artikels/<bestandsnaam>/` |
| `content/pages/*.html` | lange tekstpagina's (voorwaarden, privacy), op `/<bestandsnaam>/` |
| `content/realisaties.json` | de realisaties (titel, tekst, foto, kenmerken) |
| `content/wordpress/` | archief van de WordPress-import; wordt niet gepubliceerd |
| `assets/` | css, js, lettertype (Instrument Sans, OFL) en afbeeldingen |

Elk inhoudsbestand begint met een meta-blok:

```html
<!--meta
{
  "title": "Titel voor zoekmachines en de h1",
  "description": "Max. ~155 tekens, verschijnt in Google",
  "path": "/oplossingen/voorbeeld/",
  "section": "oplossingen",
  "summary": "Korte tekst voor de overzichtskaart",
  "order": 1
}
-->
```

`section` zet een pagina automatisch in het overzicht via `{{list_<section>}}` (bv. `{{list_oplossingen}}`, `{{list_hulp}}`). Artikels hebben `date` en optioneel `image` en `legacy_path` (oude WordPress-URL die doorverwijst).

Beschikbare tokens in pagina's: `{{email}}`, `{{phone}}`, `{{phone_href}}`, `{{hours}}`, `{{analysis_url}}`, `{{analysis_widget}}`, `{{cta}}`, `{{brand_logos}}`, `{{article_list}}`, `{{realisaties}}`, `{{reviews}}`, `{{reviews_short}}`.

Interne links schrijf je altijd als `/pad/`. De build zet er automatisch het juiste voorvoegsel voor, zodat de site ook werkt op `smartpeak-be.github.io/smartpeak-site/`.

## Afbeeldingen, SEO en toegankelijkheid

- **Nieuwe of gewijzigde afbeelding?** Draai lokaal `python3 tools/make_image_variants.py` (vraagt Pillow). Dat maakt kleinere `-w640.webp`-versies voor gsm's, deelafbeeldingen voor artikels in `assets/img/og/` en houdt de afmetingen bij in `content/image-sizes.json`. `build.py` zet daarmee zelf `width`/`height` en `srcset` op elke `<img>`.
- De build zet automatisch: het merk achter de titel als die dan nog onder 60 tekens blijft, `noindex` op de 404-pagina, brede tabellen in een scrollvak dat met het toetsenbord werkt, `lastmod` voor artikels in de sitemap en `preconnect` op pagina's met een widget.
- **Merklogo's op de startpagina:** zet het officiële logo als `assets/img/merken/<slug>.svg` (of `.webp`/`.png`), met de slugs uit `brands` in `site.json`. Zolang er geen bestand is, toont de tegel de merknaam.
- **Toegankelijkheid:** we werken naar WCAG 2.2 AA. De verklaring staat in `content/pages/toegankelijkheid.html`; pas de datum en de bekende beperkingen aan na een nieuwe controle. De knop "Lees voor" (in `assets/js/site.js`) gebruikt de spraak van de browser en verschijnt enkel als er een Nederlandse stem is.

## Koppelingen met de batterijtool

- De verbruiksanalyse draait in de pagina zelf via `assets/js/widgets/lead-wizard.js` van [battery-roi-tool](https://github.com/smartpeak-be/battery-roi-tool) (`analysis_widget_url` in `site.json`, token `{{analysis_widget}}`). Zelfde berekening, lead en resultaatmail als `lead.html`, zonder keys. De stijl volgt de site via de `--spa-*` variabelen in `assets/css/site.css`. Zonder JavaScript valt ze terug op een link naar `lead.html` (`analysis_url`).
- Testen: de workflow "Test website forms against lead rules" controleert contactformulier en analyse tegen de Firestore-regels in de emulator (geen echte leads). "Live test battery analysis" in modus `embed-check` controleert de gepubliceerde site tot net voor het verzenden.
- De reviews komen live uit Firestore via `assets/js/widgets/reviews.js` van dezelfde tool (`reviews_widget_url`). Enkel reviews met status `published` en toestemming voor de website verschijnen. De stijl wordt in `assets/css/site.css` (sectie "Reviews widget") afgestemd op de site.

## Publiceren

Elke push naar `main` bouwt, controleert en publiceert via `.github/workflows/pages.yml` (één korte job). Wijzigingen aan enkel README of het WordPress-archief starten geen deploy.

Zolang de site niet op `https://smartpeak.be` draait, krijgt elke pagina `noindex` en blokkeert `robots.txt` alles. Zo concurreert de testversie niet met de huidige site in Google. Dat schakelt vanzelf om zodra het domein ingesteld is.

Op het echte domein weigert `robots.txt` de AI-bots die enkel trainingsdata verzamelen (GPTBot, ClaudeBot, Google-Extended, Applebot-Extended, meta-externalagent, CCBot, Bytespider). Zoek- en antwoordbots zoals OAI-SearchBot, ChatGPT-User, Claude-SearchBot en PerplexityBot blijven toegelaten, zodat SmartPeak als bron in AI-antwoorden kan verschijnen. Google-Extended blokkeren heeft geen invloed op Google Search. De namen van die bots veranderen soms: kijk de lijst in `build.py` (`training_bots`) een keer per jaar na. robots.txt is een afspraak, geen slot.

## Omschakelen van WordPress naar GitHub Pages

1. **Pages aanzetten**: Settings → Pages → Source: *GitHub Actions*. GitHub Pages op een private repo vraagt een betalend GitHub-plan voor de organisatie; anders de repo publiek maken (zoals `bloxit-be-site`).
2. **Testversie nakijken** op `https://smartpeak-be.github.io/smartpeak-site/`.
3. **Custom domain**: Settings → Pages → Custom domain `smartpeak.be`, daarna *Enforce HTTPS* aanvinken zodra het certificaat klaar is. Start daarna de workflow *Deploy website to GitHub Pages* één keer opnieuw (Actions → Run workflow): pas dan bouwt de site met `https://smartpeak.be` en verdwijnt de `noindex`. Het domein eerst verifiëren onder de organisatie-instellingen (Settings → Pages → Verified domains) voorkomt dat iemand anders het claimt.
4. **DNS bij de registrar**, enkel deze records aanpassen:
   - `A` voor `smartpeak.be` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
   - `AAAA` (optioneel) → `2606:50c0:8000::153`, `2606:50c0:8001::153`, `2606:50c0:8002::153`, `2606:50c0:8003::153`
   - `CNAME` voor `www` → `smartpeak-be.github.io`
   - **MX-, SPF-, DKIM- en andere mailrecords niet aanraken**, anders stopt de mail op info@smartpeak.be.
5. **Na de omschakeling**: in Google Search Console de sitemap `https://smartpeak.be/sitemap.xml` indienen.
6. **Pas daarna WordPress uitzetten.** De batterijtool en reviews draaien los van WordPress en blijven werken.

### Oude URL's

Alle bestaande WordPress-adressen blijven werken. Hernoemde pagina's krijgen een doorverwijzing (zie `redirects` in `site.json` en `legacy_path` in de artikels), bijvoorbeeld `/about/` → `/over-ons/`, `/blog/` → `/artikels/`, `/thuisbatterij-rendabel-berekening/` → `/werkwijze/`. GitHub Pages kent geen echte 301-redirects; we gebruiken een directe meta-refresh met canonical, wat Google als verhuisd behandelt.

## WordPress-inhoud opnieuw ophalen

De Action *Import WordPress content* (handmatig te starten) haalt posts, pagina's en afbeeldingen van smartpeak.be op in `content/wordpress/`. `python3 tools/convert_wordpress.py` (vraagt Pillow) zet die om naar `content/`; dat overschrijft handmatige aanpassingen, dus enkel gebruiken voor de omschakeling.
