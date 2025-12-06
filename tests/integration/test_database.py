from projet.auth.database import Base, engine, SessionLocal
from projet.auth import models


def test_migrations_applied():
    # Vérifie que les tables principales existent après création du schéma
    Base.metadata.create_all(bind=engine)
    from sqlalchemy import inspect
    insp = inspect(engine)
    tables = set(insp.get_table_names())
    assert {"users", "roles", "user_roles", "refresh_tokens"}.issubset(tables)


def test_crud_minimal_user():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        u = models.User(email="crud@test.com", hashed_password="h")
        db.add(u); db.commit(); db.refresh(u)
        got = db.query(models.User).filter_by(email="crud@test.com").first()
        assert got is not None and got.id == u.id
    finally:
        db.close()
