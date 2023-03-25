class Request:
    counter = 0
    def __init__(self, request_priority:int, request_timeout:float, need_server:int, arrival_time:int, is_timed_out:bool = False) -> None:
        """Instance of a web server request

        Args:
            request_priority (int): priority of request
            request_timeout (float): timeout value after which request is dropped
            need_server (int): server type
            arrival_time (int): arrival time of the request in the system
            is_timed_out (bool): to check whether the request was failed before
        """
        self.id = Request.counter   
        Request.counter += 1

        self.request_priority = request_priority
        self.request_timeout = request_timeout
        self.need_server = need_server
        self.arrival_time = arrival_time
        self.is_timed_out = is_timed_out # to check whether the request was failed before