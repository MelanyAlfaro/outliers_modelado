from collections import defaultdict


from message import Message
from computer import Computer, MASTER_COMPUTER, WORKER_COMPUTER, LAZY_COMPUTER
from message_type import MessageType


class StatsCollector:
    def __init__(self) -> None:
        self.messages_dict: dict[str, list[Message]] = defaultdict(list)
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

    def get_msgs_avg_in_sys_time(self) -> tuple[float]:
        pass

    def get_msgs_avg_wait_time(self) -> tuple[float]:
        pass

    def get_msgs_efficienct_coefficient(self) -> tuple[float]:
        pass

    def add_joint_work_time(self, time: float) -> None:
        pass

    def get_avg_busy_times(self, computers: list[Computer]) -> tuple[float]:
        pass

    def get_busy_times_percentage(self, computers: list[Computer]) -> tuple[float]:
        pass

    def get_avg_joint_work_time(self) -> float:
        pass

    def get_joint_work_time_percentage(self, total_sim_time: float) -> float:
        pass
