"""change report id to bigint with daily formatted id"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision = 'fe4a9c9b82a4'
down_revision = '8bbbcda056d1'
branch_labels = None
depends_on = None


def _get_fk_name(table_name: str, column_name: str, referred_table: str):
    bind = op.get_bind()
    result = bind.execute(
        sa.text("""
            SELECT CONSTRAINT_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE TABLE_SCHEMA = DATABASE()
              AND TABLE_NAME = :table_name
              AND COLUMN_NAME = :column_name
              AND REFERENCED_TABLE_NAME = :referred_table
            LIMIT 1
        """),
        {
            "table_name": table_name,
            "column_name": column_name,
            "referred_table": referred_table,
        }
    ).scalar()

    return result


def _drop_fk_if_exists(table_name: str, column_name: str, referred_table: str):
    fk_name = _get_fk_name(table_name, column_name, referred_table)
    if fk_name:
        op.drop_constraint(fk_name, table_name, type_='foreignkey')


def upgrade():
    # 1) Borrar FKs reales si existen
    _drop_fk_if_exists('evidences', 'report_id', 'reports')
    _drop_fk_if_exists('report_behaviors', 'report_id', 'reports')
    _drop_fk_if_exists('report_history', 'report_id', 'reports')
    _drop_fk_if_exists('report_impacts', 'report_id', 'reports')

    # 2) Cambiar PK principal
    op.alter_column(
        'reports',
        'id',
        existing_type=mysql.INTEGER(),
        type_=sa.BigInteger(),
        existing_nullable=False,
        autoincrement=False
    )

    # 3) Cambiar FKs hijas
    op.alter_column(
        'evidences',
        'report_id',
        existing_type=mysql.INTEGER(),
        type_=sa.BigInteger(),
        existing_nullable=False
    )

    op.alter_column(
        'report_behaviors',
        'report_id',
        existing_type=mysql.INTEGER(),
        type_=sa.BigInteger(),
        existing_nullable=False
    )

    op.alter_column(
        'report_history',
        'report_id',
        existing_type=mysql.INTEGER(),
        type_=sa.BigInteger(),
        existing_nullable=False
    )

    op.alter_column(
        'report_impacts',
        'report_id',
        existing_type=mysql.INTEGER(),
        type_=sa.BigInteger(),
        existing_nullable=False
    )

    # 4) Recrear FKs con nombres estables
    op.create_foreign_key(
        'fk_evidences_report_id_reports',
        'evidences', 'reports',
        ['report_id'], ['id']
    )

    op.create_foreign_key(
        'fk_report_behaviors_report_id_reports',
        'report_behaviors', 'reports',
        ['report_id'], ['id']
    )

    op.create_foreign_key(
        'fk_report_history_report_id_reports',
        'report_history', 'reports',
        ['report_id'], ['id']
    )

    op.create_foreign_key(
        'fk_report_impacts_report_id_reports',
        'report_impacts', 'reports',
        ['report_id'], ['id']
    )


def downgrade():
    # 1) Borrar FKs nuevas si existen
    _drop_fk_if_exists('evidences', 'report_id', 'reports')
    _drop_fk_if_exists('report_behaviors', 'report_id', 'reports')
    _drop_fk_if_exists('report_history', 'report_id', 'reports')
    _drop_fk_if_exists('report_impacts', 'report_id', 'reports')

    # 2) Revertir hijas
    op.alter_column(
        'evidences',
        'report_id',
        existing_type=sa.BigInteger(),
        type_=mysql.INTEGER(),
        existing_nullable=False
    )

    op.alter_column(
        'report_behaviors',
        'report_id',
        existing_type=sa.BigInteger(),
        type_=mysql.INTEGER(),
        existing_nullable=False
    )

    op.alter_column(
        'report_history',
        'report_id',
        existing_type=sa.BigInteger(),
        type_=mysql.INTEGER(),
        existing_nullable=False
    )

    op.alter_column(
        'report_impacts',
        'report_id',
        existing_type=sa.BigInteger(),
        type_=mysql.INTEGER(),
        existing_nullable=False
    )

    # 3) Revertir principal
    op.alter_column(
        'reports',
        'id',
        existing_type=sa.BigInteger(),
        type_=mysql.INTEGER(),
        existing_nullable=False,
        autoincrement=True
    )

    # 4) Recrear FKs
    op.create_foreign_key(
        'fk_evidences_report_id_reports',
        'evidences', 'reports',
        ['report_id'], ['id']
    )

    op.create_foreign_key(
        'fk_report_behaviors_report_id_reports',
        'report_behaviors', 'reports',
        ['report_id'], ['id']
    )

    op.create_foreign_key(
        'fk_report_history_report_id_reports',
        'report_history', 'reports',
        ['report_id'], ['id']
    )

    op.create_foreign_key(
        'fk_report_impacts_report_id_reports',
        'report_impacts', 'reports',
        ['report_id'], ['id']
    )