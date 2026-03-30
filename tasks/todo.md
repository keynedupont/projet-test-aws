# TODO - Phase 1 multi-organisation

## Objectif de cette iteration

Ajouter les fondations multi-organisation avec organisation perso par defaut a la premiere connexion, sans casser le flux projets existant.

## Plan d'implementation (a valider avant code)

- [ ] **Data model**: ajouter `Organization` et `OrganizationUser`; relier `Project` a `organization_id`.
- [ ] **Migration**: creer migration Alembic pour nouvelles tables + FK `projects.organization_id` (+ backfill des projets existants vers org perso).
- [ ] **Creation auto org perso**: au register/login, assurer qu'un utilisateur a au moins une organisation perso (`Espace perso`) et role `owner`.
- [ ] **Organisation active**: stocker `active_organization_id` dans la session web (cookie de session existant).
- [ ] **API organisations (MVP)**:
  - [ ] GET `/auth/organizations` (mes organisations)
  - [ ] POST `/auth/organizations` (creer org team)
  - [ ] POST `/auth/organizations/select` (changer org active)
- [ ] **Scope projets**: filtrer list/create/read/update/delete projets sur l'organisation active.
- [ ] **UI header**: ajouter selecteur d'organisation (organisation active + switch simple).
- [ ] **Page organisations (MVP)**: liste + creation (sans gestion membres avancee).
- [ ] **Verification**:
  - [ ] user neuf => org perso creee automatiquement
  - [ ] switch organisation change bien la liste projets
  - [ ] isolation: user org A ne voit pas org B
  - [ ] logs propres, pas d'erreurs 500

## Ambiguites a trancher avant implementation

- [ ] Nom par defaut de l'organisation perso: `Espace perso` (propose) ou autre?
- [ ] Organisation active stockee en session web uniquement (MVP) ou en preference persistante user?
- [ ] Regle de creation projet: toujours dans organisation active (propose) ou choix explicite a la creation?

## Review (a completer en fin de tache)

- Decisions prises:
- Tradeoffs:
- Resultats de tests:
- Points a backporter cookiecutter:

