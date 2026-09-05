# V2-03-R1-P1 — Réaudit final ciblé après arbitrage humain

Date : 2026-09-04. Périmètre : code P1 existant, migration 0005, suites complètes, T01–T22, isolation et conservation. Aucun développement fonctionnel.

**P1_HIST_EXPORT_001 = CLOSED_BY_HUMAN_ARBITRATION**
**V2_03_R1_P1 = PASS**

Ce verdict remplace le FAIL global historique du rapport d'implémentation, après clôture du finding par décision humaine puis succès des contrôles ci-dessous. Il n'atteste pas les anciens contenus des quatre PDF, ne déploie pas P1 et ne migre pas la base de travail.

## 1. Arbitrage et baseline

L'utilisateur a explicitement accepté `ACCEPT_CURRENT_EXPORTS_AS_NON_AUTHORITATIVE_DERIVATIVES`. L'addendum §10 de `V2_03_R1_P1_G1_EXPORT_PRESERVATION_ADJUDICATION.md` enregistre la clôture formelle. L'incident reste documenté ; aucune restauration, suppression ou réécriture des quatre PDF/log n'a été réalisée. Aucune donnée métier persistée, source officielle ou donnée autoritative n'est considérée perdue du seul fait de cet incident, conformément à l'arbitrage, sans prétention sur l'ancien contenu.

Racine : `C:/Users/HP/Documents/ChatGPT/Fiche_pedagogique`.
Branche : `fix/ux-bb-001-identification-navigation`.
HEAD : `578b2a4b49e8284f1885693e368554762bc62e25`.
Travail P1 présent, non commité ; aucune opération Git de publication.

Gate exécuté avant modification : racine, branche, HEAD, statut et diff --check. Aucun écart de baseline.
Les 129 empreintes conservées lors de G1, couvrant le code P1 déjà rapporté, les tests, migrations, documents initiaux et data/app.db, concordaient intégralement au début de ce réaudit. Le rapport P1 avait toujours l'empreinte `4fde8adca59732212a180a361f6481dc44bf1bfa364c8463fc0030f531b3cb80` avant son nouvel addendum. Aucune modification fonctionnelle depuis l'état P1 examiné dans G1 n'est détectée.

Une nouvelle capture de 198 fichiers a précédé les campagnes : fichiers suivis/non suivis et tous les fichiers sous exports/ et data/. Elle relève SHA-256, taille, dates de création et modification à la précision fournie par Windows. La référence G1 est une preuve de continuité dans cette mission, pas un commit du code P1 non commité.

## 2. Résultats réellement rejoués

| Contrôle | Résultat actuel | Preuve |
| --- | --- | --- |
| Backend complet | **110 passed in 38.39s** ; 0 échec, 0 erreur, 0 ignoré | backend.xml et backend.log de cette campagne |
| Frontend complet | **51 passed**, 4 fichiers ; 0 échec, 0 erreur, 0 ignoré | frontend.xml et frontend.log ; Vitest 2,55 s |
| Build | **PASS**, TypeScript puis Vite ; code 0 | build.log ; 36 modules, build Vite 3,45 s |
| Migration 0005 | **PASS** sur installation vide et fixture historique 0004 | Les deux variantes T13 réussies ; lecture ultérieure des deux bases jetables : version 0005_planned_sessions et foreign_key_check vide |
| Code P1 inchangé | **PASS** | Empreintes G1 puis comparaison de début/fin de campagne |
| Isolation des exports | **PASS** | Vérification des chemins à l'exécution avant les tests, puis comparaison du dossier utilisateur |
| Conservation | **PASS dans les limites de l'arbitrage** | 73 fichiers protégés exports/data inchangés ; T13/T14/T17 rejoués |
| git diff --check | **PASS**, code 0 | Avertissements LF/CRLF uniquement ; aucun défaut de whitespace |

Avertissement non bloquant du build : bundle JavaScript d'environ 523,52 kB, au-dessus du seuil indicatif 500 kB. Aucun refactoring n'a été entrepris.

## 3. Migration et isolation

La migration `0005_planned_sessions` a pour parent `0004_curriculum_authoring`. Lecture du code : tables class_contexts, sequence_plans et planned_sessions ; lien nullable planned_session_id sur teaching_sessions ; ajout natif sur SQLite, sans backfill de l'historique. Downgrade explicitement refusé.

T13 compare avant/après les lignes des tables historiques de sa fixture, dont révisions, JSON, statuts DONE/PARTIAL/SKIPPED, segments, sources et attributs curriculaires. Les liens historiques restent NULL. La création de la fixture et ses reconstructions sont limitées aux bases jetables. **Aucun upgrade, stamp, reset ni connexion applicative à data/app.db.** PostgreSQL n'est pas couvert.

Le lanceur temporaire place TEMP/TMP et les paramètres de repli DATABASE_URL/EXPORT_DIR sous :
`C:\Users\HP\AppData\Local\Temp\fichemaths_p1_final_ir311is4`.

La fixture P1 inchangée réserve ensuite un dossier unique. Le contrôle exécuté après collecte, avant les fixtures de test, a confirmé :
- DATABASE : `C:\Users\HP\AppData\Local\Temp\fichemaths_p1_final_ir311is4\fichemaths_tests_4ca7mcir\tests.db`
- EXPORT_DIR : `C:\Users\HP\AppData\Local\Temp\fichemaths_p1_final_ir311is4\fichemaths_tests_4ca7mcir\exports`
- 110 tests collectés ; les deux destinations appartiennent au dossier temporaire, sous le même parent.

Les tests de migration utilisent aussi leur tmp_path, avec DATABASE_URL transmis explicitement aux sous-processus Alembic. L'appel direct de compilation LaTeX utilise tmp_path. Les exports API utilisent settings.export_dir. Les sorties XML/log et le cache temporaire de pytest restent dans la campagne ; le cache pytest du dépôt est désactivé pour ce lancement. Le build ne modifie que ses artefacts techniques habituels ignorés.

**Exigence permanente : chaque campagne doit isoler sa base et ses exports avant tout import applicatif. Aucun test ne doit écrire dans exports/ utilisateur ou courant.** La fixture corrigée met déjà cette règle en œuvre ; ce réaudit ne la modifie pas.

## 4. Matrice T01–T22

Toutes les preuves automatiques ci-dessous proviennent de la nouvelle campagne. Les noms exacts des cas sont conservés dans les XML, dont les paramètres T10/T11 et les deux variantes T13.

| Contrôle | Verdict | Vérification ciblée |
| --- | --- | --- |
| T01 | PASS | Fiches distinctes, numéros successifs et identité de séance conservée lors d'une nouvelle révision. |
| T02 | PASS | Deux demandes concurrentes : 201/409, une seule création ; double clic bloqué côté interface. |
| T03 | PASS | Couverture isolée par subdivision et année scolaire. |
| T04 | PASS | NOT_STARTED avant résultat explicite ; SKIPPED seul reste SKIPPED. |
| T05 | PASS | PARTIAL répété ne devient pas COVERED ; couverture explicite requise. |
| T06 | PASS | Progression partielle préservée après saut ; couverture acquise préservée après réactivation. |
| T07 | PASS | Recommandation prioritaire, saut visible, exclusion initiale de COVERED et reprise explicite. |
| T08 | PASS | Report visible et reproposé lors de la préparation suivante. |
| T09 | PASS | Résultats et minutes distincts par instruction ; aucune répartition implicite. |
| T10 | PASS | Seuils 119/120/130, pauses 0/10/10 ; surcharge locale préservée. |
| T11 | PASS | Entiers et bornes validés ; chaîne historique « 1 h 30 » refusée comme créneau. |
| T12 | PASS | Instantané conservé après changement du plan, du profil et de l'emploi du temps. |
| T13 | PASS | Migration vide et fixture historique 0004 : lignes/JSON/statuts conservés et FK conformes. |
| T14 | PASS | Historique DONE/PARTIAL/SKIPPED brut consultable, exclu de la nouvelle couverture. |
| T15 | PASS | Durées et métadonnées d'export cohérentes ; échecs de sauvegarde bloquent le départ. Rendus QA antérieurs réexaminés. |
| T16 | PASS | Niveau 4e, liens fiche/révision/segments, masse 360 min et refus de l'ancien endpoint pour séance contextualisée. |
| T17 | PASS | Provenance, contenu apprenant et duplication conservés ; exports locaux conservés pendant ce réaudit, incident clos par arbitrage. |
| T18 | PASS | Préparation/export sans exécution ni couverture acquise. |
| T19 | PASS | Finalisation sans exécution ; confirmation explicite dans l'interface. |
| T20 | PASS | Trois séances préparées à l'avance sans couverture acquise. |
| T21 | PASS | A couvert/B partiel/C sauté ; future séance et révision finalisée inchangées. |
| T22 | PASS | Recommandation sans mutation ; adaptation explicite seulement sur brouillon, numéro conservé. |

Correspondance : T01–T12 et T14–T22 dans backend/tests/test_planned_sessions.py ; T13 dans test_planned_migration.py. Compléments interface : T02/T07/T08/T09/T10/T12/T15/T22 dans Sessions.test.tsx et T19 dans App.test.tsx. Les autres tests existants complètent la non-régression.

**Portée visuelle et navigateur :** le parcours navigateur initial décrit dans le rapport P1 est conservé comme preuve antérieure, non présenté comme rejoué ici. Les rendus existants tmp/p1-qa/teacher-reviewed-1.png et learner-1.png ont été réexaminés visuellement : durées 120/10/110 et 330 minutes, conflit SA 56/60 h visible, séparation enseignant/apprenant lisible. Aucun PDF historique n'a été régénéré. La compilation PDF est à nouveau exercée par la suite backend isolée ; les interactions T15/T19 sont rejouées par les tests d'interface. Le réaudit ciblé ne prétend pas à une nouvelle campagne manuelle complète ni à une certification pédagogique du contenu.

## 5. Conservation des fichiers et historique

Les 73 fichiers préexistants sous exports/ et data/ conservent leurs empreintes, tailles et dates de création/modification pendant la campagne, sans ajout détecté dans ces dossiers. Les huit fichiers de l'incident ont également les mêmes empreintes que dans G1. Les heures d'accès ne sont pas une preuve utilisée.

data/app.db : SHA-256 inchangé `843fd91d04eaf79338f23ac3d2d18d05c197228f85b018213be45b0d1021d793`.

| Fichier de l'incident | SHA-256 début et fin |
| --- | --- |
| exports/fiche_enseignant_FICHE-4E-003_r1.pdf | `f14c9ca76ce8f09556ced72e371237d0bad05fd1e8bb3892ae17d7d80ae6e0da` |
| exports/fiche_enseignant_FICHE-4E-003_r1.log | `272ad6356d1b6b70a23b25e5c6bfb380a8d89df423f54acb92a6b053d1511a8b` |
| exports/fiche_apprenant_initiale_SUPPORT-4E-002_r1.pdf | `73165cab6b9ed2c3af181f413a6d839fe8ead22a286025db97f82ba77f8ebf61` |
| exports/fiche_apprenant_initiale_SUPPORT-4E-002_r1.log | `a50ad3bd39098ebc586fb96e51030d43a2b6116d9c3acd6eb70c402c09363e7f` |
| exports/fiche_apprenant_completee_SUPPORT-4E-002_r1.pdf | `2877812ce9f8464dbe3ab7e3ac48c4bd89855a189592485f79ef786db5ab7b25` |
| exports/fiche_apprenant_completee_SUPPORT-4E-002_r1.log | `1fc294d264da9fccd47aca85fb550cae6781483b2837d050daf09c0d1e245587` |
| exports/fiche_enseignant_FICHE-DEMO-001_r1.pdf | `c15b25837a9ee5078d386d36908039a946eec7c630947f3c5a79371c8e867aa8` |
| exports/fiche_enseignant_FICHE-DEMO-001_r1.log | `c181c13bdb9b32cbe93438a4be29690b3c831e35e236daee428a643c6daf052e` |

Conservation des données métier historiques : T13/T14/T17 et tests existants conformes sur fixtures isolées ; aucun changement de la base de travail. Conservation des octets pendant ce réaudit : vérifiée. Conservation des contenus antérieurs à l'incident : toujours non démontrée, risque traité exclusivement par l'arbitrage humain. Ces trois conclusions restent distinctes.

## 6. Traçabilité de la campagne

Dossier de preuves local temporaire : `C:\Users\HP\AppData\Local\Temp\fichemaths_p1_final_ir311is4`. Ce dossier peut être nettoyé par Windows ; les résultats et empreintes essentiels sont donc inscrits dans ce rapport.

| Preuve | SHA-256 |
| --- | --- |
| backend.xml | 8935f3c61264a92369faaa1bac5fb9c90b8bec1b00873af0b55937a96740476f |
| frontend.xml | f025a197617cd691455b2d713d2897509b3d3fc8fb4c7e0c0c9f76a84db5ce9f |
| build.log | ddceb3f55fd188d97f4efec359150f0487151ddeaac955cf1c90bf266e32d0fb |
| initial.json, inventaire des 198 fichiers | 13e04d0b6bc84ff1203cd4f800c7badad7586651b9b5f3cfaa971ebbd0e0b689 |

Lanceur conservé sous run_backend.py dans ce dossier : pytest.main avec -v, -p no:cacheprovider, --basetemp et --junitxml ; plugin local de contrôle des chemins sans modification des tests. Frontend : pnpm run test avec rapport JUnit, puis pnpm run build. Aucun résultat simulé, aucun test ajouté ou modifié pour obtenir les comptes attendus.

### Empreintes des fichiers P1 concernés

Référence de continuité, identique à G1 et au réaudit final pour les fichiers ci-dessous :

| Fichier | SHA-256 |
| --- | --- |
| backend/app/authoring.py | `037adf62488d76f116bcb382be6bf13db067b92d58b0ae8b2e1179a0456391d4` |
| backend/app/exporter.py | `7a9b027b8f7c1da815a4d423a2a3194c856404ed02b8148146f378c75c441793` |
| backend/app/main.py | `c857952741994f873e57c6f0321e7f17e3ae4010e0ee5a4d8a9f4b316d095545` |
| backend/app/models.py | `deecb0c38bff147f9badfdeecd323e964830a24b6a60282c1e1b0fa960da1c55` |
| backend/app/services.py | `794d512741da61ccd5e80d402ca1f6210976e6d6a931d925263dc10cc5c47593` |
| backend/app/sessions.py | `1dcee34c56ed6f4a8ba3dddbaeefdb6abadb74de0ab27175cf499e57dea6d001` |
| backend/alembic/versions/0005_planned_sessions.py | `4e8a94e71d14bff059e056fb03e39059f31cc1ca7baf799846c340f8ba28c5f7` |
| backend/tests/conftest.py | `e16537036c877aa258029c71fb1b75c95d3ec0950e5c8c84fa96d24f80f812a5` |
| backend/tests/test_e2e_001.py | `64b27db09806dd287aff716cc168120a66d0186630decddb4a4c18cb72971222` |
| backend/tests/test_v2_03_migration.py | `97ddcb29d1aaee2310757176eef5c6d4b8bbb8112850c05f5a5352bf7b49acd1` |
| backend/tests/test_planned_migration.py | `3443c8c1a1740802c9ba77195b77229f79a5a7064f2a6a6837a0e57d69479593` |
| backend/tests/test_planned_sessions.py | `150755e517f6db16074769e9ef6a3d4a4833f57d90229c3616448772ea6f14c2` |
| frontend/src/App.test.tsx | `59c466facc080b6523fc3ed2fc252618d79bf2a2072fcd54f628f64f247e817b` |
| frontend/src/App.tsx | `3f1fc4bea32460e4c67df7be58ae5b0a56daf3b48b04c93f2d59774200694277` |
| frontend/src/styles.css | `b78a0220c28df2c83d2b2fafc4dc9d843a8666fd56088f2d67587ad1dfe44908` |
| frontend/src/types.ts | `3cead81f43341a7fcb7b942adafb46c9f5d068d58ec4d9039bf08f62a2ea5432` |
| frontend/src/Sessions.test.tsx | `e3ef2804a3605761010b02680c3668050b3d814542a11d28cd60908f788b5fdd` |
| frontend/src/Sessions.tsx | `aea4e6d7483a879370e7157c218c91ca55b43c1e0f53c0672539c0f534f918ed` |

## 7. Changements documentaires et verdict final

Seuls changements documentaires de cette mission :
1. Addendum §10 au rapport G1 : clôture humaine formelle.
2. Addendum au rapport d'implémentation P1 : rattachement au présent verdict, ancien FAIL conservé comme état historique.
3. Création du présent rapport.

Aucun changement fonctionnel, migration, test ou source. Aucun commit, push, merge ni tag. Aucun serveur de QA lancé. Base de travail non migrée. Les limitations non bloquantes du rapport P1 restent applicables : SQLite seulement, profil de pause local, périmètre MVP et contrôle documentaire pilote.

```text
P1_HIST_EXPORT_001 = CLOSED_BY_HUMAN_ARBITRATION
V2_03_R1_P1 = PASS
FUNCTIONAL_P1_CODE_CHANGED = NO
MIGRATION_CODE_CHANGED = NO
DATABASE_CHANGED = NO
EXPORT_FILES_CHANGED = NO
PUSH = NO
MERGE = NO
TAG = NO
```
