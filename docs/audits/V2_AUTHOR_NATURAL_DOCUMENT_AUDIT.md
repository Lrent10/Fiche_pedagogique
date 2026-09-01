# Audit des documents naturels pour l'auteur

Date : 2026-08-30  
Verdict : **PASS_WITH_NON_BLOCKING_ITEMS**

## Fiche enseignant

Le PDF `fiche_enseignant_FICHE-4E-006_r1.pdf` est une page A4. L'identification, la planification et le déroulement sont hiérarchisés comme dans la référence `pa.pdf` page 2, sans chercher une reproduction graphique exacte.

Contrôles réussis :

- numéro pédagogique visible : `3`, sans repli vers un identifiant technique ;
- titres français : Mise en situation, Consigne, Propriété, Application ;
- stratégies, durées et résultats attendus associés aux bons blocs ;
- aucun pied de page technique, statut, code de bloc ou identifiant interne ;
- aucun chevauchement, débordement ou formule coupée observé au rendu.

## Supports apprenants

Les variantes initiale et complétée de `SUPPORT-4E-004 r1` font chacune trois pages A4 en deux colonnes.

- La variante initiale masque les blocs réservés à la correction.
- La variante complétée affiche notamment la trace attendue.
- Les activités sont numérotées de manière continue ; les consignes sont numérotées indépendamment.
- Les préfixes automatiques répétés ont été supprimés : pas de « Consigne - Consigne » ni « Propriété - Propriété ».
- La figure TikZ est nette et lisible.
- Aucun des motifs `FICHE-4E`, `SUPPORT-4E`, `Révision`, `DRAFT`, `FINALIZED`, `EXPECTED_` ou « généré localement » n'apparaît dans le texte imprimé.

## Comparaison aux références

SOURCE : `pa.pdf` page 2 et `1ère C cour complet.pdf` page 5, rendues sans modifier les sources.

EXTRACTION : la référence enseignant privilégie une page très dense et encadrée ; la référence de cours emploie colonnes, séparations fortes, figures intégrées et typographie sérif.

INTERPRÉTATION : la V2 reprend l'architecture documentaire et les conventions pédagogiques utiles, avec davantage d'air et des zones de réponse adaptées à un support apprenant. Elle n'est pas une copie pixel à pixel.

RECOMMANDATION non bloquante : offrir ultérieurement un choix « figure dans la colonne / figure pleine largeur » et un réglage de hauteur des zones de réponse.

## Empreintes des livrables vérifiés

| PDF | Pages | SHA-256 |
|---|---:|---|
| `fiche_enseignant_FICHE-4E-006_r1.pdf` | 1 | `19C9ECF346566C2F0BB658FA5932F6B455771BE278860E83A21FF1708C58CBE6` |
| `fiche_apprenant_initiale_SUPPORT-4E-004_r1.pdf` | 3 | `6DE5DE6131A954BA1CE5226AFE9FB37C51A8D4362BA249DDF4F86BAAAA551118` |
| `fiche_apprenant_completee_SUPPORT-4E-004_r1.pdf` | 3 | `404AA900FD7D29EAC93EE3C80E9B029A8D81BE7172499FE9247BF61D862B7DDE` |
