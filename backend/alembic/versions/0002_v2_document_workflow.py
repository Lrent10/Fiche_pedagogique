"""V2 document fidelity and support-first workflow.

Revision ID: 0002_v2_document_workflow
Revises: 0001_initial
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_v2_document_workflow"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("flow_items") as batch:
        batch.add_column(sa.Column("expected_result_latex", sa.Text(), nullable=False, server_default=""))
    with op.batch_alter_table("support_uses") as batch:
        batch.add_column(sa.Column("teacher_revision_id", sa.Integer(), nullable=True))
        batch.add_column(sa.Column("selected_block_ids_json", sa.Text(), nullable=False, server_default="[]"))
        batch.create_foreign_key(
            "fk_support_use_teacher_revision",
            "teacher_sheet_revisions",
            ["teacher_revision_id"],
            ["id"],
        )


def downgrade():
    with op.batch_alter_table("support_uses") as batch:
        batch.drop_constraint("fk_support_use_teacher_revision", type_="foreignkey")
        batch.drop_column("selected_block_ids_json")
        batch.drop_column("teacher_revision_id")
    with op.batch_alter_table("flow_items") as batch:
        batch.drop_column("expected_result_latex")
