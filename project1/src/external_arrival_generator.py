from message import Message
from event_types import EventTypes
from computer import LAZY_COMPUTER, WORKER_COMPUTER
from event import Event
import random
import math

# Average worker arrival rate (1 arrival every 15 seconds)

worker_arrival_rate = 1 / 15

"""
external_arrival_generator.py
-----------------------------

Provides static factory methods to generate external arrival events
for the Worker and Lazy computers in the discrete-event simulation.

Two different interarrival models are used:
- Worker: Exponential distribution with mean 15 seconds
- Lazy:   Triangular distribution with parameters (a=2, b=4, c=10) seconds
"""


class ExternalArrivalGenerator:
    @staticmethod
    def gen_worker_ext_arrival(now: float) -> Event:
        """
        Generate the next external arrival event for the Worker computer.

        Interarrival times follow an exponential distribution with rate λ = 1/15,
        meaning one arrival every 15 seconds on average.

        Parameters
        ----------
        now : float
            Current simulation time.

        Returns
        -------
        Event
            An event scheduled at (now + interarrival_time), containing:
            - type   : WORKER_RECEIVE_EXT_MSG
            - target : WORKER_COMPUTER
            - message: Message destined for the worker
        """
        arrival_time = random.expovariate(worker_arrival_rate)
        return Event(
            time=now + arrival_time,
            type=EventTypes.WORKER_RECEIVE_EXT_MSG,
            message=Message(WORKER_COMPUTER, now),
            target=WORKER_COMPUTER,
        )

    @staticmethod
    def gen_lazy_ext_arrival(now: float) -> Event:
        """
        Generate the next external arrival event for the Lazy computer.

        Interarrival times follow a triangular distribution with:
            a = 2  (minimum)
            b = 4  (mode)
            c = 10 (maximum)
        The inverse-transform method is used to sample values.

        Parameters
        ----------
        now : float
            Current simulation time.

        Returns
        -------
        Event
            An event scheduled at (now + interarrival_time), containing:
            - type   : LAZY_RECEIVE_EXT_MSG
            - target : LAZY_COMPUTER
            - message: Message destined for the lazy node
        """
        a, b, c = 2, 4, 10
        x_time = random.random()
        arrival_time = 0.0
        # breakpoint = (b-a)/(c-a) = (4-2)/(10-2) = 2/8 = 0.25
        if x_time < 0.25:
            arrival_time = a + math.sqrt(x_time * (b - a) * (c - a))
        else:
            arrival_time = c - math.sqrt((1 - x_time) * (c - b) * (c - a))

        return Event(
            time=now + arrival_time,
            type=EventTypes.LAZY_RECEIVE_EXT_MSG,
            message=Message(LAZY_COMPUTER, now),
            target=LAZY_COMPUTER,
        )
