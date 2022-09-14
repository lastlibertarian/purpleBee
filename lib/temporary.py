import pyrogram
import telethon.tl.types
from pyrogram import Client
from pyrogram.errors.exceptions.bad_request_400 import UsernameNotOccupied
from telethon.sync import TelegramClient
import configparser
from objects import User, Channel, Session, Message, Parser

# config = configparser.ConfigParser()
# config.read("../config.ini")
api_id = 12359630
api_hash = 'f85fd0ec567c2f9ed2378fc4bc59a137'
username = 'lastbart'


# class ChatDoesNotExistError(Exception):
#     pass
#
#
# class Parser:
#
#     def __init__(self, pyrogram_client: pyrogram.Client,
#                  telethon_client: telethon.tl.types.User,
#                  db_session: Session):
#         """
#         :param pyrogram_client: pyrogram.Client
#         :param telethon_client: telethon.tl.types.User
#         :param db_session: Session
#         """
#
#         self.pyrobot: pyrogram.Client = pyrogram_client
#         self.telebot: telethon.tl.types.User = telethon_client
#         self.session: Session = db_session
#         self.__chat_username: str = None
#         self.__db_channel: Channel = None
#
#     @property
#     def chat_username(self) -> str:
#         """
#         Геттер chat_username
#         :return: str
#         """
#         return self.__chat_username
#
#     @chat_username.setter
#     def chat_username(self, new_chat_username: str) -> None:
#         """
#         Сеттер chat_username: str и db_channel: Channel
#         :param new_chat_username: str
#         :return: None
#         :raise ChatDoesNotExistError
#         """
#         new_chat_username: str = new_chat_username.replace('https://t.me/', '') if new_chat_username.startswith(
#             'https://t.me/') else new_chat_username
#         chanel_object: Channel or str = self.__get_chat(chat_username=new_chat_username)
#         if isinstance(chanel_object, Channel):
#             self.__chat_username: str = new_chat_username
#             self.__db_channel: Channel = chanel_object
#         else:
#             raise ChatDoesNotExistError
#
#     def __get_chat(self, chat_username) -> Channel or str:
#         """
#         Получает инфо чата и добавляет в db
#         :return: object: Channel or str
#         """
#         with self.pyrobot, self.session.begin() as session:
#             try:
#                 chat: pyrogram.types.Chat = self.pyrobot.get_chat(chat_username)
#                 db_channel: Channel = Channel(id=str(chat.id),
#                                               description=chat.description,
#                                               title=chat.title,
#                                               username=chat.username,
#                                               chat_photo=chat.photo.small_photo_unique_id,
#                                               scam=chat.is_scam,
#                                               dc_id=chat.dc_id,
#                                               members_count=chat.members_count)
#
#                 session.merge(db_channel)
#                 return db_channel
#             except UsernameNotOccupied:
#                 return 'ChatDoesNotExist'
#
#     def __get_members(self) -> None:
#         """
#         Получает всех участников чата и добавляет в db
#         """
#         with self.telebot, self.session.begin() as session:
#             users: telethon.tl.types.User = self.telebot.get_participants(self.__db_channel.username)
#             db_users: list = []
#
#             for user in users:
#                 db_user: User = User(id=str(user.id),
#                                      username=user.username,
#                                      firstname=user.first_name,
#                                      lastname=user.last_name,
#                                      photo=str(user.photo.photo_id) if user.photo else None,
#                                      status=str(user.status).replace('UserStatus', '').lower()[
#                                             :-2] if user.status else None,
#                                      phone=user.phone,
#                                      bot=user.bot,
#                                      verified=user.verified,
#                                      deleted=user.deleted,
#                                      scam=user.scam,
#                                      fake=user.fake,
#                                      premium=user.premium)
#
#                 db_users.append(db_user)
#                 session.merge(db_user)
#
#             self.__db_channel.members += db_users
#             session.merge(self.__db_channel)
#
#     def __get_messages(self, limit: int = None) -> None:
#         """
#         Получает сообщения чата и добавляет в db
#         """
#         with self.pyrobot, self.session.begin() as session:
#
#             messages: pyrogram.types.Message = self.pyrobot.get_chat_history(self.__db_channel.username, limit=limit)
#             db_channel_id: int = self.__db_channel.id
#
#             for message in messages:
#                 if message.from_user:
#                     db_user: User = User(id=str(message.from_user.id),
#                                          username=message.from_user.username,
#                                          firstname=message.from_user.first_name,
#                                          lastname=message.from_user.last_name,
#                                          photo=str(message.from_user.photo.small_photo_unique_id
#                                                    ) if message.from_user.photo else None,
#                                          status=str(message.from_user.status).replace(
#                                              'UserStatus.', '').lower() if message.from_user.status else None,
#                                          bot=message.from_user.is_bot,
#                                          verified=message.from_user.is_verified,
#                                          deleted=message.from_user.is_deleted,
#                                          scam=message.from_user.is_scam,
#                                          fake=message.from_user.is_fake,
#                                          premium=message.from_user.is_premium)
#                     session.merge(db_user)
#
#                     db_message: Message = Message(id=f"{db_channel_id}:{message.id}",
#                                                   user_id=message.from_user.id,
#                                                   chat_id=message.chat.id,
#                                                   date=message.date,
#                                                   reply_to_message_id=message.reply_to_message_id,
#                                                   reply_to_top_message_id=message.reply_to_top_message_id,
#                                                   text=message.text)
#
#                 session.merge(db_message)
#                 db_user.messages.append(db_message)
#
#                 self.__db_channel.messages.append(db_message)
#
#     def parse(self):
#         self.__get_members()
#         self.__get_messages()


parser = Parser(pyrogram_client=Client(name=f'pyrogram_{username}',
                                       api_id=api_id,
                                       api_hash=api_hash),
                telethon_client=TelegramClient(session=f'telethon_{username}',
                                               api_id=api_id,
                                               api_hash=api_hash),
                db_session=Session)
# chat_username="BlackMASTChat")
# print(parser.chat_username)
# parser.chat_username = "https://t.me/BlackMASTChat"
# print(parser.chat_username)

for i in parser.get_user_messages(username='LaStbArt', chat_username='https://t.me/BlackMASTChat', limit=3):
    print(i.date, i.text)

