"""Add active flag to yara_rule

Revision ID: 8a40de624788
Revises: 15b203983adb
Create Date: 2017-09-10 12:39:39.512733

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '8a40de624788'
down_revision = '15b203983adb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('yara_rules', sa.Column('active', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('yara_rules', 'active')
    # ### end Alembic commands ###
