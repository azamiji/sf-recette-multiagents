# Pré-vol : MCP, org et connexion des personas

Le skill ne suppose aucun nom d'outil précis : il s'appuie sur les MCP déjà configurés chez l'utilisateur. Les sous-agents lancés avec l'outil Agent héritent des mêmes serveurs MCP que l'orchestrateur, donc l'inventaire fait ici vaut pour tous.

## 1. Inventaire des capacités

Repère les outils disponibles (y compris différés : cherche-les avec ToolSearch, ex. `salesforce soql`, `playwright browser`, `chrome navigate`) et classe-les par **capacité**, pas par nom :

| Capacité | Exemples d'outils (selon l'installation) | Usage dans la recette |
|---|---|---|
| Requête données | Salesforce DX MCP (`run_soql_query`…), `sf data query` | vérifier les données, droits, résultats des parcours |
| Metadata | Salesforce DX MCP (`retrieve_metadata`…), `sf project retrieve` | carte de l'app, composants suspects |
| Déploiement / tests | Salesforce DX MCP (`deploy_metadata`, `run_apex_test`…), `sf project deploy`, `sf apex run test` | phase 5 uniquement |
| Navigation UI | Playwright MCP, Claude in Chrome, navigateur intégré | parcours réels, captures, accessibilité |
| Ticketing (option) | Jira, Azure DevOps… | créer les tickets après GO si l'utilisateur le veut |

Écris le résultat dans `context.md` → section « Outils ». S'il n'y a **aucun** outil Salesforce (ni MCP ni `sf`), dis-le à l'utilisateur et arrête : une recette sans accès à l'org n'aurait que des constats inventés.

S'il n'y a pas de navigateur, la recette reste possible en mode données/droits, mais la fluidité, l'accessibilité et la facilité d'usage ne seront pas évaluées : préviens l'utilisateur et fais apparaître la limite dans chaque rapport.

## 2. Garde-fous org

Requête : `SELECT Id, Name, IsSandbox, InstanceName, OrganizationType FROM Organization`

- `IsSandbox = false` → **production** : recette en lecture seule, pas de création de données, pas de phase 5 de déploiement. Demande confirmation à l'utilisateur avant de continuer même en lecture.
- Note l'alias utilisé par le MCP / `sf` (org par défaut) et vérifie que c'est bien l'org que l'utilisateur a en tête si plusieurs orgs sont authentifiées.

## 3. Carte de l'application

Requêtes utiles (Tooling API si disponible) :
- Apps : `SELECT DeveloperName, Label FROM AppMenuItem WHERE Type = 'TabSet'`
- Objets custom : `SELECT QualifiedApiName, Label FROM EntityDefinition WHERE IsCustomizable = true AND QualifiedApiName LIKE '%__c'`
- Flows actifs : `SELECT ApiName, ProcessType, TriggerType FROM FlowDefinitionView WHERE IsActive = true`
- Profils / permission sets : `SELECT Name, Label, IsCustom, Profile.Name FROM PermissionSet`
- Sites Experience Cloud : `SELECT Name, Status, UrlPathPrefix FROM Network`
- Rapports / dashboards : `SELECT Name, FolderName FROM Report` / `FROM Dashboard`
- Erreurs récentes : `SELECT … FROM FlowInterview WHERE …` ou e-mails d'erreur Apex si accessibles

Résume par **domaine métier** (achats, chantier, finance, sous-traitance, commercial, QHSE, SAV, RH, juridique) : objets, flows, pages, rapports. C'est la référence pour juger la couverture.

## 4. Mapping persona → utilisateur

`SELECT Id, Username, Name, Profile.Name, UserRole.Name, IsActive, UserType FROM User WHERE IsActive = true`
+ `PermissionSetAssignment` pour les permission sets.

Associe chaque persona à l'utilisateur dont le profil/rôle/permission sets correspondent le mieux (nom, objets accessibles). `UserType` `PowerPartner` / `CspLitePortal` / `PowerCustomerSuccess` = utilisateurs portail pour fournisseur / sous-traitant / maître d'ouvrage.

Modes de connexion, par ordre de préférence :
1. `IDENTIFIANTS` — l'utilisateur fournit `personas.local.yaml` (gitignoré) :
   ```yaml
   acheteur: {username: acheteur.test@client.sbx, password: "...", login_url: https://test.salesforce.com}
   fournisseur: {username: ..., password: "...", login_url: https://<site>.my.site.com/fournisseurs/login}
   ```
2. `LOGIN_AS` — un admin se connecte « en tant que » via le navigateur (Setup → Utilisateurs → Connexion). Nécessite que l'option « Les administrateurs peuvent se connecter en tant que n'importe quel utilisateur » soit active. Une seule session Login-As par contexte navigateur → sérialiser.
3. `PORTAIL` — Login-As vers un utilisateur Experience Cloud depuis la fiche contact.
4. `ANALYSE_DROITS` — repli : test en admin + analyse SOQL des droits du profil cible (`ObjectPermissions`, `FieldPermissions`, `SetupEntityAccess`, `UserRecordAccess`). Fluidité/facilité notées sous réserve.

Consigne le tableau dans `plan.md`. Signale à l'utilisateur, en une ligne par cas, les personas en mode dégradé et ce qui les débloquerait (créer un utilisateur, fournir des identifiants).

## 5. Contextes navigateur

Détermine combien de sessions UI peuvent tourner en parallèle sans se marcher dessus :
- Playwright MCP lancé avec `--isolated` ou plusieurs profils → N contextes.
- Un seul Chrome partagé / un seul navigateur intégré → 1 (vagues séquentielles pour l'UI).
Inscris `vague` dans chaque brief en conséquence.
