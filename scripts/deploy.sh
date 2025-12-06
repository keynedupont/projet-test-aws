#!/bin/bash

# =============================================================================
# Script de déploiement générique
# =============================================================================
# Ce script déploie l'application sur un serveur distant
# en utilisant les images Docker depuis GHCR
#
# Usage:
#   ./scripts/deploy.sh [options]
#
# Options:
#   --tag TAG          Tag de l'image à déployer (default: latest)
#   --env ENV_FILE     Fichier .env à utiliser (default: .env)
#   --compose FILE     Fichier docker-compose à utiliser (default: docker-compose.prod.yml)
#   --skip-pull        Ne pas pull les images (utiliser les images locales)
#   --dry-run          Afficher les commandes sans les exécuter
# =============================================================================

set -euo pipefail

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Variables par défaut
IMAGE_TAG="${IMAGE_TAG:-latest}"
ENV_FILE="${ENV_FILE:-.env}"
COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.prod.yml}"
SKIP_PULL="${SKIP_PULL:-false}"
DRY_RUN="${DRY_RUN:-false}"

# Fonction d'aide
show_help() {
    cat << EOF
Usage: $0 [OPTIONS]

Options:
    --tag TAG          Tag de l'image à déployer (default: latest)
    --env ENV_FILE     Fichier .env à utiliser (default: .env)
    --compose FILE     Fichier docker-compose à utiliser (default: docker-compose.prod.yml)
    --skip-pull        Ne pas pull les images (utiliser les images locales)
    --dry-run          Afficher les commandes sans les exécuter
    -h, --help         Afficher cette aide

Exemples:
    $0
    $0 --tag v1.0.0
    $0 --env .env.prod --tag main-abc1234
    $0 --dry-run
EOF
}

# Parser les arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --tag)
            IMAGE_TAG="$2"
            shift 2
            ;;
        --env)
            ENV_FILE="$2"
            shift 2
            ;;
        --compose)
            COMPOSE_FILE="$2"
            shift 2
            ;;
        --skip-pull)
            SKIP_PULL="true"
            shift
            ;;
        --dry-run)
            DRY_RUN="true"
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Erreur: Option inconnue: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Fonction pour exécuter une commande
run_cmd() {
    if [ "$DRY_RUN" = "true" ]; then
        echo -e "${YELLOW}[DRY-RUN]${NC} $*"
    else
        echo -e "${GREEN}[EXEC]${NC} $*"
        "$@"
    fi
}

# Vérifications préalables
echo -e "${GREEN}🔍 Vérifications préalables...${NC}"

# Vérifier que Docker est installé
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker n'est pas installé${NC}"
    exit 1
fi

# Vérifier que Docker Compose est installé
if ! command -v docker compose &> /dev/null && ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose n'est pas installé${NC}"
    exit 1
fi

# Vérifier que le fichier .env existe
if [ ! -f "$ENV_FILE" ]; then
    echo -e "${YELLOW}⚠️  Fichier $ENV_FILE non trouvé${NC}"
    echo -e "${YELLOW}   Création d'un fichier .env.example...${NC}"
    if [ "$DRY_RUN" != "true" ]; then
        cp env.sample "$ENV_FILE" 2>/dev/null || true
    fi
fi

# Vérifier que le fichier docker-compose existe
if [ ! -f "$COMPOSE_FILE" ]; then
    echo -e "${RED}❌ Fichier $COMPOSE_FILE non trouvé${NC}"
    exit 1
fi

# Vérifier les variables d'environnement nécessaires
if [ "$DRY_RUN" != "true" ]; then
    source "$ENV_FILE" 2>/dev/null || true
fi

if [ -z "${GITHUB_USERNAME:-}" ] || [ -z "${GITHUB_REPO:-}" ]; then
    echo -e "${YELLOW}⚠️  Variables GITHUB_USERNAME ou GITHUB_REPO non définies${NC}"
    echo -e "${YELLOW}   Utilisation des valeurs par défaut du docker-compose${NC}"
fi

echo -e "${GREEN}✅ Vérifications OK${NC}"

# Déploiement
echo -e "${GREEN}🚀 Démarrage du déploiement...${NC}"
echo -e "${GREEN}   Tag: $IMAGE_TAG${NC}"
echo -e "${GREEN}   Compose: $COMPOSE_FILE${NC}"

# Export des variables pour docker-compose
export IMAGE_TAG
export GITHUB_USERNAME="${GITHUB_USERNAME:-}"
export GITHUB_REPO="${GITHUB_REPO:-}"

# Pull des images (si non skip)
if [ "$SKIP_PULL" != "true" ]; then
    echo -e "${GREEN}📥 Pull des images Docker...${NC}"
    run_cmd docker compose -f "$COMPOSE_FILE" pull
else
    echo -e "${YELLOW}⏭️  Skip pull (utilisation des images locales)${NC}"
fi

# Arrêt des services existants
echo -e "${GREEN}🛑 Arrêt des services existants...${NC}"
run_cmd docker compose -f "$COMPOSE_FILE" down

# Démarrage des services
echo -e "${GREEN}▶️  Démarrage des services...${NC}"
run_cmd docker compose -f "$COMPOSE_FILE" up -d

# Attendre que les services soient prêts
echo -e "${GREEN}⏳ Attente que les services soient prêts...${NC}"
sleep 5

# Vérifier le statut
echo -e "${GREEN}📊 Statut des services:${NC}"
run_cmd docker compose -f "$COMPOSE_FILE" ps

# Afficher les logs
echo -e "${GREEN}📋 Dernières lignes des logs:${NC}"
run_cmd docker compose -f "$COMPOSE_FILE" logs --tail=20

echo -e "${GREEN}✅ Déploiement terminé !${NC}"
echo -e "${GREEN}   Pour voir les logs en temps réel:${NC}"
echo -e "${GREEN}   docker compose -f $COMPOSE_FILE logs -f${NC}"

