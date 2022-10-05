from tables import User, Channel, Message
import pyrogram
import telethon.tl.types
import logging
from pyrogram.errors.exceptions.bad_request_400 import UsernameNotOccupied
from typing import Union, Generator
from logger.logger import get_logger, log_uncaught_exceptions
import sys
from exceptions import UserNotInDbError, ChatNotInDbError, ChatDoesNotExistError
from db_session.db_index import writer
from sqlalchemy.orm.session import Session
from db_session.db_session import session as db_session

sys.excepthook = log_uncaught_exceptions


class Parser:

    def __init__(self, pyrogram_client: pyrogram.Client,
                 telethon_client: telethon.tl.types.User):
        """
        :param pyrogram_client: Объект pyrogram Client
        :param telethon_client: Объект telethon User
        :param db_session: экземпляр db Session
        """
        self.logger: logging.Logger = get_logger(f'{__name__}.{__class__.__name__}',
                                                 path='../logger/logs.log',
                                                 debug_mode=True)
        self.pyrobot: pyrogram.Client = pyrogram_client
        self.telebot: telethon.tl.types.User = telethon_client
        self.session: Session = db_session()
        self.__chat_username: str = None
        self.__db_channel: Channel = None

    @property
    def chat_username(self) -> str:
        """
        Геттер chat_username
        :return: str
        """
        self.logger.debug('received chat_username')
        return self.__chat_username

    @chat_username.setter
    def chat_username(self, new_chat_username: str) -> None:
        """
        Сеттер chat_username: str и db_channel: Channel
        :param new_chat_username: username чата
        :raise ChatDoesNotExistError
        """
        self.logger.debug('called chat_username')
        new_chat_username: str = new_chat_username.replace('https://t.me/', '') if new_chat_username.startswith(
            'https://t.me/') else new_chat_username
        chanel_object: Union[Channel, str] = self.__get_chat(chat_username=new_chat_username)
        if isinstance(chanel_object, Channel):
            self.__chat_username: str = new_chat_username
            self.__db_channel: Channel = chanel_object
            self.logger.info(
                f'{self.__db_channel.username} chat_username|__db_channel: Chanel setted and merged into the db ')
        else:
            raise ChatDoesNotExistError

    def __get_chat(self, chat_username) -> Union[Channel, str]:
        """
        Получает инфо чата и добавляет в db
        :return: object: Channel or str
        """
        self.logger.debug('called __get_chat')
        with self.pyrobot, self.session.begin() as session:
            try:
                chat: pyrogram.types.Chat = self.pyrobot.get_chat(chat_username)
                db_channel: Channel = Channel(id=str(chat.id),
                                              description=chat.description,
                                              title=chat.title,
                                              username=chat.username,
                                              chat_photo=chat.photo.small_photo_unique_id,
                                              scam=chat.is_scam,
                                              dc_id=chat.dc_id,
                                              members_count=chat.members_count)

                session.merge(db_channel)
                return db_channel
            except UsernameNotOccupied as exception:
                self.logger.error(f'{exception.__class__.__name__} {exception}')
                return 'ChatDoesNotExist'
            except Exception as exception:
                self.logger.error(f'{exception.__class__.__name__} {exception}')

    def __get_members(self) -> None:
        """
        Получает всех участников чата и добавляет в db
        """
        self.logger.debug('called __get_members')
        with self.telebot, self.session.begin() as session:
            try:
                users: telethon.tl.types.User = self.telebot.get_participants(self.__db_channel.username)
                self.logger.info(f'{self.__db_channel.username} channel members received')
                db_users: list = []

                for user in users:
                    db_user: User = User(id=str(user.id),
                                         username=user.username,
                                         firstname=user.first_name,
                                         lastname=user.last_name,
                                         photo=str(user.photo.photo_id) if user.photo else None,
                                         status=str(user.status).replace('UserStatus', '').lower()[
                                                :-2] if user.status else None,
                                         phone=user.phone,
                                         bot=user.bot,
                                         verified=user.verified,
                                         deleted=user.deleted,
                                         scam=user.scam,
                                         fake=user.fake,
                                         premium=user.premium)

                    db_users.append(db_user)
                    session.merge(db_user)

                self.__db_channel.members += db_users
                session.merge(self.__db_channel)
                self.logger.info(f'merged {len(db_users)} members {self.__db_channel.username} channel into the db')

            except Exception as exception:
                self.logger.error(f'{exception.__class__.__name__} {exception}')

    def __get_messages(self, limit: int = None) -> None:
        """
        Получает сообщения чата и добавляет в db
        """
        self.logger.debug('called __get_messages')
        with self.pyrobot, self.session.begin() as session, db_writer:
            try:
                messages: pyrogram.types.Message = self.pyrobot.get_chat_history(self.__db_channel.username,
                                                                                 limit=limit)
                self.logger.info(f'{self.__db_channel.username} channel messages generator received')
                db_channel_id: int = self.__db_channel.id

                for message in messages:
                    if message.from_user:
                        db_user: User = User(id=str(message.from_user.id),
                                             username=message.from_user.username,
                                             firstname=message.from_user.first_name,
                                             lastname=message.from_user.last_name,
                                             photo=str(message.from_user.photo.small_photo_unique_id
                                                       ) if message.from_user.photo else None,
                                             status=str(message.from_user.status).replace(
                                                 'UserStatus.', '').lower() if message.from_user.status else None,
                                             bot=message.from_user.is_bot,
                                             verified=message.from_user.is_verified,
                                             deleted=message.from_user.is_deleted,
                                             scam=message.from_user.is_scam,
                                             fake=message.from_user.is_fake,
                                             premium=message.from_user.is_premium)
                        session.merge(db_user)

                        db_message: Message = Message(id=f"{db_channel_id}:{message.id}",
                                                      user_id=message.from_user.id,
                                                      chat_id=message.chat.id,
                                                      date=message.date,
                                                      reply_to_message_id=message.reply_to_message_id,
                                                      reply_to_top_message_id=message.reply_to_top_message_id,
                                                      text=message.text)

                        writer.add_document(message_id=u'{}:{}'.format(db_channel_id, message.id),
                                               user_id=u'{}'.format(message.from_user.id),
                                               content=u'{}'.format(message.text))
                    session.merge(db_message)
                    db_user.messages.append(db_message)

                    self.__db_channel.messages.append(db_message)
                self.logger.info(f'merged {self.__db_channel.username} channel messages into the db')

            except Exception as exception:
                self.logger.error(f'{exception.__class__.__name__} {exception}')

    def parse_users(self, chat_username: str) -> bool:
        """
        Метод парсинг юзеров и добавление в db
        :param chat_username: username чата
        :return: bool
        """
        self.logger.debug('called parse_users')
        self.chat_username = chat_username
        self.__get_members()
        return True

    def full_chat_parsing(self, chat_username: str, message_limit: int = 50000) -> bool:
        """
        Метод парсинг юзеров и сообщений и добавление в db
        :param chat_username: username чата
        :param message_limit: максимальное количество сообщений
        :return: bool
        """
        self.logger.debug('called full_chat_parsing')
        if self.parse_users(chat_username=chat_username):
            self.__get_messages(limit=message_limit)
            return True



    def get_chat(self, chat_username: str) -> Channel:
        """
        Принимает username, при наличии в db возвращает объект User
        :param chat_username: username чата
        :return: объект User
        :raise: UserNotInDbError
        """
        self.logger.debug('called get_chat')
        with self.session() as session:
            chat: Channel = session.query(Channel).filter(Channel.username == chat_username).first()
            if chat:
                return chat
            raise ChatNotInDbError

    def get_chat_messages(self, chat_username: str = None, limit: int = None) -> Generator:
        """
        Принимает chat_username ищет в базе,
        при наличии возвращает генератор с объектами Message
        :param chat_username: username чата
        :param limit: лимит сообщений
        :return: Generator с объектами Message
        :raises: ChatNotInDbError если чата нет в db
        """
        self.logger.debug('called get_chat_messages')
        with self.session() as session:
            chat_username: str = chat_username.replace('https://t.me/', '') if chat_username.startswith(
                'https://t.me/') else chat_username
            chat: Channel = session.query(Channel).filter(Channel.username == chat_username).first()

            if chat:

                messages: list = session.query(Message).filter(Message.chat_id == chat.id).all()
            else:
                raise ChatNotInDbError

            for number, message in enumerate(messages):
                yield message
                if number + 1 == limit:
                    break

    def get_user_messages(self, username: str, chat_username: str = None, limit: int = None) -> Generator:
        """
        Принимает username или username и chat_username ищет в базе,
        при наличии возвращает генератор с объектами Message
        :param username: username пользователя
        :param chat_username: username чата
        :param limit: лимит сообщений
        :return: Generator с объектами Message
        :raises: UserNotInDbError если юзера нет в db
        :raises: ChatNotInDbError если чата нет в db
        """
        self.logger.debug('called get_user_messages')
        with self.session() as session:

            user: User = session.query(User).filter(User.username == username).first()

            if user and chat_username:
                chat_username: str = chat_username.replace('https://t.me/', '') if chat_username.startswith(
                    'https://t.me/') else chat_username
                chat: Channel = session.query(Channel).filter(Channel.username == chat_username).first()
                if chat:
                    messages: list = session.query(Message).filter(Message.user_id == user.id,
                                                                   Message.chat_id == chat.id).all()
                else:
                    raise ChatNotInDbError

            elif user and not chat_username:
                messages: list = session.query(Message).filter(Message.user_id == user.id).all()

            else:
                raise UserNotInDbError
            for number, message in enumerate(messages):
                yield message
                if number + 1 == limit:
                    break