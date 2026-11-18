---
name: sf-recette-multiagents
description: Recette (UAT) multi-agents d'une app Salesforce par personas métier — un orchestrateur lance 20 sous-agents indépendants (CEO, directeur achats, DAF, acheteur, fournisseur, comptable, chef de projet, chef de chantier, QHSE, sous-traitant…) qui utilisent réellement l'app via les MCP déjà configurés (Salesforce DX, navigateur), jugent couverture, fluidité, accessibilité, bugs et améliorations ; l'orchestrateur consolide un compte rendu, attend le GO explicite, puis lance les corrections en parallèle et re-teste. Utilise ce skill dès que l'utilisateur parle de recette Salesforce, UAT, tests par personas/rôles/profils, tester son app Salesforce avec des agents, campagne de tests métier, audit fonctionnel ou ergonomique d'une org, validation avant mise en prod — en particulier en BTP / construction (achats, chantiers, fournisseurs, sous-traitance, facturation).
---

# Recette Salesforce multi-agents par personas

Tu es l'**orchestrateur**. Tu ne testes pas toi-même : tu prépares le terrain, lances des agents personas indépendants, consolides leurs comptes rendus, puis tu t'arrêtes et attends le GO de l'utilisateur avant toute modification.

Pourquoi cette organisation : une recette n'a de valeur que si chaque rôle regarde l'application avec ses propres yeux et ses propres droits. Un agent unique qui « joue » 20 rôles finit par tout voir avec les droits admin et par lisser les problèmes. Des agents séparés, chacun avec son brief et ses données préfixées, produisent des constats indépendants qu'on peut ensuite croiser (un bug vu par 6 personas pèse plus qu'un bug vu par une seule).

## Vue d'ensemble des phases

| Phase | Qui | Sortie | Stop ? |
|---|---|---|---|
| 0. Pré-vol | Orchestrateur | `context.md` (org, MCP, app, mapping personas→utilisateurs) | Oui si org = production ou mapping impossible |
| 1. Plan | Orchestrateur | `plan.md` + 1 brief par persona | Non (sauf ambiguïté forte) |
| 2. Recette | 20 agents personas en parallèle | `reports/<persona>.json` + `.md` | — |
| 3. Consolidation | Orchestrateur + `scripts/consolidate.py` | `rapport.md`, `rapport.html`, `backlog.json` | — |
| 4. Gate GO | Utilisateur | `GO_PENDING.md` | **Toujours** |
| 5. Améliorations | 1 agent par lot, en parallèle | branches/commits + `lots/<lot>.md` | — |
| 6. Re-test | Personas concernées | `retest/<persona>.json` + rapport final | — |

Tout le run vit dans `recette-runs/<run_id>/` à la racine du projet courant (`run_id` = `AAAAMMJJ-HHMM`). Crée-le avec :

```bash
python <skill_dir>/scripts/init_run.py --root . --personas <skill_dir>/references/personas-construction.md
```

Le script crée l'arborescence, attribue le `run_id` et le préfixe de données `RCT<run_id>`, et écrit un squelette de brief par persona dans `briefs/`.

## Phase 0 — Pré-vol

Lis `references/mcp-preflight.md` et suis-le. En résumé :

1. **Inventaire des outils** : liste les outils MCP disponibles dans la session (Salesforce DX MCP / `sf` CLI, navigateur Playwright ou Chrome, éventuellement Jira/Slack). Note pour chacun ce qu'il permet (SOQL, metadata, déploiement, Apex tests, navigation UI, captures). Les sous-agents héritent des mêmes MCP : ce que tu trouves ici, eux l'auront.
2. **Identification de l'org** : alias, instance, `IsSandbox`. **Si l'org est une production, la recette est en lecture seule** (aucune création de donnée, aucun déploiement) sauf accord écrit explicite de l'utilisateur — dis-le et demande.
3. **Découverte de l'application** : apps Lightning, objets custom, flows actifs, Lightning pages, Experience Cloud sites, profils et permission sets, rapports/tableaux de bord. Enregistre dans `context.md`. Cette carte sert à mesurer la couverture : un agent ne peut juger « fonctionnalité manquante » que s'il sait ce qui existe.
4. **Mapping persona → utilisateur de test** : pour chaque persona, trouve un utilisateur actif dont le profil/permission set correspond (ex. `Acheteur` → profil « Achats »). Méthodes de connexion, par ordre de préférence :
   - identifiants dédiés fournis par l'utilisateur dans `personas.local.yaml` (jamais commité) ;
   - « Se connecter en tant que » (Login-As) depuis un admin, via le MCP navigateur ;
   - à défaut, **mode analyse de droits** : l'agent teste avec l'admin mais vérifie via SOQL (`ObjectPermissions`, `FieldPermissions`, `SetupEntityAccess`, sharing) ce que le profil verrait. Il le déclare comme limite dans son rapport.
   Les personas externes (fournisseur, sous-traitant, maître d'ouvrage) passent par le site Experience Cloud s'il existe ; sinon ils signalent l'absence de portail comme constat.
5. Si un persona n'a aucun équivalent dans l'org (ex. pas de module QHSE), garde-le quand même : son rapport dira ce qui manque, c'est exactement l'information attendue.

S'il manque des utilisateurs de test et que l'org est une sandbox, propose de les créer — mais demande d'abord, c'est une écriture.

## Phase 1 — Plan

1. Les 20 personas par défaut sont dans `references/personas-construction.md` (8 demandés + 12 ajoutés pour couvrir le cycle complet d'un projet BTP). Adapte la liste au contexte : si l'utilisateur a donné d'autres rôles, ajoute-les ; si l'app n'a clairement qu'un périmètre (ex. achats seulement), garde quand même les rôles transverses (CEO, DAF, admin) qui jugent le pilotage et la sécurité.
2. Pour chaque persona, complète son brief `briefs/<persona_id>.md` à partir de `references/agent-brief.md` : mission, parcours à tester rattachés aux objets/flows découverts en phase 0, utilisateur et mode de connexion, préfixe de données, chemin de sortie.
3. Écris `plan.md` : tableau persona → utilisateur → mode d'accès → parcours, et la stratégie de vagues (ci-dessous).

Ne demande pas de validation du plan sauf si une décision coûteuse reste ambiguë (org incertaine, aucun utilisateur mappable). L'utilisateur veut un compte rendu, pas une réunion de cadrage.

## Phase 2 — Lancement des agents personas

Lance un sous-agent par persona avec l'outil Agent, **tous dans le même tour** quand c'est possible, en arrière-plan. Le prompt de chaque agent = contenu complet de son brief (il démarre sans ton contexte : tout ce dont il a besoin doit y être, y compris le chemin du schéma de rapport `references/report-schema.md` en absolu).

**Vagues et navigateur partagé** — point important : si le MCP navigateur n'isole pas les sessions (un seul Chrome, une seule session Salesforce), 20 agents qui font Login-As en même temps vont se voler la session les uns les autres. Dans ce cas :
- chaque agent fait en parallèle tout ce qui ne demande pas l'UI (SOQL, metadata, analyse de droits, préparation des données) ;
- les passages UI sont sérialisés : vagues de N agents où N = nombre de contextes navigateur isolés disponibles (1 si un seul). Indique la vague dans le brief et lance la vague suivante quand la précédente rend son rapport.
Si le MCP navigateur fournit des contextes isolés (ex. Playwright MCP `--isolated`, plusieurs profils), lance tout en parallèle.

Limite les lancements simultanés à ce que l'environnement supporte (10 à la fois est un bon point de départ) ; enchaîne les suivants à mesure que les rapports arrivent.

Pendant que les agents tournent, tiens la liste de tâches à jour (un item par persona) — c'est ce que l'utilisateur regarde s'il revient plus tard.

**Indépendance** : n'injecte jamais le rapport d'un agent dans le brief d'un autre. Chaque agent utilise son propre préfixe de données (`RCT<run_id>_<PERSONA>_`) pour ne pas trébucher sur les enregistrements des autres et pour permettre le nettoyage.

## Phase 3 — Consolidation

Quand tous les rapports (ou tous ceux qui pouvaient aboutir) sont dans `reports/` :

```bash
python <skill_dir>/scripts/consolidate.py recette-runs/<run_id>
```

Le script valide chaque JSON, déduplique les constats (même composant + même type + titres proches), calcule la priorité (sévérité × nombre de personas impactées), regroupe en **lots** d'amélioration indépendants (un lot = un ensemble de composants qu'un seul agent peut modifier sans conflit), et produit `consolidated.json`, `backlog.json`, `rapport.md`, `rapport.html`.

Relis ensuite le résultat avec un œil d'architecte — le script fait l'arithmétique, pas le jugement :
- fusionne les doublons que la similarité textuelle a ratés ;
- sépare « bug » et « choix produit discutable » ;
- repère les constats contradictoires entre personas (ex. le chef de chantier veut moins de champs obligatoires, le contrôleur de gestion en veut plus) : ce sont des arbitrages pour l'utilisateur, pas des corrections automatiques ; mets-les dans la section « Décisions à prendre » ;
- ajoute la synthèse exécutive en tête de `rapport.md` (verdict global, 5 points clés, carte de couverture par domaine).

Publie le rapport consolidé (artifact HTML ou fichier selon l'environnement) et envoie-le à l'utilisateur.

## Phase 4 — Gate GO (arrêt obligatoire)

Écris `GO_PENDING.md` (liste des lots, contenu, effort estimé, risque, composants touchés) puis **arrête-toi**. Présente à l'utilisateur :
- le verdict global et les chiffres clés (bugs bloquants, couverture par domaine) ;
- les lots proposés, du plus prioritaire au moins prioritaire ;
- les décisions à prendre ;
- la syntaxe de réponse : `GO` (tout), `GO L1,L3`, `GO P0` (bloquants seulement), `NO GO`.

Pourquoi un arrêt dur : les corrections touchent une org et du code partagés ; l'utilisateur doit choisir ce qui part, même si tout semble évident. N'interprète pas un « ok », « super » ou une question comme un GO — seul un GO explicite déclenche la phase 5. En session non surveillée, ne passe jamais cette étape : laisse `GO_PENDING.md` et termine.

## Phase 5 — Améliorations multi-agents (après GO)

Lis `references/improvement-brief.md`. Pour chaque lot validé, lance un agent d'amélioration, tous en parallèle (les lots sont construits pour ne pas se chevaucher). Si le projet SFDX est un dépôt git, utilise l'isolation `worktree` : chaque agent travaille sur sa branche `recette/<run_id>/<lot>`.

Chaque agent : implémente, ajoute/maj les tests Apex (couverture ≥ 85 % sur les classes touchées), valide localement (`sf project deploy validate` ou équivalent MCP) et ne déploie que sur la sandbox de recette identifiée en phase 0. Jamais en production. Il écrit `lots/<lot>.md` (changements, fichiers, résultats de tests, risques).

Fusionne ensuite les branches dans une branche d'intégration `recette/<run_id>/integration`, résous les éventuels conflits, et déploie l'ensemble sur la sandbox.

## Phase 6 — Re-test et rapport final

Relance uniquement les personas concernées par les lots livrés, en mode re-test (le brief liste les constats à vérifier + un passage rapide sur leurs parcours principaux pour détecter les régressions). Sorties dans `retest/`. Termine par `rapport-final.md` : constats corrigés / non corrigés / régressions, et ce qu'il reste à arbitrer.

Proposer le nettoyage des données de test (`RCT<run_id>_*`) — à exécuter seulement sur accord.

## Règles transverses

- **Sécurité** : les identifiants restent dans `personas.local.yaml` (ajouté au `.gitignore` par `init_run.py`) ; ne les écris dans aucun rapport ni log. Les captures d'écran contenant des données personnelles réelles restent locales.
- **Honnêteté des rapports** : un parcours non testé est « NON_TESTÉ » avec la raison, jamais « OK ». Mieux vaut un rapport avec des limites déclarées qu'une couverture gonflée.
- **Langue** : rapports en français.
- **Reprise** : si le run est interrompu, `recette-runs/<run_id>/` contient l'état ; relance seulement les personas sans rapport.

## Fichiers du skill

- `references/personas-construction.md` — les 20 personas BTP (mission, parcours, points de vigilance). Lire en phase 1.
- `references/agent-brief.md` — gabarit du prompt d'un agent persona. Lire en phase 1.
- `references/report-schema.md` — format JSON du rapport persona. À transmettre aux agents.
- `references/mcp-preflight.md` — détection des MCP, connexion, garde-fous org. Lire en phase 0.
- `references/improvement-brief.md` — gabarit des agents d'amélioration et du re-test. Lire en phase 5.
- `scripts/init_run.py` — crée le run et les squelettes de briefs.
- `scripts/consolidate.py` — consolidation, priorisation, lots, rapports MD/HTML.
