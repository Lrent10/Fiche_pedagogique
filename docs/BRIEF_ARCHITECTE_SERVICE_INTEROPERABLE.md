# Brief architecte — service interopérable avec le générateur de fiches pédagogiques

**Projet concerné :** Générateur de fiches pédagogiques de mathématiques — pilote 4e, Bénin  
**Date du brief :** 1er septembre 2026  
**Objet :** fournir à un architecte le contexte nécessaire pour analyser et concevoir un nouveau service qui fonctionnera avec l’application existante, sans casser ses règles de traçabilité et de versionnement.

## 1. Résumé exécutif

L’application existante aide un professeur à construire un support apprenant, sélectionner les blocs réellement utilisés, créer la fiche enseignant correspondante, compléter manuellement les informations pédagogiques et les résultats attendus en LaTeX, finaliser les documents, les exporter en PDF puis enregistrer l’exécution d’une séance.

Il s’agit aujourd’hui d’un **MVP local mono-utilisateur**, limité à un pilote de mathématiques de 4e (SA1 / Séquence 8). Il fonctionne sur Windows, écoute uniquement sur `127.0.0.1`, utilise une API FastAPI, une interface React et une base SQLite. Le modèle a été pensé pour rester portable vers PostgreSQL, mais cette compatibilité n’a pas encore été validée sur une instance PostgreSQL réelle.

Le futur service devra s’intégrer par des **contrats d’API explicites**. Il ne devra pas écrire directement dans la base de l’application ni modifier silencieusement une révision finalisée. La conception devra attribuer clairement la propriété de chaque donnée et préserver l’identité exacte des versions et révisions échangées.

## 2. Finalité métier de l’application existante

### Utilisateur principal

Un professeur de mathématiques préparant et exécutant une séance.

### Parcours principal

1. Créer ou ouvrir un support apprenant.
2. Ajouter des ressources de la bibliothèque ou des blocs locaux.
3. Modifier le contenu LaTeX, l’ordre et la visibilité des blocs.
4. Prévisualiser puis finaliser une révision du support.
5. Sélectionner les blocs exacts prévus pour une séance.
6. Créer une fiche enseignant à partir de cette sélection.
7. Compléter l’identification, la planification, les stratégies, les durées et les résultats attendus.
8. Finaliser et exporter la fiche enseignant en PDF.
9. Exporter le support apprenant en version initiale ou complétée.
10. Enregistrer la séance réalisée et consulter la progression.

### Règles métier structurantes

- Une révision en brouillon est modifiable; une révision finalisée est immuable.
- Une nouvelle modification après finalisation crée une nouvelle révision.
- Une fiche créée depuis un support conserve le lien vers la révision exacte du support et les identifiants des blocs sélectionnés.
- Les contenus copiés dans une fiche ou un support sont des instantanés: une évolution ultérieure de la bibliothèque ne modifie pas l’historique.
- Les résultats attendus sont saisis manuellement par le professeur en LaTeX. Ils ne sont ni générés par IA ni copiés automatiquement depuis une solution ou un corrigé source.
- Les sorties professeur et apprenant sont distinctes.
- Les PDF utilisateurs ne doivent pas afficher d’identifiants internes, de statuts techniques ou de textes de débogage.
- Une incohérence de source reste visible comme telle; l’application ne doit pas inventer une valeur pour la masquer.

## 3. État implémenté vérifié

### Baseline versionnée

- Branche de référence V2 : `feature/v2-document-fidelity-support-first`.
- Commit de référence : `414ce83e19dd629fce75cedef2d2d97950712de9`.
- Cette baseline comprend le workflow support → fiche, le versionnement, les exports enseignant/apprenant et la migration Alembic `0002_v2_document_workflow`.
- Vérification enregistrée : 24 tests backend, 3 tests frontend, build de production, migration, démarrage backend/frontend et contrôle visuel de trois PDF.

### Améliorations V2-02B présentes dans le checkout actuel

Le checkout est sur la branche `audit/v2-human-ux-document-finalization`. Il contient des modifications locales non commitées par rapport au commit de référence. Elles ajoutent notamment :

- un éditeur final structuré pour les brouillons;
- le changement d’ordre et de visibilité des blocs;
- des blocs locaux dans le support;
- une validation LaTeX simple et lisible;
- le blocage de la finalisation d’un support vide;
- des libellés plus naturels dans les PDF;
- une migration `0003_final_document_editor`;
- des améliorations de démarrage et de tests locaux.

La campagne V2-02B enregistrée a obtenu 34 tests backend, 3 tests frontend et un build réussi. Les PDF inspectés comptaient une page enseignant et trois pages pour chaque variante apprenant. Le verdict était **PASS_WITH_NON_BLOCKING_ITEMS**. Ces améliorations doivent être distinguées de la baseline tant qu’elles ne sont pas commitées et intégrées.

**Contrôle effectué pour ce brief le 1er septembre 2026 :** la suite du checkout actuel passe avec 34 tests backend, 3 tests frontend et un build de production réussi. Ce contrôle confirme le fonctionnement technique courant; il ne transforme pas les modifications locales en baseline versionnée.

### Ce que cette validation ne prouve pas

Elle prouve le fonctionnement technique du pilote et la qualité des exemples contrôlés. Elle ne certifie pas l’origine officielle, l’exhaustivité du programme, la fidélité mathématique de tout contenu ajouté localement, la tenue en charge, la sécurité d’un déploiement public ni le fonctionnement multi-utilisateur.

## 4. Architecture actuelle

```text
Interface React 19 + TypeScript + Vite
                |
                | JSON/HTTP local
                v
API FastAPI — monolithe modulaire
  - curriculum et sources
  - bibliothèque pédagogique
  - fiches enseignant
  - supports apprenant
  - exécution et progression
  - rendu et exports
                |
                v
SQLAlchemy 2 + Alembic
                |
                v
SQLite local
```

### Technologies

| Couche | Technologie actuelle |
|---|---|
| Backend | Python, FastAPI, Pydantic |
| Persistance | SQLAlchemy 2, Alembic |
| Base testée | SQLite |
| Cible envisagée | PostgreSQL |
| Frontend | React 19, TypeScript, Vite |
| Aperçu mathématique | KaTeX |
| PDF | LaTeX/MiKTeX; repli ReportLab explicite |
| Tests | pytest, Vitest, tests de workflow et contrôle visuel PDF |

### Caractéristiques d’exploitation actuelles

- Application locale Windows-first.
- Backend et frontend liés à `127.0.0.1`.
- Aucun compte utilisateur et aucune authentification.
- CORS limité au frontend local configuré.
- Fichiers PDF générés dans un répertoire contrôlé par le serveur.
- Compilation LaTeX avec `-no-shell-escape` et rejet de commandes dangereuses.
- Aucun broker, webhook, mécanisme événementiel ou traitement asynchrone distribué.

## 5. Données et responsabilités de l’application existante

L’application est actuellement propriétaire des agrégats suivants :

| Domaine | Données principales | Règle de propriété |
|---|---|---|
| Curriculum pilote | SA, séquences, instructions, allocations, problèmes de source | Lecture dans les workflows de fiche; ne pas remplacer un texte officiel par une adaptation |
| Sources | Documents, occurrences, anomalies, propositions séparées | Une proposition ne réécrit jamais la transcription source |
| Bibliothèque | Ressources, versions, blocs, variantes, rattachements aux instructions | Une version publiée/utilisée reste historiquement identifiable |
| Fiche enseignant | Identité stable, révisions, déroulement, résultats attendus | Brouillon modifiable; révision finalisée immuable |
| Support apprenant | Identité stable, révisions, blocs et variantes | Même règle de révision et d’immuabilité |
| Lien support-fiche | Révision du support, blocs sélectionnés, partie utilisée | Le lien historique doit toujours pointer vers la version exacte |
| Exécution | Séance réalisée, durée réelle, état d’exécution | Associée à une révision finalisée |
| Export | Famille, cible, révision source, statut, chemin serveur | Un export provient soit d’une fiche, soit d’un support, jamais des deux |

Les clés numériques actuelles sont des identifiants techniques locaux. Elles ne doivent pas devenir, sans décision explicite, des identifiants publics ou interservices durables.

## 6. Capacités API déjà disponibles

L’API actuelle expose notamment :

- santé et tableau de bord;
- consultation du curriculum pilote et des instructions;
- consultation des ressources;
- création, lecture, modification, finalisation, duplication et nouvelle révision des fiches;
- création, lecture, modification, finalisation et nouvelle révision des supports;
- création d’une fiche depuis une sélection de blocs d’un support finalisé;
- création et consultation des exports;
- enregistrement d’une séance réalisée et de l’utilisation d’un support;
- consultation de la progression.

La documentation interactive FastAPI est disponible localement à `/docs`. Cette API sert actuellement l’interface du MVP. Elle n’est pas encore un contrat public stabilisé : pas de version dans l’URL, pas d’authentification, pas d’idempotency key, pas de pagination généralisée, pas de webhooks, pas de politique de compatibilité ni de schéma d’erreur interservices formalisé.

## 7. Limites explicites à prendre en compte

- Périmètre chargé : mathématiques 4e, SA1 / Séquence 8 seulement.
- SQLite est la seule base réellement testée.
- Pas de concurrence multi-utilisateur validée.
- Pas d’authentification, de rôles ou de séparation entre établissements.
- Pas d’import de masse, de staging, de dry-run ou de rapport accepté/rejeté/ambigu.
- Pas de stockage objet ni d’API d’upload documentaire.
- Les fichiers sources restent hors dépôt et sont référencés par métadonnées ou chemins locaux.
- Les figures très larges restent contraintes à la largeur d’une colonne dans les supports.
- Les zones de réponse très hautes peuvent produire des espaces blancs importants.
- La validation LaTeX dans l’éditeur est syntaxique et simple; la compilation PDF demeure la validation réelle.
- L’API actuelle mélange lecture, commandes métier et besoins directs de l’interface locale.

## 8. Principes d’intégration proposés pour le futur service

Ces principes sont des **recommandations à analyser**, pas des fonctions déjà livrées.

### Frontière recommandée

- Ne pas partager directement la base de données.
- Chaque service reste propriétaire de ses données métier.
- Échanger des références de versions/révisions, pas seulement des libellés.
- Une donnée finalisée reçue par un autre service est traitée comme immuable.
- Toute correction produit une nouvelle version ou révision traçable.
- Distinguer les données officielles, transcrites, proposées, locales et de démonstration.

### Contrat MVP recommandé

Pour un premier raccordement, privilégier une API HTTP/JSON synchrone, versionnée sous `/api/v1`, plutôt qu’un bus de messages. Ajouter seulement :

1. une authentification service-à-service adaptée au mode de déploiement;
2. des identifiants externes stables ou une table de correspondance;
3. des commandes idempotentes pour éviter les doublons;
4. un schéma d’erreur stable;
5. un journal minimal des échanges;
6. des endpoints de lecture filtrés et paginés;
7. des tests de contrat entre les deux services.

Un mécanisme événementiel ne devient nécessaire que si le futur service doit être informé automatiquement d’un grand volume de finalisations ou si les deux systèmes doivent fonctionner de manière asynchrone et indépendante.

### Répartition indicative des responsabilités

| Sujet | Propriétaire recommandé | Échange minimal |
|---|---|---|
| Rédaction et finalisation des fiches/supports | Application actuelle | Révision finalisée et métadonnées métier |
| Génération des PDF pédagogiques | Application actuelle, au moins pour le MVP | URL ou identifiant d’export contrôlé |
| Domaine spécifique du nouveau service | Nouveau service | Identifiant stable et statut défini par son contrat |
| Identité des utilisateurs/établissements | À décider | Identifiant externe; ne pas utiliser les libellés comme clés |
| Référentiel curriculum partagé | À décider explicitement | Identité de version et provenance; aucune correspondance implicite |
| Suivi d’exécution/progression | Un seul propriétaire à choisir | Événement ou commande idempotente associée à une révision finalisée |

## 9. Scénarios d’interopérabilité à arbitrer

L’architecte devra identifier le scénario réel du nouveau service. Les trois familles suivantes ne demandent pas la même architecture.

### A. Le nouveau service fournit un référentiel ou une bibliothèque

Flux envisagé : nouveau service → application de fiches.

Points critiques : version du curriculum, provenance, statut de publication, mapping vers les instructions, import en staging, détection des ambiguïtés, rejet explicite et conservation du SHA-256 des fichiers ou lots sources.

### B. Le nouveau service consomme les fiches, supports ou séances

Flux envisagé : application de fiches → nouveau service.

Points critiques : ne publier que des révisions finalisées, transmettre une identité stable de révision, conserver le lien support-fiche, rendre l’envoi idempotent et définir qui possède la progression.

### C. Le nouveau service fournit une capacité technique

Exemples : stockage documentaire, génération PDF distante, authentification ou notifications.

Points critiques : confidentialité des contenus, reprise après échec, statut asynchrone éventuel, durée de conservation, intégrité du fichier et absence de mutation de l’historique métier.

## 10. Matrice de compatibilité actuelle

| Besoin d’intégration | État actuel | Verdict |
|---|---|---|
| Lecture JSON locale | Endpoints FastAPI existants | Utilisable pour prototype contrôlé |
| Commandes JSON unitaires | Endpoints de création/mise à jour existants | Utilisable localement, contrat à stabiliser |
| OpenAPI | Généré automatiquement par FastAPI | Base utile, non versionnée comme contrat public |
| Import CSV/Excel/JSONL en lot | Absent | À concevoir si requis |
| Staging/dry-run et rapport de rejet | Absent | À concevoir avant import réel |
| Webhooks/événements | Absents | À justifier avant ajout |
| Authentification/autorisation | Absentes | Obligatoire avant exposition réseau ou multi-utilisateur |
| Idempotence interservices | Absente | À ajouter pour les commandes échangées |
| Identifiants publics stables | Non définis | Décision d’architecture requise |
| PostgreSQL | Compatibilité visée, non testée en réel | Migration et tests requis |
| Partage direct de base | Non prévu | Déconseillé |

## 11. Questions auxquelles l’architecte doit répondre

1. Quelle est la responsabilité métier exacte du nouveau service ?
2. Quel système est la source d’autorité pour le curriculum, les ressources, les utilisateurs et la progression ?
3. Le flux est-il entrant, sortant ou bidirectionnel ?
4. Quelles données doivent être échangées, à quel moment et avec quelle fréquence ?
5. L’échange porte-t-il uniquement sur des révisions finalisées ou aussi sur des brouillons ?
6. Quel identifiant métier stable reliera les deux systèmes ?
7. Comment seront gérés les doublons, reprises, corrections et annulations ?
8. Faut-il une synchronisation immédiate ou une cohérence différée est-elle acceptable ?
9. Quel est le nombre attendu d’utilisateurs, d’établissements, de documents et d’échanges ?
10. Le service sera-t-il local, sur un réseau d’établissement ou hébergé sur Internet ?
11. Quelles exigences existent pour l’authentification, les rôles, l’audit, la sauvegarde et la protection des données ?
12. Faut-il migrer l’application actuelle vers PostgreSQL avant le raccordement ?

## 12. Livrables attendus de l’architecte

Pour rester MVP et directement exécutable, demander au minimum :

1. un diagramme de contexte des deux systèmes;
2. une matrice de propriété des données;
3. les séquences des deux ou trois flux prioritaires;
4. un contrat API minimal versionné avec exemples de requêtes, réponses et erreurs;
5. la stratégie d’identité, d’idempotence et de reprise;
6. les exigences de sécurité et de déploiement;
7. un plan d’évolution SQLite → PostgreSQL si nécessaire;
8. les tests de contrat et critères d’acceptation;
9. la liste des décisions différées et des risques;
10. un découpage de réalisation en petits lots indépendants.

## 13. Proposition de première tranche MVP

Sous réserve du rôle exact du nouveau service :

1. choisir un seul flux métier prioritaire;
2. figer la propriété des données concernées;
3. définir des identifiants externes stables;
4. exposer ou consommer deux à quatre opérations `/api/v1` maximum;
5. ajouter authentification, idempotence et journal d’échange;
6. écrire les tests de contrat;
7. tester sur une copie isolée de la base et des exports;
8. réaliser un pilote de bout en bout avant d’ajouter synchronisation de masse ou événements.

## 14. Repères pour examiner le dépôt

- Architecture : `docs/architecture/M02_TECHNICAL_ARCHITECTURE.md`
- Modèle physique : `docs/architecture/M02_PHYSICAL_DATA_MODEL.md`
- Décisions : `docs/DECISIONS.md`
- Limites : `docs/KNOWN_LIMITATIONS.md`
- Workflow support-first : `docs/audits/V2_SUPPORT_FIRST_WORKFLOW_AUDIT.md`
- Binding données → PDF : `docs/audits/V2_PDF_DATA_BINDING_MATRIX.md`
- API : `backend/app/main.py` et documentation locale `/docs`
- Schémas de commande : `backend/app/schemas.py`
- Modèle : `backend/app/models.py`
- Guide de test V2.1 : `README_TESTER_V2_1.md`

## 15. Commandes de prise en main

Depuis la racine du dépôt, dans PowerShell :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start-dev.ps1
```

Ouvrir ensuite :

- interface : `http://127.0.0.1:5173/`
- documentation API : `http://127.0.0.1:8000/docs`

Pour lancer la vérification automatisée :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\test-all.ps1
```

Pour arrêter l’application :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\stop-dev.ps1
```
