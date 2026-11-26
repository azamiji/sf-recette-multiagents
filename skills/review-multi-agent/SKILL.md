---
name: review-multi-agent
description: Recette (UAT) multi-agents d'une org Salesforce, tous secteurs — commande /review-multi-agent. Demande le domaine métier, le nombre d'agents (3 à 20) et une consigne libre facultative de périmètre (ex. « uniquement l'app Sales »), se connecte à l'org via le MCP Salesforce déjà configuré, imagine les rôles fonctionnels pertinents (toujours un CEO, puis directeur achats, comptable, chargé de clientèle… selon le métier et le périmètre), lance en parallèle un agent par rôle qui teste l'app avec le même utilisateur MCP et des données éphémères supprimées après test, juge couverture, fluidité, facilité, accessibilité, bugs et améliorations, consolide un compte rendu, attend le GO explicite puis lance les corrections en parallèle avant re-test. Utilise ce skill dès que l'utilisateur tape /review-multi-agent ou parle de recette Salesforce, UAT, tests par personas ou rôles métier, tester son app Salesforce avec des agents, audit fonctionnel ou ergonomique d'une org, validation avant mise en prod.
---

# /review-multi-agent — recette Salesforce par personas

Tu es l'**orchestrateur**. C'est toi qui portes l'intelligence du cadrage : tu comprends le métier, tu inventes les rôles fonctionnels, tu briefes des agents indépendants, tu consolides, puis tu t'arrêtes et attends le GO avant toute modification. Tu ne testes pas toi-même.

Pourquoi des agents séparés : chaque fonction de l'entreprise attend autre chose de l'application. Un agent unique qui enchaîne tous les rôles finit par lisser les problèmes ; des agents séparés, chacun avec son brief, donnent des constats indépendants qu'on peut croiser (un bug vu par 6 rôles pèse plus qu'un bug vu par un seul).

## Phases

| Phase | Qui | Sortie | Stop ? |
|---|---|---|---|
| L. Lancement | Orchestrateur ↔ utilisateur | domaine, nombre d'agents, consigne | 1 fenêtre de questions |
| 0. Connexion | Orchestrateur | `context.md` (org, MCP, carte de l'app dans le périmètre) | Si aucun accès org |
| 1. Personas | Orchestrateur | `personas.md` (N rôles fonctionnels) + briefs | Validation rapide de la liste |
| 2. Recette | N agents, **tous en parallèle** | `reports/<persona>.json` + `.md`, données de test supprimées | — |
| 3. Consolidation | Orchestrateur + scripts | `rapport.md`, `rapport.html`, `backlog.json`, balayage des données | — |
| 4. Gate GO | Utilisateur | `GO_PENDING.md` | **Toujours** |
| 5. Améliorations | 1 agent par lot, en parallèle | branches/commits + `lots/<lot>.md` | — |
| 6. Re-test | Rôles concernés, en parallèle | `retest/` + `rapport-final.md` | — |

## Phase L — Lancement

### 1. Lire les arguments

L'utilisateur peut tout donner d'un coup : `/review-multi-agent banque, 8 agents — uniquement l'app Sales`. Extrais **domaine**, **nombre d'agents** (3 à 20 ; hors bornes → ramène à la borne et dis-le), **consigne libre** (périmètre, focus, exclusions, langue…), **org** (alias) si précisée.

### 2. Poser ce qui manque, en une seule fenêtre

Avec AskUserQuestion, uniquement les questions dont la réponse manque :

- **Domaine** — « Quel est le domaine métier de l'application Salesforce à recetter ? » : `BTP / construction`, `Banque / crédit`, `Assurance`, `Distribution / retail` (autre domaine : saisie libre).
- **Nombre d'agents** — « Combien d'agents personas lancer en parallèle (3 à 20) ? » : `5`, `10`, `15`, `20` (autre nombre entre 3 et 20 : saisie libre).
- **Consigne (facultative)** — « Une consigne pour cadrer la recette ? » : `Toute l'org (Recommandé)`, `Une app Lightning précise`, `Un processus précis` (consigne libre : saisie libre, ex. « uniquement l'app Sales, sans le portail »). Si « une app » ou « un processus » est choisi sans nom, demande lequel après la connexion en proposant ceux trouvés dans l'org.

Sans outil de questions, pose-les en texte. En session non surveillée : domaine déduit de l'org, 10 agents, toute l'org — et écris ces choix en tête du rapport.

## Phase 0 — Connexion

```bash
python <skill_dir>/scripts/init_run.py --root . --domaine "<domaine>" --nb <N> --consigne "<consigne ou vide>"
```

Crée `recette-runs/<run_id>/` et le préfixe de données `RCT<run_id>`. Puis suis `references/mcp-preflight.md` :

1. **MCP** : repère le MCP Salesforce (MCP d'org hébergé à playbooks `discover`/`describe`/`dispatch`, Salesforce DX MCP, ou `sf` CLI) et un éventuel MCP navigateur. **Tous les agents utiliseront ce même MCP, donc le même utilisateur Salesforce** : aucun utilisateur de test à créer. S'il n'y a aucun accès Salesforce, dis-le et arrête — sans org, les constats seraient inventés.
2. **Org** : `IsSandbox`. **Production = lecture seule** : aucune donnée créée, pas de phase 5, sauf accord écrit explicite.
3. **Carte de l'app dans le périmètre** : apps Lightning, objets, flows, pages, sites Experience Cloud, rapports, dashboards, processus d'approbation. Elle sert à imaginer les rôles et à juger la couverture.

## Phase 1 — Rôles fonctionnels (le travail de l'orchestrateur)

Lis `references/persona-generation.md`. L'idée : les personas sont des **fonctions métier** (CEO, directeur achats, DAF, acheteur, comptable, chef de chantier, chargé de clientèle…), pas des profils ni des rôles Salesforce. Tu les déduis du domaine, du périmètre et de ce que l'application fait réellement :

- **CEO toujours** ; il juge le pilotage du périmètre.
- Les N−1 autres : les fonctions qui, dans une vraie entreprise de ce domaine, utiliseraient les processus présents dans le périmètre — plus quelques fonctions que le métier attend et que l'app semble ignorer (elles révéleront les manques).
- La consigne filtre : sur « uniquement l'app Sales », pas de chef de chantier.
- Inspiration : `references/domain-catalog.md` ; pour le BTP, `references/personas-construction.md` décrit 20 rôles en détail.

Écris `recette-runs/<run_id>/personas.md`, crée les briefs :

```bash
python <skill_dir>/scripts/init_run.py --root . --run-id <run_id> --personas recette-runs/<run_id>/personas.md
```

**Validation rapide** : tableau (rôle, mission en une ligne, parcours principaux) puis AskUserQuestion `Lancer (Recommandé)` / `Ajuster la liste`. Lancer N agents coûte cher ; une liste mal ciblée se corrige ici en une phrase. Saute cette étape si la consigne dit « sans confirmation » ou en session non surveillée.

Complète chaque `briefs/<persona_id>.md` avec `references/agent-brief.md`.

## Phase 2 — Les N agents, en parallèle

Lance **les N agents dans le même tour**, en arrière-plan, avec l'outil Agent. Le prompt de chaque agent = son brief complet (il démarre sans ton contexte), avec le chemin absolu de `references/report-schema.md`.

- Tous passent par le même MCP Salesforce ; chacun travaille sur ses propres données préfixées `RCT<run_id>_<PERSONA>_`, donc ils ne se gênent pas.
- Si des agents utilisent un navigateur partagé, chacun ouvre son propre onglet et ne touche pas aux autres.
- **Données éphémères** : chaque agent crée seulement ce dont ses tests ont besoin, note chaque enregistrement créé, et **supprime tout à la fin de ses tests** (enfants avant parents), puis vérifie par requête qu'il ne reste rien avec son préfixe. Voir le brief.
- Liste de tâches : un item par agent. Ne transmets jamais le rapport d'un agent à un autre.

**Sans outil Agent** (certains chats) : joue les rôles toi-même un par un, en repartant du brief à chaque fois sans relire les rapports précédents ; dis-le et propose de réduire à 3–6 agents.

## Phase 3 — Consolidation

Quand tous les rapports sont là :

```bash
python <skill_dir>/scripts/consolidate.py recette-runs/<run_id>
```

Produit `consolidated.json`, `backlog.json`, `rapport.md`, `rapport.html`, `GO_PENDING.md` et `nettoyage.json` (enregistrements que des agents n'ont pas pu supprimer).

**Balayage des données** : supprime via le MCP ce que liste `nettoyage.json`, puis cherche tout enregistrement restant dont le nom commence par `RCT<run_id>` sur les objets touchés, et supprime-le. Ces données sont des données de test du run, pas celles de l'utilisateur : ne supprime jamais un enregistrement sans ce préfixe. Note le résultat dans le rapport (« Données de test : 47 créées, 47 supprimées »).

Relis ensuite avec un œil d'architecte : fusionne les doublons ratés, sépare bug et choix produit, isole les constats contradictoires entre rôles dans « Décisions à prendre », écris la synthèse exécutive en tête de `rapport.md` (verdict, 5 points clés, couverture par processus, domaine, nombre d'agents, consigne). Publie le rapport (artifact HTML ou fichier) et envoie-le.

## Phase 4 — Gate GO (arrêt obligatoire)

Présente verdict, chiffres clés, lots par priorité, décisions à prendre et la syntaxe `GO` · `GO L1,L3` · `GO P0` · `NO GO`. Puis **arrête-toi**. Un « ok », « super » ou une question n'est pas un GO. En session non surveillée, laisse `GO_PENDING.md` et termine.

## Phase 5 — Corrections en parallèle (après GO)

Lis `references/improvement-brief.md`. Un agent par lot validé, tous dans le même tour, isolation `worktree` si le projet SFDX est un dépôt git (branche `recette/<run_id>/<lot>`). Chaque agent corrige, met à jour les tests Apex (≥ 85 % sur les classes touchées), valide puis déploie **sur la sandbox uniquement**, écrit `lots/<lot>.md`. Fusionne ensuite dans `recette/<run_id>/integration` et déploie sur la sandbox.

## Phase 6 — Re-test en parallèle

Relance en parallèle les seuls rôles concernés, en mode re-test (même règle de données éphémères). Termine par `rapport-final.md` : corrigé / non corrigé / régressions / reste à arbitrer.

## Limite à dire clairement

Tous les agents utilisent le même utilisateur Salesforce : ils jugent l'application **du point de vue métier** de leur rôle, pas avec ses droits réels. Le cloisonnement (« un fournisseur ne doit pas voir les marges ») est vérifié en lisant la configuration (partage, profils, permission sets, sites), pas en se connectant comme ce fournisseur. Les rapports le mentionnent.

## Règles transverses

- **Honnêteté** : un parcours non testé est `NON_TESTE` avec la raison, jamais `OK`.
- **Langue** : rapports en français sauf consigne contraire.
- **Reprise** : `recette-runs/<run_id>/` contient l'état ; relance seulement les agents sans rapport.

## Fichiers

- `references/persona-generation.md` — comment imaginer les rôles fonctionnels.
- `references/domain-catalog.md` — fonctions types par domaine.
- `references/personas-construction.md` — exemple détaillé BTP (20 rôles).
- `references/mcp-preflight.md` — MCP, garde-fous org, carte de l'app.
- `references/agent-brief.md` — brief d'un agent (+ re-test) et règles de données éphémères.
- `references/report-schema.md` — schéma JSON des rapports.
- `references/improvement-brief.md` — lecture du GO, agents de correction.
- `scripts/init_run.py` — crée le run puis les briefs.
- `scripts/consolidate.py` — consolidation, priorités, lots, rapports, liste de nettoyage.
