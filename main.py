from dotenv import load_dotenv
import os
import mysql.connector
import re
import bcrypt

load_dotenv() #chargement du fichier .env

""" recupération des variables d'environnement """
host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
database = os.getenv("DB_NAME")
port = int(os.getenv("DB_PORT"))

try:
    connexion = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database,
    port= port
    )
    curseur = connexion.cursor(dictionary=True)
    print("Connexion réussie à la base de données MySQL")
except mysql.connector.Error as e:
    print(f"Erreur de connexion : {e}")


def saisir_utilisateur():
    """fonction générique pour demander les infos utilisateur,  
        Collecte et valide prénom, nom, email et mot de passe."""
    while True:
        prenom = input("Entrez votre prénom : ").strip().capitalize()
        if prenom.replace(" ", "").isalpha():
            break
        print("Veuillez entrer un prénom valide")

    while True:
        nom = input("Entrez votre nom : ").strip().capitalize()
        if nom.replace(" ", "").isalpha():
            break
        print("Veuillez entrer un nom valide")

    while True:
        email = input("Entrez votre email : ").strip()
        if re.match(r"[^@]+@[^@]+\.[^@]+", email):
            break
        print("Format d'email invalide")

    while True:
        mot_de_passe = input("Mot de passe : ").strip()
        if len(mot_de_passe) >= 6:
            break
        print("Le mot de passe doit contenir au minimum 6 caractères")

    return prenom, nom, email, mot_de_passe


#gestion de l'inscription
def inscription(curseur, connexion):
    try:
        prenom, nom, email, mot_de_passe = saisir_utilisateur()

        # Vérification si email existe
        curseur.execute("SELECT * FROM users WHERE email = %s", (email,))
        if curseur.fetchone():
            print("Cet email est déjà utilisé")
            return

        # Hachage du mot de passe
        hash_password = bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt())

        # Insertion utilisateur
        curseur.execute(
            "INSERT INTO users(prenom, nom, email, password, role) VALUES (%s, %s, %s, %s, %s)",
            (prenom, nom, email, hash_password.decode('utf-8'), "user")
        )
        connexion.commit()
        print("Compte créé avec succès!")

    except mysql.connector.Error as e:
        print(f"Erreur lors de l'inscription : {e}")

#création d'un admin
def creer_admin(curseur, connexion, current_user):
    if current_user['role'] != 'admin':
        print("Accès refusé.")
        return

    print("\n=== CRÉATION D'UN ADMINISTRATEUR ===")
    prenom, nom, email, mot_de_passe = saisir_utilisateur()

    curseur.execute("SELECT * FROM users WHERE email = %s", (email,))
    if curseur.fetchone():
        print("Cet email est déjà utilisé")
        return

    hash_password = bcrypt.hashpw(mot_de_passe.encode('utf-8'), bcrypt.gensalt())

    curseur.execute(
        "INSERT INTO users(prenom, nom, email, password, role) VALUES (%s, %s, %s, %s, %s)",
        (prenom, nom, email, hash_password.decode('utf-8'), "admin")
    )
    connexion.commit()
    print("Nouvel administrateur créé avec succès !")


#gestion de la connexion
def login(curseur, connexion):
    try:
        email = input ("Email : ").strip()
        mot_de_passe = input("Mot de passe : ").strip()

        query = "SELECT * FROM users WHERE email = %s"
        curseur.execute(query, (email,))
        user = curseur.fetchone()

        if not user:
            print("Email inconnue")
            return None
        
        mot_de_passe_bytes = mot_de_passe.encode('utf-8')
        hash_bytes = user['password'].encode('utf-8')

        if bcrypt.checkpw(mot_de_passe_bytes, hash_bytes):
            print(f"Connexion réussi! Bienvenue {user['prenom']} {user['nom']}")
            return user
        else:
            print("Mot de passe incorrect")
            return None
        
    except mysql.connector.Error as e:
        print(f"Erreur lors de la connexion : {e}")

#fonctionalité pour la création d'un ticket
def creer_ticket(curseur, connexion, current_user):
    print("\n=== CRÉER UN TICKET ===")
    if current_user is None:
        print("Vous devez être connecté pour créer un ticket")
        return
    
    # Saisie du titre
    while True:
        titre = input("Titre du ticket : ").strip()
        if titre:
            break
        print("Le titre ne peut pas être vide.")

    # Saisie de la description
    while True:
        description = input("Description du problème : ").strip()
        if description:
            break
        print("La description ne peut pas être vide.")

    # Saisie du niveau d'urgence
    urgences = ['faible', 'moyenne', 'haute']
    while True:
        print("1. Faible")
        print("2. Moyenne")
        print("3. Haute")
        choix = input("Choisissez le niveau d'urgence : ").strip()
        if choix in ['1', '2', '3']:
            urgence = urgences[int(choix) - 1]
            break
        else:
            print("Choix invalide")

    # Insertion en base
    try:
        query_insert = """
            INSERT INTO tickets (titre, description, urgence, user_id)
            VALUES (%s, %s, %s, %s)
        """
        curseur.execute(query_insert, (titre, description, urgence, current_user['id']))
        connexion.commit()
        print("Ticket créé avec succès !")
    except mysql.connector.Error as e:
        print(f"Erreur lors de la création du ticket : {e}")

#fonctionalité pour voir les tickets
def voir_tickets(curseur, current_user):
    if current_user is None:
        print("Vous devez être connecté pour voir vos tickets")
        return

    try:
        if current_user['role'] == 'admin':
            # Admin voit tous les tickets avec l'auteur
            query = """
                SELECT t.id, t.titre, t.description, t.urgence, t.statut, u.prenom, u.nom AS auteur
                FROM tickets t
                JOIN users u ON t.user_id = u.id
                ORDER BY t.id
            """
            curseur.execute(query)
        else:
            # Utilisateur normal voit seulement ses tickets
            query = """
                SELECT t.id, t.titre, t.description, t.urgence, t.statut, u.prenom, u.nom AS auteur
                FROM tickets t
                JOIN users u ON t.user_id = u.id
                WHERE t.user_id = %s
                ORDER BY t.id
            """
            curseur.execute(query, (current_user['id'],))

        tickets = curseur.fetchall()

        if not tickets:
            print("Aucun ticket trouvé.")
            return

        print("\n=== TICKETS ===")
        for t in tickets:
            if current_user['role'] == 'admin':
                print(f"\nID: {t['id']}, Titre: {t['titre']}, Auteur: {t['prenom']} {t['auteur']}")
            else:
                print(f"\nID: {t['id']}, Titre: {t['titre']}\n"
                      f"Description: {t['description']}\n"
                      f"Urgence: {t['urgence']}, Statut: {t['statut']}\n")

    except mysql.connector.Error as e:
        print(f"Erreur lors de la récupération des tickets : {e}")


#fonctionalité pour la modification du statut d'un ticket
def modifier_statut_ticket(curseur, connexion, current_user):
    if current_user['role'] != 'admin':
        print("Accès refusé.")
        return

    print("\n=== MODIFICATION DU STATUT D'UN TICKET ===")

    # Afficher tous les tickets
    query = """
        SELECT t.id, t.titre, t.statut, u.prenom, u.nom AS auteur
        FROM tickets t
        JOIN users u ON t.user_id = u.id
        ORDER BY t.id
    """
    curseur.execute(query)
    tickets = curseur.fetchall()

    if not tickets:
        print("Aucun ticket disponible.")
        return

    for ticket in tickets:
        print(f"ID: {ticket['id']} | Titre: {ticket['titre']} | "
              f"Statut: {ticket['statut']} | Auteur: {ticket['prenom']} {ticket['auteur']}")

    # Choisir le ticket
    try:
        ticket_id = int(input("Entrez l'ID du ticket à modifier : "))
    except ValueError:
        print("ID invalide.")
        return

    # Vérifier que le ticket existe
    curseur.execute("SELECT * FROM tickets WHERE id = %s", (ticket_id,))
    ticket = curseur.fetchone()

    if not ticket:
        print("Ticket introuvable.")
        return

    # Choisir le nouveau statut
    statuts = ["En attente", "En cours", "Résolu"]
    print("Nouveau statut possible :")
    for i, statut in enumerate(statuts, 1):
        print(f"{i}. {statut}")

    choix = input("Choisissez un statut : ")

    if choix not in ["1", "2", "3"]:
        print("Choix invalide.")
        return

    nouveau_statut = statuts[int(choix) - 1]

    # Mise à jour
    curseur.execute(
        "UPDATE tickets SET statut = %s WHERE id = %s",
        (nouveau_statut, ticket_id)
    )
    connexion.commit()
    print("Statut mis à jour avec succès !")

current_user = None

#menu pricipal
def menu_principal(curseur, connexion):
    current_user = None

    while True:
        if current_user is None:
            print("\n=== Helpdesk Menu ===")
            print("1. Se connecter")
            print("2. S'inscrire")
            print("3. Quitter")

            choix = input("Veuillez choisir une option : ")

            if choix == "1":
                current_user = login(curseur, connexion)
            elif choix == "2":
                inscription(curseur, connexion)
            elif choix == "3":
                print("Au revoir!")
                break
            else:
                print("Option invalide")

        else:
            # Menu pour utilisateur connecté
            print(f"\nConnecté en tant que {current_user['prenom']} | {current_user['role']}")

            if current_user['role'] == 'user':
                print("1. Créer un ticket")
                print("2. Voir mes tickets")
                print("3. Se déconnecter")

                choix = input("Veuillez choisir une option : ")

                if choix == "1":
                    creer_ticket(curseur, connexion, current_user)
                elif choix == "2":
                    voir_tickets(curseur, current_user)
                elif choix == "3":
                    print("Déconnecté.")
                    current_user = None
                else:
                    print("Option invalide")

            elif current_user['role'] == 'admin':
                print("1. Voir tous les tickets")
                print("2. Créer un admin")
                print("3. Modifier le statut d'un ticket")
                print("4. Se déconnecter")

                choix = input("Veuillez choisir une option : ")

                if choix == "1":
                    # Même fonction pour admin, elle affichera tous les tickets
                    voir_tickets(curseur, current_user)
                elif choix == "2":
                    creer_admin(curseur, connexion, current_user)
                elif choix == "3":
                    modifier_statut_ticket(curseur, connexion, current_user)
                elif choix == "4":
                    print("Déconnecté.")
                    current_user = None
                else:
                    print("Option invalide")
        
menu_principal(curseur, connexion)