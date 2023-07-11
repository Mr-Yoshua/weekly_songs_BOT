import random
import json
import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot
from mongodb import connect_to_mongo
from datetime import datetime
import schedule
import time
from cron_job import change_priority_job
import logging
class Cancion:
    def __init__(self, nombre, clasificacion):
        self.nombre = nombre
        self.clasificacion = clasificacion

def connect_bd():
    URL_DB = os.getenv("URL_DB") 
    db_manager = connect_to_mongo(URL_DB)
    client = db_manager.client
    try:
        client.admin.command("ping")
        logging.info("Conexión exitosa a la base de datos")
    except Exception as e:
        logging.error("Error al conectar a la base de datos")
        logging.error(e)
    return db_manager

def load_songs(list_name):
    songs = []
    with open(list_name, "r", encoding="utf-8") as file:
        data = json.load(file)
        for song in data:
            song = Cancion(song["nombre"], song["clasificacion"])
            songs.append(song)
    return songs

def show_list(random_daily_songs):
    logging.info(f"--- Canciones para hoy elegidas al azar: ---")
    for classification, songs in random_daily_songs.items():
        print(f"- {classification.upper()} -")
        for song in songs:
            print(f"Nombre: {song['name']} - Clasificación: {song['clasification']}")
            logging.info(f"Nombre: {song['name']} - Clasificación: {song['clasification']}")
        print()


def generate_list(db_manager):
    # necesito dos canciones de cada clasificacion que tengan prioridad alta
    random_daily_songs = {}
    clasification_type = ["himnario", "carpeta", "rapida", "adoracion"]
    for clasification in clasification_type:
        selected_songs = db_manager.get_song_by_priority("high")
        selected_songs = [song for song in selected_songs if song['clasification'] == clasification]
        random_songs = random.sample(selected_songs, 2)  # Selecciona dos canciones aleatorias sin repetición
        random_daily_songs[clasification] = random_songs

    return random_daily_songs

  
   
def populate_db(db_manager,songs):
    for song in songs:
        db_manager.insert_song({"name": song.nombre, "clasification": song.clasificacion, "priority": "high", "last_update": datetime.now()})
    logging.info("Se han insertado las canciones en la base de datos")

def run_cron_priority(db_manager):
    schedule.every().month.do(change_priority_job, db_manager)
    while True:
        schedule.run_pending()
        time.sleep(1)

async def send_by_telegram(random_daily_songs, bot_token, chat_id):
    bot = Bot(token=bot_token)
    message = "Listado aleatorio de canciones:\n\n"
    for classification, songs in random_daily_songs.items():
        message += f"- {classification.upper()} -\n"
        for song in songs:
            message += f"Nombre: {song['name']}\n"
        message += "\n"
    await bot.send_message(chat_id=chat_id, text=message)
    logging.info("Mensaje enviado por Telegram")

async def main():
    load_dotenv()
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")
    db_instance = connect_bd()
    list_name = "song-list.json"
    songs = load_songs(list_name)
    populate_db(db_instance, songs) if not db_instance.collection_has_data() else None
    random_daily_songs = generate_list(db_instance)
    show_list(random_daily_songs)
    await send_by_telegram(random_daily_songs, BOT_TOKEN, CHAT_ID)

if __name__ == "__main__":
    asyncio.run(main())