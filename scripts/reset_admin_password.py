#!/usr/bin/env python3
"""Réinitialise le mot de passe d'un utilisateur (ex. admin) et déverrouille le compte.

Usage:
    python scripts/reset_admin_password.py --email admin@example.com --password AdminPass123!

Ou avec variables d'environnement:
    ADMIN_EMAIL=admin@example.com ADMIN_PASSWORD=AdminPass123! python scripts/reset_admin_password.py
"""

import os
import sys
import argparse
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from projet.auth.database import SessionLocal
from projet.auth import models, security


def reset_password(email: str, new_password: str):
    """Met à jour le mot de passe et déverrouille le compte."""
    db = SessionLocal()
    try:
        user = db.query(models.User).filter_by(email=email).first()
        if not user:
            print(f"❌ Aucun utilisateur avec l'email {email}.")
            return False

        user.hashed_password = security.hash_password(new_password)
        user.failed_login_attempts = 0
        user.locked_until = None
        user.is_verified = True
        user.is_active = True
        db.commit()

        print(f"✅ Mot de passe mis à jour pour {email}")
        print(f"   Compte déverrouillé et vérifié.")
        return True
    except Exception as e:
        db.rollback()
        print(f"❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Réinitialiser le mot de passe d'un utilisateur")
    parser.add_argument("--email", help="Email de l'utilisateur", default=os.getenv("ADMIN_EMAIL"))
    parser.add_argument("--password", help="Nouveau mot de passe", default=os.getenv("ADMIN_PASSWORD"))
    args = parser.parse_args()

    email = args.email or os.getenv("ADMIN_EMAIL")
    password = args.password or os.getenv("ADMIN_PASSWORD")
    if not email or not password:
        parser.print_help()
        print("\n❌ --email et --password requis (ou ADMIN_EMAIL, ADMIN_PASSWORD)")
        sys.exit(1)

    success = reset_password(email, password)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
