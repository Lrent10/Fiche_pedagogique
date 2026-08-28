# M01-G1 — Final Independent Reaudit

**Projet :** Générateur de fiches pédagogiques de mathématiques — MVP pilote 4e — Bénin  
**Nature :** réaudit fonctionnel indépendant, read-only sur le candidat M01-G1  
**Candidat audité :** `C:\Users\HP\Documents\ChatGPT\Fiche_pedagogique\M01_FUNCTIONAL_DOMAIN_MODEL_FINAL_CANDIDATE.md`  
**SHA-256 du candidat audité :** `03F54F7C62A0E6F2F3BE154631EE542408BF5423B5D4FAD8B147CD85CE0E3B67`  
**Date :** 28 août 2026  
**Verdict :** **PASS — M01 FUNCTIONAL DOMAIN MODEL FROZEN**

## 1. Objet du réaudit

Déterminer, sans corriger le candidat ni accorder de crédit automatique à ses verdicts déclarés, si les trois fermetures G1 sont réelles, cohérentes et sans régression :

- M01-REV-001 — cycle de vie d'une activité locale originale ;
- M01-REV-002 — snapshots et adaptations locales du support apprenant ;
- M01-REV-003 — exclusivité de la révision source d'un export.

Le réaudit reconstruit les 27 assertions, les 10 tests G1 et les 12 tests M01 impactés à partir des objets, relations, cardinalités, cycles de vie et invariants du candidat. Il ne lance pas M02 et n'introduit aucun choix technique.

## 2. Baseline contrôlée

| Élément | Valeur constatée | Preuve dans le candidat | Résultat |
|---|---|---|---|
| Statut G1 | Closure fix completed, ready for independent reaudit | En-tête, lignes 3 à 7 | PASS |
| Verdict G1 | `PASS — M01-G1... READY FOR INDEPENDENT REAUDIT` | En-tête et section 30 | PASS |
| Arbitrages | Q-M01-01..07 tous `CLOSED` | Section 25 | PASS |
| Findings G1 | M01-REV-001..003 tous `CLOSED` | Section 26.4 | PASS |
| Stress-tests M01 | 30/30 déclarés `PASS` | Sections 26.1 à 26.3 | PASS — présence contrôlée |
| Stress-tests G1 | 10/10 déclarés `PASS` | Section 26.5 | PASS — présence contrôlée |
| Invariants | INV-FP-001..050, séquence complète | Section 24 | PASS |
| Conflits déclarés | 0 | Bilan section 24 | PASS — à réauditer ci-dessous |
| Régressions ciblées déclarées | 0 | Section 26.6 | PASS — à réauditer ci-dessous |
| Findings documentaires | F-01..F-07 présents et ouverts/non bloquants | Section 3.2 | PASS |
| Questions résiduelles | QR-M01-01..04 explicites/non bloquantes | Section 27 | PASS |
| Freeze préalable | Non proclamé par G1 | Section 30 | PASS |

## 3. Préconditions

Toutes les préconditions sont satisfaites. Le candidat est lisible, sa structure contient 30 sections principales, le dossier de sortie est accessible et aucun rapport antérieur au même chemin n'existait. Aucun kill switch n'est déclenché.

Le candidat a été lu intégralement. Les `PASS` inscrits ont uniquement servi à contrôler l'état attendu de la baseline ; les conclusions ci-dessous résultent d'une nouvelle application des règles.

## 4. Réaudit de M01-REV-001

### 4.1 Reconstruction

`SheetResourceInstance` est une ressource locale de exactement une `TeacherSheetRevision`. Son origine est exclusive :

```text
LIBRARY_DERIVED
  → exactement 1 PedagogicalResourceVersion
  → 1..* SheetBlockInstance, dont les snapshots dérivés gardent leur bloc source

LOCAL_ORIGINAL
  → 0 PedagogicalResourceVersion
  → 1..* SheetBlockInstance locaux
  → aucune fausse provenance
```

Une instance locale originale peut représenter une activité complète et être référencée par un `FlowItem` de genre `ACTIVITY`. Une instance dérivée garde sa version exacte après adaptation forte. Les adaptations restent locales. Le candidat exclut explicitement de G1 toute décision de promotion future vers la bibliothèque.

### 4.2 Conclusion

M01-RAD-001..008 passent indépendamment. Les états contradictoires `LOCAL_ORIGINAL + version source` et `LIBRARY_DERIVED + aucune version source` sont exclus par les cardinalités qualifiées et INV-FP-046..048.

**M01-REV-001 = CONFIRMED_CLOSED.**

## 5. Réaudit de M01-REV-002

### 5.1 Reconstruction

Le support dispose d'une chaîne locale propre :

```text
LearnerSupportRevision
  → 0..* SupportResourceInstance en DRAFT
  → 1..* SupportResourceInstance pour FINALIZED

SupportResourceInstance
  → origine LIBRARY_DERIVED ou LOCAL_ORIGINAL, exclusivement
  → 0..1 PedagogicalResourceVersion selon l'origine
  → 1..* SupportBlockInstance

SupportBlockInstance
  → 0..1 PedagogicalBlock source
  → source exacte si dérivé, aucune source inventée si original
```

Les instances de support sont distinctes des versions/blocs de bibliothèque et des instances de fiche enseignant. Elles portent modification, omission, remplacement, complément et variantes apprenant. Une révision finalisée est immuable ; `SupportUse` conserve la révision exacte et la partie exacte, donc les instances/snapshots exacts contenus par cette révision.

### 5.2 Conclusion

M01-RAD-009..021 passent indépendamment. La création locale dans un support et l'adaptation d'une version de bibliothèque ont des parcours complets et exclusifs. Aucun chemin n'autorise une modification rétroactive de la bibliothèque ou d'une révision finalisée.

**M01-REV-002 = CONFIRMED_CLOSED.**

## 6. Réaudit de M01-REV-003

### 6.1 Reconstruction

Les deux relations vers `DocumentExport` sont optionnelles prises séparément mais soumises à une règle globale d'exactitude :

```text
TeacherSheetRevision → 0..* DocumentExport
LearnerSupportRevision → 0..* DocumentExport

Pour chaque DocumentExport :
  exactement 1 TeacherSheetRevision
  XOR
  exactement 1 LearnerSupportRevision
```

L'export conserve famille de document, révision exacte, cible, date/instant et statut de rendu. L'exclusivité est exprimée comme règle fonctionnelle, sans structure physique imposée.

### 6.2 Conclusion

M01-RAD-022..027 passent indépendamment. Les deux branches sont possibles, l'absence totale de source et la double source sont toutes deux interdites.

**M01-REV-003 = CONFIRMED_CLOSED.**

## 7. Assertions M01-RAD-001 à M01-RAD-027

| ID | Assertion réauditée | Base probante indépendante | Verdict |
|---|---|---|---|
| M01-RAD-001 | Origine fiche : exactement `LIBRARY_DERIVED` ou `LOCAL_ORIGINAL` | Description `SheetResourceInstance`; INV-FP-046 | PASS |
| M01-RAD-002 | Instance fiche dérivée → exactement une version | Cardinalité conditionnelle ; INV-FP-023/047 | PASS |
| M01-RAD-003 | Instance fiche originale → zéro version | Description ; cardinalité ; INV-FP-023/048 | PASS |
| M01-RAD-004 | Activité complète créée directement dans une fiche | Sections 10.3, 18.4 et 20 ; FlowItem `ACTIVITY` | PASS |
| M01-RAD-005 | Original local fiche → `1..*` blocs, aucune fausse provenance | Cardinalité blocs ; INV-FP-048 | PASS |
| M01-RAD-006 | Adaptation forte garde la version exacte | Versionnement §13.2 ; INV-FP-010/047 | PASS |
| M01-RAD-007 | Adaptation locale ne modifie pas la bibliothèque | Principes §6.4 ; relations §10.3 ; INV-FP-003 | PASS |
| M01-RAD-008 | Aucun workflow de promotion imposé | Exclusion explicite §26.4 | PASS |
| M01-RAD-009 | Révision support possède des instances locales explicites | Objets §8/9.5 ; cardinalité support | PASS |
| M01-RAD-010 | Instance support distincte de version bibliothèque | Identités et relation `0..1`; INV-FP-009/034 | PASS |
| M01-RAD-011 | Bloc support distinct du bloc bibliothèque | Objets §9.5 ; relation source `0..1` | PASS |
| M01-RAD-012 | Ressource de bibliothèque snapshotée avant adaptation support | Relations §10.4 ; INV-FP-047/049 | PASS |
| M01-RAD-013 | Adaptation support ne modifie pas la bibliothèque | §9.5, §10.4 ; INV-FP-049 | PASS |
| M01-RAD-014 | Origines support exclusives | Description instance support ; INV-FP-046 | PASS |
| M01-RAD-015 | Original local support → zéro version | Cardinalité conditionnelle ; INV-FP-048 | PASS |
| M01-RAD-016 | Exercice/activité original directement dans support | §9.5 et §19 | PASS |
| M01-RAD-017 | Bloc support original → zéro bloc source | Description bloc support ; cardinalité `0..1` | PASS |
| M01-RAD-018 | Bloc support dérivé garde son bloc exact | Description §9.5 ; provenance §14 ; INV-FP-047 | PASS |
| M01-RAD-019 | Révision support finalisée fige ses instances | Cycle §12.3 ; versionnement §13.5 ; INV-FP-040/049 | PASS |
| M01-RAD-020 | Séance garde révision, partie et snapshots support exacts | `SupportUse`; INV-FP-039 | PASS |
| M01-RAD-021 | Familles d'instances fiche/support distinctes | Objets §8 ; diagramme ; INV-FP-034 | PASS |
| M01-RAD-022 | Export depuis révision enseignant | Cardinalité export enseignant | PASS |
| M01-RAD-023 | Export depuis révision support | Cardinalité export support | PASS |
| M01-RAD-024 | Export possède exactement une révision source | Cardinalité globale ; INV-FP-050 | PASS |
| M01-RAD-025 | Double rattachement interdit | Description export ; INV-FP-050 | PASS |
| M01-RAD-026 | Métadonnées fonctionnelles complètes de l'export | Description `DocumentExport` | PASS |
| M01-RAD-027 | Aucune représentation technique prescrite | Description export et hors périmètre §28 | PASS |

**Bilan assertions : 27 PASS / 27 ; 0 FAIL / 27.**

## 8. Audit des invariants G1

| Invariant | Objects | Cardinalities | Stress-tests | Conflict | Verdict |
|---|---|---|---|---|---|
| INV-FP-009 | Deux familles d'instances locales couvertes | Compatible avec appartenance à une révision | G1-001..005 | Aucun | PASS |
| INV-FP-010 | Référence exacte conditionnée par l'origine | Compatible avec `0..1` + implication | G1-002/003/005 | Aucun avec INV-004/023 | PASS |
| INV-FP-023 | Cas fiche dérivé/original explicites | Exactement `1` ou `0` selon origine | G1-001/002/009/010 | Aucun | PASS |
| INV-FP-034 | Fiche et support partagent seulement les sources | Familles locales séparées | G1-003/005 ; ST-018/019 | Aucun avec Q-M01-07 | PASS |
| INV-FP-039 | Support historique exact | `SupportUse` vise la révision et la partie | G1-005 ; ST-018/019 | Aucun | PASS |
| INV-FP-045 | Export conserve famille/révision/cible | Deux branches optionnelles + XOR global | G1-006..008 ; ST-021 | Aucun | PASS |
| INV-FP-046 | Origine exclusive et totale | Qualifie les deux relations `0..1` | G1-001/004/009/010 | Aucun | PASS |
| INV-FP-047 | Dérivé exige version et snapshots | `1` conditionnel ; blocs `1..*` | G1-002/003/005/010 | Aucun | PASS |
| INV-FP-048 | Original local sans fausse source | `0` conditionnel ; blocs `1..*` | G1-001/004/009 | Aucun avec INV-005/037 | PASS |
| INV-FP-049 | Adaptation support locale et figée | Instances appartiennent à une révision | G1-003..005 | Aucun avec INV-040 | PASS |
| INV-FP-050 | Source export exclusive | Exactement une des deux branches | G1-006..008 | Aucun avec INV-045 | PASS |

Le verdict normatif de l'audit est : 11/11 invariants sensibles PASS, 0 conflit.

Les invariants non sensibles ont aussi été contrôlés par séquence et par dépendances. Aucun des 39 autres invariants ne contredit les cinq ajouts G1. En particulier, INV-FP-003/004 protègent la bibliothèque et l'historique, INV-FP-024 protège le retrait, et INV-FP-040 protège les révisions finalisées.

## 9. Audit des cardinalités G1

| Relation | Cardinalité constatée | Règle de fermeture | Combinaisons invalides encore admises ? | Verdict |
|---|---|---|---|---|
| TeacherSheetRevision → SheetResourceInstance | `0..*`; instance → révision `1` | Instance locale à une seule révision | Non | PASS |
| SheetResourceInstance → PedagogicalResourceVersion | `0..1` | Dérivé ⇒ `1`; original ⇒ `0` | Non | PASS |
| SheetResourceInstance → SheetBlockInstance | `1..*` | Toute instance a du contenu local | Non | PASS |
| SheetBlockInstance → PedagogicalBlock | `0..1` | Snapshot dérivé garde la source ; ajout original n'en invente pas | Non | PASS |
| LearnerSupportRevision → SupportResourceInstance | `0..*` DRAFT, `1..*` FINALIZED | Support finalisé non vide | Non | PASS |
| SupportResourceInstance → PedagogicalResourceVersion | `0..1` | Dérivé ⇒ `1`; original ⇒ `0` | Non | PASS |
| SupportResourceInstance → SupportBlockInstance | `1..*` | Toute instance a du contenu local | Non | PASS |
| SupportBlockInstance → PedagogicalBlock | `0..1` | Dérivé exact ; original sans fausse source | Non | PASS |
| TeacherSheetRevision → DocumentExport | `0..*`; retour `0..1` | Exclusivité globale | Non | PASS |
| LearnerSupportRevision → DocumentExport | `0..*`; retour `0..1` | Exclusivité globale | Non | PASS |
| DocumentExport → branche source | exactement une des deux | XOR fonctionnel total | Non | PASS |

Le `0..1` brut n'est jamais interprété seul : INV-FP-046..048 rendent l'origine totale et conditionnent le nombre de versions sources. De même, les deux `0..1` des exports sont complétés par INV-FP-050. Le modèle fonctionnel n'autorise donc ni état sans origine, ni origine double, ni export sans source, ni export à double source.

## 10. Réexécution indépendante de G1-ST-001 à G1-ST-010

| Test | Reconstruction indépendante | Règle décisive | Résultat |
|---|---|---|---|
| G1-ST-001 | Créer une instance fiche originale, lui donner deux blocs, l'ordonner comme activité | Origine originale ⇒ zéro version ; blocs `1..*`; FlowItem ACTIVITY | PASS |
| G1-ST-002 | Copier R-017-v2, snapshotter ses blocs, modifier localement | Dérivé ⇒ version exacte ; bibliothèque immuable | PASS |
| G1-ST-003 | Copier une définition dans un support puis reformuler le snapshot | Instance/bloc support distincts ; version/bloc sources conservés | PASS |
| G1-ST-004 | Créer un exercice original et ses blocs dans un support DRAFT puis finaliser | Original ⇒ zéro source ; finalisé exige au moins une instance | PASS |
| G1-ST-005 | Finaliser S1 sur v1, publier v2 | Révision finalisée + snapshots immuables | PASS |
| G1-ST-006 | Export enseignant depuis R3 | Branche enseignant unique, R3 exacte | PASS |
| G1-ST-007 | Export apprenant complété depuis S2 | Branche support unique, S2 exacte, cible conservée | PASS |
| G1-ST-008 | Tenter R3 + S2 sur le même export | INV-FP-050 interdit la double branche | PASS — refus correct |
| G1-ST-009 | Déclarer original local avec R-017-v2 | INV-FP-046/048 rendent l'état contradictoire | PASS — refus correct |
| G1-ST-010 | Déclarer dérivé sans version | INV-FP-047 rend la source obligatoire | PASS — refus correct |

**Bilan : 10 PASS / 10 ; 0 FAIL / 10.**

## 11. Non-régression M01 ciblée

| ST | Réaudit indépendant | Résultat |
|---|---|---|
| ST-001 | L'originalité d'une ressource de bibliothèque (`PedagogicalResourceVersion`, zéro occurrence externe possible) reste distincte de `LOCAL_ORIGINAL` | UNCHANGED_PASS |
| ST-003 | La provenance au bloc reste portée par les blocs de bibliothèque et copiée dans les snapshots dérivés | UNCHANGED_PASS |
| ST-007 | v2 ne modifie ni instances fiche ni instances support basées sur v1 | STRENGTHENED_PASS |
| ST-008 | Une ancienne fiche garde sa version exacte via l'instance dérivée et ses snapshots | STRENGTHENED_PASS |
| ST-014 | L'adaptation forte reste locale et conserve son origine/version de départ | STRENGTHENED_PASS |
| ST-018 | Quatre séances peuvent viser la même révision finalisée et ses snapshots | STRENGTHENED_PASS |
| ST-019 | `SupportUse` conserve la partie exacte dans une révision au contenu figé | STRENGTHENED_PASS |
| ST-020 | La correction d'une révision finalisée crée toujours une nouvelle révision | UNCHANGED_PASS |
| ST-021 | Un export ancien garde désormais en plus une famille source exclusive | STRENGTHENED_PASS |
| ST-025 | Les variantes enseignant/apprenant restent applicables aux blocs/snapshots concernés | STRENGTHENED_PASS |
| ST-026 | Une variante identique peut toujours viser plusieurs cibles sans duplication | STRENGTHENED_PASS |
| ST-030 | Le retrait d'une version empêche le nouvel usage mais conserve fiches, supports et exports historiques | STRENGTHENED_PASS |

**Bilan : UNCHANGED_PASS = 3 ; STRENGTHENED_PASS = 9 ; REGRESSION = 0.**

## 12. Audit snapshots et historique

### 12.1 Les trois sens d'« original »

| Cas | Identité | Version de bibliothèque source | Occurrence externe | Confusion possible après application des invariants ? |
|---|---|---:|---:|---|
| Ressource originale de bibliothèque | `PedagogicalResource` + version | Elle est elle-même la version | `0..*`, donc zéro possible | Non : `origin=ORIGINAL` appartient à l'objet bibliothèque |
| Original local de fiche | `SheetResourceInstance` | `0` | Aucune fausse occurrence | Non : `origin=LOCAL_ORIGINAL` et appartenance à une révision fiche |
| Original local de support | `SupportResourceInstance` | `0` | Aucune fausse occurrence | Non : `origin=LOCAL_ORIGINAL` et appartenance à une révision support |

ST-001 traite le premier cas ; G1-ST-001 et G1-ST-004 traitent respectivement les deux autres. Le vocabulaire est suffisamment discriminé par l'objet porteur et la valeur d'origine. Aucun finding n'est requis.

### 12.2 Chaîne non rétroactive

```text
PedagogicalResourceVersion v1
  → instance locale dérivée
  → snapshots locaux
  → adaptation locale
  → révision FINALIZED

Publication ultérieure de v2
  ↛ révision ancienne
  ↛ snapshots anciens
  ↛ TeachingSession ancienne
  ↛ SupportUse ancien
  ↛ DocumentExport ancien
```

La non-rétroactivité résulte conjointement des versions immuables, de la référence exacte, des snapshots locaux, de l'immutabilité `FINALIZED` et du rattachement des faits/exports à une révision exacte. Aucun chemin fonctionnel de remplacement automatique n'est défini.

## 13. Audit FINALIZED et faits historiques

| Objet historique | Garantie | Verdict |
|---|---|---|
| `TeacherSheetRevision FINALIZED` | Immuable ; correction par nouvelle révision DRAFT | PASS |
| `LearnerSupportRevision FINALIZED` | Immuable ; instances et blocs locaux figés | PASS |
| `TeachingSession` | Référence exactement la révision enseignant finalisée utilisée | PASS |
| `SupportUse` | Référence la révision support et la partie exactes | PASS |
| `DocumentExport` | Référence une révision exacte dans une seule famille | PASS |
| Version de bibliothèque ultérieure | Ne remplace aucune instance/snapshot contenu dans une révision finalisée | PASS |

Les cycles de vie et INV-FP-004, 010, 039, 040, 045, 047, 049 et 050 forment une chaîne cohérente. Aucun historique mutable n'est représentable selon les règles fonctionnelles.

## 14. Contrôle de F-01 à F-07

Les sept findings existent toujours dans la section 3.2 : quatre divergences de durées 4e, deux contradictions Terminale D et un résultat attendu manquant en 3e. Le texte conserve les deux valeurs contradictoires ou la lacune ; aucune valeur n'a été choisie et aucun résultat n'a été inventé.

La phrase suivant le registre les maintient ouverts jusqu'à arbitrage humain et non bloquants pour la structure. G1 n'a ni modifié leur contenu ni changé leur statut.

**F-01..F-07 preserved = PASS.**

## 15. Contrôle de QR-M01-01 à QR-M01-04

Les quatre questions demeurent explicites dans la section 27 : allocations 4e, numérotation/durée Tle D, taxonomies extensibles et traitement des `SourceIssue`. Elles sont qualifiées de décisions de contenu, généralisation, paramétrage ou gouvernance éditoriale, sans modifier les identités, relations ou cardinalités.

Elles ne cachent aucun besoin structurel indispensable à M02 et ne sont pas résolues par le réaudit.

**QR-M01-01..04 non-blocking = PASS.**

## 16. Contrôle de périmètre

La recherche ciblée des termes interdits ne trouve que :

- « architecture » et « stockage » dans les exclusions de périmètre ;
- « framework » dans la liste explicite des choix exclus ;
- « moteur de rendu » dans l'exclusion d'une implémentation concrète ;
- la déclaration finale qu'aucun code ou choix d'architecture n'a été introduit.

Aucune table, FK, ORM, UUID, SQL, PostgreSQL, JSONB, endpoint, API, service, microservice, base de données ou représentation physique de l'exclusivité n'est prescrite. Les objets `SupportResourceInstance` et `SupportBlockInstance` portent une identité et des invariants métier propres ; ils ne sont pas des composants techniques artificiels.

**Technical architecture introduced = NO.**

## 17. Nouveaux findings

| Classe | Nombre | Détail |
|---|---:|---|
| BLOCKER | 0 | Aucun |
| MAJOR | 0 | Aucun |
| MINOR | 0 | Aucun constat rédactionnel affectant l'interprétation normative |
| INFO | 0 | Aucun ajout nécessaire au gel |

Le réaudit n'invente pas de finding stylistique. Aucun quatrième besoin structurel n'est découvert.

## 18. Gate M02

Les trois closures sont confirmées, les 27 assertions passent, les 10 tests G1 passent, les 12 tests M01 ciblés ne régressent pas, les 50 invariants sont cohérents, et aucun finding bloquant ou majeur n'est ouvert.

```text
M01 FREEZE = CLOSED
M02 GATE = OPEN
```

`M02 GATE = OPEN` signifie uniquement que M02 peut désormais être préparé. Ce réaudit ne lance ni ne conçoit M02.

## 19. Verdict

**PASS — M01 FUNCTIONAL DOMAIN MODEL FROZEN**

Réponse à la question d'audit : oui, les trois closures G1 sont correctes, cohérentes de bout en bout et sans régression. Le modèle fonctionnel est suffisamment explicite et stable pour que M02 soit préparé sans nouvelle décision métier structurelle.

**M01 FREEZE = CLOSED**  
**M02 GATE = OPEN**
