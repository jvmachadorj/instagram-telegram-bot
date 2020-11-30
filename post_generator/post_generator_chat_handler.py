import time

import telepot
from decouple import config
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

from post_generator.post_generator_service import post_on_instagram
from upload_photos import download_photo, change_image_status

propose_records = telepot.helper.SafeDict()


class GeneratePostChatHandler(telepot.aio.helper.ChatHandler):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='Yes', callback_data='yes'),
        InlineKeyboardButton(text='No', callback_data='no'),
    ]])

    def __init__(self, *args, **kwargs):
        super(GeneratePostChatHandler, self).__init__(*args, **kwargs)
        global propose_records
        self.instagram_bot = kwargs["instagram_bot"]
        if self.id in propose_records:
            self._count, self._edit_msg_ident = propose_records[self.id]
            self._editor = telepot.aio.helper.Editor(self.bot,
                                                     self._edit_msg_ident) \
                if self._edit_msg_ident else None
        else:
            self._count = 0
            self._edit_msg_ident = None
            self._editor = None

    async def _cancel_last(self):
        if self._editor:
            await self._editor.editMessageReplyMarkup(reply_markup=None)
            self._editor = None
            self._edit_msg_ident = None

    async def on__idle(self, event):
        self.sender.sendMessage('I know you may need a little time to decide.')
        self.close()

    async def on_close(self, ex):
        # Save to database
        global propose_records
        propose_records[self.id] = (self._count, self._edit_msg_ident)

    async def _propose(self):
        global image
        image = download_photo()

        post = "{} \n \n Caption: {} \n \n Do you want to post it?".format(
            image.url, image.caption)

        sent = await self.sender.sendMessage(post, reply_markup=self.keyboard)
        self._editor = telepot.helper.Editor(self.bot, sent)
        self._edit_msg_ident = telepot.message_identifier(sent)

    async def on_chat_message(self, msg):
        await self._propose()

    async def on_callback_query(self, msg):
        query_id, from_id, query_data = telepot.glance(msg,
                                                       flavor='callback_query')
        print('CallbackQuery: queryid:{} chatid:{} querydata:{}'
              .format(query_id, from_id, query_data))

        if query_data == 'yes':
            post_on_instagram(self.instagram_bot)
            await self.sender.sendMessage(
                'Image posted! Check it out at: https://www.instagram.com/{}/'
                    .format(config('USERNAME_INSTAGRAM')))
            change_image_status(image)
            await self.close()
        else:
            await self.bot.answerCallbackQuery(
                query_id, text='Alright! Lets try another picture.'
            )
            await self._cancel_last()
            time.sleep(5)
            await self._propose()
