import pytest
from fastapi.testclient import TestClient
from projet.auth.app import app
from projet.auth import database


def _override_db(db_session):
    """Injecte la session de test dans l'app FastAPI."""
    def get_db_override():
        yield db_session
    app.dependency_overrides[database.get_db] = get_db_override


def test_register_then_login(db_session):
    _override_db(db_session)
    # Register
    with TestClient(app) as client:
        r = client.post("/auth/register", json={
            "email": "user@test.com",
            "password": "Test123!",
            "first_name": None,
            "last_name": None,
        })
        assert r.status_code == 201

        # Login
        r2 = client.post("/auth/login", data={"username": "user@test.com", "password": "Test123!"})
        assert r2.status_code == 200
        body = r2.json()
        assert "access_token" in body and body["access_token"]
        assert body.get("token_type") == "bearer"
    app.dependency_overrides.clear()


def test_register_duplicate_email_returns_400(db_session):
    _override_db(db_session)
    with TestClient(app) as client:
        # First registration
        r1 = client.post("/auth/register", json={
            "email": "dup@test.com",
            "password": "Test123!",
            "first_name": None,
            "last_name": None,
        })
        assert r1.status_code == 201
        # Second registration with same email
        r2 = client.post("/auth/register", json={
            "email": "dup@test.com",
            "password": "Test123!",
            "first_name": None,
            "last_name": None,
        })
        assert r2.status_code == 400
    app.dependency_overrides.clear()


def test_login_wrong_password_returns_401(db_session):
    _override_db(db_session)
    with TestClient(app) as client:
        # Register
        r = client.post("/auth/register", json={
            "email": "wrongpwd@test.com",
            "password": "Test123!",
            "first_name": None,
            "last_name": None,
        })
        assert r.status_code == 201
        # Try login with wrong password
        r2 = client.post("/auth/login", data={"username": "wrongpwd@test.com", "password": "Wrong123!"})
        assert r2.status_code == 401
    app.dependency_overrides.clear()


def test_me_with_and_without_token(db_session):
    _override_db(db_session)
    with TestClient(app) as client:
        # Register and login to get token
        r = client.post("/auth/register", json={
            "email": "me@test.com",
            "password": "Test123!",
            "first_name": None,
            "last_name": None,
        })
        assert r.status_code == 201
        r2 = client.post("/auth/login", data={"username": "me@test.com", "password": "Test123!"})
        assert r2.status_code == 200
        token = r2.json()["access_token"]

        # Without token -> 401
        noauth = client.get("/auth/me")
        assert noauth.status_code == 401

        # With token -> 200 and correct email
        headers = {"Authorization": f"Bearer {token}"}
        withauth = client.get("/auth/me", headers=headers)
        assert withauth.status_code == 200
        assert withauth.json().get("email") == "me@test.com"
    app.dependency_overrides.clear()
