from message import Message
from computer import Computer


class StatsCollector:
    def __init__(self) -> None:
        self.messages_dict: dict[str, list[Message]] = dict()
        self.joint_work_time: float = 0.0

    def store_msg(self, message: Message) -> None:
        pass

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
