from event_types import EventTypes
from computer import Computer
from computer import WORKER_COMPUTER, LAZY_COMPUTER
from master_computer import MasterComputer
from worker_computer import WorkerComputer
from lazy_computer import LazyComputer
from speed_mode import SpeedMode
from event import Event
from logger import Logger
from external_arrival_generator import ExternalArrivalGenerator

import heapq
from typing import List, Tuple


class Simulator:

    EXTERNAL_ARRIVALS = {
        EventTypes.WORKER_RECEIVE_EXT_MSG,
        EventTypes.LAZY_RECEIVE_EXT_MSG,
    }

    PROCESS_START = {
        EventTypes.WORKER_START_PROCESSING_MSG,
        EventTypes.LAZY_START_PROCESSING_MSG,
        EventTypes.MASTER_START_PROCESSING_MSG,
    }

    PROCESS_END = {
        EventTypes.WORKER_END_PROCESSING_MSG,
        EventTypes.LAZY_END_PROCESSING_MSG,
        EventTypes.MASTER_END_PROCESSING_MSG,
    }

    INTERNAL_ARRIVALS = {
        EventTypes.WORKER_RECEIVE_INT_MSG,
        EventTypes.LAZY_RECEIVE_INT_MSG,
        EventTypes.MASTER_RECEIVE_MSG,
    }

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
        # TODO (anyone) : change list for dictionary
        self.computers: List[Computer] = []
        self.speed_mode: SpeedMode = speed_mode
        self.logger: Logger = Logger()
        self.master_computer: MasterComputer = MasterComputer()
        self.worker_computer: WorkerComputer = WorkerComputer()
        self.lazy_computer: LazyComputer = LazyComputer()
        # dictionary maps event types to handler methods
        self.specific_event_handlers = {
            EventTypes.LAZY_REJECT_MSG: self._handle_lazy_reject,
            EventTypes.MASTER_SEND_MSG: self._handle_master_send,
        }

    def initialize_sim(self) -> None:
        self.clock = 0.0
        self.event_queue.clear()
        self.computers.clear()
        self.master_computer = MasterComputer()
        self.worker_computer = WorkerComputer()
        self.lazy_computer = LazyComputer()
        # TODO (anyone) : change list for dictionary
        self.computers = [
            None,
            self.master_computer,
            self.worker_computer,
            self.lazy_computer,
        ]
        self.schedule_event(Event(self.clock, EventTypes.SIMULATION_START))

    def schedule_event(self, event: Event) -> None:
        # Not enquening events after max time
        if event.time > self.max_time:
            return
        heapq.heappush(self.event_queue, event)

    def get_next_event(self) -> Event:
        return heapq.heappop(self.event_queue)

    def run(self):
        while self.total_runs < self.max_runs:
            self.initialize_sim()
            while self.event_queue:
                self.process_next_event()
            self.total_runs += 1

    def process_next_event(self) -> None:
        event = self.get_next_event()
        self.clock = event.time
        if event.type == EventTypes.SIMULATION_START:
            self.schedule_event(
                ExternalArrivalGenerator.gen_worker_ext_arrival(self.clock)
            )
            self.schedule_event(
                ExternalArrivalGenerator.gen_lazy_ext_arrival(self.clock)
            )
            return
        if event.type == EventTypes.SIMULATION_END:
            # self.event_queue.clear()
            return

        self.handle_event(event)
        # Log each time we take out an event
        Logger.log_event(
            max_sim_count=self.max_runs,
            current_time=self.clock,
            event_type=event.type,
            worker_computer=self.worker_computer,
            master_computer=self.master_computer,
            lazy_computer=self.lazy_computer,
            sim_number=self.total_runs,
            speed=self.speed_mode,
        )

        # Verification to mark end of simulations
        if self.clock >= self.max_time:
            self.schedule_event(Event(self.clock, EventTypes.SIMULATION_END))

    def handle_event(self, event: Event) -> None:
        # 1) If mapped directly → call handler and return
        handler = self.specific_event_handlers.get(event.type)
        if handler:
            handler(event)
            return

        # 2) External arrival?
        if event.type in self.EXTERNAL_ARRIVALS:
            self._handle_external_arrival(event)
            return

        # 3) Processing start?
        if event.type in self.PROCESS_START:
            self._handle_processing_start(event)
            return

        # 4) Processing end?
        if event.type in self.PROCESS_END:
            self._handle_processing_end(event)
            return

        # 5) Internal arrival?
        if event.type in self.INTERNAL_ARRIVALS:
            self._handle_internal_arrival(event)
            return

        # 6) Unknown event type
        raise ValueError(f"Unhandled event type: {event.type}")

    def _handle_lazy_reject(self, event: Event) -> None:
        self.lazy_computer.reject_message()

    def _handle_master_send(self, event: Event) -> None:
        self.master_computer.send_message()

    def _handle_external_arrival(self, event: Event) -> None:
        target = self.computers[event.target]

        # Always enqueue
        target.enqueue_message(event.message)
        target.receive_message()

        # If idle → schedule processing
        if not target.busy:
            self.schedule_event(
                Event(
                    self.clock,
                    target.get_start_processing_event_type(),
                    event.message,
                    event.target,
                )
            )

        # Schedule next arrival
        if event.type == EventTypes.WORKER_RECEIVE_EXT_MSG:
            self.schedule_event(
                ExternalArrivalGenerator.gen_worker_ext_arrival(self.clock)
            )
        else:
            self.schedule_event(
                ExternalArrivalGenerator.gen_lazy_ext_arrival(self.clock)
            )

    def _handle_internal_arrival(self, event: Event) -> None:
        target = self.computers[event.target]

        target.enqueue_message(event.message)

        if target.ID in (WORKER_COMPUTER, LAZY_COMPUTER):
            target.receive_message()

        if not target.busy:
            self.schedule_event(
                Event(
                    self.clock,
                    target.get_start_processing_event_type(),
                    event.message,
                    event.target,
                )
            )

    def _handle_processing_start(self, event: Event) -> None:
        target = self.computers[event.target]
        next_event = target.process_message(self.clock)
        self.schedule_event(next_event)

    def _handle_processing_end(self, event: Event) -> None:
        target = self.computers[event.target]
        next_event = target.determine_message_outcome(self.clock, event.message)
        self.schedule_event(next_event)


sim = Simulator(30, 1, SpeedMode.FAST)
sim.run()
