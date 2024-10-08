"""Initial migration

Revision ID: 0001
Revises: 
Create Date: 2022-10-18 11:12:22.253864

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID


# revision identifiers, used by Alembic.
revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "price_paid_data",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("price", sa.INTEGER(), nullable=False),
        sa.Column("date_of_transfer", sa.DateTime(), nullable=False),
        sa.Column("postcode", sa.String(), default=False),
        sa.Column("property_type", sa.String(length=1), default=False),
        sa.Column("is_residential", sa.String(length=1), default=False),
        sa.Column("estate_type", sa.String(length=1), default=False),
        sa.Column("duration", sa.Integer(), default=False),
        sa.Column("paon", sa.String(), default=False),
        sa.Column("saon", sa.String(), default=False),
        sa.Column("street", sa.String(), default=False),
        sa.Column("locality", sa.String(), default=False),
        sa.Column("town", sa.String(), default=False),
        sa.Column("district", sa.String(), default=False),
        sa.Column("category_type", sa.String(length=1), default=False),
        sa.Column("record_status", sa.String(length=1), default=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("price_paid_data")
