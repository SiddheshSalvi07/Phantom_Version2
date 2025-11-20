"""initial tables

Revision ID: 0001_init
Revises: 
Create Date: 2025-11-20
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0001_init'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(length=255), nullable=False, unique=True, index=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('task_uuid', sa.String(length=128), nullable=False, unique=True, index=True),
        sa.Column('owner_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=False),
        sa.Column('title', sa.String(length=255)),
        sa.Column('description', sa.Text()),
        sa.Column('status', sa.String(length=50), default='created'),
        sa.Column('approved', sa.Integer(), default=0),
        sa.Column('plan', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )
    op.create_table(
        'task_logs',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id')), 
        sa.Column('status', sa.String(length=50)),
        sa.Column('payload', sa.Text()),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_table('task_logs')
    op.drop_table('tasks')
    op.drop_table('users')
