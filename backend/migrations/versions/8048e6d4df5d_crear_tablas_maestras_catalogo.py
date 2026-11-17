"""crear_tablas_maestras_catalogo

Revision ID: 8048e6d4df5d
Revises: f25a85840a80
Create Date: 2026-11-16 17:59:51.974701

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8048e6d4df5d"
down_revision: str | Sequence[str] | None = "f25a85840a80"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema: crea tablas maestras para catálogo de forma idempotente."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    # 1. catalogo_paises
    if "catalogo_paises" not in tables:
        op.create_table(
            "catalogo_paises",
            sa.Column("id", sa.String(length=10), nullable=False),
            sa.Column("nombre", sa.String(length=100), nullable=False),
            sa.Column("orden", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.PrimaryKeyConstraint("id"),
        )

    # 2. catalogo_sectores
    if "catalogo_sectores" not in tables:
        op.create_table(
            "catalogo_sectores",
            sa.Column("id", sa.String(length=50), nullable=False),
            sa.Column("nombre", sa.String(length=100), nullable=False),
            sa.Column("isic", sa.JSON(), nullable=False),
            sa.Column("orden", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.PrimaryKeyConstraint("id"),
        )

    # 3. catalogo_ocupaciones
    if "catalogo_ocupaciones" not in tables:
        op.create_table(
            "catalogo_ocupaciones",
            sa.Column("id", sa.String(length=50), nullable=False),
            sa.Column("nombre", sa.String(length=150), nullable=False),
            sa.Column("sector_id", sa.String(length=50), nullable=False),
            sa.Column("isco", sa.String(length=20), nullable=True),
            sa.Column("orden", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.ForeignKeyConstraint(
                ["sector_id"], ["catalogo_sectores.id"], ondelete="CASCADE"
            ),
            sa.PrimaryKeyConstraint("id"),
        )
        with op.batch_alter_table("catalogo_ocupaciones", schema=None) as batch_op:
            batch_op.create_index(
                batch_op.f("ix_catalogo_ocupaciones_sector_id"),
                ["sector_id"],
                unique=False,
            )

    # 4. catalogo_indicadores
    if "catalogo_indicadores" not in tables:
        op.create_table(
            "catalogo_indicadores",
            sa.Column("id", sa.String(length=50), nullable=False),
            sa.Column("nombre", sa.String(length=150), nullable=False),
            sa.Column("unidad", sa.String(length=50), nullable=False),
            sa.Column("frecuencias", sa.JSON(), nullable=False),
            sa.Column("desagregaciones", sa.JSON(), nullable=False),
            sa.Column("descripcion", sa.String(length=500), nullable=True),
            sa.Column("orden", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("activo", sa.Boolean(), nullable=False, server_default=sa.true()),
            sa.PrimaryKeyConstraint("id"),
        )


def downgrade() -> None:
    """Downgrade schema: elimina tablas maestras del catálogo."""
    with op.batch_alter_table("catalogo_ocupaciones", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_catalogo_ocupaciones_sector_id"))

    op.drop_table("catalogo_ocupaciones")
    op.drop_table("catalogo_indicadores")
    op.drop_table("catalogo_sectores")
    op.drop_table("catalogo_paises")
