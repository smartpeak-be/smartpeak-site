"""Write the agent definitions for the Claude Console and for Claude Code from one source.

The prompts live in agent/rollen/<slug>.md. The settings per role (model, effort, tools, skills) live in ROLES below.
This script writes:
  agent/console/<slug>.md     for Claude Managed Agents (ant apply agent/console/smartpeak-website.md)
  .claude/agents/<slug>.md    subagents for Claude Code (the main session is the coordinator there)

Run: python3 tools/build_agents.py            (write the files)
     python3 tools/build_agents.py --check    (exit 1 if a generated file is out of date)
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "agent" / "rollen"
CONSOLE = ROOT / "agent" / "console"
CODE = ROOT / ".claude" / "agents"

READ_ONLY_WEB = ["Read", "Glob", "Grep", "WebSearch", "WebFetch"]

# Why these models: writing, coordinating and independent fact-checking need the strongest judgement (Opus).
# Research and chart work are broad but routine (Sonnet). The technical check is mechanical (Haiku).
ROLES = [
    {
        "slug": "smartpeak-website",
        "name": "SmartPeak website",
        "description": "Verantwoordelijke voor smartpeak.be: plant, schrijft, verdeelt werk over het team en levert een pull request af.",
        "model": "claude-opus-5-5", "effort": "high",
        "coordinator": True,
    },
    {
        "slug": "smartpeak-onderzoeker",
        "name": "SmartPeak onderzoeker",
        "description": "Onderzoekt een onderwerp voor smartpeak.be in officiële Belgische bronnen en levert een nota met bronnen. Gebruik voor nieuwe onderwerpen, actuele regels, cijfers en zoekvragen.",
        "model": "claude-sonnet-5-5", "effort": "medium",
        "code_tools": READ_ONLY_WEB,
    },
    {
        "slug": "smartpeak-feitencontroleur",
        "name": "SmartPeak feitencontroleur",
        "description": "Controleert onafhankelijk elke bewering in een nieuwe of aangepaste tekst of infographic van smartpeak.be tegen de bronnen. Gebruik altijd voor publicatie.",
        "model": "claude-opus-5-5", "effort": "high",
        "code_tools": READ_ONLY_WEB,
        "code_skills": ["smartpeak-feitencheck"],
    },
    {
        "slug": "smartpeak-grafisch",
        "name": "SmartPeak grafisch",
        "description": "Maakt of wijzigt infographics en grafieken voor smartpeak.be in de huisstijl en rendert ze naar WebP.",
        "model": "claude-sonnet-5-5", "effort": "high",
        "code_tools": ["Read", "Glob", "Grep", "Edit", "Write", "Bash"],
        "code_skills": ["smartpeak-infographic"],
    },
    {
        "slug": "smartpeak-kwaliteit",
        "name": "SmartPeak kwaliteit",
        "description": "Bouwt smartpeak.be, draait de controles en bekijkt gewijzigde pagina's op gsm en computer. Gebruik na het bouwen, voor een pull request.",
        "model": "claude-haiku-5-5", "effort": None,
        "code_tools": ["Read", "Glob", "Grep", "Bash"],
        "code_skills": ["smartpeak-publiceren"],
    },
]


def q(s):
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


def note(role):
    return f"# Gegenereerd door tools/build_agents.py uit agent/rollen/{role['slug']}.md. Pas daar aan, niet hier.\n"


def model_yaml(role):
    if role["effort"]:
        return f"model:\n  id: {role['model']}\n  effort: {role['effort']}\n"
    return f"model: {role['model']}\n"


def console_file(role, body):
    head = f"---\n{note(role)}name: {role['name']}\ndescription: {q(role['description'])}\n{model_yaml(role)}"
    if role.get("coordinator"):
        subs = [r for r in ROLES if not r.get("coordinator")]
        head += ("mcp_servers:\n  - type: url\n    name: github\n    url: https://api.githubcopilot.com/mcp/\n"
                 "tools:\n  - type: agent_toolset_20260401\n  - type: mcp_toolset\n    mcp_server_name: github\n"
                 "skills:\n  - type: anthropic\n    skill_id: pdf\n"
                 "multiagent:\n  type: multiagent_20261001\n  subagents:\n    type: enabled\n"
                 "    inline_agents:\n      type: disabled\n    predefined_agents:\n")
        head += "".join(f"      - ./{r['slug']}.md\n" for r in subs)
        head += "  workflows:\n    type: disabled\n"
    else:
        head += "tools:\n  - type: agent_toolset_20260401\n"
    return head + "---\n\n" + body


def code_file(role, body):
    head = f"---\n{note(role)}name: {role['slug']}\ndescription: {q(role['description'])}\n"
    head += f"tools: {', '.join(role['code_tools'])}\nmodel: {role['model']}\n"
    if role["effort"]:
        head += f"effort: {role['effort']}\n"
    if role.get("code_skills"):
        head += "skills:\n" + "".join(f"  - {s}\n" for s in role["code_skills"])
    return head + "---\n\n" + body


def outputs():
    for role in ROLES:
        body = (SRC / f"{role['slug']}.md").read_text(encoding="utf-8")
        yield CONSOLE / f"{role['slug']}.md", console_file(role, body)
        if not role.get("coordinator"):
            yield CODE / f"{role['slug']}.md", code_file(role, body)


def main(check):
    stale = []
    for path, content in outputs():
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != content:
                stale.append(path.relative_to(ROOT))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            print("wrote", path.relative_to(ROOT))
    if stale:
        print("Out of date, run python3 tools/build_agents.py:", *stale, sep="\n  ")
        sys.exit(1)


if __name__ == "__main__":
    main("--check" in sys.argv)
