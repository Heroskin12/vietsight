"""Added columns for profile and cover pics.

Revision ID: e49443b3c151
Revises: bc2ca07685a2
Create Date: 2022-11-29 18:26:33.871832

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e49443b3c151'
down_revision = 'bc2ca07685a2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.drop_column('place_type')

    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('profile_pic', sa.String(), nullable=True))
        batch_op.add_column(sa.Column('cover_pic', sa.String(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('cover_pic')
        batch_op.drop_column('profile_pic')

    with op.batch_alter_table('post', schema=None) as batch_op:
        batch_op.add_column(sa.Column('place_type', sa.VARCHAR(), nullable=True))

    # ### end Alembic commands ###