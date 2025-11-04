from enum import Enum


class SpeedMode(Enum):
    SLOW = ("slow", 1.5)
    FAST = ("fast", 0.0)
    SILENT = ("silent", 0.0)

    def __init__(self, label: str, delay: float):
        self.label = label
        self.delay = delay
