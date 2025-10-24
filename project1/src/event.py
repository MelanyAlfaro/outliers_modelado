from dataclasses import dataclass, field
from typing import Optional

from .event_types import EventTypes
from .message import Message


@dataclass(order=True)
class Event:
    time: float
    type: EventTypes = field(compare=False)
    message: Optional[Message] = field(default=None, compare=False)
    target: Optional[int] = field(default=None, compare=False)
