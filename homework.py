"""Super_bot."""
import json
import logging  # для ОК в тесте на платформе ЯП
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

import exceptions
import log


load_dotenv()
logging.basicConfig()  # для ОК в тесте на платформе ЯП


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
ENDPOINT = os.getenv('ENDPOINT')

RETRY_PERIOD = 600

HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message: str) -> None:
    """Отправка сообщения в чат."""
    logger = log.bot_log()
    try:
        logger.info("Начало отправки сообщения в Telegram чат")
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=f'{message}',
        )
    except telegram.TelegramError as error:
        logger.error(
            f'Ошибка при отправке сообщения: {error}!'
        )
    else:
        logger.debug(f"В Telegram отправлено сообщение '{message}'")


def get_api_answer(current_timestamp: int) -> dict:
    """Запрос на сервер Яндекса."""
    timestamp = current_timestamp or int(time.time())
    payload = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT, headers=HEADERS, params=payload
        )
    except requests.RequestException as error:
        raise exceptions.GetAPIError(
            f'Ошибка при запросе к API:{error}!')
    if homework_statuses.status_code != HTTPStatus.OK:
        raise exceptions.StatusNotOKError(
            f'Статус ответа сервера {homework_statuses.status_code}!'
        )
    try:
        response = homework_statuses.json()
    except json.JSONDecodeError:
        raise json.JSONDecodeError('Ошибка трансформации json -> dict')
    return response


def check_response(response: dict) -> list:
    """Проверяем, что пришел словарь."""
    if not isinstance(response, dict):
        raise TypeError('От сервера пришел не словарь!')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError('Данные не являются списком!')
    return homeworks


def parse_status(homework):
    """Получение статуса домашней работы."""
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if "homework_name" not in homework:
        message = "В словаре homework не найден ключ homework_name"
        raise KeyError(message)
    try:
        verdict = HOMEWORK_VERDICTS[homework_status]
    except KeyError as key_error:
        raise KeyError(
            f'Недопустимый статус домашней работы - {key_error}!'
        )
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Контроль существования переменных в окружении."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основной метод бота."""
    logger = log.bot_log()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    error = None

    if not check_tokens():
        logger.critical("Ошибка! Не все токены обнаружены.")
        sys.exit(['Ошибка! Не все токены обнаружены.'])

    while True:
        try:
            response = get_api_answer(current_timestamp)
            current_timestamp = response.get('current_date')
            homeworks = check_response(response)
            if len(homeworks) == 0:
                logger.debug('Статус домашней работы не изменился.')
            else:
                message = parse_status(homeworks[0])
                send_message(bot, message)
                logger.debug(
                    f'В телеграм отправлено сообщение: {message}'
                )
        except Exception as new_error:
            message = f'Сбой в работе программы: {new_error}.'
            logger.debug(f'Сбой в работе программы: {new_error}')
            if error != str(new_error):
                error = str(new_error)
                send_message(bot, message)
                logger.debug(f'В телеграм отправлено сообщение: {message}')

        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
