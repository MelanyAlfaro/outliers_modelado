import random as rd

from computer import Computer, MASTER_COMPUTER, WORKER_COMPUTER, LAZY_COMPUTER
from message import Message
from event import Event
from event_type import EventType

PROB_RETURN_MSG_FROM_LAZY = 0.5
PROB_RETURN_MSG_FROM_WORKER = 0.2


class MasterComputer(Computer):
    """
    Represents the master computer in the simulation.

    The master processes messages from other computers and decides whether
    to send them externally or return them to their source, based on probability.
    """

    def __init__(self) -> None:
        super().__init__(ID=MASTER_COMPUTER)
        self.sent_messages: int = 0
        self.process_time_mean: float = 3.0
        self.process_time_variance: float = 1.0

    def _get_end_processing_event_type(self) -> EventType:
        """Return the event type for when message processing ends."""
        return EventType.MASTER_END_PROCESSING_MSG

    def generate_processing_time(self) -> float:
        """
        Generate a random processing time based on a normal distribution.

        Ensures the returned time is never negative.
        """
        time = rd.normalvariate(
            mu=self.process_time_mean, sigma=self.process_time_variance
        )
        return max(0.0, time)

    def determine_message_outcome(self, now: float, message: Message) -> Event:
        """
        Decide what to do after processing a message.

        The master may:
        - Send the message externally.
        - Return it to the worker or lazy computer based on random probability.
        """
        outcome_event_type = EventType.MASTER_SEND_MSG
        target_computer = None
        message_return_rv = rd.random()

        if (
            message.source == WORKER_COMPUTER
            and message_return_rv <= PROB_RETURN_MSG_FROM_WORKER
        ):
            outcome_event_type = EventType.WORKER_RECEIVE_INT_MSG
            target_computer = WORKER_COMPUTER
        elif (
            message.source == LAZY_COMPUTER
            and message_return_rv <= PROB_RETURN_MSG_FROM_LAZY
        ):
            outcome_event_type = EventType.LAZY_RECEIVE_INT_MSG
            target_computer = LAZY_COMPUTER

        self.busy = False
        self.update_busy_time(now)
        return Event(
            time=now, type=outcome_event_type, message=message, target=target_computer
        )

    def send_message(self) -> None:
        """Increase the number of messages sent by the master."""
        self.sent_messages += 1

    def get_start_processing_event_type(self) -> EventType:
        """
        Returns the event type that signals this computer is ready to begin processing a message.
        """
        return EventType.MASTER_START_PROCESSING_MSG
