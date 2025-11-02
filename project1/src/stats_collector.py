from collections import defaultdict
from statistics import mean
from message import Message
from computer import Computer, MASTER_COMPUTER, WORKER_COMPUTER, LAZY_COMPUTER
from message_type import MessageType


class StatsCollector:
    def __init__(self) -> None:
        self.messages_dict: dict[MessageType, list[Message]] = defaultdict(list)
        self.joint_work_time: float = 0.0

        self.iteration_records: list[dict[str, list[float]]] = []

    def store_msg(self, message: Message) -> None:
        if message.rejected:
            message_type = MessageType.REJECTED_MSG
        elif message.source == WORKER_COMPUTER:
            message_type = MessageType.SENT_MSG_FROM_WORKER
        elif message.source == LAZY_COMPUTER:
            message_type = MessageType.SENT_MSG_FROM_LAZY
        else:
            raise AssertionError("Message does not fit with types")
        self.messages_dict[message_type].append(message)

    # === Message statistics ===
    def get_messages_statistics(
        self,
    ) -> tuple[list[float], list[float], list[float]]:
        avg_wait_times = list(self.get_msgs_avg_wait_time())
        avg_in_sys_times = list(self.get_msgs_avg_in_sys_time())
        assert len(avg_wait_times) == len(avg_in_sys_times)

        # Get overall averages
        total_avg_wait_time, total_avg_in_sys_time = self.get_overall_avg_times()

        # Append them to the lists
        avg_wait_times.append(total_avg_wait_time)
        avg_in_sys_times.append(total_avg_in_sys_time)

        efficiency_coefficients = [
            wait_time / in_sys_time
            for wait_time, in_sys_time in zip(avg_wait_times, avg_in_sys_times)
            if in_sys_time and in_sys_time > 0
        ]
        return avg_wait_times, avg_in_sys_times, efficiency_coefficients

    def get_msgs_avg_in_sys_time(self) -> tuple[float, float, float]:
        return (
            self._get_avg_in_sys_time_for(MessageType.REJECTED_MSG),
            self._get_avg_in_sys_time_for(MessageType.SENT_MSG_FROM_WORKER),
            self._get_avg_in_sys_time_for(MessageType.SENT_MSG_FROM_LAZY),
        )

    def _get_avg_in_sys_time_for(self, message_type: MessageType) -> float:
        message_list = self.messages_dict.get(message_type, [])
        if message_list:
            return mean(message.get_in_sys_time() for message in message_list)
        return None

    def get_overall_avg_times(self) -> tuple[float, float]:
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

    def get_msgs_avg_wait_time(self) -> tuple[float, float, float]:
        return (
            self._get_avg_wait_time_for(MessageType.REJECTED_MSG),
            self._get_avg_wait_time_for(MessageType.SENT_MSG_FROM_WORKER),
            self._get_avg_wait_time_for(MessageType.SENT_MSG_FROM_LAZY),
        )

    def _get_avg_wait_time_for(self, message_type: MessageType) -> float:
        message_list = self.messages_dict.get(message_type, [])
        if message_list:
            return mean(message.wait_time for message in message_list)
        return None

    # === Computer statistics ===
    def add_joint_work_time(self, duration: float) -> None:
        self.joint_work_time += duration

    def get_computers_statistics(
        self, computers: list[Computer], sim_end_time: float
    ) -> tuple[list[float], list[float], list[float]]:
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
        avg_msg_wait_times, avg_msg_in_sys_times, msg_efficiency_coeffs = (
            self.get_messages_statistics()
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
        return self.iteration_records[-1] if self.iteration_records else None

    # === Final aggregated statistics ===
    def get_final_statistics(self) -> dict[str, list[float]] | None:
        if not self.iteration_records:
            return None

        def avg_over_iterations(key: str) -> list[float]:
            """Average each numeric list across all iterations."""
            values_by_iteration = [rec[key] for rec in self.iteration_records]
            # zip(*...) transposes the list of lists
            # This way, all data that correlates with each other stays together
            return [mean(vals) for vals in zip(*values_by_iteration)]

        return {
            "avg_msg_wait_times": avg_over_iterations("avg_msg_wait_times"),
            "avg_msg_in_sys_times": avg_over_iterations("avg_msg_in_sys_times"),
            "msg_efficiency_coeffs": avg_over_iterations("msg_efficiency_coeffs"),
            "avg_comp_busy_times": avg_over_iterations("avg_comp_busy_times"),
            "perc_comp_busy_times": avg_over_iterations("perc_comp_busy_times"),
            "joint_work_time_stats": avg_over_iterations("joint_work_time_stats"),
        }
