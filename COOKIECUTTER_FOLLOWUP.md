# 📤 Suivi Cookiecutter (backport vers le template)

> Ce fichier sert à **tracer les bugs et améliorations** faits dans ce projet généré, pour les **remonter dans le cookiecutter** quand ils sont généralisables.  
> Un assistant ou un humain peut s’y référer pour backporter sans parcourir tout le dépôt.

---

## Mode d’emploi

1. **Quand tu corriges un bug ou améliores quelque chose** dans ce projet, ajoute une entrée ci‑dessous (voir *Comment documenter une entrée*).
2. **Quand une entrée est généralisable**, implémenter la même chose dans le template (cookiecutter), puis marquer l’entrée comme *Backporté*.
3. **Fichiers à lister** : ceux réellement modifiés dans ce projet. **Correspondance cookiecutter** : chemins dans le template (même structure : `<project_name>/src/<package_name>/...`) pour que le backport sache où appliquer les changements.

---

## Comment documenter une entrée

Pour qu’un outil ou un assistant puisse backporter **sans tout balayer**, chaque entrée doit contenir au minimum :

| Champ | Rôle |
|-------|------|
| **Titre** | Court et explicite (ex. « Fix redirection après login »). |
| **Type** | `Bug` / `Amélioration` / `Nouvelle feature`. |
| **Généralisable ?** | `Oui` / `Non` / `À évaluer`. |
| **Fichiers modifiés (ce projet)** | Liste des chemins dans ce repo (ex. `src/projet/auth/routers/auth.py`). |
| **Correspondance cookiecutter** | Chemins dans le dépôt cookiecutter (ex. `projet/src/projet/auth/routers/auth.py` ou avec les placeholders du template). |
| **Résumé** | 2–3 phrases : quoi était cassé / ce qui a été fait. |
| **Détails** | Optionnel : extrait de code ou description précise des changements (lignes, fonctions) pour permettre un copier‑coller ou un patch dans le template. |
| **Statut** | `À backporter` / `Backporté` / `Non généralisable`. |

**Exemple d’entrée :**

```markdown
### [Bug] Redirection après login (2025-02-XX)

- **Généralisable ?** Oui
- **Fichiers modifiés (ce projet)** :
  - `src/projet/app/web.py`
- **Correspondance cookiecutter** :
  - `{{cookiecutter.project_name}}/src/{{cookiecutter.package_name}}/app/web.py`
- **Résumé** : Après login, l’utilisateur était renvoyé sur `/login` au lieu du dashboard. La redirection utilisait une variable non définie ; correction en utilisant `redirect(url_for("dashboard"))`.
- **Détails** : Dans `web.py`, fonction `login_post`, remplacer `redirect(request.url)` par `redirect(url_for("dashboard"))`.
- **Statut** : À backporter
```

---

## Entrées

*(Ajouter les entrées ci‑dessous.)*

### [Amélioration] Page d'accueil : landing simplifiée et header conditionnel (2025-02-23)

- **Généralisable ?** À évaluer
- **Fichiers modifiés (ce projet)** :
  - `src/projet/app/templates/index.html`
  - `src/projet/app/templates/components/header.html`
  - `src/projet/app/web.py`
- **Correspondance cookiecutter** :
  - `{{cookiecutter.project_name}}/src/{{cookiecutter.package_name}}/app/templates/index.html`
  - `{{cookiecutter.project_name}}/src/{{cookiecutter.package_name}}/app/templates/components/header.html`
  - `{{cookiecutter.project_name}}/src/{{cookiecutter.package_name}}/app/web.py`
- **Résumé** : Sur la page d'accueil, lorsqu'on n'est pas connecté, le header affiche uniquement les boutons Connexion / S'inscrire (pas de logo ni de liens Accueil/Dashboard/Modèles/Données) et un fond transparent pour laisser voir le fond gris de la hero. La hero occupe toute la hauteur (100vh), le contenu (logo, baseline « futurization platform », bouton) est centré et légèrement remonté ; les sections « Fonctionnalités principales » et « Prêt à commencer » sont commentées en HTML. La vue `index` transmet `is_authenticated` (présence du cookie de session) pour que le header s'adapte.
- **Détails** :
  - **web.py** : Dans la route `GET /`, calculer `is_authenticated = (get_token_from_cookie(request) is not None)` et passer `is_authenticated` dans le contexte du template `index.html`.
  - **header.html** : En tête de fichier, définir `{% set is_landing = request.url.path == '/' %}` et `{% set header_is_authenticated = (is_authenticated if is_authenticated is defined else (user is defined and user)) %}`. Entourer le bloc « Logo Umagus » par `{% if not (is_landing and not header_is_authenticated) %} ... {% endif %}`. Entourer la `<nav>` desktop (liens Accueil, Dashboard, etc.) par `{% if not (is_landing and not header_is_authenticated) %} ... {% endif %}`. Même condition pour le contenu du menu mobile (liste des liens). Mettre le `<header>` en `class="... bg-transparent"` (ou appliquer un fond gris/transparent conditionnel selon is_landing et header_is_authenticated).
  - **index.html** : Hero en `min-height: 100vh`, flex avec `justify-content: center; align-items: center`. Bloc intérieur (logo + baseline + bouton) avec `style="transform: translateY(-5vh);"`. Logo avec hauteur en inline (ex. `style="height: 5.2rem; width: auto;"`). Paragraphe baseline remplacé par « futurization platform ». Sections « Fonctionnalités principales » et « Prêt à commencer » entièrement commentées en HTML (`<!-- ... -->`).
- **Statut** : Backporté

### [Bug] Pages privées : redirection login si session absente/expirée (2026-03-18)

- **Généralisable ?** Oui
- **Fichiers modifiés (ce projet)** :
  - `src/projet/app/web.py`
  - `src/projet/app/templates/login.html`
- **Correspondance cookiecutter** :
  - `{{cookiecutter.project_name}}/src/{{cookiecutter.package_name}}/app/web.py`
  - `{{cookiecutter.project_name}}/src/{{cookiecutter.package_name}}/app/templates/login.html`
- **Résumé** : Certaines pages privées (ex. `/projects`) pouvaient rester affichées même quand la session était expirée, avec des données vides. Mise en place d’un mécanisme centralisé qui redirige immédiatement vers `/login?next=...` si le cookie est absent, si le token est invalide (status non-200 sur `/me`), ou si le service auth est indisponible. Le flux conserve l’URL de retour (`next`) pour revenir sur la page demandée après login.
- **Détails** :
  - **web.py** : ajout de `require_auth(request)` et `login_redirect(next_path)`. `require_auth` vérifie la présence du cookie puis valide le token via `GET /me`. Si invalide, supprime le cookie et redirige vers `/login?next=<path>`.
  - **login.html** : ajout d’un champ hidden `next` dans le formulaire lorsqu’il est présent.
  - **web.py (login POST)** : redirige vers `next` (form/query) après authentification (fallback `/dashboard`).
  - **Pages privées** : utilisation de `require_auth` sur `/dashboard`, `/projects`, `/projects/{id}`, et les routes admin/compte/paramètres pour éviter de rendre une page si non authentifié.
- **Note UX** : En plus de la redirection, passer systématiquement `user` aux templates des pages privées pour que le header affiche le menu “connecté” (et jamais “Connexion / S’inscrire” sur une page privée).
- **Statut** : À backporter

### [Amélioration] Header : avatar seul + email dans le dropdown (2026-03-18)

- **Généralisable ?** Oui
- **Fichiers modifiés (ce projet)** :
  - `src/projet/app/templates/components/header.html`
- **Correspondance cookiecutter** :
  - `{{cookiecutter.project_name}}/src/{{cookiecutter.package_name}}/app/templates/components/header.html`
- **Résumé** : Simplification du header : le bouton utilisateur n’affiche plus l’email en permanence (avatar/initiale uniquement), et l’email est affiché dans l’en-tête du menu déroulant. Cela réduit le bruit visuel, libère de l’espace et limite l’exposition de l’email tout en le gardant accessible.
- **Détails** :
  - Retirer `{{ user.email }}` du bouton du header.
  - Ajouter un bloc en haut du dropdown (avant les liens) affichant “Connecté en tant que” + `{{ user.email }}`.
  - Ajuster la largeur du dropdown (`w-56`) et gérer l’email long (`break-all`).
- **Statut** : À backporter
