import os
import pytest
import httpx

# Skip par défaut sauf si E2E_NETWORK est défini
if not os.getenv("E2E_NETWORK"):
    pytestmark = pytest.mark.skip(reason="Définir E2E_NETWORK=1 pour activer les tests réseau (nécessite services Docker)")
else:
    pytestmark = pytest.mark.network

def test_app_health_after_tests():
    """Test que l'app fonctionne encore après tous les autres tests"""
    
    # Test que l'API auth répond
    with httpx.Client() as client:
        response = client.get("http://localhost:8000/health")
        assert response.status_code == 200
    
    # Test que l'app web répond
    with httpx.Client() as client:
        response = client.get("http://localhost:8001/")
        assert response.status_code == 200

def test_auth_register_works_after_tests():
    """Test que l'inscription fonctionne encore après tous les autres tests"""
    
    with httpx.Client() as client:
        response = client.post("http://localhost:8000/auth/register", json={
            "email": "health-check@example.com",
            "password": "HealthCheck123!",
            "first_name": None,
            "last_name": None,
        })
        assert response.status_code == 201
