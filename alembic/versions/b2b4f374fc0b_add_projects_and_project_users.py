"""add projects and project_users

Revision ID: b2b4f374fc0b
Revises: 0003_init_roles
Create Date: 2026-03-16 20:23:53.294489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2b4f374fc0b'
down_revision: Union[str, Sequence[str], None] = '0003_init_roles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Cette migration auto-générée était invalide (drop des tables auth).
    # Conservée en no-op pour maintenir une chaîne Alembic cohérente.
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
