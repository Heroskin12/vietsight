"""New Columns in Post table

Revision ID: bc2ca07685a2
Revises: 83c229e6715d
Create Date: 2022-11-28 16:27:35.313638

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc2ca07685a2'
down_revision = '83c229e6715d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('location', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('directions', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('place_type', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('comments', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('comments')
        batch_op.drop_column('place_type')
        batch_op.drop_column('directions')
        batch_op.drop_column('location')
        batch_op.drop_column('image')

    # ### end Alembic commands ###
