# Journal des frictions UX V2-02B

| ID | Friction observée | Sévérité initiale | Correction / décision | État |
|---|---|---:|---|---|
| UX-FR-01 | Un support vide pouvait être finalisé. | MAJOR | Blocage frontend et backend avec message naturel. | Corrigé |
| UX-FR-02 | L'étape finale ne permettait pas d'éditer le document comme un tout. | MAJOR | Éditeur à trois zones : structure, aperçu, bloc sélectionné. | Corrigé |
| UX-FR-03 | Les titres, contenus, positions et visibilités n'étaient pas tous ajustables au dernier moment. | MAJOR | Commandes d'édition, déplacement, visibilité et sauvegarde ajoutées. | Corrigé |
| UX-FR-04 | Une erreur LaTeX simple pouvait parvenir jusqu'à l'export. | MAJOR | Contrôle des dollars et accolades, message local et sauvegarde désactivée. | Corrigé |
| UX-FR-05 | Des termes techniques ou ambigus apparaissaient dans l'interface. | MINOR | « Portée » devient « Périmètre », « Révision » devient « Version » dans les actions, codes d'avertissement masqués. | Corrigé |
| UX-FR-06 | Le bouton principal de l'éditeur final pouvait devenir blanc sur fond blanc. | MINOR | Règle CSS spécifique rétablit le contraste. | Corrigé |
| UX-FR-07 | L'éditeur de support ne permettait pas de composer un document long hors bibliothèque. | MAJOR | Ajout de blocs locaux typés, sans modifier la bibliothèque ni ingérer V2-03. | Corrigé |
| UX-FR-08 | Le script de démarrage pouvait déclarer l'application prête alors que d'anciens serveurs occupaient les ports. | MAJOR | Refus explicite des ports occupés, attente HTTP et enregistrement des vrais PID. | Corrigé |
| UX-FR-09 | Le script global pouvait masquer un échec backend. | MAJOR | Contrôle immédiat du code retour après chaque étape. | Corrigé |
| UX-FR-10 | Les figures larges restent confinées à une colonne. | MINOR | Limite conservée et documentée ; pas de refonte de mise en page dans ce lot. | Ouvert non bloquant |
| UX-FR-11 | Les zones de réponse très hautes créent une composition aérée sur les pages 2 et 3. | MINOR | Accepté pour le test long ; aucune collision ni coupure de formule. | Ouvert non bloquant |

Les frictions « corrigées » ont été revérifiées soit par scénario humain, soit par test automatisé ciblé. Elles ne constituent pas une certification de contenu mathématique officiel.
