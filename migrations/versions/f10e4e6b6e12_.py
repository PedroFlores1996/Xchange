"""empty message

Revision ID: f10e4e6b6e12
Revises: 
Create Date: 2025-02-19 16:48:04.092167

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f10e4e6b6e12'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('expense',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('amount', sa.Float(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('creator_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_by_id', sa.Integer(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['creator_id'], ['user.id'], name=op.f('fk_expense_creator_id_user')),
    sa.ForeignKeyConstraint(['updated_by_id'], ['user.id'], name=op.f('fk_expense_updated_by_id_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_expense'))
    )
    op.create_table('balance',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('expense_id', sa.Integer(), nullable=False),
    sa.Column('owed_amount', sa.Float(), nullable=False),
    sa.Column('lent_amount', sa.Float(), nullable=False),
    sa.Column('total_amount', sa.Float(), nullable=False),
    sa.Column('positive', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['expense_id'], ['expense.id'], name=op.f('fk_balance_expense_id_expense')),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name=op.f('fk_balance_user_id_user')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_balance')),
    sa.UniqueConstraint('user_id', 'expense_id', 'positive', name=op.f('uq_balance_user_id'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('balance')
    op.drop_table('expense')
    # ### end Alembic commands ###
