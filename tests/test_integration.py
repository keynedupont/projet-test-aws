
import pytest
import httpx
from fastapi.testclient import TestClient

from projet.auth.app import app as auth_app
from projet.auth import database

from projet.app.web import app as web_app



@pytest.fixture
def auth_client(db_session):
    """Client de test pour l'API auth avec DB override."""
    auth_app.dependency_overrides[database.get_db] = lambda: db_session
    yield TestClient(auth_app)
    auth_app.dependency_overrides.clear()


@pytest.fixture
def web_client(db_session):
    """Client de test pour l'app web avec DB override dans auth_app."""
    # Override la DB dans auth_app car web_app fait des appels HTTP vers auth_app
    auth_app.dependency_overrides[database.get_db] = lambda: db_session
    yield TestClient(web_app)
    auth_app.dependency_overrides.clear()



def test_auth_register_login_flow(auth_client):
    """Test complet: register -> login -> /me"""
    # Register
    response = auth_client.post("/auth/register", json={
        "email": "test@example.com",
        "password": "TestPass123!",
        "first_name": None,
        "last_name": None
    })
    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == "test@example.com"
    assert "id" in user_data
    
    # Login
    response = auth_client.post("/auth/login", data={
        "username": "test@example.com",
        "password": "TestPass123!"
    })
    assert response.status_code == 200
    token_data = response.json()
    assert "access_token" in token_data
    token = token_data["access_token"]
    
    # /me
    response = auth_client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    me_data = response.json()
    assert me_data["email"] == "test@example.com"
    assert "roles" in me_data
    assert "user" in me_data["roles"]



def test_web_app_flow(web_client):
    """Test app web: signup -> login -> dashboard"""
    # Signup
    response = web_client.post("/signup", data={
        "email": "web@example.com",
        "password": "WebPass123!",
        "confirm-password": "WebPass123!",
        "terms": True
    })
    assert response.status_code == 303  # Redirect to login
    
    # Login
    response = web_client.post("/login", data={
        "email": "web@example.com",
        "password": "WebPass123!"
    })
    assert response.status_code == 303  # Redirect to dashboard
    
    # Dashboard (should work with session cookie)
    response = web_client.get("/dashboard")
    assert response.status_code == 200
    assert "web@example.com" in response.text


def test_admin_access_denied(web_client):
    """Test que /admin refuse l'accès sans rôle admin"""
    # First create the user via signup
    response = web_client.post("/signup", data={
        "email": "admin@example.com",
        "password": "AdminPass123!",
        "confirm-password": "AdminPass123!",
        "terms": True
    }, follow_redirects=False)
    assert response.status_code == 303
    
    # Login as regular user
    response = web_client.post("/login", data={
        "email": "admin@example.com",
        "password": "AdminPass123!"
    }, follow_redirects=False)
    assert response.status_code == 303
    
    # Try to access admin
    response = web_client.get("/admin")
    assert response.status_code == 403



def test_auth_invalid_credentials(auth_client):
    """Test login avec mauvais credentials"""
    response = auth_client.post("/auth/login", data={
        "username": "nonexistent@example.com",
        "password": "wrongpass"
    })
    assert response.status_code == 401


def test_auth_duplicate_email(auth_client):
    """Test register avec email déjà utilisé"""
    # First registration
    auth_client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "TestPass123!",
        "first_name": None,
        "last_name": None
    })
    
    # Second registration with same email
    response = auth_client.post("/auth/register", json={
        "email": "duplicate@example.com",
        "password": "TestPass123!",
        "first_name": None,
        "last_name": None
    })
    assert response.status_code == 400

