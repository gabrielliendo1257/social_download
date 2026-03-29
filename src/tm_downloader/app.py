from __future__ import annotations
import logging

from tm_downloader.domain.context import (
    AbstractPlatformResolveContext,
    DefaultContext,
    TelegramContext,
)
from tm_downloader.domain.manager import DownloadManager
from tm_downloader.domain.model import AppContext, Client
from tm_downloader.domain.queue import DownloadQueue
from tm_downloader.telegram.auth_manager import AuthManager
from tm_downloader.telegram.runtime import Runtime


async def init_core():
    AppContext.queue = DownloadQueue()


async def init_clients():
    auth = AuthManager()
    telegram_client = await auth.connecting()
    AppContext.clients[Client.telegram] = telegram_client


def init_resolvers():
    default_context = DefaultContext()
    abstract = AbstractPlatformResolveContext(wrapper=default_context)
    telegram_context = TelegramContext(abstract)

    AppContext.resolver = telegram_context


class SystemDownload:
    def __init__(self, download_manager: DownloadManager, queue: DownloadQueue):
        self.download_manager = download_manager
        self.queue = queue

    def add(self, url: str):
        job = self.download_manager.crete_job(url=url)


class AppBootstrap:

    def __init__(self) -> None:
        self.runtime = Runtime()
        self.runtime.start()
        self.loop = self.runtime.loop

    async def start(self):
        logging.info("Started application")
        await init_core()
        await init_clients()

        init_resolvers()

        AppContext.loop = self.loop
