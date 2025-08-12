"""create alpaca schema

Revision ID: 8419c5ef0121
Revises: b5f795ef2733
Create Date: 2025-07-31 12:07:45.444

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8419c5ef0121'
down_revision = 'b5f795ef2733'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create Alpaca schema with only 4 columns."""
    # Добавляем новые столбцы Alpaca как nullable=True
    op.add_column('characters', sa.Column('character_card', sa.Text(), 
                                        nullable=True))
    op.add_column('characters', sa.Column('instructions', sa.Text(), 
                                        nullable=True))
    op.add_column('characters', sa.Column('system_prompt', sa.Text(), 
                                        nullable=True))
    op.add_column('characters', sa.Column('response_format', sa.Text(), 
                                        nullable=True))
    
    # Удаляем все старые столбцы
    columns_to_drop = [
        'personality', 'background', 'speaking_style', 'interests', 
        'mood', 'additional_context', 'age', 'profession', 'behavior',
        'appearance', 'voice', 'rules', 'context', 'character_type',
        'tags', 'rating', 'language', 'max_tokens'
    ]
    
    for column in columns_to_drop:
        op.drop_column('characters', column)


def downgrade() -> None:
    """Restore old schema."""
    # Восстанавливаем старые столбцы
    op.add_column('characters', sa.Column('personality', sa.Text(), 
                                        nullable=True))
    op.add_column('characters', sa.Column('background', sa.Text(), 
                                        nullable=True))
    op.add_column('characters', sa.Column('speaking_style', sa.Text(), 
                                        nullable=True))
    op.add_column('characters', sa.Column('interests', sa.Text(), 
                                        nullable=True))
    op.add_column('characters', sa.Column('mood', sa.Text(), 
                                        nullable=True))
    op.add_column('characters', sa.Column('additional_context', sa.Text(), 
                                        nullable=True))
    op.add_column('characters', sa.Column('age', sa.Integer(), 
                                        nullable=True))
    op.add_column('characters', sa.Column('profession', sa.String(100), 
                                        nullable=True))
    op.add_column('characters', sa.Column('behavior', sa.Text(), 
                                        nullable=True))
    op.add_column('characters', sa.Column('appearance', sa.Text(), 
                                        nullable=True))
    op.add_column('characters', sa.Column('voice', sa.Text(), 
                                        nullable=True))
    op.add_column('characters', sa.Column('rules', sa.Text(), 
                                        nullable=True))
    op.add_column('characters', sa.Column('context', sa.Text(), 
                                        nullable=True))
    op.add_column('characters', sa.Column('character_type', sa.String(50), 
                                        nullable=True))
    op.add_column('characters', sa.Column('tags', sa.JSON(), 
                                        nullable=True))
    op.add_column('characters', sa.Column('rating', sa.String(20), 
                                        nullable=True))
    op.add_column('characters', sa.Column('language', sa.String(10), 
                                        nullable=True))
    op.add_column('characters', sa.Column('max_tokens', sa.Integer(), 
                                        nullable=True))
    
    # Удаляем новые столбцы Alpaca
    op.drop_column('characters', 'character_card')
    op.drop_column('characters', 'instructions')
    op.drop_column('characters', 'system_prompt')
    op.drop_column('characters', 'response_format')
