"""Add contextual planned sessions without assigning historical executions."""
from alembic import op
import sqlalchemy as sa

revision = "0005_planned_sessions"
down_revision = "0004_curriculum_authoring"
branch_labels = None
depends_on = None


def upgrade():
    inspector = sa.inspect(op.get_bind())
    # 0001 uses live metadata on empty installs; also support genuine 0004 DBs.
    if not inspector.has_table("class_contexts"):
        op.create_table("class_contexts",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("class_level", sa.String(30), nullable=False),
            sa.Column("class_label", sa.String(80), nullable=False),
            sa.Column("school_year", sa.String(9), nullable=False),
            sa.Column("teacher_actual_weekly_minutes", sa.Integer(), nullable=True),
            sa.UniqueConstraint("class_level", "class_label", "school_year"),
            sa.CheckConstraint("teacher_actual_weekly_minutes IS NULL OR teacher_actual_weekly_minutes > 0", name="ck_context_weekly_minutes"))
    if not inspector.has_table("sequence_plans"):
        op.create_table("sequence_plans",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("class_context_id", sa.Integer(), sa.ForeignKey("class_contexts.id"), nullable=False),
            sa.Column("sequence_id", sa.Integer(), sa.ForeignKey("sequences.id"), nullable=False),
            sa.Column("planned_sequence_minutes", sa.Integer(), nullable=True),
            sa.UniqueConstraint("class_context_id", "sequence_id"),
            sa.CheckConstraint("planned_sequence_minutes IS NULL OR planned_sequence_minutes > 0", name="ck_sequence_minutes"))
    if not inspector.has_table("planned_sessions"):
        op.create_table("planned_sessions",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("sequence_plan_id", sa.Integer(), sa.ForeignKey("sequence_plans.id"), nullable=False),
            sa.Column("session_number_within_sequence", sa.Integer(), nullable=False),
            sa.Column("sheet_id", sa.Integer(), sa.ForeignKey("teacher_session_sheets.id"), nullable=False, unique=True),
            sa.UniqueConstraint("sequence_plan_id", "session_number_within_sequence"),
            sa.CheckConstraint("session_number_within_sequence >= 1", name="ck_session_number"))
    if "planned_session_id" not in {c["name"] for c in inspector.get_columns("teaching_sessions")}:
        # Nullable REFERENCES is additive on SQLite; no table copy or backfill.
        if op.get_bind().dialect.name == "sqlite":
            op.execute("ALTER TABLE teaching_sessions ADD COLUMN planned_session_id INTEGER REFERENCES planned_sessions(id)")
        else:
            op.add_column("teaching_sessions", sa.Column("planned_session_id", sa.Integer(), nullable=True))
            op.create_foreign_key("fk_teaching_planned", "teaching_sessions", "planned_sessions", ["planned_session_id"], ["id"])
    if "ix_teaching_sessions_planned_session_id" not in {i["name"] for i in sa.inspect(op.get_bind()).get_indexes("teaching_sessions")}:
        op.create_index("ix_teaching_sessions_planned_session_id", "teaching_sessions", ["planned_session_id"])


def downgrade():
    raise RuntimeError("P1 preserves history; downgrade requires a separately reviewed procedure.")
