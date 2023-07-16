
import os
from dotenv import load_dotenv
from telegram import Bot
import logging
from telegram.ext import CommandHandler, Updater
from commands_helper import handle_add_song_command, handle_search_song, handle_show_list_by_category


def main():
    try :
        load_dotenv()
        BOT_TOKEN = os.getenv("BOT_TOKEN")
        bot = Bot(token=BOT_TOKEN)

        # Crear instancia del updater y pasar el bot como argumento
        updater = Updater(bot=bot, use_context=True)

        # Obtener el dispatcher del updater
        dispatcher = updater.dispatcher

        # Agregar los handlers de los comandos
        add_song_handler = CommandHandler('addsong', handle_add_song_command)
        search_song_handler = CommandHandler('searchsong', handle_search_song)
        show_list_by_category = CommandHandler('showlist', handle_show_list_by_category)
        dispatcher.add_handler(add_song_handler)
        dispatcher.add_handler(search_song_handler)
        dispatcher.add_handler(show_list_by_category)
        # Iniciar el polling del updater
        updater.start_polling()

        # Mantener el programa en ejecución
        updater.idle()
    except Exception as e:
        logging.error("Error al iniciar el bot: ", e)

if __name__ == "__main__":
    main()