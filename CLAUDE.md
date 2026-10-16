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

## Inhoudelijke regels

- Beloof nooit een terugverdientijd en noem geen prijzen in artikels of hulpgidsen.
- Sigenergy mag prominent aanwezig zijn, maar is nooit "onze voorkeur".
- Elke feitelijke bewering heeft een bron, liefst officieel (Fluvius, Vlaamse Nutsregulator, Synergrid, Vlaanderen.be, de fabrikant). Wat enkel een derde partij zegt, staat er als "volgens …".
- Geen stockfoto's. Gebruik infographics, officiële productbeelden met bronvermelding of eigen installatiefoto's met toestemming van de klant.
- Btw op thuisbatterijen is een open vraag bij Kevin en zijn boekhouder. Schrijf er niets over zonder zijn akkoord.
