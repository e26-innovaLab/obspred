"""001_create_indicadores_table.

Revision ID: 41855ddca8c9
Revises:
Create Date: 2026-10-07 16:56:49.576678
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "41855ddca8c9"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Aplica la migración creando la tabla indicadores y sus índices."""
    op.create_table(
        "indicadores",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("pais", sa.String(length=10), nullable=False),
        sa.Column("sector", sa.String(length=100), nullable=True),
        sa.Column("ocupacion", sa.String(length=150), nullable=True),
        sa.Column("indicador", sa.String(length=100), nullable=False),
        sa.Column("periodo", sa.String(length=20), nullable=False),
        sa.Column("valor", sa.Float(), nullable=False),
        sa.Column("tipo", sa.String(length=20), nullable=False),
        sa.Column("fuente", sa.String(length=100), nullable=False),
        sa.Column("fecha_actualizacion", sa.Date(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("indicadores", schema=None) as batch_op:
        batch_op.create_index(
            "ix_indicadores_busqueda_temporal",
            ["pais", "indicador", "periodo"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_indicadores_id"),
            ["id"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_indicadores_indicador"),
            ["indicador"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_indicadores_ocupacion"),
            ["ocupacion"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_indicadores_pais"),
            ["pais"],
            unique=False,
        )
        batch_op.create_index(
            "ix_indicadores_pais_sector_ocupacion",
            ["pais", "sector", "ocupacion"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_indicadores_periodo"),
            ["periodo"],
            unique=False,
        )
        batch_op.create_index(
            batch_op.f("ix_indicadores_sector"),
            ["sector"],
            unique=False,
        )


def downgrade() -> None:
    """Revierte la migración eliminando índices y la tabla indicadores."""
    with op.batch_alter_table("indicadores", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_indicadores_sector"))
        batch_op.drop_index(batch_op.f("ix_indicadores_periodo"))
        batch_op.drop_index("ix_indicadores_pais_sector_ocupacion")
        batch_op.drop_index(batch_op.f("ix_indicadores_pais"))
        batch_op.drop_index(batch_op.f("ix_indicadores_ocupacion"))
        batch_op.drop_index(batch_op.f("ix_indicadores_indicador"))
        batch_op.drop_index(batch_op.f("ix_indicadores_id"))
        batch_op.drop_index("ix_indicadores_busqueda_temporal")

    op.drop_table("indicadores")
