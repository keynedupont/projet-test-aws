import os
import secrets

# IMPORTANT : Définir SECRET_KEY AVANT tout import qui pourrait l'utiliser
# (notamment security.py qui lit settings.SECRET_KEY au moment de l'import)
if not os.environ.get("SECRET_KEY"):
    os.environ["SECRET_KEY"] = secrets.token_hex(32)  # 64 caractères (32 bytes en hex)

# Utilise SQLite en mémoire pour les tests (plus rapide, pas de fichiers)
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

# Maintenant on peut importer les modules qui utilisent SECRET_KEY
import pytest
from projet.auth.database import Base, engine


@pytest.fixture(scope="function")
def db_session():
    """Fixture pour créer une session DB propre pour chaque test."""
    Base.metadata.create_all(bind=engine)
    from projet.auth.database import SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
