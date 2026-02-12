from dotenv import load_dotenv
import os
import mysql.connector

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
    cursor = connexion.cursor(dictionary=True)
    print("Connexion réussie à la base de données MySQL")
except mysql.connector.Error as e:
    print(f"Erreur de connexion : {e}")

#menu pricipal
def menu_principal():
    while True:
        print("Menu Principal")
        print("1. Se connecter")
        print("2. S'inscrire")
        print("3. Quitter")

        choix = input("Veuillez choisir une option : ")
        if choix == "1":
            print("se connecter")
        elif choix == "2":
            print("s'inscrire")
        elif choix == "3":
            print("Au revoir!")
            exit()
        else:
            print("Option invalide. Veuillez réessayer.")
menu_principal()