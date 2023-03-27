import logging
import logging.config
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import GeneralException

load_dotenv()

logging.config.fileConfig('logging_config.ini', disable_existing_loggers=False)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logger = logging.getLogger('homework')


def send_message(bot: telegram.Bot, message: str):
    """Отправка сообщения в Telegram чат."""
    logging.info('Отправка сообщения в Telegram чат.')
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except telegram.error.TelegramError:
        logger.exception('Сообщение не отпралено.')


def get_api_answer(current_timestamp) -> dict:
    """Получение ответа от API yandex practicum."""
    logging.info('Получение ответа от API yandex practicum.')
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(url=ENDPOINT, headers=HEADERS, params=params)
        logging.debug('Ответ от API получен.')
    except Exception as error:
        message = f'Нет связи с API yandex practicum {error}'
        logger.exception(message)
        raise GeneralException(message)
    if response.status_code != HTTPStatus.OK:
        raise GeneralException(
            f'Ответ от API - {response.reason}'
            f'(Код ответа - {response.status_code}.'
            f'Содержание ответа - {response.text}'
        )
    logging.debug('Статус ответа от API - OK.')
    return response.json()


def check_response(response: dict) -> dict:
    """Проверка ответа от API yandex practicum."""
    logging.info('Проверка ответа от API yandex practicum.')
    if not isinstance(response, dict):
        raise TypeError('Ответ от API yandex practicum не является словарем.')
    logging.debug('Получен список домашних работ.')
    if not isinstance(response.get('homeworks'), list):
        raise TypeError('Домашние работы не возвращаются в виде списка.')
    return response['homeworks']


def parse_status(homework: dict) -> str:
    """Проверка статуса домашней работы."""
    logging.info('Проверка статуса домашней работы.')
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status in HOMEWORK_STATUSES:
        verdict = HOMEWORK_STATUSES.get(homework_status)
    else:
        raise KeyError('Неизвестный статус домашней работы!'
                       f'Получен статус - {homework_status}')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_tokens() -> bool:
    """Проверка доступности переменных окружения."""
    logging.info('Проверка переменных среды.')
    env_variables = [PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID]
    return all(env_variables)


def main():
    """Основная логика работы бота."""
    logging.info('Запуск программы.')
    last_sent_error_message = ''
    if not check_tokens():
        logger.critical('Отсутствуют переменные среды!')
        sys.exit()
    current_timestamp = int(time.time())
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    while True:
        try:
            response = get_api_answer(current_timestamp)
            response_json = check_response(response)
            if response_json != []:
                message = parse_status(response_json[0])
            message = 'Обновлений нет.'
            send_message(bot, message)
            current_timestamp = response.get('current_date')
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            if message != last_sent_error_message:
                send_message(bot, message)
                last_sent_error_message = message
            logger.exception(message)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
