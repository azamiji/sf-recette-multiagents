# Génération dynamique des personas (phase 1)

Objectif : 20 personas (ou le nombre demandé) **propres à ce projet**, pas une liste générique. L'org réelle dit qui utilise l'application ; le domaine dit qui *devrait* l'utiliser ; le périmètre dit ce qu'on regarde. Les écarts entre les deux premiers sont souvent les constats les plus utiles (« aucun rôle Contrôle de gestion n'a accès aux marges »).

## Entrées

- `run.json` : domaine, consigne libre, nombre demandé (20 par défaut).
- `context.md` : carte de l'app dans le périmètre (apps, objets, flows, pages, sites, rapports).
- Utilisateurs actifs : profil, rôle, permission sets, `UserType`.
- `references/domain-catalog.md` (et `personas-construction.md` pour le BTP).

## Règles

1. **CEO toujours**, id `ceo`. Sa mission s'adapte au périmètre : sur « uniquement l'app Sales », il juge le pilotage commercial (pipeline, prévisions, tableaux de bord), pas les chantiers.

2. **Personas issus de l'org (source ORG)** — la majorité des places. Regroupe les utilisateurs actifs du périmètre par combinaison *profil + rôle + permission sets clés* ; chaque groupe distinct qui a un vrai usage métier du périmètre devient un candidat. Indices d'usage : accès en écriture aux objets du périmètre, onglets de l'app, files d'attente, étapes d'approbation, assignation de records.
   - Types portail (`PowerPartner`, `CspLitePortal`, `PowerCustomerSuccess`…) → personas externes (fournisseur, partenaire, client, agent…) s'ils accèdent au périmètre.
   - Nomme le persona par son **métier** (« Chargé de clientèle »), pas par le nom technique du profil (`CDM_Agent_Profile`) — le profil va dans le champ utilisateur.

3. **Personas issus du domaine (source CATALOGUE)** — pour les rôles que le domaine attend dans ce périmètre mais que l'org ne porte pas (aucun profil/permission set correspondant). Limite-les à environ un quart des places : ils testent avec l'utilisateur le plus proche ou en mode `ANALYSE_DROITS`, et leurs constats seront surtout des `MANQUE_FONCTIONNEL`.

4. **Rôles transverses** à considérer selon les places restantes : administrateur Salesforce (sécurité, droits, santé technique), un rôle de contrôle (finance, conformité, qualité, audit selon le domaine), un utilisateur mobile/terrain si l'app est utilisée en mobilité.

5. **Le périmètre filtre tout** : un candidat dont le métier ne touche pas le périmètre est écarté, même s'il existe dans l'org. Les exclusions explicites de la consigne (« pas le portail ») sont respectées.

6. **Pas de doublons** : deux personas avec le même profil et les mêmes parcours = un seul. Si le périmètre ne justifie pas le nombre demandé, ne fabrique pas de faux rôles : prends moins de personas et dis pourquoi en une ligne. À l'inverse, s'il y a plus de candidats que de places, priorise : volume d'utilisateurs, criticité métier (argent, conformité, client), diversité des droits.

7. **Parcours concrets** : 4 à 6 parcours par persona, rédigés comme des tâches métier et rattachés aux objets/flows/pages réels de `context.md` (ex. « Convertir un lead en opportunité — Lead, flow `Lead_Qualification` »). Un parcours attendu sans support dans l'org reste dans la liste : l'agent le notera `NON_COUVERT`.

## Format de `personas.md`

Le titre `## <id> — <Libellé>` est lu par `init_run.py` : `id` en minuscules, chiffres et `_` uniquement.

```markdown
## ceo — CEO / Directeur général
- Source : ORG (profil Direction, 2 utilisateurs)
- Accès : I — utilisateur de test : ceo.demo@client.sbx (LOGIN_AS)
- Mission : piloter le pipeline et les prévisions de vente en un coup d'œil.
- Parcours :
  1. Trouver le tableau de bord commercial en < 3 clics (Dashboard `Sales_Overview`).
  2. …
- Vigilance : cohérence des chiffres entre rapports, fraîcheur, mobile.

## charge_clientele — Chargé de clientèle
- Source : ORG (profil Agent + permission set `Credit_Conso`, 48 utilisateurs)
- Accès : I — …
```

`Accès` : `I` interne, `E` externe (portail), `A` admin.

## Présentation à l'utilisateur

Tableau compact avant lancement :

| # | Persona | Source | Utilisateur / mode | Mission (1 ligne) |
|---|---|---|---|---|

Sous le tableau, une ligne pour les rôles écartés notables (« Chef de chantier écarté : hors périmètre Sales ») et une ligne pour les personas en mode dégradé (pas d'utilisateur de test).
