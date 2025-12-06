"""add email_verification_token_expires_at and rename tokens to hash

Revision ID: 0002_add_email_verification_expires
Revises: 0001_init
Create Date: 2025-10-15
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0002_add_email_verification_expires'
down_revision = '0001_init'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Ajouter la colonne email_verification_token_expires_at
    op.add_column('users', sa.Column('email_verification_token_expires_at', sa.DateTime(), nullable=True))
    
    # Renommer email_verification_token → email_verification_token_hash
    op.alter_column('users', 'email_verification_token',
                    new_column_name='email_verification_token_hash',
                    existing_type=sa.String(),
                    existing_nullable=True)
    
    # Renommer password_reset_token → password_reset_token_hash
    op.alter_column('users', 'password_reset_token',
                    new_column_name='password_reset_token_hash',
                    existing_type=sa.String(),
                    existing_nullable=True)
    
    # NULL les tokens existants (nouveau système avec hash)
    # Les tokens JWT existants ne seront plus valides
    op.execute("UPDATE users SET email_verification_token_hash = NULL, password_reset_token_hash = NULL")


def downgrade() -> None:
    # Renommer email_verification_token_hash → email_verification_token
    op.alter_column('users', 'email_verification_token_hash',
                    new_column_name='email_verification_token',
                    existing_type=sa.String(),
                    existing_nullable=True)
    
    # Renommer password_reset_token_hash → password_reset_token
    op.alter_column('users', 'password_reset_token_hash',
                    new_column_name='password_reset_token',
                    existing_type=sa.String(),
                    existing_nullable=True)
    
    # Supprimer email_verification_token_expires_at
    op.drop_column('users', 'email_verification_token_expires_at')

