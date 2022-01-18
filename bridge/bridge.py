from dataclasses import dataclass

import mimetypes
import time
import mastodon
import telebot

from typing import List, Optional

from bridge import logger
from bridge.exceptions import MastodonError
from bridge.helper import Footer


@dataclass
class Bridge():
    _telegram: telebot.TeleBot
    _mastodon: mastodon.Mastodon
    mastodon_visibility: str
    mastodon_character_limit: int
    footer_helper: Footer = Footer()

    @property
    def telegram(self) -> telebot.TeleBot:
        return self._telegram


    @property
    def mastodon(self) -> mastodon.Mastodon:
        return self._mastodon


    def telegram_ok(self) -> bool:
        self._telegram.get_me()
        return True


    def mastodon_ok(self) -> bool:
        try:
            self._mastodon.me()
            return True
        except Exception as e:
            logger.exception(e)
            return False
        # except mastodon.MastodonNetworkError:
        #     return False
        # except mastodon.MastodonIllegalArgumentError:
        #     return False
        # except mastodon.MastodonRatelimitError:
        #     return False
        # except mastodon.MastodonUnauthorizedError:
        #     return False
        # except mastodon.MastodonInternalServerError:
        #     return False
        # except mastodon.MastodonBadGatewayError:
        #     return False
        # except mastodon.MastodonServiceUnavailableError:
        #     return False
        # except mastodon.MastodonGatewayTimeoutError:
        #     return False
        # except mastodon.MastodonServerError:
        #     return False
        # except Exception:
        #     # Generic exception, raised when access denied
        #     return False


    def __post_init__(self) -> None:
        '''
        Here we check if both instances are configured properly.
        '''
        self.telegram_ok()
        self.mastodon_ok()

        if self.mastodon_visibility not in ['direct', 'private', 'unlisted', 'public']:
            raise MastodonError('Mastodon visibility string is invalid.'
                                '\nMake sure MASTODON_VISIBILITY= in `.env` file'
                                'is either one of these:\n'
                                '   direct\n'
                                '   private\n'
                                '   unlisted\n'
                                '   public\n')
        if self.mastodon_character_limit <= 0:
            raise MastodonError('Mastodon character limit cannot be 0 or less.')


    def __send_status(self, text: List[str], media: Optional[str | bytes], mime: Optional[str]) -> None:
        recent_post = self.mastodon.status_post(
            status=text[0],
            media_ids=self.mastodon.media_post(media, mime_type=mime),
            visibility=self.mastodon_visibility
        )
        for t in text[1:]:
            time.sleep(1)
            current_post = self.mastodon.status_post(
                status=t,
                visibility=self.mastodon_visibility,
                in_reply_to_id=recent_post.get('id'), # type: ignore
            )
            recent_post = current_post


    def __prepare_media(self, fileID: str, caption: List[str]):
        info: telebot.types.File = self.telegram.get_file(fileID)
        mime, _ = mimetypes.guess_type(info.file_path)
        if not mime:
            logger.error(f"No mime type can be guessed for {info.file_id} ({info.file_path})")
            logger.info(f"Trying to save file into /tmp/{info.file_id}")
            path: str = ''.join(["/tmp/", info.file_path])
            file: bytes = self.telegram.download_file(info.file_path)
            with open(path, "wb") as f:
                f.write(file)
            self.__send_status(caption, media=path, mime=None)
        else:
            file: bytes = self.telegram.download_file(info.file_path)
            self.__send_status(caption, media=file, mime=mime)


    def channel_post_photo(self, message: telebot.types.Message) -> None:
        '''
        NOTE: telebot passes only one image at a time.
            There might be a way to gather all images in one post
            and send them immediately.
            But i'm at a loss here
        '''
        if not message.photo: return
        caption = self.footer_helper.caption(message, self.mastodon_character_limit)
        fileID = message.photo[-1].file_id
        self.__prepare_media(fileID, caption)


    def channel_post_video(self, message: telebot.types.Message) -> None:
        if not message.video: return
        caption = self.footer_helper.caption(message, self.mastodon_character_limit)
        fileID = message.video.file_id
        self.__prepare_media(fileID, caption)


    def channel_post_text(self, message: telebot.types.Message) -> None:
        status_text = self.footer_helper.text(message, self.mastodon_character_limit)
        self.__send_status(status_text, media=None, mime=None)
