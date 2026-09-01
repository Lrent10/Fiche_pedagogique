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
    with op.batch_alter_table("sheet_block_instances") as batch:
        batch.add_column(sa.Column("visible", sa.Boolean(), nullable=False, server_default=sa.true()))


def downgrade():
    with op.batch_alter_table("sheet_block_instances") as batch:
        batch.drop_column("visible")
