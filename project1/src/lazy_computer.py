import random as rd

from computer import Computer, MASTER_COMPUTER, LAZY_COMPUTER
from message import Message
from event import Event
from event_types import EventTypes

PROB_REJECT_MSG = 0.75


class LazyComputer(Computer):
    """
    Represents the lazy computer (Computer No. 3) in the simulation.

    Responsibilities:
        - Receives messages from external sources.
        - Analyzes and prepares each message for the Master computer.
        - Processing time for each message follows a distribution.
        - Based on probability, decides whether to send messages to the Master (Computer No. 1) or reject them.
        - Keeps track of the total number of messages it has received and rejected.

    Attributes:
        received_messages (int): Total number of messages the computer has received.
        rejected_messages (int): Total number of messages the computer has rejected.
    """

    def __init__(self) -> None:
        """
        Initialize a LazyComputer instance with default processing time bounds
        and empty received_messages and rejected_messages counters.
        """
        super().__init__(ID=LAZY_COMPUTER)
        self.received_messages: int = 0
        self.rejected_messages: int = 0

    @staticmethod
    def processing_time_function(x: float) -> float:
        """
        Distribution used to get a result with a given value (used for comparisons).

        Args:
            x (float): Value to be processed by the function.

        Returns:
            float: Result of the function using 'x' as input.
        """
        return (3 * x**2) / 98

    def generate_processing_time(self) -> float:
        """
        Generate a random processing time based on a given distribution (using the acceptance-rejection method).

        Returns:
            float: Processing time in seconds.
        """
        lower_bound = 3.0
        upper_bound = 5.0
        M = self.processing_time_function(upper_bound)
        while True:
            r1 = rd.random()
            r2 = rd.random()
            processing_time = lower_bound + (upper_bound - lower_bound) * r1
            if r2 <= self.processing_time_function(processing_time) / M:
                return processing_time

    def _get_end_processing_event_type(self) -> EventTypes:
        """
        Get the event type corresponding to the completion of message processing.

        Returns:
            EventTypes: Event type indicating the lazy computer has finished processing a message.
        """
        return EventTypes.LAZY_END_PROCESSING_MSG

    def determine_message_outcome(self, now: float, message: Message) -> Event:
        """
        Decide what to do after processing a message.

        The lazy computer may:
        - Reject the message and delete it from the system.
        - Send it to the master computer.

        Args:
            now (float): Current simulation time in seconds.
            message (Message): The message that has just been processed.

        Returns:
            Event: Event representing the Master computer receiving the message or the message being rejected.
        """
        message_reject_rv = rd.random()

        if message_reject_rv <= PROB_REJECT_MSG:
            outcome_event_type = EventTypes.LAZY_REJECT_MSG
            target_computer = None
        else:
            outcome_event_type = EventTypes.MASTER_RECEIVE_MSG
            target_computer = MASTER_COMPUTER

        self.busy = False
        self.update_busy_time(now)
        return Event(
            time=now, type=outcome_event_type, message=message, target=target_computer
        )

    def receive_message(self) -> None:
        """Increase the number of messages received by the lazy computer."""
        self.received_messages += 1

    def reject_message(self) -> None:
        """Increase the number of messages rejected by the lazy computer."""
        self.rejected_messages += 1

    def get_start_processing_event_type(self) -> EventTypes:
        """
        Returns the event type that signals this computer is ready to begin processing a message.
        """
        return EventTypes.LAZY_START_PROCESSING_MSG
