from collections import defaultdict
from typing import Tuple
from statistics import mean

from message import Message
from computer import Computer, MASTER_COMPUTER, WORKER_COMPUTER, LAZY_COMPUTER
from message_type import MessageType


class StatsCollector:
    """
    Collects, organizes, and computes statistics for a simulation involving messages
    and computers.

    Responsibilities:
    - Track messages by type (e.g., rejected, from workers, from lazy computers)
    - Calculate average wait and in-system times for messages
    - Track computer utilization and joint work time
    - Record statistics for each simulation iteration
    - Aggregate statistics across multiple iterations
    """

    def __init__(self) -> None:
        # Dictionary mapping message types to lists of Message objects
        self.messages_dict: dict[MessageType, list[Message]] = defaultdict(list)

        # Accumulated time when computers are working together
        self.joint_work_time: float = 0.0

        # Records statistics per simulation iteration
        # Each element is a dict mapping metric names to lists of floats
        self.iteration_records: list[dict[str, list[float]]] = []

    # === Message storage ===
    def store_msg(self, message: Message) -> None:
        """
        Store a message in the appropriate category based on its source or
        rejection status.
        """
        if message.rejected:
            message_type = MessageType.REJECTED_MSG
        elif message.source == WORKER_COMPUTER:
            message_type = MessageType.SENT_MSG_FROM_WORKER
        elif message.source == LAZY_COMPUTER:
            message_type = MessageType.SENT_MSG_FROM_LAZY
        else:
            # Safety check: message doesn't match known types
            raise AssertionError("Message does not fit with types")

        self.messages_dict[message_type].append(message)

    # === Message statistics ===
    def _get_messages_statistics(self) -> Tuple[list[float], list[float], list[float]]:
        """
        Compute per-type average wait times, in-system times, and efficiency coefficients
        (wait time / in-system time). Returns three lists of floats.
        """
        avg_wait_times = list(self._get_msgs_avg_wait_time())
        avg_in_sys_times = list(self._get_msgs_avg_in_sys_time())
        assert len(avg_wait_times) == len(avg_in_sys_times)

        # Add overall averages across all message types
        total_avg_wait_time, total_avg_in_sys_time = self._get_overall_avg_times()
        avg_wait_times.append(total_avg_wait_time)
        avg_in_sys_times.append(total_avg_in_sys_time)

        # Efficiency = wait time / in-system time (avoiding division by zero)
        efficiency_coefficients = [
            wait_time / in_sys_time
            for wait_time, in_sys_time in zip(avg_wait_times, avg_in_sys_times)
            if in_sys_time and in_sys_time > 0
        ]

        return avg_wait_times, avg_in_sys_times, efficiency_coefficients

    def _get_msgs_avg_in_sys_time(self) -> Tuple[float, float, float]:
        """
        Returns average in-system times for:
        (Rejected messages, Worker messages, Lazy messages)
        """
        return (
            self._get_avg_in_sys_time_for(MessageType.REJECTED_MSG),
            self._get_avg_in_sys_time_for(MessageType.SENT_MSG_FROM_WORKER),
            self._get_avg_in_sys_time_for(MessageType.SENT_MSG_FROM_LAZY),
        )

    def _get_avg_in_sys_time_for(self, message_type: MessageType) -> float:
        """Helper: compute average in-system time for a specific message type."""
        message_list = self.messages_dict.get(message_type, [])
        if message_list:
            return mean(message.get_in_sys_time() for message in message_list)
        return None

    def _get_overall_avg_times(self) -> Tuple[float, float]:
        """
        Compute overall average wait time and in-system time across all message types.
        """
        total_in_sys_time = 0.0
        total_wait_time = 0.0
        total_count = 0

        for message_type in (
            MessageType.REJECTED_MSG,
            MessageType.SENT_MSG_FROM_WORKER,
            MessageType.SENT_MSG_FROM_LAZY,
        ):
            message_list = self.messages_dict.get(message_type, [])
            total_in_sys_time += sum(
                message.get_in_sys_time() for message in message_list
            )
            total_wait_time += sum(message.wait_time for message in message_list)
            total_count += len(message_list)

        total_avg_in_sys_time = (
            total_in_sys_time / total_count if total_count > 0 else None
        )
        total_avg_wait_time = total_wait_time / total_count if total_count > 0 else None
        return total_avg_wait_time, total_avg_in_sys_time

    def _get_msgs_avg_wait_time(self) -> Tuple[float, float, float]:
        """
        Returns average wait times for:
        (Rejected messages, Worker messages, Lazy messages)
        """
        return (
            self._get_avg_wait_time_for(MessageType.REJECTED_MSG),
            self._get_avg_wait_time_for(MessageType.SENT_MSG_FROM_WORKER),
            self._get_avg_wait_time_for(MessageType.SENT_MSG_FROM_LAZY),
        )

    def _get_avg_wait_time_for(self, message_type: MessageType) -> float:
        """Helper: compute average wait time for a specific message type."""
        message_list = self.messages_dict.get(message_type, [])
        if message_list:
            return mean(message.wait_time for message in message_list)
        return None

    # === Computer statistics ===
    def add_joint_work_time(self, duration: float) -> None:
        """Add time duration to joint work time."""
        self.joint_work_time += duration

    def get_computers_statistics(
        self, computers: list[Computer], sim_end_time: float
    ) -> Tuple[list[float], list[float], list[float]]:
        """
        Compute statistics per computer:
        - Average busy time
        - Percentage of time each computer was busy
        - Joint work time and percentage relative to simulation end
        """
        avg_busy_times = [computer.busy_time for computer in computers]
        perc_busy_times = [
            (computer.busy_time / computer.end_time) if computer.end_time > 0 else 0.0
            for computer in computers
        ]

        perc_joint_work_time = (
            self.joint_work_time / sim_end_time if sim_end_time > 0.0 else 0.0
        )

        return (
            avg_busy_times,
            perc_busy_times,
            [self.joint_work_time, perc_joint_work_time],
        )

    # === Iteration tracking ===
    def record_iteration_statistics(
        self, computers: list[Computer], sim_end_time: float
    ) -> None:
        """
        Record statistics for the current iteration.
        Stores both message and computer statistics.
        """
        avg_msg_wait_times, avg_msg_in_sys_times, msg_efficiency_coeffs = (
            self._get_messages_statistics()
        )
        avg_busy_times, perc_busy_times, joint_work_times_stats = (
            self.get_computers_statistics(computers, sim_end_time)
        )

        self.iteration_records.append(
            {
                "avg_msg_wait_times": avg_msg_wait_times,
                "avg_msg_in_sys_times": avg_msg_in_sys_times,
                "msg_efficiency_coeffs": msg_efficiency_coeffs,
                "avg_comp_busy_times": avg_busy_times,
                "perc_comp_busy_times": perc_busy_times,
                "joint_work_time_stats": joint_work_times_stats,
            }
        )

    def get_current_iteration_statistics(self) -> dict[str, list[float]] | None:
        """Return statistics for the most recent iteration, or None if no iterations recorded."""
        return self.iteration_records[-1] if self.iteration_records else None

    # === Final aggregated statistics ===
    def get_final_statistics(self) -> dict[str, list[float]] | None:
        """
        Compute averages across all iterations for each tracked metric.
        Returns a dictionary mapping metric names to lists of averaged values.
        """
        if not self.iteration_records:
            return None

        def avg_over_iterations(key: str) -> list[float]:
            """Helper: compute average across iterations for a specific metric."""
            values_by_iteration = [rec[key] for rec in self.iteration_records]
            # Transpose lists to compute mean for each corresponding position
            return [mean(vals) for vals in zip(*values_by_iteration)]

        return {
            "avg_msg_wait_times": avg_over_iterations("avg_msg_wait_times"),
            "avg_msg_in_sys_times": avg_over_iterations("avg_msg_in_sys_times"),
            "msg_efficiency_coeffs": avg_over_iterations("msg_efficiency_coeffs"),
            "avg_comp_busy_times": avg_over_iterations("avg_comp_busy_times"),
            "perc_comp_busy_times": avg_over_iterations("perc_comp_busy_times"),
            "joint_work_time_stats": avg_over_iterations("joint_work_time_stats"),
        }
