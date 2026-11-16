"""merge brechas and trimestre heads

Revision ID: a5ff39d5949a
Revises: 2cedef4ea4e2, 736f38c2f2cf
Create Date: 2026-11-16 12:59:28.002355

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5ff39d5949a'
down_revision: Union[str, Sequence[str], None] = ('2cedef4ea4e2', '736f38c2f2cf')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
