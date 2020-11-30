import asyncio

import peewee
import telepot
from InstagramAPI import InstagramAPI
from decouple import config
from telepot.aio.loop import MessageLoop
from telepot.aio.delegate import pave_event_space, per_chat_id, create_open, include_callback_query_chat_id

from models import Image
from post_generator.post_generator_chat_handler import GeneratePostChatHandler

try:
    Image.create_table()
except peewee.OperationalError:
    print('Table already exists')

INSTAGRAM_USERNAME = config('INSTAGRAM_USERNAME')
INSTAGRAM_PASSWORD = config('INSTAGRAM_PASSWORD')


def main():
    instagram_bot = InstagramAPI(INSTAGRAM_USERNAME, INSTAGRAM_PASSWORD)
    instagram_bot.login()

    bot = telepot.aio.DelegatorBot(config('TOKEN'), [
        include_callback_query_chat_id(pave_event_space())(
            per_chat_id(types=['private']), create_open, GeneratePostChatHandler, timeout=10),
    ])

    loop = asyncio.get_event_loop()
    loop.create_task(MessageLoop(bot).run_forever())
    print('Listening ...')

    loop.run_forever()


if __name__ == '__main__':
    main()
