from sqlalchemy import Column, Integer, ForeignKey, String, Boolean, DateTime, Table
from sqlalchemy.orm import relationship
from lib.db_session.db_session import session
from lib.logger.logger import log_uncaught_exceptions
import sys

sys.excepthook = log_uncaught_exceptions

Base = session(base_required=True, echo=True)

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
    members = relationship("User", secondary='chanel_users', lazy=False)
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
    # channels = relationship("Channel", secondary='chanel_users', back_populates="members")
    messages = relationship("Message", back_populates="from_user")

    def __repr__(self) -> str:
        return f'User <id={self.id} username={self.username}>'


class Message(Base):
    __tablename__ = 'messages'
    id = Column('id', String(200), primary_key=True)
    user_id = Column('user_id', String(200), ForeignKey('users.id'))
    from_user = relationship("User")
    chat_id = Column('chat_id', String(200), ForeignKey('channels.id'))
    from_chat = relationship("Channel")
    date = Column('date', DateTime())
    reply_to_message_id = Column('reply_to_message_id', String(200))
    reply_to_top_message_id = Column('reply_to_top_message_id', String(200))
    text = Column('text', String(4200))

    def __repr__(self) -> str:
        return f'Message <date={self.date} text={self.text}>'


Base.metadata.create_all()
