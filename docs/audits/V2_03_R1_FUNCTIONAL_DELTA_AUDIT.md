# V2-03-R1-G0 — Audit du delta fonctionnel

Date : 2026-09-04. Mission : `READ_ONLY_FUNCTIONAL_DELTA_AUDIT`.

Le delta est cartographié sur le code autorisé. Le modèle actuel permet de préparer une fiche sur un sous-ensemble d'instructions et d'enregistrer son exécution. Il ne possède pas encore la séance planifiée, numérotée dans une séquence et reliée à une couverture cumulative par classe. Le suivi actuel confond toute exécution avec une instruction terminée. Devoirs structurés, documents utilisés par fiche et progression annuelle nécessitent des ajouts.

Le verdict de cet audit porte sur la cartographie du delta, pas sur la conformité du produit au modèle cible, la fidélité des transcriptions ou la réussite d'une nouvelle campagne de tests.

## A. BASELINE

| Contrôle exécuté | Résultat |
|---|---|
| Racine Git | `C:/Users/HP/Documents/ChatGPT/Fiche_pedagogique` |
| `git branch --show-current` | `fix/ux-bb-001-identification-navigation` — conforme |
| `git rev-parse HEAD` | `578b2a4b49e8284f1885693e368554762bc62e25` — conforme |
| `git status --short` | Vide avant audit |
| `git status` | `nothing to commit, working tree clean` |
| `git diff --check` | Code retour 0, aucun message |

La création de ce seul rapport est l'exception documentaire expressément autorisée par la section 17 de la mission. Aucun code, source métier, export, schéma, seed ou donnée applicative n'est modifié. Aucun commit, démarrage, migration, ingestion ou appel d'API mutante n'est effectué.

### Méthode et limites de preuve

- **SOURCE** : le modèle cible et les quantités 8/6/3 viennent de la mission. Les audits V2-03 du dépôt sont des preuves historiques secondaires, pas des prescriptions nouvelles.
- **EXTRACTION** : lecture des modèles, quatre migrations, schémas, routes, services, seed/pilote, frontend, moteur LaTeX et tests. Les références ci-dessous pointent sur le code au SHA autorisé ; `fichier:ligne` désigne le début de la preuve pertinente.
- **INTERPRÉTATION** : les effets déduits du code sont explicitement exposés, sans prétendre avoir reproduit les parcours en navigateur.
- **RECOMMANDATION** : sections M à P ; aucune de ces modifications n'est exécutée.

`data/app.db` existe localement, mais n'a pas été ouverte. Le schéma audité est le schéma déclaré par le code et les migrations ; la version effectivement installée et le contenu vivant de cette base ne sont pas attestés ici. Les originaux métier cités par V2-03 ne sont pas présents dans le dépôt inspecté : le rapport de provenance les situe sous `C:\Users\HP\Desktop\Base`. Ils ne sont pas relus hors dépôt dans cette mission. Les PDF sous `exports` sont des productions de l'application, pas ces originaux.

Aucun test applicatif n'est rejoué. `backend/tests/conftest.py:19` recrée/supprime des tables à chaque test ; `test_v2_03_migration.py:16` exécute Alembic. Leur lecture est autorisée, leur exécution contrevient au périmètre strict retenu. Pas de compilation PDF ni d'inspection visuelle nouvelle. Les 77 tests backend / 42 frontend et les inspections annoncés par V2-03 restent historiques.

### Index des preuves

| Code | Preuve inspectée |
|---|---|
| E01 | `backend/app/models.py:27` à `InstructionGuide` : programme, guide, SA, séquence, connaissances, attributs |
| E02 | `backend/app/models.py:211` : fiche, révision, segments, instances, déroulement ; `:298` : séance exécutée et segments exécutés |
| E03 | `backend/app/authoring.py:79`, `:121`, `:278` : périmètre, préremplissage, composition |
| E04 | `backend/app/main.py:513`, `:540` ; `backend/app/schemas.py:55` ; `frontend/src/App.tsx:214`, `:314` : exécution et progression |
| E05 | `backend/app/models.py:97`, `:269` ; `backend/app/services.py:474` ; `backend/app/seed.py:147` : durées et alerte |
| E06 | `backend/app/authoring_pilot.py:6` ; `backend/app/authoring.py:140` : neuf attributs du pilote et héritage |
| E07 | `backend/app/authoring.py:17`, `:50`, `:165`, `:174`, `:214`, `:251` : catégories, priorité et provenance des ressources |
| E08 | `backend/app/main.py:221` ; `frontend/src/App.tsx:140` : provenance des personnalisations et sauvegarde |
| E09 | `backend/app/exporter.py:116`, `:188`, `:193` ; `backend/app/authoring.py:345` : documents enseignant et apprenant |
| E10 | `frontend/src/Authoring.tsx:23` : création, choix des instructions, ressources et support ; `frontend/src/App.tsx:316` : sources de bibliothèque |
| E11 | `backend/app/models.py:106`, `:149`, `:200`, `:378` : sources, ressources, mappings, exports |
| E12 | `backend/app/services.py:145`, `:343`, `:412` ; `backend/app/main.py:154`, `:310`, `:316` : parcours historique, support vers fiche, révisions et duplication |
| E13 | `backend/alembic/versions/0001_initial.py`, `0002_v2_document_workflow.py`, `0003_final_document_editor.py`, `0004_curriculum_authoring.py` : schéma livré |
| E14 | `backend/tests/test_v2_03_authoring.py`, `test_v2_03_migration.py`, `test_curriculum_level_invariant.py`, `test_api_vertical_slice.py` ; `frontend/src/Authoring.test.tsx`, `App.test.tsx` : tests existants consultés |
| E15 | Les sept `docs/audits/V2_03_*_AUDIT.md` antérieurs : modèle, autofill, composition, communauté, provenance, support, parcours enseignant |

## B. CURRENT MODEL MAP

```text
ProgrammeVersion(level) ──> SituationApprentissage ──> Sequence ──> InstructionGuide
GuideVersion ───────────────────────────────────────> Sequence
Sequence ──> ConnaissanceTechnique
ProgrammeVersion ──> CurriculumAttribute(scope, scope_id, field, value, source)
SituationApprentissage ──> CurriculumTimeAllocation(source, hours)

TeacherSessionSheet ──> TeacherSheetRevision
                         ├─ identification_json / planning_json / authoring_json
                         ├─ SessionCurriculumSegment ──> InstructionGuide
                         ├─ SheetResourceInstance ──> copies de blocs / FlowItem
                         └─ TeachingSession (exécution après finalisation)
                              └─ ExecutedCurriculumSegment ──> segment préparé

PedagogicalResource ──> Version ──> Block
                         └─ ResourceInstructionMapping ──> InstructionGuide
SourceDocument ──> SourceOccurrence / CurriculumAttribute / allocation

LearnerSupport (séquence OU SA) ──> Revision ──> copies de ressources/blocs
SupportUse ──> support, fiche ou exécution ; sélection de blocs
DocumentExport ──> révision enseignant OU apprenant
```

Il n'existe pas d'entité de classe scolaire/année distincte : `ProgrammeVersion.level` porte le niveau, les libellés de classe sont documentaires. Le scope `CLASS` utilise l'identifiant du programme. Une `TeachingSession` existe réellement, mais représente une exécution rattachée à une révision déjà finalisée ; elle ne constitue pas la séance planifiée cible. `revision_number` compte les versions d'une fiche, jamais les séances de la séquence. Preuves E01–E04, E12.

## C. TARGET MODEL MAP

```text
Classe (niveau + subdivision + année)
  └─ contexte de séquence / SA du curriculum versionné
       └─ Séance planifiée 1..N ──> fiche enseignant ──> révisions
            ├─ instructions retenues et partie prévue
            ├─ créneau, pause, durée pédagogique
            └─ exécution : couverture par instruction
                 NOT_STARTED / PARTIAL / COVERED

Catalogue global de compétences (8 transversales, 6 transdisciplinaires, 3 disciplinaires)
  └─ applicabilité sourcée : version, classe/niveau, SA, séquence

HOMEWORK_EXERCISE ──> classe, notions, séquence, instructions facultatives, source, validation
  └─ usage dans une séance : CURRENT_NOTION / PRIOR_NOTION_REACTIVATION

Ressources sélectionnées ──> documents distincts ──> documents utilisés de la fiche
AnnualProgressionPlan ──> classe, année, semaines, volumes et périodes
```

Cette carte est une cible métier, pas un schéma SQL décidé. La SA et la séquence restent des objets du curriculum : les réutiliser par classe ne doit pas dupliquer ni modifier leur prescription canonique. La progression annuelle est une planification séparée ; une réactivation ne change pas le périmètre de la séance courante.

## D. GAP ANALYSIS

Statuts : `ALREADY_SUPPORTED` = capacité présente dans le code, sur le périmètre indiqué ; `PARTIAL` = éléments présents, contrat cible incomplet ; `MISSING` = contrat absent ; `CONFLICT` = comportement contraire à la cible ; `UNCERTAIN` = preuve requise indisponible. Les besoins de migration sont prospectifs : `YES` inclut ajout de structures ou données de référence ; `TBD` dépend du stockage choisi. `SOURCE_EVIDENCE_REQUIRED` signifie preuve métier supplémentaire nécessaire avant implémentation/chargement, pas absence des preuves de code E01–E15.

| REQUIREMENT_ID | TARGET_CAPABILITY | CURRENT_IMPLEMENTATION | STATUS | AFFECTED_LAYER | DATA_MIGRATION_REQUIRED | UX_CHANGE_REQUIRED | SOURCE_EVIDENCE_REQUIRED | RISK | RECOMMENDED_NEXT_MISSION |
|---|---|---|---|---|---|---|---|---|---|
| R01 | Classe → SA → séquence → séance → fiche | Chaîne curriculaire ; fiche puis exécution, classe documentaire (E01–04) | PARTIAL | DB/API/UI | YES | YES | NO | Élevé : confusion préparation/exécution | P1 séance |
| R02 | Plusieurs séances planifiées par séquence | Plusieurs fiches possibles ; aucune collection de séances de séquence (E02–03) | MISSING | DB/API/UI | YES | YES | NO | Élevé : continuité absente | P1 séance |
| R03 | Sélectionner une ou plusieurs instructions | Sous-ensemble contrôlé et ordonné dans compose (E03) | ALREADY_SUPPORTED | API/UI | NO | NO | NO | Faible dans ce parcours | Conserver |
| R04 | Traiter partiellement une instruction | Adaptation de blocs et statut d'exécution PARTIAL ; pas de partie ni reliquat par instruction (E02–04) | PARTIAL | DB/API/UI | YES | YES | NO | Élevé : reste inconnu | P1 couverture |
| R05 | NOT_STARTED / PARTIAL / COVERED exacts | Toute exécution, même SKIPPED, produit DONE (E04) | CONFLICT | API/UI | TBD | YES | NO | Élevé : faux achèvement | P1 couverture |
| R06 | Couverture isolée par classe et année | Progression agrégée sans filtre classe/année (E04) | MISSING | DB/API/UI | YES | YES | NO | Élevé : mélange de classes | P1 contexte |
| R07 | session_number_within_sequence | Champ texte numéro de séance, sans compteur ni unicité (E02–03) | MISSING | DB/API/UI/PDF | YES | YES | NO | Élevé : numérotation non fiable | P1 séance |
| R08 | Reprendre/créer la séance suivante | Recréation, duplication, nouvelle révision ; aucun lien de succession (E10/E12) | MISSING | API/UI | YES | YES | NO | Élevé : répétition/omission | P1 reprise |
| R09 | SA_DURATION sourcée | Allocations distinctes ; conflit 56/60 conservé, pas de valeur résolue (E03/E05) | PARTIAL | Données/API/PDF | TBD | YES | YES | Moyen : arbitrage nécessaire | P0 durées sources |
| R10 | SEQUENCE_PLANNED_DURATION | Aucun champ métier dédié (E01/E05) | MISSING | DB/API/UI/PDF | YES | YES | YES | Élevé : planification impossible | P2 durée séquence |
| R11 | SESSION_SLOT_DURATION | Durée de séance en texte libre (E03/E12) | PARTIAL | DB/API/UI/PDF | YES | YES | NO | Moyen : unité/sens ambigus | P2 créneau |
| R12 | BREAK_DURATION | Aucune pause explicitement modélisée (E02/E03) | MISSING | DB/API/UI/PDF | YES | YES | NO | Élevé : temps disponible surestimé | P2 pause |
| R13 | SESSION_PEDAGOGICAL_DURATION | Durée II libre ; parcours historique recopie le créneau (E05/E12) | CONFLICT | DB/API/UI/PDF | YES | YES | NO | Élevé : durées confondues | P2 calcul pédagogique |
| R14 | Catalogue global 8/6/3 | Attributs textuels du pilote, aucun catalogue global (E01/E06) | MISSING | DB/seed/API/UI | YES | YES | YES | Élevé : identité des compétences absente | P3 catalogue |
| R15 | Applicabilité par version/classe/SA/séquence | Scope et provenance présents sans compétence référencée (E06) | PARTIAL | DB/API | YES | YES | YES | Moyen : portée peu contrainte | P3 applicabilité |
| R16 | Provenance du préremplissage et des choix | Snapshot et sources, version, portée, origine et override (E03/E07/E08) | ALREADY_SUPPORTED | DB/API/UI | NO | NO | NO | Faible ; ne vaut pas validation du texte | Conserver |
| R17 | Éviter duplication interclasses | Héritage SA évite duplication par séquence ; identité globale absente (E06) | PARTIAL | DB/seed | YES | NO | YES | Moyen : duplication future | P3 catalogue |
| R18 | Préremplir tous les champs I | Discipline/classe/SA/séquence ; locaux libres, numéro manuel (E03/E10) | PARTIAL | API/UI/PDF | YES | YES | YES | Moyen : fiche incomplète | P1 puis P2 |
| R19 | Préremplir tous les champs II | Compétences/connaissances pilote ; stratégies/matériel/durée libres (E03/E06) | PARTIAL | Données/API/UI/PDF | TBD | YES | YES | Moyen : ne pas inventer les valeurs | P3 champs sourcés |
| R20 | Hiérarchie documentaire à sept rangs | Programme/guide ex aequo ; progression institutionnelle absente (E07) | CONFLICT | API/DB/UI | YES | YES | YES | Élevé : priorité cible non appliquée | P0 puis P3 sources |
| R21 | Communauté sans écrasement des prescriptions | Sélection modifie une copie ; statut officiel refusé ; override tracé (E07/E08) | ALREADY_SUPPORTED | API/DB/UI | NO | NO | NO | Faible dans authoring | Conserver |
| R22 | Cinq catégories de consignes | INSTRUCTION/CONSIGNE/APPLICATION, sans les cinq usages distincts (E07/E09) | PARTIAL | API/UI/DB/PDF | TBD | YES | NO | Moyen : usages indiscernables | P4 typologie |
| R23 | Sept catégories de savoirs | Définition/propriété/formule/méthode/remarque ; théorème/règle absents (E07/E09) | PARTIAL | API/UI/PDF | TBD | YES | NO | Moyen : typage incomplet | P4 typologie |
| R24 | EXPECTED_RESPONSE et FIGURE distincts | Types reconnus et traitement distinct (E07/E09/E14) | ALREADY_SUPPORTED | API/PDF | NO | NO | NO | Faible si correctement typés | Conserver |
| R25 | Objet HOMEWORK_EXERCISE | Ressources/blocs génériques, aucun objet ou rôle devoir (E01/E02/E11) | MISSING | DB/API/UI | YES | YES | NO | Élevé : devoir non traçable | P4 devoir |
| R26 | Liens du devoir aux notions/séquence/source/validation | Briques ressource et mapping instruction réutilisables, contrat devoir absent (E11) | MISSING | DB/API | YES | YES | YES | Élevé : compatibilité non garantie | P4 liens devoir |
| R27 | CURRENT_NOTION / PRIOR_NOTION_REACTIVATION | Aucun usage distinct séparé du périmètre courant (E03/E11) | MISSING | DB/API/UI | YES | YES | NO | Élevé : extension indue du périmètre | P4 réactivation |
| R28 | Devoir de bout en bout et PDF | EXERCISE générique imprimable, aucune section devoir ni tests dédiés (E09/E14) | MISSING | API/UI/PDF/tests | YES | YES | NO | Moyen : simple texte sans fonction | P4 export devoir |
| R29 | DOCUMENTS UTILISÉS fonctionnel par fiche | Écran Sources global et provenance des choix ; aucune section fiche (E09/E10) | PARTIAL | API/UI/PDF | YES | YES | NO | Moyen : bibliographie absente | P5 documents |
| R30 | Dédupliquer les documents sélectionnés | Set de noms de fichiers sur bibliothèque entière, pas choix de fiche (E10) | PARTIAL | API/UI | TBD | YES | NO | Moyen : faux doublons/omissions | P5 déduplication |
| R31 | Documents automatiques + manuels persistés/exportés | Aucun snapshot documentaire dédié ni PDF correspondant (E02/E09) | MISSING | DB/API/UI/PDF | YES | YES | NO | Moyen : liste instable | P5 persistance |
| R32 | AnnualProgressionPlan complet et séparé | Écran de progression réalisée uniquement (E01–04/E13) | MISSING | DB/API/UI | YES | YES | YES | Élevé : pas de plan annuel | P6 plan annuel |
| R33 | EXPECTED_RESPONSE absent du support produit | Filtré à la copie V2-03 et aux deux rendus apprenant (E09/E14) | ALREADY_SUPPORTED | API/PDF | NO | NO | NO | Faible ; texte libre non analysé | Conserver |
| R34 | Aucune grande zone réponse par défaut | Types espace exclus et suffixe historique retiré au rendu (E09/E14) | ALREADY_SUPPORTED | PDF | NO | NO | NO | Faible ; contenu volontaire libre | Conserver |
| R35 | Consignes, définitions, propriétés, formules, figures conservées | Copie des blocs visibles, filtrage ciblé, rendu (E09) | ALREADY_SUPPORTED | API/PDF | NO | NO | NO | Faible ; revoir PDF après ajouts | Conserver |
| R36 | AUTO prochaine séance selon historique et reliquat | Compose tout le sous-ensemble demandé, sans historique (E03) | MISSING | API/UI | YES | YES | NO | Élevé : recommence les acquis | P7 AUTO suivant |
| R37 | AUTO selon budget pédagogique et pause | Pas de budget dans Compose ; durées créées à zéro (E03) | MISSING | API/UI | YES | YES | NO | Élevé : séance irréalisable | P7 budget |
| R38 | Compatibilité notionnelle et priorité AUTO | Filtre niveau/mapping/disponibilité ; pas lien notion ni sept rangs (E07) | PARTIAL | DB/API/tests | YES | YES | YES | Élevé : compatibilité déclarative | P3/P4 puis P7 |
| R39 | AUTO crée un brouillon sans finaliser | DRAFT par défaut ; finalisation par route/action distinctes (E02/E03/E14) | ALREADY_SUPPORTED | API/UI | NO | NO | NO | Faible | Conserver |
| R40 | Preuves officielles du catalogue et de l'applicabilité cible | Quantités exigées par mission ; originaux hors dépôt non relus (E15) | UNCERTAIN | Sources/seed | TBD | NO | YES | Élevé : certification impossible ici | P0 sources |
| R41 | Préserver sources et révisions historiques | Copies, nouvelle révision, garde ORM de finalisation (E02/E12/E13/E14) | ALREADY_SUPPORTED | DB/API | NO | NO | NO | Moyen lors des migrations futures | Conserver et tester |

### Findings nécessaires

Les sévérités qualifient les écarts à la cible. Aucun finding BLOCKING n'empêche de réaliser cet audit ; cela n'autorise pas l'implémentation. Les dix MAJOR suivants regroupent les exigences pour éviter les doublons.

| FINDING_ID | Exigences | Constat et conséquence | Preuve | Mission |
|---|---|---|---|---|
| V203R1-MAJ-SEQ-001 | R01–02, R07–08 | Pas de séance planifiée identifiée dans sa séquence ; numéro libre et duplication ne garantissent pas la continuité | E02/E03/E12 | P1 |
| V203R1-MAJ-SEQ-002 | R04–06 | Statut global recopié sur les instructions ; toute exécution devient DONE, sans classe/année. Une instruction partielle/sautée peut être affichée achevée | E04 | P1 |
| V203R1-MAJ-DUR-001 | R09–13 | Créneau et temps pédagogique confondus, pause et durée de séquence absentes ; budget non calculable | E03/E05/E12 | P0/P2 |
| V203R1-MAJ-COMP-001 | R14–15, R17–19, R40 | Attributs sourcés utiles, mais pas de catalogue global ni contextualisation par identifiant de compétence ; 8/6/3 non certifié ici | E01/E06/E15 | P0/P3 |
| V203R1-MAJ-SRC-001 | R20, R38 | Priorité programme/guide indifférenciée et progression institutionnelle absente ; l'ordre cible n'est pas représenté | E07 | P0/P3 |
| V203R1-MAJ-RES-001 | R22–23 | Typologie trop générale pour distinguer les cinq usages de consignes ; théorème/règle non reconnus dans l'API authoring | E07/E09 | P4 |
| V203R1-MAJ-HW-001 | R25–28 | Pas de devoir structuré ni de réactivation séparée ; les liens/exports/tests métier manquent | E01/E07/E09/E11/E14 | P4 |
| V203R1-MAJ-DOC-001 | R29–31 | Liste globale de bibliothèque, sans liste persistée des documents réellement utilisés dans une fiche ni export enseignant | E09/E10 | P5 |
| V203R1-MAJ-PROG-001 | R32 | Aucun plan annuel classe/année/semaine ; écran d'exécution ne remplit pas cette fonction | E01–04/E13 | P6 |
| V203R1-MAJ-AUTO-001 | R36–38 | AUTO ignore historique, reliquat et temps disponible ; produit un brouillon de périmètre, pas la prochaine séance | E03/E07 | P7 |

## E. SESSION / SEQUENCE DELTA

**Réponse A/B : ni contrainte « une fiche unique par séquence », ni vraie chaîne de séances planifiées.** L'application crée une fiche indépendante pour le périmètre choisi. Une séquence entière est présélectionnée dans l'UI ; l'enseignant peut réduire aux instructions souhaitées. Il peut créer plusieurs fiches sur la même séquence : aucune unicité fiche/séquence ne l'interdit. Cela ne suffit pas à obtenir `Sequence → Session 1..N`.

La relation est indirecte : révision → segment → instruction → séquence, complétée par un scope dans `authoring_json`. Le scope SA permet même plusieurs séquences dans une fiche. Il faudra décider explicitement du traitement de ces fiches historiques si la cible impose une seule séquence par séance ; ne pas leur attribuer artificiellement une séquence unique.

Le parcours support → fiche permet une sélection de blocs et un libellé de partie dans `SupportUse` (E12). Il ne mémorise pas la partie déjà couverte d'une instruction. Une adaptation de texte peut décrire cette partie, sans suivi exploitable par AUTO.

L'API d'exécution accepte un seul statut `DONE/PARTIAL/SKIPPED` pour toute la séance et le recopie sur chacun des segments. `/api/progress` compte les lignes sans lire leur statut : **une seule ligne PARTIAL ou SKIPPED suffit à produire DONE**. Il n'existe ni agrégation de couverture cumulative ni filtre par classe/année. L'UI transmet uniquement DONE et affiche une coche dès que `executions` est non nul. Ces conclusions sont déduites directement d'E04, non d'un test exécuté.

Reprendre manuellement une séquence est possible en la sélectionnant à nouveau. « Dupliquer » recopie une fiche ; « Nouvelle révision » révise le même document. Aucun des deux ne signifie « séance suivante ». Aucun écran de création ne présente les instructions restantes pour la classe considérée.

## F. DURATION DELTA

| Durée cible | Stockage/rendu actuel | Delta |
|---|---|---|
| SA_DURATION | `CurriculumTimeAllocation.hours` avec source et SA ; champ I distinct si valeur non ambiguë | Brique réelle. Seed 56 h programme / 60 h guide ; affichage du conflit. La hiérarchie cible exige une décision explicite de valeur applicable sans supprimer l'autre source |
| SEQUENCE_PLANNED_DURATION | Aucun attribut métier dédié à la durée de séquence | Ajouter une durée planifiée avec provenance ou origine locale explicite |
| SESSION_SLOT_DURATION | `identification_json['durée de la séance']` | Texte libre sans unité contrôlée ni sens de créneau garanti |
| BREAK_DURATION | Aucun champ dédié ; phase libre ne suffit pas | Ajouter un temps de pause explicite |
| SESSION_PEDAGOGICAL_DURATION | `planning_json['durée']` ; minutes des segments et du déroulement | Aucun calcul créneau moins pause ; parcours historiques recopient la même durée dans I et II |

`FlowItem.duration_minutes`, `ActivityPhase.duration_minutes`, `SessionCurriculumSegment.planned_minutes` et `ExecutedCurriculumSegment.actual_minutes` existent : le modèle ne se réduit donc pas à un unique champ. Ils ne réalisent toutefois pas les cinq concepts cibles. AUTO crée les minutes des segments/blocs à zéro. Le parcours historique répartit le total par division entière. L'alerte extrait les chiffres du texte de séance (`1 h 30` devient 130, pas 90) et compare à la somme du déroulement ; elle ne traite ni unité ni pause. Preuves E03/E05/E12.

## G. COMPETENCY DELTA

Le pilote ajoute neuf attributs : deux d'identification CLASS, trois compétences disciplinaires SA, une compétence disciplinaire contextualisée SEQUENCE, une transversale SEQUENCE, contenus et connaissances SEQUENCE. Il ne charge pas 17 compétences globales et ne fournit aucune compétence transdisciplinaire contextualisée. Le champ correspondant reste libre.

Il n'y a **pas de duplication interclasses démontrée** : une seule classe pilote est semée. Les trois compétences de SA sont stockées une fois et héritées, ce qui évite leur recopie sur chaque séquence. En revanche, `CurriculumAttribute.value` ne référence aucune identité de compétence globale : ajouter plusieurs classes par le même mécanisme pourrait dupliquer des textes. Une contextualisation différente ne doit pas être déclarée doublon uniquement parce qu'elle ressemble à une compétence globale.

La provenance des valeurs affichées est réelle : source_document_id, édition, page, scope ; `autofill` concatène les attributs applicables par champ, puis sauvegarde leurs références dans la révision. L'ordre est celui des identifiants d'attribut, sans résolution spécifique de priorité programme/guide. Un choix de ressource conserve séparément sa provenance dans `selections`. Personnaliser I/II exige un override explicite et change l'origine en `USER_OVERRIDE` en conservant les références. Ce mécanisme doit être conservé.

### Préremplissage des parties I et II

Ces statuts portent sur le champ fonctionnel dans le parcours V2-03 ; un champ libre disponible n'est pas un préremplissage sourcé complet.

| Partie / champ | Classification | Preuve / limite |
|---|---|---|
| I — discipline | SUPPORTED | Mathématiques puis attribut CLASS sourcé du pilote ; E03/E06 |
| I — classe | SUPPORTED | Niveau du programme prérempli ; subdivision documentaire contrôlée séparément ; E03/E08 |
| I — SA | SUPPORTED | Code/titre issus du périmètre ; E03 |
| I — séquence | SUPPORTED | Numéro/titre issus du périmètre ; plusieurs possibles au scope SA ; E03 |
| I — numéro de séance | PARTIALLY_SUPPORTED | Texte persisté et imprimé, sans calcul dans la séquence ; E03/E09 |
| I — durée SA | PARTIALLY_SUPPORTED | Valeurs sourcées présentes, conflit du pilote non résolu ; E05 |
| I — date / champs locaux | PARTIALLY_SUPPORTED | Saisie puis persistance ; profil navigateur pour professeur/établissement/année seulement ; date non préremplie par compose ; E03/E10 |
| II — compétences | PARTIALLY_SUPPORTED | Attributs SA/séquence du pilote ; catalogue global et transdisciplinaires manquants ; E06 |
| II — connaissances/techniques | PARTIALLY_SUPPORTED | Synthèse SEQ8 sourcée ; n'est pas recalculée finement selon le sous-ensemble d'instructions ; E03/E06 |
| II — stratégie objet d'apprentissage | PARTIALLY_SUPPORTED | Champ libre disponible, valeur pilote absente ; E03 |
| II — stratégies d'enseignement | PARTIALLY_SUPPORTED | Saisie libre et stratégie de FlowItem ; pas de sélection sourcée automatique ; E02/E03 |
| II — durée pédagogique | INCORRECTLY_MODELED | Texte libre ou copie de durée de séance, sans pause/calcul ; E05/E12 |
| II — matériel | PARTIALLY_SUPPORTED | Deux champs apprenants/enseignant, initialement vides ; E03/E09 |

La présence d'une clé arbitraire dans un JSON ne prouve ni typage, ni applicabilité, ni contenu officiel. Ne pas remplir les champs encore vides à partir d'une fiche de collègue en les présentant comme prescrits.

## H. HOMEWORK DELTA

### Typologie complète demandée

| Type cible | Support actuel | Conclusion |
|---|---|---|
| DISCOVERY_CONSIGNE | INSTRUCTION/CONSIGNE et titre libre | Implicite seulement ; usage découverte absent |
| APPLICATION_CONSIGNE | APPLICATION et titre Application rendu spécifiquement | Implicite ; alias métier à formaliser |
| DECONTEXTUALIZATION_CONSIGNE | Consigne générique | Type/usage absent |
| DEEPENING_CONSIGNE | Consigne générique | Type/usage absent |
| DEMONSTRATION_CONSIGNE | Consigne générique | Type/usage absent |
| HOMEWORK_EXERCISE | EXERCISE dans le rendu historique | Objet/usage devoir absent |
| REACTIVATION_EXERCISE | Exercice ou consigne générique | Type et usage séparé absents |
| DEFINITION | Type accepté, création et rendu | Déjà supporté |
| PROPERTY | Type accepté, création et rendu | Déjà supporté |
| THEOREM | Pas dans BLOCK_TYPES | Absent du parcours authoring |
| FORMULA | Type accepté ; conservé dans le support | Déjà supporté ; rendu générique côté apprenant |
| METHOD | Type accepté, création et rendu | Déjà supporté |
| RULE | Pas dans BLOCK_TYPES | Absent du parcours authoring |
| REMARK | Type accepté et rendu dédié | Déjà supporté ; absent du petit sélecteur InstructionChoices, présent dans l'éditeur support |
| EXPECTED_RESPONSE | Type accepté, réservé enseignant à l'export | Déjà supporté |
| FIGURE | Type accepté, copie et rendu TikZ/image | Déjà supporté |

Les colonnes `resource_type` et `block_type` sont des chaînes SQL libres, mais l'API authoring valide une liste fermée. Les routes locales historiques acceptent des chaînes plus libres. Injecter un mot dans ces champs ne crée pas la capacité métier correspondante. Le type de la ressource créée par authoring est celui de son premier bloc : ce raccourci ne distingue pas le rôle « devoir » de la structure « consigne + figure + propriété ».

| Couche devoir | État constaté |
|---|---|
| Backend / DB | Aucun modèle/rôle HOMEWORK_EXERCISE, aucun usage CURRENT_NOTION/PRIOR_NOTION_REACTIVATION |
| Liens | Resource possède un niveau ; mappings vers plusieurs instructions ; connaissances reliées à une séquence. Pas de lien ressource–notions ni de contrat devoir–séquence indépendant des instructions |
| Source / validation | Version et provenance, statuts documentaires/mathématiques/pédagogiques et mapping réutilisables ; aucune règle de validation propre au devoir |
| API | ResourceCreate exige au moins une instruction ; le devoir cible accepte un lien instruction facultatif. Pas d'API d'affectation de devoir à séance |
| Frontend | Création de consignes/formulations ; aucun choix de devoir courant ou de réactivation |
| PDF | Peut imprimer un texte EXERCISE/APPLICATION ; aucune section devoir structurée ni distinction des usages |
| Tests | Tests de blocs/ressources présents ; aucun scénario de devoir/réactivation avec invariance du périmètre |

Il faut séparer l'affectation d'un devoir des segments curriculaires de la séance. Les ressources de réactivation pourront référencer des notions antérieures sans être ajoutées aux instructions courantes ni incrémenter leur couverture. Cette séparation est une recommandation, pas une propriété actuelle.

## I. DOCUMENTS USED DELTA

`SourcesPage` affiche « Sources distinctes utilisées » et déduplique les `file_name` avec un Set. L'entrée est **l'ensemble des ressources de bibliothèque affichées**, pas les sélections d'une fiche. Deux documents différents portant le même nom seraient fusionnés ; deux noms différents du même document resteraient séparés.

Les choix V2-03 conservent source/version dans `authoring_json`, et les ressources possèdent des occurrences. Il existe donc une base de provenance pour produire la liste. Il manque : résolution des documents des choix actifs réellement utilisés, déduplication par identité/version, ajouts manuels, snapshot par révision et section imprimée. Les anciennes copies masquées conservées lors d'un remplacement ne doivent pas contaminer cette liste.

Le PDF enseignant imprime une liste fixe de champs I/II puis le déroulement ; aucune section DOCUMENTS UTILISÉS n'existe (E09). Ajouter une clé libre aux métadonnées via API ne crée pas son export et n'est pas un substitut fonctionnel.

## J. ANNUAL PROGRESSION DELTA

`AnnualProgressionPlan` est absent des modèles, schémas, migrations et routes inspectés. L'écran « Progression pédagogique » représente les exécutions et une allocation normative globale, pas un calendrier annuel.

| Élément cible | Présence dans un plan annuel |
|---|---|
| class | Absente ; seuls niveau/libellés d'autres objets existent |
| school_year | Absente ; champ documentaire dans la fiche uniquement |
| week | Absente |
| SA | Pas de ligne de plan ; objet canonique disponible |
| sequence/notion | Pas de ligne de plan ; objets curriculum disponibles |
| planned_hours | Absentes par semaine ; allocation SA différente |
| integration period | Absente |
| assessment period | Absente |
| remediation | Absente |
| interruptions | Absentes |

Le plan doit référencer une version du curriculum sans modifier ses allocations ni ses séquences. Une progression institutionnelle versionnée, en tant que source d'autorité, est également absente des catégories d'authoring ; elle ne doit pas être confondue avec un plan local d'enseignant.

## K. LEARNER SUPPORT STATUS

**Capacités confirmées statiquement pour la copie V2-03 et les exports apprenant régénérés :**

- EXPECTED_RESPONSE et autres types réservés enseignant sont exclus, aussi bien en LEARNER_INITIAL qu'en LEARNER_COMPLETED.
- `expected_result_latex` du déroulement n'est pas copié au support.
- RESPONSE_SPACE/ANSWER_SPACE sont exclus ; le suffixe historique « Réponse : » suivi d'un espace vertical est retiré au rendu. Aucun grand espace de réponse n'est ajouté par défaut.
- Consignes, définitions, propriétés, formules et figures visibles sont conservées.

Les tests LEARNER et TEACHER d'E14 contiennent les assertions correspondantes. La paramétrisation d'export teste consigne/définition/propriété/figure ; la formule est testée comme type de ressource, mais mérite une assertion d'export dédiée lors d'une prochaine modification du rendu.

Limites : un texte de réponse volontairement mal typé comme consigne n'est pas détecté. Les fichiers PDF historiques ne sont pas réécrits. Certaines listes d'exclusion des parcours historiques (finalisation de support, support vers fiche) n'incluent pas EXPECTED_RESPONSE, contrairement au moteur d'export : la garantie observée porte sur le support copié par V2-03 et le contenu imprimé, pas sur l'impossibilité de stocker ce type dans tout brouillon historique. Pas de fuite PDF déduite de cette différence ; ne pas inventer un finding de fuite.

## L. AUTOMATIC COMPOSITION DELTA

**Réponse A/B : AUTO compose le périmètre d'instructions sélectionné.** Par défaut, l'UI sélectionne toutes les instructions de la séquence ; un sous-ensemble donne une fiche partielle. AUTO ne détermine pas ce sous-ensemble à partir d'un historique. Ce n'est donc pas un moteur de « prochaine séance ».

| Entrée / garantie cible | Traitement actuel |
|---|---|
| Instructions déjà couvertes/restantes | Aucune lecture des exécutions dans compose |
| Durée pédagogique disponible | Aucun paramètre numérique de budget dans Compose |
| Pause | Absente |
| Priorité des sources | Programme et guide rang 0, inspection 1, communauté 2, livre 3, local 4, démo 5 ; programme/guide non départagés et progression institutionnelle absente |
| Compatibilité notionnelle | Mapping instruction, même niveau, ressource AVAILABLE, mapping non rejeté/retiré ; pas de notion explicite ni validation sémantique du contenu |
| Sélection | Tirage parmi les candidats de meilleur rang, graine possible ; même ressource copiée une fois si choisie pour plusieurs instructions |
| Candidat absent | Refus avant création automatique ; ne livre pas silencieusement un périmètre amputé |
| Brouillon | DRAFT, modifiable ; finalisation explicite séparée |

Les mappages nouvellement créés sont `MANUAL_DECLARATION`. Les statuts de revue mathématique/pédagogique ne constituent pas un filtre général du moteur : compatibilité déclarée ne signifie pas validation notionnelle certifiée. Le refus de transformer une communauté en OFFICIAL et la non-modification du curriculum canonique restent des acquis distincts de la priorité documentaire incomplète.

## M. REQUIRED MIGRATIONS

Liste prospective minimale, sans exécution :

1. Ajouter le contexte classe/année et la séance planifiée liée à une séquence, puis le lien fiche/séance et le numéro dans ce contexte. Préserver le niveau curriculaire et les libellés de subdivision existants.
2. Permettre une couverture par instruction et exécution, avec contexte de classe/année et indication de partie/reliquat. Réutiliser les segments existants autant que possible.
3. Ajouter les durées numériques distinctes de séquence, créneau et pause ; calculer le temps pédagogique selon la règle retenue. Garder les valeurs documentaires historiques intactes.
4. Ajouter catalogue de compétences et applicabilités sourcées ; réutiliser les sources/versions existantes. Importer uniquement les libellés et correspondances validés.
5. Ajouter rôle devoir, liens aux notions et usages par séance. Étendre les types reconnus ; les colonnes actuelles sont des chaînes, donc tout ajout de type n'exige pas à lui seul une migration SQL.
6. Ajouter une liste de documents utilisés par révision avec entrées automatiques/manuelles. Un snapshot simple peut suffire pour le MVP ; ne pas créer un système documentaire complet.
7. Ajouter un plan annuel distinct et ses lignes/périodes, avec version et origine.

**Reprise des données :** ne pas déduire un numéro de séance du numéro de révision ou d'un identifiant de fiche. Ne pas convertir automatiquement DONE agrégé en COVERED. Les lignes d'exécution individuelles conservent encore leur statut, mais n'apportent pas forcément l'année ni la granularité nécessaires. Ne pas interpréter « 55 min » comme une preuve de pause nulle. Les cas ambigus restent historiques/non rattachés jusqu'à attribution explicite. Ne pas réécrire les révisions finalisées pour reconstituer des sources manquantes.

`0001_initial` utilise les modèles courants pour une installation vide ; `0002–0004` contiennent des contrôles de présence. Toute future migration devra être vérifiée séparément sur installation vide et sur ancienne base, sans reset de la base utilisateur. E13 et tests de migration consultés l'établissent ; aucun upgrade n'est lancé ici.

## N. REQUIRED UI CHANGES

- Choisir une classe/année et une séquence, afficher les séances existantes, proposer « Préparer la séance suivante » et le numéro attribué.
- Afficher NOT_STARTED/PARTIAL/COVERED par instruction ; permettre de sélectionner une partie et de déclarer un résultat distinct par instruction après exécution.
- Présenter séparément durée SA sourcée, durée prévue de séquence, créneau, pause et durée pédagogique calculée.
- Sélectionner les compétences applicables et montrer leur origine ; conserver les personnalisations explicitement distinguées.
- Ajouter les types manquants et un choix de devoir « notion courante / réactivation », sans ajouter les anciennes notions au périmètre courant.
- Ajouter DOCUMENTS UTILISÉS, liste automatique éditable par ajouts manuels, avec aperçu identique au PDF enseignant.
- Ajouter un écran simple de plan annuel séparé du suivi réalisé.
- Exposer le budget et les instructions retenues par AUTO avant finalisation ; le résultat reste un brouillon.

Conserver la sauvegarde centrale avant navigation/export/finalisation, l'erreur visible en cas d'échec et les protections contre doubles clics. Ne pas multiplier les étapes du wizard pour chaque donnée si un formulaire groupé suffit.

## O. REQUIRED TEST CHANGES

Tests à ajouter dans les missions d'implémentation, pas dans cet audit :

| Domaine | Contrôle métier nécessaire |
|---|---|
| Séances | Deux séances d'une séquence, numéros distincts, même classe/année ; réviser une fiche ne crée pas une séance supplémentaire |
| Couverture | NOT_STARTED → PARTIAL → COVERED ; SKIPPED ne termine rien ; états différents pour deux instructions de la même séance ; classes/années isolées |
| Reprise | Prochaine séance reprend le reliquat ; duplication indépendante n'avance pas implicitement la séquence |
| Durées | Créneau 120 min, pause 15 min, pédagogique 105 min ; budget dépassé détecté ; historique non interprété arbitrairement |
| Compétences | 8/6/3 seulement après corpus validé ; une identité globale réutilisée ; applicability et provenance conservées ; pas de propagation abusive d'un exemple |
| Sources | Programme avant guide avant progression institutionnelle avant inspection/communauté/livre/local ; une source basse ne remplace pas une prescription |
| Devoir | Plusieurs notions, instruction facultative, source/validation ; réactivation n'altère ni segments ni couverture courante ; rendu distinct |
| Documents | Deux ressources d'une source donnent une entrée ; deux versions restent distinguées ; ressource remplacée masquée exclue ; ajout manuel persisté après réouverture et révision, visible au PDF |
| Plan annuel | Classe/année/semaine, intégration/évaluation/remédiation/interruption ; modification du plan sans modification du curriculum |
| AUTO | Ignore COVERED, conserve PARTIAL, respecte budget/pause et priorité ; absence de candidat expliquée ; reste DRAFT |
| Non-régression | Sauvegarde avant navigation, classe compatible, copies et immutabilité, consignes/formules/figures conservées, réponses exclues des deux exports apprenant |
| Migration | Installation vide et base antérieure ; conservation des révisions/sources, rapport des rattachements ambigus |

Les tests existants `test_CURR_004_005...` prouvent l'héritage du pilote, pas le catalogue global. `test_RAND_002...` prouve officiel avant communauté, pas programme avant guide. Les tests AUTO de brouillon ne prouvent pas le calcul de prochaine séance. Les contrôles de progression historiques ne couvrent pas le faux achèvement PARTIAL/SKIPPED. Ces limites doivent guider les ajouts, sans refaire une campagne sans lien avec les changements.

## P. SAFE IMPLEMENTATION SEQUENCE

Chaque phase correspond à une mission séparée et bornée ; aucune n'est lancée par cet audit.

| Phase | Mission MVP | Critère de sortie |
|---|---|---|
| P0 | Vérifier les sources du catalogue 8/6/3, l'applicabilité, les durées et la progression institutionnelle | Tableau sourcé validé ; ambiguïtés explicites, aucun contenu inventé |
| P1 | Introduire séance/classe/année, numéro, couverture par instruction et reprise manuelle | Deux séances successives ; PARTIAL/SKIPPED exacts ; aucune contamination interclasses |
| P2 | Distinguer les cinq durées | Calcul créneau moins pause correct ; durée SA et séquence séparées |
| P3 | Catalogue/applicabilités et priorité documentaire | Identités réutilisées, valeurs sourcées, sept rangs explicites ; conserver overrides |
| P4 | Typologie minimale et devoirs avec réactivation | Devoir relié aux notions, rendu et usage sans changer le périmètre |
| P5 | Documents utilisés par fiche | Liste des choix actifs dédupliquée, ajouts manuels, persistance et PDF |
| P6 | Plan annuel séparé | Une classe/année, lignes hebdomadaires et périodes, sans mutation canonique |
| P7 | AUTO prochaine séance | Couverture fiable + budget + priorité ; brouillon explicable, finalisation humaine |

P7 dépend au minimum de P1–P3 ; P4 doit précéder son éventuelle sélection de devoirs. P6 reste séparé et ne doit pas être un prétexte à refondre le moteur de fiches. Au sein de chaque phase, limiter la première mission à un scénario pilote vérifiable, puis élargir sur preuve.

### Bilan

Les compteurs ci-dessous comptent uniquement R01–R41, pas les sous-champs ni les tableaux de détail. Les dix findings MAJOR regroupent les écarts sans compter plusieurs fois une même cause. UNCERTAIN porte sur la preuve documentaire externe ; sa localisation et son impact sont cartographiés, sans certification implicite.

TOTAL_REQUIREMENTS = 41

ALREADY_SUPPORTED = 9

PARTIAL = 13

MISSING = 15

CONFLICT = 3

UNCERTAIN = 1

BLOCKING_FINDINGS = 0

MAJOR_FINDINGS = 10

MINOR_FINDINGS = 0

RECOMMENDED_IMPLEMENTATION_PHASES = 8 (P0–P7)

NO_CODE_CHANGED = YES

V2_03_R1_DELTA_AUDIT = PASS
