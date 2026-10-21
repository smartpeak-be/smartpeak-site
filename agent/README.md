# De SmartPeak-agents

Twee verantwoordelijke agents, elk met een klein team:

- **SmartPeak website** zorgt voor smartpeak.be, van de vraag van Kevin tot een pull request die klaar is om te mergen.
- **SmartPeak social** maakt posts voor Facebook en Instagram uit de inhoud van de site en plant ze in via Metricool.

De teamleden zijn gedeeld: de feitencontroleur en de grafische agent werken voor allebei. Alles bestaat voor de Claude Console (Claude Managed Agents) en voor Claude Code.

| Agent | Model | Taak |
|---|---|---|
| `smartpeak-website` | Opus 5.5, effort high | De verantwoordelijke: plant, schrijft, verdeelt werk, controleert en opent de pull request |
| `smartpeak-onderzoeker` | Sonnet 5.5, effort medium | Onderzoekt een onderwerp in officiële Belgische bronnen en levert een nota met bronnen |
| `smartpeak-feitencontroleur` | Opus 5.5, effort high | Controleert onafhankelijk elke bewering voor publicatie |
| `smartpeak-grafisch` | Sonnet 5.5, effort high | Maakt infographics in de huisstijl en rendert ze |
| `smartpeak-kwaliteit` | Haiku 5.5 | Bouwt, draait de controles en bekijkt de pagina's op gsm en computer |
| `smartpeak-social` | Opus 5.5, effort high | Verantwoordelijke voor sociale media: posts en carrousels, inplannen via Metricool. Team: feitencontroleur en grafisch |

Waarom deze modellen: schrijven, coördineren, publiceren onder de naam SmartPeak en de onafhankelijke feitencontrole vragen het beste oordeel, dus Opus. Onderzoek en grafisch werk zijn breed maar routineus, dus Sonnet. De technische controle is mechanisch werk, dus Haiku, het goedkoopst. Een model aanpassen doe je op één plaats (zie hieronder).

## Waar staat wat

| Pad | Wat |
|---|---|
| `agent/rollen/<agent>.md` | De instructies van elke agent. **Pas ze hier aan.** |
| `tools/build_agents.py` | Model, effort, tools en skills per agent. Schrijft de bestanden hieronder. |
| `agent/console/*.md` | De agents voor de Claude Console (gegenereerd) |
| `.claude/agents/*.md` | De subagents voor Claude Code (gegenereerd) |
| `agent/environment.yaml` | De omgeving waarin de Console-agents draaien |
| `../CLAUDE.md` en `../.claude/skills/` | Context en vaste werkwijzen, voor alle agents |

Na een wijziging in `agent/rollen/` of in `tools/build_agents.py`:

```bash
python3 tools/build_agents.py           # schrijft agent/console/ en .claude/agents/
python3 tools/build_agents.py --check   # controleert of alles bijgewerkt is
```

Voor de Console voer je daarna `ant apply` opnieuw uit (zie stap 3). Claude Code gebruikt de nieuwe versie zodra de wijziging gemerged is.

## In Claude Code

Niets te installeren. Open de repository in Claude Code of in een sessie van de Claude-app: de hoofdsessie is de verantwoordelijke voor de website (via `CLAUDE.md`) en roept de subagents uit `.claude/agents/` zelf op. Je kan er ook één uitdrukkelijk vragen, bijvoorbeeld "laat de feitencontroleur dit artikel nakijken" of "laat de social-agent posts maken voor het nieuwe artikel". De social-agent gebruikt de Metricool-connector van je Claude-account. Dit loopt via je Claude-abonnement.

## In de Claude Console: eenmalig instellen

### 1. Een GitHub-token maken

Op GitHub: **Settings → Developer settings → Personal access tokens → Fine-grained tokens → Generate new token**.

- **Resource owner:** `smartpeak-be`
- **Repository access:** enkel `smartpeak-site` (en eventueel `battery-roi-tool`, alleen lezen)
- **Permissions:** Contents: *Read and write*, Pull requests: *Read and write*. Verder niets.
- Kies een vervaldatum, bijvoorbeeld een jaar, en zet een herinnering om het token te vernieuwen.

Bewaar het token in je wachtwoordbeheerder. Zet het nergens in de repository.

### 2. De omgeving maken

```bash
ant apply agent/environment.yaml
```

Of in de Console: **Managed Agents → Environments → New environment**, naam `smartpeak-website`, type *Cloud*, networking *Unrestricted*, pip-pakketten `pillow` en `playwright`.

### 3. De teams maken

```bash
ant apply agent/console/smartpeak-website.md
ant apply agent/console/smartpeak-social.md
```

`ant apply` maakt of werkt de vier teamleden bij waarnaar de verantwoordelijke verwijst en koppelt ze aan hem. Doe je het liever met de hand in de Console, maak dan eerst de vier teamleden aan (model en systeemprompt uit hun bestand in `agent/console/`, standaard agent-toolset). Maak daarna de verantwoordelijke aan met de GitHub-MCP-server (`https://api.githubcopilot.com/mcp/`), de Anthropic-skill *pdf* en onder *Multiagent* de vier teamleden. Koppel je GitHub-account wanneer de Console daarom vraagt.

Voor **SmartPeak social** koppel je ook Metricool (`https://ai.metricool.com/mcp`). De Console vraagt je in te loggen bij Metricool; die toegang komt in een vault en geef je mee bij het starten van een sessie.

Een teamlid kan zelf geen teamleden hebben: er is maar één niveau. Alle agents delen dezelfde werkplek, maar elk heeft een eigen gesprek.

## Een sessie starten in de Console

Start een sessie met **SmartPeak website** en de omgeving `smartpeak-website`, en koppel de repository als **GitHub repository**:

- **URL:** `https://github.com/smartpeak-be/smartpeak-site`
- **Mount path:** `/workspace/smartpeak-site`
- **Token:** het token uit stap 1
- **Branch:** `main`

De skills in `.claude/skills/` worden bij de start van de sessie automatisch geladen. Geef daarna je opdracht, bijvoorbeeld:

- "Schrijf een hulpgids over het koppelen van de HomeWizard P1-meter aan een Zendure."
- "Hier zijn drie foto's en het dossier van een installatie bij Joeri. Voeg ze toe aan de realisaties."
- "Zoek welke onderwerpen rond thuisbatterijen nu veel gezocht worden en stel vijf artikels voor."

De agent werkt op een branch en opent een pull request. Jij bekijkt die op GitHub en klikt **Merge**, of je vraagt hem uitdrukkelijk om te mergen. Pas dan gaat de wijziging online.

## Goed om te weten

- **Kosten:** in de Console lopen sessies via je API-account, per gebruik en apart van een Claude-abonnement. Elk teamlid dat aan het werk gaat, kost ook tokens; het goedkopere model voor onderzoek en controle houdt dat beperkt.
- **Veiligheid:** de agents kunnen alles wat het token toelaat. Daarom heeft het token enkel toegang tot deze repository, en gaat er niets online zonder merge. Wie in deze repository kan committen, kan ook de skills en instructies van de agents aanpassen.
- **Beta:** Managed Agents en multiagent zijn in beta. Menu's en namen in de Console kunnen nog veranderen.

Meer uitleg: [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview), [Multiagent](https://platform.claude.com/docs/en/managed-agents/multiagent-orchestration), [Agent definiëren](https://platform.claude.com/docs/en/managed-agents/agent-setup), [Skills](https://platform.claude.com/docs/en/managed-agents/skills), [Subagents in Claude Code](https://code.claude.com/docs/en/sub-agents).
