# 🏗️ Architecture

> **Vue d'ensemble technique** du projet projet

---

## 🎯 Vue d'ensemble

### **Architecture microservices**
Le projet suit une architecture microservices avec :
- **Service Auth** : Authentification et autorisation
- **Service Web** : Interface utilisateur
- **Base de données** : SQLite (dev) / PostgreSQL (prod)
- **Cache** : Redis (optionnel)

### **Stack technique**
- **Backend** : FastAPI + SQLAlchemy + Alembic
- **Frontend** : HTML + Tailwind CSS + Jinja2
- **Base de données** : SQLite / PostgreSQL
- **Cache** : Redis
- **Containerisation** : Docker + Docker Compose
- **ML** : scikit-learn + MLflow + DVC

---

## 🔐 Service d'authentification

### **Responsabilités**
- Gestion des utilisateurs (CRUD)
- Authentification JWT
- Autorisation par rôles
- Validation des mots de passe
- Tokens de vérification email
- Reset de mot de passe

### **Endpoints principaux**
```
POST /auth/register     # Inscription
POST /auth/login        # Connexion
GET  /auth/me          # Profil utilisateur
POST /auth/refresh     # Refresh token
POST /auth/logout      # Déconnexion
```

### **Modèles de données**
```python
User:
  - id, email, hashed_password
  - is_active, is_verified
  - email_verification_token
  - password_reset_token
  - first_name, last_name
  - created_at, updated_at

Role:
  - id, name

UserRole:
  - user_id, role_id (relation many-to-many)

RefreshToken:
  - token_hash, user_id
  - expires_at, is_revoked
```

### **Sécurité**
- **Hachage** : Argon2 (moderne et sécurisé)
- **JWT** : HS256 (par défaut), RS256/ES256 (optionnel)
- **Rate limiting** : 5 tentatives/5min (avec Redis)
- **Validation** : Pydantic pour tous les inputs

---

## 🌐 Service web

### **Responsabilités**
- Interface utilisateur (HTML)
- Gestion des sessions
- Communication avec le service auth
- Pages : signup, login, dashboard, admin

### **Architecture**
```
FastAPI + Jinja2 Templates
├── Pages publiques (/, /login, /signup)
├── Pages protégées (/dashboard, /admin)
├── Middleware d'erreurs global
└── Gestion des cookies de session
```

### **Communication inter-services**
- **HTTP** : Requêtes vers le service auth
- **Timeout** : 5 secondes
- **Retry** : Non implémenté (à ajouter)
- **Circuit breaker** : Non implémenté (à ajouter)

---

## 🗄️ Base de données

### **SQLAlchemy 2.0**
```python
# Configuration
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if sqlite else {},
    future=True  # SQLAlchemy 2.0 style
)
```

### **Migrations Alembic**
- **Structure** : `alembic/versions/`
- **Initialisation** : `0001_init.py`
- **Commandes** :
  ```bash
  make db-revision message="description"
  make db-upgrade
  ```

### **Contraintes importantes**
- **User.email** : Unique, indexé
- **UserRole** : Contrainte unique (user_id, role_id)
- **RefreshToken.token_hash** : Unique, indexé

---

## 🤖 Pipeline ML

### **Structure des données**
```
data/
├── raw/          # Données brutes
├── processed/    # Données nettoyées
├── features/     # Features engineering
└── external/     # Base de données SQLite
```

### **Pipelines**
```python
# make_dataset.py
def run(input_path, output_path):
    # Chargement des données brutes
    # Nettoyage basique
    # Sauvegarde vers processed/

# make_features.py
def run():
    # Feature engineering
    # Encodage, scaling
    # Sauvegarde vers features/

# train_model.py
def run():
    # Entraînement du modèle
    # Sauvegarde vers models/

# evaluate_model.py
def run():
    # Évaluation du modèle
    # Métriques vers reports/
```

### **MLflow integration**
- **Tracking** : Expériences et métriques
- **Registry** : Modèles versionnés
- **UI** : Interface web sur port 5001

---

## 🐳 Containerisation

### **Docker Compose**
```yaml
services:
  db:        # PostgreSQL (optionnel)
  redis:     # Cache et rate limiting
  auth:      # Service d'authentification
  app:       # Service web
```

### **Dépendances**
```
db (healthy) → auth (healthy) → app
redis (healthy) → auth
```

### **Volumes**
- **db_data** : Persistance PostgreSQL
- **redis_data** : Persistance Redis
- **./data** : Données SQLite (monté dans auth)

### **Health checks**
Tous les services ont des health checks avec retry logic.

---

## 🔄 Flux de données

### **Inscription utilisateur**
```
1. POST /auth/register
2. Validation Pydantic
3. Hash du mot de passe (Argon2)
4. Création User en DB
5. Assignation rôle "user"
6. Génération token vérification email
7. Retour UserOut (sans mot de passe)
```

### **Connexion**
```
1. POST /auth/login
2. Vérification email/mot de passe
3. Génération JWT access + refresh
4. Stockage refresh token en DB
5. Retour tokens
```

### **Accès page protégée**
```
1. GET /dashboard
2. Extraction token depuis cookie
3. Vérification JWT
4. Récupération utilisateur
5. Vérification rôles
6. Affichage page
```

---

## 📊 Monitoring et observabilité

### **Logging**
- **Format** : Basique (à améliorer)
- **Niveaux** : INFO, WARNING, ERROR
- **Middleware** : Trace ID pour chaque requête

### **Health Checks**

#### **Service Auth** (`/health`)
Endpoint : `GET http://localhost:8000/health`

**Réponse** :
```json
{
  "status": "ok",
  "db": true,
  "redis": false
}
```

**Vérifications** :
- **DB** : Connexion à la base de données (SELECT 1)
- **Redis** : Connexion à Redis (optionnel, retourne `false` si non configuré)

**Code de statut** :
- `200` : Service opérationnel
- `503` : Service dégradé (DB ou Redis indisponible)

**Usage** :
```bash
# Vérifier la santé du service auth
curl http://localhost:8000/health

# Dans Docker Compose
docker compose exec auth curl http://localhost:8000/health
```

#### **Service Web** (`/health`)
Endpoint : `GET http://localhost:8001/health`

**Réponse** :
```json
{
  "status": "ok",
  "auth": true
}
```

**Vérifications** :
- **Auth** : Reachability du service auth (appel à `/auth/health`)

**Code de statut** :
- `200` : Service opérationnel
- `503` : Service dégradé (auth indisponible)

**Usage** :
```bash
# Vérifier la santé du service web
curl http://localhost:8001/health

# Dans Docker Compose
docker compose exec app curl http://localhost:8001/health
```

#### **Intégration avec Docker Compose**
Les health checks sont utilisés par Docker Compose pour :
- Détecter quand un service est prêt
- Gérer les dépendances entre services
- Redémarrer automatiquement en cas d'échec

**Configuration** (dans `docker-compose.yml`) :
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

### **Métriques**
- **Health checks** : ✅ Endpoints `/health` implémentés
- **Performance** : Non implémenté
- **Business** : Non implémenté

### **Tracing**
- **Trace ID** : UUID court (8 chars)
- **Corrélation** : Entre services (à implémenter)

---

## 🔒 Sécurité

### **Authentification**
- **JWT** : Tokens stateless
- **Refresh tokens** : Rotation automatique
- **Expiration** : Access (30min), Refresh (7j)

### **Autorisation**
- **Rôles** : User, Admin
- **RBAC** : Relation many-to-many
- **Middleware** : Vérification sur chaque requête

### **Protection**
- **Rate limiting** : Avec Redis (désactivé)
- **CORS** : Configuré pour localhost
- **HTTPS** : En production uniquement

---

## 🚀 Déploiement

### **Environnements**

#### **Développement**
- **SQLite** : Fichier local
- **Hot reload** : Activé
- **Debug** : Activé
- **CORS** : Permissif

#### **Production**
- **PostgreSQL** : Base robuste
- **HTTPS** : Obligatoire
- **Rate limiting** : Activé
- **Logs structurés** : JSON

### **CI/CD**
- **GitHub Actions** : Workflows automatisés
  - `ci.yml` : Tests Python (3.10, 3.11) sur chaque push/PR
  - `build-and-push.yml` : Build et push des images Docker vers ECR (sur main/tags)
  - `deploy.yml` : Déploiement vers ECS (Phase 3 - à configurer)
- **Tests** : Unitaires + intégration
- **Build** : Docker images (app + auth)
- **Registry** : AWS ECR (Elastic Container Registry)
- **Deploy** : ECS (Phase 3 - à configurer)
- **Rollback** : Automatique (Phase 3)

### **Infrastructure AWS (Terraform)**

Le projet inclut deux configurations Terraform pour déployer sur AWS :

#### **Version Simple** (`infra/terraform-aws-simple/`)
- **Architecture** : EC2 + Docker
- **Ressources** : VPC, Subnet public, Internet Gateway, Security Group, Instance EC2
- **Coût** : ~$10-15/mois (Free Tier éligible)
- **Installation automatique** : Docker, Docker Compose, Git (via user_data)
- **Cas d'usage** : Développement, test, apprentissage AWS
- **Avantages** : Simple, économique, rapide à déployer
- **Limitations** : Scalabilité manuelle, pas de haute disponibilité

#### **Version Complexe** (`infra/terraform-aws/`)
- **Architecture** : ECS Fargate + RDS + ElastiCache + ALB + NAT Gateway
- **Ressources** :
  - **VPC** : Réseau avec subnets publics/privés, NAT Gateway
  - **ECR** : Repositories Docker pour app et auth
  - **RDS** : PostgreSQL managé
  - **ElastiCache** : Redis pour cache
  - **S3** : Buckets pour données ML
  - **ECS** : Cluster et services pour conteneurs
  - **ALB** : Application Load Balancer
  - **IAM** : Rôles et permissions
- **Coût** : ~$115/mois
- **Cas d'usage** : Production, scalabilité automatique
- **Avantages** : Scalabilité automatique, haute disponibilité, monitoring intégré
- **Modules** : Architecture modulaire (8 modules Terraform)

**Prérequis communs** :
- Terraform >= 1.5
- AWS CLI configuré
- Credentials IAM avec permissions appropriées

---

## 🔮 Évolutions prévues

### **Court terme**
1. **Email verification** : Workflow complet
2. **Password reset** : Finalisation
3. **Rate limiting** : Activation
4. **Logs structurés** : Format JSON

### **Moyen terme**
1. **2FA** : Authentification à deux facteurs
2. **Audit logs** : Traçabilité complète
3. **API versioning** : v1, v2, etc.
4. **Circuit breaker** : Résilience

### **Long terme**
1. **Microservices** : Découpage plus fin
2. **Event sourcing** : Architecture événementielle
3. **GraphQL** : Alternative à REST
4. **Kubernetes** : Orchestration avancée

---

## 📚 Références

### **Technologies**
- [FastAPI](https://fastapi.tiangolo.com/)
- [SQLAlchemy](https://www.sqlalchemy.org/)
- [Alembic](https://alembic.sqlalchemy.org/)
- [Pydantic](https://pydantic-docs.helpmanual.io/)
- [Docker](https://docs.docker.com/)

### **Patterns**
- [Microservices](https://microservices.io/)
- [JWT](https://jwt.io/)
- [RBAC](https://en.wikipedia.org/wiki/Role-based_access_control)
- [Circuit Breaker](https://martinfowler.com/bliki/CircuitBreaker.html)

---

*Pour plus de détails, voir [Configuration](configuration.md) et [Déploiement](deployment.md).*
