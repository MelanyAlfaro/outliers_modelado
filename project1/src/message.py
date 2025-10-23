class Message:
    def __init__(self, source: int, arrival_time: float):
        self.source : int = source
        self.arrival_time : float = arrival_time
        self.exit_time : float = 0.0
        self.enqueue_time : float = 0.0
        self.wait_time : float = 0.0
        self.rejected : bool = False
        self.type : str = ""