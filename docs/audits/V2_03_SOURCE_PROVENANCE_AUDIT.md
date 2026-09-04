# V2-03 — Sources et correspondance Première C

Date : 2026-09-04. Verdict : PASS pour la traçabilité du pilote et l'analyse du modèle.
Pas de certification d'exhaustivité ou d'ingestion Première C.

## Documents effectivement lus

Les pages citées sont des numéros de pages PDF, sauf mention contraire.
Les chemins ont été résolus sur le poste ; aucun document n'a été modifié.

| Référence | Document et chemin sous `C:\Users\HP\Desktop\Base` | Pages |
|---|---|---|
| P4 | `4ème\930040566-programme-4ieme-Maths-certifie.pdf` | 127 |
| G4 | `4ème\783063322-GUIDE-4eme-Maths-Certifie-Vu.pdf` | 100 |
| P1C | `1ère\C\696438897-PPC-1ere-C-VEROFF.pdf` | 80 |
| F1C | `1ère\C\1ère C cour complet.pdf` | 98 |

Empreintes SHA-256 vérifiées :

```text
P4  7795DD2370DB4C879187F5FCBC7247BABCAB2AB0A3FD9D9F579663D0114FD62D
G4  A6E937B03DA51229E3C23D16A7105CAA4338BC29B4853B27374A1977E4BFAB93
P1C 064C2A4BDB8AB71E97D55BC57A52A8E1EDC5CF2A3DAE10116F878256CFCD8469
F1C 467813DCC67AC210DC5B15EE0C4794B457DDFDDE1B6E9344987052DC9EBDAC5C
```

P4/G4 portent les références institutionnelles béninoises et l'édition de 2020.
P1C est le programme Première C de juillet 2010. F1C est un cours Collection O.R.O,
attribué à ORO DJIBRIL Nabil et MANGOU Koudous : une source enseignante, non un
programme officiel. Le nom « Certifié » d'un fichier ne certifie pas nos transcriptions.

## Ancrage du pilote 4e

P4 p. 89 : SA1 Configurations du plan et trois compétences disciplinaires.
G4 pp. 31–32 : séquence 8, calcul sur les expressions algébriques, contenus,
instructions, compétence transversale et compétence disciplinaire propres à la séquence.
Les contenus et connaissances du préremplissage sont des synthèses normalisées
des instructions, pas des citations littérales. Les compétences reprennent le
texte avec normalisation typographique. P4/G4 divergent sur la durée SA (56/60 h) :
le conflit reste affiché. Les ressources historiques liées à G4 pp. 74–77 restent
des adaptations à relire, sans validation mathématique ou documentaire nouvelle.

## Mini-audit Première C

| Maillon | Observation source | Interprétation bornée |
|---|---|---|
| Programme | P1C p. 10 : dégager l'orthogonalité de droites/plans à partir de solides ; SA1 tôt dans l'année | Instruction générale de géométrie, non consigne d'élève |
| SA | P1C p. 67 : SA1 Configurations de l'espace, 21 h | Périmètre officiel et durée de SA |
| Séquence | F1C p. 6 : Séquence 1, Orthogonalité dans l'espace | Découpage de ces auteurs ; aucun numéro de séquence officiel inféré |
| Objectif / instruction | P1C p. 10 ; F1C p. 6, activité 1 « Droites orthogonales » | Correspondance thématique explicite, à valider avant ingestion |
| Planification | P1C p. 73 (imprimée 75) : compétences ; p. 74 (imprimée 76) : connaissances et 21 h | Attributs de SA, pas compétences à recopier artificiellement sur toutes les activités |
| Consigne observée | F1C pp. 5–6 : dessin d'armoire ; trouver des droites parallèles à (AB)/(EH) et perpendiculaires entre elles | Ressource enseignante mettant en œuvre l'objectif |
| Formulation | F1C p. 6 : Définition 1 séparée de Consigne 1, séparateurs de découpe | DEFINITION distincte de réponse attendue |
| Choix locaux | F1C p. 5 : TI/TG/TC définis par chaque enseignant | Stratégies/durées locales, jamais prétendues officielles |

Les pages G4 p. 32, P4 p. 89 et F1C p. 6 ont aussi été rendues et inspectées
visuellement. La différence entre 80 pages PDF et la pagination imprimée « sur 82 »
de P1C est conservée. Une future ingestion exige repérage page par page, choix
des versions et revue des formulations ; la Première C n'est pas activée dans l'UI.

## Provenance jusqu'au document

Sources → attributs/instructions/ressources versionnées → sélection persistée →
copies de blocs → nouvelle révision. Les PDF ne publient pas les identifiants,
hashes ou statuts techniques ; ces références restent consultables dans l'application.
L'absence de statut de validation n'est pas convertie en « officiel validé ».
L'API d'enrichissement est locale, sans circuit de comptes inspecteurs authentifiés.
