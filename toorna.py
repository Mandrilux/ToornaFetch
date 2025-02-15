import requests
import sys
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time
import redis

load_dotenv()

client = redis.StrictRedis(host='redis', port=6379, db=0)

ids = os.getenv("TOORNAMENTIDS")
ids = ids.split(',')
print("Démarrage du bot")
print(ids)
print(f"{len(ids)} tournois à scrapper")

# URL de la page web

while(1):
    for event in ids:
        url = "https://play.toornament.com/fr/tournaments/" + event + "/"
        response = requests.get(url)
        # Vérifier si la requête a réussi
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")

            # Trouver tous les éléments ayant la classe "size"
            size_elements = soup.find(class_="size")
            children = size_elements.find_all("div")

            first_child = children[0] if len(children) > 1 else None
            second_child = children[1] if len(children) > 1 else None


            discipline = soup.find(class_="discipline")
            text = discipline.find('a', class_='highlighted').get_text().lower()


            # Chercher les enfants avec la classe "current" dans chaque "size"
            if first_child:
                currentValue = first_child.text
            if first_child:
                currentMax = second_child.text

            print("{}: {} / {}".format(text, currentValue, currentMax))



            if client.exists(event):
                #print(f"comparaison entre '{client.get(event).decode('utf-8')}' et {currentValue}")
                if client.get(event).decode('utf-8')  != currentValue:
                    client.set(event, currentValue)
                    print(f"La clé '{event}' existe dans redis et la ouvelle valeur est: {currentValue}")
                else:
                    print(f"La clé '{event}' existe et la valeur n'as pas été modifié: {currentValue}")
            else:
                # Si la clé n'existe pas, l'ajouter avec la valeur
                client.set(event, currentValue)
                print(f"La clé '{event}' n'existe pas. Elle a été ajoutée avec la valeur: {currentValue}")


        else:
            print("Erreur lors de la récupération de la page:", response.status_code)
    print("En attente du prochain scrapping")
    time.sleep(300)
