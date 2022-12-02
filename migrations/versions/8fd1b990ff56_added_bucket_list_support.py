"""Added bucket list support

Revision ID: 8fd1b990ff56
Revises: d740ee7dd038
Create Date: 2022-12-02 16:15:24.590712

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8fd1b990ff56'
down_revision = 'd740ee7dd038'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('post_followers',
    sa.Column('post_follower_id', sa.Integer(), nullable=True),
    sa.Column('followed_post_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['followed_post_id'], ['post.id'], ),
    sa.ForeignKeyConstraint(['post_follower_id'], ['user.id'], )
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('post_followers')
    # ### end Alembic commands ###
