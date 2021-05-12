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
'''
import os
import logging
import telebot
from mastodon import Mastodon


# visibility of mastodon posts: direct, unlisted, public, etc.
mastodon_visibility = "direct"

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
bot = telebot.TeleBot(telegram_token, parse_mode="HTML")

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


# Returns message text + channel name or title(if private)
def footer(message, image=False):
    if not image and message.forward_from_chat == None:
        print("!!! message is text and is not forwarded")
        try:
            print("!!! Trying text + caption w/ username")
            message_to_status = message.text + "\r\r@" + message.chat.username
            return message_to_status
        except TypeError:
            print("!!! Trying text + caption w/ title")
            message_to_status = message.text + "\r\r" + message.chat.title
            return message_to_status
    elif not image:
        print("!!! message is text but is forwarded ")
        try:
            print("!!! Trying text + caption w/ username + forwarded from title")
            message_to_status = message.text + "\r\r@" + message.chat.username + \
                f"\nForwarded from {message.json.forward_from_chat.title}"
            return message_to_status
        except TypeError:
            print("!!! Trying text + caption w/ username + forwarded from title")
            message_to_status = message.text + "\r\r" + message.chat.title + \
                f"Forwarded from {message.json['forward_from_chat']['username']}"
            return message_to_status
    elif image:
        try:
            print("!!! Trying image + caption w/ username")
            message_to_status = message.json['caption'] + \
                "\r\r" + message.chat.username
            return message_to_status
        except TypeError:
            print("!!! Trying image + username")
            message_to_status = message.chat.username
            return message_to_status
        except KeyError:
            print("!!! Trying image + title")
            message_to_status = message.chat.title
            return message_to_status


# Repost 1 image (mastodon allows up to 4 in one post)
# This actually just posts multiple images in separate statuses and random order
@bot.channel_post_handler(content_types=["photo"])
def get_image(message):
    logging.info(f"New message: {message}")
    caption = footer(message, image=True)

    fileID = message.photo[-1].file_id
    logging.info(f"Photo ID {fileID}")

    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("tmp.jpg", "wb") as tmp_image:
        tmp_image.write(downloaded_file)

    media_id = mastodon_bot.media_post("tmp.jpg")
    posted = mastodon_bot.status_post(
        status=caption, media_ids=media_id, visibility=mastodon_visibility)
    logging.info(f"Posted: {posted['uri']}")


@bot.channel_post_handler(content_types=["video"])
def get_video(message):
    logging.info(message)
    caption = footer(message, image=True)

    fileID = message.video.file_id
    logging.info(f"Video ID {fileID}")

    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("tmp_video", "wb") as tmp_video:
        tmp_video.write(downloaded_file)

    media_id = mastodon_bot.media_post(
        "tmp_video", mime_type=message.video.mime_type)
    posted = mastodon_bot.status_post(
        status=caption, media_ids=media_id, visibility=mastodon_visibility)
    logging.info(f"Posted: {posted['uri']}")


# repost text messages
@bot.channel_post_handler(content_types=["text"])
def get_text(message):
    logging.info(f"New telegram post: {message}")
    # Get text from telegram
    status_text = footer(message, image=False)
    logging.info(f"Status text: {status_text}")
    # Post final content https://mastodonpy.readthedocs.io/en/stable/#writing-data-statuses
    # For more details on how to solve character limits https://mastodonpy.readthedocs.io/en/stable/#mastodon.Mastodon.status_reply
    posted = mastodon_bot.status_post(
        status=status_text, visibility=mastodon_visibility)
    logging.info(f"Posted: {posted['uri']}")


try:
    bot.polling(interval=3)
except KeyboardInterrupt:
    exit(0)
