"""Tests d'intégration pour les endpoints API admin."""
import pytest
from fastapi.testclient import TestClient
from projet.auth.app import app
from projet.auth import database, models, security


def _override_db(db_session):
    """Injecte la session de test dans l'app FastAPI."""
    app.dependency_overrides[database.get_db] = lambda: db_session


class TestAdminUsers:
    """Tests pour GET /admin/users."""
    
    def test_get_users_requires_admin(self, db_session):
        """Test que GET /admin/users nécessite le rôle admin."""
        _override_db(db_session)
        
        # Créer les rôles
        user_role = models.Role(name="user")
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(user_role)
        
        # Créer un utilisateur normal
        regular_user = models.User(
            email="user@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)
        db_session.add(models.UserRole(user_id=regular_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Token pour utilisateur normal (utiliser l'ID et rôles comme dans /auth/login)
        # Construire la liste des rôles manuellement (plus fiable que user.roles qui peut ne pas être chargé)
        user_roles = ["user"]
        user_token = security.create_access_token(str(regular_user.id), roles=user_roles)
        
        with TestClient(app) as client:
            r = client.get(
                "/auth/admin/users",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert r.status_code == 403
        app.dependency_overrides.clear()
    
    def test_get_users_success(self, db_session):
        """Test GET /admin/users retourne la liste des utilisateurs."""
        _override_db(db_session)
        
        # Créer les rôles
        admin_role = models.Role(name="admin")
        user_role = models.Role(name="user")
        db_session.add(admin_role)
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(admin_role)
        db_session.refresh(user_role)
        
        # Créer admin
        admin_user = models.User(
            email="admin@test.com",
            hashed_password=security.hash_password("AdminPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=admin_role.id))
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Créer 2 utilisateurs normaux
        user1 = models.User(
            email="user1@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=False,
        )
        user2 = models.User(
            email="user2@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=False,
        )
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user1)
        db_session.refresh(user2)
        db_session.add(models.UserRole(user_id=user1.id, role_id=user_role.id))
        db_session.add(models.UserRole(user_id=user2.id, role_id=user_role.id))
        db_session.commit()
        
        # Token admin (utiliser l'ID et rôles comme dans /auth/login)
        admin_roles = [r.name for r in admin_user.roles]
        admin_token = security.create_access_token(str(admin_user.id), roles=admin_roles)
        
        with TestClient(app) as client:
            r = client.get(
                "/auth/admin/users",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert r.status_code == 200
            users = r.json()
            assert len(users) == 3  # admin + 2 users
            assert all("email" in u for u in users)
            assert all("is_active" in u for u in users)
            assert all("is_verified" in u for u in users)
            assert all("roles" in u for u in users)
        app.dependency_overrides.clear()
    
    def test_get_user_by_id(self, db_session):
        """Test GET /admin/users/{user_id} retourne les détails d'un utilisateur."""
        _override_db(db_session)
        
        # Créer les rôles
        admin_role = models.Role(name="admin")
        user_role = models.Role(name="user")
        db_session.add(admin_role)
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(admin_role)
        db_session.refresh(user_role)
        
        # Créer admin
        admin_user = models.User(
            email="admin@test.com",
            hashed_password=security.hash_password("AdminPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=admin_role.id))
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Créer utilisateur normal
        regular_user = models.User(
            email="user@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=False,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)
        db_session.add(models.UserRole(user_id=regular_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Token admin (utiliser l'ID et rôles comme dans /auth/login)
        admin_roles = [r.name for r in admin_user.roles]
        admin_token = security.create_access_token(str(admin_user.id), roles=admin_roles)
        
        with TestClient(app) as client:
            r = client.get(
                f"/auth/admin/users/{regular_user.id}",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert r.status_code == 200
            user = r.json()
            assert user["email"] == regular_user.email
            assert user["id"] == regular_user.id
            assert "roles" in user
        app.dependency_overrides.clear()


class TestAdminToggleActive:
    """Tests pour PUT /admin/users/{user_id}/toggle-active."""
    
    def test_toggle_active_requires_admin(self, db_session):
        """Test que toggle-active nécessite le rôle admin."""
        _override_db(db_session)
        
        # Créer les rôles
        user_role = models.Role(name="user")
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(user_role)
        
        # Créer utilisateur normal
        regular_user = models.User(
            email="user@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)
        db_session.add(models.UserRole(user_id=regular_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Token utilisateur normal (utiliser l'ID et rôles comme dans /auth/login)
        user_roles = [r.name for r in regular_user.roles]
        user_token = security.create_access_token(str(regular_user.id), roles=user_roles)
        
        with TestClient(app) as client:
            r = client.put(
                f"/auth/admin/users/{regular_user.id}/toggle-active",
                json={"is_active": False},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert r.status_code == 403
        app.dependency_overrides.clear()
    
    def test_toggle_active_success(self, db_session):
        """Test toggle-active active/désactive un utilisateur."""
        _override_db(db_session)
        
        # Créer les rôles
        admin_role = models.Role(name="admin")
        user_role = models.Role(name="user")
        db_session.add(admin_role)
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(admin_role)
        db_session.refresh(user_role)
        
        # Créer admin
        admin_user = models.User(
            email="admin@test.com",
            hashed_password=security.hash_password("AdminPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=admin_role.id))
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Créer utilisateur normal
        regular_user = models.User(
            email="user@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=False,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)
        assert regular_user.is_active is True
        db_session.add(models.UserRole(user_id=regular_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Token admin (utiliser l'ID et rôles comme dans /auth/login)
        admin_roles = [r.name for r in admin_user.roles]
        admin_token = security.create_access_token(str(admin_user.id), roles=admin_roles)
        
        with TestClient(app) as client:
            # Désactiver
            r = client.put(
                f"/auth/admin/users/{regular_user.id}/toggle-active",
                json={"is_active": False},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert r.status_code == 200
            
            # Vérifier que l'utilisateur est désactivé
            db_session.refresh(regular_user)
            assert regular_user.is_active is False
            
            # Réactiver
            r = client.put(
                f"/auth/admin/users/{regular_user.id}/toggle-active",
                json={"is_active": True},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert r.status_code == 200
            
            # Vérifier que l'utilisateur est réactivé
            db_session.refresh(regular_user)
            assert regular_user.is_active is True
        app.dependency_overrides.clear()


class TestAdminUpdateRoles:
    """Tests pour PUT /admin/users/{user_id}/roles."""
    
    def test_update_roles_requires_admin(self, db_session):
        """Test que update-roles nécessite le rôle admin."""
        _override_db(db_session)
        
        # Créer les rôles
        user_role = models.Role(name="user")
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(user_role)
        
        # Créer utilisateur normal
        regular_user = models.User(
            email="user@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)
        db_session.add(models.UserRole(user_id=regular_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Token utilisateur normal (utiliser l'ID et rôles comme dans /auth/login)
        user_roles = [r.name for r in regular_user.roles]
        user_token = security.create_access_token(str(regular_user.id), roles=user_roles)
        
        with TestClient(app) as client:
            r = client.put(
                f"/auth/admin/users/{regular_user.id}/roles",
                json={"role_names": ["user"]},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert r.status_code == 403
        app.dependency_overrides.clear()
    
    def test_update_roles_success(self, db_session):
        """Test update-roles modifie les rôles d'un utilisateur."""
        _override_db(db_session)
        
        # Créer les rôles
        admin_role = models.Role(name="admin")
        user_role = models.Role(name="user")
        db_session.add(admin_role)
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(admin_role)
        db_session.refresh(user_role)
        
        # Créer admin
        admin_user = models.User(
            email="admin@test.com",
            hashed_password=security.hash_password("AdminPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=admin_role.id))
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Créer utilisateur normal
        regular_user = models.User(
            email="user@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=False,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)
        db_session.add(models.UserRole(user_id=regular_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Token admin (utiliser l'ID et rôles comme dans /auth/login)
        admin_roles = [r.name for r in admin_user.roles]
        admin_token = security.create_access_token(str(admin_user.id), roles=admin_roles)
        
        with TestClient(app) as client:
            # Ajouter le rôle admin
            r = client.put(
                f"/auth/admin/users/{regular_user.id}/roles",
                json={"role_names": ["user", "admin"]},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert r.status_code == 200
            
            # Vérifier que l'utilisateur a maintenant les deux rôles
            user_roles = db_session.query(models.UserRole).filter_by(user_id=regular_user.id).all()
            role_ids = [ur.role_id for ur in user_roles]
            assert admin_role.id in role_ids
        app.dependency_overrides.clear()


class TestAdminUpdateUser:
    """Tests pour PUT /admin/users/{user_id}."""
    
    def test_update_user_requires_admin(self, db_session):
        """Test que update-user nécessite le rôle admin."""
        _override_db(db_session)
        
        # Créer les rôles
        user_role = models.Role(name="user")
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(user_role)
        
        # Créer utilisateur normal
        regular_user = models.User(
            email="user@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)
        db_session.add(models.UserRole(user_id=regular_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Token utilisateur normal (utiliser l'ID et rôles comme dans /auth/login)
        user_roles = [r.name for r in regular_user.roles]
        user_token = security.create_access_token(str(regular_user.id), roles=user_roles)
        
        with TestClient(app) as client:
            r = client.put(
                f"/auth/admin/users/{regular_user.id}",
                json={"email": "newemail@test.com"},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert r.status_code == 403
        app.dependency_overrides.clear()
    
    def test_update_user_email_success(self, db_session):
        """Test update-user modifie l'email d'un utilisateur."""
        _override_db(db_session)
        
        # Créer les rôles
        admin_role = models.Role(name="admin")
        user_role = models.Role(name="user")
        db_session.add(admin_role)
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(admin_role)
        db_session.refresh(user_role)
        
        # Créer admin
        admin_user = models.User(
            email="admin@test.com",
            hashed_password=security.hash_password("AdminPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=admin_role.id))
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Créer utilisateur normal
        regular_user = models.User(
            email="user@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=False,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)
        original_email = regular_user.email
        db_session.add(models.UserRole(user_id=regular_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Token admin (utiliser l'ID et rôles comme dans /auth/login)
        admin_roles = [r.name for r in admin_user.roles]
        admin_token = security.create_access_token(str(admin_user.id), roles=admin_roles)
        
        with TestClient(app) as client:
            r = client.put(
                f"/auth/admin/users/{regular_user.id}",
                json={"email": "newemail@test.com"},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert r.status_code == 200
            
            # Vérifier que l'email a été modifié
            db_session.refresh(regular_user)
            assert regular_user.email == "newemail@test.com"
            assert regular_user.email != original_email
        app.dependency_overrides.clear()
    
    def test_update_user_name_success(self, db_session):
        """Test update-user modifie le nom d'un utilisateur."""
        _override_db(db_session)
        
        # Créer les rôles
        admin_role = models.Role(name="admin")
        user_role = models.Role(name="user")
        db_session.add(admin_role)
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(admin_role)
        db_session.refresh(user_role)
        
        # Créer admin
        admin_user = models.User(
            email="admin@test.com",
            hashed_password=security.hash_password("AdminPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=admin_role.id))
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Créer utilisateur normal
        regular_user = models.User(
            email="user@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=False,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)
        db_session.add(models.UserRole(user_id=regular_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Token admin (utiliser l'ID et rôles comme dans /auth/login)
        admin_roles = [r.name for r in admin_user.roles]
        admin_token = security.create_access_token(str(admin_user.id), roles=admin_roles)
        
        with TestClient(app) as client:
            r = client.put(
                f"/auth/admin/users/{regular_user.id}",
                json={"first_name": "John", "last_name": "Doe"},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert r.status_code == 200
            
            # Vérifier que le nom a été modifié
            db_session.refresh(regular_user)
            assert regular_user.first_name == "John"
            assert regular_user.last_name == "Doe"
        app.dependency_overrides.clear()


class TestAdminForceVerify:
    """Tests pour PUT /admin/users/{user_id}/verify."""
    
    def test_force_verify_requires_admin(self, db_session):
        """Test que force-verify nécessite le rôle admin."""
        _override_db(db_session)
        
        # Créer les rôles
        user_role = models.Role(name="user")
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(user_role)
        
        # Créer utilisateur normal
        regular_user = models.User(
            email="user@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=False,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)
        assert regular_user.is_verified is False
        db_session.add(models.UserRole(user_id=regular_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Token utilisateur normal (utiliser l'ID et rôles comme dans /auth/login)
        user_roles = [r.name for r in regular_user.roles]
        user_token = security.create_access_token(str(regular_user.id), roles=user_roles)
        
        with TestClient(app) as client:
            r = client.put(
                f"/auth/admin/users/{regular_user.id}/verify",
                json={"is_verified": True},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert r.status_code == 403
        app.dependency_overrides.clear()
    
    def test_force_verify_success(self, db_session):
        """Test force-verify force la vérification email."""
        _override_db(db_session)
        
        # Créer les rôles
        admin_role = models.Role(name="admin")
        user_role = models.Role(name="user")
        db_session.add(admin_role)
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(admin_role)
        db_session.refresh(user_role)
        
        # Créer admin
        admin_user = models.User(
            email="admin@test.com",
            hashed_password=security.hash_password("AdminPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=admin_role.id))
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Créer utilisateur normal non vérifié
        regular_user = models.User(
            email="user@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=False,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)
        assert regular_user.is_verified is False
        db_session.add(models.UserRole(user_id=regular_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Token admin (utiliser l'ID et rôles comme dans /auth/login)
        admin_roles = [r.name for r in admin_user.roles]
        admin_token = security.create_access_token(str(admin_user.id), roles=admin_roles)
        
        with TestClient(app) as client:
            r = client.put(
                f"/auth/admin/users/{regular_user.id}/verify",
                json={"is_verified": True},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert r.status_code == 200
            
            # Vérifier que l'utilisateur est maintenant vérifié
            db_session.refresh(regular_user)
            assert regular_user.is_verified is True
        app.dependency_overrides.clear()


class TestAdminResetPassword:
    """Tests pour POST /admin/users/{user_id}/reset-password."""
    
    def test_reset_password_requires_admin(self, db_session):
        """Test que reset-password nécessite le rôle admin."""
        _override_db(db_session)
        
        # Créer les rôles
        user_role = models.Role(name="user")
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(user_role)
        
        # Créer utilisateur normal
        regular_user = models.User(
            email="user@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)
        db_session.add(models.UserRole(user_id=regular_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Token utilisateur normal (utiliser l'ID et rôles comme dans /auth/login)
        user_roles = [r.name for r in regular_user.roles]
        user_token = security.create_access_token(str(regular_user.id), roles=user_roles)
        
        with TestClient(app) as client:
            r = client.post(
                f"/auth/admin/users/{regular_user.id}/reset-password",
                json={"new_password": "NewPass123!"},
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert r.status_code == 403
        app.dependency_overrides.clear()
    
    def test_reset_password_success(self, db_session):
        """Test reset-password réinitialise le mot de passe."""
        _override_db(db_session)
        
        # Créer les rôles
        admin_role = models.Role(name="admin")
        user_role = models.Role(name="user")
        db_session.add(admin_role)
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(admin_role)
        db_session.refresh(user_role)
        
        # Créer admin
        admin_user = models.User(
            email="admin@test.com",
            hashed_password=security.hash_password("AdminPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=admin_role.id))
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Créer utilisateur normal
        regular_user = models.User(
            email="user@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)
        original_hash = regular_user.hashed_password
        db_session.add(models.UserRole(user_id=regular_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Token admin (utiliser l'ID et rôles comme dans /auth/login)
        # Construire la liste des rôles manuellement (plus fiable que user.roles qui peut ne pas être chargé)
        admin_roles = ["admin", "user"]
        admin_token = security.create_access_token(str(admin_user.id), roles=admin_roles)
        
        with TestClient(app) as client:
            r = client.post(
                f"/auth/admin/users/{regular_user.id}/reset-password",
                json={"new_password": "NewPass123!"},
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert r.status_code == 200
            
            # Vérifier que le hash du mot de passe a changé
            db_session.refresh(regular_user)
            assert regular_user.hashed_password != original_hash
            
            # Vérifier que le nouveau mot de passe fonctionne
            assert security.verify_password("NewPass123!", regular_user.hashed_password)
        app.dependency_overrides.clear()


class TestAdminRoles:
    """Tests pour GET /admin/roles."""
    
    def test_get_roles_requires_admin(self, db_session):
        """Test que GET /admin/roles nécessite le rôle admin."""
        _override_db(db_session)
        
        # Créer les rôles
        user_role = models.Role(name="user")
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(user_role)
        
        # Créer utilisateur normal
        regular_user = models.User(
            email="user@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)
        db_session.add(models.UserRole(user_id=regular_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Token utilisateur normal (utiliser l'ID et rôles comme dans /auth/login)
        user_roles = [r.name for r in regular_user.roles]
        user_token = security.create_access_token(str(regular_user.id), roles=user_roles)
        
        with TestClient(app) as client:
            r = client.get(
                "/auth/admin/roles",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert r.status_code == 403
        app.dependency_overrides.clear()
    
    def test_get_roles_success(self, db_session):
        """Test GET /admin/roles retourne la liste des rôles."""
        _override_db(db_session)
        
        # Créer les rôles
        admin_role = models.Role(name="admin")
        user_role = models.Role(name="user")
        db_session.add(admin_role)
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(admin_role)
        db_session.refresh(user_role)
        
        # Créer admin
        admin_user = models.User(
            email="admin@test.com",
            hashed_password=security.hash_password("AdminPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=admin_role.id))
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Token admin (utiliser l'ID et rôles comme dans /auth/login)
        # Construire la liste des rôles manuellement (plus fiable que user.roles qui peut ne pas être chargé)
        admin_roles = ["admin", "user"]
        admin_token = security.create_access_token(str(admin_user.id), roles=admin_roles)
        
        with TestClient(app) as client:
            r = client.get(
                "/auth/admin/roles",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert r.status_code == 200
            roles = r.json()
            assert len(roles) >= 2  # Au moins user et admin
            assert any(r["name"] == "user" for r in roles)
            assert any(r["name"] == "admin" for r in roles)
            assert all("id" in r for r in roles)
            assert all("name" in r for r in roles)
        app.dependency_overrides.clear()


class TestAdminStats:
    """Tests pour GET /admin/stats."""
    
    def test_get_stats_requires_admin(self, db_session):
        """Test que GET /admin/stats nécessite le rôle admin."""
        _override_db(db_session)
        
        # Créer les rôles
        user_role = models.Role(name="user")
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(user_role)
        
        # Créer utilisateur normal
        regular_user = models.User(
            email="user@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(regular_user)
        db_session.commit()
        db_session.refresh(regular_user)
        db_session.add(models.UserRole(user_id=regular_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Token utilisateur normal (utiliser l'ID et rôles comme dans /auth/login)
        user_roles = [r.name for r in regular_user.roles]
        user_token = security.create_access_token(str(regular_user.id), roles=user_roles)
        
        with TestClient(app) as client:
            r = client.get(
                "/auth/admin/stats",
                headers={"Authorization": f"Bearer {user_token}"}
            )
            assert r.status_code == 403
        app.dependency_overrides.clear()
    
    def test_get_stats_success(self, db_session):
        """Test GET /admin/stats retourne les statistiques."""
        _override_db(db_session)
        
        # Créer les rôles
        admin_role = models.Role(name="admin")
        user_role = models.Role(name="user")
        db_session.add(admin_role)
        db_session.add(user_role)
        db_session.commit()
        db_session.refresh(admin_role)
        db_session.refresh(user_role)
        
        # Créer admin
        admin_user = models.User(
            email="admin@test.com",
            hashed_password=security.hash_password("AdminPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(admin_user)
        db_session.commit()
        db_session.refresh(admin_user)
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=admin_role.id))
        db_session.add(models.UserRole(user_id=admin_user.id, role_id=user_role.id))
        db_session.commit()
        
        # Créer 2 utilisateurs normaux
        user1 = models.User(
            email="user1@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=False,
        )
        user2 = models.User(
            email="user2@test.com",
            hashed_password=security.hash_password("UserPass123!"),
            is_active=True,
            is_verified=True,
        )
        db_session.add(user1)
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user1)
        db_session.refresh(user2)
        db_session.add(models.UserRole(user_id=user1.id, role_id=user_role.id))
        db_session.add(models.UserRole(user_id=user2.id, role_id=user_role.id))
        db_session.commit()
        
        # Token admin (utiliser l'ID et rôles comme dans /auth/login)
        admin_roles = [r.name for r in admin_user.roles]
        admin_token = security.create_access_token(str(admin_user.id), roles=admin_roles)
        
        with TestClient(app) as client:
            r = client.get(
                "/auth/admin/stats",
                headers={"Authorization": f"Bearer {admin_token}"}
            )
            assert r.status_code == 200
            stats = r.json()
            # Structure réelle de l'endpoint : {"users": {"total": ..., "active": ..., "verified": ...}, "roles": {...}}
            assert "users" in stats
            assert "roles" in stats
            assert "total" in stats["users"]
            assert "active" in stats["users"]
            assert "verified" in stats["users"]
            assert stats["users"]["total"] == 3
            assert stats["users"]["active"] == 3
            assert stats["users"]["verified"] >= 2  # admin + user2
        app.dependency_overrides.clear()
