from message import Message
from event_types import EventTypes
from computer import LAZY_COMPUTER, WORKER_COMPUTER
from event import Event
import random
import math

worker_arrival_rate = 1 / 15  # arrivals per second


class ArrivalGenerator:
    @staticmethod
    def gen_worker_ext_arrival():
        arrival_time = random.expovariate(worker_arrival_rate)
        return Event(
            time=arrival_time,
            type=EventTypes.WORKER_RECEIVE_EXT_MSG,
            message=None,
            target=WORKER_COMPUTER,
        )

    @staticmethod
    def gen_lazy_ext_arrival():
        a, b, c = 2, 4, 10
        x_time = random.random()
        arrival_time = 0.0
        # breakpoint = (b-a)/(c-a) = (4-2)/(10-2) = 2/8 = 0.25
        if x_time < 0.25:
            arrival_time = a + math.sqrt(x_time * (b - a) * (c - a))
        else:
            arrival_time = c - math.sqrt((1 - x_time) * (c - b) * (c - a))

        return Event(
            time=arrival_time,
            type=EventTypes.LAZY_RECEIVE_EXT_MSG,
            message=None,
            target=LAZY_COMPUTER,
        )
