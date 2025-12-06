# Infrastructure AWS Simple (EC2 + Docker)

Version simplifiée de l'infrastructure pour démarrer rapidement avec une instance EC2 et Docker.

## 🎯 Objectif

Créer une infrastructure minimale et économique pour :
- Développer et tester en environnement proche de la production
- Apprendre AWS sans complexité
- Réduire les coûts au démarrage (~$10-15/mois)

## 📊 Comparaison : Simple vs Complexe

| Aspect | Version Simple | Version Complexe |
|--------|---------------|------------------|
| **Architecture** | EC2 + Docker | ECS Fargate + ALB + NAT |
| **Coût/mois** | ~$10-15 | ~$115 |
| **Scalabilité** | Manuelle | Automatique |
| **Complexité** | Faible | Élevée |
| **Dossier** | `terraform-aws-simple/` | `terraform-aws/` |
| **Cas d'usage** | Développement, test | Production |

## 📋 Prérequis

1. **Terraform installé** (version >= 1.5)
   ```bash
   terraform --version
   ```

2. **AWS CLI configuré** avec des credentials IAM
   ```bash
   aws configure
   aws sts get-caller-identity  # Vérifier la connexion
   ```

3. **Clé SSH AWS** (optionnel mais recommandé)
   - Créer dans AWS Console > EC2 > Key Pairs
   - Télécharger le fichier `.pem`
   - Noter le nom de la clé

## 🚀 Utilisation rapide

### 1. Configuration initiale

```bash
cd infra/terraform-aws-simple

# Copier le fichier d'exemple
cp terraform.tfvars.example terraform.tfvars

# Éditer terraform.tfvars
# Optionnel : ajouter ssh_key_name si vous avez créé une clé SSH
```

### 2. Initialiser Terraform

```bash
terraform init
```

### 3. Vérifier le plan

```bash
terraform plan
```

Vous devriez voir :
- 1 VPC
- 1 Subnet public
- 1 Internet Gateway
- 1 Security Group
- 1 Instance EC2 (t3.micro)

### 4. Appliquer l'infrastructure

```bash
terraform apply
```

Tapez `yes` pour confirmer.

**Durée** : ~2-3 minutes

### 5. Voir les outputs

```bash
terraform output
```

Vous verrez :
- IP publique de l'instance
- URLs des services (auth:8000, app:8001)
- Commande SSH pour se connecter

## 🔧 Ce qui est créé

### Ressources AWS

1. **VPC** : Réseau virtuel isolé
2. **Subnet public** : Pour l'instance EC2
3. **Internet Gateway** : Accès Internet
4. **Security Group** : Pare-feu (ports 22, 8000, 8001)
5. **Instance EC2** : Machine virtuelle avec Docker installé

### Installation automatique (user_data)

Au démarrage de l'instance, le script installe automatiquement :
- ✅ Docker
- ✅ Docker Compose
- ✅ Git

## 📦 Déployer votre application

### Option 1 : Via SSH (recommandé)

```bash
# 1. Se connecter à l'instance
ssh -i ~/.ssh/ma-cle.pem ec2-user@<IP_PUBLIQUE>

# 2. Vérifier Docker
sudo systemctl status docker
docker --version
docker-compose --version

# 3. Cloner votre repo ou copier vos fichiers
git clone <votre-repo> /home/ec2-user/app
cd /home/ec2-user/app

# 4. Lancer docker-compose
docker-compose up -d

# 5. Vérifier que ça tourne
docker ps
```

### Option 2 : Via SCP (copier fichiers)

```bash
# Copier votre dossier vers l'instance
scp -i ~/.ssh/ma-cle.pem -r ./mon-projet ec2-user@<IP_PUBLIQUE>:/home/ec2-user/app

# Se connecter et lancer
ssh -i ~/.ssh/ma-cle.pem ec2-user@<IP_PUBLIQUE>
cd /home/ec2-user/app
docker-compose up -d
```

## 🌐 Accéder aux services

Une fois `docker-compose up -d` lancé :

- **Auth service** : `http://<IP_PUBLIQUE>:8000`
- **App service** : `http://<IP_PUBLIQUE>:8001`
- **API docs** : `http://<IP_PUBLIQUE>:8000/docs`

## 💰 Coûts estimés

### Avec Free Tier (12 premiers mois)

- **EC2 t3.micro** : 750h/mois gratuit
- **EBS Storage** : 30GB gratuit
- **Data Transfer** : 100GB sortant gratuit
- **Total** : ~$0-5/mois (selon usage)

### Sans Free Tier

- **EC2 t3.micro** : ~$10-15/mois
- **EBS Storage** : ~$3/mois (30GB)
- **Data Transfer** : ~$0.09/GB sortant
- **Total** : ~$15-20/mois

### IP Elastic (optionnel)

- **IP Elastic non utilisée** : ~$3.65/mois
- **IP Elastic utilisée** : Gratuit

## 🔒 Sécurité

### ⚠️ Points d'attention

1. **SSH ouvert à tous** : Par défaut, `allowed_cidr_blocks = ["0.0.0.0/0"]`
   - **Solution** : Restreindre à votre IP dans `terraform.tfvars`
   - Exemple : `allowed_cidr_blocks = ["123.45.67.89/32"]`

2. **Ports HTTP ouverts** : Ports 8000 et 8001 accessibles depuis Internet
   - **Solution** : Utiliser un reverse proxy (Nginx) ou passer à la version complexe avec ALB

3. **Pas de HTTPS** : Pas de certificat SSL par défaut
   - **Solution** : Configurer Nginx avec Let's Encrypt ou passer à la version complexe

## 🗑️ Détruire l'infrastructure

```bash
terraform destroy
```

⚠️ **Attention** : Cela supprime tout (instance, VPC, etc.)

## 🔄 Migration vers la version complexe

Quand vous êtes prêt pour la production :

1. **Sauvegarder les données** (base de données, fichiers)
2. **Créer l'infrastructure complexe** (`infra/terraform-aws/`)
3. **Migrer les données** vers RDS, S3, etc.
4. **Redéployer les applications** sur ECS
5. **Détruire la version simple**

Voir `../terraform-aws/README.md` pour la version complexe.

## 🐛 Dépannage

### Erreur : "Error launching instance"

- Vérifier les quotas AWS (nombre d'instances)
- Vérifier que l'AMI est disponible dans votre région

### Erreur : "AccessDenied"

- Vérifier les permissions IAM
- Vérifier que AWS CLI est configuré : `aws sts get-caller-identity`

### Impossible de se connecter en SSH

- Vérifier que `ssh_key_name` est correct dans `terraform.tfvars`
- Vérifier que le Security Group autorise le port 22 depuis votre IP
- Vérifier que l'instance est démarrée : `aws ec2 describe-instances`

### Docker ne démarre pas

- Se connecter en SSH et vérifier : `sudo systemctl status docker`
- Vérifier les logs : `sudo journalctl -u docker`

## 📚 Ressources

- [Documentation Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Amazon Linux 2023 User Guide](https://docs.aws.amazon.com/linux/al2023/)
- [Docker Documentation](https://docs.docker.com/)

## 🎯 Prochaines étapes

1. ✅ Tester l'infrastructure simple
2. ✅ Déployer votre application
3. 🔄 Migrer vers la version complexe quand nécessaire
4. 🔄 Configurer HTTPS avec Let's Encrypt
5. 🔄 Ajouter un reverse proxy (Nginx)

