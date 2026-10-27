"""002_add_updated_at_to_indicadores.

Revision ID: 48ad14f9fe02
Revises: 41855ddca8c9
Create Date: 2026-10-07 17:12:52.363360
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "48ad14f9fe02"
down_revision: Union[str, Sequence[str], None] = "41855ddca8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Añade la columna updated_at a la tabla indicadores."""
    with op.batch_alter_table("indicadores", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                nullable=True,
            )
        )


def downgrade() -> None:
    """Elimina la columna updated_at de la tabla indicadores."""
    with op.batch_alter_table("indicadores", schema=None) as batch_op:
        batch_op.drop_column("updated_at")
