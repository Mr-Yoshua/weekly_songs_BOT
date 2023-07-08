import random
import json
import os
import asyncio
from dotenv import load_dotenv
from telegram import Bot

class Cancion:
    def __init__(self, nombre, clasificacion):
        self.nombre = nombre
        self.clasificacion = clasificacion

def load_songs(list_name):
    songs = []
    with open(list_name, "r", encoding="utf-8") as file:
        data = json.load(file)
        for song in data:
            song = Cancion(song["nombre"], song["clasificacion"])
            songs.append(song)
    return songs

def show_list(random_daily_songs):
    print(f"--- Canciones para hoy elegidas al azar: ---")
    for clasification in random_daily_songs:
        songs_clasification = random_daily_songs[clasification]
        for song in songs_clasification:
            print(f"{song.nombre} - {song.clasificacion}")
        print()

def generate_list(songs):
    # necesito dos canciones de cada clasificacion
    random_daily_songs = {}
    clasification_type = ["himnario", "carpeta", "rapida", "adoracion"]
    for clasification in clasification_type:
        selected_songs = [song for song in songs if song.clasificacion == clasification]
        if len(selected_songs) >= 2:
            random_songs = random.sample(selected_songs, 2)
        else:
            random_songs = random.sample(selected_songs, 1)
        random_daily_songs[clasification] = random_songs
    return random_daily_songs

async def send_by_telegram(random_daily_songs, bot_token, chat_id):
    bot = Bot(token=bot_token)
    message = "Listado aleatorio de canciones:\n\n"
    for classification in random_daily_songs:
        songs_classification = random_daily_songs[classification]
        message += f"- {classification.upper()} -\n"
        for song in songs_classification:
            message += f"{song.nombre} - {song.clasificacion}\n"
        message += "\n"

    await bot.send_message(chat_id=chat_id, text=message)


async def main():
    load_dotenv()
    list_name = "song-list.json"
    songs = load_songs(list_name)
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    CHAT_ID = os.getenv("CHAT_ID")
    random_daily_songs = generate_list(songs)
    show_list(random_daily_songs)
    await send_by_telegram(random_daily_songs, BOT_TOKEN, CHAT_ID)

if __name__ == "__main__":
    asyncio.run(main())