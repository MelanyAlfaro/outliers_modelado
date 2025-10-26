import random as rd

from computer import Computer, MASTER_COMPUTER, WORKER_COMPUTER, LAZY_COMPUTER
from message import Message
from event import Event
from event_types import EventTypes

class WorkerComputer(Computer):
  
  def __init__(self) -> None:
    super().__init__(ID=WORKER_COMPUTER)
    self.received_messages = 0
    self.process_time_min : float = 5.0
    self.process_time_max : float = 10.0
  
  def generate_processing_time(self) -> float:
    return rd.uniform(self.process_time_min,self.process_time_max)
  
  def _get_end_processing_event_type(self) -> EventTypes:
    return EventTypes.WORKER_END_PROCESSING_MSG
  
  def determine_message_outcome(self, now: float, message: Message) -> Event:
    self.received_messages += 1
    self.busy = False
    return Event(time=now, type=EventTypes.MASTER_RECEIVE_MSG, message=message, target=MASTER_COMPUTER)

