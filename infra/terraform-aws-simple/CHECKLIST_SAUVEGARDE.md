# 📋 Checklist de Sauvegarde avant Suppression

> **À faire AVANT de supprimer l'ancien projet** pour tester avec le nouveau template

---

## ✅ Éléments à sauvegarder

### **1. Credentials AWS**

**Où trouver :**
- AWS Console → IAM → Users → Security credentials
- Ou fichier `~/.aws/credentials`

**À sauvegarder :**
```bash
# Copier les credentials
cat ~/.aws/credentials

# Ou exporter les variables
export AWS_ACCESS_KEY_ID="votre-access-key"
export AWS_SECRET_ACCESS_KEY="votre-secret-key"
export AWS_DEFAULT_REGION="eu-north-1"
```

**Note :** Si vous utilisez AWS CLI configuré, les credentials sont déjà sauvegardés localement.

---

### **2. Clé SSH privée**

**Où trouver :**
- Fichier `.pem` téléchargé lors de la création de la clé dans AWS
- Généralement : `~/.ssh/aws-key.pem` ou `~/Downloads/`

**À sauvegarder :**
```bash
# Copier la clé SSH
cp ~/.ssh/aws-key.pem ~/backup/aws-key.pem

# Vérifier les permissions (doit être 400)
chmod 400 ~/backup/aws-key.pem
```

**Important :** Sans cette clé, vous ne pourrez pas vous connecter en SSH à l'instance.

---

### **3. Variables d'environnement (.env)**

**Où trouver :**
- Fichier `.env` à la racine du projet

**À sauvegarder :**
```bash
# Copier le fichier .env
cp .env ~/backup/.env.backup

# Ou exporter les variables importantes
grep -E "SECRET_KEY|DATABASE_URL|REDIS_URL" .env > ~/backup/env-important.txt
```

**Variables importantes :**
- `SECRET_KEY` : Clé secrète JWT
- `DATABASE_URL` : URL de connexion base de données
- `REDIS_URL` : URL Redis
- `GITHUB_USERNAME` / `GITHUB_REPO` : Pour les images Docker

---

### **4. Configuration Terraform**

**Où trouver :**
- `infra/terraform-aws-simple/terraform.tfvars`

**À sauvegarder :**
```bash
# Copier le fichier terraform.tfvars
cp infra/terraform-aws-simple/terraform.tfvars ~/backup/terraform.tfvars.backup
```

**Contenu important :**
- `aws_region` : Région AWS utilisée
- `instance_type` : Type d'instance
- `ssh_key_name` : Nom de la clé SSH dans AWS
- `project_name` : Nom du projet

---

### **5. État Terraform (optionnel)**

**Où trouver :**
- `infra/terraform-aws-simple/terraform.tfstate`

**À sauvegarder (si vous voulez garder l'état) :**
```bash
# Copier l'état Terraform
cp infra/terraform-aws-simple/terraform.tfstate ~/backup/terraform.tfstate.backup
```

**Note :** Si vous créez un nouveau projet, vous n'avez pas besoin de l'ancien état.

---

### **6. Données de la base de données (si importante)**

**Si vous avez des données importantes :**

```bash
# Dump PostgreSQL
pg_dump $DATABASE_URL > ~/backup/database-dump.sql

# Ou pour SQLite
cp data/external/app.db ~/backup/app.db.backup
```

---

## 📝 Checklist rapide

Avant de supprimer l'ancien projet, cochez :

- [ ] Credentials AWS sauvegardés (`~/.aws/credentials` ou variables d'environnement)
- [ ] Clé SSH privée sauvegardée (`.pem`)
- [ ] Fichier `.env` sauvegardé
- [ ] `terraform.tfvars` sauvegardé (si personnalisé)
- [ ] Données base de données sauvegardées (si importantes)
- [ ] IP publique de l'instance notée (si besoin)

---

## 🚀 Après sauvegarde

Une fois tout sauvegardé, vous pouvez :

1. **Créer un nouveau projet** avec le cookiecutter mis à jour
2. **Configurer les credentials** dans le nouveau projet
3. **Déployer** avec Terraform

---

## 💡 Astuce

Créez un dossier de sauvegarde :

```bash
mkdir -p ~/backup/ancien-projet-$(date +%Y%m%d)
cd ~/backup/ancien-projet-$(date +%Y%m%d)

# Copier tout
cp ~/ancien-projet/.env .
cp ~/ancien-projet/infra/terraform-aws-simple/terraform.tfvars .
cp ~/.ssh/aws-key.pem .
```

---

*Dernière mise à jour : 2024-01-XX*

