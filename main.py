from dotenv import load_dotenv
import os
import mysql.connector
import re
import bcrypt

load_dotenv() #chargement du fichier .env

#recupération des variables d'environnement
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

#gestion de l'inscription
def inscription(curseur, connexion):
    try:
        while True:
            try:
                prenom = input("Entrez votre prénom : ").strip().capitalize()
                if prenom.replace(" ", "").isalpha():
                    break
                print("veuillez entrer un prénom valide")
            except ValueError:
                print("Le prénom doit contenir uniquement des lettres")
        while True:
            try:
                nom = input("Entrez votre nom : ").strip().capitalize()
                if nom.isalpha():
                    break
                print("veuillez entrer un nom valide")
            except ValueError:
                print("Le nom doit contenir uniquement des lettres")

        while True:
            email = input("Email : ").strip()
            if re.match(r"[^@]+@[^@]+\.[^@]+", email):
                break
            print("Format d'email invalide.")

        while True:
            mot_de_passe = input("Mot de passe : ").strip()
            if len(mot_de_passe) < 6:
                print("Le Mot de passe doit contenir au minimum 6 caractères")
                continue
            break
        query_check = "SELECT * FROM users WHERE email = %s"
        curseur.execute(query_check, (email,))
        users = curseur.fetchall()
        if users:
            print("Cet email est déjà utilisé")
            return
        mot_de_passe_bytes = mot_de_passe.encode('utf-8')
        hash_password = bcrypt.hashpw(mot_de_passe_bytes, bcrypt.gensalt())
        query_insert = "INSERT INTO users(prenom, nom, email, password) VALUES (%s, %s, %s, %s)"
        curseur.execute(query_insert, (prenom, nom, email, hash_password.decode('utf-8')))
        connexion.commit()
        print("Compte créé avec succès!")

    except mysql.connector.Error as e:
        print(f"Erreur lors de l'inscription : {e}")

#gestion de la connexion
def login(curseur, connexion):
    try:
        email = input ("Email : ").strip()
        mot_de_passe = input("Mot de passe : ").strip()
        query = "SELECT * FROM users WHERE email = %s"
        curseur.execute(query, (email,))
        user = curseur.fetchone()
        if not user:
            print("Email inconnue.")
            return None
        
        mot_de_passe_bytes = mot_de_passe.encode('utf-8')
        hash_bytes = user['password'].encode('utf-8')

        if bcrypt.checkpw(mot_de_passe_bytes, hash_bytes):
            print(f"Connexion réussi! Bienvenue {user['prenom']} {user['nom']}")
            return user
        else:
            print("Mot de passe incorrect.")
            return None
    except mysql.connector.Error as e:
        print(f"Erreur lors de la connexion : {e}")



#menu pricipal
def menu_principal(curseur, connexion):

    while True:
        print("\n=== Helpdesk Menu ===")
        print("1. Se connecter")
        print("2. S'inscrire")
        print("3. Quitter")

        choix = input("Veuillez choisir une option : ")
        if choix == "1":
            login(curseur, connexion)
        elif choix == "2":
            inscription(curseur, connexion)
        elif choix == "3":
            print("Au revoir!")
            exit()
        else:
            print("Option invalide. Veuillez réessayer.")
menu_principal(curseur, connexion)