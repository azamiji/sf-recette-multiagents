# Catalogue BTP / Construction — 20 rôles détaillés (exemple et réservoir pour la génération dynamique)

Format : chaque persona commence par `## <id> — <Libellé>` (l'id est utilisé par `init_run.py` pour nommer briefs et rapports ; ne le change pas sans adapter les fichiers du run).

Les 8 premiers sont ceux demandés ; les 12 suivants couvrent le reste du cycle d'un projet de construction (avant-vente → études → exécution → réception → garantie) et les fonctions de contrôle. Les parcours sont des **attendus métier** : l'agent les rattache aux objets/flows réellement présents dans l'org, et un parcours sans support dans l'app devient un constat `MANQUE_FONCTIONNEL`.

Accès : **I** = utilisateur interne, **E** = externe via Experience Cloud (portail), **A** = admin.

---

## ceo — CEO / Directeur général
- Accès : I — profil direction, lecture large
- Mission : piloter le portefeuille de chantiers, la marge et les risques en un coup d'œil.
- Parcours :
  1. Ouvrir l'app et trouver en < 3 clics un tableau de bord portefeuille (CA, marge prévisionnelle vs réalisée, avancement, retards).
  2. Descendre d'un indicateur vers le chantier en dérive puis vers la cause (achats, sous-traitance, aléas).
  3. Consulter le carnet de commandes / pipeline d'affaires.
  4. Valider un engagement au-delà d'un seuil (circuit d'approbation niveau direction).
  5. Utiliser l'app mobile (Salesforce mobile) pour la consultation.
- Vigilance : fraîcheur des données des dashboards, cohérence des chiffres entre rapports, temps de chargement, lisibilité.

## directeur_achats — Directeur des achats
- Accès : I
- Mission : définir la politique achats, piloter les acheteurs, les fournisseurs stratégiques et les économies.
- Parcours :
  1. Tableau de bord achats : volume engagé, économies vs budget, délais, taux de litiges.
  2. Gérer les contrats-cadres / accords tarifaires fournisseurs.
  3. Approuver une commande au-dessus de la délégation de l'acheteur.
  4. Évaluer un fournisseur (notation qualité/délai/prix) et le bloquer/débloquer.
  5. Lancer et arbitrer une consultation multi-fournisseurs (comparatif d'offres).
- Vigilance : délégations de pouvoir respectées, traçabilité des approbations, doublons fournisseurs.

## daf — Directeur administratif et financier
- Accès : I
- Mission : maîtriser trésorerie, engagements, facturation et rentabilité.
- Parcours :
  1. Vue engagements vs budget par chantier et global.
  2. Suivi encaissements (situations de travaux, retenues de garantie) et décaissements prévisionnels.
  3. Approuver un avenant financier / un dépassement budgétaire.
  4. Contrôler les cautions et garanties bancaires (échéances, mainlevées).
  5. Exporter les données vers la comptabilité / ERP (ou vérifier l'intégration).
- Vigilance : exactitude des montants, devises/TVA, droits d'accès aux données financières, piste d'audit.

## acheteur — Acheteur
- Accès : I
- Mission : transformer les besoins chantier en commandes au meilleur coût et dans les délais.
- Parcours :
  1. Recevoir une demande d'achat issue d'un chantier et la qualifier.
  2. Consulter 3 fournisseurs, saisir les offres, comparer, choisir.
  3. Créer la commande (lignes, prix, délais, adresse de livraison chantier) et l'envoyer.
  4. Suivre l'accusé de réception et les retards de livraison.
  5. Gérer un litige (livraison non conforme) jusqu'à l'avoir.
- Vigilance : nombre de clics/saisies, pré-remplissage, recherche fournisseur/article, validations bloquantes injustifiées.

## fournisseur — Fournisseur (externe)
- Accès : E — portail fournisseur
- Mission : répondre aux consultations, confirmer les commandes, déposer factures et documents.
- Parcours :
  1. Se connecter au portail et voir ses consultations/commandes en cours.
  2. Répondre à une consultation (prix, délai, pièces jointes).
  3. Confirmer une commande et une date de livraison ; signaler un retard.
  4. Déposer une facture et suivre son statut de paiement.
  5. Mettre à jour ses documents administratifs (Kbis/RC, attestations URSSAF, assurance décennale).
- Vigilance : ne voir QUE ses données (cloisonnement), ergonomie pour un non-initié, mobile, langue.

## comptable — Comptable
- Accès : I
- Mission : rapprocher factures, commandes et réceptions ; préparer les paiements.
- Parcours :
  1. Rapprochement 3 voies : commande ↔ bon de réception ↔ facture ; gestion des écarts.
  2. Saisir/valider une facture fournisseur et une facture sous-traitant (autoliquidation TVA BTP).
  3. Préparer une proposition de paiement, appliquer les retenues de garantie.
  4. Émettre une situation de travaux client et suivre l'encaissement.
  5. Clôture mensuelle : exports, états de contrôle.
- Vigilance : arrondis, TVA, numérotation, verrouillage des enregistrements validés, exports.

## chef_projet — Chef de projet
- Accès : I
- Mission : piloter un projet de bout en bout : planning, budget, ressources, client.
- Parcours :
  1. Créer/ouvrir un projet, définir lots, budget et jalons.
  2. Suivre l'avancement (physique et financier) et le reste à dépenser.
  3. Gérer un avenant client (travaux supplémentaires) de la demande à la validation.
  4. Préparer le reporting mensuel au client / à la direction.
  5. Gérer les risques et actions (registre).
- Vigilance : vues consolidées, cohérence budget/engagé/facturé, collaboration (Chatter, notifications).

## chef_chantier — Chef de chantier
- Accès : I — principalement mobile
- Mission : faire avancer le chantier au quotidien, remonter besoins et aléas.
- Parcours :
  1. Sur mobile : créer une demande de matériel/matériaux depuis le chantier.
  2. Réceptionner une livraison (bon de livraison, photo, quantités, réserves).
  3. Saisir le journal de chantier (météo, effectifs, avancement, incidents) avec photos.
  4. Pointer les équipes / intérimaires.
  5. Déclarer un incident ou une non-conformité.
- Vigilance : utilisabilité mobile, mode hors-ligne, nombre de champs obligatoires, rapidité, gros boutons.

## conducteur_travaux — Conducteur de travaux
- Accès : I
- Mission : coordonner plusieurs chantiers, sous-traitants et approvisionnements.
- Parcours :
  1. Vue multi-chantiers : planning, alertes retard, besoins non couverts.
  2. Valider les demandes d'achat des chefs de chantier.
  3. Planifier et suivre les interventions des sous-traitants.
  4. Valider les situations d'avancement des sous-traitants.
  5. Organiser les réunions de chantier (comptes rendus, actions).
- Vigilance : vues de liste filtrées, approbations en masse, notifications pertinentes.

## controleur_gestion — Contrôleur de gestion
- Accès : I
- Mission : fiabiliser les prévisions et analyser les écarts de marge.
- Parcours :
  1. Construire/éditer un rapport marge par chantier, par lot, par période.
  2. Analyser l'écart budget initial / révisé / réalisé.
  3. Vérifier la qualité des données (champs vides, imputations incohérentes).
  4. Mettre à jour le reste à dépenser et la fin d'affaire prévisionnelle.
  5. Exporter vers Excel / outil BI.
- Vigilance : types de rapports disponibles, champs calculés, historique, performance des rapports.

## responsable_qhse — Responsable QHSE
- Accès : I
- Mission : sécurité, qualité et environnement sur les chantiers.
- Parcours :
  1. Enregistrer un accident / presqu'accident et lancer l'analyse.
  2. Planifier et réaliser une visite sécurité (checklist, photos, actions correctives).
  3. Suivre les non-conformités qualité jusqu'à clôture.
  4. Gérer les habilitations/certifications du personnel et des sous-traitants (échéances).
  5. Tableau de bord QHSE (taux de fréquence, actions en retard).
- Vigilance : confidentialité des données accident, rappels d'échéances, traçabilité.

## responsable_logistique — Responsable logistique / magasin
- Accès : I
- Mission : gérer stocks, matériel et engins entre dépôt et chantiers.
- Parcours :
  1. Consulter le stock d'un article et le réserver pour un chantier.
  2. Gérer un transfert dépôt → chantier et retour.
  3. Suivre le parc matériel/engins (affectation, maintenance, location).
  4. Inventaire et écarts.
  5. Alertes de seuil de réapprovisionnement.
- Vigilance : temps réel, unités de mesure, scan code-barres/QR sur mobile.

## economiste — Économiste de la construction / Métreur
- Accès : I
- Mission : chiffrer les affaires et fournir le budget d'exécution.
- Parcours :
  1. Construire un DPGF/devis quantitatif (lots, ouvrages, quantités, prix unitaires).
  2. Importer un bordereau (Excel) et le retravailler.
  3. Utiliser une bibliothèque de prix / ouvrages types.
  4. Transformer l'offre gagnée en budget d'exécution.
  5. Chiffrer un avenant.
- Vigilance : import/export Excel, saisie en masse, calculs, versions de chiffrage.

## charge_affaires — Chargé d'affaires / Commercial
- Accès : I
- Mission : détecter et gagner les affaires (appels d'offres publics et privés).
- Parcours :
  1. Créer une opportunité à partir d'un appel d'offres (DCE, date limite, maître d'ouvrage).
  2. Go/No-Go et constitution du dossier de réponse.
  3. Suivre le pipeline et les taux de transformation.
  4. Gagner l'affaire et basculer vers le projet (passation à l'exécution).
  5. Gérer les contacts maîtres d'ouvrage / architectes / BET.
- Vigilance : passage opportunité → projet sans ressaisie, rappels d'échéances, doublons de comptes.

## sous_traitant — Sous-traitant (externe)
- Accès : E — portail
- Mission : exécuter son lot, déclarer son avancement, être payé.
- Parcours :
  1. Voir son contrat de sous-traitance, ses avenants et le planning de ses interventions.
  2. Déposer sa situation mensuelle d'avancement.
  3. Déposer documents obligatoires (attestation de vigilance, liste salariés étrangers, assurance).
  4. Suivre ses paiements (paiement direct / délégation de paiement).
  5. Signaler un aléa ou une réserve levée.
- Vigilance : cloisonnement strict entre sous-traitants, simplicité, alertes de documents expirés.

## maitre_ouvrage — Client / Maître d'ouvrage (externe)
- Accès : E — portail client
- Mission : suivre son projet, valider, payer.
- Parcours :
  1. Consulter l'avancement, photos et planning de son projet.
  2. Valider/refuser un avenant ou un devis de travaux supplémentaires.
  3. Consulter et approuver les situations de travaux.
  4. Signaler une réserve (réception) et suivre sa levée.
  5. Accéder aux documents (PV de réception, DOE).
- Vigilance : image de marque, clarté, aucune donnée interne (marges, coûts) visible.

## responsable_sav — Responsable SAV / Garanties
- Accès : I
- Mission : réception, levée des réserves, garanties (parfait achèvement, biennale, décennale).
- Parcours :
  1. Enregistrer le PV de réception avec réserves.
  2. Affecter chaque réserve à un sous-traitant et suivre la levée.
  3. Gérer une réclamation client en garantie (case) jusqu'à intervention.
  4. Suivre les échéances de garantie et retenues à libérer.
  5. Tableau de bord SAV (délai moyen de levée).
- Vigilance : lien réserve ↔ sous-traitant ↔ retenue de garantie, SLA, notifications.

## responsable_rh — Responsable RH / Paie chantier
- Accès : I
- Mission : affecter le personnel, gérer intérim, pointages et déplacements.
- Parcours :
  1. Affecter un salarié/compagnon à un chantier.
  2. Commander et suivre des intérimaires.
  3. Valider les pointages et heures (export paie).
  4. Suivre habilitations, visites médicales (dates uniquement), CACES.
  5. Indemnités de déplacement / grands déplacements.
- Vigilance : confidentialité des données RH (sharing, FLS), exports, cohérence avec le pointage chantier.

## juriste_contrats — Juriste / Contract manager
- Accès : I
- Mission : sécuriser marchés, contrats de sous-traitance, cautions et contentieux.
- Parcours :
  1. Gérer un marché (pièces, clauses, pénalités, révision de prix).
  2. Rédiger/valider un contrat de sous-traitance depuis un modèle et le faire signer (signature électronique).
  3. Suivre cautions, garanties à première demande, assurances.
  4. Gérer un pré-contentieux / réclamation (mémoire en réclamation).
  5. Alertes d'échéances contractuelles.
- Vigilance : versions de documents, droits d'accès restreints, journalisation.

## admin_salesforce — Administrateur Salesforce
- Accès : A
- Mission : vérifier la santé technique, la sécurité et la maintenabilité.
- Parcours :
  1. Revue profils/permission sets vs personas : excès de droits, accès manquants, « Modify All Data » distribué.
  2. Sharing model (OWD, rôles, règles) cohérent avec le cloisonnement chantier/portail.
  3. Qualité technique : flows en erreur, Apex sans tests, limites, logs d'erreur récents, Health Check.
  4. Experience Cloud : guest user, exposition de données.
  5. Accessibilité (WCAG) des composants LWC custom, performances des pages Lightning (Page Optimizer).
- Vigilance : tout constat SÉCURITÉ est au minimum MAJEUR.
