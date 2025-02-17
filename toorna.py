import requests
import sys
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import time
import redis
import discord
import asyncio
from datetime import datetime
import pytz


load_dotenv()

client = redis.StrictRedis(host='redis', port=6379, db=0)
intents = discord.Intents.default()  # Active les intentions par défaut

# Si vous avez besoin de certaines intentions supplémentaires, vous pouvez les activer
# Par exemple, pour recevoir des informations sur les membres du serveur :
intents.members = True

# Créer un client Discord en passant l'objet intents
client_discord = discord.Client(intents=intents)


ids = os.getenv("TOORNAMENTIDS")
chanelId =  os.getenv("CHANNELID")
token = os.getenv("TOKENDISCORD")
france_tz = pytz.timezone("Europe/Paris")

ids = ids.split(',')
print("Démarrage du bot")
print(ids)
print(f"{len(ids)} tournois à scrapper")

async def envoyer_message(message):
    # Attendez que le bot soit prêt
    await client_discord.wait_until_ready()
    channel = client_discord.get_channel(int(chanelId))
    if channel:
        await channel.send(message)
def vérifier_et_envoyer(event, currentValue, nameEvent):
    if client.exists(event):
        if client.get(event).decode('utf-8') != currentValue:
            client.set(event, currentValue)
            message = f"Il y a désormais {currentValue} inscrits pour le tournoi {nameEvent.capitalize()}"
            print(f"La clé '{event}' existe dans Redis et la nouvelle valeur est: {currentValue}")
            return message
        else:
            print(f"La clé '{event}' existe et la valeur n'a pas été modifiée: {currentValue}")
    else:
        # Si la clé n'existe pas, l'ajouter avec la valeur
        client.set(event, currentValue)
        message = f"Il y a {currentValue} inscrits pour le tournoi {nameEvent.capitalize()}"
        print(f"La clé '{event}' n'existe pas. Elle a été ajoutée avec la valeur: {currentValue}")
        return message
    return None


async def scraper_et_envoyer_messages():
    while True:
        # Obtenir la date et l'heure actuelles en France
        now_in_france = datetime.now(france_tz)
        # Afficher la date et l'heure françaises
        print("date et heure :", now_in_france.strftime("%Y-%m-%d %H:%M:%S"))
        print("--------------------------------------------")
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


                message = vérifier_et_envoyer(event, currentValue, text)
                if message:
                    await envoyer_message(message)

            else:
                print("Erreur lors de la récupération de la page:", response.status_code)
        print("--------------------------------------------")
        print("En attente du prochain scrapping")
        await asyncio.sleep(300)
@client_discord.event

async def on_ready():
    print(f'Bot connecté en tant que {client_discord.user}')

    # Lancer la tâche de scraping après que le bot soit prêt
    await scraper_et_envoyer_messages()

# Lancer le bot Discord
client_discord.run(token)