from translations import MESSAGES

class BaseClass:
    def __init__(self, language: str = "ru"):
        """
        Инициализация базового класса.
        :param language: Язык сообщений (ru, en, zh).
        """
        self.language = language

    def get_message(self, message_key: str) -> str:
        """
        Возвращает сообщение на выбранном языке.
        :param message_key: Ключ сообщения из словаря MESSAGES.
        :return: Сообщение на выбранном языке.
        """
        if message_key in MESSAGES and self.language in MESSAGES[message_key]:
            return MESSAGES[message_key][self.language]
        return f"Сообщение '{message_key}' не найдено для языка '{self.language}'."