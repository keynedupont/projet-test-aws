# ============================================================================
# FICHIER : providers.tf
# DESCRIPTION : Configuration du provider AWS pour Terraform
# ============================================================================

# Bloc "terraform" : Configuration globale de Terraform
terraform {
  # Version minimale de Terraform requise (>= 1.5 signifie 1.5 ou supérieur)
  required_version = ">= 1.5"

  # Définition des providers nécessaires (plugins qui permettent à Terraform
  # de communiquer avec AWS, Azure, GCP, etc.)
  required_providers {
    # Provider AWS : permet de créer des ressources sur Amazon Web Services
    aws = {
      source  = "hashicorp/aws"  # Source du provider (registry Terraform)
      version = "~> 5.0"         # Version : 5.0 ou supérieur, mais < 6.0
    }
  }
}

# Bloc "provider" : Configuration du provider AWS
# C'est ici qu'on dit à Terraform comment se connecter à AWS
provider "aws" {
  # Région AWS où créer les ressources (ex: eu-north-1, us-east-1)
  # La variable var.aws_region est définie dans variables.tf
  region = var.aws_region

  # Tags par défaut : ces tags seront automatiquement ajoutés à TOUTES
  # les ressources créées par Terraform (utile pour l'organisation et la facturation)
  default_tags {
    tags = {
      Project     = var.project_name  # Nom du projet
      Environment = "simple"          # Environnement (simple vs production)
      ManagedBy   = "Terraform"       # Indique que c'est géré par Terraform
      Purpose     = "Démarrage simple (EC2 + Docker)"  # But de cette infrastructure
    }
  }
}

