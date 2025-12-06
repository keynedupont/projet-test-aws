import os
import secrets
import pytest
from projet.auth.database import Base, engine

# Prépare une SECRET_KEY pour les tests si absente
if not os.environ.get("SECRET_KEY"):
    os.environ["SECRET_KEY"] = secrets.token_hex(32)

# Utilise SQLite fichier local par défaut pendant les tests
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_app.db")


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
