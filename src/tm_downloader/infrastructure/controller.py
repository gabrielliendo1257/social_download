import asyncio
import logging
import os
from typing import Callable, List

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.types import Message

from tm_downloader.app.usecases.telegram import TelegramUseCases
from tm_downloader.domain.events.manager import TelegramEventBus
from tm_downloader.domain.models.media import MediaBase, AsyncLoopRunner
from tm_downloader.infrastructure.telegram import TelegramActions

load_dotenv()

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
telegram_session = os.getenv("TG_SESSION")

log = logging.getLogger(__name__)


def _parser_message(message: Message, url_base: str | None = None) -> MediaBase:
    size = None
    if getattr(message, "video", None):
        size = message.video.size
    elif getattr(message, "photo", None):
        size = message.photo.sizes[2].size
    elif getattr(message, "document", None):
        size = message.document.size

    url_base = url_base + "/" + str(message.id)
    url_split = url_base.split("/")
    if str(url_split[-1]) == str(url_split[-2]):
        url_split.pop()
        url_base = "/".join(url_split)

    log.info(f"Url base: {url_base}, message_id: {message.id}, size: {size}")

    return MediaBase(
        uri=url_base,
        id=message.id,
        date=message.date,
        caption=message.message,
        size=size
    )


class TelegramController:
    def __init__(self, event_bus: TelegramEventBus):
        self._telegram_use_cases = TelegramUseCases()
        self.__event_bus = event_bus
        self.__loop_runner = AsyncLoopRunner()
        self.loop = self.__loop_runner.loop

        log.debug("LOOP: ", self.loop)
        self.__telegram_actions = None

        # asyncio.run_coroutine_threadsafe(
        #    monitor_tasks(),
        #    loop=self.loop
        # )

    @property
    def telegram_actions(self) -> TelegramActions:
        return self.__telegram_actions

    @property
    def event_bus(self) -> TelegramEventBus:
        return self.__event_bus

    @property
    def telegram_use_cases(self) -> TelegramUseCases:
        return self._telegram_use_cases

    async def create_client(
            self,
            on_success: Callable[[], None],
            on_error: Callable[[], None]
    ) -> None:
        try:
            client = TelegramClient(
                "session",
                int(api_id),
                api_hash,
                loop=self.loop
            )
            await client.connect()
            self.__telegram_actions = TelegramActions(telegram_client=client)
            print("Telegram client connected: ", self.__telegram_actions)
            on_success()
        except Exception as e:
            print("ERROR: ", e)
            on_error()

    def download_video(self, url_media: str, progress_callback: Callable):
        return asyncio.run_coroutine_threadsafe(
            self._telegram_use_cases.download_media(
                url_media=url_media,
                progress_callback=progress_callback,
                telegram_actions=self.__telegram_actions
            ).execute(),
            loop=self.loop
        )

    def get_information_video(self, url_video: str, on_success: Callable[[MediaBase], None]) -> None:
        async def task():
            message = await self._telegram_use_cases.get_media_information(
                url_media=url_video,
                telegram_actions=self.__telegram_actions
            ).execute()
            return _parser_message(message, url_video)

        def done(f):
            result = f.result()
            on_success(result)

        future = asyncio.run_coroutine_threadsafe(task(), self.loop)
        future.add_done_callback(done)

    def get_information_from_url_pattern(self, url_pattern: str) -> List[MediaBase]:
        split_url = url_pattern.split("/")
        split_url.remove(split_url[-1])

        url_base = "/".join(split_url)

        future_messages = asyncio.run_coroutine_threadsafe(
            self._telegram_use_cases.get_information_from_url_pattern(
                url_pattern=url_pattern,
                telegram_actions=self.__telegram_actions
            ).execute(),
            loop=self.loop
        )

        medias = []
        for message in future_messages.result():
            media = _parser_message(message=message, url_base=url_base)
            medias.append(media)

        return medias

    # TODO Metodo de reenvio a los mensages personales
    def save_message_on_personal_vault(self):
        asyncio.run_coroutine_threadsafe(
            self._telegram_use_cases.save_on_personal_vault(
                telegram_actions=self.__telegram_actions
            ).execute(),
            loop=self.loop
        )

    # TODO Implementar UI
    def forward_message_on_personal_vault(self, chat_id: int, messages):
        asyncio.run_coroutine_threadsafe(
            self._telegram_use_cases.forward_message(
                chat_id=chat_id,
                messages=messages,
                telegram_actions=self.__telegram_actions
            ).execute(),
            loop=self.loop
        )

class TwitterController:
    ...