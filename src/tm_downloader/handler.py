from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Union

from telethon import TelegramClient

from tm_downloader.utils.url import parse_telegram_url

Client = Union[TelegramClient]


@dataclass
class Request:
    url: str


@dataclass
class DownloadContext:
    client: Client
    output_dir: Path
    retries: int = 3
    timeout: int = 30


class Handler(ABC):

    @abstractmethod
    def set_next(self, handler: Handler):
        raise NotImplementedError()

    @abstractmethod
    def handle(self, request: Request) -> DownloadContext | None:
        raise NotImplementedError()


class AbstractHandler(Handler):

    __platform_handler: Handler | None = None

    def set_next(self, handler: Handler):
        self.__platform_handler = handler

    def handle(self, request: Request) -> DownloadContext | None:
        if self.__platform_handler:
            return self.__platform_handler.handle()
        else:
            return None


class TelegramHandler(AbstractHandler):

    def handle(self, request: Request) -> DownloadContext | None:
        if parse_telegram_url(request.url) is None:
            return None

        return
