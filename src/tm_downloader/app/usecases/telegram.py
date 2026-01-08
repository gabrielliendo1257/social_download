import logging
from dataclasses import dataclass
from typing import Callable, Coroutine, List

from tm_downloader.domain.models.media import MediaBase
from tm_downloader.domain.models.usecases import AsyncBaseUseCases
from tm_downloader.infrastructure.telegram import TelegramActions
from tm_downloader.utils.tm_client import parse_telegram_url

log = logging.getLogger(__name__)


class TelegramVideoDownloader(AsyncBaseUseCases):

    def __init__(
            self,
            path_to_save: str = None,
            url_media: str = None,
            progress_callback: Callable = None,
            telegram_actions: TelegramActions = None
    ):
        self.url_media = url_media
        self.path_to_save = path_to_save
        self.__progress_callback = progress_callback
        self.__telegram_actions = telegram_actions

    async def execute(self) -> Coroutine:
        return await self.__telegram_actions.download_video(
            self.url_media,
            progress_callback=self.__progress_callback
        )


class TelegramGetInformationMedia(AsyncBaseUseCases):
    def __init__(self, url_media: str, telegram_actions: TelegramActions):
        self.url_media = url_media
        self.__telegram_actions = telegram_actions

    async def execute(self) -> Coroutine:
        return await self.__telegram_actions.get_information_video(self.url_media)


class TelegramGetInformationFromUrlPattern(AsyncBaseUseCases):

    def __init__(self, url_pattern: str, telegram_actions: TelegramActions):
        self.__telegram_actions = telegram_actions

        self.__url_pattern = url_pattern

        self.__url_ids_start, self.__url_ids_end, self.__channel = self.parse_url_pattern()
        log.info(f"Url ids start: {self.__url_ids_start}, end: {self.__url_ids_end}, channel: {self.__channel}")

    def parse_url_pattern(self):
        split_url = self.__url_pattern.split("/")

        ids_message = split_url[-1].split("-")
        ids_start = int(ids_message[0])
        ids_end = int(ids_message[1])

        channel = parse_telegram_url(self.__url_pattern.split("-")[0]).chat_id

        return ids_start, ids_end, channel

    async def execute(self) -> List[MediaBase]:
        messages = []
        async for message in self.__telegram_actions.iter_messages_for_rango(
            self.__channel,
            start=self.__url_ids_start,
            end=self.__url_ids_end,
        ):
            messages.append(message)

        log.info(f"Message count: {len(messages)}")
        log.info(f"Message: {messages[0]}")
        return messages

class SaveMessageOnPersonalVault(AsyncBaseUseCases):
    def __init__(self, telegram_actions: TelegramActions):
        self.__telegram_actions = telegram_actions

    # TODO Enviar mensage o mensages perzonalidos hacia telegram, vault personal
    async def execute(self):
        await self.__telegram_actions.save_on_personal_vault()

class ForwardMessage(AsyncBaseUseCases):
    def __init__(self, chat_id: int, messages, telegram_actions: TelegramActions):
        self.__telegram_action = telegram_actions
        self.__chat_id = chat_id
        self.__messages = messages

    async def execute(self):
        await self.__telegram_action.forward_messages(chat_id=self.__chat_id, messages=self.__messages)


@dataclass
class TelegramUseCases:
    get_media_information = TelegramGetInformationMedia
    download_media = TelegramVideoDownloader
    get_information_from_url_pattern = TelegramGetInformationFromUrlPattern
    save_on_personal_vault = SaveMessageOnPersonalVault # TODO
    forward_message = ForwardMessage # TODO
