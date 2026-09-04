# V2-03 — Identification et planification

Date : 2026-09-04. Verdict : PASS sur les valeurs présentes dans les sources du pilote.

| Donnée | Applicabilité / source | Traitement |
|---|---|---|
| Pays, discipline, classe | Programme 4e, couverture ; ProgrammeVersion | Préremplissage I |
| SA et titre | SA1, programme p. 89 | Préremplissage I |
| Séquence et titre | Guide pp. 31–32 | Préremplissage I |
| Trois compétences disciplinaires | SA1, programme p. 89 | Héritage II |
| Compétence disciplinaire et transversale de calcul algébrique | Séquence 8, guide p. 32 | Ajout II |
| Contenus, connaissances et techniques | Instructions du guide pp. 31–32 | Synthèses normalisées, non citations littérales |
| Durée SA | Programme 56 h / guide 60 h | Conflit affiché, aucun arbitrage automatique |
| Établissement, professeur, année | Profil local du navigateur | Reprise éditable, jamais officielle |
| Date, effectif, groupes, séance, matériel, stratégies | Saisie enseignant | Restent libres |

La compétence transdisciplinaire n'est pas inventée à partir d'un exemple de
fiche. L'exemple du guide pp. 74–78 ne suffit pas à transformer chaque champ local
de cette séance en obligation générale de séquence.

Chaque valeur dérivée conserve source_kind, source_id/ref, empreinte/version,
page et scope. Les origines `CURRICULUM_DERIVED`, `MANUAL_USER_ENTRY`,
`REUSED_TEACHER_DATA`, `USER_OVERRIDE` restent distinctes. Une modification ou
suppression curriculaire nécessite un override explicite ; elle conserve ses
références d'origine sans rester étiquetée comme valeur officielle.
Le contrôle classe/programme 4e continue de s'appliquer après override.

Le formulaire affiche I/II avant création. Le brouillon conserve son snapshot :
pas d'écrasement silencieux lors d'une navigation ou d'une réouverture.
Les champs locaux stables sont mémorisés dans le navigateur après création.

Preuves : tests AUTO et TEACHER ; tests UX-004/005 et non-régression de la
persistance avant navigation ; parcours manuel réel, établissement et durée
enregistrés puis retrouvés dans le PDF. La réutilisation locale a une provenance
testée côté API. Les informations saisies ensuite dans une fiche ne sont pas
automatiquement synchronisées vers ce profil : limite du MVP local.
