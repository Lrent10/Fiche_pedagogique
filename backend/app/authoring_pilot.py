"""Small, source-checked pilot. No class-wide ingestion or inferred competencies."""
from sqlalchemy import select
from . import models as m


def install_pilot(db):
    programme = db.scalar(select(m.ProgrammeVersion).where(m.ProgrammeVersion.code == "PRG-4E-BJ"))
    sequence = db.scalar(select(m.Sequence).where(m.Sequence.code == "SEQ8"))
    sources = {s.code: s for s in db.scalars(select(m.SourceDocument)).all()}
    if not programme or not sequence or not {"SRC-PRG-4E", "SRC-GUIDE-4E"} <= sources.keys():
        return
    rows = [
        ("CLASS-COUNTRY", "CLASS", programme.id, "pays", "Bénin", "SRC-PRG-4E", "1"),
        ("CLASS-DISCIPLINE", "CLASS", programme.id, "discipline", "Mathématiques", "SRC-PRG-4E", "1"),
        ("SA-CD1", "SA", sequence.situation_id, "compétences disciplinaires", "Résoudre un problème ou une situation-problème en utilisant les concepts et procédures du langage et du raisonnement mathématique.", "SRC-PRG-4E", "89"),
        ("SA-CD2", "SA", sequence.situation_id, "compétences disciplinaires", "Appréhender les mathématiques dans ses aspects numériques par l’appropriation des outils, techniques et procédés conventionnels ainsi que par le traitement des données.", "SRC-PRG-4E", "89"),
        ("SA-CD3", "SA", sequence.situation_id, "compétences disciplinaires", "Appréhender les mathématiques dans ses aspects géométriques par l’appropriation d’outils et de démarches propres à la géométrie.", "SRC-PRG-4E", "89"),
        ("SEQ-CD", "SEQUENCE", sequence.id, "compétences disciplinaires", "Appréhender le calcul sur les expressions algébriques par l’appropriation des outils, techniques et procédés conventionnels de calcul ainsi que le traitement des données.", "SRC-GUIDE-4E", "32"),
        ("SEQ-CT", "SEQUENCE", sequence.id, "compétences transversales", "Résoudre un problème ou une situation-problème en utilisant les outils et propriétés relatifs au calcul sur les expressions algébriques.", "SRC-GUIDE-4E", "31-32"),
        ("SEQ-CONT", "SEQUENCE", sequence.id, "contenus de formation", "Factorisation ; produits remarquables ; développement et réduction.", "SRC-GUIDE-4E", "31-32"),
        ("SEQ-KNOW", "SEQUENCE", sequence.id, "connaissances et techniques", "Reconnaître une somme et un produit ; factoriser par un facteur commun ; énoncer et utiliser les produits remarquables ; réduire une somme ; développer un produit ; calculer une valeur numérique.", "SRC-GUIDE-4E", "32"),
    ]
    for code, scope, scope_id, field, value, source_code, page in rows:
        code = "V203-" + code
        if not db.scalar(select(m.CurriculumAttribute.id).where(m.CurriculumAttribute.code == code)):
            db.add(m.CurriculumAttribute(code=code, programme_version_id=programme.id, scope=scope, scope_id=scope_id, field=field, value=value, source_document_id=sources[source_code].id, source_version="Septembre 2020", page_label=page))
    db.flush()


if __name__ == "__main__":
    from .database import SessionLocal
    with SessionLocal() as db:
        install_pilot(db)
        db.commit()
    print("Attributs du pilote 4e installés sans modification des fiches existantes.")
