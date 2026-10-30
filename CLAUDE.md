# CLAUDE.md

Context voor Claude (Claude Code, de SmartPeak-agent in de Claude Console of een andere sessie) die aan deze repository werkt.

## Wat dit is

De statische website van SmartPeak, smartpeak.be: een Belgisch bedrijf (Kevin en Ruben, LED's Repair) dat thuisbatterijen plaatst, vooral Sigenergy SigenStor, daarnaast Zendure SolarFlow AC+, GoodWe- en Solis-omvormers en andere merken waar het past. Geen Marstek meer.

- Gebouwd met `build.py` (Python-standaardbibliotheek), gepubliceerd via GitHub Pages vanaf `main`.
- Taal van de site: Nederlands (Vlaanderen), je-vorm.
- De verbruiksanalyse en de reviews zijn widgets uit [battery-roi-tool](https://github.com/smartpeak-be/battery-roi-tool). Ze werken bewust zonder keys. Voeg nooit API-keys of geheimen toe aan deze repo.

Lees eerst `README.md`: daar staat waar alles staat, het meta-blok, de tokens en hoe je bouwt.

## Werkwijze

- Werk op een aparte branch. Een push naar `main` publiceert meteen en kost GitHub Actions-minuten. Bundel wijzigingen en publiceer één keer.
- Commits staan op naam van Kevin: auteur `Kevin <kevin@bloxit.be>`, committer `Claude <noreply@anthropic.com>`. Overschrijf nooit de geschiedenis van `main` (geen force-push) zonder Kevins uitdrukkelijk akkoord.
- Testen moeten zinvol zijn, niet elk detail. Draai altijd `python3 build.py` en `python3 tools/check_site.py`.
- Kevins ideeën zijn vaak brainstorm. Toets ze aan de praktijk en de regels in België voor je bouwt, en zeg het als iets niet klopt.
- De skills in `.claude/skills/` beschrijven de vaste werkwijzen: artikels en hulpgidsen schrijven, infographics maken, feiten controleren, realisaties toevoegen en publiceren.

## Het team

Wie aan deze site werkt, is de verantwoordelijke en levert een pull request af die klaar is om te mergen. Voor deelwerk zijn er subagents in `.claude/agents/` (in de Claude Console dezelfde teamleden, zie `agent/README.md`):

- `smartpeak-onderzoeker`: onderzoek naar een onderwerp, regels, cijfers of zoekvragen.
- `smartpeak-grafisch`: infographics maken of aanpassen.
- `smartpeak-feitencontroleur`: altijd voor een nieuwe of inhoudelijk aangepaste tekst of infographic naar Kevin gaat. Geef enkel de bestanden mee, niet je redenering.
- `smartpeak-kwaliteit`: bouwen, controles en schermafbeeldingen voor een pull request.

Schrijven doe je zelf, zodat de site één stem houdt. Kleine wijzigingen doe je zonder team. Pas de instructies van de agents aan in `agent/rollen/` en draai daarna `python3 tools/build_agents.py`.

## Inhoudelijke regels

- Beloof nooit een terugverdientijd en noem geen prijzen van SmartPeak-installaties in artikels of hulpgidsen. Bedragen uit officiële bronnen (bijvoorbeeld het besparingspotentieel volgens de CREG) mogen wel, met bron. Enige uitzondering: de richtprijzen in `content/artikels/wat-kost-een-thuisbatterij.html` (gemiddelden van Kevin, inclusief 21% btw). Pas ze enkel aan met zijn cijfers en zet de datum mee.
- Zet het plaatsbezoek niet in de verf: geen "gratis plaatsbezoek" in oproepen, knoppen of telkens opnieuw in teksten. We komen langs wanneer een plaatsing concreet wordt, en dat beoordelen we zelf. Dat we langskomen voor we een offerte maken, mag je wel uitleggen waar het over de werkwijze gaat.
- Keuring en melding: SmartPeak vraagt de keuring aan, het keuringsorganisme plant ze met de klant. Het aanmelden bij Fluvius doet de klant zelf (gids: `/hulp/thuisbatterij-aanmelden-fluvius/`). Schrijf nergens dat wij de melding regelen. Hulp als het vastloopt kan, maar presenteer dat niet als standaard of gratis service.
- Sigenergy mag prominent aanwezig zijn, maar is nooit "onze voorkeur".
- Elke feitelijke bewering heeft een bron, liefst officieel (Fluvius, Vlaamse Nutsregulator, Synergrid, Vlaanderen.be, de fabrikant). Wat enkel een derde partij zegt, staat er als "volgens …".
- Geen stockfoto's. Gebruik infographics, officiële productbeelden met bronvermelding of eigen installatiefoto's met toestemming van de klant.
- Btw op thuisbatterijen is een open vraag bij Kevin en zijn boekhouder. Schrijf er niets over zonder zijn akkoord.
