from abc import ABC, abstractmethod
from collections import deque

from message import Message
from event import Event
from event_types import EventTypes


MASTER_COMPUTER = 1
WORKER_COMPUTER = 2
LAZY_COMPUTER = 3


class Computer(ABC):
    def __init__(self, ID: int) -> None:
        self.ID: int = ID
        self.busy: bool = False
        self.busy_time: float = 0.0
        self.busy_time_start: float = None
        self.message_queue: deque[Message] = deque()

    def enqueue_message(self, message: Message) -> None:
        self.message_queue.append(message)

    def get_enqueued_messages(self) -> int:
        return len(self.message_queue)

    def get_state(self) -> str:
        return "Busy" if self.busy else "Idle"

    def process_message(self, now: float) -> Event:
        # Avoid popping if method is called while message queue is empty
        if len(self.message_queue) == 0:
            raise AssertionError("Message queue empty on process message call")

        # append() adds messages to the right, so we must popleft for queue behavior
        message = self.message_queue.popleft()

        # Mark self as busy and register when the computer started being busy
        self.busy = True
        self.busy_time_start = now

        # Mark new wait time
        message.update_wait_time(service_start_time=now)

        # Calculate processing time accordingly
        processing_end_time = now + self.generate_processing_time()

        # Create new event for process end
        end_processing_event = Event(
            time=processing_end_time,
            type=self._get_end_processing_event_type(),
            message=message,
            target=self.ID,
        )
        return end_processing_event

    def update_busy_time(self, current_time: float) -> None:
        self.busy_time += current_time - self.busy_time_start

    @abstractmethod
    def generate_processing_time(self) -> float:
        raise NotImplementedError

    @abstractmethod
    def _get_end_processing_event_type(self) -> EventTypes:
        raise NotImplementedError

    @abstractmethod
    def get_start_processing_event_type(self) -> EventTypes:
        raise NotImplementedError

    @abstractmethod
    def determine_message_outcome(self, now: float, message: Message) -> Event:
        raise NotImplementedError
