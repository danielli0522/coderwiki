"""Add priority field to tasks table

Revision ID: add_priority_field_to_tasks
Revises: 77ede5a8b634
Create Date: 2025-08-24 02:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_priority_field_to_tasks'
down_revision = '77ede5a8b634'
branch_labels = None
depends_on = None


def upgrade():
    # Add priority column to tasks table
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.add_column(sa.Column('priority', sa.String(length=20), nullable=False, server_default='normal'))


def downgrade():
    # Remove priority column from tasks table
    with op.batch_alter_table('tasks', schema=None) as batch_op:
        batch_op.drop_column('priority')
