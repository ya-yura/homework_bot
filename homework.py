import logging
import logging.config
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import APIResponseError, APIConnectionError

load_dotenv()

logging.config.fileConfig('logging_config.ini', disable_existing_loggers=False)

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_VERDICTS = {
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
        logging.debug('Сообщение успешно отправлено в Telegram чат.')
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
        raise APIConnectionError(
            f'{message}. '
            f'Ответ от API - {response.reason} '
            f'Содержание ответа - {response.text}'
        )
    if response.status_code != HTTPStatus.OK:
        raise APIResponseError(
            f'Ожидался код 200, но получен код {response.status_code}. '
            f'Ответ от API - {response.reason} '
            f'Содержание ответа - {response.text}'
        )
    logging.debug('Статус ответа от API - OK.')
    return response.json()


def check_response(response: dict) -> dict:
    """Проверка ответа от API yandex practicum."""
    logging.info('Проверка ответа от API yandex practicum.')
    if not isinstance(response, dict):
        raise TypeError(
            f'Ответ от API yandex practicum имеет тип '
            f'{type(response)}, ожидается словарь.'
        )
    logging.debug('Получен список домашних работ.')
    if not isinstance(response.get('homeworks'), list):
        raise TypeError('Домашние работы не возвращаются в виде списка.')
    return response['homeworks']


def parse_status(homework: dict) -> str:
    """Проверка статуса домашней работы."""
    logging.info('Проверка статуса домашней работы.')
    homework_name = homework.get('homework_name')
    if homework_name is None:
        raise KeyError('Ответ API не содержит ключа homework_name.')
    homework_status = homework.get('status')
    if homework_status in HOMEWORK_VERDICTS:
        verdict = HOMEWORK_VERDICTS.get(homework_status)
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
        sys.exit('Программа завершена')
    current_timestamp = int(time.time())
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    while True:
        try:
            response = get_api_answer(current_timestamp)
            response_json = check_response(response)
            if response_json:
                message = parse_status(response_json[0])
                send_message(bot, message)
            else:
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
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
