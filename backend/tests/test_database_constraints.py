import pytest
from sqlalchemy.exc import IntegrityError

from app import models as m
from app.database import SessionLocal


def test_sheet_resource_origin_source_xor():
    with SessionLocal() as db:
        revision = db.query(m.TeacherSheetRevision).first()
        invalid = m.SheetResourceInstance(
            teacher_revision_id=revision.id,
            origin="LOCAL_ORIGINAL",
            source_resource_version_id=db.query(m.PedagogicalResourceVersion).first().id,
            title="Invalide",
            position=99,
        )
        db.add(invalid)
        with pytest.raises(IntegrityError):
            db.commit()


def test_export_family_revision_xor():
    with SessionLocal() as db:
        teacher = db.query(m.TeacherSheetRevision).first()
        support = db.query(m.LearnerSupportRevision).first()
        invalid = m.DocumentExport(
            document_family="TEACHER",
            teacher_revision_id=teacher.id,
            support_revision_id=support.id,
            file_path="invalid.pdf",
        )
        db.add(invalid)
        with pytest.raises(IntegrityError):
            db.commit()


def test_support_scope_is_exactly_sequence_or_sa():
    with SessionLocal() as db:
        invalid = m.LearnerSupport(code="INVALID-SCOPE", title="Invalide", sequence_id=None, situation_id=None)
        db.add(invalid)
        with pytest.raises(IntegrityError):
            db.commit()


def test_only_one_block_variant_per_target():
    with SessionLocal() as db:
        block = db.query(m.PedagogicalBlock).first()
        db.add(m.BlockVariant(block_id=block.id, target="CUSTOM", label="A", content_latex="A"))
        db.commit()
        db.add(m.BlockVariant(block_id=block.id, target="CUSTOM", label="B", content_latex="B"))
        with pytest.raises(IntegrityError):
            db.commit()


def test_database_guard_blocks_direct_finalized_snapshot_edit():
    with SessionLocal() as db:
        revision = db.query(m.TeacherSheetRevision).filter(m.TeacherSheetRevision.status == "FINALIZED").first()
        resource = db.query(m.SheetResourceInstance).filter(m.SheetResourceInstance.teacher_revision_id == revision.id).first()
        block = db.query(m.SheetBlockInstance).filter(m.SheetBlockInstance.resource_instance_id == resource.id).first()
        block.content_latex = "MODIFICATION INTERDITE"
        with pytest.raises(ValueError, match="immuable"):
            db.commit()
