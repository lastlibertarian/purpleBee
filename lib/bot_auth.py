from telethon.sync import TelegramClient
from pyrogram import Client
import os
import configparser
from logger.logger import log_uncaught_exceptions
import sys

sys.excepthook = log_uncaught_exceptions

INDEX_DIRECTORY = '%s' % os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config_file_path = '%s/../configs/config.ini' % INDEX_DIRECTORY
config.read(config_file_path)

api_id = config.get('tgClient', 'api_id')
api_hash = config.get('tgClient', 'api_hash')
username = config.get('tgClient', 'username')

pyrobot = Client(name=f'pyrogram_{username}', api_id=api_id, api_hash=api_hash)
telebot = TelegramClient(session=f'telethon_{username}', api_id=api_id, api_hash=api_hash)


def login():
    with pyrobot, telebot:
        pyrobot.send_message("me", "**Pyrogram**")
        telebot.send_message('me', '**Telethon**')
