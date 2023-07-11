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
from telegram.ext import CommandHandler, Updater
from commands_helper import handle_add_song_command, handle_search_song
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
        print("Conexión exitosa a la base de datos")
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


import random

def generate_list(db_manager):
    random_daily_songs = {}
    clasification_type = ["himnario", "carpeta", "rapida", "adoracion"]
    for clasification in clasification_type:
        selected_songs = db_manager.get_song_by_priority("high")
        selected_songs = list(selected_songs)

        songs_with_classification = [song for song in selected_songs if song.get('clasification') == clasification]
        random_songs = random.sample(songs_with_classification, 2) if len(songs_with_classification) >= 2 else songs_with_classification
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
    URL_DB = os.getenv("URL_DB")
    db_instance = connect_bd()
    list_name = "song-list.json"
    songs = load_songs(list_name)
    populate_db(db_instance, songs) if not db_instance.collection_has_data() else None
    random_daily_songs = generate_list(db_instance)
    show_list(random_daily_songs)
    # await send_by_telegram(random_daily_songs, BOT_TOKEN, CHAT_ID)

    # Crear instancia del bot
    bot = Bot(token=BOT_TOKEN)

    # Crear instancia del updater y pasar el bot como argumento
    updater = Updater(bot=bot, use_context=True)

    # Obtener el dispatcher del updater
    dispatcher = updater.dispatcher

    # Agregar los handlers de los comandos
    add_song_handler = CommandHandler('addsong', handle_add_song_command)
    search_song_handler = CommandHandler('searchsong', handle_search_song)
    dispatcher.add_handler(add_song_handler)
    dispatcher.add_handler(search_song_handler)

    # Iniciar el polling del updater
    updater.start_polling()

    # Mantener el programa en ejecución
    updater.idle()

if __name__ == "__main__":
    asyncio.run(main())