# =============================================================================
# STAGE 1: Builder - Compile Tailwind CSS
# =============================================================================
FROM node:20-alpine AS builder

WORKDIR /build

# Copier les fichiers nécessaires pour npm install
COPY package.json package-lock.json* ./

# Installer les dépendances Node.js (Tailwind CSS)
RUN npm ci --only=production || npm install

# Copier la configuration Tailwind
COPY tailwind.config.js ./

# Copier le CSS source et les templates (pour que Tailwind scanne les classes)
COPY src/ ./src/

# Compiler Tailwind CSS en mode production (minifié)
RUN npm run build-css-prod

# =============================================================================
# STAGE 2: Runtime - Application Python
# =============================================================================
FROM python:3.11-slim

WORKDIR /app

# Installer curl pour les health checks
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code source
COPY src ./src

# Copier SEULEMENT le CSS compilé depuis le stage builder
# (pas besoin de Node.js dans l'image finale)
COPY --from=builder /build/src/projet/app/static/css/output.css \
     ./src/projet/app/static/css/output.css

# Configuration
ENV PYTHONPATH=/app/src

# Exposer le port
EXPOSE 8001

# Commande par défaut
CMD ["uvicorn", "projet.app.web:app", "--host", "0.0.0.0", "--port", "8001"]
