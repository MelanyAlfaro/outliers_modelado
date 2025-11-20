import time

from event_type import EventType
from computer import Computer
from speed_mode import SpeedMode


class Logger:
    @staticmethod
    def log_event(
        max_sim_count: int,
        current_time: float,
        event_type: EventType,
        worker_computer: Computer,
        master_computer: Computer,
        lazy_computer: Computer,
        sim_number: int,
        speed: SpeedMode = SpeedMode.SILENT,
        joint_work_time=float,
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
        if speed == SpeedMode.SILENT:
            return

        #  --- Event header ---
        print("=" * 70)
        print(f"System clock: {current_time:6.2f} s | Event: {event_type}")
        print(f"Simulation run: {sim_number+1} of {max_sim_count}")
        print("-" * 70)

        # --- Message queues ---
        print(f"Master queue (C1): {master_computer.get_enqueued_messages()} messages")
        print(f"Worker queue (C2): {worker_computer.get_enqueued_messages()} messages")
        print(f"Lazy queue (C3): {lazy_computer.get_enqueued_messages()} messages")

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
        print(f"Current joint work time (C1, C2, C3): " f"{joint_work_time:.2f} s")

        time.sleep(speed.delay)
