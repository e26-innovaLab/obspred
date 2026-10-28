"""crear tabla habilidades_brechas
 
Revision ID: 7fbe156646c7
Revises: 367806ca3627
Create Date: 2026-10-26 23:44:46.127530

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7fbe156646c7'
down_revision: Union[str, Sequence[str], None] = '367806ca3627'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'habilidades_brechas',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column('ocupacion', sa.String(length=150), nullable=False),
        sa.Column('habilidad', sa.String(length=150), nullable=False),
        sa.Column('demanda', sa.Float(), nullable=False),
        sa.Column('oferta_formativa', sa.Float(), nullable=False),
        sa.Column('emergente', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint('ocupacion', 'habilidad', name='uq_habilidades_brechas_ocupacion_habilidad'),
    )
    with op.batch_alter_table('habilidades_brechas', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_habilidades_brechas_id'), ['id'], unique=False)
        batch_op.create_index(batch_op.f('ix_habilidades_brechas_ocupacion'), ['ocupacion'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('habilidades_brechas', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_habilidades_brechas_ocupacion'))
        batch_op.drop_index(batch_op.f('ix_habilidades_brechas_id'))
    op.drop_table('habilidades_brechas')