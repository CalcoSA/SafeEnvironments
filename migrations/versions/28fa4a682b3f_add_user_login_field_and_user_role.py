"""add user_login field and user role

Revision ID: 28fa4a682b3f
Revises: 60f64592de38
Create Date: 2026-04-15 10:34:52.847086
"""
from alembic import op
import sqlalchemy as sa

revision = '28fa4a682b3f'
down_revision = '60f64592de38'
branch_labels = None
depends_on = None

def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_login', sa.String(length=100), nullable=True))
        batch_op.create_index(batch_op.f('ix_users_user_login'), ['user_login'], unique=True)

    op.execute("""
        ALTER TABLE users
        MODIFY COLUMN role ENUM('reporter','user','admin') NOT NULL DEFAULT 'reporter'
    """)

def downgrade():
    op.execute("""
        ALTER TABLE users
        MODIFY COLUMN role ENUM('reporter','admin') NOT NULL DEFAULT 'reporter'
    """)

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_users_user_login'))
        batch_op.drop_column('user_login')