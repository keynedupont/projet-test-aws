# 🚀 Terraform Scaleway - Infrastructure as Code

> **Infrastructure Terraform** pour déployer l'application sur Scaleway

---

## 📋 Table des matières

1. [Prérequis](#prérequis)
2. [Configuration](#configuration)
3. [Déploiement](#déploiement)
4. [Ressources créées](#ressources-créées)
5. [Coûts estimés](#coûts-estimés)
6. [Troubleshooting](#troubleshooting)

---

## ✅ Prérequis

### **1. Terraform installé**

```bash
# Vérifier l'installation
terraform --version

# Installer Terraform (si nécessaire)
# macOS
brew install terraform

# Linux
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

### **2. Compte Scaleway**

- Créer un compte sur [Scaleway](https://www.scaleway.com/)
- Activer la facturation

### **3. Credentials Scaleway**

**Option A : Variables d'environnement (recommandé)**

```bash
export SCALEWAY_ACCESS_KEY="your-access-key"
export SCALEWAY_SECRET_KEY="your-secret-key"
export SCALEWAY_ORGANIZATION_ID="your-org-id"
export SCALEWAY_PROJECT_ID="your-project-id"
```

**Option B : Scaleway CLI**

```bash
# Installer Scaleway CLI
brew install scw  # macOS
# ou
curl -o /usr/local/bin/scw -L "https://github.com/scaleway/scaleway-cli/releases/latest/download/scw-linux-x86_64"
chmod +x /usr/local/bin/scw

# Configurer
scw init
```

**Option C : Fichier de configuration**

Créer `~/.config/scw/config.yaml` :

```yaml
access_key: your-access-key
secret_key: your-secret-key
default_organization_id: your-org-id
default_project_id: your-project-id
default_zone: fr-par-1
default_region: fr-par
```

### **4. Clé SSH (optionnel mais recommandé)**

```bash
# Créer une clé SSH
ssh-keygen -t ed25519 -C "scaleway-key" -f ~/.ssh/scaleway-key

# Ajouter la clé dans Scaleway Console
# Console > Security > SSH Keys > Add SSH Key
# Copier le contenu de ~/.ssh/scaleway-key.pub
```

---

## ⚙️ Configuration

### **1. Copier le fichier de configuration**

```bash
cd infra/terraform-scaleway
cp terraform.tfvars.example terraform.tfvars
```

### **2. Éditer `terraform.tfvars`**

```bash
vim terraform.tfvars
```

**Variables importantes :**
- `scaleway_zone` : Zone Scaleway (fr-par-1, fr-par-2, etc.)
- `instance_type` : Type d'instance (DEV1-M recommandé)
- `ssh_key_id` : ID de votre clé SSH Scaleway
- `enable_database` : Activer PostgreSQL (true/false)
- `enable_redis` : Activer Redis (true/false)

### **3. Initialiser Terraform**

```bash
terraform init
```

**Résultat attendu :**
```
Initializing the backend...
Initializing provider plugins...
- Finding scaleway/scaleway versions matching "~> 2.31"...
- Installing scaleway/scaleway v2.31.0...
Terraform has been successfully initialized!
```

---

## 🚀 Déploiement

### **1. Valider la configuration**

```bash
terraform validate
```

### **2. Planifier les changements**

```bash
terraform plan
```

**Affiche :**
- Les ressources qui seront créées
- Les coûts estimés
- Les dépendances

### **3. Appliquer les changements**

```bash
terraform apply
```

**Confirmation :**
```
Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes
```

**Durée :** ~5-10 minutes

### **4. Vérifier les outputs**

```bash
terraform output
```

**Outputs importants :**
- `instance_public_ip` : IP publique de l'instance
- `ssh_command` : Commande SSH pour se connecter
- `database_endpoint` : Endpoint PostgreSQL
- `redis_endpoint` : Endpoint Redis
- `app_url` : URL de l'application

---

## 📦 Ressources créées

### **1. Instance Scaleway (DEV1-M)**

- **Type** : DEV1-M (4 vCPU, 8GB RAM)
- **Image** : Ubuntu 22.04 LTS
- **Docker** : Installé automatiquement (via user_data)
- **Docker Compose** : Installé automatiquement
- **Ports ouverts** : 22 (SSH), 8000 (Auth), 8001 (App)

### **2. Security Group (pare-feu)**

- **SSH** : Port 22 (restreint aux IPs autorisées)
- **Auth** : Port 8000 (accessible depuis Internet)
- **App** : Port 8001 (accessible depuis Internet)

### **3. Base de données PostgreSQL (optionnel)**

- **Type** : DB-DEV-S (1 vCPU, 2GB RAM)
- **Version** : PostgreSQL 15
- **Backups** : Activés
- **Mot de passe** : Généré aléatoirement (voir outputs)

### **4. Redis (optionnel)**

- **Type** : REDIS-DEV-S (1 vCPU, 1GB RAM)
- **Version** : Redis 7.0.5
- **Cluster** : 1 node (non-HA)

---

## 💰 Coûts estimés

### **Configuration minimale (sans DB/Redis)**

- **Instance DEV1-M** : ~20€/mois
- **Total** : ~20€/mois

### **Configuration complète (avec DB/Redis)**

- **Instance DEV1-M** : ~20€/mois
- **PostgreSQL DB-DEV-S** : ~15€/mois
- **Redis REDIS-DEV-S** : ~10€/mois
- **Total** : ~45€/mois

### **Configuration production (avec DB/Redis plus puissants)**

- **Instance DEV1-L** : ~40€/mois
- **PostgreSQL DB-DEV-M** : ~30€/mois
- **Redis REDIS-DEV-M** : ~20€/mois
- **Total** : ~90€/mois

**Note :** Les prix peuvent varier selon la zone et les promotions Scaleway.

---

## 🔧 Utilisation après déploiement

### **1. Se connecter en SSH**

```bash
# Récupérer l'IP publique
terraform output instance_public_ip

# Se connecter
ssh root@$(terraform output -raw instance_public_ip)
```

### **2. Déployer l'application**

```bash
# Sur le serveur
cd /opt/votre-projet

# Cloner le repo (première fois)
git clone https://github.com/votre-username/votre-repo.git .

# Configurer .env
cp env.sample .env
vim .env  # Éditer avec les valeurs de production

# Déployer
./scripts/deploy.sh
```

### **3. Configurer la base de données**

Dans votre `.env` :

```bash
# PostgreSQL Scaleway
DATABASE_URL=postgresql+psycopg://admin:$(terraform output -raw database_password)@$(terraform output -raw database_endpoint):$(terraform output -raw database_port)/votre-repo
```

### **4. Configurer Redis**

Dans votre `.env` :

```bash
# Redis Scaleway
REDIS_URL=redis://$(terraform output -raw redis_endpoint):$(terraform output -raw redis_port)
```

---

## 🗑️ Destruction de l'infrastructure

**⚠️ Attention :** Cela supprime TOUTES les ressources créées !

```bash
terraform destroy
```

**Confirmation :**
```
Do you really want to destroy all resources?
  Terraform will destroy all your managed infrastructure.
  This action cannot be undone.

  Enter a value: yes
```

---

## 🆘 Troubleshooting

### **Problème : Provider Scaleway non trouvé**

```bash
Error: Failed to query available provider packages
```

**Solution :**
```bash
terraform init -upgrade
```

### **Problème : Credentials non valides**

```bash
Error: invalid credentials
```

**Solution :**
- Vérifier les variables d'environnement : `echo $SCALEWAY_ACCESS_KEY`
- Vérifier le fichier de configuration : `~/.config/scw/config.yaml`
- Réinitialiser : `scw init`

### **Problème : Zone non disponible**

```bash
Error: zone not available
```

**Solution :**
- Changer la zone dans `terraform.tfvars` : `scaleway_zone = "fr-par-2"`

### **Problème : Instance ne démarre pas**

```bash
# Vérifier les logs
ssh root@$(terraform output -raw instance_public_ip)
journalctl -u cloud-init
```

---

## 📚 Ressources

- [Documentation Terraform Scaleway](https://registry.terraform.io/providers/scaleway/scaleway/latest/docs)
- [Documentation Scaleway](https://www.scaleway.com/en/docs/)
- [Prix Scaleway](https://www.scaleway.com/en/pricing/)

---

*Dernière mise à jour : 2024-01-XX*

