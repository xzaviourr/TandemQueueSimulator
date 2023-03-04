import numpy as np


class Server:
    def __init__(self, core_count:int, average_service_time:float) -> None:
        """Server instance, consisting of multiple cores.

        Args:
            core_count (int): Core count in the server for multi-processing
            average_service_time (float): average service time for exponential distribution
        """
        self.core_count = core_count
        self.busy_cores = 0
        
        self.regular_queue = [] # Waiting queue for normal requests
        self.priority_queue = []    # Waiting queue for high priority requests
        self.average_service_time = average_service_time    # Average service time 

    def get_service_time(self):
        """Generate service time from exponential distribution

        Returns:
            float: Service time
        """
        return np.random.exponential(self.average_service_time)
