"""demo: add unique (user_id, name) to api_keys — SEEDED RISK

Revision ID: demo0001
Revises:
Create Date: 2026-08-27

SEEDED DEFECT (do not fix here): creates the composite unique constraint
WITHOUT deduplicating historical rows. On any database where a user has
two API keys sharing the same name (legal before this change), upgrade
fails with IntegrityError and leaves the DB at the prior revision.
"""
from alembic import op
import sqlalchemy as sa

revision = "demo0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_api_keys_user_name", "api_keys", ["user_id", "name"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_api_keys_user_name", "api_keys", type_="unique")
