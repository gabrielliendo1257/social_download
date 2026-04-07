import asyncio
import logging
import time
from typing import List

import click
from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn

from tm_downloader.app import AppBootstrap
from tm_downloader.domain.model import (
    AppContext,
    Client,
    DownloadItem,
)
from tm_downloader.telegram.download_manager import DownloadManager
from tm_downloader.ui.controller import DownloadController

download_controller: DownloadController | None = None
download_manager: DownloadManager | None = None


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
    item = await download_controller.request_information(url=url)
    assert isinstance(item, DownloadItem)
    path_saved = await download_controller.download(
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
