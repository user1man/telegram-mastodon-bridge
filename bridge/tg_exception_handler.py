from telebot import ExceptionHandler


class TelegramExceptionHandler(ExceptionHandler):

    def handle(self, exception: Exception) -> bool:
        print(exception)
        return False
