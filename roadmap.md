# Roadmap Umagus - Management de l'innovation

## Vision

Umagus evolue d'un suivi projet vers une plateforme de pilotage strategique de l'innovation:

- niveau organisation (entreprise / organisme),
- niveau portefeuille (projets, prototypes, arbitrages),
- niveau strategie (prospective, impact, orientation des chantiers).

Objectif: relier la veille et les scenarios aux decisions d'exploration, aux projets/prototypes, puis aux impacts mesures.

---

## Principes de construction

- Construire par couches: fondations data/permissions avant modules avances.
- Garder un noyau commun pour eviter les silos (organization, project, prototype, decision, impact).
- Livrer des increments testables UI + API a chaque etape.
- Conserver la simplicite UX (friction minimale, creation a la volee, progressive disclosure).

---

## Phase 1 - Fondations multi-organisation (priorite immediate)

### Objectif

Permettre a une entreprise/organisme de gerer son propre portefeuille.

### Scope

- Entite `Organization` (company/organisme).
- Liaison utilisateurs-organisation (`OrganizationUser`) avec roles:
  - owner
  - admin
  - member
  - viewer
- Rattacher les `Project` a une `Organization`.
- Ajouter la notion d'organisation active dans l'app (scope des vues et actions).

### Livrables

- Modeles SQLAlchemy + migrations Alembic.
- Endpoints API de base:
  - creation organisation,
  - listing des organisations de l'utilisateur,
  - selection d'organisation active.
- Adaptation UI:
  - selecteur d'organisation (header/menu),
  - pages projets scopees par organisation.

### Critere d'acceptation

- Un utilisateur peut appartenir a plusieurs organisations.
- Les projets affiches/crees concernent uniquement l'organisation active.
- Un utilisateur d'une organisation A ne voit rien de l'organisation B.

---

## Phase 2 - Portefeuille projets + prototypes (execution)

### Objectif

Passer du suivi projet a l'engagement des actions, en priorisant le prototype.

### Scope

- Renforcement module projets:
  - statut, jalons, parties prenantes (MVP),
  - probleme traite, solutions envisagees (MVP).
- Module `Prototype`:
  - objectif,
  - hypotheses a tester,
  - actions,
  - resultats/preuves,
  - decision (go / no-go / pivot).

### Livrables

- Ecrans:
  - fiche projet,
  - page prototype liee au projet,
  - actions a lancer ("next actions").
- API CRUD projets/prototypes.

### Critere d'acceptation

- Depuis un projet, on peut creer un prototype et enregistrer une decision.
- La decision genere explicitement la prochaine action.

---

## Phase 3 - Module cartographie prospective

### Objectif

Structurer le radar d'anticipation et le lien avec les besoins d'exploration.

### Scope

- Veille:
  - signaux,
  - sources,
  - tendances / megatendances.
- Variables structurantes:
  - parametres/curseurs.
- Scenarios:
  - hypotheses de trajectoires.
- Radar:
  - monitorer,
  - surveiller,
  - explorer.

### Livrables

- Ecran radar (vue synthese).
- Ecran scenarios + variables.
- Liens "scenario -> besoin d'exploration / chantier / etude".

### Critere d'acceptation

- Chaque element du radar peut etre rattache a une orientation d'exploration.
- Une trajectoire roadmap (notamment R&D) est justifiable par des elements de prospective.

---

## Phase 4 - Module cartographie des impacts

### Objectif

Relier strategie, portefeuille et resultats mesurables.

### Scope

- Impacts potentiels (avant projet/prototype).
- Impacts mesures (apres execution).
- Comparaison attendu vs realise.
- Axes d'impacts (exemples):
  - business model,
  - RH/competences,
  - operations,
  - environnement,
  - client/usages.

### Livrables

- Ecran "Impact map" par organisation.
- Fiche impact par projet/prototype.
- Indicateurs de progression (qualitatifs/quantitatifs simples en MVP).

### Critere d'acceptation

- Un projet/prototype contient ses impacts attendus et mesures.
- Le portefeuille affiche une vue consolidee des impacts.

---

## Phase 5 - Gouvernance et industrialisation

### Objectif

Passer d'un MVP fonctionnel a une plateforme robuste.

### Scope

- RBAC complet (roles fins par module).
- Journal d'audit (actions critiques).
- Workflow de decision (comite/revue).
- Qualite logicielle:
  - tests integration/contrats API,
  - observabilite,
  - securite session/permissions.

### Livrables

- Matrice roles/permissions.
- Audit log consultable.
- Pipeline CI/CD avec checks renforces.

---

## Plan d'execution (ordre recommande)

1. Phase 1 (multi-organisation)  
2. Phase 2 (projets + prototypes)  
3. Phase 3 (prospective)  
4. Phase 4 (impacts)  
5. Phase 5 (gouvernance/industrialisation)

---

## Prochaine iteration concrete (Sprint suivant)

Sprint cible: **Phase 1 - Foundations**

- [ ] Ajouter `Organization` et `OrganizationUser` (modeles + migrations).
- [ ] Rattacher `Project` a `Organization`.
- [ ] Ajouter endpoints "mes organisations" et "organisation active".
- [ ] Ajouter selecteur d'organisation dans l'UI.
- [ ] Scoper la page `/projects` a l'organisation active.
- [ ] Ajouter tests d'isolation inter-organisations.

