from abc import ABC, abstractmethod
from collections import deque

from .message import Message
from .event import Event


class Computer(ABC):
    def __init__(self, ID: int) -> None:
        self.ID: int = ID
        self.end_time: float = 0.0
        self.busy: bool = False
        self.busy_time: float = 0.0
        self.message_queue: deque[Message] = deque()

    def enqueue_message(self, message: Message) -> None:
        self.message_queue.append(message)

    def get_enqueued_messages(self) -> int:
        return len(self.message_queue)

    def get_state(self) -> str:
        return "busy" if self.busy else "free"

    @abstractmethod
    def process_message(self, now: float) -> Event:
        raise NotImplementedError

    @abstractmethod
    def generate_processing_time() -> float:
        raise NotImplementedError
