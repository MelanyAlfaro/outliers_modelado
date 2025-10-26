import random as rd

from computer import Computer, MASTER_COMPUTER, WORKER_COMPUTER, LAZY_COMPUTER
from message import Message
from event import Event
from event_types import EventTypes

PROB_RETURN_MSG_FROM_LAZY = 0.5
PROB_RETURN_MSG_FROM_WORKER = 0.2


class MasterComputer(Computer):
    def __init__(self) -> None:
        super().__init__(ID=MASTER_COMPUTER)
        self.sent_messages: int = 0
        self.process_time_mean: float = 3.0
        self.process_time_variance: float = 1.0

    def _get_end_processing_event_type(self) -> EventTypes:
        return EventTypes.MASTER_END_PROCESSING_MSG

    def generate_processing_time(self) -> float:
        return rd.normalvariate(
            mu=self.process_time_mean, sigma=self.process_time_variance
        )

    def determine_message_outcome(self, now: float, message: Message) -> Event:
        # Default outcome set as message sent to exterior
        outcome_event_type = EventTypes.MASTER_SEND_MSG

        # Calculate random number between 0 and 1
        message_return_rv = rd.random()

        # Determine whether to return message or not
        if (
            message.source == WORKER_COMPUTER
            and message_return_rv <= PROB_RETURN_MSG_FROM_WORKER
        ):
            outcome_event_type = EventTypes.WORKER_RECEIVE_INT_MSG
        elif (
            message.source == LAZY_COMPUTER
            and message_return_rv <= PROB_RETURN_MSG_FROM_LAZY
        ):
            outcome_event_type = EventTypes.LAZY_RECEIVE_INT_MSG

        # Mark as not busy anymore
        self.busy = False

        # Return outcome event accordingly
        return Event(time=now, type=outcome_event_type, message=message)

    def send_message(self):
        self.sent_messages += 1
