# V2-03-R1-P0 - Consolidation des règles métier sur sources

Date : 2026-09-04. Mission documentaire, lecture seule, avant implémentation.

Révision documentaire du 2026-09-04 : correction métier explicite de l'utilisateur sur U6. `U6 = CLOSED_WITH_CORRECTION`. Elle remplace l'interprétation précédente d'une priorité absolue du guide sur le calendrier annuel ; aucune implémentation supplémentaire n'est autorisée.

Le noyau de compétences 8/6/3, la distinction SA/séquence/séance, le numéro de séance lié à une séquence et la présence de devoirs et de documents utilisés dans les exemples officiels sont documentés. Les statuts informatiques de couverture, l'automatisation, le support apprenant sans réponses et la pause sont des décisions produit distinctes des prescriptions des programmes.

**Correction importante d'interprétation : les nombres 4,5 et 5,5 de la fiche de suivi 4e 2025-2026 sont des pourcentages d'exécution, pas des heures.** Le programme 4e consulté indique 6 heures hebdomadaires. Aucune règle « semaine 4e = 4,5 h ou 5 h » ne peut être validée à partir de ce suivi.

## A. SOURCE AUTHORITY

### Baseline et périmètre

| Contrôle effectué | Résultat |
|---|---|
| Racine | `C:/Users/HP/Documents/ChatGPT/Fiche_pedagogique` |
| Branche | `fix/ux-bb-001-identification-navigation` |
| HEAD | `578b2a4b49e8284f1885693e368554762bc62e25` |
| Diff suivi avant mission | Aucun ; `git diff --check` sans erreur |
| Fichier non suivi à l'entrée | `docs/audits/V2_03_R1_FUNCTIONAL_DELTA_AUDIT.md`, entrée G0 explicitement demandée |
| SHA-256 de G0 | `ce06f0bbe754457778e1dd5fe287c3c8c61c29e87e0f6ebdbebd328facf63c16` |
| Écritures autorisées | Ce rapport seulement ; G0 et corpus conservés intacts |

Le fichier d'entrée non suivi n'est pas un changement de baseline du code ; P0 ne demande pas un worktree vide de ce rapport. Aucun code, migration, commit, export applicatif, base de données ou source métier n'est modifié. Aucun serveur ni test applicatif n'est lancé.

La lecture couvre les sources locales réellement accessibles. Les extractions et rendus de contrôle restent en mémoire : aucun fichier auxiliaire n'est créé. Les recherches de mots portent sur les dix PDF principaux, puis les pages pertinentes sont lues. Des pages sont inspectées visuellement pour contrôler l'organisation des tableaux et des rubriques. Une absence dans ces recherches est une limite du corpus inspecté, pas une preuve d'absence dans tous les textes réglementaires.

### Autorité répartie par fonction

1. Programme officiel.
2. Guide officiel.
3. Progression / planification institutionnelle.
4. Ressource validée par inspection / CP.
5. Fiche de collègue.
6. Manuel / livre.
7. Ressource locale enseignant.

Cette liste identifie les familles de sources ; ses numéros ne constituent pas une priorité absolue applicable à tous les domaines. La correction utilisateur fixe la répartition suivante :

| Source | Domaine d'autorité |
|---|---|
| Programme officiel | Curriculum, compétences, connaissances, contenus prescrits et orientations générales |
| Guide officiel | Indications pédagogiques, découpage opérationnel, instructions et exemples de mise en œuvre |
| Progression annuelle officielle | Cadence et échelonnement de l'exécution pour l'année scolaire concernée : semaines, attentes SA/séquences, ordre temporel, intégration, productions scolaires, remédiation, interruptions et objectifs d'avancement |

`CURRICULUM_AUTHORITY = PROGRAMME + GUIDE`

`YEAR_EXECUTION_AUTHORITY = OFFICIAL_ANNUAL_PROGRESSION`

La progression est produite chaque année par les inspecteurs/l'inspection pédagogique et sert de référence officielle aux enseignants, qui doivent faire l'effort de la suivre pour éviter le retard dans l'exécution. Lorsqu'il s'agit de déterminer **quand** traiter un contenu, elle est la référence opérationnelle de l'année concernée. Elle n'est ni un document local produit par l'enseignant ni une simple ressource consultative. Elle ne modifie pas silencieusement les contenus canoniques ni les prescriptions pédagogiques du guide. Une fiche de collègue, un manuel ou une ressource locale ne peut créer une prescription officielle. Une fiche-exemple incluse dans un guide prouve le modèle illustré, sans rendre toutes ses valeurs obligatoires partout.

Cette répartition fonctionnelle est fondée sur la clarification métier explicite de l'utilisateur, cohérente avec l'identification institutionnelle d'A4. Elle ne résulte pas d'une nouvelle vérification externe des textes.

L'identification institutionnelle repose sur le contenu interne des PDF : ministère, institut ou inspection, titre, édition. Les empreintes identifient les fichiers examinés ; elles ne certifient pas leur chaîne de publication ni leur applicabilité réglementaire actuelle. Aucun contrôle externe de publication n'est revendiqué. Le mot « Certifié » dans un nom de fichier n'est pas utilisé comme preuve suffisante.

### Registre des sources consultées

Toutes les pages citées sont des **pages PDF, numérotées à partir de 1**. P1 compte 80 pages PDF bien que la pagination imprimée annonce « sur 82 » ; P1 PDF 73/74 correspond à imprimé 75/76.

| ID | Fichier réellement lu | Pages PDF | SHA-256 |
|---|---|---|---|
| P4 | [930040566-programme-4ieme-Maths-certifie.pdf](<C:/Users/HP/Desktop/Base/4ème/930040566-programme-4ieme-Maths-certifie.pdf>) | 127 | `7795dd2370db4c879187f5fcbc7247babcab2ab0a3fd9d9f579663d0114fd62d` |
| G4 | [783063322-GUIDE-4eme-Maths-Certifie-Vu.pdf](<C:/Users/HP/Desktop/Base/4ème/783063322-GUIDE-4eme-Maths-Certifie-Vu.pdf>) | 100 | `a6e937b03da51229e3c23d16a7105caa4338bc29b4853b27374a1977e4bfab93` |
| P6 | [930025828-Programme-6e-Math-Certifie.pdf](<C:/Users/HP/Desktop/Base/6èmé/930025828-Programme-6e-Math-Certifie.pdf>) | 137 | `47c9cd33af1073158270a58cb6d6de2e58e9bb544466d4552ffb0f3c3ed71df7` |
| G6 | [Guide 6èMaths_ vf sept21 gsmaths.pdf](<C:/Users/HP/Desktop/Base/6èmé/Guide 6èMaths_ vf sept21 gsmaths.pdf>) | 66 | `a32666b7b5d426298d5c629d469b33d03b9b81d6b7bf64f3fa284b1beb6d7ff2` |
| P1 | [696438897-PPC-1ere-C-VEROFF.pdf](<C:/Users/HP/Desktop/Base/1ère/C/696438897-PPC-1ere-C-VEROFF.pdf>) | 80 | `064c2a4bdb8ab71e97d55bc57a52a8e1edc5cf2a3dae10116f878256cfcd8469` |
| A4 | [4e_Fiche de suivi de progression_25-26.pdf](<C:/Users/HP/Desktop/Base/4ème/4e_Fiche de suivi de progression_25-26.pdf>) | 4 | `7c4279a99bae8b31ec4e9ddf9c8c408cfe6799c93822abcd0e1c6537fc697b2f` |
| F4 | [Fiches de 4è Firm.pdf](<C:/Users/HP/Desktop/Base/4ème/Fiches de 4è Firm.pdf>) | 68 | `32120ee72565e4f28def911be13fb2530208c860ccb0e68cd2637411544056d6` |
| F4b | [pa.pdf](<C:/Users/HP/Desktop/Base/4ème/pa.pdf>) | 60 | `f7e75036a877c76c66f018a072bf59602891181361929f978b583dc6ff2ce5fc` |
| F6 | [FICHE ENSEIGNANT MATHS 6ème NVF 24-25.pdf](<C:/Users/HP/Desktop/Base/6èmé/FICHE ENSEIGNANT MATHS 6ème NVF 24-25.pdf>) | 36 | `439f383d4feed2c6323d47c9869f54177d8a8c18ad4401c6028cf948cd0c3330` |
| S1 | [1ère C cour complet.pdf](<C:/Users/HP/Desktop/Base/1ère/C/1ère C cour complet.pdf>) | 98 | `467813dcc67ac210dc5b15ee0c4794b457ddfdde1b6e9344987052dc9ebdac5c` |

| Référence | Édition / autorité observée | Pages mobilisées pour les règles |
|---|---|---|
| P4 | Programme 4e, ministère/INIFRCF ; couverture version relue août 2020, en-tête septembre 2020 ; rang 1 | 1, 12, 16-17, énoncés CT/CTD listés en E, 68, 72, 76, 89-90 |
| G4 | Guide 4e, ministère/INIFRCF, septembre 2020 ; rang 2 | 1, 3-5, 10, 24, 31-32, 66-79 |
| P6 | Programme 6e, ministère/INIFRCF, octobre 2020 ; rang 1 | 1, 13, 18-19, énoncés CT/CTD listés en E, 77, 81, 86, 100 |
| G6 | Guide 6e, ministère/INIFRCF, version relue octobre 2020, malgré le nom « sept21 » ; rang 2 | 1, 3-5, 10, 42-53 |
| P1 | Programme Première C, Direction de l'inspection pédagogique, juillet 2010 ; rang 1 | 1, 9, énoncés CT/CTD listés en E, 57, 60, 64, 67, 73-74 |
| A4 | Fiche de suivi, Inspection générale pédagogique ; datée Cotonou 20 août 2025, Eric CAKPO, CGPS/Mathématiques ; rang 3 | Les quatre pages ; planification 2025-2026 |
| F4 | Fiches de 4è Firm ; document pédagogique secondaire, validation institutionnelle non établie ; rang 5 retenu prudemment | 1-3, 26 ; échantillon de planification |
| F4b | `pa.pdf`, édition septembre 2024, noms d'auteurs en couverture et nom d'enseignant dans la fiche ; rang 5 | 1-2, 5, 8, 22, 32, 34 |
| F6 | Fiche enseignant 6e, première édition septembre 2024, auteurs en couverture ; rang 5 | 1-2, 4-5 |
| S1 | Cours Première C, Collection O.R.O, ORO et MANGOU ; ressource secondaire, rang 6, sans validation d'inspection établie | 5-6 ; organisation d'un support de cours |

Deux variantes ont été repérées : guide 4e `Guide 4èMaths_ vf sept21 gsmaths.pdf` (104 pages, SHA-256 `629ba6f3374d487cfa6157c8586fad414186865cfdc75c79075c246321920297`) et guide 6e `588119763-Guide-Math-6e-Relu-Juillet-2013.pdf` (53 pages, couverture **août 2013**, SHA-256 `7ae9c58c47130664ecf389a7e90cb558617bc3245735b1c9bc0776f8c02bba3e`). Elles ne sont pas substituées aux versions G4/G6 choisies. Leur comparaison exhaustive est différée ; ne pas déplacer les citations de pages entre versions.

Contrôles visuels directs : A4 p.1 (colonnes en %), G4 p.73 (devoirs/documents/identification), G6 p.42 (séance et compétences), P4 p.12 (masse horaire et 8/6/3), P6 p.40 (anomalie de contexte), P1 p.57 (énoncé/contexte distincts), G4 p.67 (durée de planification). Les autres constats textuels ne sont pas présentés comme des inspections visuelles exhaustives.

### Classification

| Classification demandée en section 3 de la mission | STATUS du tableau de décision |
|---|---|
| CONFIRMED_BY_OFFICIAL_SOURCE | OFFICIAL_CONFIRMED |
| CONFIRMED_BY_MULTIPLE_SOURCES | MULTI_SOURCE_CONFIRMED |
| SUPPORTED_BY_PRACTICE_ONLY | PRACTICE_CONFIRMED |
| USER_BUSINESS_DECISION | USER_DECISION |
| INSUFFICIENT_EVIDENCE | INSUFFICIENT_EVIDENCE |
| CONFLICTING_SOURCES | CONFLICT |
| Conséquence fonctionnelle proposée à partir de faits établis | DERIVED_PRODUCT_RULE |

`SOURCE_FACT` désigne ce que le document montre ; `USER_DECISION` une exigence utilisateur déjà fixée ou un arbitrage explicitement ouvert ; `DERIVED_RULE` une conséquence métier, classée `DERIVED_PRODUCT_RULE` lorsqu'elle concerne le logiciel. L'autorité d'une décision utilisateur est **produit**, pas officielle.

## B. SESSION / SEQUENCE RULES

**SOURCE_FACT.** G4 p.3 définit la séquence comme un regroupement cohérent de contenus d'une SA. G4/G6 p.4 distinguent expressément une SA d'une fiche pédagogique. G4 pp.66 et 73, G6 p.42 affichent SA, séquence puis séance ; ils précisent que le numéro de séance est lié à la séquence. Cela confirme une numérotation locale à cette séquence, sans prescrire le schéma SQL ni les règles de renumérotation.

**Convergence des sources.** G4 p.79 répartit les triangles sur les semaines 3-5 ; le calcul algébrique revient en semaines 9-10 avec « suite et fin ». A4 pp.1-2 reprend des contenus sur plusieurs semaines ; A4 pp.3-4 partage même la semaine pédagogique 20 avant et après les congés. G6 p.53 montre également des contenus repris d'une semaine à l'autre. Ces faits, rapprochés du numéro de séance lié à la séquence, soutiennent un déroulement en plusieurs séances et sa reprise. Ils ne fixent pas combien de séances contient chaque séquence.

**USER_DECISION / DERIVED_RULE.** Autoriser une séance sur une partie de la séquence et une instruction partiellement traitée est conforme à la cible explicite G0/P0. La granularité informatique par instruction ne figure pas dans A4, qui suit des activités et des taux. Retenir une couverture par classe/année est une règle produit nécessaire pour ne pas mélanger les groupes ; le guide parle d'un groupe précis dans un contexte donné, A4 d'une promotion et d'une année.

| Question | Conclusion bornée |
|---|---|
| Une séquence peut-elle s'étaler sur plusieurs séances ? | Oui, modèle soutenu par guides + progression ; cardinalité détaillée non prescrite |
| Une séance peut-elle couvrir une partie d'une séquence ? | Oui pour le produit demandé ; ne pas déclarer l'ensemble couvert dès cette séance |
| Une séquence peut-elle reprendre la séance suivante ? | Oui ; les reprises sont documentées à l'échelle hebdomadaire, leur gestion par séance est dérivée |
| Une instruction peut-elle être partiellement traitée ? | Oui comme capacité métier demandée ; pas de preuve d'un registre officiel utilisant précisément cette unité et les quatre statuts |

G4 p.5 demande de terminer une SA avant d'en commencer une autre. Cette instruction reste distincte d'un exercice de réactivation sur une notion ancienne : réactiver une notion ne signifie pas changer la SA en cours.

**Anomalie à conserver :** le tableau détaillé G4 pp.31-32 porte « Séquence 8 : Calculs sur les expressions algébriques », alors que sa fiche-exemple p.73 porte « Séquence N°1 ». Ne pas remapper le curriculum SEQ8 à partir du numéro de cet exemple. Les numéros de fiches de collègues ne sont pas non plus des identifiants canoniques.

## C. INSTRUCTION COVERAGE RULES

Les quatre codes sont un vocabulaire du produit, pas une nomenclature officielle retrouvée dans les documents.

| Statut | Sens minimal prêt à implémenter | Conséquence |
|---|---|---|
| NOT_STARTED | Aucune partie déclarée traitée dans le contexte classe/année considéré | Instruction disponible pour préparation |
| PARTIAL | Une partie est déclarée traitée, une autre reste à traiter | Ne compte pas comme COVERED ; reste éligible |
| COVERED | L'enseignant déclare la couverture complète de l'instruction | Non reproposée par défaut pour le traitement courant ; réactivation explicite possible |
| SKIPPED | Instruction écartée/non traitée lors de la séance considérée | Ne compte pas comme COVERED ; reste visible avec la décision de l'enseignant |

Ces sens minimaux sont autorisés par la mission. **Le devenir de SKIPPED reste à arbitrer** : report automatique à la prochaine séance, exclusion temporaire explicite, ou sélection manuelle. Aucune source ne choisit entre ces comportements.

Une exécution SKIPPED ne doit pas effacer une couverture PARTIAL antérieure. Une séance de réactivation ne doit pas faire régresser une instruction déjà COVERED. Séparer le résultat d'une exécution de l'état cumulé est la règle produit minimale qui évite ces contradictions ; la politique exacte de SKIPPED dans la proposition automatique attend l'arbitrage U1.

Ne pas convertir un nombre d'exécutions, une durée ou un pourcentage de plan annuel en achèvement d'une instruction. La couverture du contenu n'est pas une certification de maîtrise des élèves. Le défaut G0 qui produit DONE dès qu'une exécution existe est incompatible avec ces règles, indépendamment de l'arbitrage U1.

## D. DURATION RULES

| Concept | SOURCE_FACT | Règle produit / limite |
|---|---|---|
| SA_DURATION | G4 pp.66/73 : 60 h en identification de SA ; P4 p.90 : 56 h dans planification SA1 ; G6 p.42 : SA3 20 h | Valeur de SA séparée, sourcée et versionnée ; conflit 4e conservé |
| SEQUENCE_PLANNED_DURATION | Séquences et répartition hebdomadaire existent, mais pas de volume propre validé pour la séquence pilote dans les pages examinées | Durée planifiée distincte, renseignée localement ou par source ; aucune conversion des % d'A4 |
| SESSION_SLOT_DURATION | Aucun emploi du temps de classe donnant les créneaux effectivement disponibles n'a été fourni dans le corpus examiné | Temps calendaire disponible saisi/configuré par l'enseignant |
| BREAK_DURATION | Aucune pause de dix minutes retrouvée dans les dix PDF principaux par les recherches ciblées | Valeur locale explicite ; dix minutes n'est pas une obligation officielle ni une valeur par défaut déjà validée |
| SESSION_PEDAGOGICAL_DURATION | G4 p.67 / G6 p.43 : 1 h 50 min ; G4 p.74 / G6 p.48 : 55 min dans la planification d'exemples | Temps destiné aux activités ; ces exemples ne démontrent pas à eux seuls le créneau brut ou la pause |

**DERIVED_RULE :** lorsque le créneau inclut toutes les pauses retirées du temps d'enseignement, `SESSION_PEDAGOGICAL_DURATION = SESSION_SLOT_DURATION - BREAK_DURATION`, avec unités cohérentes et `0 <= BREAK_DURATION <= SESSION_SLOT_DURATION`. Ne pas soustraire une pause une deuxième fois à une durée déjà pédagogique. Si l'enseignant saisit 120 min de créneau et 10 min de pause, 110 min est un calcul, pas une preuve documentaire de cette organisation.

**Conflit SA1 4e :** dans le domaine de l'allocation curriculaire, la référence programme reste **56 h** pour P4 ; les **60 h** de G4 demeurent une valeur source contradictoire. La correction U6 concerne la cadence annuelle et ne résout ni n'efface cette divergence d'allocation. Elle n'autorise pas à réécrire les fiches historiques. Les 55/110 minutes des exemples ne sont pas des durées universelles de séquence.

### Heures hebdomadaires : rectification source

| Source | Valeur observée | Portée |
|---|---|---|
| P4 p.12 | 6 heures | Masse horaire hebdomadaire de l'édition 4e examinée |
| P6 p.13 | 5 h | Sixième, pas quatrième |
| P1 p.9 | 7 heures | Première C, édition 2010 |
| A4 p.1 | 5,5 puis 4,5 | Colonnes **Taux d'exécution %**, pas heures |
| A4 p.4 | 100 | Taux cumulé prévu atteint en semaine 22, pas volume horaire |

Une semaine effective de 4,5 h ou 5 h en 4e nécessiterait une preuve d'emploi du temps ou une instruction institutionnelle applicable. La durée pédagogique locale peut différer d'une masse horaire prescrite, mais aucune conversion automatique n'est autorisée par ces données. Les heures locales, la durée normative et les taux de progression doivent rester trois valeurs distinctes.

## E. COMPETENCY RULES

### Noyau 8/6/3 confirmé et comparaison des libellés

P4 p.12, P6 p.13 et P1 p.9 annoncent explicitement huit compétences transversales, six transdisciplinaires et trois disciplinaires. Le tableau suivant compare les **énoncés**, pas l'intégralité des capacités, critères et contextes. Les libellés sont présentés avec espaces/ponctuation harmonisés pour lecture ; les textes sources doivent rester conservés par version.

| Repère documentaire | Libellé général | P6 PDF | P4 PDF | P1 PDF | Comparaison |
|---|---|---|---|---|---|
| CT1 | Exploiter l'information disponible | 22 | 20 | 14 | Même libellé lexical après normalisation typographique |
| CT2 | Résoudre une situation-problème | 24 | 22 | 15 | Même libellé ; espacements autour du trait d'union |
| CT3 | Exercer sa pensée critique | 27 | 24 | 17 | Même libellé |
| CT4 | Exercer sa pensée créatrice | 29 | 26 | 19 | Même libellé |
| CT5 | Gérer ses apprentissages ou un travail à accomplir | 32 | 29 | 21 | Même libellé |
| CT6 | Travailler en coopération | 35 | 31 | 24 | Même libellé |
| CT7 | Faire preuve de sens éthique | 37 | 33 | 25 | Même libellé |
| CT8 | Communiquer de façon précise et appropriée | 40 | 35 | 27 | Même libellé ; anomalie de contexte P6 ci-dessous |
| CTD1 | Affirmer son identité personnelle et culturelle dans un monde en constante évolution | 43 | 38 | 31 | Même libellé hors ponctuation finale |
| CTD2 | Agir individuellement et collectivement dans le respect mutuel et l'ouverture d'esprit | 47 | 42 | 34 | Même libellé hors ponctuation finale |
| CTD3 | Se préparer à intégrer la vie professionnelle dans une perspective de réalisation de soi et d'insertion dans la société | 52 | 47 | 38 | Même libellé hors ponctuation finale |
| CTD4 | Pratiquer de saines habitudes de vie sur les plans de la santé, de la sexualité et de la sécurité | 59 | 52 | 42 | Même libellé hors typographie |
| CTD5 | Agir en harmonie avec l'environnement dans une perspective de développement durable | 65 | 57 | 47 | Même libellé hors ponctuation finale |
| CTD6 | Agir en consommateur averti par l'utilisation responsable de biens et de services | 70 | 62 | 51 | Même libellé hors typographie |
| CD1 | Résoudre un problème ou une situation-problème en utilisant les concepts et procédures du langage et du raisonnement mathématique | 77 | 68 | 57 | Quasi identique : les cadres P4/P6 portent « langage du raisonnement », tandis que leurs paragraphes explicatifs et P1 portent « langage et du raisonnement » |
| CD2 | Appréhender les mathématiques dans leurs aspects géométriques, par les outils et démarches propres à la géométrie | 81 | 72 | 60 | Résumé comparatif ; source P4/P6 « les mathématiques dans ses aspects », P1 « la mathématique dans ses aspects » ; conserver les variantes |
| CD3 | Appréhender les mathématiques dans leurs aspects numériques, par les outils, techniques, procédés et le traitement des données | 86 | 76 | 64 | Résumé comparatif ; variations « les mathématiques / la mathématique » et ponctuation ; même noyau métier |

Conclusion : les 14 libellés CT/CTD concordent lexicalement après normalisation ; les trois CD sont quasi identiques. Une identité globale commune est défendable, mais **pas l'effacement des variantes ni l'affirmation que tous les contextes sont identiques**. CD2 est géométrique et CD3 numérique dans les cadres numérotés : ne pas attribuer ces numéros selon l'ordre d'une liste de SA qui présente parfois numérique avant géométrique.

### Contexte distinct et sélection de fiche

P4 p.16 et P6 p.18 distinguent énoncé, contexte de réalisation/évaluation et critères. Pour CD1, P4 p.68 et P6 p.77 mentionnent au plus trois pas de déduction ; P1 p.57 mentionne au moins deux. Les contextes des CT/CTD indiquent généralement la classe concernée. Ces différences ne créent pas de nouvelles compétences globales.

**Anomalie documentaire confirmée visuellement :** P6 p.40, dans le contexte de CT8, indique des situations prévues « en troisième », alors que le document est celui de sixième. Conserver l'extrait et signaler l'anomalie ; aucune correction silencieuse ni affectation de ce contexte à la troisième. L'import du contexte corrigé attend U4, sans bloquer le libellé CT8 lui-même.

G4 p.32 contextualise des compétences au calcul algébrique. G4 p.74 sélectionne deux CD, une CTD et trois CT pour sa fiche-exemple ; G6 p.42 en sélectionne trois CD, une CTD et trois CT. P1 p.73 sélectionne deux CD, une CTD et cinq CT. F4b/F6 p.2 choisissent aussi un sous-ensemble avec une CTD. F4 p.1 en retient une avec cinq CT. Cela montre une **sélection contextualisée**, pas l'obligation d'afficher tout le catalogue sur chaque fiche.

La cardinalité « exactement une CTD dans toute fiche » n'est pas démontrée. Les exemples en montrent une ; la règle produit ne doit pas imposer cette restriction sans arbitrage. De même, une valeur contextualisée dans un exemple de fiche n'est pas une prescription applicable à toutes les séances de la séquence.

Modèle fonctionnel retenu : `GLOBAL_COMPETENCY_CATALOG` identifie la compétence ; `CURRICULUM_CONTEXT` conserve version, niveau/classe, SA/séquence, libellé contextualisé et preuve d'applicabilité ; `SHEET_SELECTION` conserve le choix de l'enseignant pour la séance. Cette séparation est une **DERIVED_PRODUCT_RULE**, non une exigence de stockage dictée par les programmes.

## F. HOMEWORK RULES

G4 pp.73/78 comporte « Exercices de maison » avec références à des exercices CIAM ; G6 pp.47/52 donne des exercices dans cette rubrique. F4b pp.22/32/34 montre une pratique similaire. Le rôle de travail donné à la maison est donc documenté dans plusieurs exemples officiels et secondaires. Leur existence ne prouve ni une quantité obligatoire ni un devoir obligatoire après toute séance.

Les exercices G6 p.47 concernent le parallélogramme et la symétrie étudiés ; G6 p.52 travaille les fractions. Le rattachement à la notion courante est soutenu. G6 p.47 explique aussi qu'une propriété admise en SA2 est démontrée après l'étude de la symétrie en SA3 : **admettre et démontrer sont deux instructions différentes**, même lorsqu'elles portent sur le même énoncé. Il ne faut pas marquer automatiquement la seconde couverte parce que la première l'a été.

Les programmes demandent d'entretenir les acquis (P4 p.12, P6 p.13, P1 p.9). Cela soutient la réactivation en général, mais ne prescrit pas explicitement la fonction informatique « ajouter un devoir sur une notion passée à la séance courante ». Cette possibilité est une **USER_DECISION déjà demandée en G0**, recevable et prête à être prévue dans le modèle.

Le contrat HOMEWORK_EXERCISE demandé conserve classe/niveau, une ou plusieurs notions, séquence, instructions facultatives, source et validation. Son usage dans une séance distingue CURRENT_NOTION et PRIOR_NOTION_REACTIVATION. La réactivation ne modifie ni le périmètre courant ni sa couverture : règle produit dérivée de la séparation entre ressources et prescription.

### Typologie liée au finding RES

Les guides distinguent consignes, propriétés, définitions, exercices, démonstrations, éléments de réponse et prises de notes. G4 p.5 distingue propriétés à démontrer, démontrables selon conditions, et à admettre. Cela prouve une différence de traitement pédagogique ; cela ne constitue pas une nomenclature officielle exhaustive de types de blocs.

Les cinq codes DISCOVERY_CONSIGNE, APPLICATION_CONSIGNE, DECONTEXTUALIZATION_CONSIGNE, DEEPENING_CONSIGNE et DEMONSTRATION_CONSIGNE, ainsi que HOMEWORK_EXERCISE/REACTIVATION_EXERCISE, sont classés **USER_DECISION** comme vocabulaire produit demandé. Définition, propriété, théorème, formule, méthode, règle et remarque restent des contenus distincts du résultat attendu. Leur présence dans un catalogue de types ne permet pas d'introduire des notions non prescrites : P4 p.12 et P6 p.13 limitent les définitions à donner à celles citées par le programme.

## G. DOCUMENTS USED RULES

**SOURCE_FACT :** G4 pp.73/78 et G6 p.47 présentent « Documents utilisés » sous forme d'une liste. Elle cite programme/guide et des manuels. Il s'agit de références documentaires, pas de la liste du matériel matériellement apporté en classe. Les listes observées ne portent ni empreintes ni identifiants informatiques.

**DERIVED_PRODUCT_RULE :** retenir une section hybride, déjà ciblée par G0 : liste automatique tirée des sources des ressources réellement sélectionnées, complétée manuellement. Les sources du préremplissage (programme/guide) peuvent également contribuer lorsqu'elles ont été utilisées. Dédupliquer par identité documentaire et version, pas seulement par nom de fichier ; préserver une entrée manuelle identifiable ; conserver la liste dans la révision et l'imprimer dans le PDF enseignant.

La génération automatique n'est **pas** une OFFICIAL_REQUIREMENT. Le choix hybride dérive du modèle de provenance et répond à la demande produit. Un simple texte libre reste acceptable pour une référence manuelle dont le document n'est pas encore enregistré ; cette entrée ne reçoit pas artificiellement une empreinte ou un statut officiel.

## H. LEARNER SUPPORT RULES

G4 pp.71-74 et G6 pp.43-47 séparent consignes, résolution/éléments de réponse et éléments à retenir ; ce sont des documents destinés à l'enseignant. S1 p.6 présente une consigne et une définition distincte dans un support de cours, avec séparateurs. F4b/F6 p.2 distinguent aussi résultats attendus et définition/propriété/« Retenons », mais leurs réponses sont incluses dans la fiche enseignant : ces fichiers ne prouvent pas une interdiction officielle générale de distribuer une correction.

| Règle | Fondement |
|---|---|
| EXPECTED_RESPONSE réservé à l'enseignant dans le support produit | USER_DECISION explicite G0/P0, cohérente avec la distinction documentaire ; pas une interdiction officielle démontrée |
| DEFINITION/PROPERTY/FORMULA/METHOD peuvent apparaître côté apprenant | Décision produit G0, appuyée par la pratique du support S1 ; pas de suppression au seul motif qu'il s'agit d'un savoir à retenir |
| Pas de grande zone de réponse générée par défaut | USER_DECISION G0 ; l'absence d'espace sur un exemple ne constitue pas une norme générale |
| Consignes et figures conservées | USER_DECISION G0, soutenue par les exemples de guides et S1 |

Ne pas assimiler toute définition figurant après une résolution à une réponse attendue. Le typage doit conserver l'énoncé de cours séparé des réponses à la consigne. Une réponse mal typée comme consigne demeure un problème de qualification du contenu ; cette mission ne prétend pas le résoudre par analyse automatique du texte.

## I. ANNUAL PROGRESSION RULES

A4 est une planification institutionnelle de **promotion quatrième, année 2025-2026**. Elle présente trimestre, mois, semaine, SA, activités, taux d'exécution prévu/réalisé, taux cumulé prévu/réalisé et observations. Les colonnes réalisées sont des champs à remplir dans le document examiné : il n'atteste pas l'exécution effective d'une classe.

Les périodes d'intégration, productions scolaires, comptes rendus, remédiation/consolidation, congés et autres activités sont explicitement présentes. La semaine pédagogique 20 commence les 30 mars-1er avril et finit les 16-17 avril après interruption. Un modèle annuel doit pouvoir représenter ce découpage sans transformer deux lignes en deux semaines pédagogiques indépendantes.

`OFFICIAL_ANNUAL_PROGRESSION != CURRICULUM` : programme/guide fixent contenus et prescriptions pédagogiques ; la progression officielle fixe leur cadence annuelle. Le suivi d'une classe/groupe relie les séances effectivement réalisées à cette référence institutionnelle sans transformer celle-ci en production locale de l'enseignant. Le stockage et l'exploitation de cette référence ne doivent pas modifier les contenus ni les durées normatives du curriculum.

**U6 fermé avec correction :** G4 p.79 achève les triangles en semaine 5 et place polygones/nombres décimaux en semaine 6 ; A4 pp.1-2 reprend les triangles jusqu'en semaine 6, avec polygones. Cette différence d'échelonnement ne justifie plus de bloquer A4 au motif d'une priorité absolue du guide. Pour la cadence de quatrième en **2025-2026**, A4 est la référence opérationnelle officielle conformément à la clarification utilisateur. Les contenus et prescriptions pédagogiques restent régis par programme/guide. La différence entre documents demeure traçable ; A4 n'est pas automatiquement applicable à une autre année scolaire.

### Futur périmètre fonctionnel : OfficialAnnualProgression

Le modèle cible doit prévoir une référence institutionnelle versionnée distincte du suivi enseignant :

| Champ / composante | Rôle |
|---|---|
| `school_year` | Année scolaire d'applicabilité |
| `class_level` | Niveau/promotion visé ; distinct de la subdivision de classe suivie |
| `issuing_authority` | Inspection ou autorité institutionnelle émettrice |
| `source_document` | Document officiel de référence |
| `weeks / periods` | Semaines et périodes, y compris une semaine pédagogique répartie sur plusieurs intervalles |
| `SA / sequence expectations` | SA/séquences attendues, ordre temporel et objectifs d'avancement |
| `integration periods` | Périodes d'intégration |
| `assessment periods` | Productions scolaires / évaluations |
| `remediation periods` | Remédiations prévues |
| `interruptions` | Congés et autres interruptions |
| `version / provenance` | Version, origine et références de traçabilité |

Le futur lien entre cette référence et les séances d'une classe/année doit permettre la comparaison **prévu/réalisé**, l'identification du **retard ou de l'avance**, la **prochaine séquence attendue** et la **prochaine séance à préparer**. Les attentes institutionnelles et les déclarations d'exécution restent séparées ; aucun taux du document n'est converti automatiquement en heures ou en couverture acquise.

**U5 reste ouvert uniquement sur le calendrier de livraison** du stockage et des écrans associés. Le caractère officiel, l'autorité sur la cadence et la présence d'OfficialAnnualProgression dans la cible ne sont plus à arbitrer. Différer l'implémentation ne doit pas ramener la progression au statut consultatif/local. Aucun stockage, lien de données ni automatisme n'est implémenté dans cette correction documentaire.

## J. RULES READY FOR IMPLEMENTATION

### Tableau de décision obligatoire

`IMPLEMENT_NOW = YES` signifie **règle suffisamment définie pour une mission ultérieure**, jamais autorisation de coder pendant P0. Les dépendances techniques de G0 restent applicables. `MIGRATION_REQUIRED` est prospectif : YES pour nouveaux objets/liens ou données versionnées, NO pour règle de service/rendu ou simple constat, TBD si le besoin dépend du mode de livraison/arbitrage. Une ligne prête peut conserver un conflit documentaire lorsque la hiérarchie imposée détermine déjà la valeur de référence et exige de préserver l'autre.

`HUMAN_DECISION_REQUIRED = NO` pour une décision utilisateur déjà explicitement posée dans G0/P0 ou dans la correction U6 ; pas de redemande d'autorisation pour ces exigences. Les seuls YES correspondent aux six arbitrages encore ouverts : U1-U5 et U7.

| RULE_ID | DOMAIN | RULE | EVIDENCE_SOURCE | AUTHORITY_LEVEL | STATUS | IMPLEMENT_NOW | MIGRATION_REQUIRED | HUMAN_DECISION_REQUIRED | NOTES |
|---|---|---|---|---|---|---|---|---|---|
| A01 | Sources | Répartir l'autorité par fonction : programme/guide pour curriculum et pédagogie, progression officielle pour cadence annuelle | Correction utilisateur U6 ; G4 p.4-5 ; A4 | Clarification métier de l'autorité institutionnelle | USER_DECISION | YES | NO | NO | Pas de priorité absolue unique sur tous les domaines |
| A02 | Sources | Une référence secondaire ne crée pas une prescription officielle | Mission §1 ; G4 p.66 | Produit ; rang 2 | USER_DECISION | YES | NO | NO | Garder nature exemple/adaptation et provenance |
| B01 | Séance | Une SA n'est pas une fiche pédagogique | G4/G6 p.4 | 2 | MULTI_SOURCE_CONFIRMED | YES | YES | NO | Éviter fusion des objets |
| B02 | Séquence | La séquence regroupe des contenus cohérents d'une SA | G4 p.3 | 2 | OFFICIAL_CONFIRMED | YES | NO | NO | Définition documentaire |
| B03 | Séance | Numéro de séance rattaché à sa séquence | G4 pp.66/73 ; G6 p.42 | 2 | MULTI_SOURCE_CONFIRMED | YES | YES | NO | Ne pas utiliser revision_number |
| B04 | Séance | Prévoir plusieurs séances, des parties et la reprise d'une séquence | G4 p.79 ; G6 p.53 ; A4 pp.1-2 ; G0 | 2/3 ; produit | MULTI_SOURCE_CONFIRMED | YES | YES | NO | Convergence, pas cardinalité chiffrée prescrite |
| B05 | Instruction | Autoriser le traitement partiel d'une instruction | G0 §3 ; P0 §4 | Produit | USER_DECISION | YES | YES | NO | Granularité de suivi demandée, non issue d'A4 |
| B06 | Séance | Isoler séances/couverture par classe et année | G4/G6 p.4 ; A4 p.1 ; G0 | 2/3 ; produit | DERIVED_PRODUCT_RULE | YES | YES | NO | Groupe précis et année ne sont pas le curriculum canonique |
| B07 | SA | Terminer une SA avant de passer à une autre | G4 p.5 | 2 | OFFICIAL_CONFIRMED | YES | NO | NO | Réactivation d'une notion antérieure distincte du changement de SA |
| B08 | Séquence | Ne pas remapper SEQ8 depuis « Séquence N°1 » de l'exemple | G4 pp.31-32/73 | 2 | CONFLICT | YES | NO | NO | Garder les deux occurrences ; suivre la structuration détaillée du curriculum |
| C01 | Couverture | Exposer NOT_STARTED, PARTIAL, COVERED, SKIPPED | P0 §5 | Produit | USER_DECISION | YES | YES | NO | Vocabulaire logiciel |
| C02 | Couverture | PARTIAL ne compte pas comme COVERED | P0 §5 | Produit | USER_DECISION | YES | NO | NO | Déclaration partielle conservée |
| C03 | Couverture | SKIPPED ne compte pas comme COVERED | P0 §5 | Produit | USER_DECISION | YES | NO | NO | Corriger le raisonnement fondé sur le seul nombre d'exécutions |
| C04 | AUTO | PARTIAL reste éligible à une prochaine séance | P0 §5 | Produit | USER_DECISION | YES | NO | NO | Proposer le reste, pas inventer sa quantité |
| C05 | AUTO | COVERED n'est pas reproposé par défaut | P0 §5 | Produit | USER_DECISION | YES | NO | NO | Réactivation explicite possible |
| C06 | Couverture | SKIPPED reste visible comme non traité/écarté | P0 §5 | Produit | USER_DECISION | YES | NO | NO | Visibilité acquise ; politique future séparée |
| C07 | AUTO | Définir le devenir automatique de SKIPPED | P0 §5 ; aucune règle source identifiée | Produit | USER_DECISION | NO | TBD | YES | U1 : report, exclusion temporaire ou reprise manuelle |
| C08 | Couverture | Distinguer résultat d'exécution et couverture cumulative | P0 §5 ; G0 SEQ-002 | Produit | DERIVED_PRODUCT_RULE | YES | YES | NO | Ni durée ni nombre d'exécutions ne prouve COVERED |
| D01 | Durées | Distinguer durée SA et durée de la séance planifiée | G4 pp.66-67/73-74 ; G6 pp.42-43/47-48 | 2 | MULTI_SOURCE_CONFIRMED | YES | YES | NO | Deux portées dans les fiches-exemples |
| D02 | Durées | Référence SA1 P4 = 56 h ; conserver G4 = 60 h en conflit | P4 p.90 ; G4 pp.66/73 ; mission §1 | 1/2 ; produit | CONFLICT | YES | TBD | NO | Priorité programme déjà imposée ; pas de réécriture historique |
| D03 | Durées | Accepter 110 min et 55 min comme exemples, sans durée universelle | G4 pp.67/74 ; G6 pp.43/48 | 2 | MULTI_SOURCE_CONFIRMED | YES | NO | NO | Ne prouve pas une pause ni un créneau brut |
| D04 | Durées | Séparer créneau/pause et calculer le temps pédagogique net | G0 §4 ; P0 §6 | Produit | DERIVED_PRODUCT_RULE | YES | YES | NO | Soustraction si créneau brut ; unités et bornes explicites |
| D05 | Durées | Choisir éventuellement une pause par défaut de 10 min | P0 §6 ; recherche négative bornée | Produit | USER_DECISION | NO | TBD | YES | U2 : portée et valeur par défaut non fixées |
| D06 | Durées | Lire 4,5/5,5 d'A4 comme pourcentages | A4 p.1, en-têtes de colonnes ; p.4 cumul 100 | 3 institutionnel | OFFICIAL_CONFIRMED | YES | NO | NO | Ne jamais importer comme planned_hours |
| D07 | Durées | Conserver 6 h hebdomadaires pour la version P4 examinée | P4 p.12 ; comparaison P6 p.13, P1 p.9 | 1 | OFFICIAL_CONFIRMED | YES | YES | NO | Version locale identifiée ; pas certification du régime actuel |
| D08 | Durées | Fixer 4,5 h ou 5 h hebdomadaires en 4e | Aucune preuve applicable ; A4 ne l'établit pas | Non établi | INSUFFICIENT_EVIDENCE | NO | TBD | YES | U3 : fournir contexte/emploi du temps, sans réécrire P4 |
| D09 | Durées | Déduire une durée officielle chiffrée de SEQ8 | Aucun volume propre identifié | Non établi | INSUFFICIENT_EVIDENCE | NO | TBD | NO | Différé ; saisie locale possible sans étiquette officielle |
| E01 | Compétences | Noyau 8 transversales / 6 transdisciplinaires / 3 disciplinaires | P4 p.12 ; P6 p.13 ; P1 p.9 | 1 | MULTI_SOURCE_CONFIRMED | YES | YES | NO | Limité aux versions/niveaux examinés |
| E02 | Compétences | Les 14 énoncés CT/CTD partagent un noyau lexical commun | Tableau comparatif E | 1 | MULTI_SOURCE_CONFIRMED | YES | YES | NO | Conserver texte brut par version |
| E03 | Compétences | Les CD sont quasi identiques, contextes distincts | P4 pp.68/72/76 ; P6 pp.77/81/86 ; P1 pp.57/60/64 | 1 | MULTI_SOURCE_CONFIRMED | YES | YES | NO | Différence de déduction et variantes textuelles conservées |
| E04 | Compétences | Séparer catalogue global, contexte et sélection de fiche | P4 p.16 ; P6 p.18 ; G4 p.74 ; G0 | 1/2 ; produit | DERIVED_PRODUCT_RULE | YES | YES | NO | Aucune duplication automatique classe par classe |
| E05 | Compétences | Permettre un sous-ensemble contextualisé dans une fiche | G4 p.74 ; G6 p.42 ; P1 p.73 | 1/2 | MULTI_SOURCE_CONFIRMED | YES | YES | NO | Exemples différents ; pas tout le catalogue systématique |
| E06 | Compétences | Imposer exactement une CTD sur toute fiche | Exemples G4/G6/P1, sans obligation universelle retrouvée | 1/2, exemples | INSUFFICIENT_EVIDENCE | NO | TBD | YES | U7 : cardinalité produit à décider |
| E07 | Compétences | Corriger le contexte CT8 « troisième » du programme 6e | P6 p.40 | 1, contradiction interne | CONFLICT | NO | TBD | YES | U4 : garder source brute, correction validée séparée |
| E08 | Compétences | Conserver CD2 géométrique / CD3 numérique et les ordres locaux | Cadres numérotés P4/P6/P1 ; P4 p.17 | 1 | DERIVED_PRODUCT_RULE | YES | NO | NO | Ne pas fabriquer les identifiants depuis l'ordre d'une liste |
| F01 | Devoirs | Supporter des exercices de maison sur la notion travaillée | G4 pp.73/78 ; G6 pp.47/52 ; F4b p.22 | 2/5 | MULTI_SOURCE_CONFIRMED | YES | YES | NO | Existence confirmée ; aucun nombre obligatoire |
| F02 | Devoirs | Autoriser un devoir de réactivation d'une notion passée | G0 §9 ; P0 §8 ; appui général P4 p.12 | Produit ; appui 1 | USER_DECISION | YES | YES | NO | Ne pas exiger une prescription officielle pour cette option |
| F03 | Devoirs | Réactivation sans changement du périmètre courant | G0 §9 ; distinction B/F | Produit | DERIVED_PRODUCT_RULE | YES | YES | NO | Usage de ressource séparé des segments |
| F04 | Devoirs | Relier devoir à classe/notions/séquence/source/validation, instructions facultatives | G0 §9 | Produit | USER_DECISION | YES | YES | NO | Contrat de données demandé, pas schéma officiel |
| F05 | Ressources | Introduire les types détaillés de consignes/savoirs/devoirs | G0 §8 ; G4 p.5 appui partiel | Produit | USER_DECISION | YES | TBD | NO | Ne pas présenter l'énumération technique comme officielle |
| F06 | Instruction | Distinguer admettre une propriété et la démontrer ultérieurement | G6 p.47 ; G4 p.5 | 2 | MULTI_SOURCE_CONFIRMED | YES | NO | NO | Même notion ne signifie pas même instruction couverte |
| F07 | Pratiques | Les fiches de collègues montrent une CTD choisie et un sous-ensemble de CT | F4 p.1 ; F4b/F6 p.2 | 5 | PRACTICE_CONFIRMED | NO | NO | NO | Constat comparatif uniquement ; pas prescription à implémenter |
| G01 | Documents | Prévoir une rubrique Documents utilisés dans la fiche enseignant | G4 pp.73/78 ; G6 p.47 | 2, exemples | MULTI_SOURCE_CONFIRMED | YES | YES | NO | Exemples officiels, sans format informatique imposé |
| G02 | Documents | Liste hybride, dédupliquée, persistée et exportée depuis les provenances | G0 §10 ; listes G4/G6 | Produit | DERIVED_PRODUCT_RULE | YES | YES | NO | Entrées automatiques et manuelles distinguées |
| H01 | Support | Distinguer consigne, éléments de réponse et contenu à retenir | G4 pp.71-74 ; G6 pp.43-47 ; S1 p.6 | 2/6 | MULTI_SOURCE_CONFIRMED | YES | NO | NO | La séparation sémantique est étayée |
| H02 | Support | EXPECTED_RESPONSE enseignant uniquement dans le support produit | G0 §12 ; P0 §10 | Produit | USER_DECISION | YES | NO | NO | Aucune interdiction officielle générale de correction inférée |
| H03 | Support | Aucune grande zone de réponse par défaut | G0 §12 ; P0 §10 | Produit | USER_DECISION | YES | NO | NO | Décision d'édition, pas déduction depuis une absence |
| H04 | Support | Des consignes et définitions distinctes peuvent coexister dans un support de cours | S1 pp.5-6 | 6, pratique de support | PRACTICE_CONFIRMED | YES | NO | NO | Exemple documenté, non preuve universelle |
| H05 | Support | Conserver définitions/propriétés/formules/méthodes et figures visibles | G0 §12 ; P0 §10 | Produit | USER_DECISION | YES | NO | NO | Type de contenu distinct d'une réponse attendue |
| I01 | Plan annuel | Représenter année/niveau/semaines/SA/activités/périodes/interruptions | A4 pp.1-4 | 3 institutionnel | OFFICIAL_CONFIRMED | YES | YES | NO | Structure observée ; heures prévues non fournies par A4 |
| I02 | Plan annuel | Séparer progression officielle, curriculum et suivi réalisé par classe/année | A4 ; G0 §11 ; correction U6 | Institutionnel ; modèle produit dérivé | DERIVED_PRODUCT_RULE | YES | YES | NO | La référence officielle n'est pas une création locale du professeur |
| I03 | Plan annuel | Une semaine pédagogique peut être interrompue puis reprise | A4 pp.3-4, semaine 20 | 3 institutionnel | OFFICIAL_CONFIRMED | YES | YES | NO | Deux intervalles, même semaine pédagogique |
| I04 | Plan annuel | Choisir la phase de livraison du stockage et des écrans OfficialAnnualProgression | P0 §11 ; correction U6 | Produit | USER_DECISION | NO | TBD | YES | U5 : échéance seulement, ni statut officiel ni inclusion dans la cible |
| I05 | Plan annuel | Prendre la progression annuelle officielle comme référence du QUAND pour son année/niveau | Correction utilisateur U6 ; A4 pp.1-4 | Autorité institutionnelle sur la cadence, clarifiée par utilisateur | USER_DECISION | YES | YES | NO | U6 = CLOSED_WITH_CORRECTION ; programme/guide conservent leurs domaines |
| I06 | Plan annuel | Ne pas prendre les colonnes prévu pour une exécution réelle | A4 pp.1-4 | 3 institutionnel | OFFICIAL_CONFIRMED | YES | NO | NO | Réalisé non renseigné dans le document |
| I07 | Plan annuel | Prévoir OfficialAnnualProgression avec année, niveau, autorité, source, semaines/périodes, attentes SA/séquences, intégration, évaluation, remédiation, interruptions, version/provenance | Correction utilisateur U6 | Produit fondé sur référence institutionnelle | USER_DECISION | YES | YES | NO | Cible définie ; aucune implémentation autorisée ici |
| I08 | Séances / progression | Relier plus tard séances et attentes officielles pour prévu/réalisé, retard/avance, prochaine séquence et prochaine séance | Correction utilisateur U6 ; I02/I07 | Produit | DERIVED_PRODUCT_RULE | YES | YES | NO | Conserver contexte classe/année et faits réalisés distincts des attentes |
| AU01 | AUTO | Proposer la prochaine séance selon couverture, temps, prescriptions et cadence annuelle officielle applicable | G0 §13 ; règles B/C/D/A/I ; correction U6 | Produit | USER_DECISION | YES | YES | NO | Dépend du modèle séance ; comportement SKIPPED exclu du périmètre prêt |
| AU02 | AUTO | Toujours produire un brouillon, finalisation humaine distincte | G0 §13 | Produit | USER_DECISION | YES | NO | NO | Ni source ni sélection automatique ne vaut certification |

### Traçabilité de chacun des dix findings majeurs G0

| Finding G0 rappelé | Règles P0 | Preuve et décision d'implémentabilité |
|---|---|---|
| V203R1-MAJ-SEQ-001 : séance planifiée/numéro/succession absents | B01-B06, B08 | Guides et progression soutiennent la structure ; prête, sans importer les numéros contradictoires des exemples |
| V203R1-MAJ-SEQ-002 : faux achèvement PARTIAL/SKIPPED, classes mélangées | C01-C08, B06 | Exigences produit définies ; correction du faux achèvement prête ; politique AUTO de SKIPPED attend U1 |
| V203R1-MAJ-DUR-001 : durées confondues, pause absente | D01-D09 | Durées d'exemples et SA prouvées ; modèle distinct prêt ; 10 min et contexte 4,5/5 h attendent U2/U3 |
| V203R1-MAJ-COMP-001 : catalogue global/applicabilité absents | E01-E08 | 8/6/3 confirmé ; catalogue/contexte/sélection prêts ; CT8 et cardinalité obligatoire attendent U4/U7 |
| V203R1-MAJ-SRC-001 : priorité incomplète | A01-A02, D02, I05 | Autorité répartie par fonction ; U6 fermé ; conserver séparément les conflits de contenu/allocation |
| V203R1-MAJ-RES-001 : types trop généraux | F05-F06, H01/H05 | Typologie produit autorisée ; différence admettre/démontrer explicitement documentée |
| V203R1-MAJ-HW-001 : devoir/réactivation absents | F01-F04 | Maison confirmé par exemples ; réactivation et liens autorisés comme décisions produit |
| V203R1-MAJ-DOC-001 : documents utilisés non persistés par fiche | G01-G02 | Rubrique confirmée ; génération hybride dérivée du produit, prête |
| V203R1-MAJ-PROG-001 : pas de plan annuel | I01-I08, D06 | OfficialAnnualProgression intégré à la cible ; autorité annuelle validée par correction U6 ; calendrier de livraison U5 ouvert ; taux ne sont pas heures |
| V203R1-MAJ-AUTO-001 : pas de prochaine séance ni budget | AU01-AU02, C04-C07, D04 | Règles prêtes pour cas sans SKIPPED, après socle ; pas d'algorithme officiel inventé |

Les règles H documentent en plus les garanties apprenant déjà supportées : elles ne créent pas un nouveau finding de régression. La levée de l'incertitude G0 sur 8/6/3 porte sur les versions lues, pas sur un chargement effectué.

### Ordre MVP recommandé après P0

1. Séance/classe/année, numéro, suivi exact NOT_STARTED/PARTIAL/COVERED et visibilité SKIPPED ; aucun automatisme non arbitré pour SKIPPED.
2. Durées séparées avec créneau et pause explicitement saisis ; aucune pause automatique de 10 min.
3. Catalogue commun et contexte versionné ; conserver variantes, isoler l'anomalie CT8 ; pas de cardinalité CTD obligatoire non décidée.
4. Devoirs/réactivation puis documents utilisés ; maintenir les exclusions apprenant.
5. Prévoir OfficialAnnualProgression et ses liens avec les séances selon le calendrier de livraison U5 ; AUTO devra tenir compte de la cadence officielle applicable en restant un brouillon. U6 est fermé, sans autorisation de mise en œuvre dans ce message.

Cet ordre est une recommandation de livraison. Il ne lance aucune des phases G0 et ne change pas leur autorisation.

## K. RULES REQUIRING USER ARBITRATION

Six questions restent ouvertes, associées aux lignes du tableau. U6 est fermé sur décision explicite de l'utilisateur ; son ancienne demande d'arbitrage est remplacée par la correction ci-dessous.

| Arbitrage | Décision manquante | Proposition concrète et effet |
|---|---|---|
| U1 - C07 | Que faire automatiquement d'une instruction SKIPPED ? | Proposer un report visible et sélectionnable, sans la déclarer couverte ; laisser l'enseignant confirmer une exclusion temporaire. Valider avant son inclusion dans AUTO |
| U2 - D05 | Faut-il une pause par défaut de 10 min, et pour quels créneaux ? | Garder d'abord une pause saisie explicitement ; 10 min peut devenir un profil local validé, jamais une prescription officielle |
| U3 - D08 | À quel contexte 4e correspondent 4,5 h ou 5 h ? | Fournir l'emploi du temps ou le texte applicable ; conserver P4 = 6 h comme fait de l'édition. A4 ne constitue pas cette preuve |
| U4 - E07 | Quelle correction validée appliquer au contexte CT8 de P6 ? | Conserver « troisième » en source brute ; bloquer la publication du contexte corrigé jusqu'à validation explicite/erratum. Le libellé de CT8 reste utilisable |
| U5 - I04 | Dans quelle phase livrer le stockage et les écrans de progression officielle ? | Planifier la livraison d'OfficialAnnualProgression ; son statut institutionnel et son inclusion dans la cible sont déjà fixés |
| U6 - I05 | CLOSED_WITH_CORRECTION | CURRICULUM_AUTHORITY = PROGRAMME + GUIDE ; YEAR_EXECUTION_AUTHORITY = OFFICIAL_ANNUAL_PROGRESSION. La progression officielle détermine le QUAND pour son année/niveau sans modifier silencieusement contenus ou prescriptions |
| U7 - E06 | Une seule CTD obligatoire ou sélection ouverte ? | Recommander une sélection ouverte, avec une CTD suggérée seulement lorsqu'une source contextualisée l'étaye ; ne pas imposer tous les exemples comme norme |

Ces arbitrages ne bloquent pas les autres règles prêtes. Ne pas redemander l'autorisation de distinguer PARTIAL/COVERED, d'ajouter la réactivation ou d'exclure les réponses du support : l'utilisateur l'a déjà demandé.

## L. RULES DEFERRED

- **D09 :** toute durée officielle chiffrée de séquence non trouvée. Une valeur locale peut être saisie sans devenir officielle.
- **F07 :** le constat sur la sélection de compétences dans les fiches de collègues reste une preuve de pratique, pas une règle normative à imposer.
- Les règles en attente U1-U5 et U7, uniquement pour leur partie non arbitrée ; U6 est fermé. Le reste du modèle ne doit pas attendre une certification globale du corpus.
- La comparaison exhaustive des variantes de guides, l'authentification externe et l'actualité réglementaire des éditions, l'import complet de tous les contextes et capacités. Pas de certification multi-niveaux ni d'activation 6e/Première C dans l'application actuelle.
- Une conversion automatique du taux prévu A4 en heures, en statut d'instruction ou en résultat réellement réalisé : **interprétation rejetée**, pas fonctionnalité à implémenter ultérieurement sur cette seule source.
- L'export de corrigés côté apprenant et la création de grandes zones de réponse par défaut : hors cible explicitement fixée, sans arbitrage nouveau nécessaire.

### Vérification et verdict

G0 conservé : SHA-256 `ce06f0bbe754457778e1dd5fe287c3c8c61c29e87e0f6ebdbebd328facf63c16`.

Contrôle initial P0 : les empreintes des dix sources principales étaient inchangées ; seul ce rapport avait été ajouté. Révision U6 : modification de ce rapport uniquement, à partir de la clarification utilisateur, sans nouvelle lecture documentaire présentée comme effectuée ni modification de G0. Le tableau comprend désormais 59 règles ; les compteurs sont actualisés ci-dessous.

PASS signifie : sources accessibles examinées, dix findings reliés à des règles, preuves/classifications/limites et décisions restantes explicitement consignées. Il ne signifie pas que les conflits sont résolus, que toutes les règles sont prêtes ou que le code est conforme.

RULES_TOTAL = 59

OFFICIAL_CONFIRMED = 7

MULTI_SOURCE_CONFIRMED = 13

PRACTICE_CONFIRMED = 2

USER_DECISION = 22

DERIVED_PRODUCT_RULE = 9

CONFLICT = 3

INSUFFICIENT_EVIDENCE = 3

READY_FOR_IMPLEMENTATION = 51

REQUIRES_HUMAN_ARBITRATION = 6

Les compteurs portent sur les règles du tableau J uniquement. Huit règles ne sont pas prêtes : six arbitrages, D09 sans preuve chiffrée et F07 constat de pratique sans obligation produit. Les 51 règles prêtes sont définies pour des missions futures ; aucun code ni migration n'est autorisé par la correction U6.

U6 = CLOSED_WITH_CORRECTION

NO_CODE_CHANGED = YES

V2_03_R1_P0 = PASS
