import pytest
from fastapi.testclient import TestClient


def test_e2e_api_register_login_me(db_session):
    # Import local pour éviter les effets de bord pendant la collecte
    from projet.auth.app import app as auth_app
    from projet.auth import database
    
    # Override la dépendance DB
    auth_app.dependency_overrides[database.get_db] = lambda: db_session

    with TestClient(auth_app) as client:
        # Register
        r = client.post(
            "/auth/register",
            json={
                "email": "e2e_api@example.com",
                "password": "E2ePass123!",
                "first_name": None,
                "last_name": None,
            },
        )
        assert r.status_code == 201

        # Login
        r = client.post(
            "/auth/login",
            data={"username": "e2e_api@example.com", "password": "E2ePass123!"},
        )
        assert r.status_code == 200
        body = r.json()
        assert body.get("token_type") == "bearer"
        token = body.get("access_token")
        assert token

        # /me
        r = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        assert r.json().get("email") == "e2e_api@example.com"
    
    auth_app.dependency_overrides.clear()


def test_e2e_web_signup_login_dashboard_logout(db_session):
    # Import local pour éviter les effets de bord pendant la collecte
    from projet.app.web import app as web_app
    from projet.auth.app import app as auth_app
    from projet.auth import database
    
    # Override la DB dans auth_app car web_app fait des appels HTTP vers auth_app
    auth_app.dependency_overrides[database.get_db] = lambda: db_session

    with TestClient(web_app) as client:
        # Signup
        r = client.post(
            "/signup",
            data={
                "email": "e2e_web@example.com",
                "password": "E2ePass123!",
                "confirm-password": "E2ePass123!",
                "terms": True,
            },
            follow_redirects=False,
        )
        assert r.status_code in (302, 303)

        # Login
        r = client.post(
            "/login",
            data={"email": "e2e_web@example.com", "password": "E2ePass123!"},
            follow_redirects=False,
        )
        assert r.status_code in (302, 303)

        # Dashboard accessible avec session
        r = client.get("/dashboard")
        assert r.status_code == 200

        # Logout
        r = client.get("/logout", follow_redirects=False)
        assert r.status_code in (302, 303)

        # Dashboard doit rediriger si non authentifié
        r = client.get("/dashboard", follow_redirects=False)
        assert r.status_code in (302, 303)
    
    auth_app.dependency_overrides.clear()


