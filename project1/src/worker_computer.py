import random as rd

from computer_id import ComputerID
from computer import Computer
from message import Message
from event import Event
from event_type import EventType


class WorkerComputer(Computer):
    """
    Represents the worker computer (Computer No. 2) in the simulation.

    Responsibilities:
        - Receives messages from external sources.
        - Analyzes and prepares each message for the Master computer.
        - Processing time for each message follows a uniform distribution between
          process_time_min and process_time_max.
        - Keeps track of the total number of messages it has received.
        - Always sends processed messages to the Master computer (Computer No. 1).

    Attributes:
        received_messages (int): Total number of messages the worker has received.
        process_time_min (float): Minimum processing time per message.
        process_time_max (float): Maximum processing time per message .
    """

    def __init__(self) -> None:
        """
        Initialize a WorkerComputer instance with default processing time bounds
        and an empty received_messages counter.
        """
        super().__init__(ID=ComputerID.WORKER_COMPUTER)
        self.received_messages: int = 0
        self.process_time_min: float = 5.0
        self.process_time_max: float = 10.0

    def generate_processing_time(self) -> float:
        """
        Generate a random processing time for a message based on a uniform distribution.

        Returns:
            float: Processing time in seconds.
        """
        return rd.uniform(self.process_time_min, self.process_time_max)

    def _get_end_processing_event_type(self) -> EventType:
        """
        Get the event type corresponding to the completion of message processing.

        Returns:
            EventType: Event type indicating the worker has finished processing a message.
        """
        return EventType.WORKER_END_PROCESSING_MSG

    def determine_message_outcome(self, now: float, message: Message) -> Event:
        """
        Decide the outcome of a message after processing.

        WorkerComputer always sends the processed message to the Master computer.

        Args:
            now (float): Current simulation time in seconds.
            message (Message): The message that has just been processed.

        Returns:
            Event: Event representing the Master computer receiving the message.
        """
        self.update_busy_time(now)
        self.busy = False
        return Event(
            time=now,
            type=EventType.MASTER_RECEIVE_MSG,
            message=message,
            target=ComputerID.MASTER_COMPUTER,
        )

    def receive_message(self) -> None:
        """Increase the number of messages received by the worker computer."""
        self.received_messages += 1

    def get_start_processing_event_type(self) -> EventType:
        """
        Returns the event type that signals this computer is ready to begin processing a message.
        """
        return EventType.WORKER_START_PROCESSING_MSG
