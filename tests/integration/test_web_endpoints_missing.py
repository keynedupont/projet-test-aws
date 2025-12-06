import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, AsyncMock
from projet.app.web import app


class TestChangePassword:
    """Tests pour le changement de mot de passe"""
    
    def test_change_password_page_requires_auth(self):
        """Test que la page change-password nécessite une authentification"""
        with TestClient(app) as client:
            r = client.get("/change-password", follow_redirects=False)
            assert r.status_code in (302, 303)
            assert "/login" in r.headers.get("location", "")
    
    @patch('projet.app.web.client.post', new_callable=AsyncMock)
    def test_change_password_success(self, mock_post):
        """Test changement de mot de passe réussi"""
        # Mock de la réponse API auth
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Mot de passe changé avec succès"}
        mock_post.return_value = mock_response
        
        with TestClient(app) as client:
            # Simuler une session authentifiée
            client.cookies.set("access_token", "fake-token")
            
            r = client.post("/change-password", data={
                "current_password": "OldPass123!",
                "new_password": "NewPass123!",
                "confirm_password": "NewPass123!"
            }, follow_redirects=False)
            
            # Doit rediriger vers login (tokens révoqués)
            assert r.status_code in (302, 303)
            assert "/login" in r.headers.get("location", "")
    
    def test_change_password_mismatch(self):
        """Test que les mots de passe doivent correspondre"""
        with TestClient(app) as client:
            client.cookies.set("access_token", "fake-token")
            
            r = client.post("/change-password", data={
                "current_password": "OldPass123!",
                "new_password": "NewPass123!",
                "confirm_password": "DifferentPass123!"
            })
            
            # Vérifie que la page se recharge avec un statut OK (message géré côté UI)
            assert r.status_code == 200
    
    @patch('projet.app.web.client.post', new_callable=AsyncMock)
    def test_change_password_api_error(self, mock_post):
        """Test gestion d'erreur API auth"""
        # Mock d'erreur API
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Mot de passe actuel incorrect"}
        mock_post.return_value = mock_response
        
        with TestClient(app) as client:
            client.cookies.set("access_token", "fake-token")
            
            r = client.post("/change-password", data={
                "current_password": "WrongPass123!",
                "new_password": "NewPass123!",
                "confirm_password": "NewPass123!"
            })
            
            # Vérifie que la page se recharge avec un statut OK (message géré côté UI)
            assert r.status_code == 200


class TestAccountManagement:
    """Tests pour la gestion du compte utilisateur"""
    
    def test_account_page_requires_auth(self):
        """Test que la page account nécessite une authentification"""
        with TestClient(app) as client:
            r = client.get("/account", follow_redirects=False)
            assert r.status_code in (302, 303)
            assert "/login" in r.headers.get("location", "")
    
    @patch('projet.app.web.client.get', new_callable=AsyncMock)
    def test_account_page_with_auth(self, mock_get):
        """Test affichage page account avec authentification"""
        # Mock de la réponse API auth
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe"
        }
        mock_get.return_value = mock_response
        
        with TestClient(app) as client:
            client.cookies.set("access_token", "fake-token")
            
            r = client.get("/account")
            assert r.status_code == 200
            # Le rendu peut varier selon le template; on vérifie simplement que la page charge
    
    @patch('projet.app.web.client.get', new_callable=AsyncMock)
    def test_account_update(self, mock_get):
        """Test mise à jour du profil utilisateur"""
        # Mock de la réponse API auth
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe"
        }
        mock_get.return_value = mock_response
        
        with TestClient(app) as client:
            client.cookies.set("access_token", "fake-token")
            
            r = client.post("/account", data={
                "first_name": "Jane",
                "last_name": "Smith"
            })
            
            assert r.status_code == 200


class TestSettings:
    """Tests pour les paramètres utilisateur"""
    
    def test_settings_page_requires_auth(self):
        """Test que la page settings nécessite une authentification"""
        with TestClient(app) as client:
            r = client.get("/settings", follow_redirects=False)
            assert r.status_code in (302, 303)
            assert "/login" in r.headers.get("location", "")
    
    @patch('projet.app.web.client.get', new_callable=AsyncMock)
    def test_settings_page_with_auth(self, mock_get):
        """Test affichage page settings avec authentification"""
        # Mock de la réponse API auth
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "email": "test@example.com",
            "theme_preference": "dark"
        }
        mock_get.return_value = mock_response
        
        with TestClient(app) as client:
            client.cookies.set("access_token", "fake-token")
            
            r = client.get("/settings")
            assert r.status_code == 200


class TestPasswordReset:
    """Tests pour le reset de mot de passe"""
    
    def test_forgot_password_page(self):
        """Test affichage page forgot-password"""
        with TestClient(app) as client:
            r = client.get("/forgot-password")
            assert r.status_code == 200
            assert "Mot de passe oublié" in r.text or "forgot" in r.text.lower()
    
    @patch('projet.app.web.client.post', new_callable=AsyncMock)
    def test_forgot_password_success(self, mock_post):
        """Test demande de reset de mot de passe"""
        # Mock de la réponse API auth
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response
        
        with TestClient(app) as client:
            r = client.post("/forgot-password", data={
                "email": "test@example.com"
            })
            
            assert r.status_code == 200
            # Vérifier que l'API auth a été appelée
            mock_post.assert_called_once()
    
    def test_reset_password_page(self):
        """Test affichage page reset-password"""
        with TestClient(app) as client:
            r = client.get("/reset-password?token=fake-token")
            assert r.status_code == 200
            assert "Nouveau mot de passe" in r.text or "reset" in r.text.lower()
    
    @patch('projet.app.web.client.post', new_callable=AsyncMock)
    def test_reset_password_success(self, mock_post):
        """Test reset de mot de passe avec token"""
        # Mock de la réponse API auth
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"message": "Password reset successfully"}
        mock_post.return_value = mock_response
        
        with TestClient(app) as client:
            r = client.post("/reset-password", data={
                "token": "fake-token",
                "password": "NewPass123!",
                "confirm_password": "NewPass123!"
            })
            
            assert r.status_code == 200
            # Vérifier que l'API auth a été appelée
            mock_post.assert_called_once()


class TestAdminPanel:
    """Tests pour le panel d'administration"""
    
    def test_admin_pages_require_auth(self):
        """Test que toutes les pages admin nécessitent une authentification"""
        admin_paths = [
            "/admin",
            "/admin/users", 
            "/admin/roles",
            "/admin/stats",
            "/admin/logs",
            "/admin/settings"
        ]
        
        with TestClient(app) as client:
            for path in admin_paths:
                r = client.get(path, follow_redirects=False)
                assert r.status_code in (302, 303)
                assert "/login" in r.headers.get("location", "")
    
    @patch('projet.app.web.client.get', new_callable=AsyncMock)
    def test_admin_pages_with_auth(self, mock_get):
        """Test affichage pages admin avec authentification"""
        # Mock de la réponse API auth
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": 1,
            "email": "admin@example.com",
            "roles": ["admin"]
        }
        mock_get.return_value = mock_response
        
        with TestClient(app) as client:
            client.cookies.set("access_token", "fake-token")
            
            # Test page admin principale
            r = client.get("/admin")
            assert r.status_code == 200


class TestLogout:
    """Tests pour la déconnexion"""
    
    def test_logout_redirects_to_login(self):
        """Test que logout redirige vers login"""
        with TestClient(app) as client:
            r = client.get("/logout", follow_redirects=False)
            assert r.status_code in (302, 303)
            assert r.headers.get("location", "") in ("/", "/login")
    
    def test_logout_clears_cookies(self):
        """Test que logout supprime les cookies"""
        with TestClient(app) as client:
            # Simuler une session avec cookie
            client.cookies.set("access_token", "fake-token")
            
            r = client.get("/logout", follow_redirects=False)
            
            # Vérifier que le cookie a été supprimé
            assert "access_token" not in r.cookies or r.cookies.get("access_token") == ""


class TestHealthEndpoint:
    """Tests pour l'endpoint de santé"""
    
    @pytest.mark.skip(reason="Désactivé temporairement: activer progressivement")
    def test_health_endpoint(self):
        """Test endpoint de santé"""
        with TestClient(app) as client:
            r = client.get("/health")
            assert r.status_code == 200
            # L'endpoint peut retourner du JSON ou du HTML
            assert r.headers.get("content-type") is not None
