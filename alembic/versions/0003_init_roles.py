"""init roles: user and admin

Revision ID: 0003_init_roles
Revises: 0002_add_email_verification_expires
Create Date: 2025-11-06
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0003_init_roles'
down_revision = '0002_add_email_verification_expires'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Créer les rôles de base s'ils n'existent pas
    connection = op.get_bind()
    
    # Vérifier si les rôles existent déjà
    result = connection.execute(sa.text("SELECT COUNT(*) FROM roles WHERE name IN ('user', 'admin')"))
    count = result.scalar()
    
    if count == 0:
        # Insérer les rôles de base
        connection.execute(
            sa.text("INSERT INTO roles (name) VALUES ('user'), ('admin')")
        )
        connection.commit()
        print("✅ Rôles 'user' et 'admin' créés")
    elif count == 1:
        # Un seul rôle existe, ajouter l'autre
        result = connection.execute(sa.text("SELECT name FROM roles WHERE name IN ('user', 'admin')"))
        existing = [row[0] for row in result]
        if 'user' not in existing:
            connection.execute(sa.text("INSERT INTO roles (name) VALUES ('user')"))
        if 'admin' not in existing:
            connection.execute(sa.text("INSERT INTO roles (name) VALUES ('admin')"))
        connection.commit()
        print("✅ Rôles manquants ajoutés")
    else:
        print("ℹ️  Rôles 'user' et 'admin' existent déjà")


def downgrade() -> None:
    # Supprimer les rôles (attention : supprime aussi les user_roles associés)
    connection = op.get_bind()
    connection.execute(sa.text("DELETE FROM roles WHERE name IN ('user', 'admin')"))
    connection.commit()

