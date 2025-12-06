# Infrastructure AWS avec Terraform (Version Production)

Ce répertoire contient la configuration Terraform pour déployer l'infrastructure AWS **complète et production-ready** du projet.

## 📌 Versions disponibles

**Quand utiliser quelle version ?**
- **Version Simple** (`../terraform-aws-simple/`) : Développement, test, apprentissage (~$10-15/mois)
- **Version Complexe** (`terraform-aws/`) : Production, scalabilité automatique (~$115/mois)
- **Scaleway** (`../terraform-scaleway/`) : Alternative française, RGPD-friendly (~20-45€/mois)

Voir `../terraform-aws-simple/README.md` pour la version simple.

---

## Infrastructure AWS complète (Production)

Ce répertoire contient la configuration Terraform pour déployer l'infrastructure AWS complète du projet.

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

3. **Permissions IAM** : L'utilisateur IAM doit avoir les permissions pour créer :
   - VPC, Subnets, Security Groups
   - ECR, ECS, ALB
   - RDS, ElastiCache
   - S3, IAM roles
   - CloudWatch Logs

## 🚀 Utilisation rapide

### 1. Configuration initiale

```bash
cd infra/terraform

# Copier le fichier d'exemple de variables
cp terraform.tfvars.example terraform.tfvars

# Éditer terraform.tfvars et remplir les valeurs
# ⚠️ IMPORTANT : Changer le mot de passe RDS !
```

### 2. Initialiser Terraform

```bash
terraform init
```

### 3. Vérifier le plan

```bash
terraform plan
```

### 4. Appliquer l'infrastructure

```bash
terraform apply
```

⚠️ **Attention** : Cela va créer des ressources AWS facturées. Vérifiez les coûts estimés avant d'appliquer.

### 5. Détruire l'infrastructure

```bash
terraform destroy
```

## 📁 Structure

```
infra/terraform-aws/
├── main.tf                    # Fichier principal (appelle les modules)
├── variables.tf               # Variables d'entrée
├── outputs.tf                 # Sorties (endpoints, URLs, etc.)
├── providers.tf              # Configuration du provider AWS
├── terraform.tfvars.example  # Exemple de configuration
├── .gitignore                 # Fichiers à ignorer (state, etc.)
└── modules/                   # Modules Terraform
    ├── vpc/                   # VPC, subnets, NAT Gateway
    ├── ecr/                   # Repositories Docker
    ├── rds/                   # Base de données PostgreSQL
    ├── elasticache/          # Redis cache
    ├── s3/                    # Buckets S3
    ├── iam/                   # Rôles et permissions
    ├── ecs/                   # Cluster et services ECS
    └── alb/                   # Application Load Balancer
```

## 🔧 Variables importantes

### Variables requises

- `rds_password` : Mot de passe pour RDS (⚠️ **À changer absolument !**)

### Variables avec valeurs par défaut

- `aws_region` : `eu-north-1`
- `environment` : `dev`
- `vpc_cidr` : `10.0.0.0/16`
- `rds_instance_class` : `db.t3.micro`
- `ecs_desired_count` : `1`

Voir `variables.tf` pour la liste complète.

## 📤 Outputs

Après `terraform apply`, les outputs suivants sont disponibles :

```bash
terraform output
```

Principaux outputs :
- `alb_dns_name` : URL de l'Application Load Balancer
- `rds_endpoint` : Endpoint de la base de données
- `redis_endpoint` : Endpoint Redis
- `ecr_repository_app_url` : URL du repository ECR pour l'app
- `s3_ml_data_bucket_name` : Nom du bucket S3

## 🔒 Sécurité

### Secrets et mots de passe

- ⚠️ **Ne jamais commiter** `terraform.tfvars` (déjà dans `.gitignore`)
- Utiliser AWS Secrets Manager pour les mots de passe en production
- Activer MFA pour les comptes AWS en production

### Backend S3 (optionnel)

Pour stocker le state Terraform dans S3 (recommandé pour équipe) :

1. Créer un bucket S3 et une table DynamoDB pour les locks
2. Décommenter le bloc `backend "s3"` dans `providers.tf`
3. Configurer les valeurs

## 💰 Coûts estimés (dev)

- **RDS db.t3.micro** : ~$15/mois
- **ElastiCache cache.t3.micro** : ~$15/mois
- **ECS Fargate** (1 tâche) : ~$30/mois
- **ALB** : ~$20/mois
- **NAT Gateway** : ~$35/mois
- **S3** : ~$1/mois (selon usage)
- **Total estimé** : ~$115/mois pour l'environnement dev

⚠️ Les coûts varient selon l'utilisation et la région.

## 🐛 Dépannage

### Erreur : "Error creating RDS instance"

- Vérifier que les subnets sont dans au moins 2 AZ différentes
- Vérifier les quotas AWS (nombre d'instances RDS)

### Erreur : "InvalidParameterValue"

- Vérifier les valeurs dans `terraform.tfvars`
- Vérifier la région AWS (certaines instances ne sont pas disponibles partout)

### Erreur : "AccessDenied"

- Vérifier les permissions IAM
- Vérifier que AWS CLI est bien configuré : `aws sts get-caller-identity`

## 📚 Ressources

- [Documentation Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Well-Architected Framework](https://aws.amazon.com/architecture/well-architected/)
- [Terraform Best Practices](https://www.terraform.io/docs/language/best-practices/index.html)

## 🔄 Prochaines étapes

1. Configurer le backend S3 pour le state Terraform
2. Ajouter AWS Secrets Manager pour les mots de passe
3. Configurer HTTPS avec ACM (certificat SSL)
4. Ajouter CloudWatch alarms et monitoring
5. Configurer les backups automatiques RDS

