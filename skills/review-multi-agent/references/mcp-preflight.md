# Connexion (phase 0) : MCP, garde-fous, carte de l'app

Le skill s'appuie sur le MCP Salesforce déjà configuré chez l'utilisateur. Les agents lancés avec l'outil Agent héritent des mêmes MCP : **un seul utilisateur Salesforce pour tous**, aucun utilisateur de test à créer, aucun identifiant à gérer.

## 1. Inventaire des capacités

Cherche les outils (y compris différés, via ToolSearch : `salesforce`, `soql`, `discover`, `playwright`, `browser`) et classe-les par capacité :

| Capacité | Exemples | Usage |
|---|---|---|
| MCP d'org « à playbooks » | `discover` / `describe` / `dispatch_readonly` / `dispatch` | en priorité : chercher le playbook, le lire, l'exécuter. `dispatch_readonly` pour lire ; `dispatch` pour créer/supprimer les données de test préfixées (sandbox) et en phase 5 après GO |
| Requête données | Salesforce DX MCP (`run_soql_query`…), `sf data query` | carte de l'app, vérification des parcours |
| Écriture données | Salesforce DX MCP, `sf data create/delete record` | données de test éphémères |
| Metadata / déploiement / tests | Salesforce DX MCP, `sf project retrieve/deploy`, `sf apex run test` | phase 5 uniquement |
| Navigation UI | Playwright, Claude in Chrome, navigateur intégré | fluidité, accessibilité, captures |

Écris le résultat dans `context.md`. Sans accès Salesforce : dis-le et arrête. Sans navigateur : la recette reste possible par le MCP, mais fluidité et accessibilité seront évaluées sur la configuration (pages, nombre de champs, composants) plutôt qu'à l'écran ; préviens l'utilisateur.

**Vérifie la suppression** : les données de test doivent être supprimées après les tests. Confirme que l'utilisateur MCP peut supprimer sur les objets du périmètre (droits objet `PermissionsDelete`, ou un essai de création/suppression d'un enregistrement préfixé). Si ce n'est pas possible, préviens l'utilisateur avant de lancer : soit il accepte une recette en lecture seule, soit il donne le droit de suppression.

## 2. Garde-fous org

`SELECT Id, Name, IsSandbox, InstanceName, OrganizationType FROM Organization`

- `IsSandbox = false` → **production** : lecture seule, aucune donnée créée, pas de phase 5. Demande confirmation avant de continuer même en lecture.
- Plusieurs orgs authentifiées : vérifie que c'est bien celle que l'utilisateur vise.

## 3. Carte de l'application

Requêtes utiles (Tooling API si disponible) :
- Apps : `SELECT DeveloperName, Label FROM AppMenuItem WHERE Type = 'TabSet'`
- Objets custom : `SELECT QualifiedApiName, Label FROM EntityDefinition WHERE IsCustomizable = true AND QualifiedApiName LIKE '%__c'`
- Flows actifs : `SELECT ApiName, ProcessType, TriggerType FROM FlowDefinitionView WHERE IsActive = true`
- Processus d'approbation, sites (`Network`), rapports, dashboards, Lightning pages.

**Périmètre** : si la consigne limite la recette (une app, un processus, une exclusion), ne garde que les onglets de l'app, leurs objets, les flows déclenchés sur ces objets, leurs pages et rapports. Note ce qui a été exclu.

Résume par **processus métier** (ex. « demande d'achat → commande → réception → facture ») : objets, automatisations, écrans, rapports. C'est la base pour imaginer les rôles (phase 1) et juger la couverture.

Pour juger plus tard le cloisonnement entre fonctions, note aussi le modèle de partage des objets du périmètre (OWD, règles de partage, sites Experience Cloud).
