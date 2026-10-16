# De SmartPeak-website-agent in de Claude Console

Deze map bevat alles om een agent in de Claude Console (Claude Managed Agents) te maken die aan smartpeak.be werkt.

| Bestand | Wat |
|---|---|
| `smartpeak-website-agent.md` | De agent: model, systeemprompt, tools, GitHub-koppeling en skills |
| `environment.yaml` | De omgeving waarin de agent draait |
| `../CLAUDE.md` | Context over de site, die de agent bij elke start leest |
| `../.claude/skills/` | De vaste werkwijzen. Ze worden automatisch geladen als de repository aan een sessie gekoppeld is |

De skills staan in de repository zelf. Pas je er een aan en merge je die wijziging, dan gebruikt de volgende sessie meteen de nieuwe versie. Je hoeft niets opnieuw op te laden.

## Eenmalig instellen

### 1. Een GitHub-token maken

Op GitHub: **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.

- **Resource owner:** `smartpeak-be`
- **Repository access:** enkel `smartpeak-site` (en eventueel `battery-roi-tool`, alleen lezen)
- **Permissions:** Contents: *Read and write*, Pull requests: *Read and write*. Verder niets.
- Kies een vervaldatum, bijvoorbeeld een jaar, en zet een herinnering om het token te vernieuwen.

Bewaar het token in je wachtwoordbeheerder. Zet het nergens in de repository.

### 2. De omgeving maken

Console → **Managed Agents → Environments → New environment**:

- **Name:** `smartpeak-website`
- **Type:** Cloud
- **Networking:** *Unrestricted*. De agent moet vrij kunnen zoeken voor zijn onderzoek. Met *Limited* werken zoeken en pagina's lezen enkel voor sites die je vooraf opgeeft.
- **Packages → pip:** `pillow`

### 3. De agent maken

Console → **Managed Agents → Agents → New agent**:

- **Name:** `SmartPeak website`
- **Model:** Claude Opus 5.5, effort *high*
- **System prompt:** kopieer alles onder de tweede `---` uit `smartpeak-website-agent.md`
- **Tools:** de standaard agent-toolset (bash, bestanden, web search, web fetch)
- **MCP server:** GitHub, `https://api.githubcopilot.com/mcp/`. Koppel je GitHub-account wanneer de Console daarom vraagt. Daarmee kan de agent pull requests openen.
- **Skills:** de Anthropic-skill *pdf*, om pdf's te lezen die je doorstuurt (klantcases, datasheets)

Werk je liever met de `ant`-CLI, dan maakt `ant apply agent/smartpeak-website-agent.md` en `ant apply agent/environment.yaml` hetzelfde aan.

## Een sessie starten

Start een sessie met de agent en de omgeving, en koppel de repository als **GitHub repository**:

- **URL:** `https://github.com/smartpeak-be/smartpeak-site`
- **Mount path:** `/workspace/smartpeak-site`
- **Token:** het token uit stap 1
- **Branch:** `main`

Geef daarna je opdracht, bijvoorbeeld:

- "Schrijf een hulpgids over het koppelen van de HomeWizard P1-meter aan een Zendure."
- "Hier zijn drie foto's en het dossier van een installatie bij Joeri. Voeg ze toe aan de realisaties."
- "Zoek welke onderwerpen rond thuisbatterijen nu veel gezocht worden en stel vijf artikels voor."

De agent werkt op een branch en opent een pull request. Jij bekijkt die op GitHub en klikt **Merge**. Pas dan gaat de wijziging online.

## Goed om te weten

- **Kosten:** sessies lopen via je API-account in de Console. Ze worden apart van een Claude-abonnement aangerekend, per gebruik.
- **Veiligheid:** de agent kan alles wat het token toelaat. Daarom heeft het token enkel toegang tot deze repository, en gaat er niets online zonder dat jij de pull request merget.
- **Beta:** Managed Agents is nog in beta. Menu's en namen in de Console kunnen nog veranderen.

Meer uitleg: [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview), [Build in Console](https://platform.claude.com/docs/en/managed-agents/onboarding), [GitHub koppelen](https://platform.claude.com/docs/en/managed-agents/github), [Skills](https://platform.claude.com/docs/en/managed-agents/skills).
