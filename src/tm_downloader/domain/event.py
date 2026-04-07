from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from tm_downloader.domain.model import DownloadJob


class EvenEmitter:
    def __init__(self) -> None:
        self.listeners: List[EventListener] = []

    def attach(self, observer: EventListener):
        self.listeners.append(observer)

    def publish(self, data: DownloadJob):
        for lst in self.listeners:
            lst.on_event(data)


class EventListener(ABC):

    @abstractmethod
    def on_event(self, data: DownloadJob):
        pass
