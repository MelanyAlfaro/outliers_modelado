class Message:
    def __init__(self, source: int, arrival_time: float):
        self.source : int = source
        self.arrival_time : float = arrival_time
        self.exit_time : float = 0.0
        self.enqueue_time : float = 0.0
        self.wait_time : float = 0.0
        self.rejected : bool = False
        self.type : str = ""
        
    def mark_enqueue_time(self, enqueue_time: float) -> None:
        self.enqueue_time = enqueue_time

    def update_wait_time(self, service_start_time: float) -> None:
        self.wait_time += service_start_time - self.enqueue_time

    def mark_departure(self, time: float) -> None:
        self.exit_time = time

    def reject(self) -> None:
        self.rejected = True

    def send(self) -> None:
        self.rejected = False
        
    def get_in_sys_time(self) -> float:
        return self.exit_time - self.arrival_time
