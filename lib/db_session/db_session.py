from sqlalchemy import orm
from sqlalchemy.ext.declarative import declarative_base
import configparser
import os
from sqlalchemy import create_engine
from lib.logger.logger import log_uncaught_exceptions
import sys

sys.excepthook = log_uncaught_exceptions

INDEX_DIRECTORY = '%s' % os.path.dirname(os.path.realpath(__file__))


def engine(echo=False):
    config = configparser.ConfigParser()
    config_file_path = '%s/../../configs/config.ini' % INDEX_DIRECTORY
    config.read(config_file_path)
    db_user = config.get('Session', 'username')
    db_pass = config.get('Session', 'password')
    db_host = config.get('Session', 'host')
    db_name = config.get('Session', 'dbname')
    conn_string = 'mysql+pymysql://%s:%s@%s/%s?charset=utf8mb4' % (db_user.replace('"', ''),
                                                                   db_pass.replace('"', ''),
                                                                   db_host.replace('"', ''),
                                                                   db_name.replace('"', ''))
    result = create_engine(conn_string, echo=echo)
    return result


def session(base_required=False, echo=False):
    eng = engine(echo=echo)
    if base_required:
        return declarative_base(bind=eng)
    return orm.sessionmaker(bind=eng, future=True)
