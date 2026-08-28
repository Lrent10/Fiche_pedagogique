# Tester le MVP — Fiches pédagogiques de mathématiques 4e

## Démarrer

Prérequis : Windows 10/11. Python, Node.js et MiKTeX sont déjà disponibles dans l’environnement où le MVP a été préparé.

Depuis PowerShell, dans ce dossier :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

Ouvrir ensuite : **http://127.0.0.1:5173/**  
Documentation technique de l’API : **http://127.0.0.1:8000/docs**  
Aucun compte n’est nécessaire.

## Scénario de test en 10 minutes

1. Ouvrir **Mes fiches**, puis la fiche de démonstration.
2. Parcourir les huit étapes et vérifier les instructions du guide.
3. À **Choix des activités**, sélectionner deux cartes avec **Comparer**.
4. Ajouter une activité, puis modifier un bloc LaTeX à **Adaptation**.
5. Réordonner un bloc dans **Déroulement** et contrôler la durée totale.
6. Consulter l’aperçu et les avertissements avant finalisation.
7. Finaliser, générer le PDF enseignant puis créer une nouvelle révision.
8. Ouvrir **Supports apprenants** et générer les PDF initial et complété.
9. Sur une fiche finalisée, cliquer **Marquer comme effectuée** et saisir une durée réelle.
10. Ouvrir **Progression** : l’exécution est comptée et le reste normatif demeure indéterminé car les sources indiquent 56 h et 60 h.

## Arrêter ou réinitialiser

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop-dev.ps1
powershell -ExecutionPolicy Bypass -File .\scripts\reset-demo.ps1
```

Limitations : pilote limité à SA1/Séquence 8, SQLite local, TikZ visible dans le PDF plutôt que dans l’aperçu KaTeX. Voir `docs/KNOWN_LIMITATIONS.md`.
