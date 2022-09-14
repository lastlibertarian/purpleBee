from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, ForeignKey, String, Boolean, DateTime
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import pyrogram
import telethon.tl.types
from pyrogram.errors.exceptions.bad_request_400 import UsernameNotOccupied
from typing import Union, Generator

# engine = create_engine('sqlite:///:memory:', echo=True)
engine = create_engine("mysql+pymysql://ll:passwd@localhost/tg_db", echo=True)
Session = sessionmaker(bind=engine, future=True)
# session = Session()
Base = declarative_base(bind=engine)

Table('chanel_users', Base.metadata,
      Column('associative_chanel', String(200), ForeignKey('channels.id')),
      Column('associative_user', String(200), ForeignKey('users.id'))
      )


class Channel(Base):
    __tablename__ = 'channels'
    id = Column('id', String(200), primary_key=True)
    title = Column('title', String(128))
    description = Column('description', String(255))
    username = Column('username', String(32), nullable=False)
    chat_photo = Column('chat_photo', String(200))
    scam = Column('scam', Boolean, default=False)
    dc_id = Column('dc_id', Integer)
    members_count = Column('members_count', Integer)
    members = relationship("User", secondary='chanel_users', back_populates="channels")
    messages = relationship("Message", back_populates="from_chat")

    def __repr__(self) -> str:
        return f'Channel <id={self.id} username={self.username}>'


class User(Base):
    __tablename__ = 'users'
    id = Column('id', String(200), primary_key=True)
    username = Column('username', String(32))
    firstname = Column('firstname', String(64))
    lastname = Column('lastname', String(64))
    photo = Column('photo', String(200))
    status = Column('status', String(200))
    phone = Column('phone', String(30))
    bot = Column('bot', Boolean, default=False)
    verified = Column('verified', Boolean, default=False)
    scam = Column('scam', Boolean, default=False)
    deleted = Column('deleted', Boolean, default=False)
    fake = Column('fake', Boolean, default=False)
    premium = Column('premium', Boolean, default=False)
    channels = relationship("Channel", secondary='chanel_users', back_populates="members")
    messages = relationship("Message", back_populates="from_user")

    def __repr__(self) -> str:
        return f'User <id={self.id} username={self.username}>'


class Message(Base):
    __tablename__ = 'messages'
    id = Column('id', String(200), primary_key=True)
    user_id = Column('user_id', String(200), ForeignKey('users.id'))
    from_user = relationship("User", back_populates="messages")
    chat_id = Column('chat_id', String(200), ForeignKey('channels.id'))
    from_chat = relationship("Channel", back_populates="messages")
    date = Column('date', DateTime())
    reply_to_message_id = Column('reply_to_message_id', String(200))
    reply_to_top_message_id = Column('reply_to_top_message_id', String(200))
    text = Column('text', String(4200))

    def __repr__(self) -> str:
        return f'Message <date={self.date} text={self.text}>'


Base.metadata.create_all()


class ChatDoesNotExistError(Exception):
    pass


class UserNotInDbError(Exception):
    pass


class ChatNotInDbError(Exception):
    pass


class Parser:

    def __init__(self, pyrogram_client: pyrogram.Client,
                 telethon_client: telethon.tl.types.User,
                 db_session: Session):
        """
        :param pyrogram_client: Объект pyrogram Client
        :param telethon_client: Объект telethon User
        :param db_session: экземпляр db Session
        """

        self.pyrobot: pyrogram.Client = pyrogram_client
        self.telebot: telethon.tl.types.User = telethon_client
        self.session: Session = db_session
        self.__chat_username: str = None
        self.__db_channel: Channel = None

    @property
    def chat_username(self) -> str:
        """
        Геттер chat_username
        :return: str
        """
        return self.__chat_username

    @chat_username.setter
    def chat_username(self, new_chat_username: str) -> None:
        """
        Сеттер chat_username: str и db_channel: Channel
        :param new_chat_username: username чата
        :raise ChatDoesNotExistError
        """
        new_chat_username: str = new_chat_username.replace('https://t.me/', '') if new_chat_username.startswith(
            'https://t.me/') else new_chat_username
        chanel_object: Union[Channel, str] = self.__get_chat(chat_username=new_chat_username)
        if isinstance(chanel_object, Channel):
            self.__chat_username: str = new_chat_username
            self.__db_channel: Channel = chanel_object
        else:
            raise ChatDoesNotExistError

    def __get_chat(self, chat_username) -> Union[Channel, str]:
        """
        Получает инфо чата и добавляет в db
        :return: object: Channel or str
        """
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
            except UsernameNotOccupied:
                return 'ChatDoesNotExist'

    def __get_members(self) -> None:
        """
        Получает всех участников чата и добавляет в db
        """
        with self.telebot, self.session.begin() as session:
            users: telethon.tl.types.User = self.telebot.get_participants(self.__db_channel.username)
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

    def __get_messages(self, limit: int = None) -> None:
        """
        Получает сообщения чата и добавляет в db
        """
        with self.pyrobot, self.session.begin() as session:

            messages: pyrogram.types.Message = self.pyrobot.get_chat_history(self.__db_channel.username, limit=limit)
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

                session.merge(db_message)
                db_user.messages.append(db_message)

                self.__db_channel.messages.append(db_message)

    def parse_users(self, chat_username: str) -> bool:
        """
        Метод парсинг юзеров и добавление в db
        :param chat_username: username чата
        :return: bool
        """
        self.chat_username = chat_username
        self.__get_members()
        return True

    def full_chat_parsing(self, chat_username: str, limit: int = 50000) -> bool:
        """
        Метод парсинг юзеров и сообщений и добавление в db
        :param chat_username: username чата
        :param limit: максимальное количество сообщений
        :return: bool
        """
        if self.parse_users(chat_username=chat_username):
            self.__get_messages(limit=limit)
            return True

    def get_user_messages(self, username: str, chat_username: str = None, limit: int = 1000) -> Generator:
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
                if number == limit - 1:
                    break