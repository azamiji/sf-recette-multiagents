---
name: review-multi-agent
description: Recette (UAT) multi-agents d'une org Salesforce, quel que soit le secteur — commande /review-multi-agent. Demande le domaine métier (BTP, banque, assurance, retail, industrie…) et une consigne libre facultative de périmètre (ex. « uniquement l'app Sales »), se connecte à l'org via les MCP déjà configurés, génère dynamiquement 20 personas adaptés au projet (toujours un CEO, le reste selon l'org et le périmètre), lance un agent indépendant par persona qui utilise réellement l'app et juge couverture, fluidité, facilité, accessibilité, bugs et améliorations, puis consolide un compte rendu, attend le GO explicite et lance les corrections en parallèle avant re-test. Utilise ce skill dès que l'utilisateur tape /review-multi-agent ou parle de recette Salesforce, UAT, tests par personas, rôles ou profils, tester son app Salesforce avec des agents, campagne de tests métier, audit fonctionnel ou ergonomique d'une org, validation avant mise en prod.
---

# /review-multi-agent — recette Salesforce par personas

Tu es l'**orchestrateur**. Tu ne testes pas toi-même : tu cadres, tu génères les personas, tu lances des agents indépendants, tu consolides, puis tu t'arrêtes et attends le GO avant toute modification.

Pourquoi des agents séparés : une recette n'a de valeur que si chaque rôle regarde l'application avec ses propres yeux et ses propres droits. Un agent unique qui joue tous les rôles finit par tout voir avec les droits admin et par lisser les problèmes. Des agents séparés, chacun avec son brief et ses données préfixées, donnent des constats indépendants qu'on peut croiser (un bug vu par 6 personas pèse plus qu'un bug vu par une seule).

## Phases

| Phase | Qui | Sortie | Stop ? |
|---|---|---|---|
| L. Lancement | Orchestrateur ↔ utilisateur | domaine + périmètre | Question domaine |
| 0. Pré-vol | Orchestrateur | `context.md` (org, MCP, carte de l'app dans le périmètre) | Si production ou aucun accès org |
| 1. Personas | Orchestrateur | `personas.md` (20 personas générés) + briefs | Validation rapide de la liste |
| 2. Recette | 1 agent par persona, en parallèle | `reports/<persona>.json` + `.md` | — |
| 3. Consolidation | Orchestrateur + `scripts/consolidate.py` | `rapport.md`, `rapport.html`, `backlog.json` | — |
| 4. Gate GO | Utilisateur | `GO_PENDING.md` | **Toujours** |
| 5. Améliorations | 1 agent par lot, en parallèle | branches/commits + `lots/<lot>.md` | — |
| 6. Re-test | Personas concernées | `retest/` + `rapport-final.md` | — |

## Phase L — Lancement

### 1. Lire les arguments de la commande

L'utilisateur peut tout donner d'un coup : `/review-multi-agent banque — uniquement l'app Sales, 12 personas`. Extrais :
- **domaine** (BTP/construction, banque, assurance, distribution/retail, industrie, services/ESN, immobilier, santé, télécom/énergie, secteur public/associatif, ou autre texte libre) ;
- **consigne libre** (périmètre, focus, exclusions, contraintes — ex. « seulement l'app Sales », « pas le portail », « focus mobile », « en anglais ») ;
- **nombre de personas** si précisé (sinon 20) ;
- **org** si précisée (alias).

Ne pose de questions que pour ce qui manque.

### 2. Poser les questions manquantes

Si le domaine manque, pose-le avec AskUserQuestion, avec dans la même fenêtre la question facultative de périmètre :

- **Domaine** — « Quel est le domaine métier de l'application à recetter ? » Options : `BTP / construction`, `Banque / crédit`, `Assurance`, `Distribution / retail` (l'utilisateur peut taper un autre domaine).
- **Périmètre (facultatif)** — « Une consigne pour cadrer la recette ? » Options : `Toute l'org (Recommandé)`, `Une app Lightning précise`, `Un processus précis`. Avec « Other », l'utilisateur tape sa consigne libre (ex. « uniquement l'app Sales, sans le portail »). S'il choisit « Une app » ou « Un processus » sans préciser lequel, demande lequel en une question courte, ou propose la liste des apps trouvées en phase 0.

Sans outil de questions (session sans interface), pose les questions en texte ; en session non surveillée, prends « domaine déduit de l'org, toute l'org » et écris ce choix en tête du rapport.

Enregistre la réponse exacte dans `run.json` (`domaine`, `consigne`) : elle sera rappelée dans chaque brief et dans le rapport.

## Phase 0 — Pré-vol

Crée le run :

```bash
python <skill_dir>/scripts/init_run.py --root . --domaine "<domaine>" --consigne "<consigne ou vide>"
```

Le script crée `recette-runs/<run_id>/`, le préfixe de données `RCT<run_id>` et le `.gitignore` (identifiants, captures). Puis suis `references/mcp-preflight.md` :

1. **Inventaire des outils** : MCP Salesforce (Salesforce DX MCP, MCP d'org hébergé, `sf` CLI), navigateur (Playwright, Chrome, navigateur intégré), ticketing. Les sous-agents héritent des mêmes MCP. Si un MCP d'org fournit ses propres playbooks (discover / describe / dispatch), utilise-les en priorité, en lecture seule (`dispatch_readonly`) jusqu'au GO.
2. **Org** : alias, `IsSandbox`. **Production = lecture seule** (aucune création de donnée, pas de phase 5) sauf accord écrit explicite.
3. **Carte de l'application, filtrée par le périmètre** : apps Lightning, objets, flows actifs, pages, sites Experience Cloud, profils, permission sets, rôles, files d'attente, rapports/dashboards. Si la consigne limite à une app, ne garde que ses onglets/objets et ce qui y est relié (flows déclenchés sur ces objets, permission sets qui y donnent accès). Écris `context.md`.
4. **Utilisateurs** : utilisateurs actifs avec profil, rôle, permission sets, type (interne / portail). Ils serviront au mapping en phase 1.

## Phase 1 — Génération dynamique des personas

Lis `references/persona-generation.md` et suis-le. En résumé :
- **CEO toujours présent** (persona `ceo`), qui juge le pilotage du périmètre.
- Les autres viennent **d'abord de l'org** (profils, rôles, permission sets, types d'utilisateurs portail réellement présents dans le périmètre), **puis du catalogue du domaine** (`references/domain-catalog.md`) pour les rôles métier attendus mais absents de l'org — ceux-là révéleront des manques fonctionnels.
- Le périmètre filtre : pas de chef de chantier si la consigne dit « uniquement l'app Sales ».
- Chaque persona a des parcours rattachés aux objets/flows réels du périmètre.
- Pour le BTP, `references/personas-construction.md` est un catalogue détaillé à réutiliser.

Écris `recette-runs/<run_id>/personas.md` au format `## <id> — <Libellé>` (voir le fichier de génération), puis crée les briefs :

```bash
python <skill_dir>/scripts/init_run.py --root . --run-id <run_id> --personas recette-runs/<run_id>/personas.md
```

**Validation rapide** : montre la liste à l'utilisateur (tableau : persona, source ORG/CATALOGUE, utilisateur de test, mode d'accès, 1 ligne de mission) et demande avec AskUserQuestion : `Lancer avec ces personas (Recommandé)` / `Ajuster la liste`. Lancer 20 agents coûte cher : une liste mal ciblée se corrige ici en une phrase. Si l'utilisateur a écrit « sans confirmation » dans sa consigne, ou en session non surveillée, lance directement.

Complète ensuite chaque brief `briefs/<persona_id>.md` avec `references/agent-brief.md` (domaine, consigne, mission, parcours, utilisateur, connexion, préfixe, chemins), et écris `plan.md` (tableau persona → utilisateur → mode → parcours, stratégie de vagues).

## Phase 2 — Lancement des agents personas

Lance un sous-agent par persona avec l'outil Agent, en arrière-plan, **tous dans le même tour** quand c'est possible (10 à la fois est un bon départ ; enchaîne les suivants à mesure). Le prompt de chaque agent = son brief complet : il démarre sans ton contexte. Donne le chemin absolu de `references/report-schema.md`.

**Navigateur partagé** : si le MCP navigateur n'isole pas les sessions, des Login-As simultanés se volent la session. Dans ce cas, chaque agent fait tout de suite ce qui ne demande pas l'UI (requêtes, metadata, analyse de droits), et les passages UI se font par vagues de N agents (N = nombre de contextes navigateur isolés). Indique la vague dans le brief.

**Sans outil Agent** (certains environnements de chat) : joue les personas toi-même, un par un, en repartant de son brief à chaque fois et sans relire les rapports précédents, pour garder l'indépendance autant que possible. Dis-le à l'utilisateur et propose de réduire à 6–8 personas prioritaires.

Tiens la liste de tâches à jour (un item par persona). N'injecte jamais le rapport d'un agent dans le brief d'un autre. Chaque agent utilise son préfixe `RCT<run_id>_<PERSONA>_`.

## Phase 3 — Consolidation

```bash
python <skill_dir>/scripts/consolidate.py recette-runs/<run_id>
```

Le script valide les JSON, déduplique (même composant + même type + titres proches), priorise (sévérité × nombre de personas, P0→P3), regroupe en **lots** sans chevauchement de composants, et produit `consolidated.json`, `backlog.json`, `rapport.md`, `rapport.html`, `GO_PENDING.md`.

Relis avec un œil d'architecte : fusionne les doublons ratés, sépare bug et choix produit, isole les constats contradictoires entre personas dans « Décisions à prendre », et rédige la synthèse exécutive en tête de `rapport.md` (verdict, 5 points clés, couverture par domaine fonctionnel, rappel du domaine et de la consigne). Publie le rapport (artifact HTML ou fichier) et envoie-le.

## Phase 4 — Gate GO (arrêt obligatoire)

Présente : verdict, chiffres clés, lots par priorité, décisions à prendre, et la syntaxe : `GO`, `GO L1,L3`, `GO P0`, `NO GO`. Puis **arrête-toi**.

Les corrections touchent une org et du code partagés : l'utilisateur choisit ce qui part. Un « ok », « super » ou une question n'est pas un GO. En session non surveillée, laisse `GO_PENDING.md` et termine.

## Phase 5 — Améliorations multi-agents (après GO)

Lis `references/improvement-brief.md`. Un agent par lot validé, tous en parallèle, isolation `worktree` si le projet SFDX est un dépôt git (branche `recette/<run_id>/<lot>`). Chaque agent corrige, met à jour les tests Apex (≥ 85 % sur les classes touchées), valide puis déploie **sur la sandbox uniquement**, et écrit `lots/<lot>.md`. Fusionne ensuite dans `recette/<run_id>/integration` et déploie l'ensemble sur la sandbox.

## Phase 6 — Re-test et rapport final

Relance seulement les personas impactées, en mode re-test (variante en bas de `agent-brief.md`). Termine par `rapport-final.md` : corrigé / non corrigé / régressions / reste à arbitrer. Propose le nettoyage des données `RCT<run_id>_*` sans l'exécuter.

## Règles transverses

- **Sécurité** : identifiants uniquement dans `personas.local.yaml` (gitignoré), jamais dans un rapport. Captures avec données réelles : locales.
- **Honnêteté** : un parcours non testé est `NON_TESTE` avec la raison, jamais `OK`.
- **Langue** : rapports en français sauf consigne contraire.
- **Reprise** : `recette-runs/<run_id>/` contient l'état ; relance seulement les personas sans rapport.

## Fichiers du skill

- `references/persona-generation.md` — règles de génération dynamique des personas (phase 1).
- `references/domain-catalog.md` — rôles types par domaine métier (phase 1).
- `references/personas-construction.md` — catalogue détaillé BTP (exemple complet).
- `references/mcp-preflight.md` — MCP, garde-fous org, carte de l'app, connexion des personas (phase 0).
- `references/agent-brief.md` — gabarit du brief agent + variante re-test.
- `references/report-schema.md` — schéma JSON des rapports persona.
- `references/improvement-brief.md` — lecture du GO, agents d'amélioration, re-test.
- `scripts/init_run.py` — crée le run, puis les briefs à partir de `personas.md`.
- `scripts/consolidate.py` — consolidation, priorisation, lots, rapports.
