class TelegramBotExceptions(Exception):
    """Базовый класс Исключений для телеграм бота."""

    pass


class GeneralException(TelegramBotExceptions):
    """Кастоиное исключение для работы телеграм бота."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)