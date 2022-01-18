from typing import List
import telebot


class Footer():

    def __forwarded_from(self, title: str) -> str:
        return f"\nForwarded from {title}"


    def __posted_in(self, name: str) -> str:
        return f"\r\rPosted in https://t.me/{name}"


    def __make_text(self, final_text: str, message: telebot.types.Message, character_limit: int) -> List:
        if message.chat.username:
            final_text += self.__posted_in(message.chat.username)
        else:
            final_text += self.__posted_in(message.chat.title)

        if message.forward_from_chat:
            final_text += self.__forwarded_from(message.forward_from_chat.title)

        if len(final_text) <= character_limit:
            return [final_text]
        else:
            return [(final_text[i:i+character_limit])
                                for i in range(0, len(final_text), character_limit)]


    def text(self, message: telebot.types.Message, character_limit: int) -> List:
        if not message.text:
            message.text = ""
        final_text: str = message.text # type: ignore
        return self.__make_text(final_text, message, character_limit)


    def caption(self, message: telebot.types.Message, character_limit: int) -> List:
        if not message.caption:
            message.caption = ""
        final_text: str = message.caption # type: ignore
        return self.__make_text(final_text, message, character_limit)
