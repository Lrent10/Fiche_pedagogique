# Audit UX humaine V2-02B

Date : 2026-08-30  
Branche : `audit/v2-human-ux-document-finalization`  
Verdict : **PASS_WITH_NON_BLOCKING_ITEMS**

## Périmètre exécuté

Deux passages complets ont été réalisés dans l'application locale avec une persona enseignante de 4e : création et révision d'un support, sélection des blocs pour une séance, identification, planification, déroulement, résultats attendus, aperçu final, finalisation et exports PDF.

Le second passage a éprouvé l'éditeur final : renommage de bloc, modification LaTeX, masquage/réaffichage, déplacement, sauvegarde avec actualisation, erreur LaTeX visible et verrouillage après finalisation.

Un support long distinct, `SUPPORT-4E-004 r1`, a été composé depuis l'interface avec 12 sections et 15 blocs. Il contient trois activités structurées, sept consignes imprimées, une définition, une propriété, une méthode, une remarque, une figure TikZ et des zones de réponse. Les deux variantes font trois pages A4.

## Résultats observés

- Les libellés visibles sont naturels : « Version », « Périmètre », « Nouvelle version », « Aperçu & édition finale ».
- Les codes de contrôle internes ne sont pas affichés dans les avertissements destinés à l'enseignant.
- Un support vide ne peut plus être finalisé ; le message indique l'action à effectuer.
- Les champs et commandes deviennent non modifiables après finalisation.
- La fiche enseignant conserve exactement le lien vers la révision du support utilisée.
- Le démarrage refuse maintenant les ports déjà occupés et enregistre les vrais processus à arrêter.
- Le script global ne peut plus annoncer un succès si un sous-test ou le build échoue.

## Preuves

- Fiche enseignant : `docs/audits/human-ux/teacher-final/page-1.png`.
- Support initial long : `docs/audits/human-ux/support-long-initial/page-1.png` à `page-3.png`.
- Support complété long : `docs/audits/human-ux/support-long-completed/page-1.png` à `page-3.png`.
- Références visuelles : `docs/audits/human-ux/references/pa-page-2.png` et `premiere-c-page-5.png`.

## Limites non bloquantes

- Les figures restent ajustées à la largeur d'une colonne ; aucun mode pleine largeur n'est exposé.
- Les grandes zones de réponse peuvent produire des pages volontairement aérées. Le document reste lisible et sans collision, mais une composition plus compacte pourra être proposée ultérieurement.
- L'acceptation de la boîte native de confirmation a bloqué le contrôleur de test. L'action a néanmoins abouti dans l'interface et l'état final a été revérifié après redémarrage ; ce point concerne l'outil de test, pas l'application.

## Conclusion

Aucun défaut MAJOR n'est ouvert dans le périmètre V2-02B. Le parcours enseignant est compréhensible, réversible tant que le document est en brouillon, puis correctement verrouillé. Les deux limites restantes sont documentaires et non bloquantes pour le pilote local.
