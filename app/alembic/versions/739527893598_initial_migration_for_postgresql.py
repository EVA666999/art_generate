"""Initial migration for PostgreSQL

Revision ID: 739527893598
Revises: 
Create Date: 2025-07-12 19:38:47.012456

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '739527893598'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('characters',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('personality', sa.String(length=500), nullable=False),
    sa.Column('background', sa.String(length=1000), nullable=True),
    sa.Column('speaking_style', sa.String(length=200), nullable=True),
        sa.Column('interests', sa.JSON(), nullable=True),
    sa.Column('mood', sa.String(length=100), nullable=True),
        sa.Column('additional_context', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), 
                  server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('age', sa.String(length=50), nullable=True),
    sa.Column('profession', sa.String(length=200), nullable=True),
    sa.Column('behavior', sa.Text(), nullable=True),
    sa.Column('appearance', sa.Text(), nullable=True),
    sa.Column('voice', sa.String(length=200), nullable=True),
    sa.Column('rules', sa.Text(), nullable=True),
    sa.Column('context', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_characters_id'), 'characters', ['id'], unique=False)
    op.create_index(op.f('ix_characters_name'), 'characters', ['name'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('last_name', sa.String(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('is_superuser', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('username')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('users')
    op.drop_index(op.f('ix_characters_name'), table_name='characters')
    op.drop_index(op.f('ix_characters_id'), table_name='characters')
    op.drop_table('characters')
    # ### end Alembic commands ###
