# Phase 5 — Agents d'amélioration (après GO uniquement)

## Lire le GO

| Réponse utilisateur | Lots lancés |
|---|---|
| `GO` | tous les lots de `backlog.json` |
| `GO L1,L3` | lots listés |
| `GO P0` / `GO P0,P1` | lots dont la priorité max est dans la liste |
| `NO GO` | aucun ; termine en laissant le backlog |
| autre chose (« ok », « super », question) | **pas un GO** : réponds, rappelle la syntaxe, reste en attente |

Les « Décisions à prendre » listées dans le rapport ne sont jamais traitées sans réponse explicite de l'utilisateur sur l'arbitrage. Si un lot dépend d'une décision non tranchée, signale-le et ne le lance pas.

Écris `GO.md` : date, réponse exacte de l'utilisateur, lots retenus.

## Pré-requis

- Un projet SFDX local (dossier avec `sfdx-project.json`). S'il n'existe pas, récupère la metadata concernée par les lots dans un projet de travail (`retrieve`) avant de lancer les agents.
- Si c'est un dépôt git : un agent par lot avec `isolation: "worktree"`, branche `recette/<run_id>/<lot_id>`.
- Org cible = la sandbox de recette identifiée en phase 0. Jamais une production.

## Gabarit du brief d'un agent d'amélioration

```markdown
# Lot {{lot_id}} — {{lot_titre}}

Tu corriges les constats suivants issus d'une recette multi-personas de l'application Salesforce
« {{app_name}} » (domaine construction). Les autres lots sont traités en parallèle par d'autres
agents sur d'autres composants : ne modifie QUE les composants listés ci-dessous.

## Constats à traiter
{{constats_detail}}   <!-- id, titre, sévérité, personas, étapes, attendu/observé, suggestion -->

## Composants autorisés
{{composants}}

## Contexte
- Projet SFDX : {{project_path}} — branche {{branch}}
- Org sandbox : {{org_alias}} (IsSandbox = true vérifié)
- Outils : {{mcp_inventory}}

## Attendus
1. Corrige au plus près de la cause (pas de contournement dans l'UI si le défaut est dans le flow).
2. Apex touché → tests unitaires ajoutés/mis à jour, couverture ≥ 85 % sur les classes modifiées,
   tous les tests du lot verts.
3. Valide le déploiement (dry-run / validate) puis déploie sur la sandbox.
4. Si une correction exige une décision métier ou dépasse les composants autorisés, ne la fais pas :
   décris-la dans la section « Hors périmètre ».
5. Commit sur ta branche : `fix(recette-{{run_id}}): {{lot_id}} <résumé>`.

## Livrable
`{{run_dir}}/lots/{{lot_id}}.md` : constats traités (id → changement), fichiers modifiés,
résultats de tests/déploiement, risques, hors périmètre.
Message final : 5 lignes max.
```

## Après les agents

1. Récupère chaque `lots/<lot>.md` ; un lot en échec n'empêche pas les autres.
2. Fusionne les branches dans `recette/<run_id>/integration`, relance la validation globale, déploie sur la sandbox.
3. Phase 6 : re-test (variante en bas de `agent-brief.md`) des seules personas présentes dans `personas_impactees` des constats traités.
4. `rapport-final.md` : tableau constat → lot → résultat re-test ; régressions ; reste à faire ; décisions toujours ouvertes.
5. Propose (sans exécuter) : PR vers la branche principale, nettoyage des données `RCT<run_id>_*`, création de tickets pour le hors-périmètre.
