from message import Message
from event import Event
from event_types import EventTypes
from computer import Computer
from master_computer import MasterComputer
from worker_computer import WorkerComputer
from lazy_computer import LazyComputer
from speed_mode import SpeedMode
from event import Event
from logger import Logger

import heapq
from typing import List, Tuple


class Simulator:
    def __init__(
        self,
        max_sim_time: float,
        requested_runs: int,
        speed_mode: SpeedMode,
    ) -> None:
        self.max_time: float = max_sim_time
        self.total_runs: int = 0
        self.max_runs: int = requested_runs
        self.clock: float = 0.0
        self.event_queue: List[Tuple[float, str]] = []
        self.computers: List[Computer] = []
        self.speed_mode: SpeedMode = speed_mode
        self.logger: Logger = Logger()

    def initialize_sim(self) -> None:
        self.clock = 0.0
        self.event_queue.clear()
        self.computers.clear()
        master_computer = MasterComputer()
        worker_computer = WorkerComputer()
        lazy_computer = LazyComputer()
        self.computers = [None, master_computer, worker_computer, lazy_computer]
        self.schedule_event(Event(self.clock, EventTypes.SIMULATION_START))

    def schedule_event(self, event: Event) -> None:
        heapq.heappush(self.event_queue, event)

    def get_next_event(self) -> Event:
        return heapq.heappop(self.event_queue)

    def run(self):
        while self.total_runs < self.max_runs:
            self.initialize_sim()
            while self.event_queue:
                self.process_next_event()

    def process_next_event(self) -> None:
        event = self.get_next_event()
        self.clock = event.time
