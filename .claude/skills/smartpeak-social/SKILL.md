---
name: smartpeak-social
description: "Maak een social-pakket (carrousel, tekst voor Facebook en Instagram) bij een pagina van smartpeak.be en plan het in via Metricool. Gebruik bij elke nieuwe pagina, en wanneer posts voor bestaande inhoud gepland moeten worden."
---

# Sociale media voor SmartPeak

SmartPeak post op een Facebook-pagina en een Instagram-account (`smartpeak.be`), via het merk SmartPeak in Metricool. LinkedIn en TikTok komen later.

## 1. Het social-pakket

Elke nieuwe pagina op de site (artikel, hulpgids, realisatie) krijgt een social-pakket, in dezelfde pull request. Zo zijn de beelden online wanneer de post verschijnt, zonder extra deploy. Het pakket staat niet zichtbaar op de site.

- `content/social/<slug>.json`: de slides en de teksten.
- `assets/img/social/<slug>-<n>.jpg`: de beelden, gemaakt met `python3 tools/social_slides.py <slug>`. Na publicatie staan ze op `https://smartpeak.be/assets/img/social/<slug>-<n>.jpg`.

```json
{
  "page": "/artikels/<slug>/",
  "slides": [ ... zie tools/social_slides.py ... ],
  "facebook": "tekst voor Facebook",
  "instagram": "tekst voor Instagram",
  "first_comment": "Lees meer: https://smartpeak.be/artikels/<slug>/"
}
```

Kijk naar `content/social/energiecontract-vergelijken-besparen.json` als voorbeeld.

## 2. Beelden

- Carrousel van 5 tot 8 slides, staand 4:5 (1080 × 1350). Carrousels worden bewaard en doorgestuurd, en dat weegt volgens Instagram zwaar ([Social Media Today, jan 2025](https://www.socialmediatoday.com/news/instagram-shares-algorithm-insights-2025/738034/)).
- Slide 1 is de haak: een vraag of belofte in een paar woorden. De laatste slide verwijst naar de pagina op smartpeak.be.
- Eén idee per slide, kort. Meldt het script "TE VEEL TEKST", kort dan in.
- Cijfers alleen met hun bron onderaan de slide, zoals op de site.
- Eigen installatiefoto's mogen enkel met toestemming van de klant. Geen stockfoto's en geen AI-beelden die echt lijken: sinds 2 augustus 2026 moet je die volgens de Europese AI-verordening (artikel 50) als AI melden. Onze infographics en slides zijn geen AI-beelden; zet `isAiGenerated` op `false`.
- Een Reel (video 9:16) haalt meer niet-volgers, maar vraagt echt beeld. Maak er enkel een als Kevin video aanlevert.

## 3. Teksten

**Facebook**
- Eerste zin: de vraag of het nut, want de rest wordt ingeklapt.
- Drie tot zes korte alinea's, gewone woorden, je-vorm.
- Eindig met de link: "Lees meer: https://smartpeak.be/...". Meta test een limiet op links in posts van pagina's ([TechCrunch, dec 2025](https://techcrunch.com/2025/12/17/facebook-is-testing-a-link-posting-limit-for-professional-accounts-and-pages)); zet de link daarom ook in `first_comment`.

**Instagram**
- Zelfde haak, korter. Links in de tekst zijn niet klikbaar: schrijf "Link in bio" en zet het adres als tekst erbij.
- Drie tot vijf gerichte hashtags, nooit meer dan vijf ([Social Media Today, dec 2025](https://www.socialmediatoday.com/news/instagram-implements-new-limits-on-hashtag-use/808309/)). Bijvoorbeeld `#thuisbatterij #capaciteitstarief #zonnepanelen #OostVlaanderen`.
- Schrijf natuurlijke zinnen met de woorden waarop mensen zoeken (thuisbatterij, capaciteitstarief, Fluvius).

**Voor allebei**
- De tekst zegt zelf iets. Beschrijf nooit de post ("In de slides: …", "Bewaar de carrousel", "Swipe"): geef de kern in gewone zinnen, met de belangrijkste feiten uit de slides.
- Dezelfde regels als op de site: geen prijzen van installaties, geen terugverdientijd, geen beloftes van besparing, Sigenergy nooit "onze voorkeur", elke bewering met bron.
- Een post zegt niets wat de pagina niet zegt.
- Bron in de post enkel bij cijfers, bedragen en regels ("Volgens de Vlaamse Nutsregulator kost 1 kW …"). Algemene vakkennis schrijf je in eigen naam, zonder "volgens …" ("Bidirectioneel laden staat in België nog in een vroege fase."): de bron staat in het artikel. Anders lijkt het alsof SmartPeak het zelf niet weet.
- Reviews enkel als ze echt zijn en de klant toestemming gaf voor sociale media. Toon niet enkel de beste reviews als je de indruk wekt dat het alle reviews zijn ([FOD Economie, 2023](https://news.economie.fgov.be/231090-online-reviews-voor-een-5-sterren-betrouwbaarheid/)).
- Betaalt een fabrikant voor een post of krijgt SmartPeak er iets voor, dan is het label "betaald partnerschap" nodig.

## 4. Reviews

Reviews komen uit de reviewtool van battery-roi-tool. De gepubliceerde reviews zijn publiek leesbaar:

```
GET https://firestore.googleapis.com/v1/projects/smartpeak-projects/databases/(default)/documents/publicReviews
```

- Gebruik een review enkel als `consentSocials` er `true` is. Ontbreekt het veld (reviews die gepubliceerd werden voor die toestemming publiek werd), vraag Kevin dan om de review opnieuw te publiceren in reviewbeheer, of om bevestiging per review.
- Neem de naam zoals de klant hem koos (`displayName`), de sterren en `solutionSummary.publicLabel`. Nooit meer: geen woonplaats, geen foto's tenzij `reviewPhotosPublic` `true` is.
- Citeer de review letterlijk. Is ze te lang voor een slide, kort ze in met "…" zonder de betekenis te veranderen, en zet de volledige tekst in de post.
- Een review is nooit kaal "de review en klaar". Zet er een eigen woord van SmartPeak omheen: een dank voor het vertrouwen, wat er geplaatst werd en waarom die oplossing bij die woning paste, en een uitnodiging voor wie twijfelt. Bijvoorbeeld: "Fijn om zo'n reactie te krijgen. Bedankt voor het vertrouwen! Hier plaatsten we …".
- Eén review per post, hoogstens één review-post per twee weken, zodat het geen reclameblok wordt. Toon niet enkel de beste reviews met de indruk dat het alle reviews zijn.
- Slides: een `cover` ("Wat onze klanten zeggen" of de essentie van de review), een `review`-slide (`rating`, `quote`, `name`, `label`), eventueel een `text`-slide over de installatie, en een `cta` naar `smartpeak.be/realisaties`.
- Bestand: `content/social/review-<document-id>.json`, met `"page": "/realisaties/"`.

## 5. Inplannen in Metricool

1. `getBrandSettings`: de `blogId` van SmartPeak en de tijdzone (Europe/Brussels).
2. Controleer dat elk beeld online staat (`https://smartpeak.be/assets/img/social/...` geeft een afbeelding terug). Anders: eerst publiceren.
3. Kijk wat er al gepland staat (`getScheduledPosts`) en wat al gepost is (analytics, metrieken `FBPO02`, `FBPO03` en `IGPO02`, `IGPO03`), zodat je geen onderwerp dubbel plaatst.
4. Ritme: twee à drie posts per week, verspreid. Volgens metingen van Buffer werken weekdagen rond 9 uur en rond 18 uur het best, donderdag het sterkst; vrijdag en zaterdag zwakker. Gebruik `getBestTimeToPostByNetwork` zodra er genoeg eigen gegevens zijn.
5. `createScheduledPost` per kanaal, minstens 24 uur vooruit, met `autoPublish: true`:
   - Facebook: `facebookData.type` `POST`, de beelden in `media`, `firstCommentText` met de link.
   - Instagram: `instagramData.type` `POST` (een carrousel is een POST met meerdere beelden), `isAiGenerated: false`.
6. **Redactie na het inplannen.** Laat de agent `smartpeak-social-redactie` de ingeplande posts nalezen in Metricool, los van wie ze schreef. Verwerk de opmerkingen met `updateScheduledPost` (een update geeft de post een nieuwe `id`, de `uuid` blijft) en in het JSON-bestand, en laat opnieuw nalezen tot alles in orde is.
7. Meld Kevin per post: kanaal, dag en uur, en de `plannerUrl`, en wat de redactie aanpaste. Hij kan in Metricool nog alles aanpassen of schrappen.

Publiceer nooit meteen, tenzij Kevin dat uitdrukkelijk vraagt voor een bepaalde post.

## 6. Wat we leren

- Kijk maandelijks naar bereik, bewaren en delen per post (Metricool-analytics). Meld Kevin welke onderwerpen en vormen het best werken, en pas het plan aan.
- Posts die over een installatie gaan en nog niet als realisatie op de site staan: stel Kevin voor ze toe te voegen (skill `smartpeak-realisatie`), met toestemming van de klant.
