"""USERS - Autoincrement set to PK

Revision ID: d385c3eb6937
Revises: ee2cbe4166fb
Create Date: 2018-02-16 11:23:29.705565

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd385c3eb6937'
down_revision = 'ee2cbe4166fb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('name', sa.String(length=20), nullable=True))
    op.add_column('user', sa.Column('surname', sa.String(length=20), nullable=True))
    op.create_index(op.f('ix_user_surname'), 'user', ['surname'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_user_surname'), table_name='user')
    op.drop_column('user', 'surname')
    op.drop_column('user', 'name')
    # ### end Alembic commands ###
