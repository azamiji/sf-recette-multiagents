# Imaginer les rôles fonctionnels (phase 1)

Un persona est une **fonction métier** dans l'entreprise cliente — CEO, directeur achats, DAF, acheteur, comptable, chef de projet, chef de chantier, chargé de clientèle, gestionnaire sinistres… — pas un profil, un rôle ou un permission set Salesforce. Tous les agents utilisent le même utilisateur MCP ; ce qui les distingue, c'est ce que leur fonction attend de l'application.

C'est l'orchestrateur qui choisit ces fonctions, avec son jugement : il connaît le métier, il a la carte de l'app, il a la consigne. Le catalogue n'est qu'une source d'inspiration.

## Entrées

- `run.json` : domaine, nombre d'agents N (3 à 20), consigne.
- `context.md` : ce que l'app fait dans le périmètre (objets, processus, flows, approbations, rapports, portails).

## Démarche

1. **Comprendre ce que l'app fait** : liste les processus métier présents dans le périmètre (ex. « demande d'achat → commande → réception → facture », « lead → opportunité → devis »). Un processus = une chaîne d'objets et d'automatisations.

2. **CEO toujours** (id `ceo`) : il juge le pilotage du périmètre — tableaux de bord, indicateurs, vision d'ensemble.

3. **Pour chaque processus, qui y intervient dans une vraie entreprise du domaine ?** Celui qui initie, celui qui exécute, celui qui valide, celui qui contrôle, celui qui consulte, l'acteur externe (client, fournisseur, partenaire) s'il y a un portail ou s'il devrait y en avoir un. Ce sont tes candidats.

4. **Ajouter les fonctions attendues mais absentes** : si le métier implique une fonction que l'app semble ignorer (aucun processus ne la sert : contrôle de gestion sans rapport de marge, QHSE sans objet incident…), garde-en une ou deux. Leurs constats seront des `MANQUE_FONCTIONNEL` — souvent les plus utiles.

5. **Choisir N rôles** : CEO + les N−1 candidats qui couvrent le plus de processus différents, avec priorité aux fonctions où l'enjeu est fort (argent, client, conformité, sécurité). Si N est petit (3–5), prends les fonctions les plus centrales du périmètre ; si N est grand, ajoute contrôle, support, externes, terrain/mobile.

6. **Respecter la consigne** : rien hors périmètre ; exclusions respectées.

7. **Pas de doublons** : deux fonctions aux parcours identiques = une seule. Si le périmètre ne justifie pas N rôles distincts, prends-en moins et dis pourquoi en une ligne.

8. **Parcours concrets** : 4 à 6 par rôle, rédigés comme des tâches de sa journée et rattachés aux objets/flows/pages réels (« Valider une commande au-dessus de 10 000 € — `Commande__c`, approbation `Validation_DA` »). Un parcours attendu sans support dans l'app reste dans la liste : l'agent le notera `NON_COUVERT`.

## Format de `personas.md`

Le titre `## <id> — <Libellé>` est lu par `init_run.py` : `id` en minuscules, chiffres et `_`.

```markdown
## ceo — CEO / Directeur général
- Type : interne
- Mission : piloter le pipeline et les prévisions de vente en un coup d'œil.
- Processus : pilotage commercial
- Parcours :
  1. Trouver le tableau de bord commercial en moins de 3 clics (Dashboard `Sales_Overview`).
  2. …
- Vigilance : cohérence des chiffres entre rapports, fraîcheur des données, mobile.

## directeur_achats — Directeur des achats
- Type : interne
- …

## fournisseur — Fournisseur
- Type : externe (portail ; testé via le même utilisateur MCP, cloisonnement vérifié par la configuration)
- …
```

## Présentation avant lancement

| # | Rôle | Mission (1 ligne) | Processus couverts |
|---|---|---|---|

Sous le tableau : une ligne pour les fonctions écartées notables (« Chef de chantier écarté : hors périmètre Sales »).
