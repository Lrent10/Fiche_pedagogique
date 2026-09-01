# Audit de l'éditeur final de document

## Couverture fonctionnelle

| Contrôle | Brouillon | Finalisé | Résultat |
|---|---:|---:|---|
| Sélection d'un bloc dans la structure | Oui | Oui, lecture seule | PASS |
| Modification du titre | Oui | Non | PASS |
| Modification du LaTeX | Oui | Non | PASS |
| Aperçu immédiat | Oui | Oui | PASS |
| Masquage / réaffichage | Oui | Non | PASS |
| Monter / descendre | Oui | Non | PASS |
| Sauvegarde et actualisation | Oui | Non | PASS |
| Erreur dollars / accolades | Visible, sauvegarde bloquée | Sans objet | PASS |
| Identification et planification accessibles | Oui | Oui, lecture seule | PASS |
| Checklist de relecture | Oui | Oui | PASS |

## Scénario vérifié

Sur `FICHE-4E-006 r1`, le premier bloc a été renommé « Mise en situation », son contenu a été remplacé, un bloc a été masqué puis réaffiché et une consigne a été descendue. L'ordre final imprimé correspond à l'ordre affiché. Une accolade LaTeX non refermée produit « Les accolades LaTeX ne sont pas équilibrées » et désactive la sauvegarde.

Après finalisation, les champs, cases et boutons de mutation sont désactivés. Le PDF régénéré contient les données finales et non une version antérieure.

## Persistance et invariants

- Le champ `visible` est persisté sur les blocs de fiche enseignant par la migration `0003_final_document_editor`.
- Une nouvelle version recopie la visibilité et les valeurs éditées sans rendre modifiable la version finalisée.
- Les exports filtrent les blocs masqués.
- La mutation backend refuse une version non brouillon.

Verdict : **PASS** pour l'éditeur final ; la figure pleine largeur appartient au moteur de composition du support et non à cet éditeur.
