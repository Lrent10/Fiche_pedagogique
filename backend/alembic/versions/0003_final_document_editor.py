"""Final document editor visibility.

Revision ID: 0003_final_document_editor
Revises: 0002_v2_document_workflow
"""

from alembic import op
import sqlalchemy as sa


revision = "0003_final_document_editor"
down_revision = "0002_v2_document_workflow"
branch_labels = None
depends_on = None


def upgrade():
    # Empty installations already receive this column from historical 0001.
    if "visible" not in {c["name"] for c in sa.inspect(op.get_bind()).get_columns("sheet_block_instances")}:
        op.add_column("sheet_block_instances", sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade():
    with op.batch_alter_table("sheet_block_instances") as batch:
        batch.drop_column("visible")
