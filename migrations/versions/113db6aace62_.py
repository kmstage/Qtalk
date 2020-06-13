"""empty message

Revision ID: 113db6aace62
Revises: 90698c8b54df
Create Date: 2020-06-11 20:27:43.601916

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '113db6aace62'
down_revision = '90698c8b54df'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('post_dislike',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['post_id'], ['post.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_column('post', 'dislike')
    op.drop_column('post', 'like')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('post', sa.Column('like', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('post', sa.Column('dislike', mysql.INTEGER(), autoincrement=False, nullable=True))
    op.drop_table('post_dislike')
    # ### end Alembic commands ###
