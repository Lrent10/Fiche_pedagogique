# M01 — Functional Domain Model — Final Candidate

**Projet :** Générateur de fiches pédagogiques de mathématiques — MVP pilote 4e — Bénin  
**Statut du document :** M01-G1 TARGETED DOMAIN CLOSURE FIX COMPLETED — READY FOR INDEPENDENT REAUDIT  
**Verdict :** **PASS — M01-G1 TARGETED DOMAIN CLOSURE FIX COMPLETED  
READY FOR INDEPENDENT REAUDIT**  
**Nature :** baseline fonctionnelle normative, indépendante de toute technologie  
**Date d'audit du corpus :** 28 août 2026

> La micro-correction M01-G1 ferme M01-REV-001 à M01-REV-003 sans rouvrir Q-M01-01 à Q-M01-07. Sept constats documentaires non bloquants sont conservés sans modification : quatre divergences de durées entre le programme et le guide de 4e, deux incohérences internes du programme de Terminale D et un motif de contenu manquant dans la fiche de pratique de 3e. Le gel définitif de M01 reste soumis au micro-réaudit indépendant.

## 1. Objectif

Établir le modèle métier minimal et suffisant permettant à un enseignant de préparer une fiche enseignant correspondant à une séance, à partir d'un référentiel déterminé, d'instructions officielles et de ressources pédagogiques sourcées, qualifiées puis localement adaptables. Le modèle doit préserver l'historique, la provenance, les anomalies des sources, la progression curriculaire, le contenu LaTeX/TikZ et la distinction entre fiche enseignant et support apprenant.

Ce document fixe les objets, responsabilités, relations, cardinalités, cycles de vie, statuts et invariants que M02 devra respecter sans les réinventer.

## 2. Périmètre

Sont inclus dans le MVP :

- le référentiel pilote de 4e et sa structuration en SA, séquences, connaissances/techniques et instructions ;
- une bibliothèque de ressources atomiques ou composites, versionnées et qualifiées ;
- la provenance documentaire jusqu'au bloc ;
- les cinq axes de validation indépendants et les anomalies de source ;
- la préparation versionnée d'une fiche enseignant pour exactement une séance ;
- l'enregistrement séparé de ce qui a réellement été exécuté ;
- les supports apprenants couvrant une séquence ou une SA et utilisables sur plusieurs séances ;
- les fragments LaTeX, TikZ et les images, leurs variantes et leur rendu sans perte de source ;
- le suivi calculable de la progression à partir des séances exécutées.

Ne sont pas inclus : architecture logicielle, stockage physique, interfaces, droits d'accès applicatifs, recommandation automatique, certification automatique d'une adaptation et diffusion communautaire avancée.

## 3. Corpus utilisé

Tous les PDF ont été retrouvés sous `C:\Users\HP\Desktop\Base`, ouverts, extraits intégralement et examinés. Les pages citées ci-dessous sont les pages physiques des PDF.

| Niveau | Document | Pages | Usage dans M01 | Lecture |
|---|---|---:|---|---|
| 1 | `930040566-programme-4ieme-Maths-certifie.pdf` | 127 | Structure normative du pilote ; SA ; durées ; planification ; déroulement | PASS |
| 1 | `783063322-GUIDE-4eme-Maths-Certifie-Vu.pdf` | 100 | Instructions ; séquences ; canevas ; stratégies ; exemples de fiches | PASS |
| 2 | `930039235-Programme-5e-Math-certifie.pdf` | 119 | Vérification de la généralité SA/temps/déroulement | PASS |
| 2 | `687810151-Guide-5e-Maths-certifie-Vu.pdf` | 91 | Vérification des instructions, catégories de propriétés et fiches | PASS |
| 2 | `738093389-Programme-terminale-D.pdf` | 87 | Épreuve des contradictions et variantes de structure | PASS |
| 3 | `828031180-New-Fiche-Enseignante-1ereD-S-a-1-N.pdf` | 14 | Usage réel des trois parties, phases, résultats attendus | PASS |
| 3 | `918890050-Fiche-Du-Cours-3eme-2023-2024.pdf` | 78 | Ressources composites et contenus explicitement manquants | PASS |
| 3 | `785120206-Fiche-Apprenant-2nde-D-2024-Public-New.pdf` | 38 | Support couvrant plusieurs séquences/SA et plusieurs séances | PASS |

### 3.1 Constatations documentaires structurantes

**Ce qui est écrit dans les sources principales :**

- le programme de 4e précise qu'une situation d'apprentissage n'est pas une fiche pédagogique (p. 89 du PDF) ;
- le guide de 4e définit une fiche comme une planification détaillée d'une activité pédagogique et demande un va-et-vient entre programme et guide (p. 3 à 5) ;
- le canevas du guide suit `A — Introduction`, `B — Réalisation`, `C — Retour et projection` (p. 9 à 10) ;
- les stratégies citées comprennent notamment travail individuel, travail en groupe et travail collectif, sans que cette liste interdise d'autres phases (p. 6 à 8) ;
- le guide impose de finir totalement une SA avant de passer à la suivante (p. 5) ;
- les exemples de fiches de 4e comportent les éléments d'identification, de planification et le déroulement (à partir de la p. 66) ;
- la fiche apprenant de 2nde D couvre plusieurs SA et de nombreuses séquences dans un même document ; elle contient situations de départ, activités, consignes, figures, contenus et retour/projection.

**Analyse :** ces observations imposent des identités distinctes pour le référentiel, l'instruction, la ressource, la fiche de séance, son exécution réelle et le support apprenant. Elles justifient une granularité session-bound pour la fiche enseignant et sequence/SA-bound pour le support apprenant.

**Validation pour le modèle :** les décisions Q-M01-01 à Q-M01-07 sont confirmées. Les différences chiffrées et contenus manquants sont représentés par `SourceIssue`, sans choisir silencieusement une valeur.

### 3.2 Registre des constats documentaires

| Finding | Source et pages physiques | Écrit dans la source | Analyse | Traitement validé |
|---|---|---|---|---|
| F-01 | Programme 4e p. 90 ; guide 4e p. 11 | SA1 : 56 h / 60 h | Deux valeurs officielles divergentes | `INTERNAL_CONTRADICTION`, non bloquant ; aucune valeur fusionnée |
| F-02 | Programme 4e p. 98 ; guide 4e p. 33 | SA2 : 28 h / 30 h | Idem | Idem |
| F-03 | Programme 4e p. 108 ; guide 4e p. 46 | SA3 : 20 h / 18 h | Idem | Idem |
| F-04 | Programme 4e p. 118 ; guide 4e p. 56 | SA4 : 22 h / 24 h | Idem | Idem |
| F-05 | Programme Tle D p. 74, 79 et 81 | « SA n°1 » puis titre « SA n°3 », puis « SA n°1 » | Numérotation interne contradictoire | `INTERNAL_CONTRADICTION`, structure-test seulement |
| F-06 | Programme Tle D p. 74 et 81 | 24 h puis 12 h pour Configurations de l'espace | Durée interne contradictoire | `INTERNAL_CONTRADICTION`, structure-test seulement |
| F-07 | Fiche 3e p. 2, 3, 38 et 55 | « Résultats attendus (à faire) » | Transcription possible mais source incomplète | `MISSING_RESULT`; ne pas inventer le résultat |

Il n'existe aucun nouveau constat bloquant. Les constats F-01 à F-07 restent ouverts tant qu'une autorité humaine n'a pas arbitré le contenu ; ils ne bloquent pas la validité du modèle qui les représente.

## 4. Hiérarchie des sources

1. **Niveau 1 — normatif pour le pilote :** programme et guide de mathématiques de 4e. Le programme fixe le cadre curriculaire ; le guide le complète et décline les instructions et séquences. Une divergence entre eux est enregistrée, non résolue par préséance silencieuse.
2. **Niveau 2 — validation de structure :** programme/guide de 5e et programme de Terminale D. Ils peuvent confirmer ou éprouver une structure ; ils ne modifient pas le contenu normatif de 4e.
3. **Niveau 3 — exemples de pratique :** fiches 1re D et 3e, support 2nde D. Ils révèlent des usages et cas limites ; ils ne peuvent contredire ni écraser le niveau 1.

Toute donnée importée conserve le document, l'occurrence et le niveau d'autorité dont elle provient.

## 5. Terminologie normative

| Terme | Définition retenue |
|---|---|
| Référentiel | Ensemble versionné programme + guide utilisé pour préparer une séance, sans fusionner leurs textes. |
| Situation d'apprentissage (SA) | Regroupement curriculaire ordonné de tâches, contenus et apprentissages ; ce n'est pas une fiche. |
| Séquence | Regroupement cohérent et ordonné de contenus notionnels au sein d'une SA. |
| ConnaissanceTechnique | Élément curriculaire de connaissance ou technique attendu dans une séquence. |
| InstructionGuide | Prescription officielle intacte du guide, portant une ou plusieurs actions pédagogiques. |
| Ressource pédagogique | Identité logique d'un contenu réutilisable, atomique ou composite. |
| Version de ressource | État exact et immuable, une fois disponible, d'une ressource. |
| Instance de ressource | Contenu local d'une révision, soit dérivé d'une version de bibliothèque, soit créé originalement dans la fiche ou le support. |
| Bloc | Plus petite unité éditable et ordonnée utile dans une ressource/version ou sa copie. |
| Fiche enseignant | Identité de préparation correspondant exactement à une séance. |
| Révision de fiche | État versionné, brouillon ou finalisé, de cette préparation. |
| Séance exécutée | Fait distinct indiquant ce qui a réellement été réalisé à partir d'une révision finalisée. |
| Support apprenant | Document métier autonome couvrant une séquence ou une SA, réutilisable sur plusieurs séances. |
| Document source | Document logique d'origine. |
| Occurrence source | Localisation précise dans un document source. |
| SourceIssue | Anomalie décrivant sans la corriger une lacune, ambiguïté ou contradiction de source. |

Les termes « fiche enseignant », « support apprenant », « ressource », « version », « instance » et « bloc » ne sont jamais synonymes.

## 6. Principes de conception

1. **Fidélité avant correction :** conserver séparément texte source, analyse, proposition et contenu validé.
2. **Référentiel versionné :** aucune donnée curriculaire flottante ou détachée de sa version.
3. **Immutabilité historique :** une évolution de bibliothèque ou de fiche crée un nouvel état ; elle ne réécrit pas l'ancien.
4. **Instance locale :** l'adaptation se fait dans une instance propre à la fiche ou au support, jamais dans la version de bibliothèque.
5. **Provenance granulaire :** la provenance peut viser la version entière ou un bloc précis ; une création originale reste sans fausse source.
6. **Validation plurielle :** fidélité, mathématiques, pédagogie, complétude et cohérence sont indépendantes.
7. **Progression factuelle :** prévu et exécuté sont séparés ; la progression résulte des exécutions ordonnées.
8. **Documents distincts, fragments partagés :** fiche enseignant et support apprenant sont autonomes mais peuvent réutiliser les mêmes ressources/blocs.
9. **Source éditable préservée :** le LaTeX/TikZ ne dépend pas du succès d'un rendu.
10. **Minimalité :** un objet n'est introduit que s'il porte une identité, un cycle, un invariant ou une relation propre.

## 7. Diagrammes métier de haut niveau

```text
ProgrammeVersion ──> SituationApprentissage ──> Sequence ──> ConnaissanceTechnique
        │                                                   ^
        └──── GuideVersion ──> InstructionGuide ────────────┘
                                  ^        ^
                                  │        │ mapping qualifié en bibliothèque
                         TeacherSheetRevision
                                  ^        │
                                  │        v
PedagogicalResource ──> PedagogicalResourceVersion ─┬─> SheetResourceInstance
                                                    └─> SupportResourceInstance
                   LOCAL_ORIGINAL ──────────────────┬─> SheetResourceInstance
                                                    └─> SupportResourceInstance
PedagogicalBlock ──────────────────────────────────┬─> SheetBlockInstance
                                                   └─> SupportBlockInstance
        (les liens source sont absents pour les originaux locaux)
PedagogicalResourceVersion / PedagogicalBlock ──> SourceOccurrence ──> SourceDocument

TeacherSessionSheet ──> TeacherSheetRevision ──> TeachingSession
                                │                       │
                    planned segments          executed segments
                                └──────── progression ──┘

TeacherSheetRevision ────┐
                         ├─> DocumentExport (exactement une branche source)
LearnerSupportRevision ──┘
```

```text
                 PedagogicalResourceVersion / PedagogicalBlock
                              /                         \
                             v                           v
             SheetResourceInstance             SupportResourceInstance
             + SheetBlockInstance              + SupportBlockInstance
                             |                           |
                             v                           v
                  TeacherSheetRevision          LearnerSupportRevision
                  (exactement 1 séance)          (1 séquence ou 1 SA)
                             \                           /
                              \── sources partageables ─/
                               instances locales distinctes
```

## 8. Objets métier définitifs

| Groupe | Objets retenus |
|---|---|
| Curriculum | `ProgrammeVersion`, `GuideVersion`, `SituationApprentissage`, `Sequence`, `ConnaissanceTechnique`, `InstructionGuide`, `CurriculumTimeAllocation` |
| Sources | `SourceDocument`, `SourceOccurrence`, `SourceIssue`, `ProposedContent` |
| Bibliothèque | `PedagogicalResource`, `PedagogicalResourceVersion`, `PedagogicalBlock`, `BlockVariant` |
| Fiche enseignant | `TeacherSessionSheet`, `TeacherSheetRevision`, `SessionCurriculumSegment`, `SheetResourceInstance`, `SheetBlockInstance`, `FlowItem`, `ActivityPhase` |
| Exécution | `TeachingSession`, `ExecutedCurriculumSegment` |
| Support apprenant | `LearnerSupport`, `LearnerSupportRevision`, `SupportResourceInstance`, `SupportBlockInstance`, `SupportUse` |
| Sorties | `DocumentExport` |

`ResourceInstructionMapping`, les dimensions de validation et les métadonnées d'identification sont des relations ou groupes d'attributs fonctionnels : ils n'ont pas besoin d'une identité autonome. Les listes de types de ressources, blocs, phases et sorties sont extensibles ; elles ne constituent pas des objets métier distincts.

## 9. Description et responsabilités des objets

### 9.1 Curriculum

**ProgrammeVersion.** Identifie une édition déterminée du programme (classe, discipline, date/édition, statut de référence). Elle ordonne les SA et garantit que tout contenu curriculaire utilisé est rattaché au bon état du programme.

**GuideVersion.** Identifie l'édition du guide qui complète une `ProgrammeVersion`. Elle conserve son propre texte, ses séquences et ses instructions ; elle n'est pas fusionnée avec le programme.

**SituationApprentissage.** Porte le numéro, le titre, la position et les contenus d'une SA dans une version de programme. Son ordre est explicite. Elle possède ses séquences dans le périmètre du couple programme/guide.

**Sequence.** Porte l'ordre, l'intitulé et le périmètre notionnel dans exactement une SA. Elle permet de localiser une séance à l'intérieur de la progression.

**ConnaissanceTechnique.** Représente une connaissance ou technique curriculaire identifiable. Elle appartient à au moins une séquence et peut être visée par plusieurs instructions.

**InstructionGuide.** Conserve mot pour mot une prescription officielle, son occurrence et une ou plusieurs actions prescrites (`définir`, `démontrer`, `faire admettre`, `appliquer`, etc.). Les actions sont des attributs analytiques ; elles ne remplacent jamais le texte officiel et ne deviennent pas systématiquement une entité.

**CurriculumTimeAllocation.** Porte une valeur de durée normative, son unité, sa portée (SA ou séquence), sa version de référentiel et sa provenance. Plusieurs allocations contradictoires peuvent coexister, chacune avec son occurrence et un `SourceIssue`; tant qu'elles ne sont pas arbitrées, aucune durée officielle unique n'est inventée.

### 9.2 Sources et anomalies

**SourceDocument.** Identité logique d'un programme, guide, manuel, fiche ou création documentée. Métadonnées minimales : titre, auteur, éditeur, édition/date, nature et niveau d'autorité.

**SourceOccurrence.** Localisation vérifiable dans exactement un document : page ou plage, section, activité, figure, correction ou autre repère. Une occurrence ne duplique pas le document.

**SourceIssue.** Conserve une anomalie sans altérer sa source : type, description factuelle, éléments affectés, une ou plusieurs occurrences, sévérité, statut et note de résolution éventuelle.

**ProposedContent.** Contenu séparé proposé pour compléter ou corriger une anomalie. Il garde le lien vers le `SourceIssue`, son auteur, sa justification et son statut `PROPOSED`, `VALIDATED` ou `REJECTED`. Même validé, il ne devient jamais rétroactivement la transcription de la source.

### 9.3 Bibliothèque pédagogique

**PedagogicalResource.** Identité logique stable d'une ressource réutilisable. Elle indique sa nature atomique ou composite et une catégorie extensible telle que `DEFINITION_FORMULATION`, `PROPERTY_STATEMENT`, `CONSIGNE`, `FIGURE`, `METHOD`, `PROOF`, `EXAMPLE`, `APPLICATION`, `EXERCISE` ou `ACTIVITY_COMPLETE`.

**PedagogicalResourceVersion.** État exact d'une ressource : blocs ordonnés, provenance, mapping vers les instructions et cinq dimensions de validation. Une version disponible est figée ; une correction produit une nouvelle version.

**PedagogicalBlock.** Unité éditable incluse dans exactement une version. Elle porte un ordre, un type extensible (`CONTEXT`, `SUPPORT`, `CONSIGNE`, `QUESTION`, `FIGURE`, `EXPECTED_RESULT`, `SOLUTION`, `EXPLOITATION`, `DEFINITION`, `PROPERTY`, `THEOREM`, `RULE`, `METHOD`, `EXAMPLE`, `APPLICATION`, `EVALUATION`, `NOTE_TAKING`, `HOMEWORK`, `OTHER`), un format (`LATEX`, `TIKZ`, `IMAGE`) et sa provenance éventuelle.

**BlockVariant.** Variante de contenu d'un bloc visant une ou plusieurs cibles : `TEACHER`, `LEARNER_INITIAL`, `LEARNER_COMPLETED` ou une future cible déclarée. Le contenu de base est partagé lorsqu'aucune différence n'est nécessaire.

### 9.4 Fiche enseignant et exécution

**TeacherSessionSheet.** Identité stable de la préparation d'exactement une séance pédagogique prévue. Elle rassemble une ou plusieurs révisions mais ne contient pas elle-même le contenu mutable.

**TeacherSheetRevision.** État exact de la préparation. Elle contient identification, planification, segments curriculaires, instructions retenues, instances de ressources et déroulement ordonné. Elle est sauvegardable incomplète en `DRAFT` et immuable en `FINALIZED`.

**SessionCurriculumSegment.** Portion curriculaire planifiée et ordonnée de la séance : SA, séquence, position (début/continuation/fin), durée prévue et connaissances prévues. Plusieurs segments permettent de franchir une limite de séquence ou, sous condition, de SA.

**SheetResourceInstance.** Ressource locale contenue dans exactement une révision de fiche. Son origine fonctionnelle est exclusivement `LIBRARY_DERIVED` ou `LOCAL_ORIGINAL`. Une instance `LIBRARY_DERIVED` référence exactement une `PedagogicalResourceVersion`, en conserve l'identité/version et produit des snapshots locaux adaptables. Une instance `LOCAL_ORIGINAL` référence zéro version de bibliothèque, peut représenter une activité complète créée directement dans la fiche et contient ses propres blocs locaux. Dans les deux cas, elle est historique dans la révision concernée et ne modifie jamais la bibliothèque.

**SheetBlockInstance.** Snapshot local d'un bloc source, ou bloc original ajouté localement. Il porte son ordre, son contenu, sa visibilité et son état `ACTIVE`, `OMITTED` ou `REPLACED`. Un bloc dérivé conserve son bloc source ; un bloc original en référence zéro. Un remplacement conserve le lien vers le bloc remplacé sans créer de fausse provenance.

**FlowItem.** Élément ordonné du déroulement. Son genre est exclusivement `ACTIVITY`, `STANDALONE_BLOCK` ou `SECTION_STAGE`; il référence respectivement une instance de ressource, un bloc local ou une étape nommée. Il permet rappel, transition, institutionnalisation, prise de notes et retour/projection sans fausse activité.

**ActivityPhase.** Phase facultative et ordonnée d'une activité locale : `TI`, `TG`, `TC`, `TEACHER_LED`, `NOTE_TAKING`, `OTHER` ou extension. Elle porte une durée prévue et éventuellement des indications.

**TeachingSession.** Enregistrement factuel de la séance réellement tenue : date effective, révision finalisée utilisée, durée totale réelle et observations. Il ne réécrit pas la préparation.

**ExecutedCurriculumSegment.** Résultat réel ordonné pour un segment planifié : durée réelle, état `NOT_STARTED`, `PARTIAL` ou `COMPLETED`, et éventuel écart explicité. Il peut référencer un segment planifié ou documenter exceptionnellement un contenu non prévu, toujours rattaché à une SA/séquence déterminée.

**DocumentExport.** Trace fonctionnelle d'une sortie générée depuis exactement une famille de révision : soit une `TeacherSheetRevision`, soit une `LearnerSupportRevision`, jamais les deux. Il conserve la famille de document, la révision source exacte, la cible, la date ou l'instant de génération et le statut de rendu. Il permet de retrouver qu'un PDF ancien provient d'une ancienne révision sans imposer de représentation technique de cette exclusivité.

### 9.5 Support apprenant

**LearnerSupport.** Identité stable d'un support autonome couvrant exactement une séquence ou exactement une SA. Il peut servir à plusieurs séances et n'est pas la projection d'une fiche enseignant.

**LearnerSupportRevision.** État versionné du support, `DRAFT` ou `FINALIZED`, contenant ses `SupportResourceInstance` ordonnées, espaces de recherche, variantes initiales/complétées, exercices, évaluation et retour/projection. Un brouillon peut ne contenir aucune instance ; une révision finalisée en contient au moins une. Elle conserve exactement ses contenus locaux afin qu'une séance historique garde le support réellement utilisé.

**SupportResourceInstance.** Ressource locale contenue dans exactement une révision de support. Son origine est exclusivement `LIBRARY_DERIVED` ou `LOCAL_ORIGINAL`. Dans le premier cas, elle référence exactement une version de bibliothèque et en snapshotte les blocs ; dans le second, elle référence zéro version de bibliothèque et permet notamment un exercice ou une activité complète originale. Toute adaptation reste locale au support.

**SupportBlockInstance.** Snapshot local d'un `PedagogicalBlock`, ou bloc original créé dans le support. Il porte ordre, contenu, visibilité, variantes apprenant utiles et état `ACTIVE`, `OMITTED` ou `REPLACED`. Un bloc dérivé conserve exactement son bloc de départ ; un bloc original en référence zéro. Modification, omission, remplacement et ajout n'altèrent jamais la bibliothèque.

**SupportUse.** Relation qualifiée entre une révision de fiche et une révision de support. Elle précise la partie utilisée (plage de blocs ou repère fonctionnel), l'usage prévu et l'ordre dans la séance. Une fiche peut donc n'utiliser qu'une partie d'un support plus large.

## 10. Relations métier

### 10.1 Chaîne curriculum → séance

Une `ProgrammeVersion` ordonne ses SA ; une `GuideVersion` associée structure leurs séquences et instructions. Chaque instruction vise une ou plusieurs connaissances/techniques. La révision de fiche sélectionne explicitement les instructions et segments concernés, puis intègre des instances dérivées de ressources déjà qualifiées ou des créations locales originales.

### 10.2 Mapping bibliothèque ↔ instructions

La relation opérationnelle est `PedagogicalResourceVersion * ↔ * InstructionGuide`, car une correction peut modifier la couverture. Elle porte au minimum l'analyse de couverture, la justification, l'auteur de l'analyse et son état de qualification. La relation logique `PedagogicalResource * ↔ * InstructionGuide` est une vue consolidée de ses versions ; elle ne remplace pas le mapping versionné. Un mapping est créé en bibliothèque avant sélection dans une fiche. Un rappel/prérequis peut légitimement avoir zéro instruction.

### 10.3 Intégration dans une fiche

Deux parcours exclusifs sont admis. La sélection d'une version crée une `SheetResourceInstance` `LIBRARY_DERIVED`, puis un snapshot local de chaque bloc. La création directe dans la fiche crée une instance `LOCAL_ORIGINAL`, sans version source ni fausse provenance, avec un ou plusieurs blocs locaux. Dans les deux parcours, la révision peut omettre, modifier, remplacer ou ajouter des blocs sans toucher à la bibliothèque. Les `FlowItem` ordonnent les activités, y compris une activité complète originale, les blocs et les sections réellement prévus.

### 10.4 Intégration dans un support apprenant

Une `LearnerSupportRevision` contient ses propres `SupportResourceInstance`. Une ressource de bibliothèque produit une instance `LIBRARY_DERIVED` et des `SupportBlockInstance` snapshotés ; une création directe produit une instance `LOCAL_ORIGINAL` et des blocs locaux. Les deux parcours conservent l'historique de la révision, autorisent modification, omission, remplacement, complément et variantes `LEARNER_INITIAL` / `LEARNER_COMPLETED`, sans modifier la bibliothèque ni fusionner support et fiche enseignant.

### 10.5 Préparation, support, export et exécution

Une `TeacherSheetRevision` peut référencer plusieurs `LearnerSupportRevision` via `SupportUse`, et un support peut servir à plusieurs séances. Chaque `DocumentExport` choisit exactement une révision source dans l'une de ces deux familles. Une `TeachingSession` consigne ensuite l'exécution d'une révision enseignant finalisée et ses segments réels. La progression est agrégée depuis les segments exécutés, jamais depuis un texte libre.

## 11. Cardinalités fonctionnelles

| Relation | Cardinalité | Justification fonctionnelle |
|---|---|---|
| `ProgrammeVersion` — `SituationApprentissage` | Programme `1` → SA `1..*`; SA → Programme `1` | Une version ordonne plusieurs SA ; une SA n'est interprétable que dans une version. |
| `ProgrammeVersion` — `GuideVersion` | Programme `1` → Guide `0..*`; Guide → Programme `1` | Un programme peut avoir plusieurs éditions de guide ; chaque guide complète une version déterminée. |
| `SituationApprentissage` — `Sequence` | SA `1` → Séquence `1..*`; Séquence → SA `1` | Le guide pilote structure chaque SA ; une séquence ne traverse pas deux SA. |
| `Sequence` — `ConnaissanceTechnique` | `1..* ↔ 1..*` | Une séquence regroupe plusieurs contenus ; un contenu transversal peut être mobilisé dans plusieurs séquences. |
| `GuideVersion` — `InstructionGuide` | Guide `1` → Instruction `1..*`; Instruction → Guide `1` | Le texte de l'instruction dépend d'une édition précise. |
| `InstructionGuide` — `ConnaissanceTechnique` | Instruction → connaissance `1..*`; connaissance → instruction `0..*` | Une instruction peut couvrir plusieurs contenus ; certains contenus n'ont pas d'instruction atomisée. |
| SA/Séquence — `CurriculumTimeAllocation` | Portée `1` → allocation `0..*`; allocation → une seule portée | L'absence et les contradictions sont possibles ; une allocation a exactement une portée. |
| `PedagogicalResource` — `PedagogicalResourceVersion` | Ressource `1` → version `1..*`; version → ressource `1` | Identité stable, états historiques multiples. |
| `PedagogicalResourceVersion` — `PedagogicalBlock` | Version `1` → bloc `1..*`; bloc → version `1` | Même une ressource atomique est représentée par un bloc ; une composite en ordonne plusieurs. |
| `PedagogicalBlock` — `BlockVariant` | Bloc `1` → variante `0..*`; variante → bloc `1` | Le contenu de base suffit souvent ; chaque variante appartient à un seul bloc. |
| `PedagogicalResourceVersion` — `InstructionGuide` | `0..* ↔ 0..*` | Plusieurs candidats par instruction et plusieurs instructions par activité ; zéro autorisé pour rappel/prérequis. |
| `SourceDocument` — `SourceOccurrence` | Document `1` → occurrence `0..*`; occurrence → document `1` | Le document logique est distinct de ses localisations. |
| Version/bloc — `SourceOccurrence` | Version `0..* ↔ 0..*` occurrence ; bloc `0..* ↔ 0..*` occurrence | Sources multiples, provenance fine et création originale sans occurrence externe. |
| `SourceIssue` — `SourceOccurrence` | Issue → occurrence `1..*`; occurrence → issue `0..*` | Une contradiction peut nécessiter deux occurrences ; une occurrence peut porter plusieurs anomalies. |
| `SourceIssue` — `ProposedContent` | Issue `1` → proposition `0..*`; proposition → issue `1` | Une lacune peut rester sans proposition ou recevoir plusieurs options séparées. |
| `TeacherSessionSheet` — `TeacherSheetRevision` | Fiche `1` → révision `1..*`; révision → fiche `1` | Historique minimal DRAFT/FINALIZED. |
| `TeacherSheetRevision` — `SessionCurriculumSegment` | Révision `1` → segment `1..*` pour finaliser, `0..*` en brouillon; segment → révision `1` | Un brouillon vide est permis ; une séance finalisée doit être située dans le curriculum. |
| Révision — `InstructionGuide` | `0..* ↔ 0..*` | Brouillon incomplet possible ; une instruction peut être mise en œuvre dans plusieurs séances. |
| Révision — `SheetResourceInstance` | Révision `1` → instance `0..*`; instance → révision `1` | Brouillon sans ressource possible ; une instance est locale à une seule révision. |
| `SheetResourceInstance` — `PedagogicalResourceVersion` | instance → version source `0..1`; version → instance `0..*` | `LIBRARY_DERIVED` impose exactement `1`; `LOCAL_ORIGINAL` impose exactement `0`. Aucun autre état n'est valide. |
| `SheetResourceInstance` — `SheetBlockInstance` — bloc source | instance `1` → snapshot `1..*`; snapshot → bloc source `0..1`; bloc source → snapshots `0..*` | Les blocs ajoutés localement n'ont pas de bloc source ; les snapshots source restent traçables. |
| `SheetResourceInstance` — `ActivityPhase` | instance `1` → phase `0..*`; phase → instance `1` | Une activité peut ne pas détailler ses phases. |
| Révision — `FlowItem` | révision `1` → item `0..*` en brouillon, `1..*` pour finaliser; item → révision `1` | Déroulement explicitement ordonné mais brouillon sauvegardable. |
| `TeacherSessionSheet` — `TeachingSession` | fiche → séance exécutée `0..1`; séance → fiche `1` | La fiche correspond à une occurrence prévue unique, encore non tenue ou tenue une fois dans le MVP. |
| `TeachingSession` — révision utilisée | séance → révision finalisée `1`; révision → séance `0..1` | L'exécution et les exports gardent l'état exact utilisé. |
| `TeachingSession` — `ExecutedCurriculumSegment` | séance `1` → segment réel `1..*`; segment → séance `1` | L'exécution doit être localisable et calculable. |
| `LearnerSupport` — `LearnerSupportRevision` | support `1` → révision `1..*`; révision → support `1` | Préserve l'état exact partagé sur plusieurs séances. |
| `LearnerSupport` — Séquence/SA | support → exactement une séquence **ou** exactement une SA; séquence/SA → support `0..*` | Granularité Q-M01-07 ; exclusivité des deux portées. |
| `LearnerSupportRevision` — `SupportResourceInstance` | révision → instance `0..*` en brouillon, `1..*` pour finaliser ; instance → révision `1` | Un brouillon vide est possible ; un support finalisé possède un contenu local ordonné. |
| `SupportResourceInstance` — `PedagogicalResourceVersion` | instance → version source `0..1`; version → instance `0..*` | `LIBRARY_DERIVED` impose exactement `1`; `LOCAL_ORIGINAL` impose exactement `0`. |
| `SupportResourceInstance` — `SupportBlockInstance` | instance `1` → bloc local `1..*`; bloc local → instance `1` | Ressource atomique ou composite, toujours éditable localement. |
| `SupportBlockInstance` — `PedagogicalBlock` source | bloc local → bloc source `0..1`; bloc source → blocs locaux `0..*` | Un snapshot dérivé conserve son bloc source ; un ajout original n'en invente aucun. |
| Révision fiche — support-révision (`SupportUse`) | `0..* ↔ 0..*` | Une fiche peut utiliser zéro ou plusieurs supports ; un support sert à plusieurs séances. |
| `TeacherSheetRevision` — `DocumentExport` | révision → export `0..*`; export → révision enseignant `0..1` | Plusieurs sorties enseignant sont possibles ; le lien est absent pour un export de support. |
| `LearnerSupportRevision` — `DocumentExport` | révision → export `0..*`; export → révision support `0..1` | Plusieurs sorties apprenant sont possibles ; le lien est absent pour un export enseignant. |
| Source de `DocumentExport` | export → exactement une révision parmi les deux familles | Exclusivité fonctionnelle : un export ne référence jamais simultanément une révision enseignant et une révision support. |

Les cardinalités `0..*` sur le brouillon ne dispensent pas des règles de finalisation.

## 12. Cycles de vie

### 12.1 Référentiel et sources

- `ProgrammeVersion` / `GuideVersion` : `REGISTERED → IN_USE → RETIRED`. Le retrait interdit un nouvel usage par défaut mais conserve tout historique.
- `SourceIssue` : `OPEN → RESOLVED` ou `OPEN → ACCEPTED_AS_SOURCE_LIMITATION`. Une résolution ajoute une note ou une proposition ; elle ne modifie pas la transcription.
- `ProposedContent` : `PROPOSED → VALIDATED` ou `PROPOSED → REJECTED`.

### 12.2 Ressource

```text
PedagogicalResourceVersion: DRAFT → QUALIFIED → AVAILABLE → RETIRED
```

`DRAFT` accepte contenu incomplet. `QUALIFIED` signifie analyse et mapping enregistrés, non certification universelle. `AVAILABLE` autorise la sélection. `RETIRED` empêche les nouvelles sélections mais préserve versions, instances et fiches anciennes. Toute modification d'une version `AVAILABLE` crée une nouvelle version `DRAFT`.

### 12.3 Fiche et support

```text
TeacherSheetRevision: DRAFT → FINALIZED
LearnerSupportRevision: DRAFT → FINALIZED
```

Un état finalisé est immuable. Toute correction crée une nouvelle révision brouillon. Une fiche peut avoir plusieurs révisions finalisées successives : une séance exécutée pointe vers la révision enseignant effectivement utilisée. Indépendamment, chaque export pointe vers exactement une révision source, enseignant ou support.

### 12.4 Exécution

```text
TeacherSessionSheet: PLANNED → CONDUCTED
```

La transition `CONDUCTED` apparaît lorsqu'une `TeachingSession` est enregistrée. Les écarts prévu/réel sont ajoutés dans l'exécution, jamais réinjectés dans la préparation finalisée.

## 13. Règles de versionnement

1. Une version de ressource disponible est immuable ; toute correction crée `v(n+1)`.
2. Toute instance locale `LIBRARY_DERIVED`, dans une fiche ou un support, conserve l'identité et la version exacte de départ, même après adaptation forte ; une instance `LOCAL_ORIGINAL` conserve explicitement l'absence de version source.
3. Les snapshots locaux de fiche et de support préservent le contenu utilisé ; une version retirée ou corrigée ne les modifie pas.
4. Une révision de fiche finalisée est immuable ; sa correction crée une nouvelle révision brouillon.
5. Une révision de support finalisée suit la même règle et fige ses `SupportResourceInstance` / `SupportBlockInstance` afin que les quatre séances qui l'utilisent puissent pointer vers le même état exact.
6. Une `DocumentExport` est liée à exactement une révision précise, enseignant ou support apprenant, pas seulement à l'identité du document et jamais aux deux familles simultanément.
7. Une nouvelle édition du programme ou du guide crée une nouvelle version de référentiel ; aucune remappage automatique des anciennes fiches n'est supposé.
8. Les occurrences sources restent liées à l'édition documentée ; une nouvelle édition ne remplace pas l'ancienne provenance.

## 14. Provenance

Le parcours fonctionnel normal est :

```text
SourceDocument
  → SourceOccurrence
  → transcription fidèle
  → analyse + cinq statuts
  → mapping vers InstructionGuide
  → PedagogicalResourceVersion AVAILABLE
  → SheetResourceInstance ou SupportResourceInstance `LIBRARY_DERIVED`
  → snapshots locaux correspondants
```

Le parcours original local, distinct, est :

```text
Création directe par l'enseignant
  → SheetResourceInstance ou SupportResourceInstance `LOCAL_ORIGINAL`
  → 1..* blocs locaux
  → zéro PedagogicalResourceVersion et zéro fausse provenance
```

Règles :

- une version peut citer plusieurs occurrences, éventuellement de plusieurs documents ;
- chaque bloc peut compléter ou préciser la provenance de la version ;
- une ressource originale porte `origin = ORIGINAL` et zéro occurrence externe ; aucun faux document n'est créé ;
- une adaptation locale dérivée conserve la version/bloc de départ et identifie séparément son auteur et son contenu adapté ; une création locale originale conserve explicitement l'absence de version/bloc source ;
- une transcription et un `ProposedContent` ne partagent jamais le même statut de vérité ;
- les métadonnées utiles restent auteur, titre, éditeur, édition/date et localisation ; aucun workflow juridique n'est ajouté au MVP.

## 15. Validation multidimensionnelle

Chaque version de ressource et, si nécessaire, chaque bloc possède cinq axes indépendants :

| Axe | Valeurs minimales | Sens |
|---|---|---|
| `transcription_status` | `NOT_REVIEWED`, `IN_REVIEW`, `VERIFIED` | Fidélité du texte saisi à ce qui est visible dans la source. |
| `mathematical_validation_status` | `NOT_REVIEWED`, `TO_REVIEW`, `VALIDATED`, `REJECTED` | Exactitude mathématique du contenu, distincte de sa fidélité. |
| `pedagogical_validation_status` | `NOT_REVIEWED`, `TO_REVIEW`, `VALIDATED`, `REJECTED` | Pertinence pédagogique évaluée humainement. |
| `source_completeness_status` | `COMPLETE`, `INCOMPLETE`, `UNKNOWN` | Présence de tout ce que la source prétend fournir. |
| `source_consistency_status` | `CONSISTENT`, `INCONSISTENT`, `UNKNOWN` | Absence ou présence de contradiction interne/documentaire. |

Le cas suivant est valide : `transcription = VERIFIED`, `math = VALIDATED`, `pedagogy = TO_REVIEW`, `completeness = INCOMPLETE`, `consistency = CONSISTENT`.

`VERIFIED` sur la transcription ne signifie ni exact mathématiquement, ni complet, ni pédagogiquement validé. Une adaptation de fiche ne reçoit aucune certification automatique ; elle peut afficher les validations de sa source et un état local `NOT_REVIEWED` après modification.

## 16. SourceIssue et anomalies documentaires

### 16.1 Types obligatoires

`MISSING_CONTENT`, `INTERNAL_CONTRADICTION`, `AMBIGUOUS_STATEMENT`, `BROKEN_FIGURE`, `MISSING_CORRECTION`, `MISSING_RESULT`, `REFERENCED_CONTENT_NOT_FOUND`, `OTHER`.

### 16.2 Attributs fonctionnels

- type et description factuelle ;
- un ou plusieurs éléments affectés ;
- une ou plusieurs occurrences ;
- sévérité `LOW`, `MEDIUM`, `HIGH` si utile ;
- statut `OPEN`, `RESOLVED`, `ACCEPTED_AS_SOURCE_LIMITATION` ;
- note de résolution et éventuels `ProposedContent` séparés.

### 16.3 Règle de non-falsification

Pour « Résultats attendus : à faire » :

```text
Transcription = « Résultats attendus : à faire »
transcription_status = VERIFIED
source_completeness_status = INCOMPLETE
SourceIssue.type = MISSING_RESULT
```

Un résultat rédigé ultérieurement devient `ProposedContent` ou bloc adapté, avec auteur et validation propres. Il n'est jamais présenté comme transcription.

Pour F-01 à F-04, les deux allocations restent enregistrées avec leur occurrence ; l'issue relie les deux. Le calcul du « reste théorique » doit signaler `UNRESOLVED_NORMATIVE_ALLOCATION` tant qu'une allocation de travail n'a pas été explicitement choisie par autorité humaine.

## 17. Temps et progression curriculaire

Trois temps restent distincts :

1. **normatif :** `CurriculumTimeAllocation` attaché à une SA ou une séquence et à une version de référentiel ;
2. **prévu :** durée d'une révision et de ses `SessionCurriculumSegment`, plus durée des activités/phases ;
3. **réel :** durée de la `TeachingSession` et de ses `ExecutedCurriculumSegment`.

### 17.1 Règles de durée

- la durée planifiée de séance est dérivée de la somme des segments curriculaires ;
- la durée du déroulement est dérivée des `FlowItem` chronométrés ; ces deux vues doivent être égales pour finaliser, sinon l'écart est signalé ;
- pour une activité sans phases, sa durée planifiée peut être saisie directement ;
- si des phases existent, la durée de l'activité est dérivée de leur somme et n'est pas une seconde valeur indépendante ;
- la durée réelle est enregistrée après la séance, sans modifier les durées prévues.

### 17.2 Reconstruction de progression

Pour chaque séquence et SA, le système additionne les durées réelles des segments `PARTIAL` ou `COMPLETED`, identifie le dernier segment ordonné exécuté et calcule : heures effectuées, allocation de travail retenue, reste théorique et position. Le reste est `allocation retenue − durée réelle cumulée`, sans descendre sous zéro ; un dépassement reste visible.

La progression curriculaire n'est pas un commentaire libre. Les observations peuvent expliquer un écart mais ne remplacent pas les segments.

### 17.3 Frontières

- une séance peut continuer, finir ou commencer une séquence ;
- elle peut finir une séquence puis commencer la suivante dans la même SA ;
- elle peut franchir SA_n → SA_n+1 uniquement si le premier segment marque la fin complète de SA_n et si tous les contenus/séquences antérieurs sont enregistrés `COMPLETED` ;
- elle ne peut ni commencer SA_n+1 avant cet achèvement, ni revenir silencieusement à une SA antérieure ; une reprise exceptionnelle doit être un segment explicite de remédiation et ne change pas l'ordre officiel.

## 18. TeacherSessionSheet

### 18.1 Identité de séance

`TeacherSessionSheet` représente exactement une séance prévue. Une révision porte : établissement, année scolaire, discipline, date prévue, classe, effectif, nombre de groupes si pertinent, professeur, numéro de séance, durée calculée et segments SA/séquences.

### 18.2 Éléments de planification

La révision peut sélectionner compétences, connaissances/techniques, instructions officielles, stratégie objet d'apprentissage, stratégies d'enseignement/apprentissage/évaluation, matériel et durées. Les instructions sont citées intactes ; l'analyse interne ou la ressource choisie ne remplace pas leur texte.

### 18.3 Déroulement

Les `FlowItem` ordonnent activités, consignes, ressources, phases, résultats attendus, exploitation, institutionnalisation, prise de notes, évaluation, retour/projection, devoirs et observations. Un item peut être un bloc indépendant ou une section, sans être artificiellement transformé en activité.

### 18.4 Brouillon et finalisation

Un `DRAFT` incomplet est toujours sauvegardable. Pour passer à `FINALIZED`, il faut au minimum : identification de la séance, référentiel, un segment curriculaire, durée cohérente, une instruction ou justification de séance de rappel, un déroulement non vide et absence d'erreur de structure bloquante. Le déroulement peut contenir une activité `LOCAL_ORIGINAL` sans passage préalable par la bibliothèque. Une instruction sélectionnée sans ressource correspondante génère une alerte, pas une disparition de l'instruction.

## 19. LearnerSupport

Le support apprenant est autonome : il possède une identité, un périmètre séquence ou SA, des révisions et son ordre propre. Chaque révision organise ses `SupportResourceInstance` et `SupportBlockInstance`. Elle peut contenir situation de départ, activités, consignes, figures, supports, espaces de recherche, énoncés à compléter, versions complétées, exercices, évaluation et retour/projection.

Il n'est ni limité à une séance ni généré mécaniquement depuis une fiche enseignant. Une même révision peut être utilisée pendant quatre séances ; chaque `SupportUse` précise la partie mobilisée. Une ressource de bibliothèque est snapshotée dans les instances du support avant adaptation. Une activité ou un exercice original peut aussi être créé directement avec origine `LOCAL_ORIGINAL`, zéro version source et ses propres blocs. Le support et la fiche enseignant conservent toujours des familles d'instances locales distinctes.

Les variantes `LEARNER_INITIAL` et `LEARNER_COMPLETED` permettent respectivement un support à trous et un corrigé/complété, sans dupliquer les blocs identiques. Les contenus réservés au professeur ne sont jamais exposés dans la cible apprenant initiale.

## 20. PedagogicalResource

Une ressource est **atomique** si son unité pédagogique utile est un bloc ; elle est **composite** si elle ordonne plusieurs blocs ou doit rester sélectionnable comme un tout (`ACTIVITY_COMPLETE`). Dans les deux cas, sa version contient au moins un bloc afin d'unifier édition, provenance et variantes.

Une activité complète peut inclure contexte, support, consignes, figure, stratégie, résultats attendus, exploitation, définition, propriété, méthode et application. Après sélection depuis la bibliothèque, l'activité reste une seule `SheetResourceInstance` ou `SupportResourceInstance` dérivée, mais ses blocs locaux sont éditables individuellement. Une activité complète originale peut aussi naître directement dans l'une de ces deux familles d'instances, sans être d'abord publiée en bibliothèque.

Le mapping vers les instructions est analysé avant disponibilité. Une ressource peut couvrir plusieurs instructions et une instruction disposer de cinq formulations candidates. Une ressource de rappel peut avoir zéro mapping. La disponibilité signifie « candidate qualifiée », jamais « pédagogiquement parfaite pour toute classe ».

## 21. PedagogicalBlock et BlockVariant

Chaque bloc a un ordre explicite, un type extensible, un format, un contenu source éditable et une visibilité. Une version composite peut avoir des provenances différentes par bloc. Dans une fiche ou un support, le snapshot local peut être modifié, omis, remplacé ou complété ; la version source reste inchangée.

Pour une cible donnée, la résolution est : variante explicitement applicable, sinon contenu de base si sa visibilité l'autorise. Il doit exister au plus une variante effective. Une même variante peut viser plusieurs cibles si son contenu est identique. Deux variantes dont les ensembles de cibles se chevauchent rendent le bloc non finalisable tant que le conflit n'est pas résolu.

## 22. FlowItem et ActivityPhase

`FlowItem` fournit un ordre total dans la révision et accepte trois formes exclusives : activité, bloc indépendant, section/étape. Les sections peuvent refléter Introduction, Réalisation, Retour et projection sans figer leur contenu interne.

`ActivityPhase` est facultative et extensible. TI/TG/TC sont des valeurs reconnues, pas une limite. Si aucune phase n'est détaillée, l'activité porte une durée directe. Si au moins une phase existe, sa durée totale est la somme des phases ; toute seconde valeur contradictoire est refusée à la finalisation.

## 23. Règles LaTeX, TikZ, image et rendu

1. Chaque bloc éditable conserve un `source_content` et un `content_format` parmi `LATEX`, `TIKZ`, `IMAGE` ou extension déclarée.
2. `rendered_output` est dérivé et séparé du source ; il n'a jamais autorité sur celui-ci.
3. Un échec de rendu porte un état `NOT_RENDERED`, `RENDERED` ou `RENDER_ERROR` et un diagnostic, sans effacer ni remplacer la source.
4. Les formules et textes mathématiques sont rédigeables en fragments LaTeX ; les figures reproductibles peuvent être en TikZ.
5. Une figure non reconstruite peut rester `IMAGE`, avec sa provenance et éventuellement `BROKEN_FIGURE`; TikZ n'est pas imposé.
6. Une variante possède son propre fragment source lorsque son contenu diffère ; sinon elle réutilise le contenu de base.
7. M01 ne prescrit aucun moteur, paquet, compilation ou mécanisme technique.

## 24. Invariants consolidés

Les 36 invariants imposés sont conservés dans leur sens. M01-G1 modifie six formulations sans les affaiblir (INV-FP-009, 010, 023, 034, 039 et 045), laisse notamment INV-FP-040 inchangé et ajoute cinq invariants de fermeture (INV-FP-046 à 050). Aucun conflit n'a été détecté.

| ID | Invariant normatif |
|---|---|
| INV-FP-001 | Une fiche ne modifie jamais le référentiel officiel. |
| INV-FP-002 | Toute donnée curriculaire utilisée est rattachée à une `ProgrammeVersion` et, pour une instruction, à une `GuideVersion` déterminées. |
| INV-FP-003 | L'adaptation d'une ressource ne modifie jamais sa version source. |
| INV-FP-004 | Une modification future de la bibliothèque ne modifie jamais rétroactivement une fiche existante. |
| INV-FP-005 | Toute version ou tout bloc issu d'une source conserve sa provenance disponible. |
| INV-FP-006 | La provenance peut être définie au niveau du bloc et différer entre blocs d'une même ressource. |
| INV-FP-007 | `InstructionGuide` et ressource pédagogique sont deux objets distincts. |
| INV-FP-008 | Une ressource/version peut être reliée à plusieurs instructions et une instruction à plusieurs ressources/versions. |
| INV-FP-009 | Toute ressource contenue dans une fiche ou un support existe comme instance locale indépendante et adaptable, qu'elle soit dérivée de bibliothèque ou créée localement. |
| INV-FP-010 | Toute instance dérivée de bibliothèque conserve l'identité et la version exacte de la ressource utilisée ; une instance originale conserve explicitement l'absence de version source. |
| INV-FP-011 | Une erreur de rendu LaTeX/TikZ ne détruit ni ne remplace le contenu source saisi. |
| INV-FP-012 | Résultats attendus, solutions et corrections peuvent être réservés à la cible enseignant. |
| INV-FP-013 | Un même bloc peut avoir plusieurs variantes selon l'usage, sans duplication lorsque le contenu est identique. |
| INV-FP-014 | L'ordre des segments, items, blocs et phases concernés est explicite. |
| INV-FP-015 | La durée prévue d'une séance finalisée est calculable depuis ses segments et vérifiable contre son déroulement. |
| INV-FP-016 | Un brouillon incomplet reste sauvegardable. |
| INV-FP-017 | Une révision de fiche permet d'identifier les instructions officielles qu'elle prévoit de mettre en œuvre. |
| INV-FP-018 | Une instruction sélectionnée sans ressource intégrée est signalée et n'est jamais supprimée silencieusement. |
| INV-FP-019 | Pour un bloc et une cible donnée, il existe au plus une variante effective. |
| INV-FP-020 | Une ressource ou activité de rappel/prérequis peut avoir zéro mapping vers une nouvelle instruction. |
| INV-FP-021 | Le mapping version de ressource ↔ instruction est établi et qualifié dans la bibliothèque avant sélection. |
| INV-FP-022 | Le texte officiel d'une instruction n'est jamais remplacé par ses actions extraites, son analyse ou une ressource. |
| INV-FP-023 | Une `SheetResourceInstance` `LIBRARY_DERIVED` référence exactement une version source ; une instance `LOCAL_ORIGINAL` en référence zéro ; ses blocs locaux restent identifiés et ordonnés. |
| INV-FP-024 | Le retrait d'une ressource empêche les nouveaux usages mais ne corrompt aucune fiche, instance ou export historique. |
| INV-FP-025 | Les cinq axes transcription, mathématiques, pédagogie, complétude et cohérence restent distincts. |
| INV-FP-026 | Une durée d'activité est soit directe sans phases, soit dérivée des phases ; jamais les deux comme valeurs indépendantes concurrentes. |
| INV-FP-027 | Une `TeacherSessionSheet` correspond exactement à une séance pédagogique prévue. |
| INV-FP-028 | Une séance peut traverser une frontière de séquence et seulement après achèvement complet de SA_n une frontière vers SA_n+1. |
| INV-FP-029 | Les `SessionCurriculumSegment` et `ExecutedCurriculumSegment` sont ordonnés. |
| INV-FP-030 | Les segments exécutés, et non un texte libre, fondent le calcul de progression. |
| INV-FP-031 | Temps normatif, durée prévue et durée réellement exécutée sont distincts. |
| INV-FP-032 | Un `LearnerSupport` n'est pas limité à une séance et peut être utilisé dans plusieurs fiches. |
| INV-FP-033 | Un support apprenant couvre exactement une séquence ou exactement une SA. |
| INV-FP-034 | Fiche enseignant et support apprenant peuvent partager les mêmes versions/blocs de départ, mais utilisent leurs propres familles d'instances locales et ne deviennent jamais le même objet métier. |
| INV-FP-035 | Une transcription fidèle peut être issue d'une source incomplète, ambiguë, mathématiquement erronée ou incohérente. |
| INV-FP-036 | Toute donnée manquante, ambiguë ou contradictoire est représentable par `SourceIssue` sans correction silencieuse. |
| INV-FP-037 | `SourceDocument` et `SourceOccurrence` restent distincts ; une occurrence appartient à exactement un document. |
| INV-FP-038 | Tout contenu proposé pour réparer une source reste séparé de la transcription, même après validation. |
| INV-FP-039 | Une séance historique utilisant un support conserve la révision exacte, la partie exacte et, par cette révision, les instances/snapshots exacts du support. |
| INV-FP-040 | Une révision de fiche ou de support `FINALIZED` est immuable ; toute correction crée une nouvelle révision. |
| INV-FP-041 | Une exécution réelle et ses écarts ne réécrivent jamais la préparation finalisée. |
| INV-FP-042 | Tant qu'une allocation curriculaire contradictoire n'est pas arbitrée, le reste théorique est déclaré indéterminé plutôt que calculé sur une valeur cachée. |
| INV-FP-043 | Chaque `FlowItem` est exactement d'un genre : activité, bloc indépendant ou section/étape. |
| INV-FP-044 | Une révision ne peut être finalisée si deux variantes concurrentes ciblent la même sortie ou si ses durées structurelles se contredisent. |
| INV-FP-045 | Chaque export conserve sa famille de document, la révision source exacte et la cible ayant produit son contenu. |
| INV-FP-046 | Toute `SheetResourceInstance` ou `SupportResourceInstance` a exactement une origine fonctionnelle : `LIBRARY_DERIVED` ou `LOCAL_ORIGINAL`, jamais les deux ni aucune. |
| INV-FP-047 | Une instance `LIBRARY_DERIVED` référence exactement une `PedagogicalResourceVersion` et snapshotte localement ses blocs utiles. |
| INV-FP-048 | Une instance `LOCAL_ORIGINAL` référence zéro version de bibliothèque et ne reçoit aucune fausse provenance ; elle contient au moins un bloc local. |
| INV-FP-049 | Toute adaptation dans un support s'effectue sur `SupportResourceInstance` / `SupportBlockInstance`; elle ne modifie pas la bibliothèque et reste figée dans une révision finalisée. |
| INV-FP-050 | Chaque `DocumentExport` provient exactement d'une `TeacherSheetRevision` ou d'une `LearnerSupportRevision`, jamais des deux simultanément. |

**Bilan après G1 :** 50 invariants ; 5 ajoutés ; 6 reformulés ; 0 conflit ; 0 règle validée supprimée ou affaiblie. INV-FP-010 protège la référence historique conditionnelle des deux familles d'instances ; INV-FP-023 l'applique explicitement à la fiche enseignant. INV-FP-040 reste inchangé et continue de garantir l'immutabilité des révisions finalisées.

## 25. Registre des arbitrages Q-M01

| ID | Sujet | Décision intégrée | Statut | Impact dans le modèle |
|---|---|---|---|---|
| Q-M01-01 | Instruction du guide | Texte officiel intact ; une ou plusieurs actions comme attributs analytiques ; aucune entité `InstructionRequirement` systématique | CLOSED | `InstructionGuide` versionnée par guide et reliée aux connaissances |
| Q-M01-02 | Mapping ressource ↔ instruction | Mapping qualifié en bibliothèque avant sélection ; relation plusieurs-à-plusieurs | CLOSED | Relation portée par `PedagogicalResourceVersion`, vue logique au niveau ressource |
| Q-M01-03 | Ressources atomiques/composites | Les deux sont admises ; `ACTIVITY_COMPLETE` reste sélectionnable comme un tout et éditable bloc par bloc | CLOSED | Toute version contient `1..* PedagogicalBlock` ordonné |
| Q-M01-04 | Versionnement ressources | Identité, version exacte et instance locale sont distinctes | CLOSED | Historique non rétroactif ; snapshot local |
| Q-M01-05 | Versionnement fiches | `DRAFT → FINALIZED`; correction par nouvelle révision ; export attaché à une révision | CLOSED | `TeacherSessionSheet`, `TeacherSheetRevision`, `DocumentExport` |
| Q-M01-06 | Validation multidimensionnelle | Cinq axes indépendants ; provenance simple ; aucun workflow juridique complexe | CLOSED | Statuts séparés sur version/bloc et adaptation locale |
| Q-M01-07 | Fiche enseignant vs support apprenant | Fiche = exactement une séance ; support = séquence ou SA, multi-séances | CLOSED | Deux identités et révisions distinctes, relation qualifiée `SupportUse` |

Aucune preuve documentaire ne force `NEW-ARBITRATION-REQUIRED`. Les divergences de durées sont des anomalies de données que le modèle conserve ; elles ne contredisent pas les décisions structurelles.

## 26. Stress-tests ST-001 à ST-030

### 26.1 Provenance, ressources et validation

| ID | Scénario | Objets concernés | Règle appliquée | Résultat attendu | Statut |
|---|---|---|---|---|---|
| ST-001 | Ressource entièrement originale, sans document source | Ressource, version, bloc | Occurrence externe `0..*`; INV-005/037 | Version `origin=ORIGINAL`, zéro occurrence, aucune fausse source | PASS |
| ST-002 | Ressource provenant de plusieurs documents | Version, occurrences, documents | Provenance plusieurs-à-plusieurs | Toutes les occurrences et métadonnées restent citées | PASS |
| ST-003 | Composite avec provenance différente par bloc | Version, blocs, occurrences | Provenance au bloc ; INV-006 | Chaque bloc cite sa propre occurrence, la ressource reste unique | PASS |
| ST-004 | Une instruction dispose de cinq formulations candidates | Instruction, cinq versions de ressources | Mapping plusieurs-à-plusieurs qualifié | Les cinq candidates sont disponibles ; l'enseignant choisit sans écraser l'instruction | PASS |
| ST-005 | Activité complète liée à plusieurs instructions | Version `ACTIVITY_COMPLETE`, instructions | Q-M01-02/03 | Une seule ressource composite porte plusieurs mappings | PASS |
| ST-006 | Activité de rappel sans nouvelle instruction | Version de ressource | Mapping `0..*`; INV-020 | Ressource qualifiable comme rappel avec zéro instruction | PASS |
| ST-007 | Ressource corrigée après usage | Ressource v1/v2, instance | Version immuable ; INV-003/004 | v2 est créée ; l'instance historique reste sur v1 | PASS |
| ST-008 | Ancienne fiche utilisant ancienne version | Révision, instance, version ancienne | Référence exacte ; INV-010/023 | Ouverture/export conserve le contenu historique | PASS |
| ST-009 | Source : « résultats attendus : à faire » | Occurrence, bloc, issue | Fidélité ≠ complétude ; INV-035/036 | Transcription `VERIFIED`, complétude `INCOMPLETE`, `MISSING_RESULT` | PASS |
| ST-010 | Source avec incohérence mathématique | Version, statuts, issue | Axes indépendants | Transcription peut être `VERIFIED`, math `REJECTED`, issue explicite | PASS |
| ST-011 | Transcription fidèle mais pédagogiquement douteuse | Version, validations | Q-M01-06 | Transcription `VERIFIED`, pédagogie `TO_REVIEW` ou `REJECTED` | PASS |
| ST-012 | Figure disponible seulement comme image | Bloc `FIGURE/IMAGE`, occurrence | TikZ non obligatoire | Image conservée et sourcée ; reconstruction future séparée | PASS |
| ST-013 | Bloc avec TikZ invalide | Bloc, rendu | Source ≠ rendu ; INV-011 | `RENDER_ERROR`, source TikZ intacte, finalisation avertie selon usage | PASS |
| ST-014 | Activité fortement modifiée dans une fiche | Instance, snapshots locaux | Copie adaptable ; INV-003/009 | Adaptation locale complète, provenance de départ conservée, validation locale à revoir | PASS |

### 26.2 Séance, progression et supports

| ID | Scénario | Objets concernés | Règle appliquée | Résultat attendu | Statut |
|---|---|---|---|---|---|
| ST-015 | Séance finit une séquence et commence la suivante | Révision, deux segments | Segments ordonnés ; INV-028/029 | Segment 1 `fin`, segment 2 `début`, durées sommées | PASS |
| ST-016 | Séance finit SA1 et commence SA2 | Révision, segments, progression | Achèvement préalable obligatoire | Accepté seulement si SA1 complète ; sinon finalisation bloquée | PASS |
| ST-017 | Prévu 1 h 50, réel 1 h 30 | Révision, séance exécutée | Prévu ≠ réel ; INV-031/041 | Préparation reste 110 min ; exécution enregistre 90 min et segments partiels | PASS |
| ST-018 | Support de séquence utilisé pendant quatre séances | Support-révision, quatre `SupportUse` | Relation plusieurs-à-plusieurs | Les quatre fiches pointent vers la même révision exacte | PASS |
| ST-019 | Fiche n'utilise qu'une partie du support | `SupportUse`, plage de blocs | Relation qualifiée | Partie utilisée identifiée sans découper ni dupliquer le support | PASS |
| ST-020 | Fiche finalisée corrigée après coup | Fiche, révisions 1 et 2 | Q-M01-05 ; INV-040 | R1 reste finalisée ; R2 est créée en brouillon puis finalisable | PASS |
| ST-021 | PDF exporté depuis une ancienne révision | Export, révision ancienne | INV-045 | L'export conserve révision, cible et date exactes | PASS |
| ST-022 | Activité avec TI/TG/TC | Instance, trois phases | Taxonomie extensible ; durée dérivée | Trois phases ordonnées ; durée activité = somme | PASS |
| ST-023 | Activité sans phase détaillée | Instance | Phase `0..*`; règle de durée | Durée directe autorisée ; aucune phase artificielle | PASS |
| ST-024 | Prise de notes sans activité | FlowItem, bloc local | Genre `STANDALONE_BLOCK` | Bloc ordonné directement dans le déroulement | PASS |
| ST-025 | Bloc enseignant, apprenant initial et complété | Bloc, trois variantes | Cibles distinctes ; INV-012/013/019 | Une variante effective par cible, contenus appropriés | PASS |
| ST-026 | Une variante valable pour plusieurs cibles | Variante multi-cible | Réutiliser l'identique | Une seule variante cible plusieurs sorties sans copie | PASS |
| ST-027 | Deux variantes concurrentes pour même sortie | Bloc, variantes | INV-019/044 | Conflit explicite ; finalisation refusée jusqu'à résolution | PASS |
| ST-028 | Ressource fidèle mais incomplète | Version, validations, issue | Axes indépendants | Transcription `VERIFIED`, complétude `INCOMPLETE`, issue ouverte | PASS |
| ST-029 | Deux valeurs contradictoires pour le même élément | Deux occurrences, allocation, issue | Ne pas choisir silencieusement ; INV-042 | Deux faits conservés, `INTERNAL_CONTRADICTION`, calcul normatif indéterminé | PASS |
| ST-030 | Ressource retirée après usage historique | Version `RETIRED`, instances | INV-024 | Nouvelle sélection empêchée ; anciennes fiches et exports intacts | PASS |

### 26.3 Bilan adversarial

- `PASS = 30/30`
- `FAIL = 0/30`
- `ARBITRATION_REQUIRED = 0/30`

ST-016 et ST-027 comportent un refus métier conditionnel attendu : ce refus prouve l'invariant et ne constitue pas un échec du modèle. ST-029 représente sans arbitrage caché les anomalies F-01 à F-06.

### 26.4 Addendum M01-G1 — fermeture des findings de revue

| Finding | Correction normative appliquée | Statut |
|---|---|---|
| M01-REV-001 | `SheetResourceInstance.source_resource_version = 0..1` sous exclusivité d'origine ; activité complète `LOCAL_ORIGINAL` admise avec `1..*` blocs et sans fausse source | CLOSED |
| M01-REV-002 | Ajout de `SupportResourceInstance` et `SupportBlockInstance`, avec snapshot, adaptation locale, origine locale possible et historique figé par révision de support | CLOSED |
| M01-REV-003 | `DocumentExport` provient exactement d'une révision enseignant ou d'une révision support, jamais des deux | CLOSED |

La promotion éventuelle d'une instance originale locale vers la bibliothèque n'est ni décidée ni modélisée par G1.

### 26.5 Stress-tests ciblés G1

| ID | Scénario | Objets concernés | Règle appliquée | Résultat attendu constaté | Statut |
|---|---|---|---|---|---|
| G1-ST-001 | Activité originale créée directement dans une fiche | Révision, instance fiche, blocs, FlowItem | INV-FP-046/048 ; cardinalité source `0..1` | `LOCAL_ORIGINAL`, zéro version source, `1..*` blocs locaux, aucune fausse provenance, item `ACTIVITY` valide | PASS |
| G1-ST-002 | R-017-v2 sélectionnée puis fortement adaptée | Instance fiche, snapshots, version | INV-FP-003/047 | `LIBRARY_DERIVED`, R-017-v2 exacte conservée, snapshots modifiés localement, bibliothèque intacte | PASS |
| G1-ST-003 | Définition de bibliothèque reformulée dans un support | Support-révision, instance/bloc support | INV-FP-047/049 | Version exacte et bloc de départ conservés ; reformulation locale historique ; bibliothèque intacte | PASS |
| G1-ST-004 | Exercice original créé directement dans un support | Support-révision, instance/blocs support | INV-FP-046/048/049 | `LOCAL_ORIGINAL`, zéro version/bloc source inventé, support finalisable avec `1..*` blocs | PASS |
| G1-ST-005 | Support S1 sur R-032-v1 après publication de v2 | Support-révision, instance, snapshots | INV-FP-004/039/049 | S1 reste sur v1 et sur ses snapshots exacts ; v2 n'a aucun effet rétroactif | PASS |
| G1-ST-006 | PDF enseignant depuis TeacherSheetRevision R3 | Export, R3 | INV-FP-045/050 | Famille enseignant, R3 exacte, zéro révision support | PASS |
| G1-ST-007 | PDF apprenant complété depuis LearnerSupportRevision S2 | Export, S2 | INV-FP-045/050 | Famille support, S2 exacte, cible complétée, zéro révision enseignant | PASS |
| G1-ST-008 | Export simultanément rattaché à R3 et S2 | Export, deux familles | Exclusivité INV-FP-050 | Refus métier de l'état à double source | PASS |
| G1-ST-009 | `LOCAL_ORIGINAL` avec source R-017-v2 | Instance locale, version | Exclusivité INV-FP-046/048 | Refus métier : origine et présence de source incompatibles | PASS |
| G1-ST-010 | `LIBRARY_DERIVED` sans version source | Instance locale | Exigence INV-FP-047 | Refus métier : source exacte obligatoire | PASS |

**Bilan G1 ciblé :** `PASS = 10/10`, `FAIL = 0/10`.

### 26.6 Matrice de non-régression des stress-tests M01 impactés

| ST | Impact G1 | Résultat |
|---|---|---|
| ST-001 | Une ressource originale de bibliothèque sans document source reste valide ; G1 ajoute séparément l'original local | UNCHANGED_PASS |
| ST-003 | La provenance différente par bloc d'une ressource composite reste inchangée | UNCHANGED_PASS |
| ST-007 | La correction de bibliothèque préserve désormais explicitement aussi les instances de support | STRENGTHENED_PASS |
| ST-008 | La référence conditionnelle exacte est clarifiée pour toutes les instances dérivées | STRENGTHENED_PASS |
| ST-014 | L'adaptation forte est explicitement bornée à une instance `LIBRARY_DERIVED` et ses snapshots | STRENGTHENED_PASS |
| ST-018 | Les quatre séances conservent la révision de support et ses snapshots exacts | STRENGTHENED_PASS |
| ST-019 | La partie de support utilisée pointe vers des instances/blocs locaux explicitement modélisés | STRENGTHENED_PASS |
| ST-020 | Le cycle `DRAFT → FINALIZED` et la nouvelle révision corrective restent inchangés | UNCHANGED_PASS |
| ST-021 | La source d'export est désormais exacte et exclusive par famille | STRENGTHENED_PASS |
| ST-025 | Les variantes enseignant/apprenant restent applicables aux snapshots locaux concernés | STRENGTHENED_PASS |
| ST-026 | Une variante multi-cible reste réutilisable sans duplication dans le support | STRENGTHENED_PASS |
| ST-030 | Le retrait de bibliothèque préserve explicitement fiches, supports et exports historiques | STRENGTHENED_PASS |

**Bilan non-régression ciblé :** `UNCHANGED_PASS = 3`, `STRENGTHENED_PASS = 9`, `REGRESSION = 0`.

## 27. Questions résiduelles non bloquantes

| ID | Question | Nature | Traitement avant usage concerné |
|---|---|---|---|
| QR-M01-01 | Quelle allocation de travail retenir pour chacune des quatre SA de 4e entre programme et guide ? | Arbitrage de contenu officiel, pas de structure | Autorité pédagogique humaine ; jusque-là, conserver les deux valeurs et signaler l'indétermination |
| QR-M01-02 | Quelle numérotation/durée retenir pour « Configurations de l'espace » en Terminale D ? | Hors pilote, constat de généralisation | Arbitrage seulement avant ingestion normative Tle D |
| QR-M01-03 | Quelles valeurs initiales retenir dans les taxonomies extensibles de ressources, blocs et phases ? | Paramétrage fonctionnel mineur | Commencer par les listes de M01 ; enrichir sans changer les objets |
| QR-M01-04 | Quels `SourceIssue` ouverts seront acceptés comme limite de source plutôt que résolus ? | Gouvernance éditoriale | Décision humaine au cas par cas ; aucune correction silencieuse |

Ces questions ne changent ni les identités, ni les relations, ni les cardinalités du modèle. Elles n'imposent pas `NEW-ARBITRATION-REQUIRED` pour M01.

## 28. Hors périmètre

Sont explicitement exclus de M01 :

- choix de framework, langage, stockage, schéma physique ou architecture ;
- noms de tables, identifiants techniques, index, migrations, endpoints et contrats techniques ;
- interfaces et maquettes supplémentaires ;
- moteur de rendu ou de compilation LaTeX/TikZ ;
- authentification et autorisations applicatives ;
- workflow juridique complexe ;
- IA générative, certification automatique, moteur de recommandation ;
- marketplace, réputation, likes, abonnements et fonctions communautaires avancées ;
- extension du contenu officiel au-delà des sources et arbitrages humains.

## 29. Critères de passage à M02

| Critère | Preuve dans M01 | Résultat |
|---|---|---|
| Objets nécessaires identifiés | Sections 8 et 9 | PASS |
| Distinctions conceptuelles sans confusion | Terminologie, objets et diagrammes | PASS |
| Cardinalités critiques définies | Section 11 | PASS |
| 30 stress-tests supportés | Section 26 | PASS — 30/30 |
| Invariants cohérents | Section 24 | PASS — 50, dont 5 ajoutés par G1, 0 conflit |
| Q-M01-01..07 intégrées | Section 25 | PASS — 7 CLOSED |
| Findings M01-REV-001..003 fermés | Section 26.4 | PASS — 3 CLOSED |
| Stress-tests G1 ciblés | Section 26.5 | PASS — 10/10 |
| Non-régression M01 ciblée | Section 26.6 | PASS — 3 inchangés, 9 renforcés, 0 régression |
| Sources incomplètes/incohérentes représentables | Sections 3.2 et 16 | PASS |
| Progression par séance calculable | Section 17 | PASS |
| Indépendance technologique | Ensemble du document ; section 28 | PASS |
| Aucun blocage caché | Findings, questions résiduelles et stress-tests explicites | PASS |

**Gate M02 : NON LANCÉ PAR G1.** Les trois lacunes de revue humaine sont fermées et M01 est éligible au micro-réaudit indépendant de gel. M02 ne doit commencer qu'après ce réaudit et la proclamation séparée du freeze définitif. Les arbitrages F-01 à F-06 restent nécessaires avant de publier une valeur curriculaire unique pour les données concernées, mais ils demeurent non bloquants pour le modèle.

## 30. Verdict final

**PASS — M01-G1 TARGETED DOMAIN CLOSURE FIX COMPLETED  
READY FOR INDEPENDENT REAUDIT**

Motif : M01-REV-001, M01-REV-002 et M01-REV-003 sont fermés ; les 10 stress-tests G1 passent ; les 12 stress-tests M01 ciblés comptent 3 passages inchangés, 9 renforcés et aucune régression. Les 50 invariants sont cohérents, Q-M01-01 à Q-M01-07 restent `CLOSED`, F-01 à F-07 restent ouverts/non bloquants et QR-M01-01 à QR-M01-04 restent non bloquantes. Aucun code ni choix d'architecture n'a été introduit. Le freeze définitif n'est pas proclamé par G1.
