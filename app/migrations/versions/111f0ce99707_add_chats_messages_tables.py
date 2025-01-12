"""add chats, messages tables

Revision ID: 111f0ce99707
Revises: 
Create Date: 2025-01-05 23:21:04.702843

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '111f0ce99707'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('telegram_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('age', sa.Integer(), nullable=True),
    sa.Column('sex', sa.Enum('male', 'female', name='usersexenum'), nullable=True),
    sa.Column('bio', sa.String(), nullable=True),
    sa.Column('photo_url', sa.String(), nullable=True),
    sa.Column('interests', sa.JSON(), nullable=True),
    sa.Column('city', sa.String(), nullable=True),
    sa.Column('zodiac', sa.Enum('aries', 'taurus', 'gemini', 'cancer', 'leo', 'virgo', 'libra', 'scorpio', 'sagittarius', 'capricorn', 'aquarius', 'pisces', name='zodiacenum'), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('likes',
    sa.Column('like_id', sa.Uuid(), nullable=False),
    sa.Column('user_id', sa.Uuid(), nullable=False),
    sa.Column('liked_user_id', sa.Uuid(), nullable=False),
    sa.Column('status', sa.Enum('new', 'seen', 'match', name='likestatusenum'), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
    sa.ForeignKeyConstraint(['liked_user_id'], ['users.user_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('like_id'),
    sa.UniqueConstraint('user_id', 'liked_user_id', name='_user_liked_user_uc')
    )
    op.create_table('matches',
    sa.Column('match_id', sa.Uuid(), nullable=False),
    sa.Column('user1_id', sa.Uuid(), nullable=False),
    sa.Column('user2_id', sa.Uuid(), nullable=False),
    sa.Column('status', sa.Enum('new', 'seen', 'deleted', name='matchstatusenum'), nullable=False),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()'), nullable=False),
    sa.ForeignKeyConstraint(['user1_id'], ['users.user_id'], ),
    sa.ForeignKeyConstraint(['user2_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('match_id'),
    sa.UniqueConstraint('user1_id', 'user2_id', name='uq_user_pair'),
    sa.UniqueConstraint('user2_id', 'user1_id', name='uq_user_pair_reversed')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('matches')
    op.drop_table('likes')
    op.drop_table('users')
    # ### end Alembic commands ###
