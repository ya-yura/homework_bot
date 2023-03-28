class TelegramBotExceptions(Exception):
    """Базовый класс Исключений для телеграм бота."""

    pass


class APIConnectionError(TelegramBotExceptions):
    """Ошибка, возникающая при разрыве связи с API."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class APIResponseError(TelegramBotExceptions):
    """Ошибка, возникающая при некорректном ответе от API."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
