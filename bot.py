#!/bin/env python
'''
|--------------------------------------------------------------|
|                 Telegram to Mastodon bridge                  |
|--------------------------------------------------------------|

Telegram bot API documentation:
    https://pypi.org/project/pyTelegramBotAPI/
Mastodon bot API documentation:
    https://mastodonpy.readthedocs.io/en/stable/

TODO:
    - Handle character limit exceptions in image and video posts
    - Use case statements in python 3.10 for footer function? maybe other ones?
'''
import os
import logging
import time
import telebot
from mastodon import Mastodon
from dotenv import load_dotenv

# We load the env vars from a .env file
load_dotenv()

character_limit = 500

'''
Basic setup
'''
logging.basicConfig(format='%(asctime)s: %(levelname)s %(name)s | %(message)s', level=logging.INFO)
# logger = telebot.logger.setLevel(logging.INFO)

mastodon_token = os.getenv('MASTODON_TOKEN')
telegram_token = os.getenv('TELEGRAM_TOKEN')
mastodon_instance = os.getenv('MASTODON_INSTANCE')
mastodon_visibility = os.getenv('MASTODON_VISIBILITY')


'''
Bots
'''
# Mastodon
mastodon_bot = Mastodon(
    access_token=mastodon_token,
    api_base_url=mastodon_instance # i.e.https://mastodon.social
)

# Telegram
# parse mode can be either HTML or MARKDOWN
bot = telebot.TeleBot(telegram_token, parse_mode="HTML")


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
    if message.forward_from_chat != None and message.chat.username != None:
        final_text = message.text + "\r\rPosted in https://t.me/" + message.chat.username + \
            f"\nForwarded from {message.forward_from_chat.title}"
    elif message.forward_from_chat != None and message.chat.username == None:
        final_text = message.text + "\r\rPosted in " + message.chat.title + \
            f"\nForwarded from {message.forward_from_chat.title}"
    elif message.chat.username != None:
        final_text = message.text + "\r\rPosted in https://t.me/" + message.chat.username
    elif message.chat.username == None:
        final_text = message.text + "\r\rPosted in " + message.chat.title
    else:
        final_text = message.text

    if len(final_text) < character_limit:
        return final_text
    else:
        final_text_split = [(final_text[i:i+character_limit])
                            for i in range(0, len(final_text), character_limit)]
        return final_text_split


def footer_image(message):
    if message.forward_from_chat != None:
        forward = f"\nForwarded from {message.forward_from_chat.title}"
        try:
            caption = message.json['caption']
            if message.chat.username != None:
                final_text = caption + "\r\rPosted in https://t.me/" + message.chat.username + forward
                return final_text
            else:
                final_text = caption + "\r\rPosted in " + message.chat.title + forward
                return final_text
        except:
            if message.chat.username != None:
                final_text = "Posted in https://t.me/" + message.chat.username + forward
                return final_text
            else:
                final_text = "Posted in " + message.chat.title + forward
                return final_text
    else:
        try:
            caption = message.json['caption']
            if message.chat.username != None:
                final_text = caption + "\r\rPosted in https://t.me/" + message.chat.username
                return final_text
            else:
                final_text = caption + "\r\rPosted in " + message.chat.title
                return final_text
        except KeyError:
            if message.chat.username != None:
                final_text = "Posted in https://t.me/" + message.chat.username
                return final_text
            else:
                final_text = "Posted in " + message.chat.title
                return final_text


'''
Posting
'''


@bot.channel_post_handler(content_types=["photo"])
def get_image(message):
    logging.info(f"New {message.content_type}")
    caption = footer_image(message)

    fileID = message.photo[-1].file_id
    logging.info(f"Photo ID {fileID}")

    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("tmp_img", "wb") as tmp_image:
        tmp_image.write(downloaded_file)

    media_id = mastodon_bot.media_post("tmp_img")
    posted = mastodon_bot.status_post(status=caption, media_ids=media_id, visibility=mastodon_visibility)
    logging.info(f"Posted: {posted['uri']}")


@bot.channel_post_handler(content_types=["video"])
def get_video(message):
    logging.info(f"New {message.content_type}")
    caption = footer_image(message)

    fileID = message.video.file_id
    logging.info(f"Video ID {fileID}")

    file_info = bot.get_file(fileID)
    downloaded_file = bot.download_file(file_info.file_path)
    with open("tmp_video", "wb") as tmp_video:
        tmp_video.write(downloaded_file)

    media_id = mastodon_bot.media_post("tmp_video", mime_type=message.video.mime_type)
    posted = mastodon_bot.status_post(status=caption, media_ids=media_id, visibility=mastodon_visibility)
    logging.info(f"Posted: {posted['uri']}")


# repost text messages
@bot.channel_post_handler(content_types=["text"])
def get_text(message):
    logging.info(f"New {message.content_type}")
    status_text = footer_text(message)

    if type(status_text) == list:
        recent_post = mastodon_bot.status_post(status=status_text[0], visibility=mastodon_visibility)

        for i in status_text[1:]:
            time.sleep(1)
            this_recent_post = mastodon_bot.status_post(
                status=i,
                visibility=mastodon_visibility,
                in_reply_to_id=recent_post.get('id')
            )
            recent_post = this_recent_post
    else:
        mastodon_bot.status_post(status=status_text, visibility=mastodon_visibility)


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
