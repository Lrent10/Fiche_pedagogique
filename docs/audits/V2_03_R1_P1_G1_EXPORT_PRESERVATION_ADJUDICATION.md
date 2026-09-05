# V2-03-R1-P1-G1 — Export preservation adjudication

Date : 2026-09-04. Projet : Fiche_pedagogique / FicheMaths.
Finding unique : **P1-HIST-EXPORT-001**. Mission parente : V2-03-R1-P1, verdict **FAIL maintenu**.

## 1. Conclusion et limite de preuve

**OPEN — HUMAN_ARBITRATION_REQUIRED = YES.** Aucune copie certaine de l'état antérieur des quatre PDF r1 ou de leurs journaux n'a été retrouvée dans le périmètre accessible inspecté. Aucune restauration exacte ni clôture automatique n'est justifiée.

Les fichiers courants sont des dérivés générés, avec une provenance QA/démonstration identifiable. Leur contenu antérieur reste inconnu : la nature générée actuelle ne permet pas d'exclure une ancienne valeur utilisateur. La classification C ci-dessous décrit les fichiers courants et la recherche, pas une certification de préservation historique.

G1 n'a lancé aucun test, serveur, migration, import applicatif ou génération PDF ; aucune connexion à la base métier n'a été ouverte. Les PDF ont été lus par pdfinfo et pdftotext vers la sortie standard. Les bases locales ont uniquement été lues comme fichiers pour leur empreinte d'intégrité.

## 2. Baseline gate

Racine vérifiée : `C:\Users\HP\Documents\ChatGPT\Fiche_pedagogique`.
Branche : `fix/ux-bb-001-identification-navigation`.
HEAD : `578b2a4b49e8284f1885693e368554762bc62e25`.

Contrôles initiaux : git branch --show-current, git rev-parse HEAD, git status, git diff --check. Gate conforme ; diff --check : code 0, avertissements de normalisation LF/CRLF uniquement. Le travail P1 est présent et non commité. Aucun nettoyage, checkout, commit ni réparation.

Fichiers suivis déjà modifiés : backend/app/{authoring.py,exporter.py,main.py,models.py,services.py}, backend/tests/{conftest.py,test_e2e_001.py,test_v2_03_migration.py}, frontend/src/{App.test.tsx,App.tsx,styles.css,types.ts}.

Fichiers déjà non suivis : backend/alembic/versions/0005_planned_sessions.py ; backend/app/sessions.py ; backend/tests/test_planned_migration.py ; backend/tests/test_planned_sessions.py ; frontend/src/Sessions.test.tsx ; frontend/src/Sessions.tsx ; docs/audits/V2_03_R1_FUNCTIONAL_DELTA_AUDIT.md ; docs/audits/V2_03_R1_P0_HUMAN_ARBITRATIONS_AND_P1_SCOPE.md ; docs/audits/V2_03_R1_P0_SOURCE_GROUNDED_BUSINESS_RULES.md ; docs/audits/V2_03_R1_P1_IMPLEMENTATION_REPORT.md.

## 3. Inventaire exact et table de décision

Tous les huit fichiers existent. Tailles en octets ; CURRENT_TIMESTAMP = dernière modification UTC. Les dates de création sont indiquées séparément. Les dates ne constituent pas une preuve autonome d'intégrité historique.

C = GENERATED_ARTIFACT_NO_PRIOR_COPY_FOUND.
PROVENANCE P1 à P4 : voir section 4 ; pour chaque log, journal technique associé au PDF du même nom.
PRIOR_COPY_FOUND désigne exclusivement une copie antérieure certaine du même artefact ; les candidats postérieurs/r2 sont inventoriés en section 5.
Risque H = contenu antérieur non prouvé, ancienne valeur utilisateur non exclue.
Action R = conserver en place, aucune restauration spéculative, demander l'arbitrage de la section 7.

| FILE | CURRENT_SHA256 | CURRENT_SIZE | CURRENT_TIMESTAMP | GIT_TRACKED | GENERATED_OR_AUTHORITATIVE | PRIOR_COPY_FOUND | PRIOR_COPY_SHA256 | PROVENANCE | CLASSIFICATION | PRESERVATION_RISK | RECOMMENDED_ACTION |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| exports/fiche_enseignant_FICHE-4E-003_r1.pdf | `f14c9ca76ce8f09556ced72e371237d0bad05fd1e8bb3892ae17d7d80ae6e0da` | 74713 | 2026-09-04T14:37:49.853832+00:00 | NO, ignoré | GENERATED DERIVATIVE / QA ARTIFACT | NO | N/A | P1 | C | H | R |
| exports/fiche_enseignant_FICHE-4E-003_r1.log | `272ad6356d1b6b70a23b25e5c6bfb380a8d89df423f54acb92a6b053d1511a8b` | 1030 | 2026-09-04T14:37:49.936610+00:00 | NO, ignoré | GENERATED DERIVATIVE / QA LOG | NO | N/A | P1 | C | H | R |
| exports/fiche_apprenant_initiale_SUPPORT-4E-002_r1.pdf | `73165cab6b9ed2c3af181f413a6d839fe8ead22a286025db97f82ba77f8ebf61` | 53768 | 2026-09-04T14:37:47.970272+00:00 | NO, ignoré | GENERATED DERIVATIVE / QA ARTIFACT | NO | N/A | P2 | C | H | R |
| exports/fiche_apprenant_initiale_SUPPORT-4E-002_r1.log | `a50ad3bd39098ebc586fb96e51030d43a2b6116d9c3acd6eb70c402c09363e7f` | 1031 | 2026-09-04T14:37:48.081516+00:00 | NO, ignoré | GENERATED DERIVATIVE / QA LOG | NO | N/A | P2 | C | H | R |
| exports/fiche_apprenant_completee_SUPPORT-4E-002_r1.pdf | `2877812ce9f8464dbe3ab7e3ac48c4bd89855a189592485f79ef786db5ab7b25` | 73014 | 2026-09-04T14:37:20.922896+00:00 | NO, ignoré | GENERATED DERIVATIVE / QA ARTIFACT | NO | N/A | P3 | C | H | R |
| exports/fiche_apprenant_completee_SUPPORT-4E-002_r1.log | `1fc294d264da9fccd47aca85fb550cae6781483b2837d050daf09c0d1e245587` | 1028 | 2026-09-04T14:37:21.035661+00:00 | NO, ignoré | GENERATED DERIVATIVE / QA LOG | NO | N/A | P3 | C | H | R |
| exports/fiche_enseignant_FICHE-DEMO-001_r1.pdf | `c15b25837a9ee5078d386d36908039a946eec7c630947f3c5a79371c8e867aa8` | 97841 | 2026-09-04T14:37:09.288580+00:00 | NO, ignoré | GENERATED DERIVATIVE / QA ARTIFACT | NO | N/A | P4 | C | H | R |
| exports/fiche_enseignant_FICHE-DEMO-001_r1.log | `c181c13bdb9b32cbe93438a4be29690b3c831e35e236daee428a643c6daf052e` | 1028 | 2026-09-04T14:37:09.424551+00:00 | NO, ignoré | GENERATED DERIVATIVE / QA LOG | NO | N/A | P4 | C | H | R |

| FILE | EXISTS | CREATED_UTC | IGNORE_RULE |
| --- | --- | --- | --- |
| exports/fiche_enseignant_FICHE-4E-003_r1.pdf | YES | 2026-08-28T13:39:23.407870+00:00 | .gitignore:19 — exports/*.pdf |
| exports/fiche_enseignant_FICHE-4E-003_r1.log | YES | 2026-08-28T13:39:23.407870+00:00 | .gitignore:20 — exports/*.log |
| exports/fiche_apprenant_initiale_SUPPORT-4E-002_r1.pdf | YES | 2026-08-28T17:07:43.428399+00:00 | .gitignore:19 — exports/*.pdf |
| exports/fiche_apprenant_initiale_SUPPORT-4E-002_r1.log | YES | 2026-08-28T17:07:43.432885+00:00 | .gitignore:20 — exports/*.log |
| exports/fiche_apprenant_completee_SUPPORT-4E-002_r1.pdf | YES | 2026-08-28T17:07:44.246339+00:00 | .gitignore:19 — exports/*.pdf |
| exports/fiche_apprenant_completee_SUPPORT-4E-002_r1.log | YES | 2026-08-28T17:07:44.246339+00:00 | .gitignore:20 — exports/*.log |
| exports/fiche_enseignant_FICHE-DEMO-001_r1.pdf | YES | 2026-08-28T17:49:18.963052+00:00 | .gitignore:19 — exports/*.pdf |
| exports/fiche_enseignant_FICHE-DEMO-001_r1.log | YES | 2026-08-28T17:49:18.967079+00:00 | .gitignore:20 — exports/*.log |

Aucune version PDF/log trouvée dans l'historique local accessible : `git log --all --format= --name-only -- 'exports/*.pdf' 'exports/*.log'` ne renvoie rien. L'historique du dossier exports contient des sources .tex ; il ne constitue pas une sauvegarde des PDF ignorés.

Les dates de création Windows sont du 28 août, les dates de modification du 4 septembre vers 14:37 UTC (16:37 à Paris). C'est cohérent avec l'incident déclaré dans le rapport P1, section I ; cela ne révèle pas les anciens octets. Les empreintes courantes concordent avec l'inventaire du rapport P1.

## 4. Nature des données et reproductibilité

Distinctions appliquées :
- **AUTHORITATIVE SOURCE DATA** : textes et références sources, dont l'autorité dépend de leur provenance ; aucun PDF QA n'acquiert ce statut par son nom.
- **PERSISTED BUSINESS DATA** : fiches, supports, révisions et saisies conservés en base. Persister une fixture dans une base de test ne la transforme pas en donnée utilisateur.
- **GENERATED DERIVATIVE** : PDF compilé à partir d'un détail de révision ; log associé.
- **QA ARTIFACT** : export issu de scénarios de test ou de démonstration.

| Provenance | PDF courant : preuve extraite | Source applicative correspondante | Reproduction et limite |
| --- | --- | --- | --- |
| P1 | FICHE-4E-003 r1, 1 page ; « Séance V2 - test », CEG_TEST_EXPORT_987, PROF_TEST_EXPORT_654, RESULTAT_PDF_MANUEL_456 ; métadonnée de création 2026-09-04 16:37:49 Paris | backend/tests/test_v2_document_workflow.py, test_wf_001_support_to_sheet_manual_result_finalize_and_export, notamment lignes 155–181 | Scénario QA reconstructible à partir des fixtures et du moteur ; pas de garantie d'identité binaire ni de restauration historique |
| P2 | SUPPORT-4E-002 initial r1, 1 page ; « Support V2 - test », parcelle de Fofo ; création PDF 16:37:47 Paris | backend/tests/test_v2_document_workflow.py, helpers de création du support et test_doc_009_and_010_exports_keep_exact_revisions | Même limite ; l'existence actuelle de cette révision dans la base métier n'a pas été contrôlée |
| P3 | SUPPORT-4E-002 complété r1, 1 page ; « E2E — support apprenant », produits remarquables ; création PDF 16:37:19 Paris | backend/tests/test_e2e_001.py, création puis exports du support E2E | Scénario distinct de P2 ; même code/révision réutilisé après réinitialisation de la base de test, donc pas une preuve d'identité métier commune |
| P4 | FICHE-DEMO-001 r1, 2 pages ; Collège et Enseignant de démonstration, classe 4e M1 ; création PDF 16:37:05 Paris | backend/app/seed.py (FICHE-DEMO-001) ; backend/tests/test_curriculum_level_invariant.py, test_007_to_010_valid_subdivision_changes_document_only, lignes 55–108 | Démonstration modifiée par le test de subdivision de classe ; date et compilation peuvent varier |

Tous les PDF indiquent Creator TeX et Producer MiKTeX pdfTeX-1.40.28, sans formulaire, chiffrement ni JavaScript. Les logs sont des sorties techniques de compilation.

Le chemin de production est identifiable dans backend/app/exporter.py : export_document (ligne 344) construit le PDF depuis la révision demandée ; la destination utilise settings.export_dir (ligne 360), avec log associé. Cela rend le **contenu QA reconstructible en principe**, sous réserve des mêmes entrées et dépendances. Cela ne démontre ni la présence des anciennes données dans la base métier actuelle, ni la reproductibilité bit à bit des PDF, ni l'identité des contenus avant incident. Aucune reconstruction n'a été exécutée en G1.

## 5. Recherche des copies antérieures

Recherche locale en lecture seule par identifiants de fiche/support, noms de PDF/log/TeX, rapports/audits et manifestes ZIP. Première passe : 5 261 fichiers distincts parcourus dans les racines accessibles, hors répertoires techniques exclus. Les 28 candidats sont les 8 fichiers courants, 4 fichiers r2 et 16 fichiers QA postérieurs.

Racines inspectées :
- `C:\Users\HP\Documents\ChatGPT\Fiche_pedagogique`
- `C:\Users\HP\Documents`
- `C:\Users\HP\Desktop`
- `C:\Users\HP\Downloads`
- `C:\Users\HP\AppData\Local\Temp`
- `C:\Users\HP\OneDrive`
- `C:\Projets`
- `C:\home`
- `C:\Users\HP\.codex\worktrees`
- `C:\Users\HP\.codex\outputs`
- `C:\Users\HP\.codex\visualizations`

Exclusions de parcours : .git, node_modules, .venv, __pycache__, .next, Cache, Code Cache, GPUCache. Git est interrogé séparément. Au total, **56 manifestes ZIP** ont été inspectés sans extraction : aucun membre correspondant aux identifiants ciblés ni entrée Fiche_pedagogique identifiée. Aucun ZIP de sauvegarde probant du projet trouvé.

Limites : accès refusé aux jonctions Documents/Ma musique, Mes images, Mes vidéos et aux dossiers temporaires msdtadmin, WinSAT. Pas de recherche distante, de récupération de fichiers supprimés, de clichés VSS, de sauvegardes hors des racines listées ou de volumes WSL. Une copie renommée sans identifiant reconnaissable ou une archive imbriquée n'est pas exclue. Le résultat est « aucune copie antérieure prouvée dans ce périmètre », pas « aucune copie n'existe ».

### Candidats hors fichiers courants

Les chemins ci-dessous sont absolus. La comparaison SHA porte sur les octets ; une homonymie ne vaut pas identité.

| CANDIDATE | SIZE | MODIFIED_UTC | SHA256 | ADJUDICATION |
| --- | ---: | --- | --- | --- |
| C:\Users\HP\Documents\ChatGPT\Fiche_pedagogique\exports\fiche_apprenant_completee_SUPPORT-4E-002_r2.log | 1028 | 2026-08-28T17:55:20.870Z | `a0e480832962bd0b02275093123ef3645367c2ceb159262c5adb87af5c153b65` | Révision r2 datée du 28 août ; artefact différent, pas copie du r1 |
| C:\Users\HP\Documents\ChatGPT\Fiche_pedagogique\exports\fiche_apprenant_completee_SUPPORT-4E-002_r2.pdf | 88410 | 2026-08-28T17:55:20.818Z | `6eca7fe0c292447cddd95287dfbbc65ddaffd480caaf0dbc29b79e5787374ab4` | Révision r2 datée du 28 août ; artefact différent, pas copie du r1 |
| C:\Users\HP\Documents\ChatGPT\Fiche_pedagogique\exports\fiche_apprenant_initiale_SUPPORT-4E-002_r2.log | 1028 | 2026-08-28T17:55:14.405Z | `f10da4ae7e8f695e01dabf542e1fb5c9e913704268eeebdc2534389648c362b8` | Révision r2 datée du 28 août ; artefact différent, pas copie du r1 |
| C:\Users\HP\Documents\ChatGPT\Fiche_pedagogique\exports\fiche_apprenant_initiale_SUPPORT-4E-002_r2.pdf | 87649 | 2026-08-28T17:55:14.344Z | `43cb3812e7fa09743944edb0051aaec4ea9baa6fc3c43a91b5644288043e44ae` | Révision r2 datée du 28 août ; artefact différent, pas copie du r1 |
| C:\Users\HP\AppData\Local\Temp\fichemaths_tests_keufuj44\exports\fiche_apprenant_completee_SUPPORT-4E-002_r1.log | 1028 | 2026-09-04T14:54:26.035Z | `1fc294d264da9fccd47aca85fb550cae6781483b2837d050daf09c0d1e245587` | Campagne QA postérieure à 14:37 UTC ; pas état antérieur |
| C:\Users\HP\AppData\Local\Temp\fichemaths_tests_keufuj44\exports\fiche_apprenant_completee_SUPPORT-4E-002_r1.pdf | 73014 | 2026-09-04T14:54:25.966Z | `5db217a9c3300b2bbb42332d27c0c3f7ff855290b3750fc2599333884ab0be56` | Campagne QA postérieure à 14:37 UTC ; pas état antérieur |
| C:\Users\HP\AppData\Local\Temp\fichemaths_tests_keufuj44\exports\fiche_apprenant_initiale_SUPPORT-4E-002_r1.log | 1031 | 2026-09-04T14:54:51.755Z | `a50ad3bd39098ebc586fb96e51030d43a2b6116d9c3acd6eb70c402c09363e7f` | Campagne QA postérieure à 14:37 UTC ; pas état antérieur |
| C:\Users\HP\AppData\Local\Temp\fichemaths_tests_keufuj44\exports\fiche_apprenant_initiale_SUPPORT-4E-002_r1.pdf | 53768 | 2026-09-04T14:54:51.690Z | `73e07e8615097cad1e2fdd184ed94953c9ba1c4334155ecadfb2b86d26f47b94` | Campagne QA postérieure à 14:37 UTC ; pas état antérieur |
| C:\Users\HP\AppData\Local\Temp\fichemaths_tests_keufuj44\exports\fiche_enseignant_FICHE-4E-003_r1.log | 1030 | 2026-09-04T14:54:52.823Z | `272ad6356d1b6b70a23b25e5c6bfb380a8d89df423f54acb92a6b053d1511a8b` | Campagne QA postérieure à 14:37 UTC ; pas état antérieur |
| C:\Users\HP\AppData\Local\Temp\fichemaths_tests_keufuj44\exports\fiche_enseignant_FICHE-4E-003_r1.pdf | 74713 | 2026-09-04T14:54:52.755Z | `df374e7f5a0eda83cf1426bf2bfe1074dcd49dd8b977f705f0f29a5573722b46` | Campagne QA postérieure à 14:37 UTC ; pas état antérieur |
| C:\Users\HP\AppData\Local\Temp\fichemaths_tests_keufuj44\exports\fiche_enseignant_FICHE-DEMO-001_r1.log | 1028 | 2026-09-04T14:54:21.750Z | `c181c13bdb9b32cbe93438a4be29690b3c831e35e236daee428a643c6daf052e` | Campagne QA postérieure à 14:37 UTC ; pas état antérieur |
| C:\Users\HP\AppData\Local\Temp\fichemaths_tests_keufuj44\exports\fiche_enseignant_FICHE-DEMO-001_r1.pdf | 97841 | 2026-09-04T14:54:21.704Z | `66386f54092bdf04cc5b28498a456b7e66ead5ae7f91d0610e0652d859bd7255` | Campagne QA postérieure à 14:37 UTC ; pas état antérieur |
| C:\Users\HP\AppData\Local\Temp\fichemaths_test_exports_qc7h6cs2\fiche_apprenant_completee_SUPPORT-4E-002_r1.log | 1028 | 2026-09-04T14:49:59.159Z | `1fc294d264da9fccd47aca85fb550cae6781483b2837d050daf09c0d1e245587` | Campagne QA postérieure à 14:37 UTC ; pas état antérieur |
| C:\Users\HP\AppData\Local\Temp\fichemaths_test_exports_qc7h6cs2\fiche_apprenant_completee_SUPPORT-4E-002_r1.pdf | 73014 | 2026-09-04T14:49:59.091Z | `1ac30ff4b7771577ffa803ce50e525a52470c2e36c87bab1af92686187a031ca` | Campagne QA postérieure à 14:37 UTC ; pas état antérieur |
| C:\Users\HP\AppData\Local\Temp\fichemaths_test_exports_qc7h6cs2\fiche_apprenant_initiale_SUPPORT-4E-002_r1.log | 1031 | 2026-09-04T14:50:23.498Z | `a50ad3bd39098ebc586fb96e51030d43a2b6116d9c3acd6eb70c402c09363e7f` | Campagne QA postérieure à 14:37 UTC ; pas état antérieur |
| C:\Users\HP\AppData\Local\Temp\fichemaths_test_exports_qc7h6cs2\fiche_apprenant_initiale_SUPPORT-4E-002_r1.pdf | 53768 | 2026-09-04T14:50:23.442Z | `4b62eadc0230ca20834ff100e586be4f937355a23029c0385ccc68ef59811242` | Campagne QA postérieure à 14:37 UTC ; pas état antérieur |
| C:\Users\HP\AppData\Local\Temp\fichemaths_test_exports_qc7h6cs2\fiche_enseignant_FICHE-4E-003_r1.log | 1030 | 2026-09-04T14:50:24.471Z | `272ad6356d1b6b70a23b25e5c6bfb380a8d89df423f54acb92a6b053d1511a8b` | Campagne QA postérieure à 14:37 UTC ; pas état antérieur |
| C:\Users\HP\AppData\Local\Temp\fichemaths_test_exports_qc7h6cs2\fiche_enseignant_FICHE-4E-003_r1.pdf | 74713 | 2026-09-04T14:50:24.415Z | `673857d541b1527b9f895469444167439e502f2e0ec71e9309af397fe84b49d9` | Campagne QA postérieure à 14:37 UTC ; pas état antérieur |
| C:\Users\HP\AppData\Local\Temp\fichemaths_test_exports_qc7h6cs2\fiche_enseignant_FICHE-DEMO-001_r1.log | 1028 | 2026-09-04T14:49:54.970Z | `c181c13bdb9b32cbe93438a4be29690b3c831e35e236daee428a643c6daf052e` | Campagne QA postérieure à 14:37 UTC ; pas état antérieur |
| C:\Users\HP\AppData\Local\Temp\fichemaths_test_exports_qc7h6cs2\fiche_enseignant_FICHE-DEMO-001_r1.pdf | 97841 | 2026-09-04T14:49:54.908Z | `be8f1aaafec68c179a65cc6d16e5e2fd31a2bd7424829d08d74d85e9084904db` | Campagne QA postérieure à 14:37 UTC ; pas état antérieur |

Les deux PDF r2 portent « Support apprenant — produits remarquables » et des métadonnées du 28 août à 19:55 Paris. Leur révision différente et leur contenu distinct interdisent de les utiliser comme restauration des r1. Ils ne justifient pas la classe B pour les fichiers ciblés.

Les campagnes fichemaths_test_exports_qc7h6cs2 (14:49–14:50 UTC) et fichemaths_tests_keufuj44 (14:54 UTC) sont postérieures à l'incident. Les quatre PDF de chaque campagne ont des SHA différents des courants ; les logs correspondants sont identiques aux logs courants. Même une identité de log postérieur ne prouve aucun état antérieur. Aucune de ces copies ne permet les CASE 1 ou CASE 2.

Les rapports/audits locaux identifient l'incident et les vérifications P1, mais aucun manifeste antérieur des huit fichiers ni copie certaine permettant une restitution exacte n'a été trouvé. Les tests historiques cités par P1 n'ont pas été rejoués en G1.

## 6. Vérification de l'isolation P1

**Vérification statique conforme pour la suite actuelle lancée dans un processus neuf par le parcours normal.**

backend/tests/conftest.py, lignes 9–15 :
- tempfile.mkdtemp(prefix="fichemaths_tests_") réserve un répertoire unique par campagne ;
- DATABASE_URL pointe vers tests.db dans ce répertoire ;
- EXPORT_DIR pointe vers son sous-dossier exports ;
- les variables sont fixées avant l'import de app.database, app.main et du seed ;
- la fixture autouse réinitialise les tables de cette base temporaire pour chaque test.

backend/app/config.py lit ces paramètres depuis l'environnement ; la valeur par défaut exports du dépôt est donc remplacée. export_document utilise settings.export_dir pour le PDF et son log. Le test appelant directement compile_pdf dans backend/tests/test_latex_export.py passe tmp_path/tikz.pdf. L'inspection des tests ne révèle pas de destination PDF codée vers exports du dépôt. scripts/test-all.ps1 lance pytest dans un nouveau processus ; les répertoires QA postérieurs observés corroborent la destination isolée.

Conséquence pour ce parcours : base propre et dossier d'exports propres par campagne, aucune écriture de ces exports dans le dossier utilisateur, aucune collision avec les noms utilisateur même si les fixtures réutilisent les mêmes codes. Cette conclusion ne couvre pas un lancement arbitraire préimportant l'application avant conftest, une future modification non revue, ni une exécution normale de l'application hors tests.

Aucun test de confirmation supplémentaire n'était nécessaire ; aucun test n'a été exécuté en G1. L'isolation corrigée empêche la répétition par la suite examinée mais ne répare pas la preuve historique manquante.

## 7. Arbitrage humain requis

CASE 1 : non satisfait, aucune copie antérieure certaine identique.
CASE 2 : non satisfait, aucune copie antérieure certaine permettant une restauration exacte.
Aucune restauration n'est proposée.

Décision explicite proposée, **non prise et non appliquée** :

`ACCEPT_CURRENT_EXPORTS_AS_NON_AUTHORITATIVE_DERIVATIVES`

Cette décision signifierait exactement :
- les quatre PDF courants sont acceptés comme exports générés ;
- aucune prétention n'est faite sur leur contenu antérieur ;
- aucune donnée métier/source n'est considérée perdue ;
- l'incident est documenté ;
- l'isolation corrigée devient obligatoire ;
- la P1 peut être réauditée pour PASS après cette acceptation.

La troisième conséquence est une convention d'adjudication acceptée par l'utilisateur, pas une preuve technique de l'absence de contenu historique utile. La reconstruction depuis les fixtures n'établit pas une restauration depuis des données métier de production persistées. Les logs restent des dérivés techniques, conservés avec leurs empreintes ; cette décision n'autorise pas leur suppression ni la réécriture des fichiers.

En attendant une acceptation explicite, le finding reste OPEN et le verdict parent reste FAIL. Une acceptation permettrait une nouvelle adjudication puis un réaudit P1 ; elle ne vaut pas PASS automatique de P1 et n'autorise aucune mutation implicite.

## 8. Préservation et contrôles de clôture G1

Le seul fichier créé pour G1 est ce rapport. Le contrôle final compare les SHA-256 des fichiers suivis/non suivis présents au début, ceux des bases data/*.db et, pour les huit exports, existence, taille, création, modification et SHA-256. Les heures d'accès ne sont pas utilisées : la lecture peut être gérée par le système de fichiers. Aucun timestamp n'est volontairement modifié.

VERIFICATION_FINALE : conforme. Les 129 fichiers de l'instantané initial ont conservé leur SHA-256 ; aucun écart d'existence, taille, création, modification ou SHA-256 sur les huit exports. Seul ajout détecté : ce rapport. La base data/app.db conserve le SHA-256 `843fd91d04eaf79338f23ac3d2d18d05c197228f85b018213be45b0d1021d793`. Le rapport P1 reste inchangé. Branche et HEAD inchangés ; git diff --check termine avec code 0 (avertissements LF/CRLF seulement).

## 9. Verdict

```text
P1_HIST_EXPORT_001 = OPEN
HUMAN_ARBITRATION_REQUIRED = YES
FUNCTIONAL_P1_CODE_CHANGED = NO
DATABASE_CHANGED = NO
EXPORT_FILES_CHANGED = NO
```

## 10. Addendum — arbitrage humain explicite du 2026-09-04

L'utilisateur a explicitement accepté `ACCEPT_CURRENT_EXPORTS_AS_NON_AUTHORITATIVE_DERIVATIVES` après remise du présent rapport. Cet addendum remplace uniquement le statut OPEN/HUMAN_ARBITRATION_REQUIRED du verdict initial ; il conserve les constats et l'incident documentés ci-dessus.

Conséquences acceptées : les quatre PDF courants sont des artefacts générés non autoritatifs ; aucune prétention n'est faite sur leur contenu antérieur ; aucune donnée métier persistée, source officielle ou donnée autoritative n'est considérée perdue du seul fait de cet incident. L'incident reste documenté. L'isolation des tests devient une exigence permanente : aucune campagne ne doit écrire dans le dossier exports utilisateur ou courant. Aucune restauration spéculative, suppression ou réécriture des PDF/log n'est demandée. Cette acceptation ne constitue pas à elle seule un PASS de P1.

**P1_HIST_EXPORT_001 = CLOSED_BY_HUMAN_ARBITRATION**

Clôture par décision humaine, sans preuve nouvelle de l'ancien contenu et sans mutation des exports. Le verdict P1 reste soumis au réaudit final ciblé, documenté séparément dans `V2_03_R1_P1_FINAL_TARGETED_REAUDIT.md`. Aucun push, merge, tag ni modification de la base de travail n'est autorisé par cet addendum.
