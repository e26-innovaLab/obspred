"""merge esco json details and develop heads

Revision ID: f25a85840a80
Revises: a5ff39d5949a, b143aed3b3a9
Create Date: 2026-11-16 13:21:16.348533

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f25a85840a80'
down_revision: Union[str, Sequence[str], None] = ('a5ff39d5949a', 'b143aed3b3a9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
