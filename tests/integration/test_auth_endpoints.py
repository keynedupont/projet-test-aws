import pytest
from fastapi.testclient import TestClient
from projet.auth.app import app


def test_register_then_login(db_session):
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


def test_register_duplicate_email_returns_400(db_session):
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


def test_login_wrong_password_returns_401(db_session):
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


def test_me_with_and_without_token(db_session):
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


def test_personal_organization_created_at_register(db_session):
    with TestClient(app) as client:
        r = client.post("/auth/register", json={
            "email": "org-init@test.com",
            "password": "Test123!",
            "first_name": None,
            "last_name": None,
        })
        assert r.status_code == 201

        login = client.post("/auth/login", data={"username": "org-init@test.com", "password": "Test123!"})
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        orgs = client.get("/auth/organizations", headers=headers)
        assert orgs.status_code == 200
        body = orgs.json()
        assert len(body) >= 1
        assert any(o.get("org_type") == "personal" for o in body)


def test_projects_are_isolated_by_organization_header(db_session):
    with TestClient(app) as client:
        r = client.post("/auth/register", json={
            "email": "org-scope@test.com",
            "password": "Test123!",
            "first_name": None,
            "last_name": None,
        })
        assert r.status_code == 201

        login = client.post("/auth/login", data={"username": "org-scope@test.com", "password": "Test123!"})
        assert login.status_code == 200
        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        orgs_resp = client.get("/auth/organizations", headers=headers)
        assert orgs_resp.status_code == 200
        personal_org = next(o for o in orgs_resp.json() if o.get("org_type") == "personal")
        personal_org_id = personal_org["id"]

        team_resp = client.post("/auth/organizations", json={"name": "Equipe A"}, headers=headers)
        assert team_resp.status_code == 201
        team_org_id = team_resp.json()["id"]

        p1 = client.post(
            "/auth/projects",
            json={},
            headers={"Authorization": f"Bearer {token}", "organization-id": personal_org_id},
        )
        assert p1.status_code == 201
        p1_id = p1.json()["id"]

        p2 = client.post(
            "/auth/projects",
            json={},
            headers={"Authorization": f"Bearer {token}", "organization-id": team_org_id},
        )
        assert p2.status_code == 201
        p2_id = p2.json()["id"]

        list_personal = client.get(
            "/auth/projects",
            headers={"Authorization": f"Bearer {token}", "organization-id": personal_org_id},
        )
        assert list_personal.status_code == 200
        personal_ids = {p["id"] for p in list_personal.json()}
        assert p1_id in personal_ids
        assert p2_id not in personal_ids

        list_team = client.get(
            "/auth/projects",
            headers={"Authorization": f"Bearer {token}", "organization-id": team_org_id},
        )
        assert list_team.status_code == 200
        team_ids = {p["id"] for p in list_team.json()}
        assert p2_id in team_ids
        assert p1_id not in team_ids
