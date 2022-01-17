#!/bin/env python
import sys
from typing import Callable, Dict
import telebot
import mastodon
from bridge.bridge import Bridge
from bridge.tg_exception_handler import TelegramExceptionHandler
from __init__ import (
    mastodon_token,
    telegram_token,
    mastodon_instance,
    mastodon_visibility,
    character_limit,
    logger,
)


bots = Bridge(
    telebot.TeleBot(
        token=telegram_token,
        exception_handler=TelegramExceptionHandler()
    ),
    mastodon.Mastodon(
        access_token=mastodon_token,
        api_base_url=mastodon_instance
    ),
    mastodon_visibility=mastodon_visibility,
    mastodon_character_limit=character_limit
)


channel_post_handler_table: Dict[str, Callable] = {
    "text": bots.channel_post_text,
    "photo": bots.channel_post_photo,
    "video": bots.channel_post_video,
}


@bots.telegram.channel_post_handler(content_types=["text", "photo", "video"])
def main_channel_post_handler(message: telebot.types.Message) -> None:
    if message.content_type not in channel_post_handler_table.keys():
        logger.warning(f"Unsupported channel content type: {message.content_type}")
        return

    handler = channel_post_handler_table[message.content_type]
    handler(message)


def main() -> int:
    try:
        bots.telegram.polling(interval=5)
    except KeyboardInterrupt:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
