"""New fields added in User model

Revision ID: 83c229e6715d
Revises: e09c739c43b0
Create Date: 2022-11-27 17:17:03.769777

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '83c229e6715d'
down_revision = 'e09c739c43b0'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('caption', sa.String(length=256), nullable=True))
        batch_op.add_column(sa.Column('lastSeen', sa.DateTime(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('lastSeen')
        batch_op.drop_column('caption')

    # ### end Alembic commands ###
