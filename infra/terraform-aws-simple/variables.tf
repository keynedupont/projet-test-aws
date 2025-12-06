# ============================================================================
# FICHIER : variables.tf
# DESCRIPTION : Définition des variables utilisables dans les autres fichiers Terraform
# ============================================================================
# Les variables permettent de rendre le code réutilisable et configurable.
# Elles peuvent être définies dans terraform.tfvars ou via la ligne de commande.

# Variable : Région AWS
# Détermine où AWS va créer les ressources (chaque région est un datacenter géographique)
variable "aws_region" {
  description = "Région AWS pour déployer les ressources"
  type        = string                    # Type de la variable (texte)
  default     = "eu-north-1"              # Valeur par défaut (Stockholm, Suède)
}

# Variable : Nom du projet
# Utilisé pour nommer toutes les ressources créées (ex: "mon-projet-vpc")
variable "project_name" {
  description = "Nom du projet (utilisé pour nommer les ressources)"
  type        = string
  default     = "projet"  # Valeur par défaut depuis le cookiecutter
}

# Variable : Type d'instance EC2
# Détermine la puissance de calcul (CPU, RAM) de la machine virtuelle
# t3.micro = 2 vCPU, 1GB RAM (éligible Free Tier AWS pendant 12 mois)
variable "instance_type" {
  description = "Type d'instance EC2 (t3.micro éligible Free Tier)"
  type        = string
  default     = "t3.small"  # Recommandé : t3.small pour production. Autres : t3.micro (Free Tier), t3.medium, etc.
}

# Variable : Clé SSH
# Nom de la clé SSH créée dans AWS Console > EC2 > Key Pairs
# Permet de se connecter en SSH à l'instance EC2
# Si vide, pas d'accès SSH (mais l'instance sera créée quand même)
variable "ssh_key_name" {
  description = "Nom de la clé SSH AWS (optionnel - laisser vide pour pas de SSH)"
  type        = string
  default     = ""  # Vide par défaut (pas de SSH)
}

# Variable : IPs autorisées pour SSH
# Liste des adresses IP autorisées à se connecter en SSH
# ["0.0.0.0/0"] = tout le monde (dangereux en production)
# ["123.45.67.89/32"] = seulement cette IP spécifique
variable "allowed_cidr_blocks" {
  description = "CIDR blocks autorisés pour SSH (0.0.0.0/0 = tout le monde, à restreindre en production)"
  type        = list(string)              # Type : liste de chaînes de caractères
  default     = ["0.0.0.0/0"]            # Par défaut : tout le monde (à changer en production !)
}

# Variable : IP Elastic
# IP Elastic = IP fixe qui ne change pas même si l'instance redémarre
# Utile si vous voulez une URL fixe pour votre application
# Coûte ~$3.65/mois si non utilisée
variable "enable_elastic_ip" {
  description = "Attacher une IP Elastic (IP fixe) à l'instance"
  type        = bool                      # Type : booléen (true/false)
  default     = false                    # Par défaut : désactivé
}

# Variable : Tags communs
# Tags = métadonnées qu'on peut ajouter aux ressources AWS
# Utiles pour l'organisation, la facturation, le filtrage
variable "common_tags" {
  description = "Tags communs à appliquer à toutes les ressources"
  type        = map(string)              # Type : dictionnaire (clé-valeur)
  default     = {}                       # Par défaut : vide (pas de tags supplémentaires)
}

