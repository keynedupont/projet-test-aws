"""organizations foundation for multi-tenant projects

Revision ID: 0004_organizations_foundation
Revises: c43e59031ab2
Create Date: 2026-02-23
"""
from alembic import op
import sqlalchemy as sa
from uuid import uuid4
from datetime import datetime


# revision identifiers, used by Alembic.
revision = "0004_organizations_foundation"
down_revision = "c43e59031ab2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "organizations",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("org_type", sa.String(length=20), nullable=False, server_default="team"),
        sa.Column("owner_user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "organization_users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.String(length=36), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="member"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "organization_id", name="uq_user_organization"),
    )

    with op.batch_alter_table("projects") as batch_op:
        batch_op.add_column(sa.Column("organization_id", sa.String(length=36), nullable=True))
        batch_op.create_index("ix_projects_organization_id", ["organization_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_projects_organization_id",
            "organizations",
            ["organization_id"],
            ["id"],
            ondelete="SET NULL",
        )

    # Backfill: create "Espace perso" for existing users and attach existing projects.
    connection = op.get_bind()
    now = datetime.utcnow()
    users = connection.execute(sa.text("SELECT id FROM users")).fetchall()

    personal_org_by_user: dict[int, str] = {}
    for row in users:
        user_id = row[0]
        org_id = str(uuid4())
        personal_org_by_user[user_id] = org_id
        connection.execute(
            sa.text(
                """
                INSERT INTO organizations (id, name, org_type, owner_user_id, created_at, updated_at)
                VALUES (:id, :name, :org_type, :owner_user_id, :created_at, :updated_at)
                """
            ),
            {
                "id": org_id,
                "name": "Espace perso",
                "org_type": "personal",
                "owner_user_id": user_id,
                "created_at": now,
                "updated_at": now,
            },
        )
        connection.execute(
            sa.text(
                """
                INSERT INTO organization_users (user_id, organization_id, role)
                VALUES (:user_id, :organization_id, :role)
                """
            ),
            {"user_id": user_id, "organization_id": org_id, "role": "owner"},
        )

    projects = connection.execute(
        sa.text(
            """
            SELECT p.id, pu.user_id
            FROM projects p
            LEFT JOIN project_users pu ON pu.project_id = p.id
            """
        )
    ).fetchall()
    for project_id, user_id in projects:
        if user_id is None:
            continue
        org_id = personal_org_by_user.get(int(user_id))
        if not org_id:
            continue
        connection.execute(
            sa.text("UPDATE projects SET organization_id = :organization_id WHERE id = :project_id"),
            {"organization_id": org_id, "project_id": project_id},
        )


def downgrade() -> None:
    with op.batch_alter_table("projects") as batch_op:
        batch_op.drop_constraint("fk_projects_organization_id", type_="foreignkey")
        batch_op.drop_index("ix_projects_organization_id")
        batch_op.drop_column("organization_id")

    op.drop_table("organization_users")
    op.drop_table("organizations")
