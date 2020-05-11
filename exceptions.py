# Исключение для ошибок при работе с API
class APIRequestException(Exception):

    def __init__(self, message=None):
        if message is None:
            super().__init__('Ошибка вызова API')
        else:
            super().__init__(message)


# Исключение для ошибок при работе парсера
class ParsingException(Exception):

    def __init__(self, message=None):
        if message is None:
            super().__init__('Ошибка парсера')
        else:
            super().__init__(message)


# Исключение для ошибок при работе с бд
class DBException(Exception):

    def __init__(self, message=None):
        if message is None:
            super().__init__('Ошибка при выполнении запроса к БД')
        else:
            super().__init__(message)
