"""Бот для проверки статуса домашних заданий."""

import sys
import logging
import time
from logging.handlers import RotatingFileHandler
from http import HTTPStatus

import requests
import telegram


import exceptions
from config import PRACTICUM_TOKEN, TELEGRAM_CHAT_ID, TELEGRAM_TOKEN


RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

logger = logging.getLogger(__name__)
handler = RotatingFileHandler('stdout', maxBytes=50000000, backupCount=5)
logger.addHandler(handler)

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def send_message(bot, message):
    """Функция отправления сообщения в Телеграм."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
        logger.info(f'Сообщение: "{message}" - успешно отправлено')
    except Exception as error:
        logger.error(f'Ошибка отправки сообщения в телеграмм: {error}')


def get_api_answer(current_timestamp):
    """Проверка ответа от API Яндекс.Практикума."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    request = requests.get(ENDPOINT, headers=HEADERS, params=params)
    if request.status_code != HTTPStatus.OK:
        logger.error(f'Сервер недоступен, код ответа: {request.status_code}')
        raise exceptions.BadHTTPStatusException(
            f'Сервер недоступен, код ответа: {request.status_code}'
        )
    return request.json()


def check_response(response):
    """Проверка полученных данных о домашней работе."""
    if not isinstance(response, dict):
        raise TypeError
    try:
        response['homeworks']
    except KeyError:
        logger.error('Ключ "homeworks" отсутствует.')
        raise exceptions.HomeworksKeyException
    if not isinstance(response.get('homeworks'), list):
        logger.error('Данные не соответствуют ожидаемым.')
        raise exceptions.HomeworksNotListException
    if len(response.get('homeworks')) == 0:
        logger.debug('Список домашних заданий пуст.')
        raise exceptions.EmptyHomeworksListException
    return response.get('homeworks')


def parse_status(homework):
    """Получение данных по статусу домашней работы."""
    if homework.get('homework_name') is None:
        logger.error('Параметр homework_name отсутствует.')
        raise KeyError
    homework_name = homework.get('homework_name')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_STATUSES:
        logger.error('Несуществующий статус проверки работы.')
        raise exceptions.StatusKeyException
    verdict = HOMEWORK_STATUSES.get(homework_status)
    return (
        f'Изменился статус проверки работы "{homework_name}".{verdict}'
    )


def check_tokens():
    """Проверка переменных окружения."""
    return all(
        [
            PRACTICUM_TOKEN,
            TELEGRAM_TOKEN,
            TELEGRAM_CHAT_ID
        ]
    )


def main():
    """Основная логика работы бота."""
    last_error = list()
    last_status = dict()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    if not check_tokens():
        logger.critical('Отсутствуют переменные окружения!')
        raise sys.exit('Завершение работы.')
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
        except Exception as error:
            if type(error) != type(last_error):
                message = f'Сбой в работе программы: {error}'
                send_message(bot, message)
                last_error = error
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    main()
