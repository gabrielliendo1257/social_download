import asyncio
import threading
from dataclasses import dataclass
from enum import Enum
from urllib.parse import urlparse


class DownloaderStatus(Enum):
    INITIALIZED = 0
    DOWNLOADING = 1
    PAUSED = 2
    ERROR = 3
    NO_INITIALIZED = 4
    FINISHED = 5


class ChatType(Enum):
    INVITE = 1
    PRIVATE = 2
    PUBLIC_THREAD = 3
    PUBLIC = 4
    PROFILE = 5


class MediaBase:
    def __init__(self, uri, id, date, size, caption):
        self.uri = uri
        self.id = id
        self.date = date
        self.size = size
        self.__caption = caption

    @property
    def caption(self):
        return self.__caption

    @caption.setter
    def caption(self, value):
        self.__aption = value


@dataclass
class UrlTelegramParts:
    chat_id: int | str | None
    thread_id: int | None
    message_id: int | None
    chat_type: ChatType


class AsyncLoopRunner:
    def __init__(self):
        self.loop_ready = threading.Event()
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

        self.loop_ready.wait()

    def _run_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop_ready.set()
        self.loop.run_forever()
