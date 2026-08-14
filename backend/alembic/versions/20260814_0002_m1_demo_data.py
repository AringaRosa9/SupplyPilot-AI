"""Add M1 inventory snapshots.

Revision ID: 20260814_0002
Revises: 20260811_0001
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260814_0002"
down_revision = "20260811_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inventory_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("product_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("snapshot_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("inventory", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(12, 2), nullable=False),
        sa.Column("benchmark_price", sa.Numeric(12, 2), nullable=False),
        sa.Column("conversion_rate", sa.Numeric(7, 4), nullable=False),
        sa.ForeignKeyConstraint(
            ["product_id"], ["products.id"], name="fk_inventory_snapshots_product_id_products"
        ),
        sa.PrimaryKeyConstraint("id", name="pk_inventory_snapshots"),
    )
    op.create_index(
        "ix_inventory_snapshots_product_id", "inventory_snapshots", ["product_id"]
    )
    op.create_index(
        "ix_inventory_snapshots_snapshot_at", "inventory_snapshots", ["snapshot_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_inventory_snapshots_snapshot_at", table_name="inventory_snapshots")
    op.drop_index("ix_inventory_snapshots_product_id", table_name="inventory_snapshots")
    op.drop_table("inventory_snapshots")
