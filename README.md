<p align="center"><img src="docs/hero.svg" alt="/review-multi-agent — recette Salesforce multi-agents" width="100%"></p>

<p align="center"><img src="docs/workflow.svg" alt="Cadrage, connexion, personas, 20 agents, rapport, GO, corrections" width="100%"></p>

<p align="center"><img src="docs/personas.svg" alt="Exemple de personas générés : domaine BTP" width="100%"></p>

<p align="center"><img src="docs/report.svg" alt="Aperçu du rapport consolidé" width="100%"></p>

## ⚡ Installer

**Claude Code**
```bash
git clone https://github.com/azamiji/sf-recette-multiagents ~/sf-recette-multiagents
ln -s ~/sf-recette-multiagents/skills/review-multi-agent ~/.claude/skills/review-multi-agent
```

**Chat Claude** — téléverser le dossier `skills/review-multi-agent` (zippé) dans *Paramètres → Skills*.

## ▶️ Lancer

```text
/review-multi-agent
```
```text
/review-multi-agent banque — uniquement l'app Sales
```
```text
GO        GO L1,L3        GO P0        NO GO
```

<sub>Prérequis : MCP Salesforce (DX, MCP d'org ou <code>sf</code> CLI) · MCP navigateur recommandé · une sandbox (lecture seule en production).</sub>
