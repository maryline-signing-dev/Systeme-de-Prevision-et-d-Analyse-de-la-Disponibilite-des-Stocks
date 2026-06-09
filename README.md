# Système de Prévision et d'analyse de la disponibilité des stocks

## Présentation

Ce projet a pour objectif de développer une application permettant de suivre et d'anticiper l'évolution des stocks d'un entrepôt à partir des flux connus (réceptions et livraisons).

Contrairement à une simple gestion de stock qui affiche uniquement le stock actuel, cette solution permet de répondre à des questions telles que :

- Quelle quantité d'un produit sera disponible à une date donnée ?
- Quelle quantité était disponible à une date passée ?
- À quelle date un produit risque-t-il d'être en rupture ?
- Comment les flux planifiés influencent-ils l'évolution du stock ?

Le système repose sur un moteur de **Projection Chronologique
Déterministe** : plutôt que d'estimer ou d'approximer, il calcule
exactement le stock à partir de l'ensemble des flux connus, dans leur
ordre chronologique strict, en appliquant des règles métier explicites.

Ce choix exclut volontairement le Machine Learning pour le MVP :
les flux étant connus, datés et statués, un calcul exact est supérieur
à toute estimation probabiliste

Le projet met l'accent sur la modélisation, l'analyse métier et la conception logicielle.

---

## Pourquoi ce projet ?

Dans de nombreuses PME, la gestion des stocks est encore réalisée à l'aide de fichiers Excel ou de méthodes manuelles.

Ces approches rendent difficile :

- l'anticipation des ruptures ;
- la planification des approvisionnements ;
- le suivi de l'évolution des stocks dans le temps.

L'objectif de cette application est donc d'apporter une solution simple permettant de mieux visualiser et prévoir l'état futur des stocks.

---

## Fonctionnalités prévues

### Version actuelle (MVP)

- Authentification administrateur
- Gestion des produits
- Gestion des flux (réceptions et livraisons)
- Calcul de la disponibilité d'un produit à une date donnée
- Reconstitution de la disponibilité passée
- Détection des ruptures de stock
- Affichage des résultats sous forme de tableau

### Évolutions futures

- Gestion de plusieurs utilisateurs
- Gestion des rayons et catégories
- Tableaux de bord et statistiques
- Alertes automatiques
- Prévision de la demande
- Intégration de modèles de Machine Learning

---

## Technologies utilisées

### Frontend

- HTML 5
- CSS
- Bootstrap
- JavaScript
- Chart.js pour visualisation

### Backend

- Python 3.0 
- Flask 2.x
- bcrypt pour sécurité mots de passe

### Authentification

- Flash-JWT-Extended

### Base de données

- MySQL

---

## Comment démarrer ?

### Prérequis

- Python 3.10 ou supérieur
- MySQL 8.x en cours d'exécution
- Git

### Cloner le projet

```bash
git clone <https://github.com/maryline-signing-dev/Systeme-de-Prevision-et-d-Analyse-de-la-Disponibilite-des-Stocks>
```

### Accéder au dossier

```bash
cd defi-tecnhique-GINUTECH
```

### Créer un environnement virtuel

```bash
python -m venv venv
```

### Activer l'environnement

Sous Windows :

```bash
venv\Scripts\activate
```
Sous Linux :

```bash
source venv/bin/activate
```

### Installer les dépendances

```bash
pip install -r requirements.txt
```

### Créer la base de données et les tables

```bash
mysql -u root -p < backend/migrations/create_table.sql
```
ou
```bash
"chemin d'accès vers mysql.exe" -u root -p < backendmigrations/create_table.sql
```

### 6. Insérer le jeu de données de démonstration

```bash
mysql -u root -p < backend/migrations/seed_data.sql
```
ou
```bash
"chemin d'accès vers mysql.exe" -u root -p < backendmigrations/seed_data.sql
```

### 7. Démarrer le serveur

```bash
cd backend
flask --app run.py run --debug
```

### 8. Ouvrir l'application
http://127.0.0.1:5000/

---

## Identifiants de Démonstration

| Champ | Valeur |
|---|---|
| Email | adminstock@gmail.com |
| Mot de passe | admin123 |

---

## Jeu de Données de Démonstration

### Accès direct en base

Pour consulter le jeu de données directement dans MySQL :

```sql
-- Se connecter
mysql -u root -p ou "chemin d'accès vers mysql.exe" -u root -p

-- Sélectionner la base
USE stock_prevision;

-- Voir tous les produits
SELECT id_produit, nom_produit, stock_initial,
       date_initialisation, unite, seuil_alerte
FROM produit;

-- Voir tous les flux avec leur statut
SELECT f.id_flux, p.nom_produit, f.type_flux,
       f.nature_flux, f.statut_flux,
       f.quantite, f.date_flux
FROM flux f
JOIN produit p ON f.id_produit = p.id_produit
ORDER BY p.id_produit, f.date_flux;

-- Voir les flux futurs planifiés
SELECT p.nom_produit, f.type_flux, f.nature_flux,
       f.quantite, f.date_flux, f.statut_flux
FROM flux f
JOIN produit p ON f.id_produit = p.id_produit
WHERE f.date_flux > CURDATE()
ORDER BY f.date_flux;
```

### Contenu du jeu de données

Le jeu de données contient **5 produits** et **34 flux**,
construits pour couvrir tous les scénarios métier du système :

| Produit | Scénario | Ce qu'il permet de tester |
|---|---|---|
| Ciment CEM II 42.5 | Rupture prévue dans ~20 jours | Détection de rupture future, flux planifiés |
| Carrelage 60x60 | Stock largement suffisant | Absence de rupture sur 90 jours |
| Fer à béton 10mm | Rupture passée au 2026-04-01 | 
Reconstitution historique du stock |
| Peinture Blanche 10L | Stock sous le seuil d'alerte | Alerte seuil sans rupture |
| Câble électrique 2.5 | Flux simultanés même date | Règle RG-03 (entrées avant sorties) |

---

## Structuration des Données — Justification des Choix

### Principe central : le stock n'est jamais stocké

La décision architecturale la plus importante est de ne **pas** conserver de colonne `stock_disponible` dans la table `produit`.
Le stock est toujours **calculé dynamiquement** à partir des flux.

Ce choix garantit la cohérence des données : il est impossible qu'un stock affiché soit désynchronisé par rapport aux mouvements
enregistrés. Toute modification d'un flux se répercute automatiquement sur tous les calculs sans aucune mise à jour econdaire.

### Une seule table FLUX (pas LIVRAISON + RECEPTION)

Tous les mouvements de stock sont stockés dans une table `flux` unique, avec un discriminant `type_flux` (ENTRANT ou SORTANT)
et un champ `nature_flux` (RECEPTION, LIVRAISON, PERTE, etc.).

Cette conception unifie l'algorithme de calcul : une seule requête SQL suffit pour récupérer l'ensemble des mouvements d'un produit, triés chronologiquement, sans UNION. L'ajout d'un nouveau type de mouvement ne nécessite pas de nouvelle table, seulement une nouvelle valeur dans `nature_flux`.

### Trois statuts de flux : PLANIFIE, EN_COURS, REALISE

Chaque flux porte un statut qui détermine son inclusion dans
les calculs :

- `REALISE` : intégré dans le calcul du stock passé et courant
- `EN_COURS` : intégré dans le stock courant
- `PLANIFIE` : intégré uniquement dans les projections futures

Cette distinction permet au même moteur de répondre aux deux questions fondamentales du système — "quel était le stock au
15 mars ?" et "quel sera le stock au 20 août ?" — en changeant simplement le filtre sur le statut.

### Gestion des flux simultanés : date + ordre_execution

Deux flux à la même date sont ordonnés par :
1. `type_flux` : les ENTRANT avant les SORTANT 
2. `ordre_execution` : numéro d'ordre explicite en cas d'égalité

Cette règle évite les ruptures artificielles : une réception et une livraison prévues le même jour sont traitées dans le bon ordre logique (on reçoit avant d'expédier), ce qui maximise la disponibilité et reflète la réalité opérationnelle.

### Date unique au format DATE (pas JOUR/MOIS/ANNÉE séparés)

Les dates sont stockées en type natif SQL `DATE` pour permettre les requêtes temporelles directes (`BETWEEN`, `>=`, tri),les index efficaces, et la compatibilité avec les calculs Python `datetime.date`. Les champs séparés auraient rendu chaque comparaison de date impossible sans reconstruction.

### Stock initial daté

Chaque produit possède un `stock_initial` associé à une `date_initialisation`. Cela permet de démarrer le calcul depuis n'importe quelle date de référence sans avoir à conserver l'historique complet depuis la création de l'entrepôt. C'est le point d'ancrage de toute la projection chronologique.

## Lancer les Tests

```bash
cd backend
python -m pytest tests/test_fonctionnel.py -v
```

22 tests couvrant les 5 scénarios métier :
- Rupture future détectée
- Reconstitution historique exacte
- Absence de rupture confirmée
- Alerte seuil sans rupture
- Règle RG-03 sur flux simultanés

---