"""Add scoped curriculum attributes and immutable authoring provenance."""
from alembic import op
import sqlalchemy as sa

revision = "0004_curriculum_authoring"
down_revision = "0003_final_document_editor"
branch_labels = None
depends_on = None


def upgrade():
    # Historical 0001 creates live metadata on empty installations. Existing
    # databases at 0003 still need these additive changes, without any reset.
    inspector = sa.inspect(op.get_bind())
    for table, column in [("teacher_sheet_revisions", "authoring_json"), ("pedagogical_resource_versions", "provenance_json")]:
        if column not in {c["name"] for c in inspector.get_columns(table)}:
            op.add_column(table, sa.Column(column, sa.Text(), nullable=False, server_default="{}"))
    if inspector.has_table("curriculum_attributes"):
        return
    op.create_table(
        "curriculum_attributes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(100), nullable=False, unique=True),
        sa.Column("programme_version_id", sa.Integer(), sa.ForeignKey("programme_versions.id"), nullable=False),
        sa.Column("scope", sa.String(30), nullable=False),
        sa.Column("scope_id", sa.Integer(), nullable=False),
        sa.Column("field", sa.String(100), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column("source_document_id", sa.Integer(), sa.ForeignKey("source_documents.id"), nullable=False),
        sa.Column("source_version", sa.String(100), nullable=False),
        sa.Column("page_label", sa.String(50), nullable=False),
        sa.CheckConstraint("scope IN ('CLASS', 'SA', 'SEQUENCE', 'INSTRUCTION')", name="ck_attribute_scope"),
    )


def downgrade():
    op.drop_table("curriculum_attributes")
    op.drop_column("pedagogical_resource_versions", "provenance_json")
    op.drop_column("teacher_sheet_revisions", "authoring_json")
