## Système de Suivi d'Incidents (Helpdesk Console)

Application console développée en Python permettant la gestion sécurisée de tickets d'assistance technique avec authentification robuste et gestion des rôles.

## Fonctionnalités

- Inscription avec mot de passe haché avec bcrypt
- Connexion sécurisée
- Gestion de session
- Création de tickets 
- Suivi du statut 
- Isolation des utilisateurs: un user ne voit que ses tickets.
- Déconnexion sécurisée
- Rôle administrateur:
    - Voir tous les tickets
    - Modifier le statut d’un ticket
    - Créer un autre administrateur

## Sécurité

- Mots de passe hachés avec bcrypt 
- Requêtes SQL paramétrées 
- Gestion stricte des rôles: user / admin
- Vérification des permissions avant chaque action sensible
- Isolation des données par user_id

## Technologies

- Python 3
- MySQL
- mysql-connector-python
- bcrypt
- python-dotenv
- Git (versioning)

## Base de données

### Table users
- id (PK)
- nom
- email (UNIQUE)
- password
- role (user / admin)

### Table tickets
- id (PK)
- titre
- description
- urgence (ENUM)
- statut (ENUM)
- user_id (FK = users.id)

## Installation

1. Cloner le repository
2. Installer les dépendances :
   pip install -r requirements.txt

3. Configurer le fichier .env
4. Exécuter le script SQL helpdesk_support.sql
5. Lancer l'application :
   python app.py


