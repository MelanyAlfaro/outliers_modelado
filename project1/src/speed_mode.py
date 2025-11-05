from enum import Enum


class SpeedMode(Enum):
    """
    Represents predefined simulation speed modes.

    Each mode stores:
    - label: text identifier
    - delay: time (in seconds) to wait after each event

    Modes
    -----
    SLOW   → adds a delay to slow down execution (for observation)
    FAST   → executes without delay
    SILENT → executes without delay, suppressing output
    """

    SLOW = ("slow", 1.5)
    FAST = ("fast", 0.0)
    SILENT = ("silent", 0.0)

    def __init__(self, label: str, delay: float) -> None:
        """
        Parameters
        ----------
        label : str
            User-friendly name of the mode.
        delay : float
            Delay in seconds to apply per event.
        """
        self.label = label
        self.delay = delay
