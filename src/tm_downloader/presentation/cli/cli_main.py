import time
from typing import List

import click

from rich.console import Console
from rich.live import Live
from rich.table import Table
from rich.progress import Progress, TextColumn, BarColumn, TimeRemainingColumn
import asyncio

from tm_downloader.domain.events.manager import TelegramEventBus
from tm_downloader.domain.models.media import MediaBase
from tm_downloader.infrastructure.controller import TelegramController
from tm_downloader.utils.tm_client import parse_url_from_pattern

tg_controller = TelegramController(
    TelegramEventBus()
)

console = Console()

def success_connect():
    print("Success connect")

def error_connect():
    print("Error connect")


async def get_inf(url: str):
    await tg_controller.create_client(
        on_success=success_connect,
        on_error=error_connect,
    )
    return await tg_controller.telegram_actions.get_information_video(url=url)

# Creamos una clase para representar el estado de cada URL
class URLStatus:
    def __init__(self, url: str):
        self.url = url
        self.status = "[grey50]⏳ Waiting..."
        self.result: MediaBase = None

    def set_scanning(self):
        self.status = "[yellow]⏳ Scanning..."

    def set_done(self):
        self.status = "[green]✔ Done"

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

async def make_progress(urls: List[str]):
    for url in urls:
        progress = Progress(
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            "[progress.percentage]{task.percentage:>3.1f}%",
            TimeRemainingColumn(),
        )
        with progress:
            description = "Downloading..."
            task1 = progress.add_task(description, total=1, desc=url)

            def telethon_progress_callback(current, total):
                global description
                if current == total:
                    description = "[green]✔ Done"
                progress.update(
                    task1,
                    description=description,
                    completed=current,
                    total=total
                )

            await tg_controller.create_client(
                on_success=success_connect,
                on_error=error_connect
            )
            await tg_controller.telegram_actions.download_video(url, telethon_progress_callback)

            while not progress.finished:
                progress.update(task1, advance=1)
                time.sleep(0.1)

async def request_inf_video_tg(url_status_obj: URLStatus):
    """
    Pide informacion del video, utilizando el cliente de telegram
    """
    await tg_controller.create_client(
        on_success=success_connect,
        on_error=error_connect
    )
    info = await tg_controller.telegram_actions.get_information_video(url=url_status_obj.url)

    url_status_obj.result = MediaBase(
        uri=url_status_obj.url,
        id=info.id,
        date=info.date,
        size=None,
        caption=info.message
    )

async def scan_url(url_status_obj: URLStatus):
    """
    Escanea la url, seteando la informacion en
    """
    url_status_obj.set_scanning()
    future_connect = asyncio.run_coroutine_threadsafe(
        request_inf_video_tg(url_status_obj),
        loop = tg_controller.loop
    )
    while not future_connect.done():
        url_status_obj.set_done()

async def app(url: str):
    """
    Orquesta el comportamiento de rich
    """
    url_status_obj = URLStatus(url)

    with Live(make_table(url_status_obj), refresh_per_second=10, console=console) as live:
        task = asyncio.create_task(scan_url(url_status_obj))
        print("Tasks: ", task)

        while not task.done():
            print("Task not done")
            live.update(make_table(url_status_obj))
            print("Esperando...")
            await asyncio.sleep(0.1)

        print("Task done")
        # Una última actualización al finalizar
        live.update(make_table(url_status_obj))


@click.command()
@click.option(
    '--url', '-u',
    type=str,
    help="The url to download",
    show_default=False
)
@click.option(
    '--url_pattern', '-p',
    type=str,
    help="The range of urls to download",
    show_default=False
)
def initializer_cli(url: str, url_pattern: str) -> None:
    #asyncio.run(app(url))
    asyncio.run(make_progress([url]))
    ids_start, ids_end, channel = parse_url_from_pattern(url_pattern)

    # sleep(5)
    # asyncio.create_task(get_int_run(url))
