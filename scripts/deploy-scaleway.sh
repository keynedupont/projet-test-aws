#!/bin/bash

# =============================================================================
# Script de déploiement pour Scaleway
# =============================================================================
# Ce script déploie l'application sur un serveur Scaleway
#
# Usage:
#   ./scripts/deploy-scaleway.sh [options]
#
# Prérequis:
#   - Accès SSH au serveur Scaleway
#   - Docker installé sur le serveur
#   - Variables d'environnement configurées
# =============================================================================

set -euo pipefail

# Couleurs
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Variables par défaut
SSH_HOST="${SSH_HOST:-}"
SSH_USER="${SSH_USER:-root}"
SSH_KEY="${SSH_KEY:-~/.ssh/scaleway-key}"
REMOTE_DIR="${REMOTE_DIR:-/opt/projet}"
IMAGE_TAG="${IMAGE_TAG:-latest}"

# Fonction d'aide
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    --host HOST        Adresse IP ou hostname du serveur Scaleway
    --user USER        Utilisateur SSH (default: root)
    --key KEY          Chemin vers la clé SSH (default: ~/.ssh/scaleway-key)
    --dir DIR          Dossier distant (default: /opt/projet)
    --tag TAG          Tag de l'image (default: latest)
    -h, --help         Afficher cette aide

Variables d'environnement:
    SSH_HOST           Adresse du serveur
    SSH_USER           Utilisateur SSH
    SSH_KEY            Chemin vers la clé SSH
    REMOTE_DIR         Dossier distant
    IMAGE_TAG          Tag de l'image

Exemples:
    export SSH_HOST=1.2.3.4
    $0

    $0 --host 1.2.3.4 --user ubuntu --key ~/.ssh/my-key
EOF
}

# Parser les arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            SSH_HOST="$2"
            shift 2
            ;;
        --user)
            SSH_USER="$2"
            shift 2
            ;;
        --key)
            SSH_KEY="$2"
            shift 2
            ;;
        --dir)
            REMOTE_DIR="$2"
            shift 2
            ;;
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo "Erreur: Option inconnue: $1"
            show_help
            exit 1
            ;;
    esac
done

# Vérifications
if [ -z "$SSH_HOST" ]; then
    echo -e "${YELLOW}⚠️  SSH_HOST non défini${NC}"
    echo "Définissez SSH_HOST ou utilisez --host"
    exit 1
fi

# Test de connexion SSH
echo -e "${GREEN}🔍 Test de connexion SSH...${NC}"
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=5 "$SSH_USER@$SSH_HOST" "echo 'Connexion OK'" &>/dev/null; then
    echo "❌ Impossible de se connecter au serveur"
    exit 1
fi

# Créer le dossier distant si nécessaire
echo -e "${GREEN}📁 Création du dossier distant...${NC}"
ssh -i "$SSH_KEY" "$SSH_USER@$SSH_HOST" "mkdir -p $REMOTE_DIR"

# Copier les fichiers nécessaires
echo -e "${GREEN}📤 Copie des fichiers...${NC}"
scp -i "$SSH_KEY" docker-compose.prod.yml "$SSH_USER@$SSH_HOST:$REMOTE_DIR/"
scp -i "$SSH_KEY" env.sample "$SSH_USER@$SSH_HOST:$REMOTE_DIR/.env.example" 2>/dev/null || true

# Exécuter le déploiement sur le serveur
echo -e "${GREEN}🚀 Déploiement sur le serveur...${NC}"
ssh -i "$SSH_KEY" "$SSH_USER@$SSH_HOST" << EOF
    set -e
    cd $REMOTE_DIR
    
    # Vérifier que .env existe
    if [ ! -f .env ]; then
        echo "⚠️  Création du fichier .env depuis .env.example"
        cp .env.example .env 2>/dev/null || echo "⚠️  .env.example non trouvé, créez .env manuellement"
    fi
    
    # Exporter les variables
    export IMAGE_TAG=$IMAGE_TAG
    source .env 2>/dev/null || true
    
    # Pull et déploiement
    docker compose -f docker-compose.prod.yml pull
    docker compose -f docker-compose.prod.yml up -d
    
    # Statut
    docker compose -f docker-compose.prod.yml ps
EOF

echo -e "${GREEN}✅ Déploiement terminé !${NC}"

