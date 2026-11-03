"""add_trimestre_to_indicadores

Revision ID: 2cedef4ea4e2
Revises: 367806ca3627
Create Date: 2026-11-03 17:08:03.864660

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2cedef4ea4e2'
down_revision: Union[str, Sequence[str], None] = '367806ca3627'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: añade columna trimestre e índice, y puebla registros existentes."""
    with op.batch_alter_table('indicadores', schema=None) as batch_op:
        batch_op.add_column(sa.Column('trimestre', sa.String(length=10), nullable=True))
        batch_op.create_index(batch_op.f('ix_indicadores_trimestre'), ['trimestre'], unique=False)

    # Migración de datos existentes: actualización con SQL ANSI compatible (PostgreSQL y SQLite)
    op.execute("UPDATE indicadores SET trimestre = 'Q1' WHERE periodo LIKE '%-Q1%' OR periodo LIKE '%Q1%'")
    op.execute("UPDATE indicadores SET trimestre = 'Q2' WHERE periodo LIKE '%-Q2%' OR periodo LIKE '%Q2%'")
    op.execute("UPDATE indicadores SET trimestre = 'Q3' WHERE periodo LIKE '%-Q3%' OR periodo LIKE '%Q3%'")
    op.execute("UPDATE indicadores SET trimestre = 'Q4' WHERE periodo LIKE '%-Q4%' OR periodo LIKE '%Q4%'")

    # Limpieza de periodo para remover el sufijo '-QX' y dejar solo el año
    op.execute("UPDATE indicadores SET periodo = replace(replace(replace(replace(periodo, '-Q1', ''), '-Q2', ''), '-Q3', ''), '-Q4', '') WHERE periodo LIKE '%-Q%'")


def downgrade() -> None:
    """Downgrade schema: elimina índice y columna trimestre."""
    with op.batch_alter_table('indicadores', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_indicadores_trimestre'))
        batch_op.drop_column('trimestre')
