from __future__ import annotations

from abc import ABC, abstractmethod
from asyncio import AbstractEventLoop
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict

from telethon.tl.types import Message

from tm_downloader.domain.queue import DownloadQueue


class MessageViewModel:
    def __init__(self, url=None, date=None, size=None, id_message=None, peer_id=None, file=None, message=None, filename=None):
        self.url = url
        self.date = date
        self.size = size
        self.id_message = id_message
        self.peer_id = peer_id
        self.file = file
        self.message = message
        self.filename = filename

    def __str__(self) -> str:
        return f"MessageViewModel(url={self.url}, data={self.date}, size={self.size}, id_message={self.id_message}, peer_id={self.peer_id}, file={str(self.file)}, file_name={self.filename})"


class AbstractUI:

    def append_download_component(self, message):
        pass

    def clean_url_component(self):
        pass

    def change_state_url_component(self, item, path):
        pass


class DownloadState(Enum):
    IDLE = "idle"
    PENDING = "pending"
    STARTING = "starting"
    DOWNLOADING = "downloading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class LinkType(Enum):
    INVITE = 1
    PRIVATE = 2
    PUBLIC_THREAD = 3
    PUBLIC = 4
    PROFILE = 5
    RANGE = 6
    PRIVATE_THREAD = 7


class Client(Enum):
    telegram = "telegram"
    yt_dl = "yt_dl"
    gallery_dl = "gallery_dl"


class BaseService:

    async def download(self, item: DownloadItem, *args, **kwargs) -> str:
        raise NotImplementedError("download not implemented")

    async def request_information(self, job: DownloadJob, file=None) -> DownloadItem:
        raise NotImplementedError("request not implemented")


class ContextPlatform:
    def __init__(
        self,
        url: str,
        connection=None,
        loop: AbstractEventLoop | None = None,
        service: BaseService | None = None,
    ):
        self.connection = connection
        self.loop = loop
        self.url = url
        self.service = service


class IResolver(ABC):

    @abstractmethod
    def resolve(self, url: str) -> ContextPlatform | None:
        pass


class AppContext:
    queue: DownloadQueue | None = None
    clients: Dict[Client, Any] = {}
    resolver: IResolver | None = None
    loop: AbstractEventLoop | None = None


class DownloadJob:
    def __init__(self, url: str, id_job: str) -> None:
        super().__init__()
        self.state = DownloadState.IDLE
        self.url = url
        self.id_job = id_job
        self.progress = 0
        self.total = None
        self.result = None
        self.error = None

    def transition(self, new_state: DownloadState):
        # invariant enforcement
        valid = {
            DownloadState.PENDING: {DownloadState.STARTING},
            DownloadState.STARTING: {DownloadState.DOWNLOADING, DownloadState.FAILED},
            DownloadState.DOWNLOADING: {
                DownloadState.PROCESSING,
                DownloadState.FAILED,
                DownloadState.CANCELLED,
            },
            DownloadState.PROCESSING: {DownloadState.COMPLETED, DownloadState.FAILED},
        }

        if self.state in valid and new_state not in valid[self.state]:
            raise ValueError(f"Invalid transition {self.state} -> {new_state}")

        self.state = new_state

    def update_progress(self, current, total):
        self.progress = current
        self.total = total

    def __str__(self) -> str:
        return f"DownloadJob(state={self.state}, id_job={self.id_job}, url={self.url})"


@dataclass
class DownloadItem:
    data: MessageViewModel
    job: DownloadJob
    message: Message

    def __str__(self) -> str:
        return f"DownloadItem(data={str(self.data)}, job={str(self.job)})"
