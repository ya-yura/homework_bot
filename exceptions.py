class TelegramBotExceptions(Exception):
    """Базовый класс Исключений для телеграм бота."""

    pass


class APIConnectionError(TelegramBotExceptions):
    """Кастомное исключение для работы телеграм бота."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class APIResponseError(TelegramBotExceptions):
    """Кастомное исключение для работы телеграм бота."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
