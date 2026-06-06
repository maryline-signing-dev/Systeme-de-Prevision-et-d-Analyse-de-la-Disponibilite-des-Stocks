# Système de Prévision et d'analyse de la disponibilité des stocks

## Présentation

Ce projet a pour objectif de développer une application permettant de suivre et d'anticiper l'évolution des stocks d'un entrepôt à partir des flux connus (réceptions et livraisons).

Contrairement à une simple gestion de stock qui affiche uniquement le stock actuel, cette solution permet de répondre à des questions telles que :

- Quelle quantité d'un produit sera disponible à une date donnée ?
- Quelle quantité était disponible à une date passée ?
- À quelle date un produit risque-t-il d'être en rupture ?
- Comment les flux planifiés influencent-ils l'évolution du stock ?

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
- Consultation de l'historique des mouvements
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

- HTML
- CSS
- Bootstrap
- JavaScript

### Backend

- Python
- Flask

### Base de données

- MySQL

### Outils

- Git
- GitHub
- Visual Studio Code
- Postman
- Figma

---

## Comment démarrer ?

### Prérequis

- Python 3.10 ou supérieur
- MySQL
- Git

### Cloner le projet

```bash
git clone <url-du-depot>
```

### Accéder au dossier

```bash
cd nom-du-projet
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

### Installer les dépendances

```bash
pip install -r requirements.txt
```

### Lancer l'application

```bash
python app.py
```
