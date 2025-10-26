from event import Event

class Logger():
    """
    Logger for simulation events.

    Attributes:
        delay (float): Sleep time
        max_sim_count (int): Maximum number of simulation iterations.
    """
    def __init__(self, delay: float, max_sim_count: int):
        self.delay = delay
        self.max_sim_count = max_sim_count