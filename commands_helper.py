import os
from telegram import Update
from mongodb import connect_to_mongo
from dotenv import load_dotenv
from datetime import datetime
from unidecode import unidecode
import re

def remove_accents(string):
    return unidecode(string)
 

def handle_add_song_command(update: Update, context):
    load_dotenv()
    URL_DB = os.getenv("URL_DB")
    message = update.message
    args = message.text.split(maxsplit=1)[1].split(',', maxsplit=1)
    args = [arg.strip() for arg in args]
    if len(args) < 2:
        context.bot.send_message(chat_id=message.chat_id, text="Por favor, proporcione el nombre y la clasificación de la canción separados por una coma.")
        return

    song_name = args[0]
    song_classification = remove_accents(args[1].lower())

    db_manager = connect_to_mongo(URL_DB)
    db_manager.insert_song({"name": song_name, "classification": song_classification, "priority": "high", "last_update": datetime.now()})

    context.bot.send_message(chat_id=message.chat_id, text=f"La canción '{song_name}' ha sido agregada correctamente.")

def handle_search_song(update: Update, context):
    load_dotenv()
    URL_DB = os.getenv("URL_DB")
    message = update.message
    args = message.text.split(maxsplit=1)[1].split(',', maxsplit=1)
    args = [arg.strip() for arg in args]
    if len(args) < 1:
        context.bot.send_message(chat_id=message.chat_id, text="Por favor, proporcione el nombre de la canción.")
        return

    song_name = args[0]

    db_manager = connect_to_mongo(URL_DB)
    songs_cursor = db_manager.get_songs()

    if not songs_cursor:
        context.bot.send_message(chat_id=message.chat_id, text="No se encontraron canciones en la base de datos.")
        return
    #de todas las canciones que hay en la base de datos, buscar las que coincidan con el nombre de la cancion
    songs = list(songs_cursor)
    #se buscan variantes que coincidan con el nombre de la cancion
    matching_songs = []
    pattern = re.compile(r'.*{}.*'.format(re.escape(song_name)), re.IGNORECASE)
    for song in songs:
        name = song.get("name") or song.get("nombre")
        if name and re.search(pattern, name):
            matching_songs.append(song)

    if not matching_songs:
        context.bot.send_message(chat_id=message.chat_id, text=f"No se encontraron canciones que coincidan con '{song_name}'.")
        return

    response = "Canciones encontradas:\n"
    for song in matching_songs:
        response += f"- {song.get('name') or song.get('nombre')}\n"

    context.bot.send_message(chat_id=message.chat_id, text=response)

def handle_show_list_by_category(update: Update, context):
    load_dotenv()
    URL_DB = os.getenv("URL_DB")
    message = update.message
    args = message.text.split(maxsplit=1)[1].split(',', maxsplit=1)
    args = [arg.strip() for arg in args]
    if len(args) < 1:
        context.bot.send_message(chat_id=message.chat_id, text="Por favor, proporcione la clasificación de la canción.")
        return

    song_classification = remove_accents(args[0].lower())

    db_manager = connect_to_mongo(URL_DB)
    songs_cursor = db_manager.get_songs()

    if not songs_cursor:
        context.bot.send_message(chat_id=message.chat_id, text="No se encontraron canciones en la base de datos.")
        return

    songs = list(songs_cursor)
    songs_with_classification = [song for song in songs if song.get('classification') == song_classification]

    if not songs_with_classification:
        context.bot.send_message(chat_id=message.chat_id, text=f"No se encontraron canciones con la clasificación '{song_classification}'.")
        return

    response = f"Canciones con clasificación '{song_classification}':\n"
    for song in songs_with_classification:
        response += f"- {song.get('name') or song.get('nombre')}\n"

    context.bot.send_message(chat_id=message.chat_id, text=response)
