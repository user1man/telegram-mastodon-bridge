from telebot import ExceptionHandler
from bridge import logger

class TelegramExceptionHandler(ExceptionHandler):

    def handle(self, exception: Exception) -> bool:
        logger.exception(exception)
        return True
