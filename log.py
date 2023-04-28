"""Модуль настроек логирования бота проверки."""
import logging
import sys


def bot_log():
    """Настройки логгера."""
    logger = logging.getLogger(__name__)
    fileHandler = logging.FileHandler("logfile.log", encoding='utf-8')
    streamHandler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    streamHandler.setFormatter(formatter)
    fileHandler.setFormatter(formatter)
    logger.addHandler(streamHandler)
    logger.addHandler(fileHandler)
    logger.setLevel(logging.DEBUG)
    return logger
