# Gestion Documentaire

Ce projet est une application web de gestion documentaire développée avec Django. Elle permet de gérer des documents, agents, rôles, permissions, structures, délégations, utilisateurs, catégories de documents, et inclut un système de versionnage des documents.

## Fonctionnalités principales
- Gestion des documents (ajout, modification, suppression, versionnage)
- Gestion des agents, rôles, permissions, structures, délégations, utilisateurs
- Historique et versionnage des documents (chaque version est conservée)
- Authentification et gestion des droits
- Interface utilisateur moderne et ergonomique

## Prérequis
- Python 3.8+
- pip
- [Git](https://git-scm.com/)

## Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com/llodia221/gestion-documentaire.git
   cd gestion-documentaire
   ```

2. **Créer un environnement virtuel**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Sur Windows : venv\Scripts\activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Appliquer les migrations**
   ```bash
   python manage.py migrate
   ```

5. **Créer un superutilisateur**
   ```bash
   python manage.py createsuperuser
   ```

6. **Lancer le serveur de développement**
   ```bash
   python manage.py runserver
   ```

7. **Accéder à l'application**
   - Ouvrez votre navigateur à l'adresse : [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Configuration des fichiers médias (uploads)
- Les fichiers uploadés (documents, CV, etc.) sont stockés dans le dossier `media/` à la racine du projet.
- En développement, Django sert automatiquement ces fichiers.

## Structure du projet
```
gestion-documentaire/
├── gestion_doc/
│   ├── document_management/   # Application principale
│   ├── gestion_doc/           # Configuration Django
│   ├── manage.py
│   └── ...
├── media/                     # Fichiers uploadés
├── static/                    # Fichiers statiques (CSS, JS)
├── requirements.txt
└── README.md
└── requirements.txt
```

## Déploiement
Pour un déploiement en production, il est nécessaire de :
- Servir les fichiers médias via un serveur web (Nginx, Apache...)
- Désactiver le mode DEBUG
- Configurer une base de données de production
- Sécuriser les clés et accès

## Contribution et suggestion
Les contributions et les suggestions sont les bienvenues !


## Licence
Ce projet est sous licence MIT.

---

**Contact** : Pour toute question, contactez l'auteur du dépôt. 