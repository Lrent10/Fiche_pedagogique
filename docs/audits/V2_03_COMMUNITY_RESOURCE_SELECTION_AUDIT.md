# V2-03 — Ressources et formulations candidates

Date : 2026-09-04. Verdict : PASS_WITH_NON_BLOCKING_ITEMS.

Une ressource versionnée peut mettre en œuvre plusieurs instructions ; chacune
peut présenter plusieurs candidats. L'API filtre par instruction, classe, version
disponible et mapping non retiré/non rejeté. Une ressource composée exclusivement
de résultats enseignant n'est pas une consigne candidate.

Les sept catégories demeurent distinctes : OFFICIAL_PROGRAM, OFFICIAL_GUIDE,
INSPECTOR_VALIDATED, TEACHER_COMMUNITY, BOOK_SOURCE, LOCAL_TEACHER,
DEMO_UNSOURCED. Référence, version, auteur connu, statut et référence d'inspection
sont conservés dans `provenance_json`, puis dans le choix de la révision.
La priorité documentaire n'est pas une note de qualité pédagogique.

Une déclaration communautaire ne peut pas prendre le statut OFFICIAL. Une
validation inspection exige sa référence, mais n'est pas authentifiée par un
compte inspecteur dans ce MVP. Une référence officielle exige un document de
type compatible, son empreinte et une page ; le texte reste une adaptation à
relire, car citer un document ne certifie pas sa transcription.

L'écran parcourt les instructions, montre les contenus typés, les sources et le
choix courant, puis permet son remplacement. Les anciennes copies et adaptations
sont conservées dans l'historique ; une copie partagée par deux instructions n'est
masquée qu'une fois qu'aucune sélection ne l'utilise. Les copies masquées ne sont
pas exportées. Une création personnelle enrichit la bibliothèque pour l'instruction.
L'API accepte les autres provenances ; leur administration complète n'est pas livrée.

Définition, propriété, formule, méthode, figure et consigne sont distinctes des
EXPECTED_RESPONSE/EXPECTED_TRACE réservées à l'enseignant. Les ressources
historiques dérivées du guide portent « adaptation à relire », non « source vérifiée ».

Preuves : RES-001..005, FORM-001/002, TRACE, remplacement avec historique ;
tests frontend UX-006/007 et choix/remplacement. Le navigateur a sélectionné une
propriété puis remplacé une ressource partagée sans perdre la première sélection.
Le corpus initial ne couvre que les instructions 3, 4 et 6 avec des candidats sourcés.
