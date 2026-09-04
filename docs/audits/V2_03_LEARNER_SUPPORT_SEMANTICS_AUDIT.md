# V2-03 — Sémantique des documents apprenants

Date : 2026-09-04. Verdict : PASS_WITH_NON_BLOCKING_ITEMS.

Le support issu d'une fiche copie le déroulement visible dans un brouillon
apprenant distinct. Il conserve les blocs sources et les copies adaptées, mais
exclut EXPECTED_RESPONSE, EXPECTED_RESULT, EXPECTED_TRACE, SOLUTION,
CORRECTION, TEACHER_NOTE, RESPONSE_SPACE et ANSWER_SPACE.
Définitions, propriétés, formules, méthodes, remarques et figures restent autorisées.
Les champs de résultats du déroulement ne sont jamais copiés côté apprenant.

Le bouton produit un PDF et conserve le brouillon dans Mes supports. Celui-ci
reste éditable avant sa propre finalisation ; la fiche enseignant n'est pas modifiée.
Le rendu ne remplace plus une copie adaptée par une variante de la bibliothèque.

`LEARNER_COMPLETED` reste accepté pour compatibilité API, avec la même exclusion
des réponses que le support standard. Le bouton « PDF complété » a été retiré.
Le test historique qui attendait une réponse dans ce PDF a été adapté à cette
nouvelle règle explicite. Les snapshots et anciens fichiers ne sont pas réécrits
par la migration ; régénérer un PDF applique en revanche le nouveau moteur de rendu.

Les suffixes historiques « Réponse : » suivis d'un espace vertical sont retirés
au rendu uniquement. Aucun autre texte libre n'est analysé comme une réponse :
la séparation repose sur le typage correct par l'auteur. Le support 7, autrefois
allongé par ces zones, tient maintenant sur une page. Son snapshot reste identique
avant/après compilation. Les titres de consigne restent attachés à leur début de texte.

## Inspection réelle

Quatre PDF A4 compilés avec LaTeX, sources `.tex` conservées dans `exports/` :

- `v2_03_enseignant.pdf` : 1 page, situation, deux consignes, propriété, application,
  figure locale, résultat saisi de contrôle et trace attendue.
- `v2_03_apprenant.pdf` : 1 page, mêmes blocs apprenants dont la figure, aucune réponse enseignant.
- `v2_03_support_long.pdf` : 1 page, contenu historique, définition, méthode et figure TikZ.
- `v2_03_multipage.pdf` : 3 pages, fixture de mise en page répétant trois fois le support
  historique en mémoire ; aucune insertion curriculaire ni modification de révision.

Les six pages finales ont été inspectées. Pas de débordement ou de texte technique
automatique constaté. Les documents finaux portent le titre « Produits remarquables —
découverte et application ». Les pointillés servent au découpage, pas à réserver une
zone de réponse. Les blocs ordinaires restent entiers ; au-delà de 85 % de la hauteur
utile d'une page, un bloc redevient sécable pour éviter un débordement.
Les figures sont limitées à la largeur d'une colonne.

Preuves PNG : `v2-03-visual/*-final-1.png`, `multipage-1.png` à `multipage-3.png`.
Les `*-first-1.png` conservent la première inspection et ses libellés corrigés.
Le scénario documentaire final est la fiche `FICHE-F0A66C2DFA5C` (révision 30),
finalisée explicitement via API, et son support `SUPPORT-149367C726B1` (révision 13).
Le schéma réutilise le bloc local du support historique 7 : sa référence est portée
par la ressource versionnée 5, classée LOCAL_TEACHER. Aucune origine officielle
ni nouvelle validation mathématique n'est revendiquée.
Tests LEARNER, TEACHER, UXDOC et compilation réelle. Le contrôle multipage valide
la mise en page ; il ne certifie pas le contenu pédagogique répété pour cet essai.
