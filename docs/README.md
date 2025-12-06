# 📚 Documentation Technique

> **Index de la documentation** pour le projet projet

## 🗂️ Structure de la documentation

### **📖 Guides utilisateur**
- [Installation et configuration](installation.md) - Setup complet du projet
- [Guide utilisateur](user-guide.md) - Utilisation de l'application
- [API Reference](api.md) - Documentation des endpoints

### **🏗️ Architecture et développement**
- [Architecture](architecture.md) - Vue d'ensemble technique
- [Configuration](configuration.md) - Variables d'environnement et subtilités
- [Développement](development.md) - Workflow et conventions

### **🚀 Déploiement et production**
- [Déploiement](DEPLOYMENT.md) - **Guide complet** : Docker, Registry (GHCR), CI/CD, AWS vs Scaleway, build vs image
- [Monitoring](monitoring.md) - Logs, métriques, observabilité
- [Troubleshooting](troubleshooting.md) - Erreurs communes et solutions

**Note :** La roadmap complète est dans `ROADMAP.md` (racine du projet).

---

## 🚀 Démarrage rapide

### **Installation en 2 minutes :**
```bash
# 1. Installation
make venv && source .venv/bin/activate
make install-minimal

# 2. Configuration
cp env.sample .env
mkdir -p data/external

# 3. Base de données
make db-upgrade

# 4. Services
make dev-auth    # Terminal 1
make dev-app     # Terminal 2
```

### **Avec Docker :**
```bash
make compose-up
```

---

## 📋 Liens utiles

- **Application** : http://localhost:8001
- **API Auth** : http://localhost:8000
- **Documentation API** : http://localhost:8000/docs
- **MLflow** : http://localhost:5001 (si activé)

---

## 🔄 Mise à jour de la documentation

Cette documentation est maintenue à jour avec le projet. Pour contribuer :

1. Modifier les fichiers `.md` dans `docs/`
2. Tester les instructions
3. Mettre à jour les liens si nécessaire

---

*Dernière mise à jour : 2024-01-XX*
