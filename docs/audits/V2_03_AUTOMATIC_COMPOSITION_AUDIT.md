# V2-03 — Composition automatique contrôlée

Date : 2026-09-04. Verdict : PASS sur un périmètre couvert.

Le moteur résout le périmètre et les attributs I/II, puis filtre les candidats de
chaque instruction. La priorité est : programme/guide, inspection, communauté,
livre, local, démonstration explicitement autorisée. Le tirage aléatoire ne départage
que les candidats du meilleur niveau présent. Une graine rend ce tirage reproductible.
La provenance réelle, la version, l'instruction et l'origine AUTO_SELECTED sont enregistrées.

Une ressource retenue pour plusieurs instructions est copiée une seule fois dans
le déroulement ; les liens multiples restent conservés. Le résultat est DRAFT,
éditable, avec champs de réponses attendues vides et durées locales à renseigner.
Aucun appel de finalisation ni moteur IA ne fait partie de la composition.

Si une instruction n'a aucun candidat compatible, la requête échoue avant de
créer la fiche et indique les instructions manquantes. L'enseignant peut réduire
le périmètre ou ajouter une ressource personnelle par le parcours manuel.
Il ne reçoit pas une fiche présentée à tort comme complète.

Preuves : RAND-001..004 et COMP-001..003, test d'absence de fiche partielle,
incompatibilité de classe, exclusion démo, priorité inspection, tirage déterministe.
Parcours navigateur automatique sur instructions 3/4/6 : brouillon directement
ouvert en aperçu, remplacement de la deuxième sélection, puis finalisation explicite.
Temps observé environ 41 s contre 90 s pour le parcours manuel de contrôle.
Ces mesures d'agent ne sont pas une étude de productivité d'enseignants.

La couverture documentaire du pilote est limitée : une composition des sept
instructions sans enrichissement est refusée pour 1/2/5/7. Ce refus protège la
fidélité et ne signifie pas que ces instructions sont absentes du curriculum.
