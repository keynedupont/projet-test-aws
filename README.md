# projet

Projet ML scaffold (data → features → train → evaluate → serve)

---

## 👤 Auteur
Keyne Dupont <keynedupont@gmail.com>

## 📜 Licence
MIT

---

## ⚡ Démarrage ultra-rapide (2 minutes)

```bash
# 1. Générer le projet
cookiecutter /chemin/vers/template

# 2. Aller dans le projet
cd [nom-du-projet]

# 3. Installation rapide
make venv && source .venv/bin/activate
make install-minimal

# 4. Configuration
cp env.sample .env

# 5. Base de données (SQLite - pas de serveur à démarrer)
mkdir -p data/external
make db-upgrade

# 6. Lancer les services
make dev-auth    # Terminal 1
make dev-app     # Terminal 2

# 7. Ouvrir http://localhost:8001
```

## 🚀 Démarrage complet

```bash
# 1. Créer l'environnement virtuel
make venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 2. Installer les dépendances (choisir une option)
make install-minimal    # Installation rapide (recommandé)
# OU
make install           # Installation complète (avec MLflow, DVC, etc.)

# 4. Configurer l'environnement
cp env.sample .env
# Éditer .env avec tes valeurs (SQLite par défaut)

# 5. Initialiser la base de données (SQLite - pas de serveur)
mkdir -p data/external
make db-upgrade

# 6. Lancer les services
make dev-auth    # API Auth (port 8000)
make dev-app     # App web (port 8001)

# 7. Tests
make test
```

---

## 📂 Structure (aperçu)
```
projet/
├─ src/projet/
│   ├─ data/              # ingestion/validation sources de données
│   │   ├─ ingest.py      # chargement brut des données
│   │   └─ validate.py    # contrôles de qualité/contrats
│   ├─ processing/        # traitements génériques (clean/transform)
│   │   ├─ clean.py       # nettoyage valeurs manquantes, outliers...
│   │   └─ transform.py   # encodages, scaling, features basiques
│   ├─ features/          # construction de features (feature store local)
│   │   └─ build.py       # pipeline de feature engineering
│   ├─ pipelines/         # orchestrations ML (ETL → train → evaluate)
│   │   ├─ make_dataset.py  # data raw → processed
│   │   ├─ make_features.py # processed → features
│   │   ├─ train_model.py   # features → modèle
│   │   └─ evaluate_model.py# évaluation du modèle
│   ├─ training/          # logique d’entraînement (hors orchestration)
│   │   └─ train.py       # fonctions d’entraînement/réglages
│   ├─ evaluation/        # logique d’évaluation/métriques
│   │   ├─ evaluate.py    # boucle d’éval
│   │   └─ metrics.py     # calcul de métriques
│   ├─ utils/             # utilitaires réutilisables (IO, logging, helpers)
│   │   ├─ io.py          # lecture/écriture de fichiers/artefacts
│   │   └─ logging.py     # configuration logging
│   ├─ auth/              # microservice Auth (FastAPI, DB, JWT, rôles)
│   │   ├─ app.py         # point d’entrée FastAPI
│   │   ├─ models.py      # modèles SQLAlchemy : User, Role, UserRole, etc.
│   │   ├─ schemas.py     # schémas Pydantic : UserCreate, UserOut, Token...
│   │   ├─ security.py    # bcrypt + JWT (HS/RS/ES)
│   │   ├─ database.py    # Session SQLAlchemy + engine + Base
│   │   └─ routers/
│   │       └─ auth.py    # /auth/register, /auth/login, /me
│   └─ app/               # microservice Web minimal (FastAPI + templates HTML)
│       ├─ web.py         # /, /login, /signup, /logout, /dashboard, /admin
│       └─ templates/     # pages HTML SSR (sans JS)
├─ data/                  # données (suivies par DVC si activé)
├─ models/                # artefacts & registres de modèles
├─ reports/               # métriques et graphiques
├─ configs/               # fichiers YAML de config
├─ tests/                 # tests unitaires / intégration
├─ alembic/   # migrations DB (Alembic)
│   └─ versions/          # scripts générés (inclut 0001_init.py)
├─ secrets/               # clés JWT / secrets (git-ignorés, garder .gitkeep)
├─ infra/                 # Docker / MLflow (si activés)
│   └─ docker/            # Dockerfiles pour app & auth
│       ├─ Dockerfile.app
│       └─ Dockerfile.auth
├─ docker-compose.yml     # stack: Postgres + Redis + auth + app (si utilisé)
├─ env.sample             # exemple de variables d'environnement (.env)
├─ orchestration/         # Airflow (si activé)
├─ requirements.txt
├─ Makefile
└─ README.md
```

---

## ⚙️ Services optionnels (raccourcis)
- **DVC** : `make dvc-init` · `make dvc-add-raw` · `make dvc-push` · `make dvc-remote-dagshub`
- **MLflow** : `make mlflow-ui` → http://localhost:5001
- **FastAPI (Auth)** : `make dev-auth` → http://localhost:8000
- **App Web minimale** : `make dev-app APP_PORT=8001` → http://localhost:8001
- **Stack Docker (Postgres + Redis + Auth + App)** : `make compose-up` / `make compose-down`
- **Airflow** : `make airflow-up` → http://localhost:8080

---

## 🔧 Services & Dépendances

### Redis (Rate Limiting)
- **Usage** : Limitation du nombre de requêtes pour l'authentification
- **Port** : 6379 (dans Docker)
- **Configuration** : `REDIS_URL=redis://localhost:6379` dans `.env`

## 🔐 Clés JWT
- **HS256** : définir `SECRET_KEY` (≥ 32 chars) dans `.env`.
- **RS256 / ES256** : placer vos clés dans `secrets/` (non versionné) :
  ```bash
  # RS256 (RSA)
  mkdir -p secrets && chmod 700 secrets
  openssl genrsa -out secrets/jwt_private.pem 2048
  openssl rsa -in secrets/jwt_private.pem -pubout -out secrets/jwt_public.pem
  chmod 600 secrets/jwt_*.pem
  ```
  ```bash
  # ES256 (Elliptic Curve)
  mkdir -p secrets && chmod 700 secrets
  openssl ecparam -genkey -name prime256v1 -noout -out secrets/jwt_private.pem
  openssl ec -in secrets/jwt_private.pem -pubout -out secrets/jwt_public.pem
  chmod 600 secrets/jwt_*.pem
  ```
- `env.sample` indique les variables attendues (`SECRET_KEY` **ou** `PRIVATE_KEY_PATH` / `PUBLIC_KEY_PATH`).

### 📄 Fichier d’environnement
Copiez `env.sample` en `.env` et adaptez:
```ini
# App minimal
APP_SESSION_SECRET=change-me-please-change-me-32-bytes
AUTH_SERVICE_URL=http://127.0.0.1:8000
COOKIE_NAME=session
COOKIE_SECURE=0
COOKIE_SAMESITE=lax

# Auth service
DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/my_ml_project
SECRET_KEY=please-change-this-to-a-strong-secret
```

---

## 🧪 Test rapide de l'Auth
1) Appliquer les migrations: `make db-upgrade`  
2) `make dev-auth` puis :
   - `POST /auth/register` → `{ "email": "a@b.com", "password": "test" }`
   - `POST /auth/login` (form-data) → `username=a@b.com`, `password=test`
   - `GET /me` avec `Authorization: Bearer <token>`

### 🧪 Test rapide de l’App Web
1) Lancer l’Auth: `make dev-auth`  
2) Lancer l’App: `make dev-app APP_PORT=8001`  
3) Naviguer: `/signup` → `/login` → `/dashboard` (et `/admin` si rôle `admin`)
