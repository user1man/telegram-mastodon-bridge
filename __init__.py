import os
import logging
from dotenv import load_dotenv

import telebot

# We load the env vars from a .env file
load_dotenv()
mastodon_token: str = str(os.getenv('MASTODON_TOKEN'))
telegram_token: str = str(os.getenv('TELEGRAM_TOKEN'))
mastodon_instance: str = str(os.getenv('MASTODON_INSTANCE'))
mastodon_visibility: str = str(os.getenv('MASTODON_VISIBILITY'))
character_limit: int = int(os.getenv('MASTODON_CHARACTER_LIMIT')) # type: ignore

logging.basicConfig(
    format='%(asctime)s: %(levelname)s %(name)s | %(message)s',
    level=logging.INFO
)

telebot.logger.setLevel(logging.INFO)
logger = logging.getLogger("Main")
