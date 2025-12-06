from datetime import datetime, timedelta
import pytest
from sqlalchemy.exc import IntegrityError

from projet.auth.database import Base, engine, SessionLocal
from projet.auth import models


def setup_module(_):
    # Réinitialise le schéma pour ces tests
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


def teardown_module(_):
    Base.metadata.drop_all(bind=engine)


def test_user_creation_and_defaults():
    db = SessionLocal()
    try:
        u = models.User(email="u1@test.com", hashed_password="hash")
        db.add(u); db.commit(); db.refresh(u)
        assert u.id is not None
        assert u.is_active is True
        assert u.is_verified is False
        assert isinstance(u.created_at, datetime)
        assert isinstance(u.updated_at, datetime)
    finally:
        db.close()


def test_user_email_uniqueness():
    db = SessionLocal()
    try:
        db.add(models.User(email="unique@test.com", hashed_password="h"))
        db.commit()
        db.add(models.User(email="unique@test.com", hashed_password="h2"))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
    finally:
        db.close()


def test_roles_and_userrole_uniqueness():
    db = SessionLocal()
    try:
        u = models.User(email="role@test.com", hashed_password="h")
        r = models.Role(name="user")
        db.add_all([u, r]); db.commit(); db.refresh(u); db.refresh(r)
        link1 = models.UserRole(user_id=u.id, role_id=r.id)
        db.add(link1); db.commit()
        # doublon doit échouer
        link2 = models.UserRole(user_id=u.id, role_id=r.id)
        db.add(link2)
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
    finally:
        db.close()


def test_refresh_token_constraints():
    db = SessionLocal()
    try:
        u = models.User(email="rt@test.com", hashed_password="h")
        db.add(u); db.commit(); db.refresh(u)
        rt = models.RefreshToken(
            token_hash="abc",
            user_id=u.id,
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_at=datetime.utcnow(),
            is_revoked=False,
        )
        db.add(rt); db.commit(); db.refresh(rt)
        assert rt.id is not None
        # unicité token_hash
        db.add(models.RefreshToken(
            token_hash="abc",
            user_id=u.id,
            expires_at=datetime.utcnow() + timedelta(days=7),
            created_at=datetime.utcnow(),
            is_revoked=False,
        ))
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()
    finally:
        db.close()
