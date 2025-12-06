#!/usr/bin/env python3
"""Script pour créer le premier utilisateur admin.

Usage:
    python scripts/create_admin.py --email admin@example.com --password AdminPass123!
    
Ou avec variables d'environnement:
    ADMIN_EMAIL=admin@example.com ADMIN_PASSWORD=AdminPass123! python scripts/create_admin.py
"""

import os
import sys
import argparse
from pathlib import Path

# Ajouter le répertoire src au PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from projet.auth.database import SessionLocal
from projet.auth import models, security


def create_admin_user(email: str, password: str, first_name: str = None, last_name: str = None):
    """Crée un utilisateur admin."""
    db = SessionLocal()
    try:
        # Vérifier si l'utilisateur existe déjà
        existing_user = db.query(models.User).filter_by(email=email).first()
        if existing_user:
            print(f"❌ L'utilisateur {email} existe déjà.")
            return False
        
        # Vérifier si les rôles existent
        admin_role = db.query(models.Role).filter_by(name="admin").first()
        if not admin_role:
            print("⚠️  Le rôle 'admin' n'existe pas. Création...")
            admin_role = models.Role(name="admin")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("✅ Rôle 'admin' créé")
        
        user_role = db.query(models.Role).filter_by(name="user").first()
        if not user_role:
            print("⚠️  Le rôle 'user' n'existe pas. Création...")
            user_role = models.Role(name="user")
            db.add(user_role)
            db.commit()
            db.refresh(user_role)
            print("✅ Rôle 'user' créé")
        
        # Créer l'utilisateur admin
        admin_user = models.User(
            email=email,
            hashed_password=security.hash_password(password),
            is_verified=True,  # Admin auto-vérifié
            is_active=True,
            first_name=first_name,
            last_name=last_name
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        # Assigner les rôles admin et user
        admin_link = models.UserRole(user_id=admin_user.id, role_id=admin_role.id)
        user_link = models.UserRole(user_id=admin_user.id, role_id=user_role.id)
        db.add(admin_link)
        db.add(user_link)
        db.commit()
        
        print(f"✅ Utilisateur admin créé avec succès : {email}")
        print(f"   ID: {admin_user.id}")
        print(f"   Rôles: admin, user")
        return True
        
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur lors de la création de l'admin : {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Créer le premier utilisateur admin")
    parser.add_argument("--email", help="Email de l'admin", default=os.getenv("ADMIN_EMAIL"))
    parser.add_argument("--password", help="Mot de passe de l'admin", default=os.getenv("ADMIN_PASSWORD"))
    parser.add_argument("--first-name", help="Prénom (optionnel)", default=None)
    parser.add_argument("--last-name", help="Nom (optionnel)", default=None)
    
    args = parser.parse_args()
    
    if not args.email or not args.password:
        parser.print_help()
        print("\n❌ Email et mot de passe requis")
        print("   Utilisez --email et --password ou les variables ADMIN_EMAIL et ADMIN_PASSWORD")
        sys.exit(1)
    
    success = create_admin_user(args.email, args.password, args.first_name, args.last_name)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

