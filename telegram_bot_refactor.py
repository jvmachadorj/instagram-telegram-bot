import logging

import peewee
from InstagramAPI import InstagramAPI
from decouple import config
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler

from models import Image
from upload_photos import download_photo, change_image_status

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    Image.create_table()
except peewee.OperationalError:
    print('Tabela já existe')

image = None
login = InstagramAPI(config('USERNAME_INSTAGRAM'), config('PASSWORD'))
login.login()


def post_on_instagram():
    global image

    # Upload Photo
    login.uploadPhoto(image.path, caption=image.caption, upload_id=None)
    print("Posted with caption {}".format(image.caption))


def start(bot, update):
    keyboard = [[InlineKeyboardButton("Yes", callback_data='1'),
                 InlineKeyboardButton("No", callback_data='2')]]

    global image
    image = download_photo()

    post = "{} \n \n Caption: {} \n \n Do you want to post it?".format(
        image.url, image.caption)

    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(post, reply_markup=reply_markup)


def button(bot, update):
    query = update.callback_query

    if query.data == '1':
        post_on_instagram()
        change_image_status(image)
        text = "Image posted! Check it out at: https://www.instagram.com/{}/ /n/n {} /n/n Caption: {}".format(config('USERNAME_INSTAGRAM'), image.url, image.caption)
        bot.edit_message_text(text=text,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        start(bot, query)
    else:
        text = 'Alright! Lets try another picture.'
        bot.edit_message_text(text=text,
                              chat_id=query.message.chat_id,
                              message_id=query.message.message_id)
        start(bot, query)


def help(bot, update):
    update.message.reply_text("Use /start to test this bot.")


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(config('TOKEN'))

    updater.dispatcher.add_handler(CommandHandler('start', start))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler('help', help))
    updater.dispatcher.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
