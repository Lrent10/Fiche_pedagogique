# Tester la V2 - fidélité documentaire et support-first

## Démarrer

Dans PowerShell, depuis le dépôt :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

Ouvrir `http://127.0.0.1:5173/`.

## Parcours support-first

1. Ouvrir **Supports apprenants** puis créer un support.
2. Ajouter une activité, éditer un bloc LaTeX, le réordonner et vérifier sa visibilité.
3. Générer **PDF initial** et **PDF complété**.
4. Finaliser la révision du support.
5. Cocher deux blocs avec **Utiliser dans la séance**.
6. Régler la durée puis cliquer **Créer la fiche**.
7. Dans la fiche, vérifier le lien vers le support et compléter les champs d'identification/planification.
8. À l'étape **Déroulement**, saisir les **RÉSULTATS ATTENDUS** manuellement en LaTeX et vérifier l'aperçu.
9. Finaliser puis générer le PDF enseignant.
10. Créer une nouvelle révision du support et vérifier que l'ancienne fiche reste liée à l'ancienne révision.

## Vérification automatisée

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\test-all.ps1
```

## Arrêter

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop-dev.ps1
```

Les trois nouvelles ressources 4e ne font pas partie de cette V2-01/V2-02 et ne doivent pas être importées pendant ce test.
