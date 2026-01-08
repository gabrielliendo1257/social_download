import logging
import os
from typing import Callable, Union, TypeAlias, List

from dotenv import load_dotenv
from flet.core.control import Control
from telethon import TelegramClient
from telethon.tl.types import (
    InputMessagesFilterVideo,
    InputMessagesFilterPhotos,
    InputMessagesFilterDocument,
    InputMessagesFilterVoice,
    InputMessagesFilterUrl,
    InputMessagesFilterGif,
    InputMessagesFilterMusic, InputMessageID, Message,
)

from tm_downloader.domain.models.platforms import AbstractPlatform
from tm_downloader.utils.tm_client import parse_telegram_url

load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
telegram_session = os.getenv("TG_SESSION")

log = logging.getLogger(__name__)

TelegramMediaFilter: TypeAlias = Union[
    InputMessagesFilterPhotos,
    InputMessagesFilterVideo,
    InputMessagesFilterDocument,
    InputMessagesFilterVoice,
    InputMessagesFilterUrl,
    InputMessagesFilterGif,
    InputMessagesFilterMusic,
]


class TelegramActions(AbstractPlatform):
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)

        return cls.__instance

    def __init__(
            self,
            func: Callable = None,
            editor: Control = None,
            telegram_client: TelegramClient | None = None,
            *args, **kwargs
    ):
        super().__init__(func, editor, args, kwargs)
        self.__is_authorized = False
        self.__telegram_client = telegram_client
        print("Client: ", telegram_client)

    async def get_information_video(self, url):
        if isinstance(self.__telegram_client, TelegramClient):
            result_parser = parse_telegram_url(url)
            return await self.__telegram_client.get_messages(
                result_parser.chat_id,
                ids=result_parser.message_id
            )

        raise Exception(f"self.__telegram_client is not instance of TelegramClient")

    async def download_video(self, url, progress_callback: Callable):
        path_to_save = None
        if isinstance(self.__telegram_client, TelegramClient):
            result_parser = parse_telegram_url(url)
            log.info(f"Result parser: {result_parser}")
            message_response = await self.__telegram_client.get_messages(
                result_parser.chat_id,
                ids=result_parser.message_id
            )
            path_to_save = await self.__telegram_client.download_media(
                message_response,
                progress_callback=progress_callback
            )

            if path_to_save is None:
                path_to_save = await self.__telegram_client.download_media(
                    message_response,
                    reply_to=result_parser.thread_id,
                    progress_callback=progress_callback
                )

        return path_to_save

    async def iter_messages_for_rango(
            self,
            channel: str,
            start: int,
            end: int,
            tg_filter: TelegramMediaFilter | None = None
    ):
        log.info(f"Iterating messages between {start} and {end} and channel {channel} and filter {tg_filter}")
        async for message in self.__telegram_client.iter_messages(
                channel,
                min_id=start - 1,
                max_id=end,
                filter=tg_filter
        ):
            yield message

    async def save_on_personal_vault(self):
        await self.__telegram_client.send_message("me", "Hola mundo.")

    async def forward_messages(self, chat_id: int, messages: Message | List[Message]):
        await self.__telegram_client.forward_messages("me", messages=messages, from_peer=chat_id)