from event_types import EventTypes
from computer import Computer
from computer import WORKER_COMPUTER, LAZY_COMPUTER
from master_computer import MasterComputer
from worker_computer import WorkerComputer
from lazy_computer import LazyComputer
from speed_mode import SpeedMode
from event import Event
from logger import Logger
from stats_collector import StatsCollector
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
        self.joint_work_start_time = -1.0  # timestamp for start time of joint work

        self.event_queue = []  # min-heap of pending events
        self.computers = []  # computer entities indexed by ID

        self.speed_mode = speed_mode  # execution pacing config
        self.logger = Logger()  # logs output
        self.stats_collector = StatsCollector()  # stats collector for each run

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

        Reinitializes simulation time, event queue, joint work start time and
        computer entities, then schedules the initial SIMULATION_START event.
        """
        self.clock = 0.0  # reset simulation time
        self.event_queue.clear()  # remove any pending events
        self.computers.clear()  # reset computer container
        self.stats_collector.clear_iteration_records()  # clear stats for new run
        self.joint_work_start_time = -1  # reset mark for start of joint work

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

    def show_collected_stats(
        self, current_run: int, show_final_statistics: bool
    ) -> None:
        """
        Show the collected statistics to the user.

        Shows the average wait times, average in system times and efficiency
        coefficients for all messages that exited the system before the simulation
        ended. It also shows how much time each computer was busy and for how many
        time they worked together.

        Parameters
        ----------
        current_run : int
            The number of the current simulation run
        show_final_statistics: bool
            Decides if final statistics or current iteration statistics are shown
        """
        if show_final_statistics == False:
            print("\n" + "=" * 60)
            print(f"STATISTICS COLLECTED FOR SIMULATION #{current_run + 1}")
            print("=" * 60)
            stats = self.stats_collector.get_current_iteration_statistics()
        else:
            print("\n" + "=" * 60)
            print(f"FINAL STATISTICS FOR THE SIMULATION (AVERAGE)")
            print("=" * 60)
            stats = self.stats_collector.get_final_statistics()

        # Verify if statistics are available
        if stats is None:
            print("There are no statistics to be shown.")
            return

        message_titles = [
            "Rejected messages",
            "Sent messages from Worker",
            "Sent messages from Lazy",
            "All",
        ]

        avg_wait = stats["avg_msg_wait_times"]
        avg_in_sys = stats["avg_msg_in_sys_times"]
        eff = stats["msg_efficiency_coeffs"]
        busy = stats["avg_comp_busy_times"]
        busy_perc = stats["perc_comp_busy_times"]
        joint = stats["joint_work_time_stats"]

        # Average wait times
        print("\nAVERAGE WAIT TIMES")
        print("-" * 50)
        for i in range(len(avg_wait)):
            print(f"- {message_titles[i]}: {avg_wait[i]:.4f}s")

        # In sys times
        print("\nAVERAGE IN SYSTEM TIMES")
        print("-" * 50)
        for i in range(len(avg_wait)):
            print(f"- {message_titles[i]}: {avg_in_sys[i]:.4f}s")

        # Efficiency coefficients
        print("\nEFFICIENCY COEFFICIENTS")
        print("-" * 50)
        for i in range(len(avg_wait)):
            print(f"- {message_titles[i]}: {eff[i]:.4f}")

        # Busy times/percentages for each computer
        print("\nBUSY TIME FOR EACH COMPUTER")
        print("-" * 50)
        print("Computer   Busy time (s)  Percentage (%)")
        print("--------   -------------  --------------")
        print(f"Master   {busy[0]:>11.4f}s  {busy_perc[0]:>11.2f}%")
        print(f"Worker   {busy[1]:>11.4f}s  {busy_perc[1]:>11.2f}%")
        print(f"Lazy     {busy[2]:>11.4f}s  {busy_perc[2]:>11.2f}%")

        # Joint work
        print("\nJOINT WORK TIME OF THE 3 COMPUTERS")
        print("-" * 50)
        print(f"- Total joint work time: {joint[0]:.4f}s")
        print(f"- Percentage from total time: {joint[1]:.2f}%")

        print("\n" + "=" * 60)

    def ask_for_statistics(self, current_run: int) -> None:
        """
        Ask the user if statistics for current run should be shown.

        Parameters
        ----------
        current_run : int
            The number of the current simulation run
        """
        # Ask user if they want to see statistics for this run
        while True:
            skip_choice = input(
                f"\nDo you want to see statistics for Simulation #{self.total_runs + 1}? (y/n): "
            )
            if skip_choice.lower() == "y":
                self.show_collected_stats(current_run, False)
                break
            elif skip_choice.lower() == "n":
                print(f"Skipping statistics for Simulation #{self.total_runs + 1}")
                return
            else:
                print(f"Invalid input. Please enter 'y' for yes or 'n' for no.")

        # Ask user to enter 'c' to continue
        while True:
            continue_option = input(
                f"\nPlease enter 'c' to continue with the next run: "
            )
            if continue_option.lower() == "c":
                break
            else:
                print(f"Invalid input.")

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
        shows stats for the current run, and then advances to the next run.
        """

        while self.total_runs < self.max_runs:

            # Reset per-run simulation state
            self.initialize_sim()

            # Process events in chronological order
            while self.event_queue:
                self.process_next_event()

            # Get stats for the iteration and show them
            self.stats_collector.record_iteration_statistics(
                self.computers, self.max_time
            )

            # Show statistics (ask user) and ask the user to continue
            self.ask_for_statistics(self.total_runs)

            # Mark run as completed
            self.total_runs += 1

        # Show a summary for the final statistics
        while True:
            skip_choice = input(
                f"\nDo you want to see the final statistics for the simulation system? (y/n): "
            )
            if skip_choice.lower() == "y":
                self.show_collected_stats(self.total_runs, True)
                break
            elif skip_choice.lower() == "n":
                print(f"Skipping statistics for the simulation system.")
                return
            else:
                print(f"Invalid input. Please enter 'y' for yes or 'n' for no.")
        self.show_collected_stats(self.total_runs, True)

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
            joint_work_time=self.stats_collector.joint_work_time
        )

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
        event.message.mark_departure(self.clock)
        # Delegate rejection logic to the lazy computer and store message (for stats collector)
        self.lazy_computer.reject_message(event.message)
        self.stats_collector.store_msg(event.message)

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
        event.message.mark_enqueue_time(self.clock)
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
        event.message.mark_enqueue_time(self.clock)
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

        Delegates processing to the computer, defines timestamp por joint time if
        all computers are working, and schedules the resulting event.
        """

        target = self.computers[event.target]  # lookup target computer

        # Process message and obtain follow-up event
        next_event = target.process_message(self.clock)

        # Mark the start time of joint work if all 3 are working
        if (
            self.master_computer.busy
            and self.worker_computer.busy
            and self.lazy_computer.busy
        ):
            self.joint_work_start_time = self.clock

        # Schedule event returned by the computer
        self.schedule_event(next_event)

    def _handle_processing_end(self, event: Event) -> None:
        """
        Finalize message processing on the target computer.

        Determines the outcome (forwarding, rejection, etc.), calculates joint time (if it applies),
        stores the message for the statistics collector if the message will exit the system,
        and schedules the resulting follow-up event.
        """

        target = self.computers[event.target]  # lookup target computer

        # Evaluate outcome of completed processing
        next_event = target.determine_message_outcome(self.clock, event.message)

        # If the 3 computers were working together, update the joint work time
        # The time is updated locally and in the stats collector
        if self.joint_work_start_time != -1:
            addend_joint_work = self.clock - self.joint_work_start_time
            self.stats_collector.add_joint_work_time(addend_joint_work)
            self.joint_work_start_time = -1

        # Store processed message in stats collector if it will be sent by the master
        if next_event.type == EventTypes.MASTER_SEND_MSG:
            event.message.mark_departure(self.clock)
            self.stats_collector.store_msg(event.message)

        # Schedule resulting follow-up event
        self.schedule_event(next_event)

        # Computer that ended processing keeps working if its queue is not empty
        if target.get_enqueued_messages() > 0:
            self.schedule_event(
                Event(
                    self.clock,
                    type=target.get_start_processing_event_type(),
                    target=event.target,
                )
            )
