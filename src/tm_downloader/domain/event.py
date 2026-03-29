from abc import ABC, abstractmethod
from typing import List


class EvenEmitter:
    def __init__(self) -> None:
        self.listeners: List[Observer] = []

    def attach(self, observer: Observer):
        self.listeners.append(observer)

    def publish(self):
        for lst in self.listeners:
            lst.on_event(self)


class Observer(ABC):

    @abstractmethod
    def on_event(self, EvenEmitter):
        pass
