"""remove_character_card_column

Revision ID: ae4bf9509a19
Revises: 4e84f6c9a28f
Create Date: 2025-08-10 02:19:44.351326

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ae4bf9509a19'
down_revision: Union[str, Sequence[str], None] = '4e84f6c9a28f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Удаляем столбец character_card из таблицы characters
    op.drop_column('characters', 'character_card')


def downgrade() -> None:
    """Downgrade schema."""
    # Восстанавливаем столбец character_card в таблице characters
    op.add_column('characters', sa.Column('character_card', sa.Text(), nullable=True))
