# ============================================================================
# FICHIER : main.tf
# DESCRIPTION : Définition des ressources AWS à créer
# ============================================================================
# Ce fichier contient toutes les ressources AWS que Terraform va créer :
# - VPC (réseau virtuel)
# - Subnet (sous-réseau)
# - Internet Gateway (accès Internet)
# - Security Group (pare-feu)
# - Instance EC2 (machine virtuelle)

# Version Simple : EC2 + Docker
# Infrastructure minimale pour démarrer rapidement

# ============================================================================
# DATA SOURCES : Récupération d'informations depuis AWS (sans créer de ressources)
# ============================================================================

# Data source : AMI Amazon Linux 2023
# AMI = Amazon Machine Image = image de système d'exploitation pré-configurée
# On cherche automatiquement la dernière version d'Amazon Linux 2023
data "aws_ami" "amazon_linux" {
  most_recent = true                    # Prendre la version la plus récente
  owners      = ["amazon"]              # Seulement les AMI officielles Amazon

  # Filtre 1 : Nom de l'AMI doit correspondre à ce pattern
  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]   # al2023 = Amazon Linux 2023, x86_64 = architecture 64 bits
  }

  # Filtre 2 : Type de virtualisation
  filter {
    name   = "virtualization-type"
    values = ["hvm"]                    # HVM = Hardware Virtual Machine (meilleure performance)
  }
}

# ============================================================================
# RESSOURCES : Création de ressources AWS
# ============================================================================

# Ressource 1 : VPC (Virtual Private Cloud)
# VPC = Réseau virtuel isolé dans AWS (comme un réseau local privé dans le cloud)
# Toutes les autres ressources (EC2, RDS, etc.) doivent être dans un VPC
resource "aws_vpc" "main" {
  # CIDR block : Plage d'adresses IP pour le VPC
  # "10.0.0.0/16" = 65 536 adresses IP (de 10.0.0.0 à 10.0.255.255)
  cidr_block           = "10.0.0.0/16"
  
  # Activer la résolution DNS : permet d'utiliser des noms de domaine au lieu d'IP
  enable_dns_hostnames = true
  enable_dns_support   = true

  # Tags : métadonnées pour identifier la ressource
  tags = merge(
    var.common_tags,                    # Tags communs définis dans variables.tf
    {
      Name = "${var.project_name}-vpc-simple"  # Nom de la ressource (visible dans AWS Console)
    }
  )
}

# Ressource 2 : Internet Gateway
# Internet Gateway = Porte d'entrée/sortie vers Internet pour le VPC
# Sans ça, les ressources dans le VPC ne peuvent pas accéder à Internet
resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id              # Attacher cet Internet Gateway au VPC créé ci-dessus

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-igw"  # igw = Internet Gateway
    }
  )
}

# Ressource 3 : Subnet public
# Subnet = Sous-réseau dans le VPC (une portion du réseau VPC)
# "Public" = Les ressources dans ce subnet peuvent avoir une IP publique et accéder à Internet
resource "aws_subnet" "public" {
  vpc_id                  = aws_vpc.main.id              # Dans quel VPC créer ce subnet
  
  # CIDR block du subnet : "10.0.1.0/24" = 256 adresses IP (de 10.0.1.0 à 10.0.1.255)
  # Doit être inclus dans le CIDR du VPC (10.0.0.0/16)
  cidr_block              = "10.0.1.0/24"
  
  # Zone de disponibilité : Datacenter physique AWS (ex: eu-north-1a)
  # On prend la première zone disponible
  availability_zone       = data.aws_availability_zones.available.names[0]
  
  # map_public_ip_on_launch = true : Les instances lancées dans ce subnet
  # auront automatiquement une IP publique (nécessaire pour accéder depuis Internet)
  map_public_ip_on_launch = true

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-public-subnet"
    }
  )
}

# Ressource 4 : Route Table (table de routage)
# Route Table = Règles qui définissent où envoyer le trafic réseau
# Ici : tout le trafic (0.0.0.0/0) va vers l'Internet Gateway (accès Internet)
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  # Route : Règle de routage
  route {
    cidr_block = "0.0.0.0/0"                    # 0.0.0.0/0 = toutes les adresses IP (tout Internet)
    gateway_id = aws_internet_gateway.main.id   # Envoyer vers l'Internet Gateway
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-public-rt"   # rt = Route Table
    }
  )
}

# Ressource 5 : Association Route Table ↔ Subnet
# Cette association lie la route table au subnet public
# Sans ça, le subnet ne saurait pas comment router le trafic
resource "aws_route_table_association" "public" {
  subnet_id      = aws_subnet.public.id        # Le subnet public
  route_table_id = aws_route_table.public.id   # Utilise cette route table
}

# Ressource 6 : Security Group (pare-feu)
# Security Group = Règles de pare-feu qui contrôlent le trafic entrant/sortant
# Par défaut, tout est bloqué. On doit explicitement autoriser les ports nécessaires.
resource "aws_security_group" "ec2" {
  name        = "${var.project_name}-ec2-sg"   # Nom du security group
  description = "Security group pour instance EC2"
  vpc_id      = aws_vpc.main.id                # Dans quel VPC

  # Règle INGRESS (trafic entrant) : SSH (port 22)
  # "dynamic" = créer cette règle seulement si ssh_key_name n'est pas vide
  # (si pas de clé SSH, pas besoin d'ouvrir le port 22)
  dynamic "ingress" {
    for_each = var.ssh_key_name != "" ? [1] : []  # Si ssh_key_name existe, créer la règle
    content {
      description = "SSH"                         # Description de la règle
      from_port   = 22                            # Port de début
      to_port     = 22                            # Port de fin (même port = un seul port)
      protocol    = "tcp"                         # Protocole (tcp, udp, icmp, etc.)
      cidr_blocks = var.allowed_cidr_blocks       # IPs autorisées (défini dans variables.tf)
    }
  }

  # Règle INGRESS : Auth service (port 8000)
  # Autorise le trafic HTTP vers le service d'authentification
  ingress {
    description = "Auth service HTTP"
    from_port   = 8000                            # Port 8000 (service auth)
    to_port     = 8000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]                   # 0.0.0.0/0 = tout le monde (depuis Internet)
  }

  # Règle INGRESS : App service (port 8001)
  # Autorise le trafic HTTP vers l'application web
  ingress {
    description = "App service HTTP"
    from_port   = 8001                            # Port 8001 (application web)
    to_port     = 8001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]                   # Accessible depuis Internet
  }

  # Règle EGRESS (trafic sortant) : Tout autoriser
  # Permet à l'instance de faire des requêtes vers Internet
  # (télécharger des packages, appeler des APIs, etc.)
  egress {
    description = "All outbound traffic"
    from_port   = 0                               # 0 = tous les ports
    to_port     = 0
    protocol    = "-1"                            # -1 = tous les protocoles
    cidr_blocks = ["0.0.0.0/0"]                   # Vers n'importe quelle destination
  }

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-ec2-sg"        # sg = Security Group
    }
  )
}

# ============================================================================
# LOCALS : Variables locales (utilisables uniquement dans ce fichier)
# ============================================================================

# Local : Script user_data
# user_data = Script shell qui s'exécute automatiquement au premier démarrage de l'instance EC2
# C'est ici qu'on installe Docker, Docker Compose, etc.
locals {
  # <<-EOF ... EOF = Heredoc (bloc de texte multi-lignes)
  # Le "-" avant EOF supprime les espaces en début de ligne (pour l'indentation)
  user_data = <<-EOF
#!/bin/bash
# Ce script s'exécute automatiquement au démarrage de l'instance EC2

# Étape 1 : Mise à jour du système
# -y = répondre "yes" automatiquement aux questions
yum update -y

# Étape 2 : Installation de Docker
yum install -y docker                    # Installer Docker
systemctl start docker                   # Démarrer Docker maintenant
systemctl enable docker                  # Démarrer Docker automatiquement au boot
usermod -aG docker ec2-user              # Ajouter l'utilisateur ec2-user au groupe docker
                                         # (permet d'utiliser docker sans sudo)

# Étape 3 : Installation de Docker Compose
# Télécharger la dernière version depuis GitHub
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose   # Rendre le fichier exécutable
ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose  # Créer un lien symbolique

# Étape 4 : Installation de Git
# Utile pour cloner votre repository depuis GitHub
yum install -y git

# Étape 5 : Création du dossier pour l'application
mkdir -p /home/ec2-user/app              # Créer le dossier
chown ec2-user:ec2-user /home/ec2-user/app  # Changer le propriétaire

# Étape 6 : Message de confirmation
# Écrire un message dans un fichier pour confirmer que l'installation est terminée
echo "Docker et Docker Compose installés avec succès !" > /home/ec2-user/install-complete.txt
echo "Pour lancer vos conteneurs, connectez-vous en SSH et utilisez docker-compose" >> /home/ec2-user/install-complete.txt
EOF
}

# ============================================================================
# RESSOURCE PRINCIPALE : Instance EC2 (machine virtuelle)
# ============================================================================

# Ressource 7 : Instance EC2
# EC2 = Elastic Compute Cloud = machine virtuelle dans le cloud AWS
# C'est sur cette machine qu'on va lancer Docker et nos conteneurs
resource "aws_instance" "main" {
  # AMI : Image du système d'exploitation à utiliser
  # On utilise l'AMI Amazon Linux 2023 trouvée via le data source ci-dessus
  ami           = data.aws_ami.amazon_linux.id
  
  # Type d'instance : Détermine la puissance (CPU, RAM)
  # t3.micro = 2 vCPU, 1GB RAM (éligible Free Tier)
  instance_type = var.instance_type

  # Réseau : Dans quel subnet placer l'instance
  subnet_id              = aws_subnet.public.id              # Subnet public (pour avoir une IP publique)
  
  # Sécurité : Quels security groups appliquer (pare-feu)
  vpc_security_group_ids = [aws_security_group.ec2.id]      # Le security group créé ci-dessus

  # Clé SSH : Permet de se connecter en SSH à l'instance
  # Si ssh_key_name est vide, pas de clé SSH (pas d'accès SSH)
  # La clé doit être créée dans AWS Console > EC2 > Key Pairs
  key_name = var.ssh_key_name != "" ? var.ssh_key_name : null

  # Script user_data : S'exécute automatiquement au premier démarrage
  # Installe Docker, Docker Compose, Git, etc.
  user_data = local.user_data

  # Tags : Métadonnées pour identifier l'instance
  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-ec2"
    }
  )

  # Protection contre suppression accidentelle
  # false = on peut supprimer l'instance (true = protection activée)
  disable_api_termination = false
}

# Ressource 8 : Elastic IP (optionnel)
# Elastic IP = IP publique fixe qui ne change pas même si l'instance redémarre
# Utile si vous voulez une URL fixe pour votre application
# ⚠️ Coûte ~$3.65/mois si non utilisée (attachée mais pas à une instance)
resource "aws_eip" "main" {
  # count = Créer cette ressource seulement si enable_elastic_ip = true
  # Si false, count = 0, donc la ressource n'est pas créée
  count = var.enable_elastic_ip ? 1 : 0

  domain = "vpc"                          # Pour VPC (pas pour EC2-Classic, ancien système)
  instance = aws_instance.main.id        # Attacher cette IP à l'instance EC2

  tags = merge(
    var.common_tags,
    {
      Name = "${var.project_name}-eip"   # eip = Elastic IP
    }
  )

  # Dépendance : L'Internet Gateway doit exister avant de créer l'Elastic IP
  depends_on = [aws_internet_gateway.main]
}

# ============================================================================
# DATA SOURCE : Zones de disponibilité
# ============================================================================

# Data source : Zones de disponibilité disponibles
# Zone de disponibilité = Datacenter physique AWS (ex: eu-north-1a, eu-north-1b)
# On récupère la liste pour utiliser la première zone dans le subnet
data "aws_availability_zones" "available" {
  state = "available"                     # Seulement les zones disponibles (pas celles en maintenance)
}

