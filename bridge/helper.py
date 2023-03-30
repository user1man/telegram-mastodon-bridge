from typing import List
import telebot


class Footer():

    def __make_text(self, final_text: str, message: telebot.types.Message, character_limit: int) -> List[str]:

        if len(final_text) <= character_limit:
            return [final_text]
        else:
            return [(final_text[i:i+character_limit])
                                for i in range(0, len(final_text), character_limit)]


    def text(self, message: telebot.types.Message, character_limit: int) -> List[str]:
        if not message.text:
            message.text = ""
        final_text: str = message.text # type: ignore
        return self.__make_text(final_text, message, character_limit)


    def caption(self, message: telebot.types.Message, character_limit: int) -> List[str]:
        if not message.caption:
            message.caption = ""
        final_text: str = message.caption # type: ignore
        return self.__make_text(final_text, message, character_limit)
