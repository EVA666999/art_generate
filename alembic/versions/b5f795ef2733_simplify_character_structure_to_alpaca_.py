"""simplify_character_structure_to_alpaca_format

Revision ID: b5f795ef2733
Revises: 66e7609b7cb9
Create Date: 2025-07-31 11:52:31.024679

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5f795ef2733'
down_revision: Union[str, Sequence[str], None] = '66e7609b7cb9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema to Alpaca format."""
    # Добавляем новые столбцы Alpaca
    op.add_column('characters', sa.Column('character_card', sa.Text(), nullable=True))
    op.add_column('characters', sa.Column('instructions', sa.Text(), nullable=True))
    op.add_column('characters', sa.Column('system_prompt', sa.Text(), nullable=True))
    op.add_column('characters', sa.Column('response_format', sa.Text(), nullable=True))
    
    # Удаляем старые столбцы
    op.drop_column('characters', 'personality')
    op.drop_column('characters', 'background')
    op.drop_column('characters', 'age')
    op.drop_column('characters', 'profession')
    op.drop_column('characters', 'speaking_style')
    op.drop_column('characters', 'behavior')
    op.drop_column('characters', 'mood')
    op.drop_column('characters', 'appearance')
    op.drop_column('characters', 'voice')
    op.drop_column('characters', 'interests')
    op.drop_column('characters', 'context')
    op.drop_column('characters', 'rules')
    op.drop_column('characters', 'additional_context')
    op.drop_column('characters', 'custom_fields')


def downgrade() -> None:
    """Downgrade schema back to old format."""
    # Восстанавливаем старые столбцы
    op.add_column('characters', sa.Column('personality', sa.Text(), nullable=True))
    op.add_column('characters', sa.Column('background', sa.Text(), nullable=True))
    op.add_column('characters', sa.Column('age', sa.String(length=50), nullable=True))
    op.add_column('characters', sa.Column('profession', sa.String(length=200), nullable=True))
    op.add_column('characters', sa.Column('speaking_style', sa.Text(), nullable=True))
    op.add_column('characters', sa.Column('behavior', sa.Text(), nullable=True))
    op.add_column('characters', sa.Column('mood', sa.Text(), nullable=True))
    op.add_column('characters', sa.Column('appearance', sa.Text(), nullable=True))
    op.add_column('characters', sa.Column('voice', sa.Text(), nullable=True))
    op.add_column('characters', sa.Column('interests', sa.JSON(), nullable=True))
    op.add_column('characters', sa.Column('context', sa.Text(), nullable=True))
    op.add_column('characters', sa.Column('rules', sa.Text(), nullable=True))
    op.add_column('characters', sa.Column('additional_context', sa.JSON(), nullable=True))
    op.add_column('characters', sa.Column('custom_fields', sa.JSON(), nullable=True))
    
    # Удаляем новые столбцы Alpaca
    op.drop_column('characters', 'character_card')
    op.drop_column('characters', 'instructions')
    op.drop_column('characters', 'system_prompt')
    op.drop_column('characters', 'response_format')
