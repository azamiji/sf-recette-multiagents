# sf-recette-multiagents

Skill Claude pour la **recette multi-agents d'une application Salesforce par personas métier** (domaine BTP / construction par défaut).

Un orchestrateur lance 20 sous-agents indépendants — CEO, directeur achats, DAF, acheteur, fournisseur, comptable, chef de projet, chef de chantier, conducteur de travaux, contrôleur de gestion, QHSE, logistique, économiste, chargé d'affaires, sous-traitant, maître d'ouvrage, SAV, RH, juriste, admin Salesforce. Chacun utilise l'application avec ses droits, vérifie la couverture fonctionnelle de son domaine, la fluidité, l'accessibilité et les bugs, puis propose des améliorations. L'orchestrateur consolide tout dans un rapport (MD + HTML), propose des lots de corrections et **attend le GO** avant de lancer les corrections en parallèle puis le re-test.

## Pré-requis

- Claude Code (sous-agents via l'outil Agent).
- MCP déjà configurés : **Salesforce DX MCP** (ou `sf` CLI authentifié sur la sandbox) et idéalement un **MCP navigateur** (Playwright, Claude in Chrome…). Les sous-agents héritent des MCP de la session.
- Python 3.9+ (scripts sans dépendance).
- Une **sandbox** de recette. En production, le skill passe en lecture seule.

## Installation

```bash
git clone <ce-repo> ~/sf-recette-multiagents
ln -s ~/sf-recette-multiagents/skills/sf-recette-multiagents ~/.claude/skills/sf-recette-multiagents
# ou, pour un projet seulement :
cp -r skills/sf-recette-multiagents <projet-sfdx>/.claude/skills/
```

## Utilisation

Depuis le projet SFDX (ou n'importe quel dossier) :

> Lance la recette de notre app chantier sur la sandbox `uat` avec les 20 personas BTP.

Puis, après lecture du rapport : `GO`, `GO L1,L3`, `GO P0` ou `NO GO`.

Identifiants des utilisateurs de test (optionnel, jamais commité) : `personas.local.yaml` à la racine du projet — voir `references/mcp-preflight.md`.

## Contenu

| Fichier | Rôle |
|---|---|
| `SKILL.md` | Workflow de l'orchestrateur (phases 0 → 6, gate GO) |
| `references/personas-construction.md` | Les 20 personas BTP : mission, parcours, points de vigilance |
| `references/agent-brief.md` | Gabarit du prompt d'un agent persona (+ variante re-test) |
| `references/report-schema.md` | Schéma JSON des rapports persona |
| `references/mcp-preflight.md` | Inventaire MCP, garde-fous org, connexion des personas, vagues navigateur |
| `references/improvement-brief.md` | Lecture du GO, agents d'amélioration par lot, re-test |
| `scripts/init_run.py` | Crée `recette-runs/<run_id>/` et les briefs |
| `scripts/consolidate.py` | Dédoublonnage, priorisation P0–P3, lots, `rapport.md/html`, `GO_PENDING.md` |
| `evals/` | Cas de test du skill (format `claude plugin eval`) |

## Adapter à un autre domaine

Copier `references/personas-construction.md` en `personas-<domaine>.md` en gardant le format `## <id> — <Libellé>` et passer ce fichier à `init_run.py --personas`.
