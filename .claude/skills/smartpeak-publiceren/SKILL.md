---
name: smartpeak-publiceren
description: "Bouw, controleer en publiceer wijzigingen aan smartpeak.be via een branch en pull request, zuinig met GitHub Actions. Gebruik telkens je wijzigingen aan de site online wil zetten."
---

# Publiceren

Een push naar `main` publiceert de site meteen via `.github/workflows/pages.yml`. Elke run kost GitHub Actions-minuten van Kevin. Werk dus op een branch, bundel je wijzigingen, en laat Kevin `main` bijwerken door een pull request te mergen, of merge zelf als hij daar uitdrukkelijk om vraagt.

## 1. Branch

```bash
git checkout -b <korte-naam>     # bijvoorbeeld artikel-netcongestie
```

## 2. Bouwen en controleren

```bash
python3 tools/make_image_variants.py           # enkel als er afbeeldingen bij kwamen of veranderden
SITE_URL=https://smartpeak.be python3 build.py
SITE_URL=https://smartpeak.be python3 tools/check_site.py   # moet "0 problem(s)" geven
```

Controleer daarna in de gebouwde HTML (`_site/<pad>/index.html`):
- `<title>` niet langer dan 60 tekens, `meta description` tussen 120 en 155 tekens, `robots` op `index, follow`;
- één `h1` en een logische volgorde van de koppen.

Bekijk de pagina zelf met Playwright, op 390 px en op 1280 px breed. Let erop dat niets breder is dan het scherm en dat de afbeeldingen laden:

```bash
python3 -m http.server 8000 --directory _site &   # bouw daarvoor zonder SITE_URL: python3 build.py
```

Neem schermafbeeldingen, bekijk ze en los op wat er misloopt. Bouw daarna opnieuw met `SITE_URL=https://smartpeak.be` als je verder wil.

## 3. Commit

- Auteur: Kevin. Committer: Claude.
  ```bash
  git -c user.name=Claude -c user.email=noreply@anthropic.com \
    commit --author="Kevin <kevin@bloxit.be>" -m "Korte titel in het Engels" -m "Waarom, in één of twee zinnen."
  ```
- Commit `_site/` nooit: het staat in `.gitignore`.
- Geen API-keys, tokens of persoonsgegevens van klanten in de repo.

## 4. Push en pull request

- Push je branch: `git push -u origin <branch>`. Lukt dat niet met git, gebruik dan de GitHub-tools (branch, bestanden, pull request).
- Open een pull request naar `main`. Zet erin wat er verandert, de link naar de pagina zoals ze live zal staan, en wat Kevin zelf moet nakijken.
- Merge enkel zelf als Kevin daar uitdrukkelijk om vraagt, en force-push nooit naar `main`. Elke merge start één deploy.
- Wijzigingen enkel aan `README.md`, `CLAUDE.md`, `.claude/` of `agent/` starten geen deploy.

## 5. Na de merge

- Wacht tot de workflow "Deploy website to GitHub Pages" klaar is en open de live pagina op `https://smartpeak.be/...` om te controleren.
- Raakte je het contactformulier of de widgets van de batterijtool, laat dan de workflow "Test website forms against lead rules" draaien. Enkel dan: die run kost ook minuten.
