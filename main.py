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
    - Handle character limit exceptions
    - Use case statements in python 3.10 for footer function? maybe other ones?
'''
import os
import logging
import telebot
from mastodon import Mastodon


# visibility of mastodon posts: direct, unlisted, public, etc.
mastodon_visibility = "direct"
character_limit = 500


'''
Basic setup
'''
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

# Telegram
# parse mode can be either HTML or MARKDOWN
bot = telebot.TeleBot(telegram_token, parse_mode="HTML")

# See if the bot can be accessed


def ping_bots():
    try:
        ping_mastodon = mastodon_bot.me()["username"]
        logging.info(f"Running mastodon as {ping_mastodon}")
    except:
        logging.fatal("Failed to verify mastodon access token.")
        exit(1)

    try:
        ping_telegram = bot.get_me()
        logging.info(f"Running telegram as {ping_telegram.username}")
    except:
        logging.fatal("Failed to verify telegram token.")
        exit(1)


'''
Functions
'''


def footer_text(message):
    final_text = ""
    if message.forward_from_chat != None and message.chat.username != None:
        final_text = message.text + "\r\r@" + message.chat.username
    elif message.forward_from_chat != None and message.chat.username == None:
        final_text = message.text + "\r\r" + message.chat.title
    elif message.chat.username != None:
        final_text = message.text + "\r\r@" + message.chat.username
    elif message.chat.username == None:
        final_text = message.text + "\r\r" + message.chat.title
    else:
        final_text = message.text

    if len(final_text) < character_limit:
        return final_text
    else:
        final_text_split = [(final_text[i:i+character_limit])
                            for i in range(0, len(final_text), character_limit)]
        return final_text_split


def footer(message, media=False):
    if not media:
        try:
            message_to_status = message.text + "\r\r@" + message.chat.username + \
                f"\nForwarded from {message.json.forward_from_chat.title}"
            return message_to_status
        except TypeError:
            message_to_status = message.text + "\r\r" + message.chat.title + \
                f"Forwarded from {message.json['forward_from_chat']['username']}"
            return message_to_status
    elif media:
        try:
            message_to_status = message.json['caption'] + \
                "\r\r" + message.chat.username
            return message_to_status
        except KeyError:
            try:
                message_to_status = "@" + message.chat.username
                return message_to_status
            except TypeError:
                message_to_status = message.chat.title
                return message_to_status


'''
Posting
'''


@bot.channel_post_handler(content_types=["photo"])
def get_image(message):
    logging.info(f"New message: {message}")
    caption = footer(message, media=True)

    fileID = message.photo[-1].file_id
    logging.info(f"Photo ID {fileID}")

    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("tmp_img", "wb") as tmp_image:
        tmp_image.write(downloaded_file)

    media_id = mastodon_bot.media_post("tmp_img")
    posted = mastodon_bot.status_post(
        status=caption, media_ids=media_id, visibility=mastodon_visibility)
    logging.info(f"Posted: {posted['uri']}")


@bot.channel_post_handler(content_types=["video"])
def get_video(message):
    logging.info(message)
    caption = footer(message, media=True)

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
    status_text = footer_text(message)

    if type(status_text) == list:
        recent_post = mastodon_bot.status_post(
            status=status_text[0], visibility=mastodon_visibility)

        for i in status_text:
            this_recent_post = mastodon_bot.status_post(
                status=i, visibility=mastodon_visibility, in_reply_to_id=recent_post.get('id'))
            recent_post = this_recent_post
    else:
        print(status_text)
        mastodon_bot.status_post(
            status=status_text, visibility=mastodon_visibility)


'''
Finally run tg polling
'''

try:
    ping_bots()
    bot.polling(interval=5)
except KeyboardInterrupt:
    exit(0)
except:
    logging.error("Something went wrong.")
    ping_bots()
    bot.polling(interval=5)
finally:
    print("\nBye!")
