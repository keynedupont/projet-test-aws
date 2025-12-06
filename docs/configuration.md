# ⚙️ Configuration

> **Guide complet** des variables d'environnement, configurations et subtilités techniques.

---

## 🔧 Variables d'environnement

### **Fichier `.env`**
Copiez `env.sample` vers `.env` et adaptez les valeurs :

```bash
cp env.sample .env
```

### **Variables principales**

#### **🌐 Application web**
```bash
APP_SESSION_SECRET=change-me-please-change-me-32-bytes  # Secret de session (32+ chars)
AUTH_SERVICE_URL=http://127.0.0.1:8000                  # URL du service auth
COOKIE_NAME=session                                      # Nom du cookie de session
COOKIE_SECURE=0                                          # HTTPS en production (1)
COOKIE_SAMESITE=lax                                      # Politique SameSite
```

#### **🗄️ Base de données**
```bash
# SQLite (par défaut - développement)
DATABASE_URL=sqlite:///./data/external/app.db

# PostgreSQL (production)
# DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/my_ml_project
```

#### **🔐 Authentification JWT**
```bash
# HS256 (par défaut)
SECRET_KEY=7f8a9b2c4d5e6f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c

# RS256/ES256 (optionnel)
# PRIVATE_KEY_PATH=secrets/jwt_private.pem
# PUBLIC_KEY_PATH=secrets/jwt_public.pem

ACCESS_TOKEN_EXPIRE_MINUTES=30  # Durée de vie des tokens
```

**Note OAuth2** : L'API utilise `OAuth2PasswordRequestForm` (standard FastAPI). Le champ `username` contient l'email de l'utilisateur pour respecter la compatibilité OAuth2.

#### **🔴 Redis (optionnel)**
```bash
REDIS_URL=redis://localhost:6379  # Pour rate limiting et cache
```

#### **🌍 CORS**
```bash
CORS_ORIGINS=http://localhost:8001,http://127.0.0.1:8001  # Origines autorisées
```

---

## 🐳 Configuration Docker

### **SQLite vs PostgreSQL**

#### **SQLite (développement)**
- **Avantage** : Pas de serveur à démarrer
- **Fichier** : `data/external/app.db`
- **Docker** : Volume monté `./data:/app/data`

#### **PostgreSQL (production)**
- **Service** : `db` dans docker-compose.yml
- **Port** : 5432
- **Health check** : `pg_isready`

### **Activation PostgreSQL**
1. Décommentez les lignes dans `docker-compose.yml` :
```yaml
# Ligne 55 - Alternative Postgres
DATABASE_URL: ${DATABASE_URL:-postgresql+psycopg://app:app@db:5432/my_ml_project}
```

2. Modifiez `.env` :
```bash
DATABASE_URL=postgresql+psycopg://app:app@localhost:5432/my_ml_project
```

3. Lancez la stack :
```bash
make compose-up
```

### **Health checks**
Tous les services ont des health checks :
- **Postgres** : `pg_isready`
- **Redis** : `redis-cli ping`
- **Auth** : `curl http://localhost:8000/health`
- **App** : `curl http://localhost:8001/health`

---

## 🔐 Sécurité

### **JWT - Algorithmes supportés**

#### **HS256 (par défaut)**
```bash
SECRET_KEY=your-secret-key-32-chars-minimum
```

#### **RS256 (RSA)**
```bash
# Générer les clés
mkdir -p secrets && chmod 700 secrets
openssl genrsa -out secrets/jwt_private.pem 2048
openssl rsa -in secrets/jwt_private.pem -pubout -out secrets/jwt_public.pem
chmod 600 secrets/jwt_*.pem

# Configuration
PRIVATE_KEY_PATH=secrets/jwt_private.pem
PUBLIC_KEY_PATH=secrets/jwt_public.pem
```

#### **ES256 (Elliptic Curve)**
```bash
# Générer les clés
openssl ecparam -genkey -name prime256v1 -noout -out secrets/jwt_private.pem
openssl ec -in secrets/jwt_private.pem -pubout -out secrets/jwt_public.pem
```

### **Cookies sécurisés**
En production, modifiez :
```bash
COOKIE_SECURE=1        # HTTPS uniquement
COOKIE_SAMESITE=strict # Protection CSRF
```

### **Rate limiting**
Activation avec Redis :
```bash
# 1. Démarrer Redis
make compose-up  # ou docker run redis

# 2. Décommenter dans auth/routers/auth.py
# Lignes 20-22 : Rate limiting
```

---

## 🤖 Configuration ML

### **MLflow**
```bash
MLFLOW_PORT=5001  # Port de l'interface MLflow
```

Lancement :
```bash
make mlflow-ui
```

### **DVC (optionnel)**
```bash
DAGSHUB_USER=your-username
DAGSHUB_REPO=your-repo-name
DAGSHUB_TOKEN=your-token
```

Configuration :
```bash
make dvc-init
make dvc-remote-dagshub
```

---

## 🎨 Frontend

### **Tailwind CSS**
Configuration dans `tailwind.config.js` :
- **Palette** : Personnalisée "eneky"
- **Mode sombre** : Supporté
- **Police** : Marianne (système français)

### **Compilation**
```bash
# Installation Node.js requise
npm install
npm run build-css
```

---

## 🧪 Tests

### **Configuration pytest**
```bash
# Tests unitaires
make test

# Tests avec coverage (à configurer)
pytest --cov=src tests/
```

### **Variables de test**
```bash
# Base de données de test
DATABASE_URL=sqlite:///:memory:
```

**⚠️ Important : Backend email dans les tests**
- Les tests forcent automatiquement `EMAIL_BACKEND=console` dans `tests/conftest.py`
- Aucun email réel ne sera envoyé pendant les tests, même si `EMAIL_BACKEND=smtp` est défini dans `.env`
- Les emails apparaissent dans les logs de test (utile pour le debug)

## 🔄 CI/CD (GitHub Actions)

### **Workflows disponibles**

Le projet inclut trois workflows GitHub Actions :

#### **1. `ci.yml` - Continuous Integration**
- **Déclencheurs** : Push sur `main` et Pull Requests
- **Actions** : Tests Python (3.10, 3.11)
- **Durée** : ~2-5 minutes
- **Accès AWS** : Non requis

#### **2. `build-and-push.yml` - Build et Push ECR**
- **Déclencheurs** : Push sur `main` ou tags `v*` (ex: `v1.0.0`)
- **Actions** :
  - Tests Python (validation)
  - Build des images Docker (app + auth)
  - Push vers AWS ECR (Elastic Container Registry)
- **Durée** : ~5-10 minutes
- **Accès AWS** : Requis (via OIDC avec rôle IAM)
- **Secrets GitHub** : `AWS_ROLE_ARN` (ARN du rôle IAM)

#### **3. `deploy.yml` - Déploiement ECS (Phase 3)**
- **Déclencheurs** : Tags `v*` ou manuel (`workflow_dispatch`)
- **Actions** :
  - Tests Python
  - Build + Push ECR
  - Déploiement vers AWS ECS
- **Durée** : ~10-15 minutes
- **Accès AWS** : Requis
- **Status** : ⚠️ À configurer lors de la Phase 3 Production

### **Configuration GitHub Actions**

#### **Secrets nécessaires (GitHub → Settings → Secrets)**

1. **`AWS_ROLE_ARN`** (pour `build-and-push.yml` et `deploy.yml`)
   - ARN du rôle IAM AWS configuré pour OIDC
   - Exemple : `arn:aws:iam::123456789:role/github-actions-role`
   - À créer lors de la Phase 3 Production

#### **Variables d'environnement (dans les workflows)**

Les workflows utilisent des variables configurables :
- `AWS_REGION` : Région AWS (défaut : `us-east-1`)
- `ECR_REPOSITORY_APP` : Nom du repo ECR pour l'app
- `ECR_REPOSITORY_AUTH` : Nom du repo ECR pour l'auth

### **Workflow typique**

```bash
# 1. Développeur push du code
git push origin main

# 2. GitHub Actions se déclenche automatiquement
ci.yml → Tests ✅
build-and-push.yml → Tests ✅ → Build + Push ECR ✅

# 3. Images disponibles dans ECR
# Prêtes pour déploiement (Phase 3)
```

### **Versioning et Git/DVC**

- **Git** : Versionne le code source, configs, Dockerfiles
- **DVC** : Versionne les données ML (via `.dvc` files dans Git)
- **S3** : Stockage réel des données ML (remote DVC)
- **`.gitignore`** : Ignore les fichiers lourds (data/, models/)
- **`.dvcignore`** : Ignore les fichiers temporaires pour DVC (cache, logs, etc.)
- **`.gitkeep`** : Préserve la structure de dossiers vides dans Git

## 📧 Email & Vérification

### **Mode développement (débranchement email)**

Pour éviter de gérer l'envoi d'email à chaque test, plusieurs options sont disponibles :

#### **Option 1 : Auto-verification (recommandé pour dev)**
```bash
# Désactive complètement la vérification email
SKIP_EMAIL_VERIFICATION=true
```
**Comportement** : À l'inscription, `is_verified=True` automatiquement. Aucun email envoyé.

#### **Option 2 : Backend email console/file**
```bash
# Backend email console (log dans la console)
EMAIL_BACKEND=console

# Ou backend file (écrit dans /tmp/emails.json)
EMAIL_BACKEND=file
```
**Avantages** : Vous voyez le contenu de l'email et pouvez copier le token. Tests réalistes sans serveur email.

**Note pour les tests** : Les tests forcent automatiquement `EMAIL_BACKEND=console` (voir section Tests ci-dessus), donc aucun email réel ne sera envoyé pendant l'exécution des tests.

#### **Option 3 : Production (SMTP réel)**
```bash
# Configuration SMTP
EMAIL_BACKEND=smtp
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_TLS=true
```

### **Variables email**
```bash
# TTL des tokens
EMAIL_VERIFICATION_TTL=86400  # 24h en secondes
RESET_TOKEN_TTL=3600           # 1h en secondes

# URL de base pour les liens email
BASE_URL=http://localhost:8001  # Dev
# BASE_URL=https://yourdomain.com  # Production
```

---

## 🚀 Production

### **Variables critiques**
```bash
# Sécurité
SECRET_KEY=your-production-secret-key-64-chars
COOKIE_SECURE=1
COOKIE_SAMESITE=strict

# Base de données
DATABASE_URL=postgresql+psycopg://user:pass@host:5432/db

# CORS
CORS_ORIGINS=https://yourdomain.com

# Environnement
APP_ENV=production
```

### **Health checks**
Vérifiez la santé des services :
```bash
# Auth
curl http://localhost:8000/health

# App
curl http://localhost:8001/health

# Postgres
docker compose exec db pg_isready

# Redis
docker compose exec redis redis-cli ping
```

---

## ⚠️ Points d'attention

### **Développement**
1. **SECRET_KEY** : Changez la valeur par défaut
2. **SQLite** : Fichier dans `data/external/app.db`
3. **Hot reload** : Activé en dev (`--reload`)

### **Production**
1. **HTTPS** : `COOKIE_SECURE=1`
2. **PostgreSQL** : Base de données robuste
3. **Rate limiting** : Activez avec Redis
4. **Logs** : Configurez le logging structuré

### **Docker**
1. **Volumes** : `db_data` et `redis_data` persistants
2. **Health checks** : Tous les services vérifiés
3. **Dépendances** : Ordre de démarrage respecté

---

## 🔄 Migration des configurations

### **SQLite → PostgreSQL**
1. Sauvegardez les données SQLite
2. Modifiez `DATABASE_URL` dans `.env`
3. Décommentez PostgreSQL dans `docker-compose.yml`
4. Lancez `make compose-up`
5. Appliquez les migrations : `make db-upgrade`

### **HS256 → RS256**
1. Générez les clés RSA
2. Modifiez `PRIVATE_KEY_PATH` et `PUBLIC_KEY_PATH`
3. Redémarrez les services
4. Les tokens existants deviendront invalides

---

*Pour plus de détails, voir [Architecture](architecture.md) et [Déploiement](deployment.md).*
