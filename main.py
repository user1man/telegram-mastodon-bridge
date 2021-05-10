'''
|--------------------------------------------------------------|
|                 Telegram to Mastodon bridge                  |
|--------------------------------------------------------------|

Telegram bot API documentation:
    https://pypi.org/project/pyTelegramBotAPI/
Mastodon bot API documentation:
    https://mastodonpy.readthedocs.io/en/stable/

TODO:
           - Prompt for tokens then write them to a file (no need for cred.py)
           - Generally nice and friendly installation?
    [MT]   - Handle character limit exceptions
    [MT]   - Handle all other exceptions
    [TG]   - Try parsing md or html instead of None
    [TG-MT]- Handle image reposts
'''

import logging
import telebot
from mastodon import Mastodon
from credentials import mastodon_token, telegram_token

logging.basicConfig(format='%(asctime)s: %(levelname)s %(name)s | %(message)s',
                    level=logging.INFO)

'''
Mastodon
'''
mastodon_bot = Mastodon(access_token=mastodon_token,
                        api_base_url="https://mastodon.social")

# Posts a single test message --> toot variable stores returned value
# toot = mastodon_bot.status_post("Test message")

'''
Telegram
'''
# parse mode can be either HTML or MARKDOWN
bot = telebot.TeleBot(telegram_token, parse_mode=None)


# This one gets the channel message and posts it -> to mastodon
@bot.channel_post_handler(content_types=["text", "photo", "video", "audio", "document"])
def get_message(message):
    logging.info(f"New telegram post: {message}")
    # Get text from telegram
    status = message.text
    logging.info(f"Status text: {status}")
    # Get images from telegram
    # +++TODO+++
    # Post images to mastodon https://mastodonpy.readthedocs.io/en/stable/#writing-data-media
    # +++TODO+++
    media_ids = None
    # Post final content https://mastodonpy.readthedocs.io/en/stable/#writing-data-statuses
    posted = mastodon_bot.status_post(
        status=status, media_ids=media_ids, visibility="direct")
    logging.info(f"Posted: {posted}")


# @bot.message_handler(commands=['start', 'help'])
# def send_welcome(message):
#     bot.reply_to(message, "START || HELP: COMMAND NOT SUPPORTED")


# @bot.message_handler(func=lambda m: True)
# def echo_all(message):
#     bot.reply_to(message, message.text)
bot.polling()
