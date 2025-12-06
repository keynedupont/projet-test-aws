#!/usr/bin/env python3
import os
import sys
from pathlib import Path

# Ajouter src/ au PYTHONPATH pour importer les settings
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mlflow.server import app
from projet.settings import settings

port = settings.MLFLOW_PORT
try:
    from waitress import serve  # si installé
    serve(app, host="127.0.0.1", port=port)
except Exception:
    # fallback: serveur Flask (dev)
    app.run(host="127.0.0.1", port=port, debug=False)