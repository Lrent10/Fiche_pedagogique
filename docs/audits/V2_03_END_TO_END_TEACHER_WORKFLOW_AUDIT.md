# V2-03 — Parcours enseignant de bout en bout

Date : 2026-09-04. FUNCTIONAL_VERDICT = PASS_WITH_NON_BLOCKING_ITEMS.
INTUITIVENESS_VERDICT = NOT_INDEPENDENTLY_TESTED.

## Observations dans le navigateur local

Tests conduits par l'agent dans le navigateur réel, pas par un enseignant indépendant.
Le formulaire montre les quatre périmètres, I/II préremplis, le conflit 56/60 h et
les instructions. Les sources sont consultables. Inspection visuelle de l'écran effectuée.

| Étape | Manuel | Automatique |
|---|---|---|
| Périmètre | 4e, SA1, séquence 8, instructions 3/4/6 | Identique |
| Création | Commencer la conception | Composition automatique |
| I/II | Préremplis ; établissement de test et durée 55 min saisis | Préremplis |
| Ressources | Produits remarquables/propriété, application, parcelle | Produits partagés et parcelle |
| Adaptation | Résultat attendu de contrôle saisi dans le déroulement | Deuxième sélection remplacée par application |
| Aperçu et PDF | Enseignant + création du support apprenant | Aperçu du brouillon puis de la fiche |
| Finalisation | Action explicite, état finalisé observé | Action explicite, état finalisé observé |
| Durée approximative | 90 s | 41 s |

Fiche manuelle : `FICHE-BE6EB797B87D`, révision ID 28.
Support dérivé : `SUPPORT-B372C62CC1D4`, révision ID 12 (brouillon).
Fiche automatique : `FICHE-0CC96A573C5F`, révision ID 29.
Ces objets de contrôle restent dans la base locale ; les fiches antérieures n'ont
pas été éditées. Les résultats et durées incomplets restent des champs enseignant
à renseigner ; finalisé signifie figé techniquement, pas certifié pédagogiquement.

Un scénario documentaire complémentaire via API a ensuite ajouté une figure
locale traçable : fiche `FICHE-F0A66C2DFA5C` (révision 30, finalisée), support
`SUPPORT-149367C726B1` (révision 13, brouillon), ressource locale versionnée 5.
Les PDF livrés sous `exports/v2_03_*.pdf` utilisent ce scénario complet ; ils ne
sont pas présentés comme les clics chronométrés des deux parcours précédents.

## Frictions et récupération observées

- OBSERVED : le pilote ne propose pas de candidat pour chaque instruction.
  Les parcours ont explicitement limité le périmètre à 3/4/6.
- OBSERVED : la confirmation native de finalisation a fait expirer l'appel du
  contrôleur navigateur (4 s), mais l'état finalisé a été confirmé par la lecture
  suivante. Aucune seconde finalisation ni perte de saisie constatée.
- OBSERVED : premier PDF avec « Expected Trace », corrigé en « Trace attendue ».
  La numérotation de séquence est désormais naturelle dans le document.
- OBSERVED : titres orphelins dans l'essai multipage corrigés au rendu.
- NOT_TESTED : facilité d'usage par un professeur découvrant seul le produit,
  productivité moyenne, accessibilité complète, impression papier physique.

## Vérifications techniques

Campagne finale : 77 backend, 42 frontend, build PASS. Les anciens tests de
sauvegarde avant navigation, cohérence 4e et CTA directs sont inclus.
Migration vide et migration 0003 avec conservation de données : PASS.
Dernier startup réel : HTTP 200/200 ; PID backend 16272, frontend 4732,
enregistrés et identiques aux listeners 8000/5173. Aucun ancien listener présent
avant ce démarrage. `alembic current` et `heads` donnent tous deux 0004.
La campagne a inclus l'arrêt/reprise par les scripts ; arrêt final avant commit.
`git diff --check` et empreinte M01 : PASS. Voir le rapport final pour le SHA livré.

La compilation LaTeX réelle et l'inspection des documents sont décrites dans
`V2_03_LEARNER_SUPPORT_SEMANTICS_AUDIT.md`. L'avertissement Vite sur un bundle
de 505,29 kB est non bloquant, sans optimisation d'architecture dans cette mission.
