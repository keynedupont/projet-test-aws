# ============================================================================
# FICHIER : providers.tf
# DESCRIPTION : Configuration des providers Terraform
# ============================================================================
# Les providers sont les plugins Terraform qui permettent de gérer
# les ressources d'un cloud provider spécifique (Scaleway ici)

terraform {
  # Version minimale de Terraform requise
  required_version = ">= 1.0"

  # Providers nécessaires
  required_providers {
    scaleway = {
      source  = "scaleway/scaleway"
      version = "~> 2.31"  # Version du provider Scaleway
    }
  }

  # Backend : Où stocker l'état Terraform (optionnel)
  # Par défaut, l'état est stocké localement dans terraform.tfstate
  # Pour la production, utilisez un backend distant (S3, etc.)
  # backend "s3" {
  #   bucket = "mon-bucket-terraform"
  #   key    = "scaleway/terraform.tfstate"
  #   region = "fr-par"
  # }
}

# Provider Scaleway
# Configuration du provider pour interagir avec l'API Scaleway
provider "scaleway" {
  # Zone par défaut (fr-par-1, fr-par-2, fr-par-3, nl-ams-1, pl-waw-1)
  zone = var.scaleway_zone

  # Région par défaut (fr-par, nl-ams, pl-waw)
  region = var.scaleway_region

  # Access Key et Secret Key (optionnel si défini via variables d'environnement)
  # SCALEWAY_ACCESS_KEY et SCALEWAY_SECRET_KEY
  # access_key = var.scaleway_access_key
  # secret_key = var.scaleway_secret_key

  # Organisation ID (optionnel si défini via variable d'environnement)
  # organization_id = var.scaleway_organization_id

  # Project ID (optionnel si défini via variable d'environnement)
  # project_id = var.scaleway_project_id
}

