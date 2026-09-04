# V2-03 — Modèle de conception curriculaire

Date : 2026-09-04. Verdict : PASS_WITH_NON_BLOCKING_ITEMS, sur le pilote 4e.

## Baseline et périmètre

Baseline expressément autorisée : `fix/ux-bb-001-identification-navigation`,
`2ec0f27d75fc6d6e86d1caa079012afc9736f7f4`. Le checkpoint V2-02B est déjà
`a1c6b67efc46e92b535477be918f9fdc2bbc77c6` ; aucun nouveau checkpoint,
changement de branche ou rapprochement Git n'était nécessaire.

Le gate a vérifié racine, branche, HEAD, worktree propre, M01, migration locale
0003, 49 tests backend, 28 frontend, build et démarrage HTTP 200/200.
M01 demeure à `03F54F7C62A0E6F2F3BE154631EE542408BF5423B5D4FAD8B147CD85CE0E3B67`.

## Modèle livré

`ProgrammeVersion → SituationApprentissage → Sequence → InstructionGuide`
reste la chaîne curriculaire. `CurriculumAttribute` porte séparément la valeur,
le champ, le programme, le niveau d'applicabilité CLASS/SA/SEQUENCE/INSTRUCTION,
l'identifiant du périmètre, le document, sa version et sa page.
Les trois compétences disciplinaires SA ne sont pas dupliquées sur chaque séquence.
Le préremplissage compose les attributs applicables et en conserve un instantané
dans `TeacherSheetRevision.authoring_json`.

Les quatre périmètres sont accessibles. Le périmètre classe sert à parcourir ;
la création exige une SA, une séquence ou une instruction. Un sous-ensemble
d'instructions conserve l'ordre du guide. Une instruction extérieure est rejetée.

Le pilote installe neuf attributs sourcés, une seule classe, SA1/séquence 8.
Aucune ingestion Première C ni extension du corpus national n'a été effectuée.

## Migration et immutabilité

`0004_curriculum_authoring` ajoute une table et deux colonnes JSON, sans reset.
La base locale a été migrée depuis 0003. Deux tests Alembic réels couvrent
l'installation vide et une base temporaire représentant 0003 avec une révision
finalisée et une ressource préexistantes : contenu conservé, nouvelles colonnes `{}`.

Le contrôle d'installation vide a découvert l'ancien bootstrap 0001 fondé sur
les modèles courants. Les migrations 0002/0003/0004 vérifient désormais la présence
des ajouts avant de les appliquer ; elles ne modifient pas un ajout déjà présent.
`start-dev.ps1` s'arrête si migration ou seed échoue.

Les écritures API et ORM sur les révisions finalisées sont rejetées. Une nouvelle
révision copie les instantanés et remappe les identifiants des ressources choisies.
Les snapshots historiques ne sont pas réinterprétés par le seed.

Preuves : `test_v2_03_authoring.py` (CURR, COMP, IMMUT),
`test_v2_03_migration.py` ; campagne globale 77 backend / 42 frontend / build PASS.
Limites : SQLite testé ; pas de campagne PostgreSQL ni de certification multi-SA.
