from message import Message
from event import Event
from event_types import EventTypes
from computer import Computer
from computer import WORKER_COMPUTER, LAZY_COMPUTER
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
        self.master_computer: MasterComputer = MasterComputer()
        self.worker_computer: WorkerComputer = WorkerComputer()
        self.lazy_computer: LazyComputer = LazyComputer()

    def initialize_sim(self) -> None:
        self.clock = 0.0
        self.event_queue.clear()
        self.computers.clear()
        self.master_computer = MasterComputer()
        self.worker_computer = WorkerComputer()
        self.lazy_computer = LazyComputer()
        self.computers = [
            None,
            self.master_computer,
            self.worker_computer,
            self.lazy_computer,
        ]
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

        if event.type == EventTypes.SIMULATION_START:
            self.schedule_event(self.gen_msg_arrival_worker)
            self.schedule_event(self.gen_msg_arrival_lazy)
            return
        if event.type == EventTypes.SIMULATION_END:
            return

        self.handle_event(event)

    def handle_event(self, event: Event) -> None:

        # Specific events
        if event.type == EventTypes.LAZY_REJECT_MSG:
            self.lazy_computer.reject_message()
            return
        elif event.type == EventTypes.MASTER_SEND_MSG:
            self.master_computer.send_message()
            return

        # Common events
        target_computer = self.computers[event.target]
        if event.type in (
            EventTypes.WORKER_RECEIVE_EXT_MSG,
            EventTypes.LAZY_RECEIVE_EXT_MSG,
        ):
            target_computer.enqueue_message(event.message)
            target_computer.receive_message()
            if not target_computer.busy:
                self.schedule_event(
                    Event(
                        self.clock,
                        target_computer.get_start_processing_event_type(),
                        event.message,
                        event.target,
                    )
                )

                if EventTypes.WORKER_RECEIVE_EXT_MSG:
                    self.schedule_event(self.gen_msg_arrival_worker())

                elif EventTypes.LAZY_RECEIVE_EXT_MSG:
                    self.schedule_event(self.gen_msg_arrival_lazy())
        elif event.type in (
            EventTypes.WORKER_START_PROCESSING_MSG,
            EventTypes.LAZY_START_PROCESSING_MSG,
            EventTypes.MASTER_START_PROCESSING_MSG,
        ):
            self.schedule_event(target_computer.process_message(self.clock))
        elif event.type in (
            EventTypes.WORKER_END_PROCESSING_MSG,
            EventTypes.LAZY_END_PROCESSING_MSG,
            EventTypes.MASTER_END_PROCESSING_MSG,
        ):
            self.schedule_event(
                target_computer.determine_message_outcome(self.clock, event.message)
            )
        elif event.type in (
            EventTypes.WORKER_RECEIVE_INT_MSG,
            EventTypes.LAZY_RECEIVE_INT_MSG,
            EventTypes.MASTER_RECEIVE_MSG,
        ):
            target_computer.enqueue_message(event.message)
            if (
                target_computer.ID == WORKER_COMPUTER
                or target_computer.ID == LAZY_COMPUTER
            ):
                target_computer.receive_message()

            if not target_computer.busy:
                self.schedule_event(
                    Event(
                        self.clock,
                        target_computer.get_start_processing_event_type(),
                        event.message,
                        event.target,
                    )
                )

    def gen_msg_arrival_worker(self) -> Event:
        pass

    def gen_msg_arrival_lazy(self) -> Event:
        pass
