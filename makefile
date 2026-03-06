.PHONY: venv install test

PY := python3.11


venv:               ## crée un venv local .venv
	$(PY) -m venv .venv

install:            ## installe les dépendances
	. .venv/bin/activate && pip install -U pip && pip install -e .

install-minimal:    ## installe les dépendances minimales (plus rapide)
	. .venv/bin/activate && pip install -U pip && pip install -r requirements-minimal.txt
	@echo "🎨 Installation du frontend..."
	@if command -v npm >/dev/null 2>&1; then \
		npm install && npm run build-css && echo "✅ Frontend installé avec succès"; \
	else \
		echo "⚠️  npm non trouvé. Installez Node.js pour le frontend Tailwind CSS"; \
		echo "   Ou utilisez: make install-frontend après avoir installé Node.js"; \
	fi

install-frontend:   ## installe les dépendances frontend (Tailwind CSS)
	npm install
	npm run build-css

install-full:       ## installation complète (backend + frontend)
	. .venv/bin/activate && pip install -U pip && pip install -e .
	npm install && npm run build-css

test:               ## lance les tests
	. .venv/bin/activate && PYTHONPATH=src python -m pytest -q $(TEST_ARGS)


.PHONY: git-init dvc-init dvc-status dvc-add-raw dvc-push dvc-pull

git-init:         ## init git + premier commit
	git init
	git checkout -b main || true
	git add .
	git commit -m "init scaffold"

dvc-init:         ## init DVC dans ce repo
	. .venv/bin/activate && dvc init -q
	git add .dvc .dvcignore
	git commit -m "dvc: init"

dvc-status:       ## état DVC
	. .venv/bin/activate && dvc status

dvc-add-raw:      ## exemple: suivre data/raw avec DVC
	. .venv/bin/activate && dvc add data/raw
	git add data/raw.dvc .gitignore
	git commit -m "dvc: track data/raw"

dvc-push:         ## pousser les données/artefacts vers le remote DVC
	. .venv/bin/activate && dvc push

dvc-pull:         ## tirer les données/artefacts depuis le remote DVC
	. .venv/bin/activate && dvc pull


.PHONY: dvc-remote-dagshub

dvc-remote-dagshub:  ## configure DVC remote vers DagsHub
	@if [ ! -f .env ]; then echo "❌ Fichier .env manquant (copie .env.example et remplis tes valeurs)"; exit 1; fi
	@set -a; . .env; set +a; \
	if [ -z "$$DAGSHUB_USER" ] || [ -z "$$DAGSHUB_REPO" ] || [ -z "$$DAGSHUB_TOKEN" ]; then \
		echo "❌ Variables DAGSHUB_USER, DAGSHUB_REPO, DAGSHUB_TOKEN manquantes dans .env"; exit 1; fi; \
	. .venv/bin/activate && dvc remote add -d origin https://dagshub.com/$$DAGSHUB_USER/$$DAGSHUB_REPO.dvc || true; \
	. .venv/bin/activate && dvc remote modify origin --local auth basic; \
	. .venv/bin/activate && dvc remote modify origin --local user $$DAGSHUB_USER; \
	. .venv/bin/activate && dvc remote modify origin --local password $$DAGSHUB_TOKEN; \
	echo "✅ Remote DVC configuré : https://dagshub.com/$$DAGSHUB_USER/$$DAGSHUB_REPO.dvc"


.PHONY: mlflow-ui
mlflow-ui:  ## MLflow UI (sans gunicorn)
	@lsof -ti :5001 | xargs -r kill -9 || true
	@MLFLOW_PORT=5001 . .venv/bin/activate && python scripts/mlflow_ui.py

.PHONY: dev-auth dev-app db-revision db-upgrade install-fastapi

install-fastapi:  ## installe les dépendances FastAPI
	. .venv/bin/activate && pip install -e ".[fastapi]"

dev-auth:  ## lance l'API Auth (FastAPI)
	. .venv/bin/activate && PYTHONPATH=src uvicorn projet.auth.app:app --reload --host 0.0.0.0 --port 8000

APP_PORT ?= 8001
AUTH_SERVICE_URL ?= http://127.0.0.1:8000
dev-app: ## lance l'app web minimale (FastAPI templates)
	. .venv/bin/activate && AUTH_SERVICE_URL=$(AUTH_SERVICE_URL) PYTHONPATH=src uvicorn projet.app.web:app --reload --host 0.0.0.0 --port $(APP_PORT)

db-revision:  ## nouvelle migration (usage: make db-revision message="init")
	. .venv/bin/activate && PYTHONPATH=src alembic revision --autogenerate -m "$(message)"

db-upgrade:   ## applique les migrations
	. .venv/bin/activate && PYTHONPATH=src alembic upgrade head

create-admin:  ## crée un utilisateur admin (ADMIN_EMAIL=... ADMIN_PASSWORD=...)
	. .venv/bin/activate && PYTHONPATH=src python scripts/create_admin.py --email $(ADMIN_EMAIL) --password $(ADMIN_PASSWORD)

reset-admin:   ## réinitialise le mot de passe d'un utilisateur (ADMIN_EMAIL=... ADMIN_PASSWORD=...)
	. .venv/bin/activate && PYTHONPATH=src python scripts/reset_admin_password.py --email $(ADMIN_EMAIL) --password $(ADMIN_PASSWORD)

.PHONY: compose-up compose-down

compose-up:   ## démarre Postgres + auth + app
	docker compose up -d --build

compose-down: ## arrête la stack Docker
	docker compose down -v
