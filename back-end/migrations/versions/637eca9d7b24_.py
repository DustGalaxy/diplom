"""empty message

Revision ID: 637eca9d7b24
Revises: 251ae6c1b2fb
Create Date: 2025-05-28 19:21:05.547020

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '637eca9d7b24'
down_revision: Union[str, None] = '251ae6c1b2fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_history_stat',
    sa.Column('user_id', sa.UUID(), nullable=False),
    sa.Column('yt_id', sa.String(length=25), nullable=False),
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['yt_id'], ['tracks.yt_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_history_stat_id'), 'user_history_stat', ['id'], unique=True)
    op.create_index(op.f('ix_user_history_stat_updated_at'), 'user_history_stat', ['updated_at'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_history_stat_updated_at'), table_name='user_history_stat')
    op.drop_index(op.f('ix_user_history_stat_id'), table_name='user_history_stat')
    op.drop_table('user_history_stat')
    # ### end Alembic commands ###
