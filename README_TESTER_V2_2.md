# Tester V2.2 — Conception depuis le curriculum

Pilote local 4e, SA1 / séquence 8. V2-03 ajoute le préremplissage I/II, les choix
par instruction, la composition automatique contrôlée et le support sans réponses.
Les contenus dérivés du guide restent des adaptations à relire.

## Démarrer et vérifier

Depuis la racine du dépôt dans PowerShell :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\test-all.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

Ouvrir `http://127.0.0.1:5173/`. Le démarrage applique la migration additive
`0004_curriculum_authoring` et installe les attributs manquants du petit pilote.
Il refuse de démarrer si les ports 8000/5173 sont déjà occupés ou si migration/seed échoue.
Ne pas supprimer la base pour mettre à jour.

Pour contrôler la migration :

```powershell
Push-Location .\backend
..\.venv\Scripts\python.exe -m alembic current
..\.venv\Scripts\python.exe -m alembic heads
Pop-Location
```

Les deux résultats doivent indiquer `0004_curriculum_authoring`.

## Parcours manuel

1. Cliquer « Nouvelle fiche ». Choisir classe, SA, séquence ou instruction.
2. Lire I/II préremplis et les références dépliables. Le conflit de durée 56/60 h
   reste visible ; choisir soi-même la durée de séance.
3. Pour un premier essai avec le corpus fourni, ne retenir que les instructions
   « Énoncer les propriétés… », « Utiliser les produits remarquables… » et
   « Développer un produit » (positions 3, 4, 6).
4. Cliquer « Commencer la conception ». Renseigner les champs locaux. Les valeurs
   curriculaires se personnalisent explicitement ; une autre classe que 4e reste refusée.
5. À l'étape des consignes, parcourir les instructions, lire les formulations et
   choisir une ressource. Une ressource personnelle peut être enregistrée dans
   la bibliothèque pour l'instruction courante, avec son type et son LaTeX.
6. Adapter le déroulement, les durées et les résultats attendus. Ceux-ci sont une
   saisie enseignant à relire, jamais une correction officielle produite par le moteur.
7. Dans l'éditeur final, vérifier visibilité, ordre, contenu et aperçu. Exporter
   le PDF enseignant et créer le support apprenant. Celui-ci reste dans Mes supports.
8. Finaliser explicitement. La suite des adaptations exige une nouvelle révision.

## Parcours rapide

Reprendre le même périmètre couvert, puis « Composition automatique ». Le brouillon
s'ouvre en aperçu avec les choix effectués. Revenir aux consignes, remplacer une
sélection, compléter les informations locales et les résultats attendus, puis relire
et finaliser. La composition seule ne finalise jamais.

Avec toutes les instructions cochées, le pilote manque de ressources pour 1/2/5/7.
Le refus est attendu : réduire le périmètre ou ajouter des consignes personnelles
par le parcours manuel. Aucune donnée manquante n'est fabriquée.

## Résultats à observer

- I/II ne repartent pas de zéro ; chaque donnée dérivée reste traçable.
- « Suivant », aperçu et finalisation enregistrent d'abord les modifications.
- Les sources locales, communautaires, livres, inspection et documents officiels
  ne sont pas confondues. Un document officiel ne certifie pas une adaptation.
- Une propriété ou une définition peut être imprimée côté apprenant ; les résultats
  enseignant et grandes zones de réponse sont exclus.
- L'ancien export API `LEARNER_COMPLETED` reste compatible, sans réintroduire les réponses.
- Les fichiers finalisés restent figés. Le moteur de rendu peut évoluer lors d'une
  nouvelle exportation ; les anciens snapshots ne sont pas modifiés.

## Preuves de la mission

Campagne : 77 tests backend, 42 frontend, build PASS. Installation vide et upgrade
0003 avec données préexistantes testés. Les parcours navigateur de l'agent durent
environ 90 s / 41 s ; ils ne remplacent pas une évaluation indépendante par enseignants.

PDF et LaTeX éditables sous `exports/` : `v2_03_enseignant`, `v2_03_apprenant`,
`v2_03_support_long`, `v2_03_multipage` (ce dernier est une fixture répétée de QA).
Images finales sous `docs/audits/v2-03-visual/`. Les sept rapports V2_03 détaillent
sources, modèle, préremplissage, ressources, composition, sémantique et parcours.

Limites : corpus partiel ; champs locaux et résultats à compléter ; aucune
certification mathématique ; inspection déclarative sans comptes ; SQLite seul
testé ; longues consignes susceptibles de continuer sur une autre colonne.
Pas de synchronisation cloud ni de déploiement public.

Pour arrêter :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop-dev.ps1
```
