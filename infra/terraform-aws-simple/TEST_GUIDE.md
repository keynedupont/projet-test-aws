# 🧪 Guide de Test - Terraform Simple

Guide pas à pas pour tester l'infrastructure Terraform simple.

## ✅ Checklist avant de commencer

- [ ] Terraform installé (`terraform --version`)
- [ ] AWS CLI configuré (`aws configure`)
- [ ] Credentials IAM vérifiés (`aws sts get-caller-identity`)
- [ ] Compte AWS actif avec facturation activée
- [ ] Clé SSH AWS créée (optionnel mais recommandé)

## 🚀 Test complet

### Étape 1 : Préparation

```bash
# Aller dans le dossier Terraform simple
cd infra/terraform-aws-simple

# Copier le fichier d'exemple
cp terraform.tfvars.example terraform.tfvars

# Éditer terraform.tfvars (optionnel)
# - Vérifier aws_region
# - Ajouter ssh_key_name si vous avez une clé SSH
# - Modifier project_name si nécessaire
```

### Étape 2 : Initialisation

```bash
# Initialiser Terraform (télécharge le provider AWS)
terraform init
```

**Résultat attendu** :
```
Initializing the backend...
Initializing provider plugins...
Terraform has been successfully initialized!
```

### Étape 3 : Validation

```bash
# Valider la syntaxe des fichiers Terraform
terraform validate
```

**Résultat attendu** :
```
Success! The configuration is valid.
```

### Étape 4 : Plan (sans créer - GRATUIT)

```bash
# Voir ce qui sera créé (sans créer réellement)
terraform plan
```

**Résultat attendu** :
```
Plan: 7 to add, 0 to change, 0 to destroy.

Changes to Outputs:
  + ec2_public_ip = (known after apply)
  + ssh_command   = (known after apply)
  ...
```

**Ressources à créer** :
- 1 VPC
- 1 Internet Gateway
- 1 Subnet public
- 1 Route Table
- 1 Security Group
- 1 Instance EC2

### Étape 5 : Apply (CRÉE LES RESSOURCES - COÛT)

⚠️ **ATTENTION** : Cette étape crée des ressources AWS facturées (~$10-15/mois).

```bash
# Créer l'infrastructure
terraform apply
```

Terraform va :
1. Afficher le plan
2. Demander confirmation : `Do you want to perform these actions?`
3. Tapez `yes` pour continuer

**Durée** : ~2-3 minutes

**Résultat attendu** :
```
Apply complete! Resources: 7 added, 0 changed, 0 destroyed.

Outputs:

ec2_instance_id = "i-0123456789abcdef0"
ec2_public_ip = "12.34.56.78"
ssh_command = "ssh -i ~/.ssh/ma-cle.pem ec2-user@12.34.56.78"
auth_service_url = "http://12.34.56.78:8000"
app_service_url = "http://12.34.56.78:8001"
...
```

### Étape 6 : Vérification

```bash
# Voir tous les outputs
terraform output

# Voir un output spécifique
terraform output ec2_public_ip
terraform output ssh_command
```

### Étape 7 : Test de connexion SSH (si clé SSH configurée)

```bash
# Récupérer la commande SSH
SSH_CMD=$(terraform output -raw ssh_command)

# Se connecter (remplacer par votre vraie commande)
ssh -i ~/.ssh/ma-cle.pem ec2-user@<IP_PUBLIQUE>
```

Une fois connecté :

```bash
# Vérifier Docker
sudo systemctl status docker
docker --version
docker-compose --version

# Vérifier le message d'installation
cat /home/ec2-user/install-complete.txt
```

### Étape 8 : Test de déploiement (optionnel)

```bash
# Sur l'instance EC2 (via SSH)
cd /home/ec2-user/app

# Cloner votre repo ou copier vos fichiers
git clone <votre-repo> .

# Lancer docker-compose
docker-compose up -d

# Vérifier que les conteneurs tournent
docker ps
```

### Étape 9 : Accès aux services

Une fois `docker-compose up -d` lancé :

- **Auth service** : `http://<IP_PUBLIQUE>:8000`
- **App service** : `http://<IP_PUBLIQUE>:8001`
- **API docs** : `http://<IP_PUBLIQUE>:8000/docs`

### Étape 10 : Nettoyage (IMPORTANT)

⚠️ **Pour éviter les coûts**, détruisez l'infrastructure après les tests :

```bash
# Détruire toutes les ressources créées
terraform destroy
```

Tapez `yes` pour confirmer.

**Durée** : ~1-2 minutes

## 🐛 Dépannage

### Erreur : "Error: No valid credential sources found"

**Cause** : AWS CLI non configuré

**Solution** :
```bash
aws configure
aws sts get-caller-identity  # Vérifier
```

### Erreur : "Error: creating EC2 Instance: UnauthorizedOperation"

**Cause** : Permissions IAM insuffisantes

**Solution** : Vérifier que l'utilisateur IAM a les permissions :
- `ec2:*`
- `vpc:*`
- `iam:CreateRole` (si nécessaire)

### Erreur : "Error: creating VPC: VpcLimitExceeded"

**Cause** : Limite de VPC atteinte (5 par défaut)

**Solution** : Supprimer des VPC inutilisés ou demander une augmentation de quota

### Erreur : "Error: creating EC2 Instance: InstanceLimitExceeded"

**Cause** : Limite d'instances EC2 atteinte

**Solution** : Supprimer des instances inutilisées ou demander une augmentation de quota

### Impossible de se connecter en SSH

**Vérifications** :
1. La clé SSH est correctement configurée dans `terraform.tfvars`
2. Le Security Group autorise le port 22 depuis votre IP
3. L'instance est démarrée : `aws ec2 describe-instances --instance-ids <ID>`

## 📊 Coûts estimés

### Avec Free Tier (12 premiers mois)
- **EC2 t3.micro** : 750h/mois gratuit
- **EBS Storage** : 30GB gratuit
- **Data Transfer** : 100GB sortant gratuit
- **Total** : ~$0-5/mois

### Sans Free Tier
- **EC2 t3.micro** : ~$10-15/mois
- **EBS Storage** : ~$3/mois (30GB)
- **Total** : ~$15-20/mois

## ✅ Checklist de test réussie

- [ ] `terraform init` : Succès
- [ ] `terraform validate` : Succès
- [ ] `terraform plan` : 7 ressources à créer
- [ ] `terraform apply` : Infrastructure créée
- [ ] `terraform output` : Affiche les outputs
- [ ] Connexion SSH : Réussie (si clé configurée)
- [ ] Docker installé : Vérifié
- [ ] `terraform destroy` : Infrastructure supprimée

## 🎯 Prochaines étapes

Après avoir testé la version simple :

1. **Déployer votre application** sur l'instance EC2
2. **Tester en conditions réelles** (charges, performances)
3. **Migrer vers la version complexe** quand nécessaire (`infra/terraform-aws/`)
4. **Configurer CI/CD** avec GitHub Actions
5. **Mettre en production** avec la version complexe

---

**Note** : Ce guide teste uniquement la création de l'infrastructure. Pour déployer votre application, suivez les instructions dans `README.md`.

