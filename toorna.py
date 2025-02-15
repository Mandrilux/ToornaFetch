import requests
import sys
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

ids = os.getenv("TOORNAMENTIDS")
ids = ids.split(',')
print("Démarrage du bot")
print(ids)
print(f"{len(ids)} tournois à scrapper")

# URL de la page web

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
    else:
        print("Erreur lors de la récupération de la page:", response.status_code)