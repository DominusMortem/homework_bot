"""Бот для проверки статуса домашних заданий."""

from http import HTTPStatus
import logging
import os
import time

import requests
import telegram

from dotenv import load_dotenv
from logging.handlers import RotatingFileHandler

import exceptions


load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 2
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}


HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler('stdout', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)


def send_message(bot, message):
    """Функция отправления сообщения в Телеграм."""
    bot.send_message(TELEGRAM_CHAT_ID, message)
    logger.info(f'Сообщение: "{message}" - успешно отправлено')


def get_api_answer(current_timestamp):
    """Проверка ответа от API Яндекс.Практикума."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    request = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if request.status_code == HTTPStatus.OK:
        return request.json()
    else:
        logger.error(f'Сервер недоступен, код ответа: {request.status_code}')
        raise exceptions.BadHTTPStatusException(
            f'Сервер недоступен, код ответа: {request.status_code}'
        )


def check_response(response):
    """Проверка полученных данных о домашней работе."""
    if type(response) == dict:
        try:
            'homeworks' in response
        except KeyError:
            logger.error('Ключ "homeworks" отсутствует.')
            raise exceptions.HomeworksKeyException
        if type(response.get('homeworks')) is not list:
            logger.error('Данные не соответствуют ожидаемым.')
            raise exceptions.HomeworksNotListException
        if len(response.get('homeworks')) == 0:
            logger.debug('Список домашних заданий пуст.')
            raise exceptions.EmptyHomeworksListException
        return response.get('homeworks')
    else:
        raise TypeError


def parse_status(homework):
    """Получение данных по статусу домашней работы."""
    if homework.get('homework_name'):
        homework_name = homework.get('homework_name')
        homework_status = homework.get('status')
        if homework_status in HOMEWORK_STATUSES:
            verdict = HOMEWORK_STATUSES.get(homework_status)
            return (
                f'Изменился статус проверки работы "{homework_name}".{verdict}'
            )
        else:
            logger.error('Несуществующий статус проверки работы.')
            raise exceptions.StatusKeyException
    else:
        logger.error('Параметр homework_name отсутствует.')
        raise KeyError


def check_tokens():
    """Проверка переменных окружения."""
    return all([PRACTICUM_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID])


def main():
    """Основная логика работы бота."""
    last_error = list()
    last_status = dict()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = 1645960144
    if not check_tokens():
        logger.critical('Отсутствуют переменные окружения!')
        raise SystemExit()
    while True:
        try:
            response = get_api_answer(current_timestamp)
            homeworks = check_response(response)
            for homework in homeworks:
                message = parse_status(homework)
                id = homework.get('id')
                if last_status.get(id) != message:
                    send_message(bot, message)
                    last_status[id] = last_status.get(id, message)
                else:
                    logger.info('Обновлений статуса не поступало.')
            current_timestamp = int(time.time())
            time.sleep(RETRY_TIME)
        except Exception as error:
            if type(error) != type(last_error):
                message = f'Сбой в работе программы: {error}'
                send_message(bot, message)
                last_error = error
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    main()
