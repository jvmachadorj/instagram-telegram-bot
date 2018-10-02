import asyncio
import time

import peewee
import telepot
import telepot.aio
from InstagramAPI import InstagramAPI
from decouple import config
from telepot.aio.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from models import Image
from upload_photos import download_photo, change_image_status, \
    post_on_instagram

"""
$ python3.5 skeletona_route.py <token>
It demonstrates:
- passing a routing table to `MessageLoop` to filter flavors.
- the use of custom keyboard and inline keyboard, and their various buttons.
Remember to `/setinline` and `/setinlinefeedback` to enable inline mode for your bot.
It works like this:
- First, you send it one of these 4 characters - `c`, `i`, `h`, `f` - and it replies accordingly:
    - `c` - a custom keyboard with various buttons
    - `i` - an inline keyboard with various buttons
    - `h` - hide custom keyboard
    - `f` - force reply
- Press various buttons to see their effects
- Within inline mode, what you get back depends on the **last character** of the query:
    - `a` - a list of articles
    - `p` - a list of photos
    - `b` - to see a button above the inline results to switch back to a private chat with the bot
"""

try:
    Image.create_table()
except peewee.OperationalError:
    print('Tabela já existe')


message_with_inline_keyboard = None

image = None

chat_id_reply = None

login = InstagramAPI(config('USERNAME'), config('PASSWORD'))
login.login()
print(login)


def generate_post():

    global chat_id_reply
    global image
    image = download_photo()
    time.sleep(15)
    
    markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='Yes', callback_data='yes'),
        InlineKeyboardButton(text='No', callback_data='no'),
    ]])

    url = image.url
    caption = image.caption

    post = "{} \n \n Caption: {} \n \n Do you want to post it?".format(
        url, caption)

    return {'markup': markup, 'url': url, 'caption': caption, 'post': post}


async def on_chat_message(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print('Chat:', content_type, chat_type, chat_id)

    if content_type != 'text':
        return

    global chat_id_reply
    chat_id_reply = chat_id
    command = msg['text'][-1:].lower()
    print(command, msg['text'])

    result = generate_post()

    global message_with_inline_keyboard
    message_with_inline_keyboard = await bot.sendMessage(chat_id, result['post'],
                                                         reply_markup=result['markup'])


async def on_callback_query(msg):
    query_id, from_id, data = telepot.glance(msg, flavor='callback_query')
    print('Callback query:', query_id, from_id, data)
    print(msg)
    global chat_id_reply

    if data == 'yes':
        global image
        global login
        post_on_instagram(image, login)
        change_image_status(image)
        text = 'Image posted! Check it out at: https://www.instagram.com/{}/' \
               ' \n \n Click here to generate a /new_post'.format(
            config('USERNAME'))
        await bot.sendMessage(chat_id_reply, text=text)
    else:
        result = generate_post()
        await bot.sendMessage(chat_id_reply,
                              text=result['post'],
                              reply_markup=result['markup'])


bot = telepot.aio.Bot(config('TOKEN'))
answerer = telepot.aio.helper.Answerer(bot)

loop = asyncio.get_event_loop()
loop.create_task(MessageLoop(bot, {'chat': on_chat_message,
                                   'callback_query': on_callback_query, }).run_forever())
print('Listening ...')

loop.run_forever()
