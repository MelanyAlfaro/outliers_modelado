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

"""
Defines the Simulator class, which executes a discrete-event simulation
of a system composed of a Master, Worker, and Lazy computer.

The simulator maintains an event priority queue, advances simulation time,
dispatches event handlers, and supports multiple independent simulation runs.

External arrivals, internal arrivals, processing start, and processing end
events are categorized via class-level sets for fast lookup.
"""


class Simulator:
    """
    EXTERNAL_ARRIVALS : set[EventTypes]
        Event types corresponding to arrivals from outside the system.
    """

    EXTERNAL_ARRIVALS = {
        EventTypes.WORKER_RECEIVE_EXT_MSG,
        EventTypes.LAZY_RECEIVE_EXT_MSG,
    }
    """
    PROCESS_START : set[EventTypes]
        Event types that indicate the start of message processing.
    """
    PROCESS_START = {
        EventTypes.WORKER_START_PROCESSING_MSG,
        EventTypes.LAZY_START_PROCESSING_MSG,
        EventTypes.MASTER_START_PROCESSING_MSG,
    }
    """
    PROCESS_END : set[EventTypes]
        Event types that indicate the completion of message processing.
    """
    PROCESS_END = {
        EventTypes.WORKER_END_PROCESSING_MSG,
        EventTypes.LAZY_END_PROCESSING_MSG,
        EventTypes.MASTER_END_PROCESSING_MSG,
    }
    """
    INTERNAL_ARRIVALS : set[EventTypes]
        Event types corresponding to internal message transfer.
    """
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
        """
        Initialize simulator configuration and core runtime state.

        Parameters
        ----------
        max_sim_time : float
            Maximum simulation time allowed per run.
        requested_runs : int
            Number of simulation iterations to execute.
        speed_mode : SpeedMode
            Controls logging / pacing behavior during execution.
        """
        self.max_time = max_sim_time  # time limit for each run

        self.max_runs = requested_runs  # number of runs requested
        self.total_runs = 0  # number of completed runs
        self.clock = 0.0  # current simulation timestamp

        self.event_queue = []  # min-heap of pending events
        self.computers = []  # computer entities indexed by ID

        self.speed_mode = speed_mode  # execution pacing config
        self.logger = Logger()  # logs output

        self.master_computer = MasterComputer()  # system entity
        self.worker_computer = WorkerComputer()
        self.lazy_computer = LazyComputer()

        # maps event types → handler functions
        self.specific_event_handlers = {
            EventTypes.LAZY_REJECT_MSG: self._handle_lazy_reject,
            EventTypes.MASTER_SEND_MSG: self._handle_master_send,
        }

    def initialize_sim(self) -> None:
        """
        Reset simulation state for a new run.

        Reinitializes simulation time, event queue, and computer entities, then
        schedules the initial SIMULATION_START event.
        """
        self.clock = 0.0  # reset simulation time
        self.event_queue.clear()  # remove any pending events
        self.computers.clear()  # reset computer container

        # fresh computer instances for this run
        self.master_computer = MasterComputer()
        self.worker_computer = WorkerComputer()
        self.lazy_computer = LazyComputer()

        # TODO (anyone): store as dict instead of list
        # index 1: Master, 2: Worker, 3: Lazy
        self.computers = [
            None,  # keep index alignment
            self.master_computer,
            self.worker_computer,
            self.lazy_computer,
        ]

        # schedule the first event in the run
        self.schedule_event(Event(self.clock, EventTypes.SIMULATION_START))

    def schedule_event(self, event: Event) -> None:
        """
        Add a new event to the simulation queue if it occurs before max_time.

        Events scheduled beyond the simulation horizon are ignored.

        Parameters
        ----------
        event : Event
            The event to be scheduled into the priority queue.
        """
        # Prevent scheduling events after simulation time limit
        if event.time > self.max_time:
            return
        # Push event into min-heap (sorted by event.time)
        heapq.heappush(self.event_queue, event)

    def get_next_event(self) -> Event:
        """
        Retrieve and remove the next scheduled event.

        Returns
        -------
        Event
            The earliest event in the priority queue.
        """

        # Pop smallest timestamp event from min-heap
        return heapq.heappop(self.event_queue)

    def run(self):
        """
        Execute the configured number of simulation runs.

        Each run resets simulation state, processes events until the queue empties,
        and then advances to the next run.
        """

        while self.total_runs < self.max_runs:

            # Reset per-run simulation state
            self.initialize_sim()

            # Process events in chronological order
            while self.event_queue:
                self.process_next_event()

            # Mark run as completed
            self.total_runs += 1

    def process_next_event(self) -> None:
        """
        Gets and process the next event in time order.

        Advances the simulation clock, dispatches event handling,
        schedules new events when appropriate, and logs the activity.
        """
        event = self.get_next_event()  # next event by timestamp
        self.clock = event.time  # advance simulation time

        # Handle first event: schedule external arrivals
        if event.type == EventTypes.SIMULATION_START:
            self.schedule_event(
                ExternalArrivalGenerator.gen_worker_ext_arrival(self.clock)
            )
            self.schedule_event(
                ExternalArrivalGenerator.gen_lazy_ext_arrival(self.clock)
            )
            return

        # Stop processing if end-of-simulation is reached
        if event.type == EventTypes.SIMULATION_END:
            # self.event_queue.clear()
            return

        # Dispatch event to appropriate handler
        self.handle_event(event)

        # Log event after handling
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

        # If time limit reached, schedule end event
        if self.clock >= self.max_time:
            self.schedule_event(Event(self.clock, EventTypes.SIMULATION_END))

        # Verification to mark end of simulations
        if self.clock >= self.max_time:
            self.schedule_event(Event(self.clock, EventTypes.SIMULATION_END))

    def handle_event(self, event: Event) -> None:
        """
        Route an event to the appropriate handler based on its type.

        Events are dispatched through a priority order:
        direct handler mapping → external arrivals → processing start →
        processing end → internal arrivals. Unknown types raise an error.
        """
        # If mapped directly → call handler and return
        handler = self.specific_event_handlers.get(event.type)
        if handler:
            handler(event)
            return

        # External arrival?
        if event.type in self.EXTERNAL_ARRIVALS:
            self._handle_external_arrival(event)
            return

        # Processing start?
        if event.type in self.PROCESS_START:
            self._handle_processing_start(event)
            return

        # Processing end?
        if event.type in self.PROCESS_END:
            self._handle_processing_end(event)
            return

        # Internal arrival?
        if event.type in self.INTERNAL_ARRIVALS:
            self._handle_internal_arrival(event)
            return

        # Unknown event type
        raise ValueError(f"Unhandled event type: {event.type}")

    def _handle_lazy_reject(self, event: Event) -> None:
        """
        Handle a lazy computer rejecting a message.
        """
        # Delegate rejection logic to the lazy computer
        self.lazy_computer.reject_message()

    def _handle_master_send(self, event: Event) -> None:
        """
        Handle message transmission initiated by the master computer.
        """
        # Delegate message send logic to the master computer
        self.master_computer.send_message()

    def _handle_external_arrival(self, event: Event) -> None:
        """
        Process an external message arrival at its target computer.

        Enqueues the message, starts processing if the computer is idle,
        and schedules the next external arrival event.
        """

        target = self.computers[event.target]  # lookup target computer

        # Queue incoming message and attempt immediate processing
        target.enqueue_message(event.message)
        target.receive_message()

        # If the computer is idle, schedule message processing start
        if not target.busy:
            self.schedule_event(
                Event(
                    self.clock,
                    target.get_start_processing_event_type(),
                    event.message,
                    event.target,
                )
            )

        # Schedule a future external arrival of the same type
        if event.type == EventTypes.WORKER_RECEIVE_EXT_MSG:
            self.schedule_event(
                ExternalArrivalGenerator.gen_worker_ext_arrival(self.clock)
            )
        else:
            self.schedule_event(
                ExternalArrivalGenerator.gen_lazy_ext_arrival(self.clock)
            )

    def _handle_internal_arrival(self, event: Event) -> None:
        """
        Process an internal message arrival at its target computer.

        Enqueues the message, optionally triggers receipt behavior (for
        Worker and Lazy computers), and schedules message processing if
        the target is currently idle.
        """

        target = self.computers[event.target]  # lookup target computer

        # Queue the incoming internal message
        target.enqueue_message(event.message)

        # Worker/Lazy explicitly receive internal messages
        if target.ID in (WORKER_COMPUTER, LAZY_COMPUTER):
            target.receive_message()

        # If idle, schedule processing start
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
        """
        Begin processing the next message on the target computer.

        Delegates processing to the computer and schedules the resulting event.
        """

        target = self.computers[event.target]  # lookup target computer

        # Process message and obtain follow-up event
        next_event = target.process_message(self.clock)

        # Schedule event returned by the computer
        self.schedule_event(next_event)

    def _handle_processing_end(self, event: Event) -> None:
        """
        Finalize message processing on the target computer.

        Determines the outcome (forwarding, rejection, etc.) and schedules
        the resulting follow-up event.
        """

        target = self.computers[event.target]  # lookup target computer

        # Evaluate outcome of completed processing
        next_event = target.determine_message_outcome(self.clock, event.message)

        # Schedule resulting follow-up event
        self.schedule_event(next_event)


# TODO(anyone): remove and create main
# TODO (anyone): ask user for values
sim = Simulator(20, 2, SpeedMode.FAST)
sim.run()
