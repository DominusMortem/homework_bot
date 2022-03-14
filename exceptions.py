"""Исключения при работе с ботом."""


class BadHTTPStatusException(Exception):
    """Исключение о статусе кода страницы."""

    pass


class HomeworksKeyException(Exception):
    """Исключение при отсутствии ключа homeworks."""

    def __str__(self):
        return 'Ключ "homeworks" отсутствует в словаре'


class HomeworksNotListException(Exception):
    """Исключение при несовпадении данных."""

    def __str__(self):
        return 'Тип данных не соответствует ожидаемым.'


class StatusKeyException(Exception):
    """Исключение при незарегистрированном статусе."""

    def __str__(self):
        return 'Несуществующий статус проверки работы.'


class EmptyHomeworksListException(Exception):
    """Исключение при пустом списке."""

    def __str__(self):
        return 'Список домашних работ пуст.'


class ResponseNotDictException(Exception):
    """Исключение при неправильном типе данных."""

    def __str__(self):
        return 'Ошибочный тип полученных данных.'
