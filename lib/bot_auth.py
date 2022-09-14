import telethon
import pyrogram
import asyncio

api_id = 12359630
api_hash = 'f85fd0ec567c2f9ed2378fc4bc59a137'
username = 'lastbart'


async def login():
    async with pyrogram.Client(name=f'pyrogram_{username}',
                               api_id=api_id,
                               api_hash=api_hash) as pyrobot, \
            telethon.TelegramClient(session=f'telethon_{username}',
                                    api_id=api_id,
                                    api_hash=api_hash) as telebot:
        await pyrobot.send_message("me", "**Pyrogram**")
        await telebot.send_message('me', '**Telethon**')


asyncio.run(login())

