"""Add versioned competency reference and revision selections; no historical backfill."""
from alembic import op
import sqlalchemy as sa

revision = "0006_competency_catalog"
down_revision = "0005_planned_sessions"
branch_labels = None
depends_on = None

def upgrade():
    if not sa.inspect(op.get_bind()).has_table('competencies'):
        op.create_table('competencies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('canonical_code', sa.String(length=20), nullable=False),
        sa.Column('competency_type', sa.String(length=30), nullable=False),
        sa.Column('canonical_label', sa.Text(), nullable=False),
        sa.Column('canonical_number', sa.Integer(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.CheckConstraint("competency_type IN ('DISCIPLINARY','TRANSDISCIPLINARY','TRANSVERSAL')", name='ck_competency_type'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('canonical_code')
        )
    if not sa.inspect(op.get_bind()).has_table('competency_contexts'):
        op.create_table('competency_contexts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('competency_id', sa.Integer(), nullable=False),
        sa.Column('curriculum_version', sa.String(length=100), nullable=False),
        sa.Column('class_level', sa.String(length=30), nullable=False),
        sa.Column('source_document_id', sa.Integer(), nullable=False),
        sa.Column('source_page', sa.String(length=40), nullable=True),
        sa.Column('source_raw_label', sa.Text(), nullable=False),
        sa.Column('normalized_display_label', sa.Text(), nullable=False),
        sa.Column('source_raw_text', sa.Text(), nullable=False),
        sa.Column('realization_context', sa.Text(), nullable=True),
        sa.Column('evaluation_context', sa.Text(), nullable=True),
        sa.Column('criteria_json', sa.Text(), nullable=True),
        sa.Column('capacities_json', sa.Text(), nullable=True),
        sa.Column('skills_json', sa.Text(), nullable=True),
        sa.Column('authority_class', sa.String(length=40), nullable=False),
        sa.Column('source_status', sa.String(length=40), nullable=False),
        sa.Column('source_issue_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['competency_id'], ['competencies.id'], ),
        sa.ForeignKeyConstraint(['source_document_id'], ['source_documents.id'], ),
        sa.ForeignKeyConstraint(['source_issue_id'], ['source_issues.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
        )
        op.create_index(op.f('ix_competency_contexts_competency_id'), 'competency_contexts', ['competency_id'], unique=False)
        op.create_index(op.f('ix_competency_contexts_class_level'), 'competency_contexts', ['class_level'], unique=False)
    if not sa.inspect(op.get_bind()).has_table('competency_applicabilities'):
        op.create_table('competency_applicabilities',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=100), nullable=False),
        sa.Column('competency_context_id', sa.Integer(), nullable=False),
        sa.Column('class_level', sa.String(length=30), nullable=False),
        sa.Column('programme_version_id', sa.Integer(), nullable=True),
        sa.Column('situation_id', sa.Integer(), nullable=True),
        sa.Column('sequence_id', sa.Integer(), nullable=True),
        sa.Column('instruction_id', sa.Integer(), nullable=True),
        sa.Column('applicability_type', sa.String(length=40), nullable=False),
        sa.Column('source_document_id', sa.Integer(), nullable=False),
        sa.Column('source_version', sa.String(length=100), nullable=False),
        sa.Column('source_page', sa.String(length=40), nullable=True),
        sa.Column('notes', sa.Text(), nullable=False),
        sa.CheckConstraint("applicability_type IN ('REQUIRED','RECOMMENDED','EXAMPLE_SELECTION','LOCAL_SELECTION','CONTEXTUAL_CANDIDATE')", name='ck_competency_applicability'),
        sa.ForeignKeyConstraint(['competency_context_id'], ['competency_contexts.id'], ),
        sa.ForeignKeyConstraint(['programme_version_id'], ['programme_versions.id'], ),
        sa.ForeignKeyConstraint(['instruction_id'], ['guide_instructions.id'], ),
        sa.ForeignKeyConstraint(['sequence_id'], ['sequences.id'], ),
        sa.ForeignKeyConstraint(['situation_id'], ['learning_situations.id'], ),
        sa.ForeignKeyConstraint(['source_document_id'], ['source_documents.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
        )
        op.create_index(op.f('ix_competency_applicabilities_competency_context_id'), 'competency_applicabilities', ['competency_context_id'], unique=False)
        op.create_index(op.f('ix_competency_applicabilities_situation_id'), 'competency_applicabilities', ['situation_id'], unique=False)
        op.create_index(op.f('ix_competency_applicabilities_instruction_id'), 'competency_applicabilities', ['instruction_id'], unique=False)
        op.create_index(op.f('ix_competency_applicabilities_sequence_id'), 'competency_applicabilities', ['sequence_id'], unique=False)
        op.create_index('ix_competency_applicabilities_programme_version_id', 'competency_applicabilities', ['programme_version_id'], unique=False)
    if not sa.inspect(op.get_bind()).has_table('teacher_sheet_competency_selections'):
        op.create_table('teacher_sheet_competency_selections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('teacher_revision_id', sa.Integer(), nullable=False),
        sa.Column('competency_id', sa.Integer(), nullable=False),
        sa.Column('competency_context_id', sa.Integer(), nullable=True),
        sa.Column('applicability_id', sa.Integer(), nullable=True),
        sa.Column('selection_origin', sa.String(length=40), nullable=False),
        sa.Column('selected_order', sa.Integer(), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=True),
        sa.Column('snapshot_json', sa.Text(), nullable=False),
        sa.CheckConstraint("selection_origin IN ('OFFICIAL_CONTEXT','GUIDE_EXAMPLE','INSPECTOR_VALIDATED','AUTO_SELECTED','TEACHER_SELECTED')", name='ck_competency_origin'),
        sa.CheckConstraint('selected_order >= 0', name='ck_competency_order'),
        sa.ForeignKeyConstraint(['applicability_id'], ['competency_applicabilities.id'], ),
        sa.ForeignKeyConstraint(['competency_context_id'], ['competency_contexts.id'], ),
        sa.ForeignKeyConstraint(['competency_id'], ['competencies.id'], ),
        sa.ForeignKeyConstraint(['teacher_revision_id'], ['teacher_sheet_revisions.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('teacher_revision_id', 'competency_id'),
        sa.UniqueConstraint('teacher_revision_id', 'selected_order')
        )
        op.create_index(op.f('ix_teacher_sheet_competency_selections_teacher_revision_id'), 'teacher_sheet_competency_selections', ['teacher_revision_id'], unique=False)

def downgrade():
    raise RuntimeError("Historical selections must be preserved; downgrade requires separate review.")
