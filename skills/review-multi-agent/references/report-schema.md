# Schéma du rapport persona (`reports/<persona_id>.json`)

`scripts/consolidate.py` lit ces fichiers : respecte les noms de champs et les valeurs d'énumération exactement, sinon le constat est rejeté et signalé dans le rapport consolidé.

```json
{
  "schema_version": "1.0",
  "run_id": "20261118-1930",
  "persona_id": "acheteur",
  "persona_label": "Acheteur",
  "utilisateur_teste": "acheteur.test@client.sandbox (profil Achats)",
  "mode_acces": "LOGIN_AS",
  "debut": "2026-11-18T19:40:00Z",
  "fin": "2026-11-18T20:25:00Z",
  "verdict": "PRET_AVEC_RESERVES",
  "synthese": "3 à 5 phrases en français.",
  "scores": {
    "couverture": 3,
    "fluidite": 4,
    "facilite": 2,
    "accessibilite": 3,
    "fiabilite": 4
  },
  "parcours": [
    {
      "id": "P1",
      "titre": "Qualifier une demande d'achat chantier",
      "statut": "PARTIEL",
      "nb_ecrans": 5,
      "nb_clics": 14,
      "observations": "La demande arrive mais sans le code chantier."
    }
  ],
  "constats": [
    {
      "id": "acheteur-001",
      "type": "BUG",
      "severite": "MAJEUR",
      "titre": "Le code chantier n'est pas reporté sur la commande",
      "description": "…",
      "etapes": ["Ouvrir la DA RCT…", "Cliquer « Créer commande »", "…"],
      "attendu": "Code chantier pré-rempli",
      "observe": "Champ vide, saisie manuelle obligatoire",
      "composant": {"type": "Flow", "nom": "DA_to_Commande"},
      "parcours": "P1",
      "preuves": ["evidence/acheteur/p1-commande.png"],
      "suggestion": "Mapper Chantier__c dans le flow de conversion."
    }
  ],
  "donnees_creees": [{"objet": "Commande__c", "id": "a0X…", "nom": "RCT20261118-1930_ACHETEUR_CMD1"}],
  "limites": "Pas de test mobile : aucun appareil disponible."
}
```

## Énumérations

| Champ | Valeurs |
|---|---|
| `mode_acces` | `IDENTIFIANTS`, `LOGIN_AS`, `PORTAIL`, `ANALYSE_DROITS`, `ADMIN` |
| `verdict` | `PRET`, `PRET_AVEC_RESERVES`, `NON_PRET` |
| `scores.*` | entier 0–5 (0 = inexistant, 5 = excellent). Couverture = part des parcours attendus réellement supportés par l'app |
| `parcours[].statut` | `OK`, `PARTIEL`, `KO`, `NON_COUVERT` (l'app ne le permet pas), `BLOQUE` (empêché par un bug/accès), `NON_TESTE` (limite du test) |
| `constats[].type` | `BUG`, `MANQUE_FONCTIONNEL`, `UX`, `ACCESSIBILITE`, `PERFORMANCE`, `SECURITE`, `DONNEES`, `AMELIORATION`, `REGRESSION` |
| `constats[].severite` | `BLOQUANT`, `MAJEUR`, `MINEUR`, `COSMETIQUE` |
| `composant.type` | `Flow`, `LWC`, `Aura`, `Apex`, `Layout`, `LightningPage`, `Permission`, `Sharing`, `Validation`, `Rapport`, `Dashboard`, `ExperienceCloud`, `Integration`, `Donnees`, `Autre` |

## Règles de sévérité

- `BLOQUANT` : impossible de terminer un parcours métier essentiel, perte/corruption de données, fuite de données vers un rôle non autorisé.
- `MAJEUR` : contournement possible mais coûteux ; erreur de calcul ; tout constat `SECURITE`.
- `MINEUR` : gêne réelle sans impact sur le résultat.
- `COSMETIQUE` : libellés, alignements, fautes.

`composant.nom` : nom API exact quand il est connu (`DA_to_Commande`, `Commande__c.Montant_TTC__c`), sinon `"inconnu"` — la consolidation regroupe les lots par composant, un nom précis évite des lots fourre-tout.

## Champ supplémentaire en re-test

```json
"verifications": [{"constat_id": "acheteur-001", "resultat": "CORRIGE", "commentaire": "…"}]
```
`resultat` ∈ `CORRIGE`, `NON_CORRIGE`, `PARTIEL`.
