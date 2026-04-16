"""add archived status and report history table

Revision ID: 8bbbcda056d1
Revises: 1810197e79a8
Create Date: 2026-04-16 11:10:02.282823

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8bbbcda056d1'
down_revision = '1810197e79a8'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'report_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('report_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('nuevo', 'en_proceso', 'finalizado', 'archivado'), nullable=False),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.Column('changed_by_user_login', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id']),
        sa.PrimaryKeyConstraint('id')
    )

    with op.batch_alter_table('report_history', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_report_history_report_id'), ['report_id'], unique=False)

    # Agregar el nuevo valor al enum de reports.status
    op.execute("""
        ALTER TABLE reports
        MODIFY COLUMN status ENUM('nuevo', 'en_proceso', 'finalizado', 'archivado')
        NOT NULL DEFAULT 'nuevo'
    """)


def downgrade():
    with op.batch_alter_table('report_history', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_report_history_report_id'))

    op.drop_table('report_history')

    # Revertir enum de reports.status
    op.execute("""
        ALTER TABLE reports
        MODIFY COLUMN status ENUM('nuevo', 'en_proceso', 'finalizado')
        NOT NULL DEFAULT 'nuevo'
    """)