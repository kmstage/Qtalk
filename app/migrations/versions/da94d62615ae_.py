"""empty message

Revision ID: da94d62615ae
Revises: 
Create Date: 2020-07-06 23:02:41.173007

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'da94d62615ae'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_foreign_key(None, 'comment', 'user', ['user_id'], ['id'])
    op.drop_column('comment', 'user_name')
    op.drop_column('comment', 'image_file')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comment', sa.Column('image_file', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=20), nullable=False))
    op.add_column('comment', sa.Column('user_name', mysql.VARCHAR(collation='utf8mb4_unicode_ci', length=20), nullable=False))
    op.drop_constraint(None, 'comment', type_='foreignkey')
    # ### end Alembic commands ###
