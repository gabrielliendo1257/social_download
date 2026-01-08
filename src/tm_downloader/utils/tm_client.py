import asyncio
import logging
from urllib.parse import urlparse

from tm_downloader.domain.models.media import DownloaderStatus, UrlTelegramParts, ChatType

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d %(levelname)s: %(message)s",
    datefmt="%H:%M:%S",
)


async def monitor_tasks() -> None:
    while True:
        tasks = [t for t in asyncio.all_tasks() if not t.done()]
        print(f"Tareas activas: {len(tasks)}")
        for t in tasks:
            print(f" - {t.get_coro().__name__} -> {t._state}")
        await asyncio.sleep(4)


def parse_telegram_url(url: str) -> UrlTelegramParts:
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split("/") if p]
    print("Partes del path: ", path_parts)

    # Validar dominio
    if parsed.netloc not in ("t.me", "telegram.me", "www.t.me", "www.telegram.me"):
        raise Exception(f"Invalid netloc url: {parsed.netloc}")

    # Caso 1: enlace de invitación
    if path_parts and path_parts[0].startswith("+"):
        return UrlTelegramParts(None, None, None, chat_type=ChatType.INVITE)

    # Caso 2: grupo/canal privado (t.me/c/CHAT_ID/MESSAGE_ID)
    if len(path_parts) == 3 and path_parts[0] == "c":
        username, thread_id, message_id = path_parts
        return UrlTelegramParts(
            chat_id=int("-100" + thread_id),
            thread_id=None,
            message_id=int(message_id),
            chat_type=ChatType.PRIVATE
        )

    # Caso 3: canal público con posible thread (t.me/username/thread/message)
    if len(path_parts) > 3 and path_parts[0] == "c":
        c, username, thread_id, message_id = path_parts
        return UrlTelegramParts(
            chat_id=int("-100" + username),
            thread_id=int(thread_id),
            message_id=int(message_id),
            chat_type=ChatType.PUBLIC_THREAD
        )

    # Caso 4: canal público normal (t.me/username/message)
    if len(path_parts) == 2:
        username, message_id = path_parts
        return UrlTelegramParts(
            chat_id=username,
            thread_id=None,
            message_id=int(message_id),
            chat_type=ChatType.PUBLIC
        )

    # Caso 5: perfil o canal sin mensaje (t.me/username)
    if len(path_parts) == 1:
        return UrlTelegramParts(
            chat_id=path_parts[0],
            thread_id=None,
            message_id=None,
            chat_type=ChatType.PROFILE
        )

    raise Exception(f"Invalid telegram url: {url}")


def default_progress_callback(current_template, current: int, total: int) -> None:
    if current == total:
        current_template.status = DownloaderStatus.FINISHED

    current = current / total
    current_template.pb.value = current

    current_template.update()
