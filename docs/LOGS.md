# 📋 Guide des logs

## Docker Compose

### Voir tous les logs
```bash
docker compose logs
```

### Logs en temps réel (suivi)
```bash
docker compose logs -f
```

### Logs d'un service spécifique
```bash
# Service auth (API)
docker compose logs auth

# Service app (Web)
docker compose logs app

# Service db (PostgreSQL)
docker compose logs db

# Service redis
docker compose logs redis
```

### Logs en temps réel d'un service
```bash
docker compose logs -f auth
```

### Dernières lignes (ex: 100 dernières)
```bash
docker compose logs --tail=100 auth
```

### Logs depuis une date/heure
```bash
docker compose logs --since 2025-11-10T09:00:00 auth
```

## Services locaux (make dev-*)

### Service auth
```bash
make dev-auth
# Les logs s'affichent directement dans le terminal
```

### Service app
```bash
make dev-app
# Les logs s'affichent directement dans le terminal
```

## Fichiers de logs (si configurés)

Les logs peuvent aussi être écrits dans :
- `tests/logs/` - Logs de tests
- `/tmp/emails.json` - Emails (si `EMAIL_BACKEND=file`)

## Recherche dans les logs

### Filtrer par mot-clé
```bash
docker compose logs auth | grep "ERROR"
docker compose logs auth | grep "admin"
```

### Compter les erreurs
```bash
docker compose logs auth | grep -c "ERROR"
```

## Debug des erreurs 500

Si vous voyez des erreurs 500, cherchez dans les logs :
```bash
docker compose logs auth | grep -A 10 "Internal error"
docker compose logs auth | grep -A 10 "trace_id"
```

Le `trace_id` dans l'erreur correspond au trace_id dans les logs pour faciliter le debug.

