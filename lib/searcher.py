from db_session.db_session import session as db_session
from db_session.db_index import searcher
import logging
from sqlalchemy.orm.session import Session
from logger.logger import get_logger, log_uncaught_exceptions
from tables import User
from exceptions import UserNotInDbError, ChatNotInDbError, ChatDoesNotExistError
import sys

sys.excepthook = log_uncaught_exceptions


class Searcher:

    def __init__(self):
        self.logger: logging.Logger = get_logger(f'{__name__}.{__class__.__name__}',
                                                 path='../logger/logs.log',
                                                 debug_mode=True)
        self.session: Session = db_session()
        self.searcher = searcher

    def get_user(self, username: str = None, user_id: str = None) -> User:
        """
        Принимает username, при наличии в db возвращает объект User
        :param username: username пользователя
        :return: объект User
        :raise: UserNotInDbError
        """
        self.logger.debug('called get_user')
        with self.session() as session:
            if username:
                user: User = session.query(User).filter(User.username == username).first()
            elif user_id:
                user: User = session.query(User).filter(User.id == user_id).first()
            if user:
                return user
            raise UserNotInDbError(f"User <{username}> not found in database")


srch = Searcher()
result = srch.get_user('lastbart')
print(result)
