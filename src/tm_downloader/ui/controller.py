import asyncio
import logging
from concurrent.futures import Future
from typing import Any

from telethon.tl.types import Message

from tm_downloader.domain.context import resolve_context
from tm_downloader.domain.model import (
    AbstractUI,
    AppContext,
    Client,
    ContextPlatform,
    DownloadItem,
)
from tm_downloader.telegram.download_manager import DownloadManager
from tm_downloader.utils.url import (
    ParserResult,
    expand_telegram_media_url,
    parse_telegram_url,
)


class DownloadController:

    def __init__(
        self,
        download_manager: DownloadManager,
        ui: AbstractUI | None = None,
        events=None,
    ):
        self.download_manager = download_manager
        self.__events = events
        self.__ui = ui

    def _match_valid_url(self, url: str) -> ParserResult:
        parser_result = parse_telegram_url(url)

        if parser_result is None:
            raise Exception(f"No match url {url}")

        return parser_result

    @resolve_context
    async def request_information(
        self,
        ctx: ContextPlatform | None = None,
        url: str | None = None,
    ):
        assert isinstance(url, str) and url != "", "url is empty or None"
        assert ctx is not None, "context is None"
        assert ctx.service is not None, "service is None"
        return await ctx.service.request_information(
            self.download_manager.crete_job(url)
        )

    @resolve_context
    async def download(
        self,
        ctx: ContextPlatform | None = None,
        item: DownloadItem | None = None,
        *args,
        **kwargs,
    ):
        assert item is not None, "item is None"
        assert ctx is not None, "context is None"
        assert ctx.service is not None, "service is None"
        return await ctx.service.download(item, *args, **kwargs)


if __name__ == "__main__":
    from tm_downloader.app import AppBootstrap

    app_bootstrap: AppBootstrap | None = None
    if app_bootstrap is None:
        app_bootstrap = AppBootstrap()
        logging.info(f"Loop: {app_bootstrap.loop}")
        asyncio.run_coroutine_threadsafe(
            app_bootstrap.start(), loop=app_bootstrap.loop
        ).result()
    logging.info(f"AppContext: {AppContext.__dict__}")

    download_manager = DownloadManager(AppContext.clients.get(Client.telegram))
    download_controller = DownloadController(download_manager)

    try:

        def create_tasks():
            urls_expanded = expand_telegram_media_url(
                "https://t.me/c/3353920644/12836-12867"
            )
            assert urls_expanded is not None
            return [
                asyncio.create_task(download_controller.request_information(url))
                for url in urls_expanded
            ]

        item = asyncio.run_coroutine_threadsafe(
            download_controller.request_information(
                url="https://t.me/c/2066575278/7143"
            ),
            loop=app_bootstrap.loop,
        ).result()
        logging.info(f"DownloadItem result: {item}")
        path_saved = asyncio.run_coroutine_threadsafe(
            download_controller.download(item=item), loop=app_bootstrap.loop
        ).result()
        logging.info(f"Path saved: {path_saved}")
    except Exception as ex:
        logging.exception(ex)
    finally:
        app_bootstrap.loop.close()
