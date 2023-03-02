import numpy as np


class Server:
    def __init__(self, core_count, average_service_time) -> None:
        self.core_count = core_count
        self.busy_cores = 0
        
        self.regular_queue = [] # Waiting queue for normal requests
        self.priority_queue = []    # Waiting queue for high priority requests
        self.average_service_time = average_service_time    # Average service time 

    def get_service_time(self):
        return np.random.exponential(self.average_service_time)
