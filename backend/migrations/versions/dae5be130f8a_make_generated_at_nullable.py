"""make generated_at nullable

Revision ID: dae5be130f8a
Revises: 002d59f5f897
Create Date: 2025-08-24 00:07:33.740393

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dae5be130f8a'
down_revision = '002d59f5f897'
branch_labels = None
depends_on = None


def upgrade():
    # Make generated_at column nullable
    op.alter_column('documents', 'generated_at',
                    existing_type=sa.DateTime(),
                    nullable=True,
                    existing_server_default=None)


def downgrade():
    # Make generated_at column NOT NULL again
    op.alter_column('documents', 'generated_at',
                    existing_type=sa.DateTime(),
                    nullable=False,
                    existing_server_default=None)
