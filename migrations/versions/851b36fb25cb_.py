"""empty message

Revision ID: 851b36fb25cb
Revises: 18294e934b96
Create Date: 2025-02-05 20:27:29.545216

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "851b36fb25cb"
down_revision = "18294e934b96"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "group",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_group")),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=150), nullable=False),
        sa.Column("password", sa.String(length=150), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user")),
        sa.UniqueConstraint("username", name=op.f("uq_user_username")),
    )
    op.create_table(
        "debt",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("lender_id", sa.Integer(), nullable=False),
        sa.Column("borrower_id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("group_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["borrower_id"], ["user.id"], name=op.f("fk_debt_borrower_id_user")
        ),
        sa.ForeignKeyConstraint(
            ["group_id"], ["group.id"], name=op.f("fk_debt_group_id_group")
        ),
        sa.ForeignKeyConstraint(
            ["lender_id"], ["user.id"], name=op.f("fk_debt_lender_id_user")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_debt")),
        sa.UniqueConstraint(
            "lender_id", "borrower_id", "group_id", name=op.f("uq_debt_lender_id")
        ),
    )
    op.create_table(
        "group_members",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("group_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["group_id"], ["group.id"], name=op.f("fk_group_members_group_id_group")
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], name=op.f("fk_group_members_user_id_user")
        ),
        sa.PrimaryKeyConstraint("user_id", "group_id", name=op.f("pk_group_members")),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("group_members")
    op.drop_table("debt")
    op.drop_table("user")
    op.drop_table("group")
    # ### end Alembic commands ###
