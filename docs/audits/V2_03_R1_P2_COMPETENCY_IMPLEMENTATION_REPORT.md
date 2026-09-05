# V2-03-R1-P2 — Rapport d'implémentation du modèle de compétences

Date : 2026-09-05. Nature : implémentation ciblée P2, sans commit, push, merge ni tag.

## A. BASELINE

- Racine : `C:/Users/HP/Documents/ChatGPT/Fiche_pedagogique`.
- Branche : `fix/ux-bb-001-identification-navigation`.
- HEAD initial et final : `582f68c19fb17370e3d1112ba06d3bbd1a5cb3a2`.
- Gate initial : worktree propre, `git diff --check` sans erreur.
- Gate final : uniquement les changements P2 non committés ; `git diff --check` sans erreur, avertissements LF/CRLF non bloquants.

## B. EXISTING COMPETENCY MODEL AUDIT

L'existant plaçait des valeurs de compétences dans `CurriculumAttribute` et dans `TeacherSheetRevision.planning_json`. Les codes locaux `SA-CD1..3` reflètent un ordre de liste où le numérique précède parfois la géométrie ; ils ne constituent donc pas des identités canoniques fiables. Ces tables et toutes les valeurs historiques sont conservées comme `LEGACY_REFERENCE` ou `LEGACY_SHEET_VALUE`. Aucun rapprochement textuel, backfill ou réécriture n'est effectué.

## C. TARGET MODEL

Le modèle ajoute quatre objets relationnels : `Competency` pour les 17 identités stables, `CompetencyContext` pour les textes et métadonnées versionnés, `CompetencyApplicability` pour la pertinence par programme/classe/SA/séquence/instruction, et `TeacherSheetCompetencySelection` pour le choix propre à chaque révision. Une sélection stocke aussi un instantané JSON du libellé et de sa provenance afin que l'historique reste reproductible.

## D. MIGRATION 0006

`0006_competency_catalog` suit `0005_planned_sessions`. Elle crée uniquement les quatre nouvelles tables, index, contraintes et clés étrangères. Elle ne charge aucune donnée, ne modifie aucune table historique et refuse le downgrade destructif. La migration a été validée depuis une base vide et depuis une base isolée au schéma 0005, avec comparaison de toutes les anciennes tables et `foreign_key_check` vide.

## E. CANONICAL CATALOG

Le seed idempotent charge exactement 8 CT, 6 CTD et 3 CD. Les codes `CT1..CT8`, `CTD1..CTD6` et `CD1..CD3` sont explicites et indépendants de l'ordre local. `CD2` demeure géométrique et `CD3` numérique. Un seed répété conserve les mêmes identifiants et refuse d'écraser une référence divergente.

## F. CONTEXTS / VARIANTS

Le fichier de référence conserve 51 contextes issus des pages de programme P4/P6/P1 et 6 contextes de l'exemple du guide G4 p.74. Pour chaque page : texte brut complet, libellé brut, libellé d'affichage, niveau, version, page, empreinte du document, autorité, état et champs disponibles. Les contextes 4e, 6e et Première C restent des lignes distinctes liées à la même identité canonique. Les extraits de critères/capacités sont marqués `page_only` lorsqu'ils sont présents sur la page ; aucune complétude non vérifiée n'est revendiquée.

## G. APPLICABILITY

Le pilote actif rattache l'exemple G4 p.74 à `PRG-4E-BJ` / SA1 / SEQ8. Le type reste `EXAMPLE_SELECTION`, jamais `REQUIRED`. La correspondance vérifie toute la chaîne programme, SA, séquence et instruction éventuelle. Les priorités sont déterministes : REQUIRED, RECOMMENDED, CONTEXTUAL_CANDIDATE, EXAMPLE_SELECTION ; des plafonds empêchent d'injecter le catalogue entier.

## H. SHEET SELECTION

Toute nouvelle fiche du parcours curriculaire reçoit un brouillon éditable et un sous-ensemble contextualisé. L'enseignant peut retirer ou ajouter une compétence et sélectionner 0..N compétences de chaque type. La sélection est copiée vers une nouvelle révision puis peut diverger ; l'ancienne révision finalisée et ses lignes restent immuables.

## I. SOURCE / PROVENANCE

Les lectures API exposent le document, sa version/empreinte, la page, le texte brut, la version curriculaire, la classe d'autorité, l'état de source et l'éventuel `SourceIssue`. L'interface affiche des libellés métier simples : Programme, Exemple officiel, Suggestion automatique et Sélection enseignant. Une suggestion automatique ne devient ni une prescription officielle ni une validation.

## J. CT8 SOURCE ISSUE

`P0-SOURCE-CT8-6E-CONTEXT` est persisté à l'état OPEN. Le texte brut de P6 p.40 contient toujours « situations d'apprentissage prévues en troisième ». Aucun contexte corrigé n'est fabriqué. Le libellé canonique « Communiquer de façon précise et appropriée » demeure disponible ; le contexte 6e reste une référence inactive et n'est pas proposé dans le produit.

## K. LEGACY TRANSITION

Les valeurs historiques demeurent dans leurs colonnes d'origine. Les anciennes révisions retournent `competency_selection = null` et conservent leur export historique. Le premier passage explicite au nouveau stockage archive les anciennes rubriques dans `legacy_competency_values` sans les transformer. Les anciennes compétences ambiguës ne sont ni supprimées ni fusionnées.

## L. API

- `GET /api/competencies` : catalogue actif 4e avec contexte et provenance.
- `GET /api/competencies/sheets/{revision_id}` : sélection, applicabilités, suggestions et catalogue.
- `PUT /api/competencies/sheets/{revision_id}` : remplacement ordonné d'une sélection DRAFT.
- Le parcours 6e/Première C est refusé ; une révision FINALIZED est immuable.

## M. FRONTEND

La Partie II contient une section « Compétences proposées pour cette séance », regroupée par type. Les suggestions indiquent leur nature, leur source et leur page. L'enseignant peut décocher ou ajouter des choix. La sauvegarde est centralisée avec celle du wizard : « Enregistrer » et « Suivant » persistent d'abord les compétences, bloquent les doubles clics, restent sur l'étape et montrent l'erreur si la sauvegarde échoue.

## N. PDF / EXPORT

Le PDF enseignant lit exclusivement la sélection persistée via `sheet_detail`; il ne recalcule rien au moment de l'export. L'ordre est celui stocké dans la révision et seules les catégories sélectionnées sont rendues. Le support apprenant ne reçoit pas les compétences. Une génération isolée a produit deux PDF A4 d'une page : enseignant avec seulement CD1/CTD2/CT6, apprenant avec consigne, propriété et figure, sans le bloc `EXPECTED_RESPONSE`. Les deux pages ont été rendues en PNG et relues visuellement : pas de chevauchement, texte coupé, glyphe noir ou défaut de mise en page observé.

## O. TESTS P2-T01..P2-T30

| Tests | Résultat | Preuve principale |
|---|---|---|
| P2-T01–T02 | PASS | 8/6/3, double seed, codes stables et CD2 géométrique. |
| P2-T03–T04 | PASS | Variantes P4/P6/P1 séparées, contextes distincts, identité canonique commune. |
| P2-T05–T06 | PASS | Chaîne d'applicabilité complète ; EXAMPLE_SELECTION reste un exemple. |
| P2-T07–T08 | PASS | Sous-ensemble SEQ8 de 6 compétences, contexte et provenance. |
| P2-T09–T11 | PASS | Ajout/retrait, persistance par révision, copie et divergence sans mutation de l'ancienne finalisée. |
| P2-T12–T16 | PASS | 0 et plusieurs CTD acceptées ; plafonds AUTO 1 CTD, 3 CT, 2 CD ; aucune suggestion sans contexte. |
| P2-T17 | PASS | « troisième » conservé, issue OPEN, aucun contexte corrigé. |
| P2-T18–T19 | PASS | 6e et Première C absentes du parcours et refusées à l'écriture. |
| P2-T20–T21 | PASS | Export enseignant limité au snapshot ; support apprenant sans compétence ni réponse attendue. |
| P2-T22–T24 | PASS | Migration 0005→0006 et vide ; anciennes tables identiques. |
| P2-T25–T27 | PASS | Seed idempotent, legacy inchangé, provenance visible. |
| P2-T28–T30 | PASS | Déterminisme, AUTO éditable, base/exports de test isolés et fichiers protégés inchangés. |

## P. P1 NON-REGRESSION

- Backend complet : **136 passed**, 0 échec, 0 erreur, 59,408 s.
- Frontend complet : **54 passed**, 4 fichiers, 0 échec, 2,388 s.
- Build TypeScript/Vite : **PASS**, 37 modules, 2,73 s.
- T01–T22 P1 : inclus et passants dans la suite backend/frontend.
- Migration 0005 : son test historique vise désormais explicitement la cible 0005 ; la campagne P2 teste ensuite 0006 séparément.
- Navigateur : création depuis le programme, affichage des 6 suggestions, retrait de CTD, ajout de 2 CTD, sauvegarde avant navigation et aperçu vérifiés sur l'instance isolée.
- PDF enseignant et support apprenant : compilés et relus visuellement dans l'environnement isolé.

## Q. KNOWN LIMITATIONS

Le dataset actif d'applicabilité est volontairement limité à l'exemple 4e SEQ8 de G4 p.74. Les autres séquences n'ont pas de suggestion automatique tant qu'une applicabilité sourcée n'est pas ajoutée. Les champs structurés critères/capacités ne revendiquent que l'extrait visible sur la page de début ; une extraction documentaire exhaustive relèverait d'une autre mission. SQLite est couvert ; PostgreSQL ne l'est pas dans ce dépôt.

Le bundle frontend reste à environ 526 kB et déclenche l'avertissement indicatif Vite déjà connu. Aucun refactoring hors périmètre n'a été entrepris.

## R. FINAL VERDICT

Les 69 fichiers préexistants sous `data/` et `exports/` sont identiques à la capture initiale. `data/app.db` conserve SHA-256 `843fd91d04eaf79338f23ac3d2d18d05c197228f85b018213be45b0d1021d793`. Toutes les bases, migrations, seeds et sorties de QA sont sous `C:/Users/HP/AppData/Local/Temp/fichemaths_p2_a_4qa3gf`. Aucun plan annuel, devoir, documents-used, activation 6e/Première C, push, merge, tag ou commit n'a été introduit.

V2_03_R1_P2 = PASS
