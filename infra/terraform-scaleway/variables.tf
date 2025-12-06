# ============================================================================
# FICHIER : variables.tf
# DESCRIPTION : Définition des variables utilisables dans les autres fichiers Terraform
# ============================================================================

# Variable : Zone Scaleway
# Zone = Datacenter physique Scaleway (fr-par-1, fr-par-2, fr-par-3, nl-ams-1, pl-waw-1)
variable "scaleway_zone" {
  description = "Zone Scaleway pour déployer les ressources"
  type        = string
  default     = "fr-par-1"  # Paris 1 (par défaut)
}

# Variable : Région Scaleway
# Région = Zone géographique (fr-par, nl-ams, pl-waw)
variable "scaleway_region" {
  description = "Région Scaleway"
  type        = string
  default     = "fr-par"  # Paris (par défaut)
}

# Variable : Nom du projet
# Utilisé pour nommer toutes les ressources créées
variable "project_name" {
  description = "Nom du projet (utilisé pour nommer les ressources)"
  type        = string
  default     = "projet"
}

# Variable : Type d'instance
# Détermine la puissance de calcul (CPU, RAM) de la machine virtuelle
# DEV1-S = 2 vCPU, 4GB RAM (~10€/mois)
# DEV1-M = 4 vCPU, 8GB RAM (~20€/mois) - Recommandé
# DEV1-L = 8 vCPU, 16GB RAM (~40€/mois)
variable "instance_type" {
  description = "Type d'instance Scaleway (DEV1-S, DEV1-M, DEV1-L)"
  type        = string
  default     = "DEV1-M"  # Recommandé pour production
}

# Variable : Image système
# Image = Système d'exploitation pré-configuré
variable "instance_image" {
  description = "Image système pour l'instance (Ubuntu, Debian, etc.)"
  type        = string
  default     = "ubuntu_jammy"  # Ubuntu 22.04 LTS
}

# Variable : Clé SSH
# ID de la clé SSH créée dans Scaleway Console > Security > SSH Keys
# Permet de se connecter en SSH à l'instance
variable "ssh_key_id" {
  description = "ID de la clé SSH Scaleway (optionnel - laisser vide pour pas de SSH)"
  type        = string
  default     = ""
}

# Variable : IPs autorisées pour SSH
# Liste des adresses IP autorisées à se connecter en SSH
variable "allowed_cidr_blocks" {
  description = "CIDR blocks autorisés pour SSH (0.0.0.0/0 = tout le monde, à restreindre en production)"
  type        = list(string)
  default     = ["0.0.0.0/0"]  # Par défaut : tout le monde (à changer en production !)
}

# Variable : Activer la base de données PostgreSQL
# Base de données PostgreSQL managée Scaleway
variable "enable_database" {
  description = "Créer une base de données PostgreSQL managée"
  type        = bool
  default     = true  # Activée par défaut
}

# Variable : Type de base de données
# DB-DEV-S = 1 vCPU, 2GB RAM (~15€/mois)
# DB-DEV-M = 2 vCPU, 4GB RAM (~30€/mois)
variable "database_type" {
  description = "Type d'instance PostgreSQL (DB-DEV-S, DB-DEV-M)"
  type        = string
  default     = "DB-DEV-S"
}

# Variable : Activer Redis
# Redis managé Scaleway
variable "enable_redis" {
  description = "Créer un Redis managé"
  type        = bool
  default     = true  # Activé par défaut
}

# Variable : Type de Redis
# REDIS-DEV-S = 1 vCPU, 1GB RAM (~10€/mois)
# REDIS-DEV-M = 2 vCPU, 2GB RAM (~20€/mois)
variable "redis_type" {
  description = "Type d'instance Redis (REDIS-DEV-S, REDIS-DEV-M)"
  type        = string
  default     = "REDIS-DEV-S"
}

# Variable : Tags communs
# Tags = métadonnées qu'on peut ajouter aux ressources Scaleway
variable "common_tags" {
  description = "Tags communs à appliquer à toutes les ressources"
  type        = map(string)
  default     = {}
}

