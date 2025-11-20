from dataclasses import dataclass, field
from typing import Optional

from event_type import EventType
from message import Message


@dataclass(order=True)
class Event:
    time: float
    type: EventType = field(compare=False)
    message: Optional[Message] = field(default=None, compare=False)
    target: Optional[int] = field(default=None, compare=False)
