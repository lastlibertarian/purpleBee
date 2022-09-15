import logging
import traceback


_log_format = '[%(asctime)s] [%(name)s.%(funcName)-8s] [%(levelname)s] : %(message)s'


class CustomFormatter(logging.Formatter):
    green = "\x1b[0;32m"
    white = "\x1b[1;37m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    FORMATS = {
        logging.DEBUG: white + _log_format + reset,
        logging.INFO: green + _log_format + reset,
        logging.WARNING: yellow + _log_format + reset,
        logging.ERROR: red + _log_format + reset,
        logging.CRITICAL: bold_red + _log_format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(fmt=log_fmt,
                                      datefmt='%d-%m-%y %H:%M:%S')
        return formatter.format(record)


def get_file_handler(path):
    file_handler = logging.FileHandler(path)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(fmt=_log_format,
                                                datefmt='%d-%m-%y %H:%M:%S'))
    return file_handler


def get_stream_handler():
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(CustomFormatter())
    return stream_handler


def get_logger(name, path, debug_mode=False):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    if debug_mode:
        logger.addHandler(get_stream_handler())
        return logger
    logger.addHandler(get_file_handler(path))
    return logger


def log_uncaught_exceptions(ex_cls, ex, tb):
    text = '{}: {}:\n'.format(ex_cls.__name__, ex)
    text += ''.join(traceback.format_tb(tb))
    logger = get_logger(__name__, '../logger/logs.log', debug_mode=True)
    logger.critical(text)

