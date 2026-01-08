from __future__ import annotations

from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass
from typing import TypeVar, Generic

EventMessage = TypeVar("EventMessage")


@dataclass
class EventBus(ABC, Generic[EventMessage]):

    @abstractmethod
    def subscriber(self, event_type: type, handler: Callable) -> None:
        raise NotImplementedError("Subscriber not implemented")

    @abstractmethod
    def unsubscriber(self, event_type: type, handler: Callable) -> None:
        raise NotImplementedError("Unsubscriber not implemented")

    @abstractmethod
    def notify(self, event) -> None:
        raise NotImplementedError("Notify not implemented")


class EventListener(ABC, Generic[EventMessage]):
    def __init__(self, event_message: EventMessage | None) -> None:
        self.__event_message = event_message

    @property
    def event_message(self) -> EventMessage:
        return self.__event_message

    @event_message.setter
    def event_message(self, event_message: EventMessage) -> None:
        self.__event_message = event_message

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError("Run not implemented")


class TelegramEventBus(EventBus):

    def __init__(self):
        self._subscribers = defaultdict(list)

    def subscriber(self, event_type: type, handler: Callable) -> None:
        self._subscribers[event_type].append(handler)

    def unsubscriber(self, event_type: type, handler: Callable) -> None:
        self._subscribers[event_type].remove(handler)

    def notify(self, event) -> None:
        print("Events to call: ", self._subscribers[type(event)])
        for handler in self._subscribers[type(event)]:
            handler(event)
