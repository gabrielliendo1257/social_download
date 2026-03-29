import logging
import re

from telethon import TelegramClient
from telethon.tl.types import Message

from tm_downloader.domain.model import (
    DownloadItem,
    DownloadJob,
    LinkType,
    BaseService,
    MessageViewModel,
)
from tm_downloader.domain.queue import DownloadQueue
from tm_downloader.utils.url import parse_telegram_url


def to_view_model(item: ..., *args, **kwargs):
    if item.file:
        size = item.file.size
    else:
        size = None

    return MessageViewModel(
        date=item.date, size=size, id_message=item.id, *args, **kwargs
    )


class TelegramService(BaseService):

    def __init__(self, client: TelegramClient, event=None) -> None:
        self.client = client
        self.download_queue = DownloadQueue()
        self.NUM_CONSUMERS = 3
        self.event = event

    async def download(self, item: DownloadItem, *args, **kwargs) -> str:
        assert isinstance(item.message, Message)
        return str(await self.client.download_media(item.message, *args, **kwargs))

    async def request_information_range(self, job: DownloadJob, **kwargs):
        result_parser = parse_telegram_url(job.url)

        if result_parser is None:
            raise Exception("Parser failed.")

        if result_parser.link_type != LinkType.RANGE:
            raise Exception("Not url range recognition.")

        base_url = re.sub(r"/\d+(-\d+)?$", "/", job.url)
        assert base_url != "", "base_url is empty."

        reply_to = None
        if len(result_parser.groups) == 4:
            reply_to = int(result_parser.groups[-3])

        channel = str(result_parser.groups[0])
        try:
            channel = int("-100" + channel)
        except ValueError:
            pass

        ids_start = int(result_parser.groups[-2])
        ids_end = int(result_parser.groups[-1])

        logging.info(
            f"Iterating messages between {ids_start} and {ids_end} and channel {channel}"
        )
        async for msg in self.client.iter_messages(
            channel, min_id=ids_start - 1, max_id=ids_end + 1, **kwargs
        ):
            logging.debug(f"Message from Telegram: {msg}")
            url = base_url + str(msg.id)
            yield DownloadItem(data=to_view_model(msg, url=url), job=job, message=msg)

    async def request_information(self, job: DownloadJob):
        result_parser = parse_telegram_url(job.url)
        if result_parser is None:
            raise Exception("Parser error.")

        if result_parser.link_type == LinkType.RANGE:
            logging.info("Range url detect.")
            return self.request_information_range(job)
        else:
            logging.info("Unit url detect")
            channel = str(result_parser.groups[0])
            id_message = int(result_parser.groups[-1])
            try:
                channel = int("-100" + channel)
            except ValueError:
                pass

            message = await self.client.get_messages(channel, ids=id_message)

            if message is None:
                logging.warning("Message from telegram is None")
                return None
            assert isinstance(message, Message), "message not is instance of Message"
            return DownloadItem(
                data=to_view_model(message, url=job.url), job=job, message=message
            )


class XService(BaseService): ...
