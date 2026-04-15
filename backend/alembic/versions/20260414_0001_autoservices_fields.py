"""Autoservices fields: yamap import + subscription plan.

Revision ID: 20260414_0001
Revises: 
Create Date: 2026-04-14
"""

from alembic import op
import sqlalchemy as sa

revision = "20260414_0001"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Новые поля для импорта из Яндекс.Карт
    op.add_column("partners", sa.Column("yamap_id", sa.String(50), nullable=True))
    op.add_column("partners", sa.Column("working_hours", sa.String(300), nullable=True))
    op.add_column("partners", sa.Column("payment_methods", sa.Text(), nullable=True))
    op.add_column("partners", sa.Column("whatsapp", sa.String(100), nullable=True))
    op.add_column("partners", sa.Column("vkontakte", sa.String(300), nullable=True))
    op.add_column("partners", sa.Column("region", sa.String(150), nullable=True))
    op.add_column("partners", sa.Column("subcategory", sa.String(500), nullable=True))
    op.add_column("partners", sa.Column("is_imported", sa.Boolean(), nullable=False, server_default=sa.text("false")))
    op.add_column("partners", sa.Column("yamap_reviews_count", sa.Integer(), nullable=False, server_default=sa.text("0")))

    # Уникальный индекс по yamap_id
    op.create_unique_constraint("uq_partners_yamap_id", "partners", ["yamap_id"])
    op.create_index("ix_partners_yamap_id", "partners", ["yamap_id"])
    op.create_index("ix_partners_region", "partners", ["region"])


def downgrade() -> None:
    op.drop_index("ix_partners_region", table_name="partners")
    op.drop_index("ix_partners_yamap_id", table_name="partners")
    op.drop_constraint("uq_partners_yamap_id", "partners", type_="unique")
    op.drop_column("partners", "yamap_reviews_count")
    op.drop_column("partners", "is_imported")
    op.drop_column("partners", "subcategory")
    op.drop_column("partners", "region")
    op.drop_column("partners", "vkontakte")
    op.drop_column("partners", "whatsapp")
    op.drop_column("partners", "payment_methods")
    op.drop_column("partners", "working_hours")
    op.drop_column("partners", "yamap_id")
