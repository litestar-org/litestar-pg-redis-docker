"""initial revision.

Revision ID: 769c4a8c5435
Revises:
Create Date: 2022-07-10 23:21:51.492639
"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "769c4a8c5435"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "provider",
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_date", sa.DateTime(), nullable=False),
        sa.Column("updated_date", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_provider")),
        sa.UniqueConstraint("name", name=op.f("uq_provider_name")),
    )
    op.create_table(
        "entity",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column(
            "type",
            sa.Enum(
                "competitor",
                "contest",
                "sport",
                "sport_person",
                "team",
                "tournament",
                name="entitiesenum",
            ),
            nullable=False,
        ),
        sa.Column("owner_id", sa.UUID(), nullable=True),
        sa.Column("ryno_id", sa.Integer(), nullable=True),
        sa.Column(
            "extra",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("provider_id", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_date", sa.DateTime(), nullable=False),
        sa.Column("updated_date", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["entity.id"], name=op.f("fk_entity_owner_id_entity")),
        sa.ForeignKeyConstraint(["provider_id"], ["provider.id"], name=op.f("fk_entity_provider_id_provider")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_entity")),
    )
    op.create_index(op.f("ix_entity_owner_id"), "entity", ["owner_id"], unique=False)
    op.create_index(op.f("ix_entity_ryno_id"), "entity", ["ryno_id"], unique=False)
    op.create_table(
        "integration",
        sa.Column("type", sa.Enum("fixture_events", name="integrationenum"), nullable=False),
        sa.Column("provider_id", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_date", sa.DateTime(), nullable=False),
        sa.Column("updated_date", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["provider_id"], ["provider.id"], name=op.f("fk_integration_provider_id_provider")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_integration")),
        sa.UniqueConstraint("provider_id", "type", name="ux_integration_provider_type"),
    )
    op.create_index(op.f("ix_integration_type"), "integration", ["type"], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_integration_type"), table_name="integration")
    op.drop_table("integration")
    op.drop_index(op.f("ix_entity_ryno_id"), table_name="entity")
    op.drop_index(op.f("ix_entity_owner_id"), table_name="entity")
    op.drop_table("entity")
    op.drop_table("provider")
    # ### end Alembic commands ###