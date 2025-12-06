# 🚀 Guide de Déploiement

> **Documentation complète** du workflow de déploiement : Docker, CI/CD, Registry, et Cloud Providers.

---

## 📚 Table des matières

1. [Concepts fondamentaux](#concepts-fondamentaux)
2. [Workflow CI/CD complet](#workflow-cicd-complet)
3. [Docker Compose : build vs image](#docker-compose--build-vs-image)
4. [Build Docker : Multi-Stage](#-build-docker--multi-stage)
5. [Cloud Providers : AWS vs Scaleway](#cloud-providers--aws-vs-scaleway)
6. [Déploiement étape par étape](#déploiement-étape-par-étape)

---

## 🎯 Concepts fondamentaux

### **1. Registry Docker (GHCR, ECR, etc.)**

#### **Qu'est-ce qu'un Registry ?**

Un **Registry** est un stockage centralisé pour les images Docker. C'est comme une bibliothèque pour vos images.

**Exemples de registries :**
- **GHCR** (GitHub Container Registry) : Gratuit, intégré à GitHub
- **ECR** (AWS Elastic Container Registry) : Service AWS managé
- **Docker Hub** : Public/gratuit (limité)
- **Scaleway Container Registry** : Service Scaleway

#### **Workflow avec Registry**

```
┌─────────────────────────────────────────────────────────────┐
│  DÉVELOPPEMENT LOCAL                                        │
│  - Code modifié                                             │
│  - Commit + Push vers GitHub                                │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  GITHUB ACTIONS (CI/CD)                                    │
│  1. Tests automatiques                                      │
│  2. Build images Docker (app + auth)                       │
│  3. Push vers Registry (GHCR)                              │
│     → ghcr.io/votre-username/votre-repo/app:latest         │
│     → ghcr.io/votre-username/votre-repo/auth:latest        │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  SERVEUR DISTANT (Scaleway/AWS)                             │
│  1. docker pull ghcr.io/.../app:latest                      │
│  2. docker pull ghcr.io/.../auth:latest                     │
│  3. docker compose up -d                                    │
│                                                              │
│  ✅ Pas de code source                                      │
│  ✅ Pas de build local                                      │
│  ✅ Juste pull + run                                         │
└─────────────────────────────────────────────────────────────┘
```

**Avantages :**
- ✅ Pas de copier-coller manuel
- ✅ Images toujours à jour (tags Git)
- ✅ Build centralisé (GitHub Actions)
- ✅ Traçabilité (qui a buildé quoi, quand)
- ✅ Sécurité (images signées, scan de vulnérabilités)

---

### **2. ECR vs EC2 (AWS) - Clarification**

#### **ECR (Elastic Container Registry)**
- **Quoi** : Registry Docker (stockage d'images)
- **Où** : Service AWS managé
- **Rôle** : Stocker les images Docker (comme GHCR)
- **Coût** : ~0.10$ par GB/mois
- **Analogie** : Bibliothèque (stocke les livres/images)

#### **EC2 (Elastic Compute Cloud)**
- **Quoi** : Serveur virtuel (VM)
- **Où** : Service AWS de compute
- **Rôle** : Machine où tournent vos conteneurs
- **Coût** : Dépend de l'instance (t3.small ~15$/mois)
- **Analogie** : Maison (où vous lisez les livres/run les images)

#### **Workflow avec AWS**

```
GitHub Actions → Build → Push ECR → Pull sur EC2 → Run
```

#### **Workflow avec GHCR (recommandé)**

```
GitHub Actions → Build → Push GHCR → Pull sur Scaleway/AWS → Run
```

**Pourquoi GHCR plutôt qu'ECR ?**
- ✅ Gratuit (vs ECR payant)
- ✅ Intégré à GitHub (pas besoin de config AWS)
- ✅ Multi-cloud (fonctionne avec AWS, Scaleway, etc.)

---

### **3. Docker Compose : `build:` vs `image:`**

#### **Concept clé : deux modes d'utilisation**

##### **Mode 1 : `build:` (développement local)**

```yaml
services:
  app:
    build:
      context: .
      dockerfile: infra/docker/Dockerfile.app
```

**Quand utiliser :**
- ✅ Développement local
- ✅ Tests
- ✅ Modifications fréquentes du code

**Action :**
- Docker **build** l'image depuis le Dockerfile
- Utilise le code source local
- Rebuild à chaque `docker compose up` (si code modifié)

**Avantages :**
- Modifications du code reflétées immédiatement
- Pas besoin de registry
- Parfait pour le développement

**Inconvénients :**
- Build peut être long
- Nécessite Node.js, Python, etc. localement

---

##### **Mode 2 : `image:` (production)**

```yaml
services:
  app:
    image: ghcr.io/votre-username/votre-repo/app:latest
```

**Quand utiliser :**
- ✅ Production
- ✅ Déploiement
- ✅ CI/CD

**Action :**
- Docker **pull** l'image depuis le registry
- Image pré-buildée (par GitHub Actions)
- Pas de build local

**Avantages :**
- ⚡ Rapide (pas de build)
- ✅ Images optimisées (multi-stage)
- ✅ Sécurité (images signées)
- ✅ Traçabilité (tags Git)

**Inconvénients :**
- Nécessite que l'image existe dans le registry
- Pas de modifications locales directes

---

##### **Solution hybride (recommandée)**

```yaml
services:
  app:
    # En dev: build local
    # En prod: utilise l'image du registry
    build:
      context: .
      dockerfile: infra/docker/Dockerfile.app
    image: ghcr.io/votre-username/votre-repo/app:latest
```

**Comportement :**
- **En dev** : `docker compose up` → build local
- **En prod** : `docker compose pull && docker compose up` → pull du registry

**Comment forcer l'utilisation de l'image :**
```bash
# Pull les images du registry
docker compose pull

# Lance avec les images pullées (ignore le build)
docker compose up -d
```

---

## 🔄 Workflow CI/CD complet

### **Étape 1 : Développement local**

```bash
# 1. Modifier le code
vim src/projet/app/web.py

# 2. Tester localement
make test

# 3. Build local (optionnel)
docker compose build

# 4. Commit + Push
git add .
git commit -m "feat: nouvelle fonctionnalité"
git push origin main
```

---

### **Étape 2 : GitHub Actions (automatique)**

Quand vous poussez sur `main`, GitHub Actions :

1. **Tests automatiques** (workflow `ci.yml`)
   ```yaml
   - name: Run tests
     run: pytest -q
   ```

2. **Build des images Docker** (workflow `build-and-push.yml`)
   - Build multi-architecture (AMD64 + ARM64)
   - Utilise Docker Buildx
   - Cache optimisé (GitHub Actions cache)

3. **Push vers GHCR**
   - Utilise `GITHUB_TOKEN` (automatique, pas besoin de configurer)
   - Push uniquement sur `main` ou tags `v*.*.*`
   - Pas de push sur Pull Requests (build seulement)

**Résultat :**
- Images disponibles sur `ghcr.io/votre-username/votre-repo/app:latest`
- Tags automatiques :
  - `latest` : Branche principale
  - `v1.0.0` : Tags semver
  - `main-abc1234` : Commit SHA
  - `pr-123` : Pull Requests (build seulement)

---

### **Configuration GitHub Actions**

#### **Secrets et Permissions**

**✅ Aucun secret à configurer !**

Le workflow utilise `GITHUB_TOKEN` qui est **automatiquement fourni** par GitHub Actions.

**Permissions nécessaires :**
```yaml
permissions:
  contents: read      # Lire le code
  packages: write     # Push vers GHCR
```

**Vérifier les permissions :**
1. Aller dans **Settings** → **Actions** → **General**
2. Section **Workflow permissions**
3. Vérifier que **"Read and write permissions"** est activé
4. Cocher **"Allow GitHub Actions to create and approve pull requests"** (optionnel)

#### **Activer GitHub Container Registry**

1. Aller sur votre repository GitHub
2. Cliquer sur **Packages** (à droite)
3. Les packages apparaissent automatiquement après le premier push

#### **Tags automatiques**

Le workflow génère automatiquement des tags selon le contexte :

| Événement | Tags générés | Exemple |
|-----------|-------------|---------|
| Push sur `main` | `latest`, `main-abc1234` | `ghcr.io/user/repo/app:latest` |
| Tag `v1.0.0` | `v1.0.0`, `v1.0`, `1`, `latest` | `ghcr.io/user/repo/app:v1.0.0` |
| Pull Request | `pr-123` (build seulement) | Pas de push |

#### **Utiliser les images**

```bash
# Pull l'image latest
docker pull ghcr.io/votre-username/votre-repo/app:latest

# Pull une version spécifique
docker pull ghcr.io/votre-username/votre-repo/app:v1.0.0

# Pull un commit spécifique
docker pull ghcr.io/votre-username/votre-repo/app:main-abc1234
```

#### **Login à GHCR (première fois)**

Sur votre serveur, pour pull les images privées :

```bash
# Login avec votre token GitHub
echo $GITHUB_TOKEN | docker login ghcr.io -u votre-username --password-stdin

# Ou avec un Personal Access Token
echo $PAT_TOKEN | docker login ghcr.io -u votre-username --password-stdin
```

**Créer un Personal Access Token :**
1. GitHub → **Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. Générer un token avec scope `read:packages`
3. Utiliser ce token pour login sur le serveur

---

### **Étape 3 : Déploiement sur serveur**

#### **Sur le serveur distant (Scaleway/AWS) :**

```bash
# 1. Se connecter au serveur
ssh user@votre-serveur.com

# 2. Aller dans le dossier du projet
cd /opt/votre-projet

# 3. Pull les dernières images
docker compose pull

# 4. Redémarrer les services
docker compose up -d

# 5. Vérifier les logs
docker compose logs -f
```

**✅ Avantages :**
- Pas de code source sur le serveur
- Pas de build local (rapide)
- Images optimisées et testées
- Rollback facile (pull d'une ancienne version)

---

## ☁️ Cloud Providers : AWS vs Scaleway

### **AWS (Amazon Web Services)**

#### **Services utilisés :**
- **EC2** : Serveur virtuel (t3.small, t3.medium, etc.)
- **ECR** : Registry Docker (optionnel, on utilise GHCR)
- **RDS** : Base de données PostgreSQL managée
- **ElastiCache** : Redis managé
- **S3** : Stockage pour données ML

#### **Coûts estimés (par mois) :**
- **EC2 t3.small** (2 vCPU, 2 GB RAM) : ~15$
- **RDS db.t3.micro** (PostgreSQL) : ~15$
- **ElastiCache cache.t3.micro** (Redis) : ~12$
- **S3** (stockage) : ~1-5$ (selon usage)
- **Total** : ~43-50$/mois

#### **Terraform :**
- ✅ Déjà configuré dans `infra/terraform-aws/` (complet) et `infra/terraform-aws-simple/` (simple)
- Modules : VPC, ECS, RDS, ElastiCache, S3, ALB

---

### **Scaleway (Recommandé pour ce projet)**

#### **Pourquoi Scaleway ?**
- 🇫🇷 Français (RGPD-friendly)
- 💰 Prix compétitifs
- 🚀 Instances ARM moins chères
- 📦 Container Registry intégré
- 🎯 Simple pour débuter

#### **Offres recommandées :**

##### **Option A : Instance dédiée (DEV1)**

**DEV1-S** (2 vCPU, 4 GB RAM)
- Prix : ~10€/mois
- Architecture : AMD64 ou ARM64
- Stockage : 80 GB SSD
- **Recommandé pour** : Tests, développement

**DEV1-M** (4 vCPU, 8 GB RAM)
- Prix : ~20€/mois
- Architecture : AMD64 ou ARM64
- Stockage : 160 GB SSD
- **Recommandé pour** : Production légère

**DEV1-L** (8 vCPU, 16 GB RAM)
- Prix : ~40€/mois
- Architecture : AMD64 ou ARM64
- Stockage : 320 GB SSD
- **Recommandé pour** : Production avec charge

##### **Option B : Kubernetes (Kapsule)**

- Plus flexible, mais plus complexe
- ~15-30€/mois minimum
- **Recommandé pour** : Production avancée

##### **Option C : Serverless Containers**

- Pay-as-you-go
- Bon pour tester
- Peut coûter plus en production

#### **Terraform pour Scaleway :**

✅ **Créé** : Infrastructure Terraform complète pour Scaleway dans `infra/terraform-scaleway/`

**Structure :**
```
infra/
├── terraform-aws/          # AWS complet (ECS, RDS, ALB, etc.)
├── terraform-aws-simple/   # AWS simple (EC2 + Docker)
├── terraform-scaleway/     # Scaleway (Instance + DB + Redis)
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── providers.tf
│   ├── terraform.tfvars.example
│   └── README.md
```

**Ressources créées :**
- ✅ Instance Scaleway (DEV1-M recommandé)
- ✅ Security Group (pare-feu)
- ✅ PostgreSQL managé (optionnel)
- ✅ Redis managé (optionnel)

**Quick start :**
```bash
cd infra/terraform-scaleway
cp terraform.tfvars.example terraform.tfvars
# Éditer terraform.tfvars
terraform init
terraform plan
terraform apply
```

**Voir la documentation complète :** `infra/terraform-scaleway/README.md`

---

### **Comparaison rapide**

| Critère | AWS | Scaleway |
|---------|-----|----------|
| **Prix** | ~50$/mois | ~20-45€/mois |
| **Complexité** | Élevée | Moyenne |
| **Terraform** | ✅ Configuré | ✅ Configuré |
| **RGPD** | ⚠️ Attention | ✅ Conforme |
| **Support** | International | Français |
| **Recommandé pour** | Production enterprise | Projets ML, startups |
| **Instance type** | t3.small, t3.medium | DEV1-S, DEV1-M, DEV1-L |
| **Database** | RDS (PostgreSQL) | PostgreSQL managé |
| **Redis** | ElastiCache | Redis managé |
| **Documentation** | `infra/terraform-aws/README.md` (complet) ou `infra/terraform-aws-simple/README.md` (simple) | `infra/terraform-scaleway/README.md` |

### **Quand choisir Scaleway ?**

✅ **Choisir Scaleway si :**
- Budget limité (~20-45€/mois vs ~50$/mois AWS)
- Conformité RGPD importante
- Support en français nécessaire
- Projet ML/startup (pas enterprise)
- Infrastructure simple (pas besoin de services AWS avancés)

✅ **Choisir AWS si :**
- Budget plus élevé acceptable
- Besoin de services AWS spécifiques (S3, Lambda, etc.)
- Infrastructure complexe (multi-région, etc.)
- Entreprise avec contraintes de conformité spécifiques

---

## 🐳 Build Docker : Multi-Stage

### **Architecture Multi-Stage**

Le projet utilise des **Dockerfiles multi-stage** pour optimiser les images finales.

#### **Dockerfile.app (Application Web)**

**Stage 1 : Builder (Node.js)**
- Base : `node:20-alpine`
- Rôle : Compiler Tailwind CSS
- Actions :
  1. Installe les dépendances Node.js (`npm install`)
  2. Compile Tailwind CSS (`npm run build-css-prod`)
  3. Génère `output.css` minifié

**Stage 2 : Runtime (Python)**
- Base : `python:3.11-slim`
- Rôle : Exécuter l'application FastAPI
- Actions :
  1. Installe les dépendances Python
  2. Copie le code source
  3. **Copie SEULEMENT le CSS compilé** depuis le stage builder
  4. Lance l'application

**Avantages :**
- ✅ Image finale **< 300 MB** (vs 500+ MB avec Node.js)
- ✅ Pas de Node.js dans l'image finale (sécurité)
- ✅ Build optimisé (cache des layers)
- ✅ CSS toujours compilé et minifié

#### **Dockerfile.auth (Service Auth)**

**Architecture simple** (pas de multi-stage nécessaire) :
- Base : `python:3.11-slim`
- Installe les dépendances Python
- Copie le code source
- Lance l'application

**Optimisations :**
- ✅ Image légère (~200 MB)
- ✅ Health checks avec `curl`
- ✅ Cache des layers optimisé

---

### **Commandes de Build**

#### **Build local (développement)**

```bash
# Build l'image app
docker build -t votre-repo-app:latest \
  -f infra/docker/Dockerfile.app .

# Build l'image auth
docker build -t votre-repo-auth:latest \
  -f infra/docker/Dockerfile.auth .

# Build avec docker-compose
docker compose build
```

#### **Build pour production**

```bash
# Build avec tag spécifique
docker build -t ghcr.io/votre-username/votre-repo/app:v1.0.0 \
  -f infra/docker/Dockerfile.app .

# Build multi-architecture (ARM + AMD)
docker buildx create --use
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --push \
  -t ghcr.io/votre-username/votre-repo/app:latest \
  -f infra/docker/Dockerfile.app .
```

#### **Vérifier la taille des images**

```bash
# Lister les images et leur taille
docker images | grep votre-repo

# Inspecter une image
docker inspect votre-repo-app:latest | grep -i size
```

**Taille attendue :**
- `app` : ~250-300 MB (avec CSS compilé)
- `auth` : ~200-250 MB

---

### **Structure des Dockerfiles**

```
infra/docker/
├── Dockerfile.app      # Multi-stage : Node.js builder + Python runtime
└── Dockerfile.auth     # Simple : Python uniquement
```

**Fichiers nécessaires pour le build :**
- `package.json` (pour npm install)
- `tailwind.config.js` (configuration Tailwind)
- `requirements.txt` (dépendances Python)
- `src/` (code source)

---

### **Optimisations appliquées**

1. **Multi-stage build** : Réduit la taille finale
2. **Alpine/Node Alpine** : Images de base légères
3. **Cache des layers** : Ordre optimisé pour le cache
4. **Production dependencies only** : `npm ci --only=production`
5. **Nettoyage apt** : `rm -rf /var/lib/apt/lists/*`
6. **No cache pip** : `pip install --no-cache-dir`

---

### **Troubleshooting Build**

#### **Problème : npm install échoue**

```bash
Error: npm ERR! code ENOENT
```

**Solution :**
- Vérifier que `package.json` existe
- Vérifier que `package-lock.json` existe (ou utiliser `npm install` au lieu de `npm ci`)

#### **Problème : Tailwind ne compile pas**

```bash
Error: Cannot find module 'tailwindcss'
```

**Solution :**
- Vérifier que `package.json` contient `tailwindcss`
- Vérifier que `npm install` s'est bien exécuté

#### **Problème : output.css non trouvé**

```bash
Error: COPY failed: file not found
```

**Solution :**
- Vérifier le chemin dans `package.json` (`build-css-prod`)
- Vérifier que le stage builder a bien généré le fichier
- Vérifier le chemin dans `COPY --from=builder`

---

## 📋 Déploiement étape par étape

### **Scénario 1 : Développement local**

```bash
# 1. Cloner le projet
git clone https://github.com/votre-username/votre-repo.git
cd votre-repo

# 2. Configuration
cp env.sample .env
# Éditer .env

# 3. Build local
docker compose build

# 4. Lancer
docker compose up -d

# 5. Vérifier
curl http://localhost:8001/health
```

**Docker Compose utilise :** `build:` (build local)

---

### **Scénario 2 : Production avec GHCR**

#### **Prérequis :**
- ✅ GitHub Actions configuré
- ✅ Images pushées sur GHCR
- ✅ Serveur distant (Scaleway/AWS) avec Docker installé

#### **Sur le serveur :**

```bash
# 1. Créer le dossier
mkdir -p /opt/votre-projet
cd /opt/votre-projet

# 2. Créer docker-compose.yml (avec image: au lieu de build:)
cat > docker-compose.yml <<EOF
version: "3.8"
services:
  app:
    image: ghcr.io/votre-username/votre-repo/app:latest
    ports:
      - "8001:8001"
    env_file:
      - .env
  auth:
    image: ghcr.io/votre-username/votre-repo/auth:latest
    ports:
      - "8000:8000"
    env_file:
      - .env
EOF

# 3. Créer .env
cp env.sample .env
# Éditer .env avec les valeurs de production

# 4. Login à GHCR (première fois)
echo $GITHUB_TOKEN | docker login ghcr.io -u votre-username --password-stdin

# 5. Pull et run
docker compose pull
docker compose up -d

# 6. Vérifier
docker compose logs -f
curl http://localhost:8001/health
```

**Docker Compose utilise :** `image:` (pull du registry)

---

### **Scénario 3 : Mise à jour en production**

```bash
# 1. Sur votre machine : push du code
git push origin main
# → GitHub Actions build + push automatiquement

# 2. Sur le serveur : pull + restart
ssh user@votre-serveur.com
cd /opt/votre-projet
docker compose pull
docker compose up -d

# 3. Vérifier
docker compose ps
docker compose logs -f app
```

**✅ Avantages :**
- Mise à jour en 2 commandes
- Rollback facile (pull d'une ancienne version)
- Pas de downtime (si configuré avec health checks)

---

## 🔧 Configuration avancée

### **Multi-architecture (ARM/AMD)**

Pour supporter Mac (ARM) et serveurs (AMD) :

```yaml
# .github/workflows/build-and-push.yml
- name: Build multi-arch
  run: |
    docker buildx create --use
    docker buildx build \
      --platform linux/amd64,linux/arm64 \
      --push \
      -t ghcr.io/votre-username/votre-repo/app:latest \
      -f infra/docker/Dockerfile.app .
```

**Résultat :**
- Une seule image, deux architectures
- Docker sélectionne automatiquement la bonne

---

### **Tags automatiques**

```yaml
# Tag avec version Git
- name: Tag images
  run: |
    docker tag app:latest ghcr.io/.../app:${{ github.sha }}
    docker tag app:latest ghcr.io/.../app:v1.0.0
```

**Tags disponibles :**
- `latest` : Dernière version
- `v1.0.0` : Version spécifique
- `abc1234` : Commit SHA
- `main` : Branche

---

## 📝 Checklist de déploiement

### **Avant le premier déploiement :**
- [ ] GitHub Actions configuré
- [ ] Images pushées sur GHCR
- [ ] Serveur distant créé (Scaleway/AWS)
- [ ] Docker installé sur le serveur
- [ ] `.env` configuré avec valeurs de production
- [ ] `docker-compose.yml` avec `image:` (pas `build:`)
- [ ] Login GHCR configuré sur le serveur

### **Déploiement :**
- [ ] `docker compose pull`
- [ ] `docker compose up -d`
- [ ] Vérifier les logs
- [ ] Tester les endpoints

### **Après déploiement :**
- [ ] Monitoring configuré
- [ ] Backups configurés
- [ ] Documentation mise à jour

---

## 🛠️ Scripts de Déploiement

### **Scripts disponibles**

Le projet inclut trois scripts de déploiement :

1. **`scripts/deploy.sh`** : Script générique (local ou SSH)
2. **`scripts/deploy-aws.sh`** : Script spécifique AWS EC2
3. **`scripts/deploy-scaleway.sh`** : Script spécifique Scaleway

---

### **Script générique : `deploy.sh`**

**Usage :**
```bash
./scripts/deploy.sh [options]
```

**Options :**
- `--tag TAG` : Tag de l'image à déployer (default: `latest`)
- `--env ENV_FILE` : Fichier `.env` à utiliser (default: `.env`)
- `--compose FILE` : Fichier docker-compose (default: `docker-compose.prod.yml`)
- `--skip-pull` : Ne pas pull les images (utiliser les images locales)
- `--dry-run` : Afficher les commandes sans les exécuter

**Exemples :**
```bash
# Déploiement standard (latest)
./scripts/deploy.sh

# Déploiement d'une version spécifique
./scripts/deploy.sh --tag v1.0.0

# Déploiement avec un fichier .env personnalisé
./scripts/deploy.sh --env .env.prod --tag main-abc1234

# Dry-run (test sans exécution)
./scripts/deploy.sh --dry-run
```

**Ce que fait le script :**
1. ✅ Vérifie que Docker et Docker Compose sont installés
2. ✅ Vérifie que les fichiers nécessaires existent
3. ✅ Pull les images depuis GHCR (sauf `--skip-pull`)
4. ✅ Arrête les services existants
5. ✅ Démarre les nouveaux services
6. ✅ Affiche le statut et les logs

---

### **Script AWS : `deploy-aws.sh`**

**Usage :**
```bash
./scripts/deploy-aws.sh [options]
```

**Options :**
- `--host HOST` : Adresse IP ou hostname du serveur EC2
- `--user USER` : Utilisateur SSH (default: `ec2-user`)
- `--key KEY` : Chemin vers la clé SSH (default: `~/.ssh/aws-key.pem`)
- `--dir DIR` : Dossier distant (default: `/opt/votre-repo`)
- `--tag TAG` : Tag de l'image (default: `latest`)

**Variables d'environnement :**
```bash
export SSH_HOST=ec2-1-2-3-4.compute-1.amazonaws.com
export SSH_USER=ec2-user
export SSH_KEY=~/.ssh/aws-key.pem
export IMAGE_TAG=latest
```

**Exemples :**
```bash
# Avec variables d'environnement
export SSH_HOST=1.2.3.4
./scripts/deploy-aws.sh

# Avec options en ligne de commande
./scripts/deploy-aws.sh --host 1.2.3.4 --user ubuntu --key ~/.ssh/my-key.pem

# Déploiement d'une version spécifique
./scripts/deploy-aws.sh --host 1.2.3.4 --tag v1.0.0
```

**Ce que fait le script :**
1. ✅ Teste la connexion SSH
2. ✅ Crée le dossier distant si nécessaire
3. ✅ Copie `docker-compose.prod.yml` et `.env.example`
4. ✅ Exécute le déploiement sur le serveur distant
5. ✅ Affiche le statut

---

### **Script Scaleway : `deploy-scaleway.sh`**

**Usage :**
```bash
./scripts/deploy-scaleway.sh [options]
```

**Options :**
- `--host HOST` : Adresse IP ou hostname du serveur Scaleway
- `--user USER` : Utilisateur SSH (default: `root`)
- `--key KEY` : Chemin vers la clé SSH (default: `~/.ssh/scaleway-key`)
- `--dir DIR` : Dossier distant (default: `/opt/votre-repo`)
- `--tag TAG` : Tag de l'image (default: `latest`)

**Variables d'environnement :**
```bash
export SSH_HOST=1.2.3.4
export SSH_USER=root
export SSH_KEY=~/.ssh/scaleway-key
export IMAGE_TAG=latest
```

**Exemples :**
```bash
# Avec variables d'environnement
export SSH_HOST=1.2.3.4
./scripts/deploy-scaleway.sh

# Avec options en ligne de commande
./scripts/deploy-scaleway.sh --host 1.2.3.4 --user ubuntu --key ~/.ssh/my-key

# Déploiement d'une version spécifique
./scripts/deploy-scaleway.sh --host 1.2.3.4 --tag v1.0.0
```

**Ce que fait le script :**
1. ✅ Teste la connexion SSH
2. ✅ Crée le dossier distant si nécessaire
3. ✅ Copie `docker-compose.prod.yml` et `.env.example`
4. ✅ Exécute le déploiement sur le serveur distant
5. ✅ Affiche le statut

---

### **Configuration des scripts**

#### **Variables d'environnement nécessaires**

Dans votre fichier `.env` (ou variables d'environnement) :

```bash
# GitHub Container Registry
GITHUB_USERNAME=votre-username
GITHUB_REPO=votre-repo

# Tag de l'image (optionnel, default: latest)
IMAGE_TAG=latest
```

#### **Permissions des scripts**

Les scripts sont exécutables par défaut. Si nécessaire :

```bash
chmod +x scripts/*.sh
```

---

### **Workflow de déploiement complet**

#### **1. Développement local**

```bash
# Modifier le code
vim src/projet/app/web.py

# Tester
make test

# Commit + Push
git add .
git commit -m "feat: nouvelle fonctionnalité"
git push origin main
```

#### **2. GitHub Actions (automatique)**

- Build les images Docker
- Push vers GHCR avec tags automatiques

#### **3. Déploiement sur serveur**

**Option A : Script local (déploiement sur serveur distant)**

```bash
# AWS
export SSH_HOST=1.2.3.4
./scripts/deploy-aws.sh

# Scaleway
export SSH_HOST=1.2.3.4
./scripts/deploy-scaleway.sh
```

**Option B : Script sur serveur (déploiement local)**

```bash
# Se connecter au serveur
ssh user@votre-serveur.com

# Cloner le repo (première fois)
git clone https://github.com/votre-username/votre-repo.git
cd votre-repo

# Configurer .env
cp env.sample .env
vim .env  # Éditer avec les valeurs de production

# Déployer
./scripts/deploy.sh --tag latest
```

---

### **Rollback (retour en arrière)**

Pour revenir à une version précédente :

```bash
# Déployer une version spécifique
./scripts/deploy.sh --tag v1.0.0

# Ou un commit spécifique
./scripts/deploy.sh --tag main-abc1234
```

---

## 🆘 Troubleshooting

### **Problème : Image non trouvée**

```bash
Error: pull access denied for ghcr.io/...
```

**Solution :**
```bash
# Login à GHCR
echo $GITHUB_TOKEN | docker login ghcr.io -u votre-username --password-stdin
```

---

### **Problème : Build échoue (Node.js manquant)**

```bash
Error: npm: command not found
```

**Solution :** Utiliser Docker multi-stage (voir `Dockerfile.app`)

---

### **Problème : Architecture incompatible**

```bash
Error: image platform (linux/arm64) does not match
```

**Solution :** Build multi-architecture (voir section ci-dessus)

---

## 📚 Ressources

- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Docker Compose documentation](https://docs.docker.com/compose/)
- [Scaleway documentation](https://www.scaleway.com/en/docs/)
- [AWS ECR documentation](https://docs.aws.amazon.com/ecr/)

---

*Dernière mise à jour : 2024-01-XX*

