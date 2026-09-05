# V2-03-R1-P0 — Arbitrages humains et proposition P1

Date : 2026-09-04. Nature : addendum documentaire autoritatif pour les arbitrages ; périmètre final intégrant les trois corrections de la validation conditionnelle. **NO IMPLEMENTATION YET.**

## 1. Portée et ordre des décisions

Entrées : message utilisateur « ARBITRAGES HUMAINS V2-03-R1-P0 — U1 À U7 », pièce jointe `486c3628-6e58-4dba-ab3e-cb51fc1f0d72/pasted-text.txt`, puis « VALIDATION CONDITIONNELLE DU PÉRIMÈTRE V2-03-R1-P1 », pièce jointe `045c4e65-549b-4e0f-bc05-9d01d898501c/pasted-text.txt`. Cette dernière décision prévaut : autorité répartie par fonction pour U6, séparation planification/exécution/couverture et préparation anticipée indépendante de l'exécution. Les anciens rapports sont conservés comme traces de l'analyse précédente.

En particulier, les règles C07, D05, D08, E07, I04, I05 et E06 de P0 doivent être lues avec les décisions ci-dessous. Les anciennes mentions de six ou sept arbitrages ouverts ne décrivent plus l'état courant. Les dépendances au plan annuel et les formulations des sections A/I/J/K incompatibles avec U5/U6 sont remplacées par cet addendum.

`HUMAN_ARBITRATIONS_CLOSED = 7/7`. Clôture d'un arbitrage ne signifie ni implémentation, ni certification documentaire, ni résolution d'une anomalie de source. Ne pas rouvrir U1–U7 sans nouvelle preuve documentaire ou nouvelle décision explicite.

## 2. Registre des décisions applicables

| Arbitrage | Statut | Règle produit validée |
|---|---|---|
| U1 — SKIPPED | CLOSED | Une instruction sautée reste non traitée, visible, éligible et reproposée par défaut avec son signalement. Reprise des PARTIAL prioritaire ; NOT_STARTED éligible ; COVERED exclu par défaut mais réactivable explicitement. Exclusion/report temporaire explicite possible. |
| U2 — Pause | CLOSED | Donnée locale configurable, jamais prescription officielle. Profil initial : 10 minutes proposées si créneau brut ≥ 120 minutes, sinon 0. Surcharge par séance. Durée pédagogique = créneau brut − pause ; aucune double soustraction. |
| U3 — Masse horaire | CLOSED | Hypothèse 4,5/5 h abandonnée. Les 4,5 et 5,5 du suivi 2025–2026 sont des pourcentages d'exécution. Le programme 4e examiné indique 6 h hebdomadaires ; l'emploi du temps réel reste local et distinct. Aucune constante 4,5 h ou 5 h pour la 4e. |
| U4 — CT8 en 6e | CLOSED | Conserver le texte brut mentionnant « troisième ». Libellé utilisable : « Communiquer de façon précise et appropriée ». Ne pas fabriquer un contexte canonique corrigé. Conserver un SourceIssue documentaire ; correction ultérieure par erratum autoritatif ou arbitrage inspecteur/CP. |
| U5 — Plan annuel | CLOSED | `ANNUAL_PROGRESSION_PLAN = DEFERRED_AS_FULL_FEATURE`. Documents consultables/référencés ; préparation indépendante du plan annuel : CLASS → SA → SEQUENCE → SESSION → INSTRUCTION COVERAGE. |
| U6 — Autorité | CLOSED_WITH_CORRECTION | Autorité répartie par fonction : programme et guide sur le curriculum ; progression annuelle officielle applicable sur la cadence, l'ordre temporel et l'échéancier de la classe et de l'année concernées. Aucune priorité absolue programme > guide > progression pour tous les domaines ; aucune mutation silencieuse du curriculum. |
| U7 — CTD | CLOSED | Sélection techniquement 0..N ; `EXACTLY_ONE_CTD` interdit comme invariant universel. Présélection d'une CTD pertinente proposée par une source contextualisée ; présentation habituelle d'une CTD principale et sélection modifiable. Ne jamais injecter automatiquement les six CTD. |

`CURRICULUM_AUTHORITY = PROGRAMME_OFFICIEL + GUIDE_OFFICIEL`

`YEAR_EXECUTION_AUTHORITY = OFFICIAL_ANNUAL_PROGRESSION` applicable à l'année scolaire et à la classe concernées.

Le programme fait autorité sur les compétences, connaissances, contenus prescrits et orientations. Le guide fait autorité sur les indications pédagogiques, instructions, découpage opérationnel et traitements didactiques. La progression annuelle officielle, produite par l'inspection, fait autorité sur le QUAND : cadence, ordre temporel et échéancier d'exécution. Si G4 et la progression officielle 4e 2025–2026 diffèrent sur une semaine ou l'échelonnement d'une séquence, la progression 2025–2026 est la référence temporelle pour cette année ; elle ne modifie ni le contenu canonique ni les instructions du guide.

Son origine officielle, son année et sa version restent conservées. Le report de la fonctionnalité annuelle complète ne suspend pas cette autorité métier et ne fait pas de la progression une simple ressource locale ou consultative. U6 reste fermé, avec correction.

### SourceIssue documentaire maintenu

- Identifiant documentaire : `P0-SOURCE-CT8-6E-CONTEXT` (aucune insertion en base).
- Source : P6 du registre P0, programme 6e ; occurrence/contextualisation CT8 signalée dans P0.
- Anomalie : le contexte mentionne « troisième » dans le programme 6e.
- État de la source : OPEN, en attente d'un erratum autoritatif ou d'un arbitrage inspecteur/CP.
- Traitement produit décidé : conserver la source brute et la provenance ; seul le libellé non contradictoire est utilisable. Aucune correction inventée. U4 reste CLOSED car le traitement de l'anomalie est arbitré.

### Périmètre annuel ultérieur

Conserver comme cible distincte `OfficialAnnualProgression` : school_year, class_level, issuing_authority, source_document, weeks/periods, SA/sequence expectations, integration periods, assessment periods, remediation periods, interruptions, version/provenance. Une mission autonome traitera import, stockage, édition et association explicite de la version applicable à la classe/année, puis comparaison prévu/réalisé, retard/avance et prochaine séquence/séance attendue. Aucun de ces traitements annuels n'est une dépendance obligatoire de P1 ; leur report technique ne remet pas en cause U6.

## 3. V2-03-R1-P1 — objectif et limites proposés

**Résultat attendu :** pour une classe et une année choisies, préparer plusieurs séances numérotées d'une même séquence à l'avance sans exécution préalable, enregistrer séparément le résultat réel instruction par instruction, puis obtenir une recommandation fondée sur la couverture réelle, sans écraser les séances futures ni modifier les révisions finalisées.

Périmètre initial : niveau curriculum 4e déjà actif, subdivisions de classe distinctes, années scolaires distinctes, une séquence par séance. Aucune activation du corpus 6e ni élargissement multiniveau. Une révision reste une version de la même fiche ; elle n'est jamais assimilée à une nouvelle séance.

Inclus : parcours de création et préparation suivante, enregistrement d'exécution, affichage de progression contextuelle, champs de durée distincts, profil local de pause et restitution des nouvelles durées dans la fiche enseignant. Réutiliser le moteur existant pour les ressources compatibles ; ne pas construire un nouvel optimiseur de contenu.

Exclus : planification annuelle complète, rapprochement avec ses semaines, import de corpus, correction des sources, refonte générale des classements de ressources, statistiques avancées, calendrier réel détaillé, gestion multi-enseignants, réécriture des exports historiques, correction/suppression des exécutions déjà enregistrées. U7 constitue un garde-fou de compatibilité ; une refonte dédiée de l'UX CTD n'entre pas dans cette P1.

## 4. Modèle minimal proposé

Les noms suivants sont des propositions d'implémentation, pas des objets déjà présents.

| Objet | Champs et relations essentiels |
|---|---|
| ClassContext | id, class_level, class_label, school_year ; unicité de ce triplet, libellés normalisés à l'entrée. Le niveau canonique demeure 4e, indépendamment de la subdivision. |
| SequencePlan | id, class_context_id, sequence_id, planned_sequence_minutes nullable ; unicité contexte + séquence. Durée planifiée locale, distincte de la durée officielle de SA. |
| PlannedSession | id, sequence_plan_id, session_number_within_sequence, sheet_id unique ; numéro entier ≥ 1, unique dans le SequencePlan. Une fiche appartient à une séance planifiée et conserve ses révisions. |
| PLANNED_SESSION_INSTRUCTION | Instructions prévues conservées via les SessionCurriculumSegment de chaque TeacherSheetRevision de la fiche liée à PlannedSession : instruction_id, ordre et durée prévue. Cet instantané identifie le prévu de chaque révision ; il ne représente aucune exécution. |
| TeachingSession existant | Exécution datée liée à une révision finalisée ; ajouter planned_session_id nullable. Pour le nouveau parcours, lien obligatoire et cohérent avec la fiche et le contexte. |
| EXECUTED_INSTRUCTION_RESULT | ExecutedCurriculumSegment existant : résultat explicitement enregistré après séance, PARTIAL, COVERED ou SKIPPED, minutes réelles et ordre ; lié au segment prévu de la révision exécutée. NOT_STARTED n'est pas un résultat d'exécution à saisir. |
| CUMULATIVE_INSTRUCTION_COVERAGE | InstructionCoverage : projection calculée exclusivement des résultats d'exécution, clé (class_context_id, instruction_id), statut NOT_STARTED/PARTIAL/COVERED/SKIPPED, dernier résultat, indicateur de saut antérieur et références des exécutions sources. Pas de table redondante de couverture en P1. |

Le calcul s'appuie sur les identifiants exacts des instructions et leur provenance curriculum ; aucun rapprochement de textes entre versions. Le contexte annuel est explicite, sans déduction à partir de la date ou d'un libellé historique.

`CREATE_NEXT_PLANNED_SESSION` crée atomiquement un PlannedSession, une nouvelle fiche et sa première révision DRAFT avec ses instructions prévues. Aucune exécution préalable n'est exigée : les séances 1, 2 et 3 peuvent être préparées successivement avant tout cours. Le numéro proposé suit le plus grand numéro déjà attribué dans la séquence et le contexte, protégé par contrainte d'unicité ; en conflit, réponse claire et rechargement, aucun écrasement. Aucun renumérotage silencieux. Une nouvelle révision conserve le même numéro de séance.

`RECOMMEND_NEXT_SESSION_FROM_ACTUAL_COVERAGE` produit une proposition séparée à partir des seuls résultats réels disponibles. Elle ne crée, ne supprime et ne modifie aucune séance existante. Les instructions déjà prévues ailleurs peuvent être signalées comme telles, sans devenir couvertes ni disparaître de la recommandation pour ce seul motif. L'enseignant choisit d'utiliser la proposition pour une nouvelle séance ou d'adapter explicitement le brouillon d'une séance future. Si sa fiche est finalisée, l'adaptation passe par une nouvelle révision DRAFT conformément au mécanisme existant.

En cas de divergence prévu/réalisé, afficher les instructions à reprendre et leur présence éventuelle dans les séances futures. Aucune réconciliation ni aucun recalcul destructif automatique. Enregistrer une exécution ne modifie jamais rétroactivement une révision finalisée.

La duplication ne copie pas implicitement l'identité de séance : soit elle reste une fiche indépendante, soit l'enseignant choisit explicitement la création d'une nouvelle séance contextualisée. Aucun rattachement automatique des anciennes fiches.

## 5. Résultat d'exécution et couverture cumulative

`PLANNED != EXECUTED != COVERAGE`. Une fiche préparée, sa finalisation avant cours, un PDF généré, une durée prévue ou le nombre de séances ne créent aucun résultat d'exécution ni aucune couverture implicite. Sans résultat réel explicitement enregistré pour le contexte et l'instruction, la couverture reste NOT_STARTED, même si plusieurs séances futures contiennent cette instruction.

Le nouveau formulaire saisit le résultat **par instruction**, avec minutes réelles explicites. Interdire la copie implicite d'un DONE global sur tous les segments et la répartition égale automatique des minutes comme preuve de réalisation. Une instruction sans résultat soumis ne produit aucun événement ; l'interface affiche ce qui reste à renseigner avant confirmation.

Proposition de réduction cumulative pour les exécutions du même contexte et de la même instruction :

1. Une déclaration explicite COVERED rend la couverture COVERED.
2. Sinon, au moins une déclaration PARTIAL rend la couverture PARTIAL.
3. Sinon, au moins une déclaration SKIPPED rend la couverture SKIPPED.
4. Sinon, la couverture vaut NOT_STARTED.

Plusieurs PARTIAL ne deviennent jamais COVERED par leur seul nombre ou leur durée. Un SKIPPED après PARTIAL ne supprime pas le travail déjà réalisé : couverture PARTIAL, dernier résultat SKIPPED et signalement conservé. Une réactivation de COVERED autorise une nouvelle préparation sans effacer la couverture acquise. Ces règles d'agrégation sont conservées dans le périmètre final.

La recommandation fondée sur la couverture réelle prend d'abord les PARTIAL, puis les NOT_STARTED et SKIPPED dans l'ordre curriculaire disponible ; les SKIPPED portent un signalement. Les COVERED ne sont ajoutés que sur action explicite. Le professeur confirme la sélection ; pas de clôture automatique ni de génération de contenu officiel. Cette recommandation est distincte de la création anticipée, qui reste disponible sans exécution préalable.

Report temporaire MVP : exclusion explicite **pour cette préparation**, enregistrée dans son instantané avec les instructions concernées. Elle ne modifie pas la couverture et n'empêche pas une nouvelle proposition lors d'une préparation ultérieure. Les instructions exclues restent visibles. Pas de moteur de dates de report en P1.

### Correction du faux DONE et données anciennes

Le compteur d'exécutions ne prouve aucune couverture. Remplacer l'affichage fondé sur `executions > 0` et le calcul DONE fondé sur ce compteur par la projection contextuelle ci-dessus.

Les anciens enregistrements sans PlannedSession restent consultables comme historique non contextualisé. Conserver leurs statuts bruts, y compris DONE, sans les convertir automatiquement en COVERED ni les attribuer à une classe/année supposée. Dans cette vue, présenter le résultat historique et le nombre d'exécutions, avec couverture contextuelle non déterminée ; ne pas afficher une validation verte sur la seule présence d'une exécution. Un futur rapprochement de cet historique relève d'une mission distincte.

## 6. Durées et profil local

| Donnée | Origine et traitement P1 |
|---|---|
| SA_OFFICIAL_DURATION | Valeur sourcée existante, provenance et éventuels conflits conservés ; pas de recalcul par addition des séances. |
| SEQUENCE_PLANNED_DURATION | Minutes locales facultatives du SequencePlan ; ne devient pas une prescription officielle. |
| SESSION_SLOT_DURATION | Créneau brut en minutes, explicitement saisi dans le nouveau parcours. |
| BREAK_DURATION | Minutes locales proposées puis confirmées/modifiées pour la séance. |
| SESSION_PEDAGOGICAL_DURATION | Créneau brut moins pause, calculé une seule fois. |
| ACTUAL_DURATION | Temps effectivement réalisé, saisi à l'exécution et distinct des durées prévues. |
| CURRICULUM_WEEKLY_MASS | 6 h pour la version 4e examinée, avec référence source ; aucune généralisation sans source. |
| TEACHER_ACTUAL_TIMETABLE | Volume hebdomadaire réel facultatif du contexte classe/année, local et configurable ; aucune déduction depuis les pourcentages de progression. |

Proposition minimale : ajouter le volume hebdomadaire réel facultatif à ClassContext. Stocker les durées de séance dans une structure typée et validée de `TeacherSheetRevision.authoring_json`, avec créneau brut, pause, durée pédagogique calculée, origine locale et surcharge éventuelle. Une révision finalisée fige cet instantané ; changer le profil ou SequencePlan ne recalcule jamais une ancienne révision. La durée planifiée de séquence utilisée dans la fiche est également capturée dans l'instantané.

Profil local dans le navigateur, sans compte ni synchronisation supplémentaire : `default_break_minutes = 10`, seuil initial 120 minutes. Sous le seuil : proposition 0 ; au seuil ou au-dessus : valeur du profil. Une surcharge explicite de séance prévaut ; changer de profil n'écrase pas cette surcharge. Validation : créneau > 0, pause ≥ 0 et pause < créneau, minutes entières. Une durée déjà pédagogique provenant de l'ancien parcours n'est jamais réinterprétée comme créneau brut.

Pour le nouveau parcours, affichage et export enseignant utilisent les valeurs typées : durée de séquence et durée pédagogique de séance dans leurs rubriques respectives, créneau/pause explicitement distingués. Aucune extraction de chiffres d'une chaîne libre du type « 1 h 30 ». Les anciennes révisions conservent leurs données et leur chemin de restitution. Un dépassement du budget pédagogique est signalé pour décision du professeur, sans tronquer automatiquement les contenus.

## 7. Migration prévue — uniquement après autorisation P1

Une migration additive après `0004_curriculum_authoring`, proposée sous le nom `0005_planned_sessions` :

1. Créer ClassContext et SequencePlan avec clés étrangères et contraintes d'unicité ; champs locaux de durée/volume hebdomadaire facultatifs et contrôles de positivité.
2. Créer PlannedSession, ses liens et ses contraintes de numéro et de fiche unique.
3. Ajouter à TeachingSession le lien nullable vers PlannedSession et son index. Les anciennes lignes restent NULL.
4. Ajouter les index utiles aux lectures de couverture par contexte et instruction. Réutiliser le stockage existant des segments d'exécution ; accepter les nouveaux codes au niveau du contrat du nouveau parcours sans réécrire les anciens DONE.

Les instructions prévues réutilisent SessionCurriculumSegment, déjà lié à la révision : aucune nouvelle table parallèle nécessaire. Le chemin PlannedSession → fiche → révision → segments prévus conserve explicitement la planification, tandis que TeachingSession → segments exécutés conserve le réalisé. Aucun lien ni instantané historique n'est reconstruit.

Aucun backfill, aucune nouvelle révision historique, aucune mutation de JSON ancien, aucun changement de source, aucun reset de base. Les nouveaux instantanés JSON sont créés seulement par le nouveau parcours. Le modèle de lecture InstructionCoverage ne requiert pas de migration de données.

Vérifier la migration depuis une base au schéma 0004 et depuis une base vide : les anciennes migrations utilisent des créations/contrôles de présence, ce qui impose de vérifier ces deux chemins. Toute adaptation technique nécessaire doit rester additive et compatible avec les données existantes. Tests exclusivement sur bases isolées ; aucune migration sur la base de travail dans la phase de proposition.

## 8. Invariants d'acceptation

- I01 — Une séance planifiée appartient à une seule séquence et un seul contexte classe/année ; plusieurs séances de cette séquence sont autorisées.
- I02 — Numéro positif unique par SequencePlan ; nouvelle révision ≠ nouvelle séance.
- I03 — Exécution liée à une révision finalisée de la fiche attendue ; instruction étrangère à cette préparation refusée.
- I04 — Aucune contribution croisée entre classes, années ou identifiants de curriculum différents.
- I05 — PLANNED != EXECUTED != COVERAGE ; seuls les résultats réels explicitement enregistrés alimentent la couverture. Préparation, FINALIZED, PDF, durée prévue, nombre de séances et répétition de PARTIAL ne prouvent pas COVERED.
- I06 — SKIPPED reste visible et éligible, avec report local explicite ; reprise PARTIAL prioritaire ; COVERED réactivable seulement explicitement.
- I07 — Chaque durée garde son sens, son unité et son origine ; pause locale soustraite exactement une fois.
- I08 — Anciennes révisions, sources, statuts bruts et exports historiques ne sont ni réécrits ni enrichis par inférence.
- I09 — Provenance et validation humaine finale conservées ; aucune finalisation automatique.
- I10 — Aucun plan annuel obligatoire, aucune correction CT8 inventée, aucune cardinalité CTD exactement-un imposée.
- I11 — Sauvegarde avant navigation conservée ; erreur de sauvegarde maintient l'étape, doubles clics protégés.
- I12 — Création anticipée indépendante de l'exécution et de la recommandation ; trois séances peuvent être préparées sans aucun résultat réel.
- I13 — Recommandation séparée, aucune suppression/modification silencieuse des séances futures ; adaptation explicite du brouillon uniquement, nouvelle révision si nécessaire.
- I14 — Programme/guide : autorité curriculaire ; progression officielle applicable : autorité temporelle. Report technique du plan annuel ≠ report de cette autorité ; U6 CLOSED_WITH_CORRECTION.

## 9. Tests d'acceptation à réaliser pendant P1

| Test | Résultat attendu |
|---|---|
| T01 — Deux séances, même séquence/classe/année | Deux fiches et numéros 1/2 ; réviser la première ne crée pas un numéro 3. |
| T02 — Créations concurrentes / double clic | Aucun numéro ni lien de fiche dupliqué ; conflit traité sans écrasement ni création partielle. |
| T03 — Autre subdivision et autre année | Couverture indépendante ; le travail de 4e A ne marque pas 4e B ni l'année suivante. |
| T04 — Aucun résultat, puis SKIPPED seul | NOT_STARTED puis SKIPPED ; jamais COVERED, même avec une exécution enregistrée. |
| T05 — PARTIAL, PARTIAL, puis COVERED explicite | PARTIAL conservé jusqu'à la déclaration explicite ; ensuite COVERED. |
| T06 — PARTIAL puis SKIPPED ; COVERED réactivé | Couverture acquise conservée, dernier résultat et signalement lisibles ; aucun effacement de l'historique. |
| T07 — Prochaine séance | PARTIAL prioritaire, NOT_STARTED/SKIPPED éligibles, saut signalé ; COVERED absent sauf réactivation. |
| T08 — Report temporaire | Exclu de cette préparation uniquement, toujours visible, reproposé lors d'une préparation ultérieure. |
| T09 — Résultats différents dans une même séance | PARTIAL/COVERED/SKIPPED conservés par instruction, minutes saisies sans division automatique. |
| T10 — Créneaux 119, 120 et 130 minutes | Profil initial : pauses 0/10/10, durées pédagogiques 119/110/120. Surcharge et profil configurable testés. |
| T11 — Durées anciennes et entrées invalides | Aucune double soustraction sur durée pédagogique ; pause négative ou ≥ créneau refusée ; « 1 h 30 » jamais traité comme 130 minutes. |
| T12 — Révision finalisée puis changement de profil | Instantané et restitution historique inchangés ; nouvelle préparation utilise le nouveau profil. |
| T13 — Migration 0004 et base vide | Deux chemins réussis sur bases isolées ; anciennes lignes/JSON/statuts conservés, relations anciennes non inférées. |
| T14 — Ancienne exécution DONE/PARTIAL/SKIPPED | Résultat brut consultable ; compteur non converti en DONE/COVERED ; exclusion de la couverture contextuelle non attribuable. |
| T15 — Parcours navigateur et export | Classe → SA → séquence → séance → exécution → prochaine séance fonctionne sans plan annuel ; bonne durée dans la fiche enseignant ; sauvegarde en erreur bloque la navigation. |
| T16 — Garde-fous métier et sécurité des liens | Pas de constante 4,5/5 h, de conversion de pourcentage, de CTD exactement-un ni d'injection automatique des six ; lien incohérent fiche/révision/instruction refusé. |
| T17 — Conservation fonctionnelle | Provenance visible, brouillon modifiable, validation humaine, support apprenant sans réponses attendues ; anciennes révisions non modifiées après les nouveaux parcours. |
| T18 — Instruction prévue mais séance non exécutée | Sans résultat réel préalable, couverture NOT_STARTED ; préparation, durée prévue et export PDF n'apportent aucune couverture. |
| T19 — Fiche finalisée avant le cours | Aucune instruction ne devient COVERED du fait de FINALIZED ; sans résultat réel, couverture NOT_STARTED. |
| T20 — Trois séances préparées à l'avance | Numéros 1/2/3 créés avec leurs instructions prévues, sans exécution préalable ni modification de la couverture. |
| T21 — Prévision et réalisation divergent | Séance 1 prévoit A/B/C ; résultats A=COVERED, B=PARTIAL, C=SKIPPED : couvertures correspondantes correctes, reprise B/C signalée ; séance 2 déjà préparée et révision finalisée de séance 1 inchangées. |
| T22 — Recommandation avec séances futures existantes | Proposition séparée et réconciliable explicitement par l'enseignant ; aucune suppression/modification silencieuse. Une adaptation touche seulement le brouillon choisi, créé par nouvelle révision si nécessaire. |

Les tests ci-dessus sont prévus, pas exécutés dans cet addendum. La conservation des données sera comparée avant/après migration sur un jeu historique représentatif ; les exports seront vérifiés sur leur contenu et leur rendu, sans exiger des octets PDF identiques lorsqu'ils contiennent des métadonnées variables.

## 10. Ordre de réalisation proposé et état de sortie

Lors de la mission d'implémentation ultérieure, réaliser dans cet ordre : (1) modèle et migration additive ; (2) projection cumulative et correction de progression ; (3) création anticipée, recommandation séparée et saisie par instruction ; (4) durées/profil et restitution ; (5) tests T01–T22 et rapport. Ce découpage ne constitue pas une autorisation de commencer dans cette étape documentaire.

Baseline de conception vérifiée : racine `C:/Users/HP/Documents/ChatGPT/Fiche_pedagogique`, branche `fix/ux-bb-001-identification-navigation`, HEAD `578b2a4b49e8284f1885693e368554762bc62e25`. La future mission doit faire confirmer sa baseline autorisée et la vérifier avant toute modification ; ne pas supposer que celle-ci restera courante.

État livré : sept arbitrages fermés, dont U6 CLOSED_WITH_CORRECTION ; trois corrections obligatoires intégrées ; périmètre final avec migration 0005 prévue, 14 invariants et tests T01–T22. Code fonctionnel, base, corpus et migrations inchangés. **P1 non commencée.**

V2_03_R1_P1_READY_FOR_IMPLEMENTATION = YES
