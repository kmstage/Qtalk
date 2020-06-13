"""empty message

Revision ID: 90698c8b54df
Revises: c7d0c5a891e0
Create Date: 2020-06-11 19:17:48.018388

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '90698c8b54df'
down_revision = 'c7d0c5a891e0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('post_like',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('post_like')
    # ### end Alembic commands ###
