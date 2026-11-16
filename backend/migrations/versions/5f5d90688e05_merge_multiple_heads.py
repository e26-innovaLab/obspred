"""merge multiple heads

Revision ID: 5f5d90688e05
Revises: 367806ca3627, 736f38c2f2cf
Create Date: 2026-11-02 14:54:30.903272

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5f5d90688e05'
down_revision: Union[str, Sequence[str], None] = ('367806ca3627', '736f38c2f2cf')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
