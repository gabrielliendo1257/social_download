import queue
from abc import ABC
from typing import Callable, Any


class AbstractPlatform(ABC):

    def __init__(self, func: Callable = None, editor: Any = None, *args, **kwargs):
        self.__queue_downloads = queue.Queue()
        self.__client = None
        self.__editor = editor
        self.__func = func
        self.__args = args
        self.__kwargs = kwargs

    @property
    def client(self):
        return self.__client

    async def get_information_video(self, url):
        raise NotImplementedError()

    async def download_video(self, url, progress_callback: Callable):
        raise NotImplementedError()

    async def verify_code(self, phone: str, code: str, phone_code_hash: str, password: str):
        raise NotImplementedError()

    async def send_code(self, phone: str) -> Any:
        raise NotImplementedError()

    async def is_user_authorized(self) -> bool:
        raise NotImplementedError()

