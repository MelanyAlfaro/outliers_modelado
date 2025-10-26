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

    def process_message(self, now: float) -> Event:
        # append() adds messages to the right, so we must popleft for queue behavior
        message = self.message_queue.popleft()
        message.update_wait_time(service_start_time=now)

        # Calculate processing time accordingly
        processing_end_time = now + self.generate_processing_time()

        # Create new event for process end
        end_processing_event = Event(
            time=processing_end_time,
            type=EventTypes.MASTER_END_PROCESSING_MSG,
            message=message,
        )
        return end_processing_event

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
        if message.source == WORKER_COMPUTER and message_return_rv <= PROB_RETURN_MSG_FROM_WORKER:
            outcome_event_type = EventTypes.WORKER_RECEIVE_INT_MSG
        elif message.source == LAZY_COMPUTER and message_return_rv <= PROB_RETURN_MSG_FROM_LAZY:
            outcome_event_type = EventTypes.LAZY_RECEIVE_INT_MSG

        # Return outcome event accordingly
        return Event(time=now, type=outcome_event_type, message=message)

    def send_message(self):
        self.sent_messages += 1
