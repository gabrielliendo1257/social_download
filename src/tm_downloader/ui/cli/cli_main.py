import asyncio
import logging
from threading import Thread
import time
from typing import List

import click
from rich import progress
from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn
from rich.table import Table

from tm_downloader.app import AppBootstrap
from tm_downloader.domain.model import (
    AbstractUI,
    AppContext,
    Client,
    DownloadItem,
    LinkType,
)
from tm_downloader.telegram.auth_manager import AuthManager
from tm_downloader.telegram.download_manager import DownloadManager
from tm_downloader.telegram.runtime import Runtime
from tm_downloader.ui.controller import DownloadController
from tm_downloader.utils.url import parse_telegram_url

download_controller: DownloadController | None = None
download_manager: DownloadManager | None = None


class TelegramCli(AbstractUI):

    def __init__(self, runtime: Runtime) -> None:
        super().__init__()
        self.runtime = runtime
        self.download_controller = None

    def show_new_url_component(self, message):
        print("Message receiver from cli: ", message)

    def show_queue_download(self):
        pass

    def change_state_url_component(self, item, path):
        return super().change_state_url_component(item, path)


def success_connect():
    print("Success connect")


def error_connect():
    print("Error connect")


# Genera la tabla a partir del estado actual
def make_table(url_status_obj):
    """
    Retorna una objeto Table de rich, con toda la informacion del objeto URLStatus
    """
    table = Table(show_header=True)
    table.add_column("URL", style="cyan")
    table.add_column("Status")

    table.add_row(url_status_obj.url, url_status_obj.status)

    return table


async def worker(url, task_id, progress):
    global download_controller

    def make_callback(task_id):
        progress.update(task_id, advance=1)
        time.sleep(0.1)
        description = "Starting......"

        progress.update(task_id, description=description)

        def callback(current, total):
            description = "Downloading..."
            if current == total:
                description = "[green]✔ Done"
            progress.update(
                task_id, description=description, completed=current, total=total
            )

        return callback

    description = "Requesting..."
    progress.update(task_id, description=description)
    assert isinstance(
        download_controller, DownloadController
    ), "DownloadController is None"
    item = await download_controller.request_information_new(url=url)
    assert isinstance(item, DownloadItem)
    path_saved = await download_controller.download_new(
        item=item, progress_callback=make_callback(task_id)
    )
    logging.info(f"Saved on: {path_saved}")


async def make_progress(urls: List[str]):
    global download_controller

    download_manager = DownloadManager(client=AppContext.clients.get(Client.telegram))
    download_controller = DownloadController(download_manager=download_manager)

    progress = Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.1f}%",
        TimeRemainingColumn(),
    )
    with progress:
        task_ids = [progress.add_task(description="Pending...", total=1) for _ in urls]

        tasks = [worker(url, task_id, progress) for url, task_id in zip(urls, task_ids)]

        await asyncio.gather(*tasks)


@click.command()
@click.option(
    "--download", "-d", type=str, help="Download media from url.", show_default=False
)
@click.option("--information", "--i", type=str, help="Request information url.")
def initializer_cli(download: str, information: str) -> None:
    app_bootstrap = AppBootstrap()
    logging.info(f"Loop: {app_bootstrap.loop}")
    asyncio.run_coroutine_threadsafe(
        app_bootstrap.start(), loop=app_bootstrap.loop
    ).result()
    urls = download.split(",")
    asyncio.run_coroutine_threadsafe(make_progress(urls), loop=AppContext.loop).result()
