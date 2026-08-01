"""Updated transaction model

Revision ID: 6dd98849b0a1
Revises: 3ccb04462077
Create Date: 2026-07-24 20:19:36.437574

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "6dd98849b0a1"
down_revision = "3ccb04462077"
branch_labels = None
depends_on = None



def upgrade():

    with op.batch_alter_table(
        "transaction",
        schema=None
    ) as batch_op:


        batch_op.add_column(
            sa.Column(
                "transaction_reference",
                sa.String(length=50),
                nullable=False
            )
        )


        batch_op.add_column(
            sa.Column(
                "balance_after",
                sa.Float(),
                nullable=False
            )
        )


        batch_op.add_column(
            sa.Column(
                "created_by",
                sa.String(length=100),
                nullable=True
            )
        )


        batch_op.alter_column(
            "description",
            existing_type=sa.VARCHAR(length=100),
            type_=sa.String(length=150),
            nullable=False
        )


        batch_op.alter_column(
            "amount",
            existing_type=sa.FLOAT(),
            nullable=False
        )


        batch_op.alter_column(
            "transaction_type",
            existing_type=sa.VARCHAR(length=20),
            type_=sa.String(length=30),
            nullable=False
        )


        batch_op.create_unique_constraint(
            "uq_transaction_reference",
            ["transaction_reference"]
        )





def downgrade():

    with op.batch_alter_table(
        "transaction",
        schema=None
    ) as batch_op:


        batch_op.drop_constraint(
            "uq_transaction_reference",
            type_="unique"
        )


        batch_op.alter_column(
            "transaction_type",
            existing_type=sa.String(length=30),
            type_=sa.VARCHAR(length=20),
            nullable=True
        )


        batch_op.alter_column(
            "amount",
            existing_type=sa.FLOAT(),
            nullable=True
        )


        batch_op.alter_column(
            "description",
            existing_type=sa.String(length=150),
            type_=sa.VARCHAR(length=100),
            nullable=True
        )


        batch_op.drop_column(
            "created_by"
        )


        batch_op.drop_column(
            "balance_after"
        )


        batch_op.drop_column(
            "transaction_reference"
        )