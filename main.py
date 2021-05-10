'''
|--------------------------------------------------------------|
|                 Telegram to Mastodon bridge                  |
|--------------------------------------------------------------|

Telegram bot API documentation:
    https://pypi.org/project/pyTelegramBotAPI/
Mastodon bot API documentation:
    https://mastodonpy.readthedocs.io/en/stable/

TODO:
           - Generally nice and friendly installation?
    [MT]   - Handle character limit exceptions
    [MT]   - Handle all other exceptions
    [TG]   - Try parsing md or html instead of None | handle links
    [TG-MT]- Handle image reposts
'''
import os
import logging
import telebot
from mastodon import Mastodon

logging.basicConfig(format='%(asctime)s: %(levelname)s %(name)s | %(message)s',
                    level=logging.INFO)

if (os.path.isfile("credentials.py") == False):
    logging.info("No credentials found")
    telegram_token = input("Enter your telegram bot token: ")
    mastodon_token = input("Enter your mastodon bot token: ")
    mastodon_instance = input(
        "Enter url to instance where your bot is located(https://example.social): ")
    with open("credentials.py", "w") as creds:
        creds.write(f"telegram_token = '{telegram_token}'" +
                    "\n" + f"mastodon_token = '{mastodon_token}'" +
                    "\n" + f"mastodon_instance = '{mastodon_instance}'")
else:
    logging.info("Running normally")
    from credentials import mastodon_token, telegram_token, mastodon_instance

'''
Bots
'''
mastodon_bot = Mastodon(access_token=mastodon_token,
                        api_base_url=mastodon_instance)  # i.e.https://mastodon.social

# Posts a single test message --> toot variable stores returned value
# toot = mastodon_bot.status_post("Test message")


# Telegram
# parse mode can be either HTML or MARKDOWN
bot = telebot.TeleBot(telegram_token, parse_mode="MARKDOWN")


'''
Posting
'''


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


bot.polling()
