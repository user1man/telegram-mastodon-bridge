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
logger = telebot.logger.setLevel(logging.INFO)

# check if credentials exist, create if not
if (os.path.isfile("credentials.py") == False):
    logging.info("No credentials found")
    telegram_token = input("Enter your telegram bot token: ")
    mastodon_token = input("Enter your mastodon bot token: ")
    mastodon_instance = input(
        "Enter url to instance where your bot is located(https://example.social): ")
    with open("credentials.py", "w") as creds:
        creds.write(
            f"telegram_token = '{telegram_token}'\nmastodon_token = '{mastodon_token}'\nmastodon_instance = '{mastodon_instance}'")
else:
    try:
        from credentials import mastodon_token, telegram_token, mastodon_instance
        logging.info("Running normally")
    except ImportError:
        logging.fatal(
            "Something is wrong with credentials, delete credentials.py and try again")
        exit(1)
'''
Bots
'''
# Mastodon
mastodon_bot = Mastodon(access_token=mastodon_token,
                        api_base_url=mastodon_instance)  # i.e.https://mastodon.social

# See if the bot can be accessed
try:
    ping_mastodon = mastodon_bot.me()["username"]
    logging.info(f"Running mastodon as {ping_mastodon}")
except:
    logging.fatal("Failed to verify mastodon access token.")
    exit(1)

# Telegram
# parse mode can be either HTML or MARKDOWN
bot = telebot.TeleBot(telegram_token, parse_mode="MARKDOWN")

# See if the bot can be accessed
try:
    ping_telegram = bot.get_me()
    logging.info(f"Running telegram as {ping_telegram.username}")
except:
    logging.fatal("Failed to verify telegram token.")
    exit(1)


'''
Posting
'''


# Repost 1 image (mastodon allows up to 4 in one post)
# This actually just posts multiple images in separate statuses and random order
@bot.channel_post_handler(content_types=["photo"])
def get_image(message):
    logging.debug(f"New message: {message}")
    try:
        caption = message.json['caption']
        logging.info(
            f"New photo: {message.photo}\nCaption reads {message.json['caption']}")
    except KeyError:
        caption = None
        logging.info(f"New photo: {message.photo}\nNo caption")

    fileID = message.photo[-1].file_id
    logging.info(f"Photo ID {fileID}")

    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("tmp.jpg", "wb") as tmp_image:
        tmp_image.write(downloaded_file)
        logging.info(f"Downloaded {file_info.file_path}")

    media_id = mastodon_bot.media_post("tmp.jpg")
    posted = mastodon_bot.status_post(
        status=caption, media_ids=media_id, visibility="direct")
    logging.info(f"Posted: {posted['uri']}")


@bot.channel_post_handler(content_types=["text"])
def get_text(message):
    logging.debug(f"New telegram post: {message}")
    # Get text from telegram
    status_text = message.text
    logging.info(f"Status text: {status_text}")
    # Post final content https://mastodonpy.readthedocs.io/en/stable/#writing-data-statuses
    posted = mastodon_bot.status_post(
        status=status_text, media_ids=None, visibility="direct")
    logging.info(f"Posted: {posted['uri']}")


try:
    bot.polling(interval=3)
except KeyboardInterrupt:
    exit(0)
