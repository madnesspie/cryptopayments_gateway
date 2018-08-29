import logging
from functools import wraps

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
ERROR = logging.ERROR

logging.basicConfig(
    format='%(asctime)s ~ %(levelname)-10s %(name)-25s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S', filename='gateway.log', level=DEBUG)

logging.addLevelName(DEBUG, '🐛 DEBUG')
logging.addLevelName(INFO, '📑 INFO')
logging.addLevelName(WARNING, '🤔 WARNING')
logging.addLevelName(ERROR, '🚨 ERROR')


def setup_logger(name, level=DEBUG):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    return logger


def log(func):
    logger = logging.getLogger(func.__module__)

    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        logger.debug(f"Called::{func.__name__}. Returned {result}")
        return result
    return wrapper
