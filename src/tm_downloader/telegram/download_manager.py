from __future__ import annotations

import logging
import re
import uuid
from typing import Dict

from telethon import TelegramClient
from telethon.tl.types import Message

from tm_downloader.domain.model import DownloadJob, DownloadState, LinkType
from tm_downloader.domain.queue import DownloadQueue
from tm_downloader.utils.url import parse_telegram_url


class DownloadManager:

    def __init__(self, client: TelegramClient, event=None):
        self.client = client
        self.jobs: Dict[str, DownloadJob] = {}
        self.event = event
        self.download_queue = DownloadQueue()
        self.NUM_CONSUMERS = 3

    def change_job_state(self, id_job: str, state: DownloadState):
        download_job = self.jobs[id_job]
        assert download_job is not None, "Job not found."
        download_job.transition(new_state=state)

    def crete_job(self, url: str) -> DownloadJob:
        job = DownloadJob(url, str(uuid.uuid4()))
        self.jobs[job.id_job] = job

        return job

    def delete_job(self, id_job: str) -> DownloadJob:
        return self.jobs.pop(id_job)

    def resume_job(self, id_job: str) -> DownloadJob | None:
        if self.can_activate_job(id_job):
            return self.jobs[id_job]
        return None

    def can_activate_job(self, id_job: str) -> bool:
        job = self.jobs.get(id_job)
        assert job is not None, "job is None"
        if job.error:
            return False
        return True

    async def download(self, url: str, **kwargs):
        message = await self.request_information(url)
        if not isinstance(message, Message):
            raise Exception("Message type not supported.")
        return await self.client.download_media(message, **kwargs)

    async def download_range(self, url_range: str) -> None:
        generator = self.request_information_range(url_range)

        async for message in generator:
            await self.download_queue.queue.put(message)

        for _ in range(self.NUM_CONSUMERS):
            await self.download_queue.queue.put(None)

    async def request_information_range(self, url_range: str):
        result_parser = parse_telegram_url(url_range)

        if result_parser is None:
            raise Exception("Parser failed.")

        if result_parser.link_type != LinkType.RANGE:
            raise Exception("Not url range recognition.")

        base_url = re.sub(r"/\d+(-\d+)?$", "/", url_range)
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

        async for msg in self._request_information_range(
            channel, ids_start, ids_end, reply_to=reply_to
        ):
            url = base_url + str(msg.id)
            setattr(msg, "current_url", url)
            yield msg

    async def _request_information_range(
        self, channel: str | int, ids_start: int, ids_end: int, tg_filter=None, **kwargs
    ):
        logging.info(
            f"Iterating messages between {ids_start} and {ids_end} and channel {channel} and filter {tg_filter}"
        )
        async for message in self.client.iter_messages(
            channel, min_id=ids_start - 1, max_id=ids_end + 1, **kwargs
        ):
            logging.debug(f"Message from Telegram: {message}")

            yield message

    async def request_information(self, url: str):
        result_parser = parse_telegram_url(url)
        if result_parser is None:
            raise Exception("Parser error.")

        if result_parser.link_type == LinkType.RANGE:
            raise Exception("Not range supported.")

        channel = str(result_parser.groups[0])
        id_message = int(result_parser.groups[-1])
        try:
            channel = int("-100" + channel)
        except ValueError:
            pass

        message = await self._request_information(channel, id_message)
        setattr(message, "current_url", url)

        return message

    async def _request_information(self, channel: str | int, id_message: int):
        return await self.client.get_messages(channel, ids=id_message)
