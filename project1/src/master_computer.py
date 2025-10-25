import random as rd

from computer import Computer
from message import Message
from event import Event


class MasterComputer(Computer):
    def __init__(self, ID: int) -> None:
        super().__init__(ID)
        self.sent_messages: int = 0
        self.process_time_mean: float = 3
        self.process_time_variance: float = 1

    def process_message(self, now: float) -> Event:
        # append() adds messages to the right, so we must popleft for queue behavior
        message = self.message_queue.popleft()
        # TODO check if it's necessary to pass message
        processing_time = self.generate_processing_time(message)

    def generate_processing_time(self, message: Message) -> float:
        return rd.normalvariate(
            mu=self.process_time_mean, sigma=self.process_time_variance
        )

    def _send_message(self):
        self.sent_messages += 1
