# ============================================================================
# FICHIER : main.tf
# DESCRIPTION : Définition des ressources Scaleway à créer
# ============================================================================
# Ce fichier contient toutes les ressources Scaleway que Terraform va créer :
# - Instance (machine virtuelle)
# - Security Group (pare-feu)
# - Database PostgreSQL (optionnel)
# - Redis (optionnel)

# ============================================================================
# RESSOURCE 1 : Security Group (pare-feu)
# ============================================================================
# Security Group = Règles de pare-feu qui contrôlent le trafic entrant/sortant

resource "scaleway_instance_security_group" "main" {
  name                    = "${var.project_name}-sg"
  description             = "Security group pour ${var.project_name}"
  inbound_default_policy  = "drop"    # Par défaut, tout est bloqué
  outbound_default_policy = "accept"   # Par défaut, tout est autorisé

  # Règle INGRESS : SSH (port 22)
  # "dynamic" = créer cette règle seulement si ssh_key_id n'est pas vide
  dynamic "inbound_rule" {
    for_each = var.ssh_key_id != "" ? [1] : []
    content {
      action   = "accept"
      port     = 22
      protocol = "TCP"
      ip_range = var.allowed_cidr_blocks[0]  # Première IP autorisée
    }
  }

  # Règle INGRESS : Auth service (port 8000)
  inbound_rule {
    action   = "accept"
    port     = 8000
    protocol = "TCP"
    ip_range = "0.0.0.0/0"  # Accessible depuis Internet
  }

  # Règle INGRESS : App service (port 8001)
  inbound_rule {
    action   = "accept"
    port     = 8001
    protocol = "TCP"
    ip_range = "0.0.0.0/0"  # Accessible depuis Internet
  }

  tags = var.common_tags
}

# ============================================================================
# LOCALS : Variables locales (utilisables uniquement dans ce fichier)
# ============================================================================

# Local : Script user_data
# user_data = Script shell qui s'exécute automatiquement au premier démarrage de l'instance
locals {
  user_data = <<-EOF
#!/bin/bash
# Ce script s'exécute automatiquement au démarrage de l'instance Scaleway

# Étape 1 : Mise à jour du système
apt-get update
apt-get upgrade -y

# Étape 2 : Installation de Docker
apt-get install -y \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Ajouter la clé GPG Docker
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Ajouter le repository Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Installer Docker
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Démarrer Docker
systemctl start docker
systemctl enable docker

# Ajouter l'utilisateur au groupe docker (permet d'utiliser docker sans sudo)
usermod -aG docker $USER

# Étape 3 : Installation de Git
apt-get install -y git

# Étape 4 : Création du dossier pour l'application
mkdir -p /opt/${var.project_name}
chmod 755 /opt/${var.project_name}

# Étape 5 : Message de confirmation
echo "Docker et Docker Compose installés avec succès !" > /root/install-complete.txt
echo "Pour lancer vos conteneurs, connectez-vous en SSH et utilisez docker compose" >> /root/install-complete.txt
EOF
}

# ============================================================================
# RESSOURCE 2 : Instance (machine virtuelle)
# ============================================================================

resource "scaleway_instance_server" "main" {
  name  = "${var.project_name}-instance"
  type  = var.instance_type
  image = var.instance_image
  zone  = var.scaleway_zone

  # Security Group
  security_group_id = scaleway_instance_security_group.main.id

  # Clé SSH
  # Si ssh_key_id est vide, pas de clé SSH (pas d'accès SSH)
  dynamic "public_ip" {
    for_each = var.ssh_key_id != "" ? [1] : []
    content {
      # IP publique automatique
    }
  }

  # User data (script d'initialisation)
  user_data = {
    cloud-init = local.user_data
  }

  # Tags
  tags = merge(
    var.common_tags,
    ["${var.project_name}", "instance"]
  )
}

# ============================================================================
# RESSOURCE 3 : Base de données PostgreSQL (optionnel)
# ============================================================================

resource "scaleway_rdb_instance" "main" {
  count = var.enable_database ? 1 : 0

  name           = "${var.project_name}-db"
  node_type      = var.database_type
  engine         = "PostgreSQL-15"
  is_ha_cluster  = false  # High Availability désactivé (moins cher)
  disable_backup = false  # Backups activés
  user_name      = "admin"
  password       = random_password.db_password[0].result  # Mot de passe généré aléatoirement

  region = var.scaleway_region

  tags = merge(
    var.common_tags,
    ["${var.project_name}", "database"]
  )
}

# Génération aléatoire du mot de passe de la base de données
resource "random_password" "db_password" {
  count   = var.enable_database ? 1 : 0
  length  = 32
  special = true
}

# Base de données dans l'instance PostgreSQL
resource "scaleway_rdb_database" "main" {
  count    = var.enable_database ? 1 : 0
  instance_id = scaleway_rdb_instance.main[0].id
  name     = var.project_name
}

# ============================================================================
# RESSOURCE 4 : Redis (optionnel)
# ============================================================================

resource "scaleway_redis_cluster" "main" {
  count = var.enable_redis ? 1 : 0

  name         = "${var.project_name}-redis"
  node_type    = var.redis_type
  version      = "7.0.5"  # Version Redis
  cluster_size = 1        # 1 node (pas de cluster)
  zone         = var.scaleway_zone

  tags = merge(
    var.common_tags,
    ["${var.project_name}", "redis"]
  )
}

# ============================================================================
# PROVIDER RANDOM : Pour générer des mots de passe aléatoires
# ============================================================================

terraform {
  required_providers {
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }
}

