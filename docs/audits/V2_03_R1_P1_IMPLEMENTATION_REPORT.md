# V2-03-R1-P1 — Session / Coverage / Durations Foundation

Date : 2026-09-04. Implémentation locale, sans commit, push, merge ni tag.

**Résultat fonctionnel :** périmètre P1 implémenté ; 110 tests backend et 51 tests frontend passent, build réussi, parcours navigateur et rendu PDF contrôlés. **Verdict global : FAIL**, car la première campagne a utilisé le dossier d’exports courant avant correction de l’isolation des tests. La conservation intégrale des anciens fichiers PDF ne peut donc pas être attestée. Voir I et O ; aucun PASS global ne doit être déduit des tests fonctionnels.

## A. BASELINE

- Racine vérifiée : `C:/Users/HP/Documents/ChatGPT/Fiche_pedagogique`.
- Branche attendue et observée : `fix/ux-bb-001-identification-navigation`.
- HEAD initial et final : `578b2a4b49e8284f1885693e368554762bc62e25`.
- Ascendance : `git merge-base --is-ancestor 578b2a4b49e8284f1885693e368554762bc62e25 HEAD`, code 0.
- `git branch --show-current`, `git rev-parse HEAD`, `git status`, `git diff --check`, `git log --oneline --decorate -n 10` exécutés avant modification.
- Aucun changement suivi à l’entrée. Trois documents non suivis expliqués par les missions précédentes : G0 `V2_03_R1_FUNCTIONAL_DELTA_AUDIT.md`, P0 `V2_03_R1_P0_SOURCE_GROUNDED_BUSINESS_RULES.md`, arbitrages/périmètre P1 `V2_03_R1_P0_HUMAN_ARBITRATIONS_AND_P1_SCOPE.md`. Lus et conservés ; G0 conserve l’empreinte documentée dans P0, `ce06f0bbe754457778e1dd5fe287c3c8c61c29e87e0f6ebdbebd328facf63c16`.
- Source autoritative appliquée : périmètre final P1, U1–U7 fermés. Aucun corpus ni source corrigé.

## B. FILES CHANGED

| Groupe | Fichiers |
|---|---|
| Modèle et migration | `backend/app/models.py`, nouveau `backend/alembic/versions/0005_planned_sessions.py` |
| Services/API | nouveau `backend/app/sessions.py`, `backend/app/main.py`, `backend/app/authoring.py`, `backend/app/services.py` |
| Exports | `backend/app/exporter.py` |
| Frontend | nouveau `frontend/src/Sessions.tsx`, `frontend/src/App.tsx`, `frontend/src/types.ts`, `frontend/src/styles.css` |
| Tests backend | nouveaux `test_planned_sessions.py`, `test_planned_migration.py` ; `conftest.py`, `test_e2e_001.py`, `test_v2_03_migration.py` sous `backend/tests` |
| Tests frontend | nouveau `frontend/src/Sessions.test.tsx`, `frontend/src/App.test.tsx` |
| Rapport | ce document |

Les artefacts de QA sont dans `tmp/p1-qa/`, ignoré par Git. Les quatre PDF et leurs journaux du dossier `exports/` touchés par le premier essai sont décrits en I. Les trois rapports d’entrée ne font pas partie des modifications de cette mission.

## C. DATABASE MODEL

`ClassContext` : niveau canonique 4e, subdivision normalisée, année scolaire consécutive, volume hebdomadaire réel facultatif. Unicité niveau/libellé/année ; niveau et subdivision restent distincts.

`SequencePlan` : contexte + séquence uniques, durée locale facultative et positive. `PlannedSession` : lien à la séquence contextualisée, fiche unique, numéro positif unique dans le plan. Le lien appartient à la fiche, donc toutes ses révisions gardent la même identité de séance.

`TeachingSession.planned_session_id` nullable et indexé. Les instructions prévues et résultats réels utilisent les deux tables existantes. La couverture est une projection calculée, sans table supplémentaire.

## D. MIGRATION 0005

Migration additive après 0004 : trois tables, contraintes et lien nullable. Sur SQLite, ajout natif de la colonne avec `REFERENCES`, sans reconstruction de la table vivante. Les tables/colonnes déjà créées par le comportement historique de 0001 sur installation vide sont reconnues.

T13 vérifie une base vide et une fixture de forme 0004 contenant révisions/JSON/statuts historiques, avec comparaison avant/après des lignes et contrôle des clés étrangères. Les nouveaux liens historiques restent NULL. Les suppressions/reconstructions présentes dans le test servent uniquement à fabriquer la fixture 0004 jetable ; elles ne figurent pas dans l’upgrade.

Aucun upgrade sur `data/app.db`, aucun backfill, reset, stamp ou conversion DONE. Le downgrade est refusé explicitement : il nécessite une procédure de préservation distincte. La validation actuelle concerne SQLite, pas PostgreSQL.

## E. SESSION MODEL

Création atomique fiche + révision DRAFT + segments + séance. Le client transmet le numéro attendu ; une collision renvoie 409 avec rechargement, sans fiche orpheline. Deux requêtes réellement concurrentes sont testées. Les doubles clics sont également bloqués dans le frontend.

Trois séances peuvent être préparées sans exécution. Une nouvelle révision conserve le numéro. La duplication produit une fiche indépendante et retire l’identité/instantané de séance contextualisée. La suppression d’une fiche numérotée est refusée proprement, afin de ne pas réutiliser silencieusement son numéro.

## F. PLANNED / EXECUTED / COVERAGE

`PLANNED != EXECUTED != COVERAGE`.

Le nouveau formulaire accepte des résultats explicites PARTIAL/COVERED/SKIPPED, chacun avec ses minutes réelles. Il indique les instructions non renseignées ; aucune ligne d’exécution n’est créée pour celles-ci. Une révision finalisée de la fiche attendue est requise ; segments étrangers, répétés ou liens incohérents sont refusés. L’ancien endpoint global refuse les fiches contextualisées.

Réduction par contexte/instruction : COVERED explicite, sinon PARTIAL, sinon SKIPPED, sinon NOT_STARTED. Dernier résultat, saut antérieur, minutes et références des événements restent disponibles. Ni répétition de PARTIAL, ni durée, ni préparation, ni finalisation, ni export ne créent COVERED.

## G. SKIPPED BEHAVIOR

PARTIAL prioritaire ; NOT_STARTED et SKIPPED ensuite dans l’ordre curriculaire. SKIPPED reste visible, éligible et signalé. COVERED est désélectionné par défaut dès l’ouverture d’une préparation ; sa reprise exige un choix explicite validé aussi côté serveur.

Le report temporaire est enregistré dans l’instantané courant et reste visible, sans événement ni changement de couverture. La préparation suivante le repropose. Aucun moteur de dates.

La recommandation est une lecture séparée, sans création de plan/séance, suppression ou mutation de révision. L’UI demande d’abord d’ouvrir le plan de séquence. Elle signale les séances non exécutées contenant déjà chaque instruction. Appliquer une proposition est un geste distinct. L’adaptation d’une séance existante cible exclusivement son brouillon ; une révision finalisée exige une nouvelle révision. Les copies de ressources retirées restent conservées mais masquées, avec historique de sélection.

## H. DURATIONS

| Concept | Traitement |
|---|---|
| SA officielle | Sources/provenances existantes ; divergence 56 h / 60 h conservée et explicitée pour les nouvelles fiches |
| Séquence prévue | Minutes locales facultatives du plan, capturées dans chaque préparation |
| Créneau | Entier strictement positif saisi explicitement |
| Pause | Entier local, positif ou nul et strictement inférieur au créneau |
| Séance pédagogique | Créneau moins pause, une seule fois |
| Réel | Minutes saisies par instruction à l’exécution |
| Masse hebdomadaire curriculum | 360 min, programme 4e examiné P4 p.12 et SHA-256 du registre P0 |
| Emploi du temps réel | Facultatif, configurable pour la classe/année, indépendant du programme |

Profil navigateur initial : 10 min dès 120 min, sinon zéro. Surcharge explicite préservée lors d’un changement de profil. Les instantanés de révisions existantes ne sont pas recalculés automatiquement. Une chaîne historique « 1 h 30 » n’est pas convertie en créneau ni en 130 minutes.

## I. HISTORICAL PRESERVATION

La migration conserve les lignes historiques et leur JSON ; DONE/PARTIAL/SKIPPED restent consultables dans la vue « Historique sans classe et année associées ». Le compteur n’entraîne plus de validation verte. Les anciennes données ne sont pas intégrées à une couverture contextualisée. Le chemin de restitution des révisions sans instantané P1 est conservé.

**P1-HIST-EXPORT-001 — préservation des fichiers non attestée, bloquant pour le verdict global.** La première campagne backend a été lancée avec la fixture préexistante, qui isolait la base mais pas `EXPORT_DIR`. Elle a écrit entre 16:37:09 et 16:37:49 dans le dossier d’exports courant les fichiers suivants, ainsi que leurs `.log` :

| Fichier sous `exports/` | SHA-256 après l’incident |
|---|---|
| `fiche_enseignant_FICHE-4E-003_r1.pdf` | `F14C9CA76CE8F09556CED72E371237D0BAD05FD1E8BB3892AE17D7D80AE6E0DA` |
| `fiche_apprenant_initiale_SUPPORT-4E-002_r1.pdf` | `73165CAB6B9ED2C3AF181F413A6D839FE8EAD22A286025DB97F82BA77F8EBF61` |
| `fiche_apprenant_completee_SUPPORT-4E-002_r1.pdf` | `2877812CE9F8464DBE3AB7E3AC48C4BD89855A189592485F79EF786DB5AB7B25` |
| `fiche_enseignant_FICHE-DEMO-001_r1.pdf` | `C15B25837A9EE5078D386D36908039A946EEC7C630947F3C5A79371C8E867AA8` |

Aucun inventaire/empreinte avant cet essai n’avait été établi pour ces fichiers ignorés par Git. Il n’est donc pas possible de distinguer avec certitude création et remplacement, ni d’attester leur contenu antérieur. Aucune restauration conjecturale n’a été tentée. La base de travail n’a pas été utilisée par ces tests.

Correction appliquée : chaque campagne possède désormais une base et un dossier d’exports dans un répertoire temporaire unique dès l’import de `conftest.py`. Les campagnes finales n’écrivent plus dans `exports/`. La levée du finding exige une comparaison avec une sauvegarde antérieure identifiée, ou une décision explicite sur ces quatre fichiers ; les tests réussis ne remplacent pas cette preuve.

## J. API

Préfixe `/api/session-planning` :

- GET/POST `/contexts`, PUT `/contexts/{id}/timetable`.
- POST `/plans`, GET `/plans/{id}`, PUT `/plans/{id}/duration`.
- POST `/plans/{id}/sessions` : prochaine séance planifiée.
- GET `/contexts/{id}/coverage`, GET `/plans/{id}/recommendation` : projections en lecture seule.
- PUT `/revisions/{id}/preparation` : adaptation explicite d’un brouillon.
- POST `/sessions/{id}/executions` : résultats réels par instruction.

`GET /api/sheets/{id}` expose le numéro/lien de séance et son instantané. `GET /api/progress` restitue les résultats historiques bruts sans faux DONE. Le test E2E historique vérifie maintenant ce contrat corrigé, et conserve son assertion sur le statut brut DONE.

## K. FRONTEND

Entrée « Planifier des séances par classe et année » dans Mes fiches ; le formulaire existant et ses CTA restent disponibles. Parcours classe/année → SA → séquence → séance, création manuelle ou composition automatique existante.

Panneau de séance : identité, durées, sources de durée SA, couverture, résultats réels après cours et adaptation explicite. Les champs d’identité contextuelle sont protégés dans le formulaire générique. Les métadonnées sont sauvegardées avant ouverture de l’adaptation ; une erreur bloque ce passage. La fenêtre d’adaptation ne se ferme qu’après sauvegarde réussie ou annulation explicite.

La confirmation native de finalisation a bloqué l’onglet de QA. Pour le seul parcours contextualisé, elle a été remplacée par une fenêtre HTML avec confirmation explicite et protection des doubles soumissions. Le parcours historique conserve son dialogue. La récupération et la finalisation ont été rejouées dans le navigateur.

## L. EXPORTS

Deux PDF LaTeX contrôlés visuellement sur toutes leurs pages (une page chacun) : enseignant et apprenant. Le rendu enseignant final distingue 56/60 h avec conflit conservé, séquence 330 min, créneau 120 min, pause 10 min et séance pédagogique 110 min. Le support apprenant conserve consignes et propriété, sans résultats attendus ni grande zone de réponse. Les tests V2-03 existants couvrent aussi les catégories de formulations et figures.

Artefacts de contrôle, non documents officiels : `tmp/p1-qa/teacher-reviewed.pdf`, sa source `.tex`, `tmp/p1-qa/exports/fiche_apprenant_initiale_SUPPORT-1D7B3FADCDEC_r1.pdf`, et rendus PNG voisins. La fiche de test contient volontairement des métadonnées et résultats attendus non renseignés ; sa finalisation de QA ne constitue pas une validation pédagogique du contenu.

## M. TEST RESULTS T01–T22

Campagne finale backend : **110 passed in 39.24s**. Frontend final : **51 passed**, quatre fichiers. Build TypeScript/Vite : réussi ; avertissement de taille du bundle, sans erreur.

| Test | Résultat et preuve principale |
|---|---|
| T01 | PASS — fiches/numéros distincts, révision conservant la séance |
| T02 | PASS — deux requêtes concurrentes : 201/409, une seule fiche supplémentaire ; garde double clic frontend |
| T03 | PASS — isolation subdivision et année |
| T04 | PASS — NOT_STARTED puis SKIPPED seul |
| T05 | PASS — PARTIAL/PARTIAL/COVERED explicite |
| T06 | PASS — PARTIAL puis SKIPPED ; couverture acquise conservée après réactivation |
| T07 | PASS — classement de recommandation, saut visible, exclusion COVERED par défaut et reprise explicite |
| T08 | PASS — report enregistré, visible et reproposé ultérieurement |
| T09 | PASS — trois statuts/minutes distincts ; aucune division automatique |
| T10 | PASS — 119/120/130, pauses 0/10/10, profil et surcharge frontend |
| T11 | PASS — entiers, positivité, limites pause, ancienne chaîne non utilisée comme créneau |
| T12 | PASS — snapshot/export inchangés après modification profil, plan et emploi du temps |
| T13 | PASS — migration depuis fixture 0004 et base vide, comparaison des lignes et contrôle FK |
| T14 | PASS — historique brut consultable et exclu de la couverture contextualisée |
| T15 | PASS fonctionnel — parcours navigateur, PDF, sauvegarde bloquante testée par erreurs injectées en frontend |
| T16 | PASS — niveau 4e, masse sourcée, révisions et segments cohérents, ancien endpoint refusé pour nouvelle séance |
| T17 | PASS sur fixtures — auteur/provenance/support/duplication/historique ; ne lève pas P1-HIST-EXPORT-001 sur les fichiers locaux |
| T18 | PASS — création et export d’un brouillon sans nouvelle exécution ni couverture |
| T19 | PASS — finalisation sans exécution, confirmation humaine explicite |
| T20 | PASS — trois préparations à l’avance, également réalisées en navigateur |
| T21 | PASS — A couvert, B partiel, C sauté ; séances futures et révision finalisée inchangées |
| T22 | PASS — recommandation sans mutation, signalement des séances futures, adaptation explicite d’une nouvelle révision |

Tests P1 : `backend/tests/test_planned_sessions.py`, `backend/tests/test_planned_migration.py`, `frontend/src/Sessions.test.tsx` et test de confirmation dans `App.test.tsx`. Les tests existants complètent la non-régression ; les numéros T15/T17 regroupent preuves automatiques et observations visuelles, pas une certification de sources.

Trace navigateur sur base dédiée `tmp/p1-qa/browser.db` : contexte 4e QA/2026-2027 ; séances 1/2/3 créées avant exécution. Fiches `FICHE-96D799446220`, `FICHE-BD49C7D62A96`, `FICHE-921846AEDBD3`. Séance 1 finalisée puis résultats INS3=COVERED/25 min, INS4=PARTIAL/35 min, INS6=SKIPPED/0 min. Recommandation : INS4 prioritaire, INS6 signalée, séances 2/3 présentes ; numéro suivant toujours 4, sans création par recommandation. Application explicite de la proposition : INS3 décochée. Contrôle visuel de la lisibilité après correction de la largeur des lignes de couverture.

## N. NON-REGRESSION

77 tests backend antérieurs inclus dans les 110 ; 42 frontend antérieurs inclus dans les 51. Composition/source/provenance, mode manuel, sélection des ressources, support apprenant, édition des résultats attendus, sauvegarde avant navigation et révisions sont exercés. L’ancien test de migration cible désormais explicitement 0004 pour continuer à vérifier cette migration ; T13 couvre la nouvelle tête 0005.

Aucune progression annuelle complète, activation 6e, import de corpus, correction de source, backfill, homework, documents utilisés ou refonte CTD. U7 reste un garde-fou : aucun invariant exactement-une CTD ni injection automatique des six ajouté.

Commande de reproduction depuis la racine : `powershell -ExecutionPolicy Bypass -File .\scripts\test-all.ps1`. Les migrations sont exercées par pytest sur bases isolées. Cette commande ne déploie pas la migration sur la base de travail.

## O. KNOWN LIMITATIONS

1. **Bloquant global : P1-HIST-EXPORT-001**, conservation des quatre PDF antérieurs non attestée, malgré l’isolation corrigée.
2. SQLite validé ; PostgreSQL et montée de version de la base de travail non exécutés. L’application habituelle nécessitera une migration contrôlée après revue ; la QA a utilisé exclusivement son propre environnement.
3. Profil de pause local au navigateur, sans synchronisation. Pas de correction/suppression des événements réels, de suppression/renumérotation des séances ou de plan annuel : exclusions du périmètre.
4. Vérification visuelle sur scénario pilote d’une page ; les contrôles V2-03 existants complètent les tests, sans nouvelle certification mathématique ou documentaire.

## P. FINAL VERDICT

Implémentation P1 fonctionnelle et tests réussis. Migration additive validée sur bases isolées ; prévu/réalisé/couverture séparés ; aucun enrichissement hors périmètre métier. Le finding sur les fichiers d’exports empêche de déclarer que l’ensemble de l’historique local est préservé.

Modifications laissées non commitées, rapports d’entrée conservés. SHA final de HEAD : `578b2a4b49e8284f1885693e368554762bc62e25` ; ce SHA désigne la baseline, pas les changements non committés. Aucun push, merge ou tag.

Contrôle final : branche inchangée, `git status` inventorié, `git diff --check` code 0. Serveurs de QA arrêtés ; ports 8000 et 5173 libérés. La base de travail reste non migrée.

**V2_03_R1_P1 = FAIL**

## Q. Addendum — clôture humaine et réaudit final du 2026-09-04

Le FAIL ci-dessus décrit l'état initial et reste conservé avec l'incident. L'utilisateur a depuis explicitement accepté `ACCEPT_CURRENT_EXPORTS_AS_NON_AUTHORITATIVE_DERIVATIVES`, sans prétention sur l'ancien contenu des PDF et sans mutation demandée. L'addendum §10 du rapport G1 enregistre **P1_HIST_EXPORT_001 = CLOSED_BY_HUMAN_ARBITRATION** ; l'isolation des exports de test devient une exigence permanente.

Le réaudit final ciblé documenté dans `V2_03_R1_P1_FINAL_TARGETED_REAUDIT.md` a ensuite confirmé le code P1 inchangé, la migration 0005 sur bases jetables, 110 tests backend et 51 tests frontend réussis, le build, T01–T22, l'isolation, la conservation des fichiers pendant la campagne et git diff --check. Les preuves navigateur antérieures sont distinguées des tests réellement rejoués. Les contenus préincident ne sont toujours pas prouvés ; leur adjudication repose sur la décision humaine.

**Verdict courant remplaçant le FAIL global historique : V2_03_R1_P1 = PASS.** Base de travail et exports concernés inchangés. Aucun push, merge ni tag. Les limites non bloquantes initiales restent applicables.
