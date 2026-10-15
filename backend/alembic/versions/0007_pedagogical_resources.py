"""Extend the resource library and add revision-owned homework/documents."""
from alembic import op
import sqlalchemy as sa

revision = "0007_pedagogical_resources"
down_revision = "0006_competency_catalog"
branch_labels = None
depends_on = None


def _column_names(bind, table):
    return {column["name"] for column in sa.inspect(bind).get_columns(table)}


def upgrade():
    bind = op.get_bind()
    existing = _column_names(bind, "pedagogical_resources")
    additions = [
        sa.Column("content", sa.Text(), nullable=False, server_default=""),
        sa.Column("content_format", sa.String(20), nullable=False, server_default="LATEX"),
        sa.Column("programme_version_id", sa.Integer(), sa.ForeignKey("programme_versions.id", name="fk_resource_programme_version"), nullable=True),
        sa.Column("situation_id", sa.Integer(), sa.ForeignKey("learning_situations.id", name="fk_resource_situation"), nullable=True),
        sa.Column("sequence_id", sa.Integer(), sa.ForeignKey("sequences.id", name="fk_resource_sequence"), nullable=True),
        sa.Column("primary_instruction_id", sa.Integer(), sa.ForeignKey("guide_instructions.id", name="fk_resource_primary_instruction"), nullable=True),
        sa.Column("source_document_id", sa.Integer(), sa.ForeignKey("source_documents.id", name="fk_resource_source_document"), nullable=True),
        sa.Column("source_page", sa.String(50), nullable=True),
        sa.Column("origin_type", sa.String(40), nullable=False, server_default="CURATED_PROJECT"),
        sa.Column("validation_status", sa.String(30), nullable=False, server_default="CURATED"),
        sa.Column("visibility_scope", sa.String(30), nullable=False, server_default="CURATED_GLOBAL"),
        sa.Column("created_by", sa.String(120), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("provenance_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("content_hash", sa.String(64), nullable=False, server_default=""),
    ]
    missing_additions = [column for column in additions if column.name not in existing]
    if missing_additions:
        if bind.dialect.name == "sqlite":
            # SQLite cannot attach foreign-key constraints with ALTER TABLE.
            # Batch mode rebuilds the historical 0006 table once and preserves
            # its rows while creating the five P3 foreign keys.
            with op.batch_alter_table("pedagogical_resources", recreate="always") as batch_op:
                for column in missing_additions:
                    batch_op.add_column(column)
        else:
            for column in missing_additions:
                op.add_column("pedagogical_resources", column)

    mapping_columns = _column_names(bind, "resource_instruction_mappings")
    for column in (
        sa.Column("relevance", sa.String(30), nullable=False, server_default="DIRECT"),
        sa.Column("created_by", sa.String(120), nullable=True),
        sa.Column("provenance_json", sa.Text(), nullable=False, server_default="{}"),
    ):
        if column.name not in mapping_columns:
            op.add_column("resource_instruction_mappings", column)
    if "snapshot_json" not in _column_names(bind, "sheet_resource_instances"):
        op.add_column("sheet_resource_instances", sa.Column("snapshot_json", sa.Text(), nullable=False, server_default="{}"))

    if not sa.inspect(bind).has_table("teacher_sheet_homework_selections"):
        op.create_table("teacher_sheet_homework_selections",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("teacher_revision_id", sa.Integer(), sa.ForeignKey("teacher_sheet_revisions.id"), nullable=False),
            sa.Column("pedagogical_resource_id", sa.Integer(), sa.ForeignKey("pedagogical_resources.id"), nullable=False),
            sa.Column("resource_version_id", sa.Integer(), sa.ForeignKey("pedagogical_resource_versions.id"), nullable=False),
            sa.Column("homework_usage_type", sa.String(40), nullable=False),
            sa.Column("selected_order", sa.Integer(), nullable=False),
            sa.Column("teacher_note", sa.Text(), nullable=True),
            sa.Column("snapshot_json", sa.Text(), nullable=False),
            sa.Column("selected_at", sa.DateTime(), nullable=False),
            sa.CheckConstraint("homework_usage_type IN ('CURRENT_SCOPE','PRIOR_NOTION_REACTIVATION')", name="ck_homework_usage"),
            sa.UniqueConstraint("teacher_revision_id", "selected_order"),
            sa.UniqueConstraint("teacher_revision_id", "pedagogical_resource_id"),
        )
        op.create_index("ix_homework_revision", "teacher_sheet_homework_selections", ["teacher_revision_id"])
    if not sa.inspect(bind).has_table("teacher_sheet_document_references"):
        op.create_table("teacher_sheet_document_references",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("teacher_revision_id", sa.Integer(), sa.ForeignKey("teacher_sheet_revisions.id"), nullable=False),
            sa.Column("origin", sa.String(30), nullable=False),
            sa.Column("source_document_id", sa.Integer(), sa.ForeignKey("source_documents.id"), nullable=True),
            sa.Column("source_version", sa.String(100), nullable=True),
            sa.Column("display_label", sa.String(255), nullable=False),
            sa.Column("author", sa.String(255), nullable=True),
            sa.Column("title", sa.String(255), nullable=True),
            sa.Column("edition", sa.String(120), nullable=True),
            sa.Column("note", sa.Text(), nullable=True),
            sa.Column("selected_order", sa.Integer(), nullable=False),
            sa.Column("snapshot_json", sa.Text(), nullable=False, server_default="{}"),
            sa.CheckConstraint("origin IN ('AUTO_DERIVED','MANUAL_REFERENCE')", name="ck_document_origin"),
            sa.UniqueConstraint("teacher_revision_id", "selected_order"),
        )
        op.create_index("ix_documents_revision", "teacher_sheet_document_references", ["teacher_revision_id"])
    if not sa.inspect(bind).has_table("package_import_records"):
        op.create_table("package_import_records",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("package_version", sa.String(80), nullable=False),
            sa.Column("schema_version", sa.String(20), nullable=False),
            sa.Column("manifest_hash", sa.String(64), nullable=False, unique=True),
            sa.Column("imported_at", sa.DateTime(), nullable=False),
            sa.Column("imported_by", sa.String(120), nullable=False),
            sa.Column("resource_count", sa.Integer(), nullable=False),
            sa.Column("source_count", sa.Integer(), nullable=False),
            sa.Column("link_count", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(30), nullable=False),
            sa.Column("report_json", sa.Text(), nullable=False),
        )


def downgrade():
    raise RuntimeError("Resource snapshots and package audit records must be preserved.")
