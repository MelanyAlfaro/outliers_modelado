import time

from event_types import EventTypes
from computer import Computer
from master_computer import MasterComputer
from worker_computer import WorkerComputer
from lazy_computer import LazyComputer


class Logger:
    """
    Logger for simulation events.

    Attributes:
        delay (float): Sleep time
        max_sim_count (int): Maximum number of simulation iterations.
    """

    def __init__(self, delay: float, max_sim_count: int) -> None:
        self.delay = delay
        self.max_sim_count = max_sim_count

    def log_event(
        self,
        current_time: float,
        event_type: EventTypes,
        worker_computer: WorkerComputer,
        master_computer: MasterComputer,
        lazy_computer: LazyComputer,
        sim_number: int,
        speed: str = "fast",
    ) -> None:
        """
        Displays the current state of the system during a simulation event.

        Parameters:
        current_time : Current simulation clock time (in seconds).
        event_type : The type of event that occurred (e.g., message arrival,
                    processing completion).
        worker_computer : Reference to the Worker computer (C2).
        master_computer : Reference to the Master computer (C1).
        lazy_computer :  Reference to the Lazy computer (C3).
        sim_number : The number of the current simulation run.
        speed : str, optional
            The visualization speed for event logging.
            Accepted values:
                - "slow": adds a delay (`self.delay`) between events.
                - "fast": no delay (default).
                - "silent": disables output entirely.
        """
        if speed == "silent":
            return

        #  --- Event header ---
        print("=" * 70)
        print(f"System clock: {current_time:6.2f} s | Event: {event_type}")
        print(f"Simulation run: {sim_number} of {self.max_sim_count}")
        print("-" * 70)

        # --- Message queues ---
        print(f"Master queue (C1): {master_computer.get_enqueued_messages()} messages")
        print(
            f"Worker queue (C2): {worker_computer.message_queue.get_enqueued_messages()} messages"
        )
        print(
            f"Lazy queue (C3): {lazy_computer.message_queue.get_enqueued_messages()=} messages"
        )

        # --- Processor states ---
        print(f"Master (C1) state: {master_computer.get_state()}")
        print(f"Worker (C2) state: {worker_computer.get_state()}")
        print(f"Lazy (C3) state: {lazy_computer.get_state()}")

        # --- Real-time statistics ---
        print("-" * 70)
        print(f"Messages sent by Master (C1): {master_computer.sent_messages}")
        print(f"Messages received by Worker (C2): {worker_computer.received_messages}")
        print(f"Messages received by Lazy (C3): {lazy_computer.received_messages}")
        print(f"Messages rejected by Lazy (C3): {lazy_computer.rejected_messages}")
        print(
            f"Total processing time (C1 + C2 + C3): "
            f"{master_computer.busy_time + worker_computer.busy_time + lazy_computer.busy_time:.2f} s"
        )

        if speed == "slow":
            time.sleep(self.delay)
