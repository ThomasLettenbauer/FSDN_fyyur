"""empty message

Revision ID: 851f6717b627
Revises: 0fde8d01bc19
Create Date: 2020-04-29 08:23:26.485515

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '851f6717b627'
down_revision = '0fde8d01bc19'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('artist', sa.Column('genres', sa.ARRAY(sa.String(length=120)), nullable=True))
    op.add_column('venue', sa.Column('genres', sa.ARRAY(sa.String(length=120)), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'genres')
    op.drop_column('artist', 'genres')
    # ### end Alembic commands ###