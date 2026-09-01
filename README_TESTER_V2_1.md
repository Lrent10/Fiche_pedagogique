# Tester la V2.1 — finition humaine et documentaire

## Démarrer

Dans PowerShell, à la racine du dépôt :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

Ouvrir `http://127.0.0.1:5173/`. Si un service utilise déjà le port 8000 ou 5173, le démarrage s'arrête et indique le processus concerné.

## Parcours court recommandé

1. Ouvrir **Supports apprenants** et créer un support.
2. Ajouter une activité de la bibliothèque, puis un **bloc local**.
3. Modifier le LaTeX, l'ordre et la visibilité ; générer l'aperçu PDF.
4. Finaliser le support et vérifier que ses champs sont verrouillés.
5. Sélectionner des blocs et créer la fiche enseignant.
6. Compléter identification, planification, stratégies, durées et résultats attendus.
7. Dans **Aperçu & édition finale**, renommer un bloc, le déplacer et le masquer temporairement.
8. Saisir volontairement une accolade non refermée : la sauvegarde doit être bloquée avec un message clair.
9. Corriger, finaliser et générer le PDF enseignant.
10. Vérifier qu'aucun identifiant interne, statut technique ou texte de génération n'est imprimé.

## Vérification automatisée

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\test-all.ps1
```

Résultat attendu pour cette révision : 34 tests backend, 3 tests frontend et build de production réussis.

## Arrêter

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop-dev.ps1
```

Ce test valide le fonctionnement et le rendu du pilote local. Il ne certifie pas l'origine officielle ni la fidélité mathématique d'un contenu ajouté localement.
