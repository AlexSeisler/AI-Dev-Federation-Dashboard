"""
Alembic migration script: Add DevBot Runner tables (tasks, logs, user_log, memory)

Revision ID: add_devbot_runner_tables
Revises: <put_previous_revision_here>
Create Date: 2025-09-14
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_devbot_runner_tables'
down_revision = None  # TODO: replace with actual previous revision id
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('type', sa.String, nullable=False),
        sa.Column('status', sa.String, default='pending'),
        sa.Column('created_at', sa.DateTime, server_default=sa.func.now())
    )

    op.create_table(
        'logs',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('task_id', sa.Integer, sa.ForeignKey('tasks.id'), nullable=False),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now()),
        sa.Column('message', sa.Text, nullable=False)
    )

    op.create_table(
        'user_log',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('task_id', sa.Integer, sa.ForeignKey('tasks.id'), nullable=False),
        sa.Column('timestamp', sa.DateTime, server_default=sa.func.now()),
        sa.Column('response', sa.Text, nullable=False)
    )

    op.create_table(
        'memory',
        sa.Column('id', sa.Integer, primary_key=True, index=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id'), nullable=False),
        sa.Column('data', postgresql.JSONB, nullable=False),
        sa.Column('queue_num', sa.Integer, nullable=False)
    )


def downgrade():
    op.drop_table('memory')
    op.drop_table('user_log')
    op.drop_table('logs')
    op.drop_table('tasks')
