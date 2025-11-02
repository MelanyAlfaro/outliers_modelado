from collections import defaultdict
from statistics import mean

from message import Message
from computer import Computer, MASTER_COMPUTER, WORKER_COMPUTER, LAZY_COMPUTER
from message_type import MessageType


class StatsCollector:
    def __init__(self) -> None:
        self.messages_dict: dict[MessageType, list[Message]] = defaultdict(list)
        self.joint_work_time: float = 0.0

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

    def get_messages_statistics(
        self,
    ) -> tuple[tuple[float, ...], tuple[float, ...], tuple[float, ...]]:
        avg_wait_times = self.get_msgs_avg_wait_time()
        avg_in_sys_times = self.get_msgs_avg_in_sys_time()
        assert len(avg_wait_times) == len(avg_in_sys_times)
        efficiency_coefficients = tuple(
            wait_time / in_sys_time
            for wait_time, in_sys_time in zip(avg_wait_times, avg_in_sys_times)
            if in_sys_time and in_sys_time > 0
        )
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

    def add_joint_work_time(self, duration: float) -> None:
        self.joint_work_time += duration

    def get_avg_busy_times(
        self, computers: list[Computer]
    ) -> tuple[float, float, float]:
        pass

    def get_busy_times_percentage(
        self, computers: list[Computer]
    ) -> tuple[float, float, float]:
        pass

    def get_avg_joint_work_time(self) -> float:
        pass

    def get_joint_work_time_percentage(self, total_sim_time: float) -> float:
        pass
