from __future__ import annotations

import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models as m


def add_resource(
    db: Session,
    *,
    code: str,
    title: str,
    resource_type: str,
    provenance_kind: str,
    summary: str,
    minutes: int,
    blocks: list[tuple[str, str, str]],
    instruction_ids: list[int],
    validation_status: str,
) -> m.PedagogicalResourceVersion:
    resource = m.PedagogicalResource(
        code=code,
        title=title,
        resource_type=resource_type,
        provenance_kind=provenance_kind,
        structure_kind="COMPOSITE" if len(blocks) > 1 else "ATOMIC",
    )
    db.add(resource)
    db.flush()
    version = m.PedagogicalResourceVersion(
        resource_id=resource.id,
        version_number=1,
        title=title,
        summary=summary,
        estimated_minutes=minutes,
        transcription_status="CONFIRMED" if provenance_kind == "SOURCED" else "DEMO",
        mathematical_status="TO_REVIEW",
        pedagogical_status="TO_REVIEW",
        source_completeness_status="PARTIAL" if provenance_kind == "SOURCED" else "NOT_APPLICABLE",
        source_consistency_status="ISSUE_RECORDED" if provenance_kind == "SOURCED" else "NOT_APPLICABLE",
    )
    db.add(version)
    db.flush()
    for position, (block_type, block_title, content) in enumerate(blocks, 1):
        db.add(
            m.PedagogicalBlock(
                resource_version_id=version.id,
                block_type=block_type,
                title=block_title,
                content_latex=content,
                position=position,
            )
        )
    for instruction_id in instruction_ids:
        db.add(
            m.ResourceInstructionMapping(
                resource_version_id=version.id,
                instruction_id=instruction_id,
                validation_status=validation_status,
            )
        )
    return version


def seed_database(db: Session) -> bool:
    if db.scalar(select(m.ProgrammeVersion.id).limit(1)):
        return False

    programme = m.ProgrammeVersion(
        code="PRG-4E-BJ",
        title="Programme d'études de mathématiques — classe de quatrième",
    )
    guide = m.GuideVersion(
        code="GUIDE-4E-BJ",
        title="Guide de l'enseignant — Mathématiques 4e",
    )
    db.add_all([programme, guide])
    db.flush()

    source_programme = m.SourceDocument(
        code="SRC-PRG-4E",
        title=programme.title,
        document_type="PROGRAMME",
        file_name="930040566-programme-4ieme-Maths-certifie.pdf",
        sha256="7795DD2370DB4C879187F5FCBC7247BABCAB2AB0A3FD9D9F579663D0114FD62D",
        authority="Document pédagogique fourni par l'utilisateur",
    )
    source_guide = m.SourceDocument(
        code="SRC-GUIDE-4E",
        title=guide.title,
        document_type="GUIDE",
        file_name="783063322-GUIDE-4eme-Maths-Certifie-Vu.pdf",
        sha256="A6E937B03DA51229E3C23D16A7105CAA4338BC29B4853B27374A1977E4BFAB93",
        authority="Document pédagogique fourni par l'utilisateur",
    )
    db.add_all([source_programme, source_guide])
    db.flush()

    situation = m.SituationApprentissage(
        programme_version_id=programme.id,
        code="SA1",
        title="Configurations du plan",
        position=1,
    )
    db.add(situation)
    db.flush()
    sequence = m.Sequence(
        situation_id=situation.id,
        guide_version_id=guide.id,
        code="SEQ8",
        title="Calculs sur les expressions algébriques",
        position=8,
    )
    db.add(sequence)
    db.flush()

    knowledge_labels = [
        "Somme et produit d'expressions algébriques",
        "Factorisation par mise en évidence",
        "Produits remarquables",
        "Développement et réduction",
        "Valeur numérique d'une expression littérale",
    ]
    for index, label in enumerate(knowledge_labels, 1):
        db.add(m.ConnaissanceTechnique(sequence_id=sequence.id, code=f"SEQ8-SAV{index}", label=label, position=index))

    instruction_texts = [
        "Reconnaître une somme et un produit.",
        "Factoriser une somme en mettant un facteur commun en évidence.",
        "Énoncer les propriétés des produits remarquables : $(a+b)^2=a^2+2ab+b^2$, $(a-b)^2=a^2-2ab+b^2$ et $(a+b)(a-b)=a^2-b^2$.",
        "Utiliser les produits remarquables pour factoriser, développer et effectuer des calculs numériques.",
        "Réduire une somme.",
        "Développer un produit.",
        "Calculer la valeur numérique d'une expression littérale en remplaçant les lettres par des nombres.",
    ]
    instructions: list[m.InstructionGuide] = []
    for index, text in enumerate(instruction_texts, 1):
        instruction = m.InstructionGuide(sequence_id=sequence.id, code=f"SEQ8-INS{index}", text=text, position=index)
        db.add(instruction)
        instructions.append(instruction)
    db.flush()

    db.add_all(
        [
            m.CurriculumTimeAllocation(
                situation_id=situation.id,
                source_document_id=source_programme.id,
                hours=56,
                note="Durée portée par le programme d'études.",
            ),
            m.CurriculumTimeAllocation(
                situation_id=situation.id,
                source_document_id=source_guide.id,
                hours=60,
                note="Durée portée par le guide de l'enseignant.",
            ),
            m.SourceIssue(
                code="F-01",
                title="Durées divergentes pour la SA1",
                description="Le programme indique 56 h tandis que le guide indique 60 h. Les deux valeurs sont conservées sans arbitrage automatique.",
                status="OPEN",
            ),
            m.SourceIssue(
                code="PILOT-OBS-01",
                title="Numérotation différente dans l'exemple de fiche",
                description="Le guide structure le contenu comme Séquence 8, alors que l'exemple de fiche imprimé le désigne Séquence N°1. L'occurrence est conservée sans changer le code canonique du guide.",
                status="OPEN",
            ),
            m.SourceIssue(code="F-02", title="Durées divergentes pour la SA2", description="Programme 4e p. 98 : 28 h ; guide 4e p. 33 : 30 h. Aucune valeur fusionnée.", status="OPEN"),
            m.SourceIssue(code="F-03", title="Durées divergentes pour la SA3", description="Programme 4e p. 108 : 20 h ; guide 4e p. 46 : 18 h. Aucune valeur fusionnée.", status="OPEN"),
            m.SourceIssue(code="F-04", title="Durées divergentes pour la SA4", description="Programme 4e p. 118 : 22 h ; guide 4e p. 56 : 24 h. Aucune valeur fusionnée.", status="OPEN"),
            m.SourceIssue(code="F-05", title="Numérotation interne contradictoire en Terminale D", description="Programme Terminale D p. 74, 79 et 81 : numérotation SA contradictoire. Constat structurel conservé, hors corpus pilote 4e.", status="OPEN"),
            m.SourceIssue(code="F-06", title="Durée interne contradictoire en Terminale D", description="Programme Terminale D p. 74 et 81 : 24 h puis 12 h pour Configurations de l'espace. Constat structurel conservé, hors corpus pilote 4e.", status="OPEN"),
            m.SourceIssue(code="F-07", title="Résultats attendus manquants dans une fiche 3e", description="Fiche 3e p. 2, 3, 38 et 55 : « Résultats attendus (à faire) ». Le résultat n'est pas inventé.", status="OPEN"),
        ]
    )

    for instruction in instructions:
        db.add(
            m.SourceOccurrence(
                source_document_id=source_guide.id,
                entity_type="InstructionGuide",
                entity_id=instruction.id,
                page_label="31-32",
                locator="Séquence 8 — Instructions",
                excerpt=instruction.text,
            )
        )
    db.add_all(
        [
            m.SourceOccurrence(
                source_document_id=source_programme.id,
                entity_type="SituationApprentissage",
                entity_id=situation.id,
                page_label="SA1",
                locator="Contenus de formation",
                excerpt="Configurations du plan ; expressions algébriques et produits remarquables.",
            ),
            m.SourceOccurrence(
                source_document_id=source_guide.id,
                entity_type="Sequence",
                entity_id=sequence.id,
                page_label="31-32",
                locator="Séquence 8",
                excerpt="Calculs sur les expressions algébriques.",
            ),
        ]
    )

    parcel = add_resource(
        db,
        code="RES-GUIDE-PARCELLE",
        title="Activité de découverte — parcelle de Fofo",
        resource_type="DISCOVERY_ACTIVITY",
        provenance_kind="SOURCED",
        summary="Modéliser l'aire d'une parcelle rectangulaire découpée afin d'établir la distributivité.",
        minutes=20,
        instruction_ids=[instructions[5].id],
        validation_status="SOURCE_CONFIRMED",
        blocks=[
            (
                "STATEMENT",
                "Situation de départ",
                r"Fofo dispose d'une parcelle rectangulaire dont les côtés sont partagés en longueurs $x$, $z$ d'une part et $y$, $b$ d'autre part. Exprimer son aire de deux façons.",
            ),
            (
                "INSTRUCTION",
                "Consigne",
                r"Calcule l'aire du grand rectangle, puis la somme des aires des quatre rectangles. Compare les résultats et complète : $(x+z)(y+b)=\ldots$",
            ),
            (
                "EXPECTED_TRACE",
                "Trace attendue",
                r"$(x+z)(y+b)=xy+xb+zy+zb$. Cette égalité illustre la distributivité de la multiplication sur l'addition.",
            ),
        ],
    )
    products = add_resource(
        db,
        code="RES-GUIDE-PR",
        title="Consigne — établir les produits remarquables",
        resource_type="DISCOVERY_ACTIVITY",
        provenance_kind="SOURCED",
        summary="Développer puis réduire trois produits afin de faire formuler les identités remarquables.",
        minutes=15,
        instruction_ids=[instructions[2].id, instructions[3].id, instructions[5].id],
        validation_status="SOURCE_CONFIRMED",
        blocks=[
            (
                "INSTRUCTION",
                "Consigne 2",
                r"Développe et réduis $(a+b)^2$, $(a-b)^2$ et $(a+b)(a-b)$, puis formule les égalités obtenues.",
            ),
            (
                "PROPERTY",
                "Propriété",
                r"Pour tous nombres $a$ et $b$ : $(a+b)^2=a^2+2ab+b^2$ ; $(a-b)^2=a^2-2ab+b^2$ ; $(a+b)(a-b)=a^2-b^2$.",
            ),
        ],
    )
    application = add_resource(
        db,
        code="RES-GUIDE-APP",
        title="Application — développer et factoriser",
        resource_type="APPLICATION",
        provenance_kind="SOURCED",
        summary="Exercices d'application directe sur les trois produits remarquables.",
        minutes=10,
        instruction_ids=[instructions[3].id, instructions[5].id],
        validation_status="SOURCE_CONFIRMED",
        blocks=[
            (
                "INSTRUCTION",
                "Application",
                r"Développe : $A=(2x+1)^2$, $B=(3x-2)^2$, $C=(4x-3)(4x+3)$. Factorise : $D=x^2+6x+9$, $E=4x^2-9$, $F=4x^2-4x+1$.",
            ),
        ],
    )
    demo = add_resource(
        db,
        code="RES-DEMO-TUILES",
        title="[DÉMO — NON SOURCÉ] Carrés et tuiles algébriques",
        resource_type="DISCOVERY_ACTIVITY",
        provenance_kind="DEMO_NON_SOURCE",
        summary="Contenu fictif de démonstration permettant de tester la comparaison et l'adaptation.",
        minutes=15,
        instruction_ids=[instructions[2].id, instructions[5].id],
        validation_status="DEMO",
        blocks=[
            (
                "STATEMENT",
                "Énoncé de démonstration",
                r"[DÉMO] Un carré de côté $a+b$ est partagé en un carré de côté $a$, un carré de côté $b$ et deux rectangles de dimensions $a$ et $b$.",
            ),
            (
                "INSTRUCTION",
                "Consigne de démonstration",
                r"[DÉMO] Exprime l'aire totale de deux manières et déduis une identité remarquable.",
            ),
            (
                "FIGURE",
                "Figure TikZ de démonstration",
                r"\begin{tikzpicture}[scale=0.55]\draw[thick] (0,0) rectangle (5,5);\draw (3,0)--(3,5);\draw (0,3)--(5,3);\node at (1.5,1.5) {$a^2$};\node at (4,4) {$b^2$};\node at (4,1.5) {$ab$};\node at (1.5,4) {$ab$};\end{tikzpicture}",
            ),
        ],
    )
    db.flush()

    product_property = db.scalar(select(m.PedagogicalBlock).where(m.PedagogicalBlock.resource_version_id == products.id, m.PedagogicalBlock.block_type == "PROPERTY"))
    if product_property:
        db.add_all(
            [
                m.BlockVariant(block_id=product_property.id, target="TEACHER", label="Version enseignant", content_latex=r"$(a+b)^2=a^2+2ab+b^2$ ; $(a-b)^2=a^2-2ab+b^2$ ; $(a+b)(a-b)=a^2-b^2$."),
                m.BlockVariant(block_id=product_property.id, target="LEARNER_INITIAL", label="Version apprenant à compléter", content_latex=r"$(a+b)^2=\ldots$ ; $(a-b)^2=\ldots$ ; $(a+b)(a-b)=\ldots$."),
                m.BlockVariant(block_id=product_property.id, target="LEARNER_COMPLETED", label="Version apprenant complétée", content_latex=r"$(a+b)^2=a^2+2ab+b^2$ ; $(a-b)^2=a^2-2ab+b^2$ ; $(a+b)(a-b)=a^2-b^2$."),
            ]
        )

    for version, pages in [(parcel, "74-76"), (products, "76-77"), (application, "77")]:
        db.add(
            m.SourceOccurrence(
                source_document_id=source_guide.id,
                entity_type="PedagogicalResourceVersion",
                entity_id=version.id,
                page_label=pages,
                locator="Exemple de fiche pédagogique",
                excerpt=version.summary,
            )
        )

    sheet = m.TeacherSessionSheet(code="FICHE-DEMO-001", title="Produits remarquables — séance de découverte")
    db.add(sheet)
    db.flush()
    revision = m.TeacherSheetRevision(
        sheet_id=sheet.id,
        revision_number=1,
        status="DRAFT",
        identification_json=json.dumps(
            {
                "établissement": "Collège de démonstration",
                "année scolaire": "2026-2027",
                "professeur": "Enseignant de démonstration",
                "classe": "4e",
                "effectif": "40",
                "groupes": "8 groupes de 5",
                "date": m.now().date().isoformat(),
                "durée": "55 min",
                "numéro séance": "1",
            },
            ensure_ascii=False,
        ),
        planning_json=json.dumps(
            {
                "situation_apprentissage": "SA1 — Configurations du plan",
                "séquence": "Séquence 8 — Calculs sur les expressions algébriques",
                "stratégies": "TI / TG / TC",
            },
            ensure_ascii=False,
        ),
    )
    db.add(revision)
    db.flush()
    for pos, instruction in enumerate([instructions[2], instructions[3], instructions[5]], 1):
        db.add(m.SessionCurriculumSegment(teacher_revision_id=revision.id, instruction_id=instruction.id, position=pos, planned_minutes=15 if pos < 3 else 25))

    for resource_position, version in enumerate([parcel, products, application], 1):
        instance = m.SheetResourceInstance(
            teacher_revision_id=revision.id,
            origin="LIBRARY_DERIVED",
            source_resource_version_id=version.id,
            title=version.title,
            position=resource_position,
        )
        db.add(instance)
        db.flush()
        blocks = db.scalars(select(m.PedagogicalBlock).where(m.PedagogicalBlock.resource_version_id == version.id).order_by(m.PedagogicalBlock.position)).all()
        for block in blocks:
            copy = m.SheetBlockInstance(
                resource_instance_id=instance.id,
                source_block_id=block.id,
                block_type=block.block_type,
                title=block.title,
                content_latex=block.content_latex,
                position=block.position,
            )
            db.add(copy)
            db.flush()
            db.add(
                m.FlowItem(
                    teacher_revision_id=revision.id,
                    block_instance_id=copy.id,
                    phase_code="REALISATION",
                    teacher_action="Présente la consigne et accompagne la mise en commun.",
                    learner_action="Cherche, échange puis restitue.",
                    strategy="TI / TG / TC",
                    duration_minutes=max(3, version.estimated_minutes // max(1, len(blocks))),
                    position=(resource_position - 1) * 10 + block.position,
                )
            )

    support = m.LearnerSupport(code="SUPPORT-DEMO-001", title="Support apprenant — produits remarquables", sequence_id=sequence.id)
    db.add(support)
    db.flush()
    support_revision = m.LearnerSupportRevision(support_id=support.id, revision_number=1, status="DRAFT")
    db.add(support_revision)
    db.flush()
    for resource_position, version in enumerate([products, application], 1):
        instance = m.SupportResourceInstance(
            support_revision_id=support_revision.id,
            origin="LIBRARY_DERIVED",
            source_resource_version_id=version.id,
            title=version.title,
            position=resource_position,
        )
        db.add(instance)
        db.flush()
        blocks = db.scalars(select(m.PedagogicalBlock).where(m.PedagogicalBlock.resource_version_id == version.id).order_by(m.PedagogicalBlock.position)).all()
        for block in blocks:
            if block.block_type == "EXPECTED_TRACE":
                continue
            db.add(
                m.SupportBlockInstance(
                    support_resource_instance_id=instance.id,
                    source_block_id=block.id,
                    block_type=block.block_type,
                    title=block.title,
                    content_latex=block.content_latex,
                    position=block.position,
                )
            )

    db.flush()
    support_revision.status = "FINALIZED"
    support_revision.finalized_at = m.now()
    db.flush()

    finalized_sheet = m.TeacherSessionSheet(code="FICHE-DEMO-EXECUTEE", title="Application des produits remarquables — exemple exécuté")
    db.add(finalized_sheet)
    db.flush()
    finalized_revision = m.TeacherSheetRevision(
        sheet_id=finalized_sheet.id,
        revision_number=1,
        status="DRAFT",
        identification_json=json.dumps({"établissement": "Collège de démonstration", "classe": "4e", "date": m.now().date().isoformat(), "durée": "45 min"}, ensure_ascii=False),
        planning_json=json.dumps({"situation_apprentissage": "SA1 — Configurations du plan", "séquence": "Séquence 8 — Calculs sur les expressions algébriques", "stratégies": "TI / TC"}, ensure_ascii=False),
    )
    db.add(finalized_revision)
    db.flush()
    executed_segment = m.SessionCurriculumSegment(teacher_revision_id=finalized_revision.id, instruction_id=instructions[3].id, position=1, planned_minutes=45)
    db.add(executed_segment)
    db.flush()
    final_resource = m.SheetResourceInstance(teacher_revision_id=finalized_revision.id, origin="LIBRARY_DERIVED", source_resource_version_id=application.id, title=application.title, position=1)
    db.add(final_resource)
    db.flush()
    application_block = db.scalar(select(m.PedagogicalBlock).where(m.PedagogicalBlock.resource_version_id == application.id))
    final_block = m.SheetBlockInstance(resource_instance_id=final_resource.id, source_block_id=application_block.id, block_type=application_block.block_type, title=application_block.title, content_latex=application_block.content_latex, position=1)
    db.add(final_block)
    db.flush()
    db.add(m.FlowItem(teacher_revision_id=finalized_revision.id, block_instance_id=final_block.id, item_kind="ACTIVITY", phase_code="REALISATION", teacher_action="Organise la correction.", learner_action="Traite puis corrige.", strategy="TI / TC", duration_minutes=45, position=1))
    db.flush()
    finalized_revision.status = "FINALIZED"
    finalized_revision.finalized_at = m.now()
    db.flush()
    teaching_session = m.TeachingSession(teacher_revision_id=finalized_revision.id, taught_on=m.now().date().isoformat(), class_label="4e A", notes="Donnée de démonstration.")
    db.add(teaching_session)
    db.flush()
    db.add(m.ExecutedCurriculumSegment(teaching_session_id=teaching_session.id, session_curriculum_segment_id=executed_segment.id, status="DONE", actual_minutes=50, position=1))
    db.add(m.SupportUse(support_revision_id=support_revision.id, teaching_session_id=teaching_session.id, used_on=m.now().date().isoformat(), class_label="4e A", part_label="Application", notes="Donnée de démonstration."))
    db.commit()
    return True


if __name__ == "__main__":
    from .database import SessionLocal

    with SessionLocal() as session:
        created = seed_database(session)
        print("Seed créé." if created else "Seed déjà présent.")
